#!/usr/bin/env python3
"""Unisce più file Moodle XML (di questa skill o delle skill CodeRunner) in un
unico file da importare, nell'ordine dato.

Uso:
    python3 unisci_xml.py USCITA.xml FILE1.xml FILE2.xml ... [--categoria "Nome"]

Con --categoria toglie le categorie dei singoli file e mette tutte le domande
nella categoria indicata ("Nome" diventa $module$/top/Nome, se non inizia con $).
Senza, conserva le categorie dei file. Segnala i nomi di domanda ripetuti.
"""
import pathlib
import re
import sys
import xml.dom.minidom

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import moodle_lib as ml  # noqa: E402

DOMANDA_RE = re.compile(r"<question type=\"([\w-]+)\">[\s\S]*?</question>")


def main():
    args = sys.argv[1:]
    categoria = None
    if "--categoria" in args:
        i = args.index("--categoria")
        categoria = args[i + 1]
        del args[i:i + 2]
    if len(args) < 3:
        print(__doc__)
        sys.exit(2)
    uscita, sorgenti = args[0], args[1:]
    pezzi = ['<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n']
    if categoria:
        pezzi.append(ml.xml_categoria(ml.percorso_categoria(categoria)))
    nomi, totale = {}, 0
    for f in sorgenti:
        testo = pathlib.Path(f).read_text(encoding="utf-8")
        n = 0
        for m in DOMANDA_RE.finditer(testo):
            if m.group(1) == "category" and categoria:
                continue
            pezzi.append("  " + m.group(0) + "\n\n")
            if m.group(1) != "category":
                n += 1
                nome = re.search(r"<name>\s*<text>([\s\S]*?)</text>", m.group(0))
                nome = nome.group(1).strip() if nome else "?"
                nomi.setdefault(nome, []).append(pathlib.Path(f).name)
        print("%-40s %d domande" % (pathlib.Path(f).name, n))
        totale += n
    pezzi.append("</quiz>\n")
    risultato = "".join(pezzi)
    xml.dom.minidom.parseString(risultato.encode("utf-8"))
    ripetuti = {k: v for k, v in nomi.items() if len(v) > 1}
    for k, v in ripetuti.items():
        print("AVVISO: nome ripetuto '%s' in %s" % (k, ", ".join(v)))
    pathlib.Path(uscita).write_text(risultato, encoding="utf-8")
    print("OK: %d domande -> %s" % (totale, uscita))


if __name__ == "__main__":
    main()
