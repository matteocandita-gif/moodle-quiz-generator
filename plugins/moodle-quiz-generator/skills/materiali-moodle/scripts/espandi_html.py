#!/usr/bin/env python3
"""Prepara una pagina HTML da incollare in Moodle (attività Pagina, Area di
testo e media, descrizione): espande i blocchi [[codice LINGUA]] ... [[/codice]]
e controlla che sia un frammento nello stile della skill.

Uso:
    python3 espandi_html.py SORGENTE.html USCITA.html
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import moodle_lib as ml  # noqa: E402


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sorgente = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    pagina = ml.espandi_codice(sorgente)
    errori, avvisi = ml.controlla_html(pagina, "pagina")
    avvisi += ml.AVVISI_LETTURA
    if ml.campi_cloze(pagina):
        e, a = ml.controlla_cloze(pagina)
        errori += e; avvisi += a
    for a in avvisi:
        print("AVVISO: " + a)
    if errori:
        print("ERRORI (pagina non scritta):")
        for e in errori:
            print("  - " + e)
        sys.exit(1)
    pathlib.Path(sys.argv[2]).write_text(pagina, encoding="utf-8")
    print("OK -> %s" % sys.argv[2])


if __name__ == "__main__":
    main()
