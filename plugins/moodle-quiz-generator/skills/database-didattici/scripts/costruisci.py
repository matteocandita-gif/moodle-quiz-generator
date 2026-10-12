#!/usr/bin/env python3
"""Costruisce un database didattico da un modello: script per phpMyAdmin (MySQL), script comune
(dashboard «Bozze dei quiz», CodeRunner SQLite), file .db, scheda con lo schema.

Uso:
    python3 costruisci.py MODELLO.py --taglia piccolo|medio|grande [--seme N] [--uscita CARTELLA]
    python3 costruisci.py MODELLO.py --tutte [--uscita CARTELLA]

Produce in USCITA/<nome>/<taglia>/:
    <nome>_<taglia>.sql         script comune: CREATE TABLE e INSERT che funzionano in MySQL e in SQLite
                                (va nel riquadro «Database del quiz» della dashboard)
    <nome>_<taglia>_mysql.sql   per phpMyAdmin/XAMPP: crea il database <nome>, cancella le tabelle se
                                esistono e le ricrea (si può reimportare)
    <nome>_<taglia>.db          SQLite pronto, con le chiavi esterne controllate
    scheda.md                   schema (notazione con chiave sottolineata e asterisco), righe, trappole,
                                controlli, prime righe di ogni tabella
    info.json                   riepilogo per il catalogo

Il modello è un file Python con:
    NOME = "biblioteca"                 nome del database (minuscolo, senza spazi)
    TITOLO, CONTESTO = "...", "..."     titolo e descrizione per la scheda e il catalogo
    TABELLE = [                         in ordine di creazione: prima le tabelle padre
      {"nome": "Autori",
       "colonne": [("IdAutore", "INT", "PRIMARY KEY"), ("Nome", "VARCHAR(40)", "NOT NULL"), ...],
       "chiave": ["IdA", "IdB"],        facoltativa: chiave primaria composta
       "esterne": [("IdAutore", "Autori", "IdAutore")],        (colonna, tabella, colonna)
       "unici": [["Email"]]},           facoltativo: vincoli UNIQUE
      ...]
    TAGLIE = {"piccolo": {...}, "medio": {...}, "grande": {...}}   parametri liberi letti da genera()
    def genera(g, t): ...               g = Generatore, t = TAGLIE[taglia]; restituisce
                                        {tabella: [righe]}, ogni riga una tupla nell'ordine delle colonne
    CONTROLLI = [("descrizione", "SELECT ... righe che violano la regola")]   devono dare 0 righe
    TRAPPOLE = ["righe pensate per smascherare errori: ..."]                  vanno nella scheda

Si ferma se: una chiave esterna non trova il padre, una chiave primaria o UNIQUE è ripetuta, un NOT NULL è
vuoto, una stringa supera la lunghezza di VARCHAR/CHAR, un numero non sta in DECIMAL o INT (MySQL in modo
stretto rifiuterebbe l'import), un controllo di coerenza trova righe, un nome di tabella o colonna è una
parola riservata di MySQL.
"""
import datetime
import decimal
import importlib.util
import json
import os
import random
import re
import sqlite3
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import dati_it as D  # noqa: E402

RISERVATE = set("""ADD ALL ALTER AND AS ASC BETWEEN BY CASE CHECK COLUMN CONDITION CONSTRAINT CREATE CROSS
CURRENT_DATE CURRENT_TIME DATABASE DEFAULT DELETE DESC DESCRIBE DISTINCT DIV DROP ELSE EXISTS FALSE FETCH
FOR FOREIGN FROM FULLTEXT GROUP GROUPS HAVING IF IN INDEX INNER INSERT INTERVAL INTO IS JOIN KEY KEYS LEFT
LIKE LIMIT LINES LOAD LOCK MATCH MOD NATURAL NOT NULL ON OPTION OR ORDER OUTER PRIMARY RANGE RANK READ
REFERENCES REPLACE RIGHT ROW ROWS SELECT SET SHOW TABLE THEN TO TRUE UNION UNIQUE UPDATE USAGE USE USING
VALUES WHEN WHERE WITH WRITE YEAR_MONTH""".split())


