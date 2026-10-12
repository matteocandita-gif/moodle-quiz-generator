"""Modello: biblioteca scolastica (4 tabelle). Prova della skill database-didattici."""
import datetime

NOME = "biblioteca"
TITOLO = "Biblioteca scolastica"
CONTESTO = ("La biblioteca dell'istituto presta libri agli studenti. Ogni libro ha un solo autore; "
            "un prestito è aperto finché la data di restituzione è vuota.")
SEME = 2026

TABELLE = [
    {"nome": "Autori", "colonne": [
        ("IdAutore", "INT", "PRIMARY KEY"),
        ("Nome", "VARCHAR(40)", "NOT NULL"),
        ("Cognome", "VARCHAR(40)", "NOT NULL"),
        ("Nazionalita", "VARCHAR(30)", "NOT NULL"),
        ("AnnoNascita", "INT", "")]},
    {"nome": "Libri", "colonne": [
        ("ISBN", "CHAR(13)", "PRIMARY KEY"),
        ("Titolo", "VARCHAR(100)", "NOT NULL"),
        ("Genere", "VARCHAR(20)", "NOT NULL"),
        ("AnnoPubblicazione", "INT", "NOT NULL"),
        ("Pagine", "INT", ""),
        ("Copie", "INT", "NOT NULL"),
        ("IdAutore", "INT", "NOT NULL")],
     "esterne": [("IdAutore", "Autori", "IdAutore")]},
    {"nome": "Studenti", "colonne": [
        ("Matricola", "INT", "PRIMARY KEY"),
        ("Nome", "VARCHAR(40)", "NOT NULL"),
        ("Cognome", "VARCHAR(40)", "NOT NULL"),
        ("Classe", "VARCHAR(3)", "NOT NULL"),
        ("Email", "VARCHAR(80)", "NOT NULL")],
     "unici": [["Email"]]},
    {"nome": "Prestiti", "colonne": [
        ("IdPrestito", "INT", "PRIMARY KEY"),
        ("ISBN", "CHAR(13)", "NOT NULL"),
        ("Matricola", "INT", "NOT NULL"),
        ("DataPrestito", "DATE", "NOT NULL"),
        ("DataRestituzione", "DATE", "")],
     "esterne": [("ISBN", "Libri", "ISBN"), ("Matricola", "Studenti", "Matricola")]},
]

TAGLIE = {
    "piccolo": {"autori": 6, "libri": 10, "studenti": 8, "prestiti": 16},
    "medio": {"autori": 15, "libri": 40, "studenti": 30, "prestiti": 50},
    "grande": {"autori": 40, "libri": 120, "studenti": 100, "prestiti": 300},
}

# sostantivo, articolo determinativo
SOSTANTIVI = [("mare", "il"), ("notte", "la"), ("città", "la"), ("giardino", "il"), ("viaggio", "il"),
              ("segreto", "il"), ("isola", "l'"), ("fiume", "il"), ("silenzio", "il"), ("ombra", "l'"),
              ("inverno", "l'"), ("estate", "l'"), ("strada", "la"), ("lettera", "la"), ("casa", "la"),
              ("memoria", "la"), ("vento", "il"), ("porto", "il"), ("torre", "la"), ("bosco", "il"),
              ("stazione", "la"), ("confine", "il"), ("specchio", "lo"), ("sogno", "il"), ("ritorno", "il")]
AGG_M = ["perduto", "nascosto", "lontano", "dimenticato", "d'inverno", "di vetro", "senza nome", "di mezzanotte"]
AGG_F = ["perduta", "nascosta", "lontana", "dimenticata", "d'inverno", "di vetro", "senza nome", "di mezzanotte"]
FEMM = {"la"} | {"isola", "ombra", "estate"}
PREP = {"il": "del", "la": "della", "l'": "dell'", "lo": "dello"}
NAZ = ["Italiana"] * 7 + ["Francese", "Inglese", "Statunitense", "Spagnola", "Tedesca", "Argentina"]
CLASSI = ["3A", "3B", "4A", "4B", "5A", "5B"]


def con_art(art, s):
    return art + s if art.endswith("'") else art + " " + s


def titolo(g):
    s, art = g.scegli(SOSTANTIVI)
    femm = art == "la" or s in FEMM
    forma = g.intero(1, 4)
    if forma == 1:
        t = "%s %s" % (con_art(art, s), g.scegli(AGG_F if femm else AGG_M))
    elif forma == 2:
        s2, art2 = g.scegli([x for x in SOSTANTIVI if x[0] != s])
        t = "%s e %s" % (con_art(art, s), con_art(art2, s2))
    elif forma == 3:
        t = "Racconti %s" % (PREP[art] + s if art == "l'" else PREP[art] + " " + s)
    else:
        t = con_art(art, s)
    return t[0].upper() + t[1:]


