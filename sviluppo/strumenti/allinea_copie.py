#!/usr/bin/env python3
"""Tiene allineate le copie dei file condivisi tra le skill del plugin.

Ogni skill deve funzionare da sola, quindi alcuni file stanno in più skill. La copia di
riferimento è una sola (ORIGINALI); le altre si rigenerano da lei con un'intestazione che
dice da dove vengono. Non modificare mai una copia: modifica l'originale e rilancia.

Uso (dalla radice del repository):
    python3 sviluppo/strumenti/allinea_copie.py              aggiorna le copie
    python3 sviluppo/strumenti/allinea_copie.py --controlla  segnala le copie diverse
                                                             (esce con 1: da usare prima di
                                                             una nuova versione del plugin)
"""
import pathlib
import sys

RADICE = pathlib.Path(__file__).resolve().parents[2]
SKILL = RADICE / "plugins" / "moodle-quiz-generator" / "skills"

# originale -> copie (percorsi relativi a skills/)
ORIGINALI = {
    "materiali-moodle/scripts/moodle_lib.py": [
        "domande-coderunner-js/scripts/moodle_lib.py",
        "domande-coderunner-sql/scripts/moodle_lib.py",
        "domande-php-mysqli-mock/scripts/moodle_lib.py",
    ],
}

INTESTAZIONE = ("# COPIA di {orig}: non modificarla qui. Si rigenera con\n"
                "# sviluppo/strumenti/allinea_copie.py dalla radice del repository.\n")


def contenuto_copia(orig):
    testo = (SKILL / orig).read_text(encoding="utf-8")
    righe = testo.splitlines(keepends=True)
    testa = INTESTAZIONE.format(orig=orig)
    if righe and righe[0].startswith("#!"):          # lo shebang resta in cima
        return righe[0] + testa + "".join(righe[1:])
    return testa + testo


def main():
    controlla = "--controlla" in sys.argv
    diverse = 0
    for orig, copie in ORIGINALI.items():
        atteso = contenuto_copia(orig)
        for c in copie:
            p = SKILL / c
            attuale = p.read_text(encoding="utf-8") if p.exists() else None
            if attuale == atteso:
                print("ok         %s" % c)
                continue
            diverse += 1
            if controlla:
                print("DIVERSA    %s (originale: %s)" % (c, orig))
            else:
                p.write_text(atteso, encoding="utf-8")
                print("aggiornata %s" % c)
    if controlla and diverse:
        sys.exit(1)


if __name__ == "__main__":
    main()
