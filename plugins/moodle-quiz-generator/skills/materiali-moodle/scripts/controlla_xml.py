#!/usr/bin/env python3
"""Controlla un file Moodle XML (esportato da Moodle o prodotto da un'altra
skill) con le regole della skill: Cloze, emoji, tag vietati, residui di escaping.

Uso:
    python3 controlla_xml.py FILE.xml [--avvisi]

Senza --avvisi mostra solo gli errori.
"""
import pathlib
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import moodle_lib as ml  # noqa: E402


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mostra_avvisi = "--avvisi" in sys.argv
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    radice = ET.parse(args[0]).getroot()
    categoria, n_dom, n_err, n_avv = "", 0, 0, 0
    for q in radice.findall("question"):
        tipo = q.get("type")
        if tipo == "category":
            categoria = q.findtext("category/text") or ""
            continue
        n_dom += 1
        nome = (q.findtext("name/text") or "").strip()
        testo = q.findtext("questiontext/text") or ""
        errori, avvisi = ml.controlla_html(testo, tipo)
        if tipo == "cloze":
            e, a = ml.controlla_cloze(testo)
            errori += e; avvisi += a
        for fb in q.iter("feedback"):
            t = fb.findtext("text") or ""
            if "\\/" in t:
                avvisi.append("feedback con barra rovesciata davanti a /")
        if errori or (mostra_avvisi and avvisi):
            print("\n[%s] %s\n    categoria: %s" % (tipo, nome, categoria))
            for e in errori:
                print("    ERRORE: " + e)
            if mostra_avvisi:
                for a in avvisi:
                    print("    avviso: " + a)
        n_err += len(errori); n_avv += len(avvisi)
    print("\n%d domande controllate: %d errori, %d avvisi%s" % (
        n_dom, n_err, n_avv, "" if mostra_avvisi else " (usa --avvisi per vederli)"))


if __name__ == "__main__":
    main()
