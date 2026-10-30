#!/usr/bin/env python3
"""Tiene allineate le copie dei file condivisi tra le skill del plugin.

Ogni skill deve funzionare da sola, quindi alcuni file stanno in più skill. La copia di
riferimento è una sola (ORIGINALI); le altre si rigenerano da lei con un'intestazione che
dice da dove vengono. Non modificare mai una copia: modifica l'originale e rilancia.

Uso (dalla radice del repository):
    python3 sviluppo/strumenti/allinea_copie.py              aggiorna le copie e i blocchi
                                                             condivisi nelle pagine (BLOCCHI)
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
    "progettazione-quiz/references/navigazione.md": [
        "correzione-verifiche/references/navigazione.md",
        "mappe-prerequisiti/references/navigazione.md",
    ],
}

INTESTAZIONE = ("# COPIA di {orig}: non modificarla qui. Si rigenera con\n"
                "# sviluppo/strumenti/allinea_copie.py dalla radice del repository.\n")

# blocchi condivisi dentro le pagine: originale (relativo alla radice) -> pagine (relative alla radice).
# Nella pagina il blocco sta tra la riga che comincia con INIZIO e quella con FINE, che
# sono anche la prima e l'ultima riga dell'originale.
BLOCCHI = {
    "sviluppo/strumenti/barra-navigazione.html": [
        "plugins/moodle-quiz-generator/skills/progettazione-quiz/assets/dashboard.html",
        "plugins/moodle-quiz-generator/skills/correzione-verifiche/assets/dashboard-correzioni.html",
        "sviluppo/mappe-prerequisiti/editor.src.html",
        "plugins/moodle-quiz-generator/skills/mappe-prerequisiti/assets/editor.html",
        "plugins/moodle-quiz-generator/skills/tracce-progettazione/assets/dashboard-tracce.html",
    ],
}
# file JavaScript inclusi interi in una pagina, tra le righe «/* incluso: NOME — inizio */» e «… — fine */»
INCLUSI = {
    "plugins/moodle-quiz-generator/skills/tracce-progettazione/scripts/uscite_traccia.js": [
        "plugins/moodle-quiz-generator/skills/tracce-progettazione/assets/dashboard-tracce.html",
    ],
}
INIZIO, FINE = "<!-- barra-navigazione: inizio", "<!-- barra-navigazione: fine -->"


def contenuto_copia(orig):
    testo = (SKILL / orig).read_text(encoding="utf-8")
    righe = testo.splitlines(keepends=True)
    testa = INTESTAZIONE.format(orig=orig)
    if orig.endswith(".md"):                          # nel Markdown un commento HTML
        testa = "<!-- " + testa.replace("# ", "").replace("\n", " ").strip() + " -->\n"
    if righe and righe[0].startswith("#!"):          # lo shebang resta in cima
        return righe[0] + testa + "".join(righe[1:])
    return testa + testo


def con_blocco(pagina, blocco, incluso=None):
    """La pagina con il blocco sostituito; None se mancano i segnaposto."""
    ini, fin = (("/* incluso: %s — inizio */" % incluso, "/* incluso: %s — fine */" % incluso) if incluso
                else (INIZIO, FINE))
    righe = pagina.splitlines(keepends=True)
    i = next((k for k, r in enumerate(righe) if r.lstrip().startswith(ini)), None)
    j = next((k for k, r in enumerate(righe) if r.lstrip().startswith(fin)), None)
    if i is None or j is None or j < i:
        return None
    return "".join(righe[:i]) + blocco + "".join(righe[j + 1:])


def allinea_blocchi(controlla):
    diverse = 0
    voci = [(o, pg, None) for o, pp in BLOCCHI.items() for pg in pp] + \
           [(o, pg, pathlib.Path(o).name) for o, pp in INCLUSI.items() for pg in pp]
    for orig, pg, incluso in voci:
        blocco = (RADICE / orig).read_text(encoding="utf-8")
        if not blocco.endswith("\n"):
            blocco += "\n"
        if incluso:
            # il file intero, tra i due commenti che lo delimitano nella pagina (che restano)
            blocco = "/* incluso: %s — inizio */\n%s/* incluso: %s — fine */\n" % (incluso, blocco, incluso)
        for pg in [pg]:
            p = (RADICE / pg).resolve()
            nome = p.relative_to(RADICE)
            attuale = p.read_text(encoding="utf-8")
            atteso = con_blocco(attuale, blocco, incluso)
            if atteso is None:
                diverse += 1
                print("SEGNAPOSTO MANCANTE %s" % nome)
                continue
            if atteso == attuale:
                print("ok         %s" % nome)
                continue
            diverse += 1
            if controlla:
                print("DIVERSA    %s (blocco: %s)" % (nome, orig))
            else:
                p.write_text(atteso, encoding="utf-8")
                print("aggiornata %s" % nome)
    return diverse


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
    diverse += allinea_blocchi(controlla)
    if controlla and diverse:
        sys.exit(1)


if __name__ == "__main__":
    main()
