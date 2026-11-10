#!/usr/bin/env python3
"""Aggiorna il risultato atteso dei quiz di prova. Si usa SOLO quando una modifica cambia apposta
le domande generate, e DOPO che l'utente ha visto la differenza e ha detto che va bene.

    python3 sviluppo/prove/aggiorna_atteso.py                      mostra che cosa cambierebbe, senza scrivere
    python3 sviluppo/prove/aggiorna_atteso.py --ok-dell-utente     scrive i nuovi file in sviluppo/prove/atteso/

Non usarlo per far passare una prova che fallisce senza un motivo che l'utente conosce.
"""
import sys

import prova_tutto as pt


def main():
    scrivi = "--ok-dell-utente" in sys.argv
    cambiati = 0
    for q in pt.QUIZ:
        ok, messaggi, testi = pt.quiz_generato(q)
        if not ok:
            sys.exit("Il quiz di prova «%s» non si genera: prima correggi l'errore.\n%s" % (q, messaggi[-800:]))
        for testo, suffisso in zip(testi, (".struttura.txt", ".output.txt")):
            f = pt.ATTESO / (q + suffisso)
            vecchio = f.read_text(encoding="utf-8") if f.exists() else ""
            if testo == vecchio:
                continue
            cambiati += 1
            print("== %s cambia:\n%s" % (f.name, pt.differenza(vecchio, testo, f.name)))
            if scrivi:
                f.write_text(testo, encoding="utf-8")
    if not cambiati:
        print("Niente da aggiornare: il risultato è già quello atteso.")
    elif scrivi:
        print("\nAggiornati %d file. Scrivi nel CHANGELOG che cosa è cambiato nelle domande generate e perché." % cambiati)
    else:
        print("\n%d file cambierebbero. Mostra queste differenze all'utente; con il suo ok rilancia con --ok-dell-utente." % cambiati)


if __name__ == "__main__":
    main()
