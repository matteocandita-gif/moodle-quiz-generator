"""Costruisce l'interfaccia html_sito di CodeRunner dai sorgenti di questa cartella.

    python3 build.py

Il codice sta in modulo.js, lo stile in stile.css: si modificano lì, mai nel file costruito.
Scrive ui_html_sito.js negli asset del plugin (materiali-moodle/assets/interfaccia-html-sito/),
con la versione presa da VERSIONE qui sotto: alzala a ogni modifica, così i browser non usano la copia vecchia."""
import json
import os

VERSIONE = "0.8.0"

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
DEST = os.path.join(RADICE, "plugins", "moodle-quiz-generator", "skills", "materiali-moodle", "assets",
                    "interfaccia-html-sito", "ui_html_sito.js")

modulo = open(os.path.join(QUI, "modulo.js"), encoding="utf-8").read()
stile = open(os.path.join(QUI, "stile.css"), encoding="utf-8").read()
for segnaposto in ("__VERSIONE__", "__STILE__"):
    if segnaposto not in modulo:
        raise SystemExit("modulo.js: manca il segnaposto %s" % segnaposto)
uscita = modulo.replace("__VERSIONE__", VERSIONE).replace("__STILE__", json.dumps(stile, ensure_ascii=False))
with open(DEST, "w", encoding="utf-8") as f:
    f.write(uscita)
print("scritto %s (%d caratteri, versione %s)" % (os.path.relpath(DEST, RADICE), len(uscita), VERSIONE))
