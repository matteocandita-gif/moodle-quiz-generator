"""Prove del template del prototipo html_con_file: lancia le quattro serie di prove e dice se sono tutte superate.

    python3 prove.py

Ogni serie esegue il template come CodeRunner su Jobe (prova.py) su consegne giuste e sbagliate e confronta
l'esito di ogni controllo con quello atteso. Se una serie fallisce, leggi le righe che cominciano con «!!»."""
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
SERIE = ["test_prove.py", "test_css.py", "test_js.py", "test_link.py", "test_stile.py"]
male = []
for nome in SERIE:
    r = subprocess.run([sys.executable, os.path.join(QUI, nome)], cwd=QUI, capture_output=True, text=True)
    fallite = [int(x) for x in re.findall(r"FALLITE: (\d+)", r.stdout)]
    if r.returncode != 0 or not fallite or any(fallite):
        male.append(nome)
        print("== %s: PROBLEMI" % nome)
        print("\n".join(l for l in r.stdout.splitlines() if l.startswith("!!") or "FALLITE" in l))
        print(r.stderr[-2000:])
    else:
        print("== %s: superate" % nome)
print("TUTTO A POSTO" if not male else "DA SISTEMARE: " + ", ".join(male))
sys.exit(1 if male else 0)
