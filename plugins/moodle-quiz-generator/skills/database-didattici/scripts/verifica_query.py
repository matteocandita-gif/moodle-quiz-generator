#!/usr/bin/env python3
"""Controlla che il database smascheri gli errori tipici: esegue la soluzione e le sue varianti sbagliate
(WHERE dimenticata, > al posto di >=, JOIN al posto di LEFT JOIN, condizione di JOIN mancante,
GROUP BY senza la chiave, = NULL, ORDER BY mancante…) e segnala quelle che danno lo stesso risultato.

Uso:
    python3 verifica_query.py DB.db --soluzione "SELECT ..." [--test "SELECT ..."] [--extra "..."] [--no-fk]
    python3 verifica_query.py DB.db --file soluzione.sql [--test ...]
    python3 verifica_query.py --specifica specifica-sql.txt [--solo NOME]

La seconda forma legge la specifica della skill domande-coderunner-sql (quella che scrive da_dashboard.py
in specifica-sql.txt): costruisce i database delle sezioni «=== database» (pieno, struttura o vuoto come
farebbe crea_xml.py) e controlla ogni domanda con i suoi test. I test con [[struttura T]] e le domande
in cui la soluzione deve dare un errore (vincoli) si controllano lo stesso: conta che l'output cambi.

Controlla anche i pari merito: se due righe del risultato sono alla pari nelle chiavi dell'ORDER BY (sui
dati del database e delle prove, con le righe di «extra»), l'ordine tra loro non è deciso dalla consegna e
una risposta giusta può darle nell'ordine opposto: CodeRunner confronta le righe nell'ordine. Si risolve
cambiando i dati, scegliendo una chiave unica o scrivendo nella traccia il secondo criterio.

Per ogni domanda stampa le varianti NON smascherate (stesso output della soluzione su tutti i test) con il
suggerimento sui dati da aggiungere. Una variante equivalente per costruzione (per esempio LEFT JOIN verso
una chiave esterna NOT NULL) non si può smascherare con i dati: si ignora.
Esce con codice 1 se almeno una variante importante non è smascherata (utile negli script).
"""
import os
import re
import shutil
import sqlite3
import sys
import tempfile

STRUTTURA_RE = re.compile(r"\[\[struttura\s+(\w+)\]\]")


def macro_struttura(m):
    t = m.group(1)
    return ("SELECT name, replace(upper(type), ' (', '(') AS tipo, \"notnull\", pk FROM pragma_table_info('%s');\n"
            "SELECT \"table\", \"from\", \"to\" FROM pragma_foreign_key_list('%s');" % (t, t))


# ---------------------------------------------------------------- esecuzione

def dividi(sql):
    """Istruzioni separate da ; fuori dalle stringhe e dai commenti."""
    out, cur, i, q = [], "", 0, None
    while i < len(sql):
        c = sql[i]
        if q:
            cur += c
            if c == q:
                if i + 1 < len(sql) and sql[i + 1] == q:
                    cur += sql[i + 1]; i += 1
                else:
                    q = None
        elif c in "'\"":
            q = c; cur += c
        elif sql.startswith("--", i):
            j = sql.find("\n", i)
            j = len(sql) if j < 0 else j
            i = j; cur += "\n"; continue
        elif c == ";":
            if cur.strip():
                out.append(cur.strip())
            cur = ""
        else:
            cur += c
        i += 1
    if cur.strip():
        out.append(cur.strip())
    return out


def esegui(db, codice, fk=True):
    """Esegue le istruzioni su una copia del database: [(colonne, righe)] dei risultati e gli errori."""
    tmp = tempfile.mktemp(suffix=".db")
    shutil.copy(db, tmp)
    con = sqlite3.connect(tmp)
    con.execute("PRAGMA foreign_keys = %s" % ("ON" if fk else "OFF"))
    ris, err = [], []
    for st in dividi(codice):
        try:
            cur = con.execute(st)
            if cur.description:
                righe = cur.fetchall()
                if righe:
                    ris.append((tuple(d[0].lower() for d in cur.description), tuple(righe)))
        except sqlite3.Error as e:
            err.append(str(e))
    con.commit()
    con.close()
    os.remove(tmp)
    return ris, err


