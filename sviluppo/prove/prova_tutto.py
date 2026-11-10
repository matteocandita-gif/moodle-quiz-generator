#!/usr/bin/env python3
"""Prove del plugin prima di un rilascio. Uso, dalla radice del repository:

    python3 sviluppo/prove/prova_tutto.py

Stampa «TUTTO A POSTO» oppure l'elenco dei problemi, ognuno con che cosa fare.
Lo script è volutamente semplice: una lista di controlli indipendenti (CONTROLLI, in fondo).
Ogni controllo restituisce una lista di messaggi; lista vuota = controllo superato.

NON modificare questo script per far passare una prova. Se una prova fallisce:
  - o la modifica appena fatta ha un errore (correggi la modifica),
  - o il cambiamento è voluto (mostra la differenza all'utente e, solo con il suo ok,
    aggiorna il risultato atteso con sviluppo/prove/aggiorna_atteso.py).
"""
import difflib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

RADICE = pathlib.Path(__file__).resolve().parents[2]
SKILL = RADICE / "plugins" / "moodle-quiz-generator" / "skills"
PROVE = RADICE / "sviluppo" / "prove"
EXPORT = PROVE / "export"            # i quiz di prova, nella forma dell'esportazione della dashboard
ATTESO = PROVE / "atteso"            # il risultato giusto, salvato
QUIZ = ["prova", "verprova"]         # prova: tutte le tipologie; verprova: verifica con varianti per tag


# ------------------------------------------------------------------ generazione dei quiz di prova
def genera(quiz, cartella):
    """Genera un quiz di prova con genera_quiz.py. Restituisce (riuscito, messaggi dello script)."""
    r = subprocess.run([sys.executable, str(SKILL / "materiali-moodle" / "scripts" / "genera_quiz.py"),
                        str(EXPORT), quiz, str(cartella), "--nome=" + quiz], capture_output=True, text=True)
    return r.returncode == 0 and (cartella / (quiz + ".xml")).exists(), r.stdout + r.stderr


