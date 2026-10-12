#!/usr/bin/env python3
"""Aggiorna catalogo.json (letto dalla pagina «Database didattici») dalle cartelle prodotte da costruisci.py.

Uso:  python3 catalogo.py CARTELLA_DATABASE CATALOGO.json
CARTELLA_DATABASE contiene <nome>/<taglia>/info.json. Nel catalogo ogni database ha le sue taglie
in ordine piccolo, medio, grande, con i percorsi dei file relativi alla pagina (database/<nome>/<taglia>/…).
"""
import glob
import json
import os
import sys

ORDINE = {"piccolo": 0, "medio": 1, "grande": 2}


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    radice, uscita = sys.argv[1:]
    db = {}
    for p in sorted(glob.glob(os.path.join(radice, "*", "*", "info.json"))):
        info = json.load(open(p, encoding="utf-8"))
        cart = os.path.relpath(os.path.dirname(p), os.path.dirname(os.path.abspath(radice)))
        info["percorso"] = cart.replace(os.sep, "/")
        d = db.setdefault(info["nome"], {"nome": info["nome"], "titolo": info["titolo"],
                                         "contesto": info["contesto"], "taglie": []})
        d["taglie"].append(info)
    for d in db.values():
        d["taglie"].sort(key=lambda t: ORDINE.get(t["taglia"], 9))
    json.dump({"database": sorted(db.values(), key=lambda d: d["titolo"])}, open(uscita, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("OK: %d database, %d taglie -> %s" % (len(db), sum(len(d["taglie"]) for d in db.values()), uscita))


if __name__ == "__main__":
    main()