def firma(db, risposta, tests, fk):
    return [esegui(db, "\n".join([t.get("extra", ""), risposta + ";", STRUTTURA_RE.sub(macro_struttura, t["codice"])]), fk)
            for t in tests]


# ---------------------------------------------------------------- varianti

def maschera(sql):
    """Sostituisce le stringhe con segnaposto, per mutare solo il codice."""
    lit = []
    def sost(m):
        lit.append(m.group(0))
        return "\x00%d\x00" % (len(lit) - 1)
    return re.sub(r"'(?:[^']|'')*'", sost, sql), lit


def smaschera(sql, lit):
    return re.sub(r"\x00(\d+)\x00", lambda m: lit[int(m.group(1))], sql)


def chiave(col):
    """La colonna sembra una chiave (Id…, …Id, Cod…, Matricola, ISBN, Targa, CF…)?"""
    c = col.split(".")[-1].strip().lower()
    return bool(re.match(r"(id|cod)\w*$|\w*id$|matricola$|isbn$|targa$|cf$|codice\w*$|piva$|numero\w*$", c))


FINE_CLAUSOLA = r"(?=\bGROUP\s+BY\b|\bORDER\s+BY\b|\bHAVING\b|\bLIMIT\b|\bUNION\b|\)|;|$)"


def varianti(sol):
    """[(categoria, descrizione, sql_variante, importante)]"""
    m, lit = maschera(sol)
    out = []

    def add(cat, desc, nuovo, imp=True):
        s = smaschera(nuovo, lit)
        if s.strip() != sol.strip() and all(s != v[2] for v in out):
            out.append((cat, desc, s, imp))

    def ogni(pattern, sost, cat, desc, flags=re.I, imp=True):
        for mm in re.finditer(pattern, m, flags):
            r = sost(mm) if callable(sost) else sost
            add(cat, desc + " («%s» → «%s»)" % (smaschera(mm.group(0), lit).strip(), smaschera(r, lit).strip()),
                m[:mm.start()] + r + m[mm.end():], imp)

    # WHERE dimenticata (SELECT, UPDATE, DELETE)
    for mm in re.finditer(r"\bWHERE\b.*?" + FINE_CLAUSOLA, m, re.I | re.S):
        add("where", "WHERE dimenticata", m[:mm.start()] + m[mm.end():])
    # confronti
    sw = {">=": ">", "<=": "<", ">": ">=", "<": "<=", "<>": "=", "!=": "="}
    ogni(r"(?<![<>!=])(>=|<=|<>|!=|>|<)(?![=>])", lambda mm: sw[mm.group(1)], "confronto", "confronto al confine")
    ogni(r"\bAND\b", " OR ", "logica", "AND al posto di OR")
    ogni(r"\bOR\b", " AND ", "logica", "OR al posto di AND")
    ogni(r"\bIS\s+NULL\b", "= NULL", "null", "«= NULL» al posto di IS NULL")
    ogni(r"\bIS\s+NOT\s+NULL\b", "IS NULL", "null", "IS NULL al posto di IS NOT NULL")
    ogni(r"\bNOT\s+IN\b", "IN", "logica", "IN al posto di NOT IN")
    # LIKE: % iniziale tolto o aggiunto
    for k, l in enumerate(lit):
        if re.search(r"\bLIKE\s*\x00%d\x00" % k, m, re.I):
            alt = []
            if l.startswith("'%"):
                alt.append("'" + l[2:])
            else:
                alt.append("'%" + l[1:])
            if l.endswith("%'") and not l.startswith("'%"):
                alt.append(l[:-2] + "'")
            for a in alt:
                lit2 = lit[:k] + [a] + lit[k + 1:]
                s = smaschera(m, lit2)
                if all(s != v[2] for v in out):
                    out.append(("like", "LIKE con il %% spostato (%s → %s)" % (l, a), s, True))
            # = al posto di LIKE
            s = smaschera(re.sub(r"\bLIKE(\s*\x00%d\x00)" % k, r"=\1", m, flags=re.I), lit)
            out.append(("like", "= al posto di LIKE %s" % l, s, True))
    # JOIN
    ogni(r"\bLEFT\s+(OUTER\s+)?JOIN\b", "JOIN", "join", "JOIN interna al posto di LEFT JOIN")
    ogni(r"(?<!LEFT )(?<!OUTER )\b(INNER\s+)?JOIN\b", "LEFT JOIN", "join", "LEFT JOIN al posto di JOIN", imp=False)
    for mm in re.finditer(r"\bON\b(.*?)(?=\bJOIN\b|\bLEFT\b|\bINNER\b|\bWHERE\b|\bGROUP\b|\bORDER\b|\bHAVING\b|\bLIMIT\b|;|$)", m, re.I | re.S):
        add("join", "condizione della JOIN sbagliata o dimenticata (prodotto cartesiano)",
            m[:mm.start()] + "ON 1 = 1 " + m[mm.end():])
    # aggregati
    ogni(r"\bCOUNT\s*\(\s*DISTINCT\s+", "COUNT(", "aggregato", "COUNT senza DISTINCT")
    ogni(r"\bCOUNT\s*\(\s*(?!\*|DISTINCT)[\w.]+\s*\)", "COUNT(*)", "aggregato", "COUNT(*) al posto di COUNT(colonna)")
    ogni(r"\bMIN\s*\(", "MAX(", "aggregato", "MAX al posto di MIN")
    ogni(r"\bMAX\s*\(", "MIN(", "aggregato", "MIN al posto di MAX")
    ogni(r"\bAVG\s*\(", "SUM(", "aggregato", "SUM al posto di AVG", imp=False)
    ogni(r"\bSELECT\s+DISTINCT\b", "SELECT", "distinct", "DISTINCT dimenticato")
    # GROUP BY senza una delle colonne
    for mm in re.finditer(r"\bGROUP\s+BY\b(.*?)(?=\bHAVING\b|\bORDER\b|\bLIMIT\b|;|\)|$)", m, re.I | re.S):
        cols = [c.strip() for c in mm.group(1).split(",")]
        if len(cols) > 1:
            for k in range(len(cols)):
                resto = cols[:k] + cols[k + 1:]
                # togliere una colonna non chiave quando la chiave resta è equivalente (dipendenza funzionale)
                imp = chiave(cols[k]) or not any(chiave(c) for c in resto)
                add("group", "GROUP BY senza «%s»" % cols[k],
                    m[:mm.start()] + "GROUP BY " + ", ".join(resto) + " " + m[mm.end():], imp)
    for mm in re.finditer(r"\bHAVING\b.*?(?=\bORDER\b|\bLIMIT\b|;|\)|$)", m, re.I | re.S):
        add("group", "HAVING dimenticato", m[:mm.start()] + m[mm.end():])
    # ORDER BY
    for mm in re.finditer(r"\bORDER\s+BY\b.*?(?=\bLIMIT\b|;|\)|$)", m, re.I | re.S):
        add("ordine", "ORDER BY dimenticato", m[:mm.start()] + m[mm.end():], imp=False)
        primo = re.match(r"(\s*ORDER\s+BY\s+[\w.()*]+)(\s+(ASC|DESC)\b)?", mm.group(0), re.I)
        if primo:
            verso = (primo.group(3) or "ASC").upper()
            nuovo = primo.group(1) + (" ASC" if verso == "DESC" else " DESC")
            add("ordine", "ordinamento al contrario", m[:mm.start()] + nuovo + mm.group(0)[primo.end():] + m[mm.end():])
    ogni(r"\bLIMIT\s+\d+(\s*,\s*\d+)?", "", "limit", "LIMIT dimenticato")
    return out