class Generatore:
    """Dati casuali ma riproducibili (stesso seme, stessi dati)."""

    def __init__(self, seme):
        self.r = random.Random(seme)
        self._usati = {}

    # scelte generiche
    def scegli(self, lista): return self.r.choice(lista)
    def campione(self, lista, k): return self.r.sample(list(lista), k)
    def intero(self, a, b): return self.r.randint(a, b)
    def prob(self, p): return self.r.random() < p
    def mescola(self, lista): lista = list(lista); self.r.shuffle(lista); return lista

    def unico(self, chiave, fn, tentativi=500):
        """Valore di fn() non ancora usato per «chiave» (email, codici, targhe…)."""
        s = self._usati.setdefault(chiave, set())
        for _ in range(tentativi):
            v = fn()
            if v not in s:
                s.add(v)
                return v
        raise SystemExit("ERRORE: non trovo valori unici per «%s»: allarga la lista" % chiave)

    # persone e luoghi
    def nome(self, sesso=None):
        sesso = sesso or self.scegli("MF")
        return self.scegli(D.NOMI_M if sesso == "M" else D.NOMI_F)
    def cognome(self): return self.scegli(D.COGNOMI)
    def persona_estera(self, nazionalita):
        """Nome e cognome coerenti con la nazionalità (vedi dati_it.NOMI_ESTERI); «Italiana» usa i nomi italiani."""
        if nazionalita not in D.NOMI_ESTERI:
            return self.persona()
        nomi, cognomi = D.NOMI_ESTERI[nazionalita]
        return {"sesso": "", "nome": self.scegli(nomi), "cognome": self.scegli(cognomi)}
    def persona(self):
        s = self.scegli("MF")
        return {"sesso": s, "nome": self.nome(s), "cognome": self.cognome()}
    def comune(self, solo_provincia=None, peso_bologna=0.0):
        """(comune, provincia, regione, cap); peso_bologna = probabilità di un comune della provincia di BO."""
        lista = [c for c in D.COMUNI if not solo_provincia or c[1] == solo_provincia]
        if peso_bologna and self.prob(peso_bologna):
            lista = [c for c in D.COMUNI if c[1] == "BO"]
        return self.scegli(lista)
    def via(self): return "%s %d" % (self.scegli(D.VIE), self.intero(1, 180))
    def telefono(self, cellulare=True):
        return ("3%d%d %07d" % (self.intero(2, 9), self.intero(0, 9), self.intero(0, 9999999)) if cellulare
                else "051 %06d" % self.intero(100000, 999999))
    def email(self, nome, cognome, dominio=None):
        """Email unica nome.cognome[numero]@dominio, senza spazi né apostrofi."""
        base = re.sub(r"[^a-z.]", "", ("%s.%s" % (nome, cognome)).lower())
        return self.unico("email", lambda: "%s%s@%s" % (base, "" if self.prob(0.6) else self.intero(1, 99),
                                                       dominio or self.scegli(D.DOMINI_EMAIL)))

    # date e numeri
    def data(self, s): return datetime.date.fromisoformat(s) if isinstance(s, str) else s
    def data_tra(self, a, b):
        a, b = self.data(a), self.data(b)
        return a + datetime.timedelta(days=self.intero(0, (b - a).days))
    def dopo(self, d, min_giorni, max_giorni): return self.data(d) + datetime.timedelta(days=self.intero(min_giorni, max_giorni))
    def nascita(self, eta_min, eta_max, oggi="2026-09-15"):
        o = self.data(oggi)
        return self.data_tra(o.replace(year=o.year - eta_max - 1) + datetime.timedelta(days=1),
                             o.replace(year=o.year - eta_min))
    def importo(self, a, b, passo=0.5):
        n = int(round((b - a) / passo))
        return decimal.Decimal(str(round(a + passo * self.intero(0, n), 2)))


# ---------------------------------------------------------------- SQL

def valore_sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int,)):
        return str(v)
    if isinstance(v, decimal.Decimal):
        return format(v, "f")
    if isinstance(v, float):
        return repr(round(v, 4))
    if isinstance(v, datetime.datetime):
        return "'%s'" % v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, datetime.date):
        return "'%s'" % v.isoformat()
    return "'%s'" % str(v).replace("'", "''")


