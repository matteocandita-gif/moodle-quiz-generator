#!/usr/bin/env python3
"""Genera l'XML Moodle di una o più domande CodeRunner PHP con database simulato
(prototipi php_mysqli_sqlite e php_mysqli_mock) da un file di specifica.

Uso:
    python3 crea_xml.py SPECIFICA.txt OUTPUT.xml [--verifica] [--cartella-db DIR]

Formato (le righe che iniziano con "=== " aprono una sezione; il resto è
contenuto grezzo, senza escaping):

    === category                 (facoltativa; "Nome" -> $module$/top/Nome)
    Lezione 5 - PHP e database
    === database dblibreria      (facoltativa, ripetibile: SQL che crea e popola
    CREATE TABLE ...;             il database; diventa dblibreria.db allegato)
    INSERT INTO ...;
    === question                 (apre una domanda; ripetibile)
    === name
    L5 - C8 - Scrivere: le presentazioni
    === options                  (facoltativa: righe chiave: valore)
    prototipo: sqlite
    === note                     (facoltativa: note per il docente, non esportate)
    === questiontext             (HTML; blocchi [[codice LINGUA]] ... [[/codice]])
    === preload                  (facoltativa)
    === answer
    === test                     (ripetibile; "=== test HIDE" per un test nascosto)
    === descrizione              (facoltativa, dopo il test: ciò che lo studente
                                  vede nella colonna della prova, campo Extra)
    === expected                 (obbligatoria, dopo il test)

Con --verifica, se PHP (e per il prototipo sqlite il client sqlite3) sono
installati, esegue la soluzione su ogni test e confronta l'output.
"""
import base64
import pathlib
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import xml.dom.minidom

QUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import moodle_lib as ml  # noqa: E402

DISCLAIMER = "N.B. questa è una simulazione"
PROTOTIPI = {"sqlite": "php_mysqli_sqlite", "mock": "php_mysqli_mock"}
TEMPLATE = {"sqlite": "prototipo-sqlite-template.php", "mock": "prototipo-mock-template.php"}

OPZIONI_PREDEFINITE = {
    "prototipo": "sqlite",
    "database": None,            # nome di una sezione database da allegare
    "defaultgrade": "1",
    "penalty": "0",
    "allornothing": "1",
    "penaltyregime": "0",
    "precheck": "0",
    "hidecheck": "0",
    "showsource": "0",
    "answerboxlines": None,
    "answerboxcolumns": "100",
    "validateonsave": "1",
    "displayfeedback": "1",
    "giveupallowed": "0",
}


# ---------------------------------------------------------------- lettura

def leggi_specifica(testo):
    testo = testo.replace("\r\n", "\n")
    stato = {"categoria": None, "database": {}, "domande": []}
    corrente = None
    sezione, righe = None, []

    def chiudi():
        nonlocal sezione, righe
        if sezione is None:
            return
        contenuto = "\n".join(righe).strip("\n")
        nome, _, arg = sezione.partition(" ")
        arg = arg.strip()
        if nome == "category":
            stato["categoria"] = contenuto.strip()
        elif nome == "database":
            if not arg:
                raise ValueError("'=== database' senza nome (es. '=== database dblibreria')")
            stato["database"][arg] = contenuto
        elif corrente is None:
            raise ValueError(f"sezione '{nome}' fuori da una domanda (manca '=== question')")
        elif nome == "test":
            corrente["test"].append({"testcode": contenuto, "expected": None, "extra": "",
                                     "display": "HIDE" if arg.upper() == "HIDE" else "SHOW"})
        elif nome in ("expected", "descrizione"):
            if not corrente["test"]:
                raise ValueError(f"'{corrente.get('name', '?')}': '=== {nome}' senza un '=== test' prima")
            chiave = "expected" if nome == "expected" else "extra"
            corrente["test"][-1][chiave] = contenuto
        elif nome == "options":
            for riga in contenuto.splitlines():
                if riga.strip():
                    k, _, v = riga.partition(":")
                    k = k.strip()
                    if k not in OPZIONI_PREDEFINITE:
                        raise ValueError(f"opzione sconosciuta: {k}")
                    corrente["options"][k] = v.strip()
        elif nome in ("name", "questiontext", "preload", "answer", "note"):
            corrente[nome] = contenuto
        else:
            raise ValueError(f"sezione sconosciuta: '{nome}'")
        sezione, righe = None, []

    for riga in testo.split("\n"):
        if riga.startswith("=== "):
            chiudi()
            intestazione = riga[4:].strip()
            if intestazione == "question":
                corrente = {"options": {}, "test": [], "preload": ""}
                stato["domande"].append(corrente)
            else:
                sezione = intestazione
        else:
            righe.append(riga)
    chiudi()
    return stato


