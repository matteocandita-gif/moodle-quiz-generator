#!/usr/bin/env python3
"""Dal file scaricato dalla dashboard «Bozze dei quiz» alla cartella di esportazione che usano gli script.

Uso:
    python3 spacchetta_quiz.py FILE.quiz.json CARTELLA

FILE.quiz.json  il file del pulsante «Scarica il quiz» della dashboard: un solo file con il quiz, tutte le
                sue righe e le impostazioni che servono a generare (depositi, Safe Exam Browser, domanda
                delle note, descrizioni PDP)
CARTELLA        dove scrivere l'esportazione, nella stessa forma di ArtifactData con out_dir:
                CARTELLA/quiz/<id>.json, CARTELLA/quiz/<id>/domande/<riga>.json, CARTELLA/impostazioni/<nome>.json

Stampa l'id del quiz, quante righe ha e quando è stato scaricato. Se il file ha più di un'ora avvisa:
la dashboard può essere cambiata nel frattempo, e conviene farsi mandare un file nuovo.

Di solito non serve lanciarlo a mano: genera_quiz.py accetta direttamente il file
(python3 genera_quiz.py FILE.quiz.json USCITA ...).
"""
import datetime
import json
import os
import re
import shutil
import sys

FORMATO = "bozze-dei-quiz"
VECCHIO_DOPO_MINUTI = 60
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")


def leggi(percorso):
    """Il contenuto del file, controllato. Si ferma con un messaggio chiaro se non è il file della dashboard."""
    try:
        with open(percorso, encoding="utf-8-sig") as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        raise SystemExit("ERRORE: non riesco a leggere %s come file della dashboard (%s). Serve il file del "
                         "pulsante «Scarica il quiz», non modificato." % (percorso, e))
    if not isinstance(d, dict) or d.get("formato") != FORMATO:
        raise SystemExit("ERRORE: %s non è un file scaricato dalla dashboard «Bozze dei quiz» (manca "
                         "\"formato\": \"%s\")." % (percorso, FORMATO))
    quiz, righe = d.get("quiz"), d.get("domande")
    if not isinstance(quiz, dict) or not ID_RE.fullmatch(str(quiz.get("id") or "")):
        raise SystemExit("ERRORE: nel file manca il quiz, o il suo id non è valido.")
    if not isinstance(righe, list) or not righe:
        raise SystemExit("ERRORE: il quiz «%s» nel file non ha righe." % quiz["id"])
    for r in righe:
        if not isinstance(r, dict) or not ID_RE.fullmatch(str(r.get("id") or "")):
            raise SystemExit("ERRORE: una riga del file non ha un id valido.")
    imp = d.get("impostazioni") or {}
    if not isinstance(imp, dict) or not all(ID_RE.fullmatch(str(k)) for k in imp):
        raise SystemExit("ERRORE: le impostazioni nel file non sono valide.")
    return d


def minuti_da(iso):
    """Minuti passati dall'ora scritta nel file (None se l'ora manca o non si legge)."""
    try:
        t = datetime.datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=datetime.timezone.utc)
    return (datetime.datetime.now(datetime.timezone.utc) - t).total_seconds() / 60


def spacchetta(percorso, cartella):
    """Scrive l'esportazione in cartella e restituisce (id del quiz, righe di messaggio da stampare)."""
    d = leggi(percorso)
    quiz = dict(d["quiz"])
    qid = quiz.pop("id")
    base = os.path.join(cartella, "quiz")
    shutil.rmtree(os.path.join(base, qid), ignore_errors=True)   # niente righe rimaste da un file precedente
    os.makedirs(os.path.join(base, qid, "domande"), exist_ok=True)

    def scrivi(p, dati):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(dati, f, ensure_ascii=False, indent=1)

    scrivi(os.path.join(base, qid + ".json"), quiz)
    for r in d["domande"]:
        r = dict(r)
        rid = r.pop("id")
        scrivi(os.path.join(base, qid, "domande", rid + ".json"), r)
    imp = {k: v for k, v in (d.get("impostazioni") or {}).items() if isinstance(v, dict)}
    if imp:
        os.makedirs(os.path.join(cartella, "impostazioni"), exist_ok=True)
        for nome, dati in imp.items():
            scrivi(os.path.join(cartella, "impostazioni", nome + ".json"), dati)

    msg = ["OK: quiz «%s» (id %s), %d righe%s -> %s"
           % (quiz.get("titolo") or qid, qid, len(d["domande"]),
              (", impostazioni: " + ", ".join(sorted(imp))) if imp else "", cartella)]
    m = minuti_da(d.get("scaricato"))
    if m is None:
        msg.append("ATTENZIONE: nel file non c'è l'ora dello scaricamento: non si sa se la dashboard è cambiata dopo.")
    elif m > VECCHIO_DOPO_MINUTI:
        eta = "%d ore" % round(m / 60) if m < 48 * 60 else "%d giorni" % round(m / 1440)
        msg.append("ATTENZIONE: il file è stato scaricato circa %s fa. Se da allora il quiz è stato modificato "
                   "nella dashboard o in chat, il backup non lo contiene: chiedi all'utente un file nuovo." % eta)
    else:
        msg.append("Scaricato %d minuti fa (pagina %s)." % (max(0, round(m)), d.get("pagina") or "?"))
    return qid, msg


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) != 2:
        raise SystemExit(__doc__)
    qid, msg = spacchetta(a[0], a[1])
    print("\n".join(msg))


if __name__ == "__main__":
    main()