def ddl(t):
    righe = ["    %s %s%s" % (c[0], c[1], (" " + c[2]) if len(c) > 2 and c[2] else "") for c in t["colonne"]]
    if t.get("chiave"):
        righe.append("    PRIMARY KEY (%s)" % ", ".join(t["chiave"]))
    for u in t.get("unici", []):
        righe.append("    UNIQUE (%s)" % ", ".join(u))
    for col, padre, pcol in t.get("esterne", []):
        righe.append("    FOREIGN KEY (%s) REFERENCES %s(%s)" % (col, padre, pcol))
    return "CREATE TABLE %s (\n%s\n);" % (t["nome"], ",\n".join(righe))


def insert(t, righe, blocco=50):
    out = []
    cols = ", ".join(c[0] for c in t["colonne"])
    for i in range(0, len(righe), blocco):
        vals = ",\n".join("(%s)" % ", ".join(valore_sql(v) for v in r) for r in righe[i:i + blocco])
        out.append("INSERT INTO %s (%s) VALUES\n%s;" % (t["nome"], cols, vals))
    return "\n".join(out)


def pk_di(t):
    if t.get("chiave"):
        return list(t["chiave"])
    return [c[0] for c in t["colonne"] if len(c) > 2 and "PRIMARY KEY" in (c[2] or "").upper()]


# ---------------------------------------------------------------- controlli

def controlla_struttura(M):
    err = []
    nomi = set()
    for t in M.TABELLE:
        if t["nome"].upper() in RISERVATE:
            err.append("tabella %s: è una parola riservata di MySQL" % t["nome"])
        nomi.add(t["nome"])
        for c in t["colonne"]:
            if c[0].upper() in RISERVATE:
                err.append("%s.%s: è una parola riservata di MySQL" % (t["nome"], c[0]))
            tipo = c[1].upper()
            if re.search(r"\bENUM\b|AUTO_INCREMENT\s*$", tipo) or re.search(r"PRIMARY\s+KEY\s+AUTO_INCREMENT",
                                                                          (tipo + " " + (c[2] if len(c) > 2 else "")).upper()):
                err.append("%s.%s: ENUM o PRIMARY KEY AUTO_INCREMENT non funzionano in SQLite" % (t["nome"], c[0]))
        if not pk_di(t):
            err.append("tabella %s senza chiave primaria" % t["nome"])
        for col, padre, pcol in t.get("esterne", []):
            if padre not in nomi:
                err.append("%s.%s: la tabella %s deve essere creata prima" % (t["nome"], col, padre))
    return err


def controlla_dati(M, dati):
    err = []
    for t in M.TABELLE:
        righe = dati.get(t["nome"])
        if righe is None:
            err.append("genera() non restituisce righe per %s" % t["nome"])
            continue
        ncol = len(t["colonne"])
        for k, r in enumerate(righe):
            if len(r) != ncol:
                err.append("%s, riga %d: %d valori per %d colonne" % (t["nome"], k + 1, len(r), ncol))
                break
            for v, c in zip(r, t["colonne"]):
                tipo, vinc = c[1].upper(), (c[2] if len(c) > 2 else "").upper()
                if v is None:
                    if "NOT NULL" in vinc or "PRIMARY KEY" in vinc:
                        err.append("%s.%s: NULL in una colonna obbligatoria (riga %d)" % (t["nome"], c[0], k + 1))
                    continue
                m = re.match(r"(VAR)?CHAR\((\d+)\)", tipo)
                if m and len(str(v)) > int(m.group(2)):
                    err.append("%s.%s: «%s» supera %s caratteri (MySQL rifiuta)" % (t["nome"], c[0], v, m.group(2)))
                m = re.match(r"DECIMAL\((\d+),\s*(\d+)\)", tipo)
                if m:
                    p, s = int(m.group(1)), int(m.group(2))
                    d = decimal.Decimal(str(v))
                    if abs(d) >= decimal.Decimal(10) ** (p - s) or d != round(d, s):
                        err.append("%s.%s: %s non sta in %s" % (t["nome"], c[0], v, tipo))
                if re.match(r"(TINY|SMALL)?INT", tipo) and not isinstance(v, (int, bool)):
                    err.append("%s.%s: «%s» non è un intero" % (t["nome"], c[0], v))
                if tipo.startswith("TINYINT") and isinstance(v, int) and not -128 <= v <= 127:
                    err.append("%s.%s: %s fuori dall'intervallo di TINYINT" % (t["nome"], c[0], v))
                if tipo == "DATE" and not isinstance(v, datetime.date):
                    err.append("%s.%s: «%s» non è una data" % (t["nome"], c[0], v))
        if len(err) > 30:
            break
    return err


