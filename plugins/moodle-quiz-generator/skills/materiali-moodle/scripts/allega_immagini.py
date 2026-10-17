#!/usr/bin/env python3
"""Incorpora nel Moodle XML le immagini riferite nel testo delle domande.

Uso:
    python3 allega_immagini.py DOMANDE.xml CARTELLA [--uscita=ALTRO.xml]

Nelle tracce della dashboard un'immagine si scrive ![testo alternativo](nome.png); da_dashboard.py la
trasforma in <img src="@@PLUGINFILE@@/nome.png" ...>. Questo script cerca quei riferimenti nel testo di
ogni domanda (questiontext) e aggiunge dentro <questiontext> l'elemento

    <file name="nome.png" path="/" encoding="base64">...</file>

con il contenuto preso da CARTELLA: è la forma con cui Moodle esporta e importa le immagini di una
domanda. crea_mbz.py legge poi quei <file> e li mette nel backup (componente question, area questiontext).

Si ferma se un'immagine manca nella cartella o se un riferimento sta fuori dal testo della domanda
(feedback, risposte): lì le immagini non sono gestite. Senza riferimenti non cambia nulla.
"""
import base64
import os
import re
import sys
import urllib.parse

RIF_RE = re.compile(r"@@PLUGINFILE@@/([^\"'\s<>)]+)")
QT_RE = re.compile(r"(<questiontext\b[^>]*>)(.*?)(</questiontext>)", re.S)
Q_RE = re.compile(r"<question\b.*?</question>", re.S)


def nome_domanda(blocco):
    m = re.search(r"<name>\s*<text>(.*?)</text>", blocco, re.S)
    return m.group(1).strip() if m else "?"


def allega(xml, cartella):
    errori, usate = [], []

    def domanda(mq):
        blocco = mq.group(0)
        nome = nome_domanda(blocco)
        fatto = []

        def testo(mt):
            apri, corpo, chiudi = mt.groups()
            gia = set(re.findall(r'<file name="([^"]+)"', corpo))
            nuovi = ""
            for rif in dict.fromkeys(RIF_RE.findall(corpo)):
                f = urllib.parse.unquote(rif)
                fatto.append(f)
                if f in gia:
                    continue
                p = os.path.join(cartella, f)
                if not os.path.isfile(p):
                    errori.append("%s: manca l'immagine «%s» in %s" % (nome, f, cartella))
                    continue
                b64 = base64.b64encode(open(p, "rb").read()).decode("ascii")
                nuovi += '\n    <file name="%s" path="/" encoding="base64">%s</file>' % (f, b64)
                usate.append(f)
            return apri + corpo.rstrip() + nuovi + "\n  " + chiudi if nuovi else mt.group(0)

        nuovo = QT_RE.sub(testo, blocco, count=1)
        resto = QT_RE.sub("", nuovo, count=1)
        for rif in RIF_RE.findall(resto):
            errori.append("%s: immagine «%s» fuori dal testo della domanda (feedback o risposte): non gestita"
                          % (nome, urllib.parse.unquote(rif)))
        return nuovo

    out = Q_RE.sub(domanda, xml)
    return out, usate, errori


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) != 2:
        raise SystemExit(__doc__)
    src, cartella = a
    opz = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    xml = open(src, encoding="utf-8").read()
    out, usate, errori = allega(xml, cartella)
    if errori:
        raise SystemExit("ERRORE immagini:\n  " + "\n  ".join(errori))
    open(opz.get("uscita", src), "w", encoding="utf-8").write(out)
    print("OK: %d immagini incorporate (%d file diversi)" % (len(usate), len(set(usate))))


if __name__ == "__main__":
    main()
