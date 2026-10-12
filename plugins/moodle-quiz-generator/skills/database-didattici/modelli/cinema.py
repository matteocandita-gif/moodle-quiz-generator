"""Modello: cinema (4 tabelle). Registi 1-N Film, Clienti N-N Film tramite Biglietti.
Creato per la verifica V5R (quinta SIA): stessa forma di palestra e veterinario."""
import datetime
import decimal

NOME = "cinema"
TITOLO = "Cinema"
CONTESTO = ("Un cinema di Bologna con tre sale vende i biglietti ai clienti con la tessera del cinema. "
            "Ogni film ha un solo regista; il cliente fa la tessera (DataTessera) e poi compra i biglietti "
            "(tabella Biglietti). Il prezzo dipende dall'orario: 16:00 6.50 euro, 18:30 7.50 euro, 21:00 9.00 euro.")
SEME = 5102

TABELLE = [
    {"nome": "Registi", "colonne": [
        ("IdRegista", "INT", "PRIMARY KEY"),
        ("Nome", "VARCHAR(40)", "NOT NULL"),
        ("Cognome", "VARCHAR(40)", "NOT NULL"),
        ("Nazionalita", "VARCHAR(30)", "NOT NULL"),
        ("AnnoNascita", "INT", "NOT NULL")]},
    {"nome": "Film", "colonne": [
        ("IdFilm", "INT", "PRIMARY KEY"),
        ("Titolo", "VARCHAR(60)", "NOT NULL"),
        ("Genere", "VARCHAR(20)", "NOT NULL"),
        ("Durata", "INT", "NOT NULL"),
        ("AnnoUscita", "INT", "NOT NULL"),
        ("IdRegista", "INT", "NOT NULL")],
     "esterne": [("IdRegista", "Registi", "IdRegista")]},
    {"nome": "Clienti", "colonne": [
        ("IdCliente", "INT", "PRIMARY KEY"),
        ("Nome", "VARCHAR(40)", "NOT NULL"),
        ("Cognome", "VARCHAR(40)", "NOT NULL"),
        ("DataNascita", "DATE", "NOT NULL"),
        ("Citta", "VARCHAR(40)", "NOT NULL"),
        ("Email", "VARCHAR(80)", ""),
        ("DataTessera", "DATE", "NOT NULL")]},
    {"nome": "Biglietti", "colonne": [
        ("IdBiglietto", "INT", "PRIMARY KEY"),
        ("IdFilm", "INT", "NOT NULL"),
        ("IdCliente", "INT", "NOT NULL"),
        ("DataProiezione", "DATE", "NOT NULL"),
        ("Ora", "CHAR(5)", "NOT NULL"),
        ("Sala", "VARCHAR(10)", "NOT NULL"),
        ("Prezzo", "DECIMAL(4,2)", "NOT NULL")],
     "esterne": [("IdFilm", "Film", "IdFilm"), ("IdCliente", "Clienti", "IdCliente")]},
]

TAGLIE = {
    "piccolo": {"registi": 6, "film": 10, "clienti": 12, "biglietti": 20},
    "medio": {"registi": 9, "film": 18, "clienti": 30, "biglietti": 50},
    "grande": {"registi": 15, "film": 30, "clienti": 100, "biglietti": 220},
}

GENERI = ["Commedia", "Drammatico", "Animazione", "Thriller", "Fantascienza", "Avventura"]
NAZ = ["Italiana", "Italiana", "Italiana", "Francese", "Inglese", "Statunitense", "Spagnola", "Tedesca"]
TITOLI = ["Il ritorno", "La casa sul lago", "Ultima fermata", "Notte di luglio", "Le stelle di Marte",
          "Un'estate al mare", "Il segreto del faro", "Fuga da Neo Tokyo", "La festa di nozze", "Il volo del gabbiano",
          "Cuori in trasferta", "L'isola dei robot", "Ombre sul fiume", "Il caso Moretti", "Pane e cioccolato fondente",
          "La grande corsa", "Il pianeta verde", "Il viaggio di Leo", "Doppio gioco", "Sotto la pioggia",
          "Il mistero della villa", "Amici per sempre", "La lunga notte", "Il drago di carta", "Codice rosso",
          "Le ali della libertà", "Tre giorni a Parigi", "La valle silenziosa", "Missione Giove", "Il ladro di sogni"]
