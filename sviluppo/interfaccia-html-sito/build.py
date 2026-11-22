"""Costruisce l'interfaccia html_sito di CodeRunner dai sorgenti di questa cartella.

    python3 build.py

Il codice sta in modulo.js, lo stile in stile.css: si modificano lì, mai nel file costruito.
Scrive ui_html_sito.js negli asset del plugin (materiali-moodle/assets/interfaccia-html-sito/),
con la versione presa da VERSIONE qui sotto: alzala a ogni modifica, così i browser non usano la copia vecchia."""
import json
import os

VERSIONE = "0.12.0"

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
DEST = os.path.join(RADICE, "plugins", "moodle-quiz-generator", "skills", "materiali-moodle", "assets",
                    "interfaccia-html-sito", "ui_html_sito.js")

modulo = open(os.path.join(QUI, "modulo.js"), encoding="utf-8").read()

# Il programma dell'anteprima PHP (anteprima_php.py), con l'avvio di PHP del prototipo php_sito (template.py)
# e la facciata di mysqli di domande-php-mysqli-mock: una sola copia di ognuno, presa dall'originale.
import re
import sys
sys.path.insert(0, os.path.join(RADICE, "sviluppo", "prototipo-html-con-file"))
import facciata  # noqa: E402
template = open(os.path.join(RADICE, "sviluppo", "prototipo-html-con-file", "template.py"), encoding="utf-8").read()
avvio = re.search(r'AVVIO_PHP = r"""(.*?)"""', template, re.S).group(1)
anteprima = open(os.path.join(QUI, "anteprima_php.py"), encoding="utf-8").read()
for segnaposto, valore in (("__AVVIO_PHP__", avvio), ("__FAKEDB_PHP__", facciata.originale())):
    if anteprima.count(segnaposto) != 1:
        raise SystemExit("anteprima_php.py: il segnaposto %s deve comparire una volta" % segnaposto)
    anteprima = anteprima.replace(segnaposto, json.dumps(valore, ensure_ascii=False))
with open(os.path.join(QUI, "prova", "anteprima_php_costruito.py"), "w", encoding="utf-8") as f:
    f.write(anteprima)   # lo stesso programma, per le prove in locale (prova/server_prova.py)
stile = open(os.path.join(QUI, "stile.css"), encoding="utf-8").read()
for segnaposto in ("__VERSIONE__", "__STILE__", "__ANTEPRIMA_PHP__"):
    if segnaposto not in modulo:
        raise SystemExit("modulo.js: manca il segnaposto %s" % segnaposto)
uscita = (modulo.replace("__VERSIONE__", VERSIONE).replace("__STILE__", json.dumps(stile, ensure_ascii=False))
          .replace("__ANTEPRIMA_PHP__", json.dumps(anteprima, ensure_ascii=False)))
with open(DEST, "w", encoding="utf-8") as f:
    f.write(uscita)
print("scritto %s (%d caratteri, versione %s)" % (os.path.relpath(DEST, RADICE), len(uscita), VERSIONE))