CONSIGLI = {
    "where": "aggiungi righe che la condizione deve escludere",
    "confronto": "aggiungi una riga con il valore esattamente sul confine della condizione",
    "logica": "aggiungi righe che soddisfano una sola delle due condizioni",
    "null": "aggiungi righe con il campo NULL (e altre con il campo valorizzato)",
    "like": "aggiungi un valore con il testo cercato all'inizio e uno con il testo in mezzo",
    "join": "aggiungi righe senza corrispondenza nell'altra tabella (un padre senza figli)",
    "aggregato": "aggiungi valori NULL o ripetuti nella colonna, o gruppi con valori diversi",
    "distinct": "aggiungi righe ripetute nel risultato",
    "group": "aggiungi omonimi (stesso nome, chiave diversa) o gruppi che la condizione HAVING deve escludere",
    "ordine": "ordina su valori diversi e mescola l'ordine di inserimento; due righe uguali nella chiave d'ordine le rende ambigue",
    "limit": "servono più righe di quelle del LIMIT",
}


# ---------------------------------------------------------------- pari merito nell'ORDER BY

def con_spareggio(sol, ncol, verso):
    """La soluzione con l'ORDER BY principale completato da tutte le colonne del risultato (1, 2, … in un verso)."""
    m, lit = maschera(sol)
    tutti = list(re.finditer(r"\bORDER\s+BY\b", m, re.I))
    if not tutti:
        return None
    ini = tutti[-1].start()
    coda = m[ini:]
    if coda.count(")") > coda.count("("):                # ORDER BY dentro una sottoquery: non lo tocco
        return None
    lim = re.search(r"\bLIMIT\b", coda, re.I)
    fine = ini + (lim.start() if lim else len(coda))
    agg = ", " + ", ".join("%d %s" % (k, verso) for k in range(1, ncol + 1))
    return smaschera(m[:fine].rstrip() + agg + " " + m[fine:], lit)