ORE = [("16:00", "6.50"), ("18:30", "7.50"), ("21:00", "9.00")]
SALE = ["Sala 1", "Sala 2", "Sala 3"]
FINE = datetime.date(2026, 9, 27)


def d(s):
    return datetime.date.fromisoformat(s)


def genera(g, t):
    nr, nf, nc, nb = t["registi"], t["film"], t["clienti"], t["biglietti"]
    # registi: il secondo e il penultimo sono omonimi; l'ultimo non ha film in programma
    registi = []
    for i in range(1, nr + 1):
        naz = g.scegli(NAZ)
        p = g.persona_estera(naz)
        registi.append([i, p["nome"], p["cognome"], naz, g.intero(1950, 1990)])
    registi[-2][1], registi[-2][2], registi[-2][3] = registi[1][1], registi[1][2], registi[1][3]
    registi[3][4] = 1958                                # firma il film del 1998
    registi = [tuple(x) for x in registi]
    # film: registi con 3, 2, 1 film; gli omonimi con un film ciascuno; due film «Il ritorno»
    assegnati = [1, 1, 1, 3, 3, 2, 4, 4, 5, nr - 1]
    film = []
    for k in range(nf):
        tit = TITOLI[k] if k < len(TITOLI) else "%s %d" % (TITOLI[k % len(TITOLI)], k)
        if k == 6:
            tit = "Il ritorno"
        reg = assegnati[k] if k < len(assegnati) else g.scegli([1, 5] + list(range(6, nr - 1)))
        anno = 2026 if g.prob(0.45) else 2025
        if k == 6:
            anno = 1998                                 # rassegna: il primo «Il ritorno» è del 1998
        film.append((k + 1, tit, GENERI[(k * 5 + 1) % len(GENERI)] if k not in (0, 6) else "Drammatico",
                     g.scegli([88, 95, 100, 104, 110, 118, 120, 126, 135]), anno, reg))
    # clienti: il primo e il terzultimo omonimi (città diverse)
    clienti = []
    for i in range(1, nc + 1):
        p = g.persona()
        comune = g.comune(solo_provincia="BO") if g.prob(0.85) else g.comune()
        citta = "Bologna" if g.prob(0.3) else comune[0]
        mail = g.email(p["nome"], p["cognome"]) if g.prob(0.8) else None
        clienti.append([i, p["nome"], p["cognome"], g.nascita(16, 75, oggi="2026-09-30"), citta, mail,
                        g.data_tra("2023-01-10", "2026-09-10")])
    clienti[-3][1], clienti[-3][2] = clienti[0][1], clienti[0][2]
    clienti[0][4], clienti[-3][4] = "Bologna", "San Lazzaro di Savena"
    clienti[1][6], clienti[1][4] = d("2025-01-01"), "Bologna"
    clienti[2][6], clienti[2][4] = d("2025-12-31"), "Bologna"
    clienti[3][6], clienti[3][4] = d("2024-12-31"), "Bologna"
    clienti[4][6], clienti[4][4] = d("2026-01-01"), "Bologna"
    clienti[-1][6], clienti[-1][4] = d("2025-06-14"), "Bologna"
    for c in clienti:                                   # la mail, se c'è, coerente con il nome
        if c[5]:
            c[5] = g.email(c[1], c[2])
    clienti = [tuple(c) for c in clienti]
    # biglietti
    senza = {clienti[-1][0], clienti[-2][0], clienti[4][0]}
    cli_ok = [c for c in clienti if c[0] not in senza]
    f_om1 = next(f[0] for f in film if f[5] == 2)
    f_om2 = next(f[0] for f in film if f[5] == nr - 1)
    vuoti = [f[0] for f in film if f[0] not in (f_om1, f_om2)][-2:]
    film_ok = [f[0] for f in film if f[0] not in vuoti + [f_om1, f_om2]]
    anno_film = {f[0]: f[4] for f in film}
    piani = [(clienti[0], 1), (clienti[0], 4), (clienti[0], f_om1), (clienti[1], 1), (clienti[1], 3),
             (clienti[1], f_om2), (clienti[2], 2), (clienti[2], f_om2), (clienti[2], 7),
             (clienti[3], 3), (clienti[-3], 4)]
    big = []
    for c, f in piani:
        big.append((c, f))
    while len(big) < nb:
        big.append((g.scegli(cli_ok), g.scegli(film_ok)))
    righe = []
    for c, f in big:
        inizio = max(c[6], d("%d-01-15" % max(anno_film[f], 2025)))
        if inizio > FINE:
            inizio = FINE
        data = g.data_tra(inizio, min(FINE, g.dopo(inizio, 0, 200)))
        ora, prezzo = g.scegli(ORE)
        righe.append((f, c[0], data, ora, g.scegli(SALE), decimal.Decimal(prezzo)))
    righe.sort(key=lambda r: (r[2], r[3], r[1]))
    biglietti = [(k + 1,) + r for k, r in enumerate(righe)]
    return {"Registi": registi, "Film": film, "Clienti": clienti, "Biglietti": biglietti}


