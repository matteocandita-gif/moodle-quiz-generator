#!/usr/bin/env python3
"""Sostituto minimo del client sqlite3 per eseguire in locale il template php_mysqli_sqlite
quando il client vero non c'è (nell'ambiente di Claude manca).

Uso (come il client vero):  sqlite3_cli.py FILE.db  < script
Gestisce ciò che usa il template: .mode json, .print TESTO, istruzioni SQL separate da ;.
Scrive i risultati in JSON come il client (una matrice per istruzione che restituisce righe)
e gli errori su stderr come «Parse error near line N: messaggio» oppure, per i vincoli,
«Runtime error near line N: messaggio (19)». I messaggi vengono dalla libreria SQLite di Python,
di versione vicina a quella di Jobe (3.46): il controllo definitivo resta il bulk tester su Jobe.
"""
import json
import sqlite3
import sys


def valore(v):
    if isinstance(v, bytes):
        return v.decode("utf-8", "replace")
    return v


def main():
    if len(sys.argv) < 2:
        sys.exit("uso: sqlite3_cli.py FILE.db < script")
    con = sqlite3.connect(sys.argv[1], isolation_level=None)
    testo = sys.stdin.read()
    buf, inizio, riga_n = "", 1, 0
    out = sys.stdout

    def esegui(sql, riga):
        try:
            cur = con.execute(sql)
            righe = cur.fetchall()
            if cur.description and righe:
                nomi = [d[0] for d in cur.description]
                pezzi = [json.dumps({n: valore(v) for n, v in zip(nomi, r)}, ensure_ascii=False,
                                    separators=(",", ":")) for r in righe]
                out.write("[" + ",\n".join(pezzi) + "]\n")
        except sqlite3.IntegrityError as e:
            sys.stderr.write("Runtime error near line %d: %s (19)\n" % (riga, e))
        except sqlite3.Error as e:
            sys.stderr.write("Parse error near line %d: %s\n" % (riga, e))

    for linea in testo.split("\n"):
        riga_n += 1
        if not buf.strip() and linea.startswith("."):
            cmd = linea.strip()
            if cmd.startswith(".print"):
                out.write(cmd[len(".print"):].strip() + "\n")
            continue
        if not buf.strip():
            inizio = riga_n
        buf += linea + "\n"
        if sqlite3.complete_statement(buf):
            if buf.strip().strip(";").strip():
                esegui(buf, inizio)
            buf = ""
    if buf.strip():
        # istruzione non chiusa (apice aperto): il client la segnala come errore di sintassi
        esegui(buf, inizio)
    out.flush()


if __name__ == "__main__":
    main()