def opzioni(d, databases):
    o = dict(OPZIONI_PREDEFINITE)
    o.update(d["options"])
    if o["prototipo"] not in PROTOTIPI:
        raise ValueError(f"{d.get('name')}: prototipo '{o['prototipo']}' sconosciuto (sqlite o mock)")
    if o["database"] is None and o["prototipo"] == "sqlite" and len(databases) == 1:
        o["database"] = next(iter(databases))
    if o["answerboxlines"] is None:
        o["answerboxlines"] = str(max(18, len(d["preload"].splitlines()) + 3))
    return o


def controlla(d, o, databases):
    nome = d.get("name", "(senza nome)")
    problemi = []
    for campo in ("name", "questiontext", "answer"):
        if not d.get(campo):
            problemi.append(f"{nome}: manca la sezione '{campo}'")
    if d.get("questiontext") and DISCLAIMER not in d["questiontext"]:
        problemi.append(f"{nome}: il testo non contiene il disclaimer della simulazione")
    if d.get("answer") and not d["answer"].lstrip().startswith("<?php"):
        problemi.append(f"{nome}: la soluzione deve iniziare con <?php")
    if d.get("preload") and not d["preload"].lstrip().startswith("<?php"):
        problemi.append(f"{nome}: il preload deve iniziare con <?php")
    if o["database"] and o["database"] not in databases:
        problemi.append(f"{nome}: il database '{o['database']}' non è definito")
    if o["database"] and o["prototipo"] == "mock":
        problemi.append(f"{nome}: il prototipo mock non usa database allegati")
    if not d["test"]:
        problemi.append(f"{nome}: nessun test")
    for i, t in enumerate(d["test"], 1):
        if t["expected"] is None:
            problemi.append(f"{nome}: il test {i} non ha '=== expected'")
        if "FakeDB::configure" not in t["testcode"]:
            problemi.append(f"{nome}: il test {i} non chiama FakeDB::configure")
    return problemi


# ---------------------------------------------------------------- database

def costruisci_db(nome, sql, cartella):
    percorso = pathlib.Path(cartella) / f"{nome}.db"
    if percorso.exists():
        percorso.unlink()
    con = sqlite3.connect(percorso)
    try:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(sql)
        con.commit()
    except sqlite3.Error as e:
        raise ValueError(f"errore nel database '{nome}': {e}")
    finally:
        con.close()
    return percorso


# ---------------------------------------------------------------- scrittura