CONTROLLI = [
    ("un biglietto non precede la tessera del cliente",
     "SELECT * FROM Biglietti b JOIN Clienti c ON b.IdCliente = c.IdCliente WHERE b.DataProiezione < c.DataTessera"),
    ("un film non si proietta prima dell'anno di uscita",
     "SELECT * FROM Biglietti b JOIN Film f ON b.IdFilm = f.IdFilm WHERE CAST(substr(b.DataProiezione, 1, 4) AS INT) < f.AnnoUscita"),
    ("il prezzo dipende dall'orario",
     "SELECT * FROM Biglietti WHERE NOT ((Ora = '16:00' AND Prezzo = 6.5) OR (Ora = '18:30' AND Prezzo = 7.5) "
     "OR (Ora = '21:00' AND Prezzo = 9))"),
    ("i registi hanno almeno 25 anni all'uscita del film",
     "SELECT * FROM Film f JOIN Registi r ON f.IdRegista = r.IdRegista WHERE f.AnnoUscita < r.AnnoNascita + 25"),
]

TRAPPOLE = [
    "tre clienti (il quinto e gli ultimi due) non hanno comprato biglietti, e alcuni clienti di Bologna ne hanno più d'uno: "
    "una JOIN inutile con Biglietti in una query sui clienti perde i primi e ripete i secondi",
    "Clienti.DataTessera e Biglietti.DataProiezione sono date diverse: filtrare l'una al posto dell'altra cambia il risultato",
    "clienti con la tessera fatta esattamente il 2025-01-01 e il 2025-12-31 (e il 2024-12-31, il 2026-01-01): smascherano i confini dell'anno",
    "due film non hanno venduto biglietti (LEFT JOIN), l'ultimo regista non ha film",
    "due film si intitolano «Il ritorno» (1998 e uno recente, registi diversi): raggruppare per titolo li fonde",
    "il secondo e il penultimo regista sono omonimi, con un film ciascuno: raggruppare per nome dà 2 film e supera HAVING >= 2; "
    "i loro film hanno 1 e 2 biglietti di clienti di Bologna, insieme 3",
    "il primo e il terzultimo cliente sono omonimi (Bologna e San Lazzaro di Savena)",
    "alcuni clienti hanno Email NULL; i prezzi sono 6.50, 7.50 e 9.00 secondo l'orario",
]
