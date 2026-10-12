#!/usr/bin/env python3
"""Esegue una query su un database definito nella specifica, come la vedrebbe
lo studente con il prototipo php_mysqli_sqlite: valori come stringhe PHP,
NULL come null, errori con il messaggio di SQLite.

Uso:
    python3 prova_query.py SPECIFICA.txt NOME_DB "SELECT ..." [--prima "SQL del campo schema"]

Serve a calcolare gli output attesi: le righe, il loro ordine e il formato dei
numeri (12 e 9.5, non 12.00 e 9.50). Il SQLite di Python può essere di una
versione leggermente diversa da quello di Jobe: il controllo definitivo resta
Validate on save.
"""
import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from crea_xml import leggi_specifica  # noqa: E402


def come_php(v):
    if v is None:
        return None
    if isinstance(v, float):
        testo = format(v, ".14g")          # PHP: (string) di un float, precision 14
        return testo
    return str(v)


def main():
    args = sys.argv[1:]
    prima = ""
    if "--prima" in args:
        i = args.index("--prima")
        prima = args[i + 1]
        del args[i:i + 2]
    if len(args) != 3:
        sys.exit(__doc__)
    spec, nome_db, query = args
    stato = leggi_specifica(pathlib.Path(spec).read_text(encoding="utf-8"))
    if nome_db not in stato["database"]:
        sys.exit(f"database '{nome_db}' non definito nella specifica")
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(stato["database"][nome_db])
    if prima:
        con.executescript(prima)
    try:
        cur = con.execute(query)
    except sqlite3.Error as e:
        print(f"ERRORE: {e}")
        return
    if cur.description is None:
        print(f"(nessuna riga restituita; righe coinvolte: {cur.rowcount}, ultimo id: {cur.lastrowid})")
        return
    colonne = [c[0] for c in cur.description]
    righe = cur.fetchall()
    print(" | ".join(colonne))
    for r in righe:
        print(" | ".join("NULL" if v is None else come_php(v) for v in r))
    print(f"({len(righe)} righe)")


if __name__ == "__main__":
    main()