def esc(testo):
    return testo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def xml_domanda(d, o, db_b64):
    test_xml = []
    for t in d["test"]:
        atteso = t["expected"].rstrip("\n") + "\n"
        test_xml.append(f"""      <testcase testtype="0" useasexample="0" hiderestiffail="0" mark="1.0000000" >
      <testcode>
                <text>{ml.cdata(t["testcode"])}</text>
      </testcode>
      <stdin>
                <text></text>
      </stdin>
      <expected>
                <text>{ml.cdata(atteso)}</text>
      </expected>
      <extra>
                <text>{ml.cdata(t["extra"]) if t["extra"] else ""}</text>
      </extra>
      <display>
                <text>{t["display"]}</text>
      </display>
    </testcase>""")
    if db_b64:
        test_xml.append(f'<file name="{o["database"]}.db" path="/" encoding="base64">{db_b64}</file>')

    return f"""  <question type="coderunner">
    <name>
      <text>{esc(d["name"])}</text>
    </name>
    <questiontext format="html">
      <text>{ml.cdata(d["questiontext"])}</text>
    </questiontext>
    <generalfeedback format="html">
      <text></text>
    </generalfeedback>
    <defaultgrade>{o["defaultgrade"]}</defaultgrade>
    <penalty>{o["penalty"]}</penalty>
    <hidden>0</hidden>
    <idnumber></idnumber>
    <coderunnertype>{PROTOTIPI[o["prototipo"]]}</coderunnertype>
    <prototypetype>0</prototypetype>
    <allornothing>{o["allornothing"]}</allornothing>
    <penaltyregime>{o["penaltyregime"]}</penaltyregime>
    <precheck>{o["precheck"]}</precheck>
    <hidecheck>{o["hidecheck"]}</hidecheck>
    <showsource>{o["showsource"]}</showsource>
    <answerboxlines>{o["answerboxlines"]}</answerboxlines>
    <answerboxcolumns>{o["answerboxcolumns"]}</answerboxcolumns>
    <answerpreload>{ml.cdata(d["preload"])}</answerpreload>
    <globalextra></globalextra>
    <useace></useace>
    <resultcolumns></resultcolumns>
    <template></template>
    <iscombinatortemplate></iscombinatortemplate>
    <allowmultiplestdins></allowmultiplestdins>
    <answer>{ml.cdata(d["answer"])}</answer>
    <validateonsave>{o["validateonsave"]}</validateonsave>
    <testsplitterre></testsplitterre>
    <language></language>
    <acelang></acelang>
    <sandbox></sandbox>
    <grader></grader>
    <cputimelimitsecs></cputimelimitsecs>
    <memlimitmb></memlimitmb>
    <sandboxparams></sandboxparams>
    <templateparams></templateparams>
    <hoisttemplateparams>1</hoisttemplateparams>
    <extractcodefromjson>1</extractcodefromjson>
    <templateparamslang>None</templateparamslang>
    <templateparamsevalpertry>0</templateparamsevalpertry>
    <templateparamsevald>{{}}</templateparamsevald>
    <twigall>0</twigall>
    <uiplugin></uiplugin>
    <uiparameters></uiparameters>
    <attachments>0</attachments>
    <attachmentsrequired>0</attachmentsrequired>
    <maxfilesize>10240</maxfilesize>
    <filenamesregex></filenamesregex>
    <filenamesexplain></filenamesexplain>
    <displayfeedback>{o["displayfeedback"]}</displayfeedback>
    <giveupallowed>{o["giveupallowed"]}</giveupallowed>
    <prototypeextra></prototypeextra>
    <testcases>
{chr(10).join(test_xml)}
    </testcases>
  </question>
"""


def percorso_categoria(cat):
    return cat if cat.startswith("$") else "$module$/top/" + cat


# ---------------------------------------------------------------- verifica

def esegui(template, testcode, codice, db_file):
    programma = template.replace("{{ TEST.testcode }}", testcode).replace("{{ STUDENT_ANSWER }}", codice)
    with tempfile.TemporaryDirectory() as cartella:
        (pathlib.Path(cartella) / "prog.php").write_text(programma, encoding="utf-8")
        if db_file:
            shutil.copy(db_file, cartella)
        r = subprocess.run(["php", "-n", "-d", "display_errors=stdout", "prog.php"],
                           capture_output=True, text=True, timeout=30, cwd=cartella)
    return r.stdout + (("\n[stderr] " + r.stderr) if r.stderr else "")


