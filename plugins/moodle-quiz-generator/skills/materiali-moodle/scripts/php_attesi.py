#!/usr/bin/env python3
"""Calcola gli output attesi delle domande PHP (prototipo php_mysqli_sqlite) eseguendo la soluzione
con il template del prototipo, come fa Jobe, e li scrive al posto del segnaposto @@CALCOLA@@.

Uso:  python3 php_attesi.py SPECIFICA-PHP.txt [--php=CARTELLA_SCRIPTS_DELLA_SKILL_PHP]

SPECIFICA-PHP.txt è nel formato di domande-php-mysqli-mock (la scrive da_dashboard.py): i test senza
output atteso hanno «=== expected» con il solo segnaposto. Serve PHP; se il client sqlite3 manca
(nell'ambiente di Claude) usa sqlite3_cli.py, che sta in questa cartella. Si ferma se l'esecuzione
della soluzione produce avvisi o errori di PHP (non devono mai finire nell'output atteso) o un
errore di FakeDB.
"""
import glob
import os
import pathlib
import shutil
import stat
import sys
import tempfile

QUI = pathlib.Path(__file__).resolve().parent
SEGNAPOSTO = "@@CALCOLA@@"


def cerca_php():
    for pat in [str(QUI.parent.parent / "domande-php-mysqli-mock" / "scripts"),
                str(QUI.parent / "domande-php-mysqli-mock" / "scripts"),
                "/mnt/skills/*/domande-php-mysqli-mock/scripts",
                "/mnt/skills/*/*/domande-php-mysqli-mock/scripts",
                "/root/.claude/skills/*/domande-php-mysqli-mock/scripts",
                "/root/.claude/skills/*/*/domande-php-mysqli-mock/scripts",
                os.path.expanduser("~/.claude/skills/*/*/domande-php-mysqli-mock/scripts")]:
        for d in glob.glob(pat):
            if os.path.exists(os.path.join(d, "crea_xml.py")):
                return os.path.abspath(d)
    return None


def prepara_sqlite3():
    """Se il client sqlite3 non c'è, mette nel PATH un comando sqlite3 che chiama sqlite3_cli.py."""
    if shutil.which("sqlite3"):
        return "client sqlite3 del sistema"
    cart = tempfile.mkdtemp()
    p = os.path.join(cart, "sqlite3")
    with open(p, "w") as f:
        f.write('#!/bin/sh\nexec "%s" "%s" "$@"\n' % (sys.executable, QUI / "sqlite3_cli.py"))
    os.chmod(p, os.stat(p).st_mode | stat.S_IEXEC)
    os.environ["PATH"] = cart + os.pathsep + os.environ.get("PATH", "")
    return "sqlite3_cli.py (SQLite di Python %s)" % __import__("sqlite3").sqlite_version


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) != 1:
        raise SystemExit(__doc__)
    opz = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    sk = opz.get("php") or cerca_php()
    if not sk:
        raise SystemExit("Servono gli script di domande-php-mysqli-mock: indica la cartella con --php=")
    sys.path.insert(0, sk)
    import crea_xml as cx  # noqa: E402  (skill PHP)
    if not shutil.which("php"):
        raise SystemExit("PHP non disponibile: gli output attesi vanno scritti a mano in === expected")
    client = prepara_sqlite3()
    percorso = pathlib.Path(a[0])
    testo = percorso.read_text(encoding="utf-8")
    if SEGNAPOSTO not in testo:
        print("Nessun output da calcolare")
        return
    stato = cx.leggi_specifica(testo)
    lavoro = pathlib.Path(tempfile.mkdtemp())
    dbs = {n: cx.costruisci_db(n, sql, lavoro) for n, sql in stato["database"].items()}
    template = (pathlib.Path(sk).parent / "assets" / cx.TEMPLATE["sqlite"]).read_text(encoding="utf-8")
    calcolati, errori = [], []
    for d in stato["domande"]:
        o = cx.opzioni(d, stato["database"])
        db = dbs.get(o["database"]) if o["database"] else None
        for i, t in enumerate(d["test"], 1):
            if (t["expected"] or "").strip() != SEGNAPOSTO:
                continue
            out = cx.esegui(template, t["testcode"], d["answer"], db)
            bad = [r for r in out.splitlines() if r.startswith("[stderr]") or
                   any(k in r for k in ("Warning:", "Fatal error", "Deprecated:", "Notice:", "FakeDB:"))]
            if bad:
                errori.append("%s, test %d: %s" % (d.get("name"), i, bad[0]))
            calcolati.append(out.rstrip("\n"))
            print("%s, test %d (%s):\n    %s" % (d.get("name"), i, t.get("extra") or "",
                                                 out.rstrip().replace("\n", "\n    ")))
            if d.get("preload"):
                pre = cx.esegui(template, t["testcode"], d["preload"], db).strip().splitlines()
                print("    PRELOAD -> %s" % (pre[0] if pre else "(nessun output)"))
    if errori:
        raise SystemExit("ERRORI eseguendo le soluzioni PHP:\n- " + "\n- ".join(errori))
    pezzi = testo.split(SEGNAPOSTO)
    if len(pezzi) - 1 != len(calcolati):
        raise SystemExit("segnaposto e test non corrispondono (%d e %d)" % (len(pezzi) - 1, len(calcolati)))
    nuovo = pezzi[0] + "".join(c + p for c, p in zip(calcolati, pezzi[1:]))
    percorso.write_text(nuovo, encoding="utf-8")
    print("OK: %d output attesi calcolati con PHP e %s" % (len(calcolati), client))


if __name__ == "__main__":
    main()
