#!/usr/bin/env python3
"""Riesegue le risposte degli studenti con i test delle domande CodeRunner, come Jobe, per sapere
quali test superano e stimare il punteggio automatico che ha dato Moodle.

Uso:
    python3 esegui_risposte.py LAVORO --dashboard=CARTELLA --quiz=ID

LAVORO       la cartella di leggi_export.py (dati.json). Scrive esiti.json e aggiunge l'esito
             in testa a ogni risposta dei file D01.txt… (riscrivendoli).
--dashboard  esportazione del database della dashboard (come per leggi_export.py).

Linguaggio deciso dal campo «coderunner» della riga:
- SQL: `database:` nelle opzioni e soluzione non PHP. Ogni test esegue la query sul database
  del quiz più le righe di `=== extra`, in SQLite (Python, versione vicina a quella di Jobe).
- PHP: soluzione che comincia con <?php (prototipo php_mysqli_sqlite). Ogni test esegue la pagina
  con il template della skill domande-php-mysqli-mock e il database del quiz; spazi e a capo non
  contano. Serve `php`; il client sqlite3 lo sostituisce sqlite3_cli.py di materiali-moodle.
- JavaScript con prompt: nessun database e niente `=== code`. Esegue in Node con esegui_js.py di
  domande-coderunner-js.
Le righe senza test (HTML, CSS, teoria) restano alla correzione manuale.

Il punteggio automatico è stimato: tutto o niente, salvo `allornothing: 0` nelle opzioni (frazione
dei test superati). Se Moodle dice altro, vale Moodle.
"""
import glob
import json
import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import tempfile

QUI = pathlib.Path(__file__).resolve().parent
SKILLS = QUI.parent.parent


def sezioni(campo):
    """Il campo coderunner della dashboard: opzioni, soluzione, test (con stdin, extra, nascosto)."""
    opz, answer, code, tests, cur, nome = {}, "", None, [], None, None
    buf = []

    def chiudi():
        testo = "\n".join(buf).strip("\n")
        if nome == "options":
            for r in testo.splitlines():
                if ":" in r:
                    k, v = r.split(":", 1)
                    opz[k.strip()] = v.strip()
        elif nome == "answer":
            nonlocal answer
            answer = testo
        elif nome == "code":
            nonlocal code
            code = testo
        elif nome == "test":
            tests.append({"codice": testo, "stdin": "", "extra": "", "nascosto": cur})
        elif nome in ("stdin", "extra", "descrizione", "expected") and tests:
            tests[-1][nome] = testo

    for riga in (campo or "").splitlines():
        m = re.match(r"^=== (\w+)(?:\s+(HIDE))?\s*$", riga)
        if m:
            if nome:
                chiudi()
            nome, cur, buf = m.group(1), bool(m.group(2)), []
        else:
            buf.append(riga)
    if nome:
        chiudi()
    return opz, answer, code, tests


def db_base(quiz, nome):
    for d in quiz.get("database", []) or []:
        if d.get("nome") == nome:
            con = sqlite3.connect(":memory:")
            con.executescript(d["sql"])
            return con
    sys.exit(f"Il database «{nome}» non è nel campo database del quiz.")


def copia(con):
    nuovo = sqlite3.connect(":memory:")
    con.backup(nuovo)
    return nuovo


def esegui_sql(con, q):
    try:
        return [tuple(r) for r in con.execute(q).fetchall()], None
    except Exception as e:
        return None, str(e)


def esito_sql(base, answer, tests, risposta):
    esiti = []
    for t in tests:
        c = copia(base)
        if t["extra"]:
            c.executescript(t["extra"])
        atteso, _ = esegui_sql(c, answer)
        ottenuto, err = esegui_sql(c, risposta)
        if err:
            esiti.append(("errore", err))
        elif ottenuto == atteso:
            esiti.append(("ok", ""))
        elif sorted(map(repr, ottenuto)) == sorted(map(repr, atteso)):
            esiti.append(("ordine", "stesse righe, ordine diverso"))
        else:
            esiti.append(("diverso", f"{len(ottenuto)} righe invece di {len(atteso)}"))
    return esiti


