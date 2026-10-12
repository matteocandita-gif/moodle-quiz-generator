#!/usr/bin/env python3
"""Genera domande CodeRunner SQL (prototipo sql_salvemini) da una specifica.

Uso:
    python3 crea_xml.py SPECIFICA.txt USCITA.xml [--cartella-db DIR]

Lo script costruisce i database SQLite dalle sezioni "=== database NOME",
esegue la soluzione su ogni test con l'emulatore del client sqlite3 di Jobe
(SQLite 3.46, verificato con la domanda di taratura), scrive gli output attesi,
incorpora il database nella domanda e controlla le regole. Esegue anche il
codice precaricato, per mostrare che cosa incontra per primo lo studente.

Formato: references/formato-specifica.md.
"""
import base64
import pathlib
import re
import sqlite3
import sys
import tempfile
import xml.dom.minidom

QUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import emula_sqlite as em  # noqa: E402
import moodle_lib as ml  # noqa: E402

OPZIONI = {
    "database": None,          # nome di una sezione === database
    "database_file": None,     # oppure un file .db esistente
    "dati": None,              # pieno | struttura | vuoto (dedotto se assente)
    "foreign_keys": "1",
    "precheck": "0",           # 1 = aggiunge il test di sola sintassi
    "defaultgrade": "1",
    "penalty": "0",
    "allornothing": "1",
    "grader": "",              # vuoto = quello del prototipo (EqualityGrader)
    "answerboxlines": None,
    "hidecheck": "0",
    "giveupallowed": "0",
}

STRUTTURA_RE = re.compile(r"\[\[struttura\s+(\w+)\]\]")


def macro_struttura(m):
    t = m.group(1)
    return ("SELECT name, replace(upper(type), ' (', '(') AS tipo, \"notnull\", pk "
            "FROM pragma_table_info('%s');\n"
            "SELECT \"table\", \"from\", \"to\" FROM pragma_foreign_key_list('%s');"
            % (t, t))


class Domanda:
    def __init__(self, categoria):
        self.categoria = categoria
        self.campi = {}
        self.opzioni = dict(OPZIONI)
        self.test = []        # dict: codice, extra, nascosto, precheck, atteso


def leggi(testo):
    testo = testo.replace("\r\n", "\n")
    database, domande, errori = {}, [], []
    categoria, corrente, sezione, righe = None, None, None, []

    def chiudi():
        nonlocal sezione, righe, categoria
        if sezione is None:
            return
        c = "\n".join(righe).strip("\n")
        nome, _, arg = sezione.partition(" ")
        arg = arg.strip()
        if nome == "category":
            categoria = ml.percorso_categoria(c)
        elif nome == "database":
            if not arg:
                errori.append("=== database senza nome")
            database[arg] = c
        elif corrente is None:
            errori.append("sezione '%s' prima di '=== question'" % nome)
        elif nome in ("name", "questiontext", "preload", "answer", "generalfeedback"):
            corrente.campi[nome] = c
        elif nome == "note":
            pass
        elif nome == "options":
            for r in c.splitlines():
                if r.strip():
                    k, _, v = r.partition(":")
                    k = k.strip()
                    if k not in OPZIONI:
                        errori.append("%s: opzione sconosciuta '%s'"
                                      % (corrente.campi.get("name", "?"), k))
                    corrente.opzioni[k] = v.strip()
        elif nome == "test":
            flag = arg.upper().split()
            corrente.test.append({"codice": c, "extra": "", "nascosto": "HIDE" in flag,
                                  "precheck": False, "atteso": None})
        elif nome in ("extra", "expected"):
            if not corrente.test:
                errori.append("%s: '=== %s' senza un test prima"
                              % (corrente.campi.get("name", "?"), nome))
            elif nome == "extra":
                corrente.test[-1]["extra"] = c
            else:
                corrente.test[-1]["atteso"] = c
        else:
            errori.append("sezione sconosciuta: '%s'" % nome)
        sezione, righe = None, []

    for r in testo.split("\n"):
        if r.startswith("=== "):
            chiudi()
            intest = r[4:].strip()
            if intest == "question":
                corrente = Domanda(categoria)
                domande.append(corrente)
            else:
                sezione = intest
        else:
            righe.append(r)
    chiudi()
    return database, domande, errori