def righe_di(db, codice, fk):
    tmp = tempfile.mktemp(suffix=".db")
    shutil.copy(db, tmp)
    con = sqlite3.connect(tmp)
    con.execute("PRAGMA foreign_keys = %s" % ("ON" if fk else "OFF"))
    try:
        st = dividi(codice)
        for x in st[:-1]:
            con.execute(x)
        cur = con.execute(st[-1])
        return len(cur.description or []), cur.fetchall()
    except (sqlite3.Error, IndexError):
        return None, None
    finally:
        con.close()
        os.remove(tmp)


def pari_merito(db, sol, tests, fk=True):
    """Elenco di (prova, riga A, riga B) per le prove in cui l'ORDER BY lascia righe alla pari."""
    if not re.search(r"^\s*(SELECT|WITH)\b", sol, re.I) or not re.search(r"\bORDER\s+BY\b", sol, re.I):
        return []
    out = []
    for k, t in enumerate(tests or [{"extra": ""}]):
        extra = (t.get("extra") or "").strip()
        pre = (extra.rstrip(";") + ";\n") if extra else ""
        ncol, base = righe_di(db, pre + sol, fk)
        if not ncol or not base or len(base) < 2:
            continue
        a, b = (con_spareggio(sol, ncol, v) for v in ("ASC", "DESC"))
        if a is None:
            continue
        ra, rb = righe_di(db, pre + a, fk)[1], righe_di(db, pre + b, fk)[1]
        if ra is not None and rb is not None and ra != rb:
            i = next(j for j in range(len(ra)) if ra[j] != rb[j])
            out.append((k + 1, ra[i], rb[i]))
    return out


# ---------------------------------------------------------------- controllo

def controlla(db, sol, tests, fk=True, nome=""):
    base = firma(db, sol, tests, fk)
    if all(not r for r, e in base) and not any(e for r, e in base):
        print("ATTENZIONE %s: la soluzione e i test non producono nessuna riga: il confronto non distingue niente" % nome)
    vs = varianti(sol)
    scoperte, mancate = 0, []
    for cat, desc, s, imp in vs:
        if firma(db, s, tests, fk) != base:
            scoperte += 1
        else:
            mancate.append((cat, desc, s, imp))
    imp_m = [x for x in mancate if x[3]]
    pari = pari_merito(db, sol, tests, fk)
    stato = "OK" if not imp_m and not pari else "DA RIVEDERE"
    print("%s %s: %d varianti, %d smascherate%s" % (stato, nome or "soluzione", len(vs), scoperte,
          "" if not mancate else ", %d no" % len(mancate)))
    for cat, desc, s, imp in mancate:
        print("   %s %s\n      %s\n      -> %s" % ("NO " if imp else "(i)", desc, " ".join(s.split())[:200], CONSIGLI.get(cat, "")))
    for k, ra, rb in pari:
        print("   PARI MERITO nella prova %d: righe alla pari nelle chiavi dell'ORDER BY, per esempio %s e %s\n"
              "      -> cambia i dati (UPDATE in fondo allo script del quiz), usa una chiave unica o scrivi il "
              "secondo criterio nella traccia; se lo lasci apposta, correzione a mano" % (k, ra, rb))
    return not imp_m and not pari