def prepara_php(quiz, nome, cartella):
    tpl = SKILLS / "domande-php-mysqli-mock" / "assets" / "prototipo-sqlite-template.php"
    if not tpl.exists():
        sys.exit("Non trovo il template del prototipo php_mysqli_sqlite (skill domande-php-mysqli-mock).")
    dbfile = os.path.join(cartella, nome + ".db")
    if not os.path.exists(dbfile):
        con = sqlite3.connect(dbfile)
        for d in quiz.get("database", []):
            if d.get("nome") == nome:
                con.executescript(d["sql"])
        con.commit()
        con.close()
    sqlite = "sqlite3"
    if not any(os.access(os.path.join(p, "sqlite3"), os.X_OK) for p in os.environ.get("PATH", "").split(os.pathsep)):
        cli = SKILLS / "materiali-moodle" / "scripts" / "sqlite3_cli.py"
        sqlite = os.path.join(cartella, "sqlite3")
        with open(sqlite, "w") as f:
            f.write(f"#!/bin/sh\nexec python3 '{cli}' \"$@\"\n")
        os.chmod(sqlite, 0o755)
    return tpl.read_text(encoding="utf-8"), dbfile, sqlite


def esegui_php(tpl, dbfile, sqlite, test, codice, quiz_db):
    configura = (f"\nFakeDB::configure(['user' => 'root', 'password' => '', 'database' => '{quiz_db}', "
                 f"'dbfile' => '{dbfile}', 'sqlite' => '{sqlite}']);\n")
    prog = tpl.replace("{{ TEST.testcode }}", test["codice"] + configura).replace("{{ STUDENT_ANSWER }}", codice)
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "pagina.php"
        p.write_text(prog, encoding="utf-8")
        try:
            r = subprocess.run(["php", "-n", "-d", "display_errors=stdout", str(p)],
                               capture_output=True, text=True, cwd=d, timeout=20)
            return r.stdout
        except subprocess.TimeoutExpired:
            return "##TIMEOUT##"


def esito_php(ctx, answer, tests, risposta):
    tpl, dbfile, sqlite, nome = ctx
    norm = lambda s: re.sub(r"\s+", "", s)
    esiti = []
    for t in tests:
        atteso = esegui_php(tpl, dbfile, sqlite, t, answer, nome)
        ottenuto = esegui_php(tpl, dbfile, sqlite, t, risposta, nome)
        if norm(ottenuto) == norm(atteso):
            esiti.append(("ok", ""))
        else:
            m = re.search(r"(Parse error|Fatal error|Warning)[^\n]*", ottenuto)
            esiti.append(("errore" if m else "diverso",
                          re.sub(r" in /\S+ on line \d+", "", m.group(0))[:120] if m else "output diverso"))
    return esiti


def esito_js(answer, tests, risposta, opz):
    sys.path.insert(0, str(SKILLS / "domande-coderunner-js" / "scripts"))
    import esegui_js as ej
    esiti = []
    for t in tests:
        a = ej.esegui(ej.programma_prompt(answer, t["codice"], t["stdin"], t["extra"]))
        o = ej.esegui(ej.programma_prompt(risposta, t["codice"], t["stdin"], t["extra"]))
        if o["errore"] or o["timeout"]:
            esiti.append(("errore", "ciclo infinito o troppo lento" if o["timeout"] else o["errore"][:120]))
        elif o["output"].rstrip() == a["output"].rstrip():
            esiti.append(("ok", ""))
        else:
            esiti.append(("diverso", "output diverso"))
    return esiti