def carica_modello(percorso):
    spec = importlib.util.spec_from_file_location("modello", percorso)
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    return M


# ---------------------------------------------------------------- scheda

def schema_riga(t, html=False):
    pk, fk = set(pk_di(t)), {c for c, _, _ in t.get("esterne", [])}
    parti = []
    for c in t["colonne"]:
        n = c[0] + ("*" if c[0] in fk else "")
        parti.append(("<u>%s</u>" if html else "__%s__") % n if c[0] in pk else n)
    return ("<strong>%s</strong> (%s)" if html else "**%s** (%s)") % (t["nome"], ", ".join(parti))


def tabella_md(cur, t, n=5):
    cols = [c[0] for c in t["colonne"]]
    righe = cur.execute("SELECT * FROM %s LIMIT %d" % (t["nome"], n)).fetchall()
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in righe:
        out.append("| " + " | ".join("" if v is None else str(v) for v in r) + " |")
    return "\n".join(out)


def costruisci(M, taglia, seme, uscita):
    g = Generatore(seme)
    dati = M.genera(g, M.TAGLIE[taglia])
    err = controlla_dati(M, dati)
    if err:
        raise SystemExit("ERRORI nei dati (%s):\n- " % taglia + "\n- ".join(err[:30]))

    comune = ["-- Database «%s» (%s), taglia %s, seme %d: generato con database-didattici" % (M.NOME, M.TITOLO, taglia, seme)]
    comune += [ddl(t) for t in M.TABELLE]
    comune += [insert(t, dati[t["nome"]]) for t in M.TABELLE if dati[t["nome"]]]
    comune_sql = "\n\n".join(comune) + "\n"

    mysql = ["-- Da importare in phpMyAdmin (scheda Importa) o con: mysql -u root < questo_file.sql",
             "-- Crea il database «%s» e ricrea le tabelle: si può reimportare per ripartire dai dati originali." % M.NOME,
             "CREATE DATABASE IF NOT EXISTS %s CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" % M.NOME,
             "USE %s;" % M.NOME, "SET NAMES utf8mb4;", "SET FOREIGN_KEY_CHECKS = 0;"]
    mysql += ["DROP TABLE IF EXISTS %s;" % t["nome"] for t in reversed(M.TABELLE)]
    mysql += ["SET FOREIGN_KEY_CHECKS = 1;", ""]
    mysql_sql = "\n".join(mysql) + "\n" + comune_sql

    cart = os.path.join(uscita, M.NOME, taglia)
    os.makedirs(cart, exist_ok=True)
    base = os.path.join(cart, "%s_%s" % (M.NOME, taglia))
    pdb = base + ".db"
    if os.path.exists(pdb):
        os.remove(pdb)
    con = sqlite3.connect(pdb)
    con.execute("PRAGMA foreign_keys = ON")
    try:
        con.executescript(comune_sql)
    except sqlite3.Error as e:
        raise SystemExit("ERRORE: lo script non funziona in SQLite: %s" % e)
    cur = con.cursor()
    fkc = cur.execute("PRAGMA foreign_key_check").fetchall()
    if fkc:
        raise SystemExit("ERRORE: chiavi esterne senza padre: %s" % fkc[:10])
    viol = []
    for desc, q in getattr(M, "CONTROLLI", []):
        r = cur.execute(q).fetchall()
        if r:
            viol.append("%s: %d righe (prima: %s)" % (desc, len(r), r[0]))
    if viol:
        raise SystemExit("ERRORE: controlli di coerenza non rispettati (%s):\n- " % taglia + "\n- ".join(viol))
    conteggi = {t["nome"]: cur.execute("SELECT COUNT(*) FROM %s" % t["nome"]).fetchone()[0] for t in M.TABELLE}
    con.commit()

    open(base + ".sql", "w", encoding="utf-8").write(comune_sql)
    open(base + "_mysql.sql", "w", encoding="utf-8").write(mysql_sql)

    s = ["# %s — taglia %s" % (M.TITOLO, taglia), "", M.CONTESTO, "",
         "Nome del database: `%s` · seme %d · %s" % (M.NOME, seme, ", ".join("%s %d righe" % kv for kv in conteggi.items())), "",
         "## Schema (per le tracce della dashboard)", ""]
    s += [schema_riga(t) for t in M.TABELLE]
    s += ["", "## Schema (HTML per Moodle)", "", "```html"] + ["<p>%s</p>" % schema_riga(t, True) for t in M.TABELLE] + ["```"]
    if getattr(M, "TRAPPOLE", None):
        s += ["", "## Righe pensate per smascherare gli errori", ""] + ["- " + x for x in M.TRAPPOLE]
    if getattr(M, "CONTROLLI", None):
        s += ["", "## Controlli di coerenza (tutti rispettati)", ""] + ["- " + d for d, _ in M.CONTROLLI]
    s += ["", "## Prime righe", ""]
    for t in M.TABELLE:
        s += ["### %s (%d righe)" % (t["nome"], conteggi[t["nome"]]), "", tabella_md(cur, t), ""]
    open(os.path.join(cart, "scheda.md"), "w", encoding="utf-8").write("\n".join(s))
    info = {"nome": M.NOME, "titolo": M.TITOLO, "contesto": M.CONTESTO, "taglia": taglia, "seme": seme,
            "righe": conteggi, "schema": [schema_riga(t) for t in M.TABELLE],
            "schema_html": [schema_riga(t, True) for t in M.TABELLE], "trappole": getattr(M, "TRAPPOLE", []),
            "file": [os.path.basename(base) + x for x in (".sql", "_mysql.sql", ".db")] + ["scheda.md"],
            "tabelle": [{"nome": t["nome"], "colonne": [{"nome": c[0], "tipo": c[1], "vincoli": c[2] if len(c) > 2 else ""}
                                                       for c in t["colonne"]],
                         "chiave": pk_di(t), "esterne": [list(e) for e in t.get("esterne", [])],
                         "righe": conteggi[t["nome"]],
                         "esempi": [[None if v is None else str(v) for v in r]
                                    for r in cur.execute("SELECT * FROM %s LIMIT 5" % t["nome"]).fetchall()]}
                        for t in M.TABELLE],
            "controlli": [d for d, _ in getattr(M, "CONTROLLI", [])]}
    json.dump(info, open(os.path.join(cart, "info.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    con.close()
    print("OK %-8s %s -> %s" % (taglia, ", ".join("%s %d" % kv for kv in conteggi.items()), cart))
    return cart


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    opz = {}
    args = sys.argv[1:]
    for i, x in enumerate(args):
        if x.startswith("--") and "=" in x:
            k, v = x[2:].split("=", 1)
            opz[k] = v
        elif x.startswith("--") and i + 1 < len(args) and not args[i + 1].startswith("--"):
            opz[x[2:]] = args[i + 1]
            if args[i + 1] in a:
                a.remove(args[i + 1])
    if len(a) != 1:
        raise SystemExit(__doc__)
    M = carica_modello(a[0])
    err = controlla_struttura(M)
    if err:
        raise SystemExit("ERRORI nel modello:\n- " + "\n- ".join(err))
    uscita = opz.get("uscita", "database")
    seme = int(opz.get("seme", getattr(M, "SEME", 2026)))
    taglie = list(M.TAGLIE) if "--tutte" in sys.argv else [opz.get("taglia", "medio")]
    for t in taglie:
        if t not in M.TAGLIE:
            raise SystemExit("taglia «%s» non definita nel modello (%s)" % (t, ", ".join(M.TAGLIE)))
        costruisci(M, t, seme, uscita)


if __name__ == "__main__":
    main()