# ---------------------------------------------------------------- specifica di domande-coderunner-sql

def leggi_specifica(testo):
    dbs, domande, cur, sez, buf = {}, [], None, None, []

    def chiudi():
        if sez is None:
            return
        c = "\n".join(buf).strip("\n")
        nome, _, arg = sez.partition(" ")
        if nome == "database":
            dbs[arg.strip()] = c
        elif cur is None:
            return
        elif nome in ("name", "answer", "preload"):
            cur[nome] = c
        elif nome == "options":
            for r in c.splitlines():
                k, _, v = r.partition(":")
                if k.strip():
                    cur["opz"][k.strip()] = v.strip()
        elif nome == "test":
            cur["test"].append({"codice": c, "extra": ""})
        elif nome == "extra" and cur["test"]:
            cur["test"][-1]["extra"] = c
    for r in testo.replace("\r\n", "\n").split("\n"):
        if r.startswith("=== "):
            chiudi()
            sez, buf = r[4:].strip(), []
            if sez == "question":
                cur = {"opz": {}, "test": []}
                domande.append(cur)
                sez = None
        else:
            buf.append(r)
    chiudi()
    return dbs, domande


def deduci_dati(risposta):
    a = risposta.upper()
    if re.search(r"\bCREATE\s+TABLE\b", a):
        return "vuoto"
    if re.search(r"\bINSERT\b", a) and not re.search(r"\b(SELECT|UPDATE|DELETE)\b", a):
        return "struttura"
    return "pieno"


def costruisci_db(script, dati, dest):
    con = sqlite3.connect(dest)
    if dati != "vuoto":
        con.executescript(script)
        if dati == "struttura":
            con.execute("PRAGMA foreign_keys = OFF")
            for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
                con.execute("DELETE FROM %s" % t)
    con.commit()
    con.close()


def da_specifica(percorso, solo=None):
    dbs, domande = leggi_specifica(open(percorso, encoding="utf-8").read())
    cart = tempfile.mkdtemp()
    tutto_ok = True
    for d in domande:
        nome = d.get("name", "?")
        if solo and solo.lower() not in nome.lower():
            continue
        if "answer" not in d or not d["test"]:
            continue
        base = d["opz"].get("database") or (next(iter(dbs)) if len(dbs) == 1 else None)
        if base not in dbs:
            print("SALTATA %s: database non trovato" % nome)
            continue
        dati = d["opz"].get("dati") or deduci_dati(d["answer"])
        p = os.path.join(cart, "%s_%s.db" % (base, dati))
        if not os.path.exists(p):
            costruisci_db(dbs[base], dati, p)
        tutto_ok &= controlla(p, d["answer"].strip().rstrip(";"), d["test"], d["opz"].get("foreign_keys", "1") == "1", nome)
    return tutto_ok


def main():
    args = sys.argv[1:]
    opz, pos, i = {}, [], 0
    while i < len(args):
        if args[i] in ("--soluzione", "--file", "--test", "--extra", "--specifica", "--solo"):
            opz.setdefault(args[i][2:], []).append(args[i + 1]); i += 2
        elif args[i].startswith("--"):
            opz[args[i][2:]] = True; i += 1
        else:
            pos.append(args[i]); i += 1
    if "specifica" in opz:
        ok = da_specifica(opz["specifica"][0], (opz.get("solo") or [None])[0])
        sys.exit(0 if ok else 1)
    if len(pos) != 1 or not ("soluzione" in opz or "file" in opz):
        raise SystemExit(__doc__)
    sol = opz["soluzione"][0] if "soluzione" in opz else open(opz["file"][0], encoding="utf-8").read()
    tests = [{"codice": t, "extra": (opz.get("extra") or [""])[0]} for t in (opz.get("test") or ["-- risultato"])]
    ok = controlla(pos[0], sol.strip().rstrip(";"), tests, "no-fk" not in opz)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