def main():
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    opz = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    if len(arg) != 1 or "dashboard" not in opz or "quiz" not in opz:
        sys.exit(__doc__)
    lavoro = arg[0]
    dati = json.load(open(os.path.join(lavoro, "dati.json"), encoding="utf-8"))
    quiz = json.load(open(os.path.join(opz["dashboard"], "quiz", opz["quiz"] + ".json"), encoding="utf-8"))
    esiti = {}
    tmp = tempfile.mkdtemp(prefix="php-", dir=lavoro)
    cache = {}

    def prepara(rid):
        """Riga della dashboard → (lingua, contesto, answer, tests, punti, tutto) oppure None."""
        if rid in cache:
            return cache[rid]
        riga = json.load(open(os.path.join(opz["dashboard"], "quiz", opz["quiz"], "domande", rid + ".json"),
                              encoding="utf-8"))
        o, answer, code, tests = sezioni(riga.get("coderunner", ""))
        out = None
        if tests and answer:
            punti = float(riga.get("punti") or 0)
            tutto = o.get("allornothing", "1").strip() != "0"
            if o.get("database") and answer.lstrip().startswith("<?php"):
                out = ("php", prepara_php(quiz, o["database"], tmp) + (o["database"],), answer, tests, punti, tutto, o)
            elif o.get("database"):
                out = ("sql", db_base(quiz, o["database"]), answer, tests, punti, tutto, o)
            elif code is None:
                out = ("js", None, answer, tests, punti, tutto, o)
            else:
                print(f"{rid}: gapfiller JavaScript, non rieseguito")
        cache[rid] = out
        return out

    for k, dom in dati["domande"].items():
        if not dom.get("riga"):
            continue
        risultati = {}
        for s in dati["studenti"]:
            rid = s.get("righe", {}).get(k) or dom["riga"]
            p = prepara(rid) if rid else None
            if not p:
                continue
            lingua, ctx, answer, tests, punti, tutto, o = p
            r = s["risposte"][k].strip()
            if not r or r == "-":
                risultati[s["chiave"]] = {"esito": "vuota", "auto": 0, "riga": rid}
                continue
            if lingua == "sql":
                e = esito_sql(ctx, answer, tests, r)
            elif lingua == "php":
                e = esito_php(ctx, answer, tests, r)
            else:
                e = esito_js(answer, tests, r, o)
            passati = sum(1 for x in e if x[0] == "ok")
            auto = punti if passati == len(tests) else (0 if tutto else round(punti * passati / len(tests), 2))
            if passati == len(tests):
                testo = "OK, test superati"
            else:
                primo = next(x for x in e if x[0] != "ok")
                quale = "" if e[0][0] != "ok" else "test nascosto: "
                testo = (f"{passati}/{len(tests)} test · " if not tutto else "") + quale + (
                    primo[1] if primo[0] != "errore" else "ERRORE: " + primo[1])
            risultati[s["chiave"]] = {"esito": testo[:110], "auto": auto, "riga": rid,
                                      "dettaglio": [list(x) for x in e]}
        if not risultati:
            continue
        lingue = {cache[r][0] for r in dom.get("righe", [dom["riga"]]) if cache.get(r)}
        esiti[k] = {"lingua": "/".join(sorted(lingue)), "studenti": risultati}
        pieni = sum(1 for c, v in risultati.items() if v["esito"].startswith("OK"))
        print(f"D{int(k):02d} {'/'.join(sorted(lingue)).upper()}: {pieni}/{len(dati['studenti'])} con il punteggio pieno in automatico")
    json.dump(esiti, open(os.path.join(lavoro, "esiti.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    posizioni = {os.path.basename(f)[:-5]: json.load(open(f, encoding="utf-8")).get("pos", "")
                 for f in glob.glob(os.path.join(opz["dashboard"], "quiz", opz["quiz"], "domande", "*.json"))}
    for k in dati["domande"]:
        with open(os.path.join(lavoro, f"D{int(k):02d}.txt"), "w", encoding="utf-8") as f:
            for s in dati["studenti"]:
                es = esiti.get(k, {}).get("studenti", {}).get(s["chiave"], {})
                rid = s.get("righe", {}).get(k)
                pos = f"[{posizioni.get(rid, rid)}] " if rid and len(dati["domande"][k].get("righe", [])) > 1 else ""
                f.write(f"\n##### {s['sigla']}   {pos}{es.get('esito', '')}\n{s['risposte'][k]}\n")
    print("esiti.json scritto; i file D01.txt… hanno l'esito accanto a ogni studente.")


if __name__ == "__main__":
    main()
