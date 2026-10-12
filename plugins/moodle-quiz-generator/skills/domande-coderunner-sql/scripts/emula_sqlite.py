"""Emula il client a riga di comando sqlite3 (versione 3.46, modalità column con
intestazioni) come lo usa il prototipo sql_salvemini, per calcolare gli output
attesi senza passare da Jobe.

Riproduce: una tabella per ogni istruzione che restituisce colonne (intestazione,
riga di trattini, righe allineate a sinistra, colonne larghe quanto il valore più
lungo, due spazi tra le colonne); nessuna stampa per i risultati senza righe;
gli errori raccolti a parte e mostrati dal prototipo in fondo, come
"ERRORE: messaggio"; i comandi .mode, .headers, .width (ignorati) e .schema.

Uso come modulo:
    uscita, errori = esegui(percorso_db, codice, foreign_keys=True)
    testo = formatta_test(uscita, errori)        # ciò che il prototipo stampa
"""
import json
import re
import shutil
import sqlite3
import tempfile


def _testo(con, v):
    if v is None:
        return ""
    if isinstance(v, float):
        return con.execute("SELECT CAST(? AS TEXT)", (v,)).fetchone()[0]
    if isinstance(v, bytes):
        return v.decode("utf-8", "replace")
    return str(v)


def _tabella(intest, righe):
    larg = [max([len(h)] + [len(r[i]) for r in righe]) for i, h in enumerate(intest)]
    fmt = lambda celle: "  ".join(c.ljust(larg[i]) for i, c in enumerate(celle)).rstrip()
    out = [fmt(intest), "  ".join("-" * w for w in larg)]
    out += [fmt(r) for r in righe]
    return out


def _schema(con, arg):
    if arg:
        q = ("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND "
             "lower(tbl_name) = lower(?) ORDER BY rowid")
        rows = con.execute(q, (arg,)).fetchall()
    else:
        rows = con.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL "
                           "AND name NOT LIKE 'sqlite_%' ORDER BY rowid").fetchall()
    return [r[0] + ";" for r in rows]


def _solo_commenti(testo):
    """Come il client sqlite3: un buffer con soli spazi e commenti è vuoto."""
    testo = re.sub(r"/\*[\s\S]*?\*/", "", testo)
    testo = re.sub(r"--[^\n]*", "", testo)
    return not testo.strip()


def estrai_risposta(risposta):
    """Le domande con l'interfaccia scratchpad salvano la risposta in JSON."""
    r = (risposta or "").strip()
    if r.startswith("{"):
        try:
            dati = json.loads(r)
            if isinstance(dati, dict) and "answer_code" in dati:
                return "\n".join(dati["answer_code"])
        except ValueError:
            pass
    return risposta


def esegui_su_connessione(con, codice):
    """Esegue il codice (SQL e comandi punto) come farebbe sqlite3 leggendo da
    standard input, senza fermarsi agli errori. Restituisce (righe, errori)."""
    out, errori, buffer = [], [], ""
    for riga in codice.split("\n"):
        if _solo_commenti(buffer) and riga.lstrip().startswith("."):
            buffer = ""
            parti = riga.strip().split(None, 1)
            cmd = parti[0]
            if cmd == ".schema":
                out += _schema(con, parti[1].strip() if len(parti) > 1 else None)
            elif cmd in (".mode", ".headers", ".width"):
                pass
            else:
                raise ValueError("comando %s non emulato: verifica il test su Jobe" % cmd)
            continue
        buffer += riga + "\n"
        if sqlite3.complete_statement(buffer):
            istr, buffer = buffer.strip(), ""
            try:
                cur = con.execute(istr)
                if cur.description:
                    intest = [d[0] for d in cur.description]
                    righe = [[_testo(con, v) for v in r] for r in cur.fetchall()]
                    if righe:
                        out += _tabella(intest, righe)
                con.commit()
            except sqlite3.Error as e:
                errori.append(str(e))
    if buffer.strip():
        try:
            con.execute(buffer)
        except sqlite3.Error as e:
            errori.append(str(e))
    return out, errori


def esegui(percorso_db, codice, foreign_keys=True):
    with tempfile.TemporaryDirectory() as tmp:
        copia = tmp + "/lavoro.db"
        shutil.copyfile(percorso_db, copia)
        con = sqlite3.connect(copia, isolation_level=None)
        if foreign_keys:
            con.execute("PRAGMA foreign_keys = ON")
        try:
            return esegui_su_connessione(con, codice)
        finally:
            con.close()


def formatta_test(righe, errori, precheck=False):
    """Ciò che il prototipo stampa per un test."""
    err = ["ERRORE: " + e for e in errori]
    if precheck:
        return "\n".join(err)
    return "\n".join(righe + err)


def chiudi_risposta(risposta):
    risposta = estrai_risposta(risposta).rstrip()
    return risposta if risposta.endswith(";") else risposta + ";"
