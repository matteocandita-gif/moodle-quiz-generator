"""Esegue il template come farebbe CodeRunner su Jobe: rende il Twig (con Jinja2, sintassi
compatibile per quello che usa il template), copia gli allegati nella cartella di lavoro,
lancia Python e divide l'output con il separatore dei test."""
import os
import shutil
import subprocess
import sys
import tempfile

import jinja2

QUI = os.path.dirname(os.path.abspath(__file__))
SEPARATORE = "#<ab@17943918#@>#"


def escaper_py(s, lingua=None):
    # come qtype_coderunner_escapers::python
    return (s or "").replace("\\", "\\\\").replace('"', '\\"')


def rendi(testcodes, allegati, risposta, soluzione, pagina, php=False, lasco=False, database=""):
    env = jinja2.Environment(undefined=jinja2.Undefined, autoescape=False,
                             keep_trailing_newline=True)
    env.filters["e"] = escaper_py
    t = env.from_string(open(os.path.join(QUI, "template.py"), encoding="utf-8").read())
    contesto = {
        "ATTACHMENTS": ",".join(allegati),
        "STUDENT_ANSWER": risposta,
        "QUESTION": {"answer": soluzione},
        "TESTCASES": [{"testcode": c} for c in testcodes],
    }
    if pagina:
        contesto["pagina"] = pagina
    if php:
        contesto["php"] = "1"
    if lasco:
        contesto["lasco"] = "1"
    if database:
        contesto["database"] = database
    return t.render(**contesto)


def esegui(testcodes, allegati=None, risposta="", soluzione="", pagina="", senza_node=False, supporto=None, php=False,
           lasco=False, database=""):
    """supporto: file di supporto della domanda (nella cartella di lavoro, ma non tra gli allegati)."""
    allegati = allegati or {}
    programma = rendi(testcodes, allegati, risposta, soluzione, pagina, php, lasco, database)
    if senza_node:
        # simula un Jobe in cui node non c'è: trova_node() restituisce sempre None
        programma = programma.replace("def trova_node():", "def trova_node():\n    return None\n\n\ndef _trova_node_vero():")
    with tempfile.TemporaryDirectory() as d:
        for nome, dati in list(allegati.items()) + list((supporto or {}).items()):
            with open(os.path.join(d, nome), "wb") as f:
                f.write(dati)
        with open(os.path.join(d, "__tester__.python3"), "w", encoding="utf-8") as f:
            f.write(programma)
        ambiente = dict(os.environ)
        if not shutil.which("sqlite3"):
            # come php_attesi.py: dove manca il client sqlite3 (l'ambiente di Claude) lo sostituisce sqlite3_cli.py
            cli = os.path.join(QUI, "..", "..", "plugins", "moodle-quiz-generator", "skills", "materiali-moodle",
                               "scripts", "sqlite3_cli.py")
            os.makedirs(os.path.join(d, "_bin"), exist_ok=True)
            with open(os.path.join(d, "_bin", "sqlite3"), "w") as f:
                f.write('#!/bin/sh\nexec "%s" "%s" "$@"\n' % (sys.executable, os.path.abspath(cli)))
            os.chmod(os.path.join(d, "_bin", "sqlite3"), 0o755)
            ambiente["PATH"] = os.path.join(d, "_bin") + os.pathsep + ambiente.get("PATH", "")
        if "mysqli" in subprocess.run(["php", "-m"], capture_output=True, text=True).stdout.split():
            # su Jobe mysqli non c'è (la facciata del prototipo la sostituisce): qui php parte senza estensioni
            os.makedirs(os.path.join(d, "_bin"), exist_ok=True)
            with open(os.path.join(d, "_bin", "php"), "w") as f:
                f.write('#!/bin/sh\nexec "%s" -n "$@"\n' % shutil.which("php"))
            os.chmod(os.path.join(d, "_bin", "php"), 0o755)
            ambiente["PATH"] = os.path.join(d, "_bin") + os.pathsep + ambiente.get("PATH", "")
        if senza_node:
            ambiente["PATH"] = "/usr/bin:/bin"   # come un Jobe senza node nel PATH
        r = subprocess.run([sys.executable, "-I", "__tester__.python3"], cwd=d, env=ambiente,
                           capture_output=True, text=True, timeout=20)
    if r.stderr:
        print("STDERR:", r.stderr)
    parti = r.stdout.split(SEPARATORE + "\n")
    return [p.rstrip("\n") for p in parti]