def genera(g, t):
    # autori: l'ultimo non ha libri (LEFT JOIN)
    autori = []
    for i in range(1, t["autori"] + 1):
        naz = g.scegli(NAZ)
        p = g.persona_estera(naz)
        autori.append((i, p["nome"], p["cognome"], naz, g.intero(1920, 1990) if g.prob(0.85) else None))
    # due autori omonimi (il secondo e il terzultimo): raggruppare per nome li fonde
    a2 = autori[1]
    autori[-3] = (autori[-3][0], a2[1], a2[2], a2[3], autori[-3][4])
    # libri: 978 + 10 cifre; almeno un libro esattamente del 2000 (confine) e uno con Pagine NULL
    libri = []
    nascita = {a[0]: a[4] for a in autori}
    for i in range(t["libri"]):
        tit = g.unico("titolo", lambda: titolo(g))
        aut = g.intero(1, t["autori"] - 1)
        minimo = max(1960, (nascita[aut] or 1940) + 20)
        if i == 1:                                   # confine: un libro esattamente del 2000
            aut = next(a for a in range(1, t["autori"]) if (nascita[a] or 0) <= 1980)
            anno = 2000
        elif i % 3 == 0:                             # un terzo dei libri prima del 2000
            anno = g.intero(minimo, max(minimo, 1999))
        else:
            anno = g.intero(max(minimo, 2001), 2025)
        isbn = "978%010d" % g.unico("isbn", lambda: g.intero(0, 10 ** 10 - 1))
        pag = None if i == 2 else g.intero(90, 620)
        genere = "Poesia" if i in (5, 6) else g.scegli(["Romanzo", "Giallo", "Fantasy", "Storico", "Saggio"])
        libri.append((isbn, tit, genere,
                      anno, pag, g.intero(1, 3), aut))
    # titoli con «amore» all'inizio e in mezzo (LIKE e maiuscole)
    l0 = list(libri[3]); l0[1] = "Amore di mezzanotte"; libri[3] = tuple(l0)
    l1 = list(libri[4]); l1[1] = "Un amore lontano"; libri[4] = tuple(l1)
    # studenti: due omonimi in classi diverse
    studenti = []
    for i in range(t["studenti"]):
        p = g.persona()
        studenti.append([1001 + i, p["nome"], p["cognome"], g.scegli(CLASSI), None])
    studenti[-1][1], studenti[-1][2] = studenti[0][1], studenti[0][2]
    studenti[-1][3] = [c for c in CLASSI if c != studenti[0][3]][0]
    for s in studenti:
        s[4] = g.email(s[1], s[2], "studenti.istituto.it")
    studenti = [tuple(s) for s in studenti]
    # prestiti: l'ultimo libro e l'ultimo studente senza prestiti; prestiti aperti ≤ copie
    prestiti, aperti = [], {}
    isbn_ok = [l[0] for l in libri[:-1]]
    copie = {l[0]: l[5] for l in libri}
    mat_ok = [s[0] for s in studenti[:-2]] + [studenti[-1][0]]
    for i in range(1, t["prestiti"] + 1):
        isbn, mat = g.scegli(isbn_ok), g.scegli(mat_ok)
        dp = g.data_tra("2025-09-15", "2026-05-31")
        if i == 1:
            dp = datetime.date(2026, 1, 31)        # confine: fine gennaio
        if i == 2:
            dp = datetime.date(2026, 1, 1)         # confine: inizio mese, prestito ancora aperto
        restituito = (g.prob(0.75) and i != 2) or aperti.get(isbn, 0) >= copie[isbn]
        dr = g.dopo(dp, 3, 40) if restituito else None
        if dr and dr > datetime.date(2026, 6, 10):
            dr = datetime.date(2026, 6, 10)
        if not restituito:
            aperti[isbn] = aperti.get(isbn, 0) + 1
        prestiti.append((i, isbn, mat, dp, dr))
    prestiti.sort(key=lambda p: p[3])
    prestiti = [(k + 1,) + p[1:] for k, p in enumerate(prestiti)]
    return {"Autori": autori, "Libri": libri, "Studenti": studenti, "Prestiti": prestiti}


CONTROLLI = [
    ("la restituzione non precede il prestito",
     "SELECT * FROM Prestiti WHERE DataRestituzione < DataPrestito"),
    ("i prestiti aperti di un libro non superano le copie",
     "SELECT p.ISBN FROM Prestiti p JOIN Libri l ON p.ISBN = l.ISBN WHERE p.DataRestituzione IS NULL "
     "GROUP BY p.ISBN, l.Copie HAVING COUNT(*) > l.Copie"),
    ("gli autori sono nati prima di pubblicare",
     "SELECT * FROM Libri l JOIN Autori a ON l.IdAutore = a.IdAutore WHERE a.AnnoNascita IS NOT NULL "
     "AND l.AnnoPubblicazione < a.AnnoNascita + 18"),
]

TRAPPOLE = [
    "l'ultimo autore non ha libri: una JOIN interna lo perde, una LEFT JOIN lo mostra con NULL",
    "l'ultimo libro non è mai stato prestato e il penultimo studente non ha prestiti",
    "il primo e l'ultimo studente hanno lo stesso nome e cognome in classi diverse, e così il secondo e il terzultimo autore: raggruppare per nome invece che per chiave li fonde",
    "i prestiti aperti hanno DataRestituzione NULL: «= NULL» non trova niente, COUNT(DataRestituzione) li salta",
    "un prestito cade esattamente il 2026-01-01 (ancora aperto) e uno il 2026-01-31, un libro è del 2000: smascherano > al posto di >= sui confini dei mesi e degli anni",
    "un libro ha Pagine NULL: SUM e AVG lo ignorano, COUNT(Pagine) lo salta",
    "il genere Poesia ha esattamente 2 libri: smaschera HAVING COUNT(*) > 2 al posto di >= 2",
    "«Amore di mezzanotte» e «Un amore lontano»: LIKE 'amore%' trova solo il primo, LIKE '%amore%' entrambi",
]