def verifica(lavori):
    if not shutil.which("php"):
        print("PHP non disponibile: verifica non eseguita, controlla gli output a mano.")
        return True
    tutto_ok = True
    for d, o, db_file in lavori:
        if o["prototipo"] == "sqlite" and not shutil.which("sqlite3"):
            print(f"## {d['name']}: client sqlite3 non disponibile, verifica saltata")
            continue
        template = (QUI.parent / "assets" / TEMPLATE[o["prototipo"]]).read_text(encoding="utf-8")
        print(f"\n## {d['name']}")
        for i, t in enumerate(d["test"], 1):
            out = esegui(template, t["testcode"], d["answer"], db_file)
            ok = out.rstrip() == t["expected"].rstrip()
            tutto_ok &= ok
            print(f"  test {i}: soluzione {'OK' if ok else 'DIVERSA DALL OUTPUT ATTESO'}")
            if not ok:
                print("    ottenuto:\n      " + out.rstrip().replace("\n", "\n      "))
            if d["preload"]:
                pre = esegui(template, t["testcode"], d["preload"], db_file).strip().splitlines()
                print(f"           preload -> {pre[0] if pre else '(nessun output)'}")
    return tutto_ok


# ---------------------------------------------------------------- main

def main():
    args = sys.argv[1:]
    cartella_db = None
    if "--cartella-db" in args:
        i = args.index("--cartella-db")
        cartella_db = args[i + 1]
        del args[i:i + 2]
    posizionali = [a for a in args if not a.startswith("--")]
    if len(posizionali) != 2:
        sys.exit(__doc__)
    stato = leggi_specifica(pathlib.Path(posizionali[0]).read_text(encoding="utf-8"))
    if not stato["domande"]:
        sys.exit("Nessuna domanda nella specifica.")

    lavoro = pathlib.Path(cartella_db or tempfile.mkdtemp())
    lavoro.mkdir(parents=True, exist_ok=True)
    db_files = {n: costruisci_db(n, sql, lavoro) for n, sql in stato["database"].items()}

    problemi, avvisi, preparate = [], [], []
    for d in stato["domande"]:
        o = opzioni(d, stato["database"])
        if d.get("questiontext"):
            d["questiontext"] = ml.espandi_codice(d["questiontext"])
            e, a = ml.controlla_html(d["questiontext"], "coderunner")
            problemi += [f"{d.get('name')}: {x}" for x in e]
            avvisi += [f"{d.get('name')}: {x}" for x in a]
        problemi += controlla(d, o, stato["database"])
        preparate.append((d, o, db_files.get(o["database"]) if o["database"] else None))
    nomi = [d.get("name") for d in stato["domande"]]
    problemi += [f"nome ripetuto: {n}" for n in set(nomi) if nomi.count(n) > 1]
    if problemi:
        sys.exit("Specifica non valida:\n- " + "\n- ".join(problemi))

    parti = ['<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n']
    if stato["categoria"]:
        parti.append(f"""  <question type="category">
    <category>
      <text>{esc(percorso_categoria(stato["categoria"]))}</text>
    </category>
  </question>
""")
    for d, o, db_file in preparate:
        b64 = base64.b64encode(db_file.read_bytes()).decode() if db_file else ""
        parti.append(xml_domanda(d, o, b64))
    parti.append("</quiz>\n")
    pathlib.Path(posizionali[1]).write_text("".join(parti), encoding="utf-8")
    xml.dom.minidom.parse(posizionali[1])

    for a in avvisi:
        print("AVVISO: " + a)
    print(f"Creato {posizionali[1]}: " + ", ".join(
        f"{d['name']} ({PROTOTIPI[o['prototipo']]}, {len(d['test'])} test"
        + (f", allegato {o['database']}.db" if db_file else "") + ")"
        for d, o, db_file in preparate))
    if cartella_db:
        print(f"Database salvati in {cartella_db}")

    if "--verifica" in sys.argv and not verifica(preparate):
        sys.exit(1)


if __name__ == "__main__":
    main()