def costruisci_db(script, dati, destinazione):
    """Crea il file .db: pieno (tutto lo script), struttura (tabelle senza
    righe), vuoto (nessuna tabella)."""
    con = sqlite3.connect(destinazione)
    if dati != "vuoto":
        con.executescript(script)
        if dati == "struttura":
            con.execute("PRAGMA foreign_keys = OFF")
            tabelle = [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'")]
            for t in tabelle:
                con.execute('DELETE FROM "%s"' % t)
            con.commit()
    con.close()
    if dati == "vuoto":
        # sqlite crea il file solo alla prima scrittura
        con = sqlite3.connect(destinazione)
        con.execute("PRAGMA user_version = 0")
        con.execute("CREATE TABLE _x(a)")
        con.execute("DROP TABLE _x")
        con.execute("VACUUM")
        con.close()


def deduci_dati(risposta):
    a = risposta.upper()
    if re.search(r"\bCREATE\s+TABLE\b", a):
        return "vuoto"
    if re.search(r"\bINSERT\b", a) and not re.search(r"\b(SELECT|UPDATE|DELETE)\b", a):
        return "struttura"
    return "pieno"


def _t(tag, contenuto, ind="    "):
    return "%s<%s>%s</%s>\n" % (ind, tag, ml.cdata(contenuto) if contenuto else "", tag)


def genera(d, nome_db, db_b64):
    o = d.opzioni
    righe_preload = len(d.campi.get("preload", "").splitlines())
    boxlines = o["answerboxlines"] or str(max(8, righe_preload + 3))
    params = "" if o["foreign_keys"] == "1" else '{"foreign_keys": false}'
    x = ['  <question type="coderunner">\n',
         '    <name>\n      <text>%s</text>\n    </name>\n' % ml.esc_xml(d.campi["name"]),
         '    <questiontext format="html">\n      <text>%s</text>\n    </questiontext>\n'
         % ml.cdata(d.campi["questiontext"]),
         '    <generalfeedback format="html">\n      <text>%s</text>\n    </generalfeedback>\n'
         % (ml.cdata(d.campi["generalfeedback"]) if d.campi.get("generalfeedback") else ""),
         "    <defaultgrade>%s</defaultgrade>\n    <penalty>%s</penalty>\n"
         % (o["defaultgrade"], o["penalty"]),
         "    <hidden>0</hidden>\n    <idnumber></idnumber>\n",
         "    <coderunnertype>sql_salvemini</coderunnertype>\n    <prototypetype>0</prototypetype>\n",
         "    <allornothing>%s</allornothing>\n    <penaltyregime>0</penaltyregime>\n" % o["allornothing"],
         "    <precheck>%s</precheck>\n" % ("3" if o["precheck"] == "1" else "0"),
         "    <hidecheck>%s</hidecheck>\n    <showsource>0</showsource>\n" % o["hidecheck"],
         "    <answerboxlines>%s</answerboxlines>\n    <answerboxcolumns>100</answerboxcolumns>\n" % boxlines,
         _t("answerpreload", d.campi.get("preload", "")),
         "    <globalextra></globalextra>\n    <useace></useace>\n    <resultcolumns></resultcolumns>\n",
         "    <template></template>\n    <iscombinatortemplate></iscombinatortemplate>\n",
         "    <allowmultiplestdins></allowmultiplestdins>\n",
         _t("answer", d.campi["answer"]),
         "    <validateonsave>1</validateonsave>\n    <testsplitterre></testsplitterre>\n",
         "    <language></language>\n    <acelang></acelang>\n    <sandbox></sandbox>\n",
         "    <grader>%s</grader>\n" % o["grader"],
         "    <cputimelimitsecs></cputimelimitsecs>\n    <memlimitmb></memlimitmb>\n",
         "    <sandboxparams></sandboxparams>\n",
         "    <templateparams>%s</templateparams>\n" % ml.esc_xml(params),
         "    <hoisttemplateparams>1</hoisttemplateparams>\n    <extractcodefromjson>1</extractcodefromjson>\n",
         "    <templateparamslang>None</templateparamslang>\n    <templateparamsevalpertry>0</templateparamsevalpertry>\n",
         "    <templateparamsevald>%s</templateparamsevald>\n" % ml.esc_xml(params or "{}"),
         "    <twigall>0</twigall>\n    <uiplugin></uiplugin>\n    <uiparameters></uiparameters>\n",
         "    <attachments>0</attachments>\n    <attachmentsrequired>0</attachmentsrequired>\n",
         "    <maxfilesize>10240</maxfilesize>\n    <filenamesregex></filenamesregex>\n",
         "    <filenamesexplain></filenamesexplain>\n    <displayfeedback>1</displayfeedback>\n",
         "    <giveupallowed>%s</giveupallowed>\n    <prototypeextra></prototypeextra>\n" % o["giveupallowed"],
         "    <testcases>\n"]
    for t in d.test:
        x.append('      <testcase testtype="%s" useasexample="0" hiderestiffail="0" mark="1.0000000" >\n'
                 % ("1" if t["precheck"] else "0"))
        x.append("      <testcode>\n        <text>%s</text>\n      </testcode>\n" % ml.cdata(t["codice"]))
        x.append("      <stdin>\n        <text></text>\n      </stdin>\n")
        x.append("      <expected>\n        <text>%s</text>\n      </expected>\n"
                 % (ml.cdata(t["atteso"]) if t["atteso"] else ""))
        x.append("      <extra>\n        <text>%s</text>\n      </extra>\n"
                 % (ml.cdata(t["extra"]) if t["extra"] else ""))
        x.append("      <display>\n        <text>%s</text>\n      </display>\n"
                 % ("HIDE" if t["nascosto"] else "SHOW"))
        x.append("    </testcase>\n")
    x.append('<file name="%s" path="/" encoding="base64">%s</file>\n' % (nome_db, db_b64))
    x.append("    </testcases>\n  </question>\n\n")
    return "".join(x)


def main():
    args = sys.argv[1:]
    cartella_db = None
    if "--cartella-db" in args:
        i = args.index("--cartella-db")
        cartella_db = pathlib.Path(args[i + 1])
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__)
        sys.exit(2)
    database, domande, errori = leggi(pathlib.Path(args[0]).read_text(encoding="utf-8"))
    tmp = pathlib.Path(tempfile.mkdtemp())
    pezzi, nomi = [], {}
    cat_corrente = object()
    for d in domande:
        nome = d.campi.get("name", "").strip()
        etichetta = nome or "(senza nome)"
        nomi[etichetta] = nomi.get(etichetta, 0) + 1
        mancanti = [s for s in ("name", "questiontext", "answer") if not d.campi.get(s, "").strip()]
        if mancanti:
            errori.append("%s: mancano %s" % (etichetta, ", ".join(mancanti)))
            continue
        if not d.test:
            errori.append("%s: nessun test" % etichetta)
            continue
        d.campi["name"] = nome
        d.campi["questiontext"] = ml.espandi_codice(d.campi["questiontext"])
        e, a = ml.controlla_html(d.campi["questiontext"], "coderunner")
        errori += ["%s: %s" % (etichetta, x) for x in e]
        for x in a:
            print("AVVISO  %s: %s" % (etichetta, x))

        # database
        o = d.opzioni
        dati = o["dati"] or deduci_dati(d.campi["answer"])
        if o["database_file"]:
            percorso = pathlib.Path(o["database_file"])
            if not percorso.exists():
                errori.append("%s: database_file non trovato: %s" % (etichetta, percorso))
                continue
            nome_db = percorso.name
        else:
            base = o["database"] or (next(iter(database)) if len(database) == 1 else None)
            if base not in database:
                errori.append("%s: indica 'database: NOME' (definiti: %s)"
                              % (etichetta, ", ".join(database) or "nessuno"))
                continue
            nome_db = base + ("" if dati == "pieno" else "_" + dati) + ".db"
            percorso = tmp / nome_db
            if not percorso.exists():
                try:
                    costruisci_db(database[base], dati, str(percorso))
                except sqlite3.Error as ex:
                    errori.append("database %s: lo script SQL non funziona: %s" % (base, ex))
                    continue
                if cartella_db:
                    cartella_db.mkdir(parents=True, exist_ok=True)
                    (cartella_db / nome_db).write_bytes(percorso.read_bytes())

        # test e output attesi
        fk = o["foreign_keys"] == "1"
        if o["precheck"] == "1" and not any(t["precheck"] for t in d.test):
            d.test.insert(0, {"codice": "-- controllo di sola sintassi", "extra": "",
                              "nascosto": False, "precheck": True, "atteso": None})
        risposta = em.chiudi_risposta(d.campi["answer"])
        regex = o["grader"] == "RegexGrader"
        for n, t in enumerate(d.test, 1):
            t["codice"] = STRUTTURA_RE.sub(macro_struttura, t["codice"])
            codice = risposta if t["precheck"] else "\n".join(
                [t["extra"], risposta, t["codice"]])
            try:
                righe, err = em.esegui(str(percorso), codice, fk)
            except ValueError as ex:
                errori.append("%s, test %d: %s" % (etichetta, n, ex))
                continue
            calcolato = em.formatta_test(righe, err, precheck=t["precheck"])
            if t["precheck"] and err:
                errori.append("%s: la soluzione non passa il controllo di sintassi: %s"
                              % (etichetta, "; ".join(err)))
            if t["atteso"] is None:
                if regex:
                    errori.append("%s, test %d: con RegexGrader scrivi l'espressione in === expected"
                                  % (etichetta, n))
                t["atteso"] = calcolato
            elif not regex and t["atteso"].rstrip() != calcolato:
                print("AVVISO  %s, test %d: l'output atteso scritto a mano è diverso da "
                      "quello calcolato:\n%s" % (etichetta, n, calcolato))
            if err and not t["precheck"]:
                print("NOTA    %s, test %d: la soluzione produce un errore (%s): va bene solo "
                      "se è voluto, come nelle domande sui vincoli" % (etichetta, n, "; ".join(err)))
            if not t["precheck"] and not righe and not err:
                print("AVVISO  %s, test %d: output vuoto: il test non controlla niente"
                      % (etichetta, n))
        if not any(not t["precheck"] for t in d.test):
            errori.append("%s: serve almeno un test oltre al controllo di sintassi" % etichetta)
        if d.campi.get("preload", "").strip():
            righe, err = em.esegui(str(percorso), em.chiudi_risposta(d.campi["preload"]), fk)
            primo = err[0] if err else (righe[0] if righe else "(nessun output)")
            print("PRELOAD %s: con il codice di partenza lo studente vede per primo: %s"
                  % (etichetta, primo))

        if d.categoria != cat_corrente:
            if d.categoria:
                pezzi.append(ml.xml_categoria(d.categoria))
            cat_corrente = d.categoria
        b64 = base64.b64encode(percorso.read_bytes()).decode()
        pezzi.append(genera(d, nome_db, b64))

    for n, c in nomi.items():
        if c > 1:
            errori.append("nome ripetuto %d volte: %s" % (c, n))
    if errori:
        print("\nERRORI (XML non generato):")
        for e in errori:
            print("  - " + e)
        sys.exit(1)
    testo = '<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n' + "".join(pezzi) + "</quiz>\n"
    xml.dom.minidom.parseString(testo.encode("utf-8"))
    pathlib.Path(args[1]).write_text(testo, encoding="utf-8")
    print("\nOK: %d domande -> %s" % (len(domande), args[1]))


if __name__ == "__main__":
    main()