def struttura_e_output(quiz, cartella):
    """Divide il risultato in due testi da confrontare:
    - struttura: l'XML delle domande e l'impaginazione, senza le parti che dipendono dal computer
      (output calcolati eseguendo le soluzioni, file dei database allegati);
    - output: gli output attesi dei test CodeRunner, calcolati con Node, PHP e SQLite."""
    xml = (cartella / (quiz + ".xml")).read_text(encoding="utf-8")
    output = []

    def togli_output(m):
        output.append(m.group(1).strip())
        return "<expected>[output %d]</expected>" % len(output)
    struttura = re.sub(r"<expected>(.*?)</expected>", togli_output, xml, flags=re.S)
    struttura = re.sub(r"(<file [^>]*>)[^<]*(</file>)", r"\1[file]\2", struttura)
    imp = json.loads((cartella / "impaginazione.json").read_text(encoding="utf-8"))
    struttura += "\n\n=== impaginazione ===\n" + json.dumps(imp, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    testo_output = "".join("--- output %d ---\n%s\n" % (i + 1, o) for i, o in enumerate(output))
    return struttura, testo_output


def differenza(atteso, ottenuto, nome):
    righe = list(difflib.unified_diff(atteso.splitlines(), ottenuto.splitlines(), "atteso/" + nome, "ottenuto", lineterm="", n=1))
    return "\n".join("      " + r[:200] for r in righe[:40]) + ("\n      … (altre differenze)" if len(righe) > 40 else "")


_generati = {}


def quiz_generato(quiz):
    if quiz not in _generati:
        cartella = pathlib.Path(tempfile.mkdtemp(prefix="prova-" + quiz + "-"))
        ok, messaggi = genera(quiz, cartella)
        _generati[quiz] = (ok, messaggi, struttura_e_output(quiz, cartella) if ok else None)
    return _generati[quiz]


# ------------------------------------------------------------------ i controlli
def controllo_programmi():
    """Node e PHP servono per calcolare gli output delle domande CodeRunner."""
    return ["Manca il programma «%s» in questo ambiente: installalo e rilancia. Non è un errore del plugin." % p
            for p in ("node", "php") if not shutil.which(p)]


def controllo_copie():
    """I file condivisi tra più skill devono essere uguali all'originale."""
    r = subprocess.run([sys.executable, str(RADICE / "sviluppo" / "strumenti" / "allinea_copie.py"), "--controlla"],
                       capture_output=True, text=True)
    diverse = [l for l in r.stdout.splitlines() if not l.startswith("ok")]
    if not diverse:
        return []
    return ["Copie non allineate:\n      " + "\n      ".join(diverse) +
            "\n   CHE COSA FARE: hai modificato un originale (o per errore una copia). Lancia "
            "«python3 sviluppo/strumenti/allinea_copie.py» e controlla con git diff che le copie abbiano preso la modifica giusta."]


def controllo_file_citati():
    """Ogni file citato nelle skill come `references/…`, `scripts/…` o `assets/…` deve esistere."""
    esistenti = {(p.parent.name, p.name) for p in SKILL.rglob("*") if p.is_file()}
    problemi, visti = [], set()
    for md in sorted(SKILL.rglob("*.md")):
        for cart, nome in re.findall(r"`(references|scripts|assets)/([\w.\-]+\.\w+)`", md.read_text(encoding="utf-8")):
            if (cart, nome) not in esistenti and (md, cart, nome) not in visti:
                visti.add((md, cart, nome))
                problemi.append("%s cita `%s/%s`, che non esiste.\n   CHE COSA FARE: il file è stato rinominato o spostato? "
                                "Correggi il nome citato (o ripristina il file)." % (md.relative_to(SKILL), cart, nome))
    return problemi


def controllo_tipologie():
    """Ogni tipologia di domanda che la dashboard conosce deve avere una riga nel quiz di prova."""
    sys.path.insert(0, str(SKILL / "materiali-moodle" / "scripts"))
    import da_dashboard
    conosciute = set(da_dashboard.CATALOGO) | set(da_dashboard.CODERUNNER)
    provate = {json.loads(p.read_text(encoding="utf-8")).get("tipologia") for p in EXPORT.glob("quiz/*/domande/*.json")}
    mancanti = sorted(conosciute - provate)
    if not mancanti:
        return []
    return ["Tipologie senza una riga nel quiz di prova: %s.\n   CHE COSA FARE: aggiungi a sviluppo/prove/export/quiz/prova/domande/ "
            "una riga per ognuna (copia un file vicino e cambialo), poi aggiorna il risultato atteso come dice "
            "sviluppo/prove/README.md." % ", ".join(mancanti)]


def controllo_generazione():
    """I quiz di prova si devono generare senza errori."""
    problemi = []
    for q in QUIZ:
        ok, messaggi, _ = quiz_generato(q)
        if not ok:
            problemi.append("Il quiz di prova «%s» non si genera più. Ultime righe dello script:\n      %s\n"
                            "   CHE COSA FARE: è quasi sempre un errore nella modifica appena fatta a uno script o a una convenzione. "
                            "Leggi il messaggio e correggi la modifica." % (q, "\n      ".join(messaggi.strip().splitlines()[-8:])))
    return problemi


def controllo_struttura():
    """Testo delle domande, risposte, punti, pagine e sezioni devono essere quelli attesi."""
    problemi = []
    for q in QUIZ:
        ok, _, testi = quiz_generato(q)
        if not ok:
            continue
        atteso = (ATTESO / (q + ".struttura.txt")).read_text(encoding="utf-8")
        if testi[0] != atteso:
            problemi.append("Il quiz di prova «%s» produce domande diverse da quelle attese:\n%s\n"
                            "   CHE COSA FARE: se la modifica che stai facendo NON doveva cambiare le domande generate, è un errore: "
                            "correggi la modifica. Se doveva cambiarle, NON aggiornare da solo il risultato atteso: mostra questa "
                            "differenza all'utente e, con il suo ok, usa sviluppo/prove/aggiorna_atteso.py."
                            % (q, differenza(atteso, testi[0], q + ".struttura.txt")))
    return problemi


def controllo_output():
    """Gli output dei test CodeRunner (calcolati con Node, PHP e SQLite) devono essere quelli attesi."""
    problemi = []
    for q in QUIZ:
        ok, _, testi = quiz_generato(q)
        if not ok:
            continue
        atteso = (ATTESO / (q + ".output.txt")).read_text(encoding="utf-8")
        if testi[1] != atteso:
            problemi.append("Il quiz di prova «%s» calcola output diversi da quelli attesi:\n%s\n"
                            "   CHE COSA FARE: questi output dipendono anche dal computer (versioni di Node, PHP e SQLite). "
                            "Se il controllo «domande generate» qui sopra è superato e non hai toccato gli script che eseguono "
                            "le soluzioni, la causa probabile è l'ambiente: dillo all'utente con la differenza, senza cambiare "
                            "niente. Altrimenti è un errore della modifica."
                            % (q, differenza(atteso, testi[1], q + ".output.txt")))
    return problemi


CONTROLLI = [
    ("Programmi necessari (Node, PHP)", controllo_programmi),
    ("Copie dei file condivisi allineate", controllo_copie),
    ("File citati nelle skill esistenti", controllo_file_citati),
    ("Ogni tipologia ha una riga nel quiz di prova", controllo_tipologie),
    ("I quiz di prova si generano", controllo_generazione),
    ("Domande generate uguali a quelle attese", controllo_struttura),
    ("Output dei test CodeRunner uguali a quelli attesi", controllo_output),
]


def main():
    falliti = 0
    for titolo, controllo in CONTROLLI:
        problemi = controllo()
        print("%s  %s" % ("ok      " if not problemi else "PROBLEMA", titolo))
        for p in problemi:
            print("   " + p)
        falliti += bool(problemi)
    print()
    if falliti:
        print("%d controlli con problemi: NON rilasciare finché non sono risolti o spiegati all'utente." % falliti)
        sys.exit(1)
    print("TUTTO A POSTO: %d controlli superati." % len(CONTROLLI))


if __name__ == "__main__":
    main()
