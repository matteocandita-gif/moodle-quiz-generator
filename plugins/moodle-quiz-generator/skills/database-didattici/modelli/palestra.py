"""Modello: palestra (4 tabelle). Istruttori 1-N Corsi, Soci N-N Corsi tramite Iscrizioni.
Creato per la verifica V5R (quinta SIA): stessa forma di cinema e veterinario."""
import datetime
import decimal

NOME = "palestra"
TITOLO = "Palestra"
CONTESTO = ("Una palestra della provincia di Bologna organizza corsi tenuti dai suoi istruttori. "
            "Ogni corso ha un solo istruttore; un socio si iscrive alla palestra (DataIscrizione) e poi "
            "a uno o più corsi (tabella Iscrizioni). Un'iscrizione a un corso è attiva finché DataFine è vuota.")
SEME = 5101

TABELLE = [
    {"nome": "Istruttori", "colonne": [
        ("IdIstruttore", "INT", "PRIMARY KEY"),
        ("Nome", "VARCHAR(40)", "NOT NULL"),
        ("Cognome", "VARCHAR(40)", "NOT NULL"),
        ("Qualifica", "VARCHAR(40)", "NOT NULL"),
        ("DataAssunzione", "DATE", "NOT NULL")]},
    {"nome": "Corsi", "colonne": [
        ("IdCorso", "INT", "PRIMARY KEY"),
        ("Nome", "VARCHAR(40)", "NOT NULL"),
        ("Livello", "VARCHAR(15)", "NOT NULL"),
        ("Giorno", "VARCHAR(10)", "NOT NULL"),
        ("Orario", "CHAR(5)", "NOT NULL"),
        ("CostoMensile", "DECIMAL(5,2)", "NOT NULL"),
        ("PostiMax", "INT", "NOT NULL"),
        ("IdIstruttore", "INT", "NOT NULL")],
     "esterne": [("IdIstruttore", "Istruttori", "IdIstruttore")]},
    {"nome": "Soci", "colonne": [
        ("IdSocio", "INT", "PRIMARY KEY"),
        ("Nome", "VARCHAR(40)", "NOT NULL"),
        ("Cognome", "VARCHAR(40)", "NOT NULL"),
        ("DataNascita", "DATE", "NOT NULL"),
        ("Citta", "VARCHAR(40)", "NOT NULL"),
        ("Telefono", "VARCHAR(15)", ""),
        ("DataIscrizione", "DATE", "NOT NULL")]},
    {"nome": "Iscrizioni", "colonne": [
        ("IdIscrizione", "INT", "PRIMARY KEY"),
        ("IdSocio", "INT", "NOT NULL"),
        ("IdCorso", "INT", "NOT NULL"),
        ("DataInizio", "DATE", "NOT NULL"),
        ("DataFine", "DATE", "")],
     "esterne": [("IdSocio", "Soci", "IdSocio"), ("IdCorso", "Corsi", "IdCorso")]},
]

TAGLIE = {
    "piccolo": {"istruttori": 6, "corsi": 10, "soci": 12, "iscrizioni": 20},
    "medio": {"istruttori": 9, "corsi": 18, "soci": 30, "iscrizioni": 50},
    "grande": {"istruttori": 15, "corsi": 30, "soci": 100, "iscrizioni": 220},
}

# (nome del corso, specialità dell'istruttore che lo tiene)
CORSI = [("Yoga", "Discipline olistiche"), ("Pilates", "Discipline olistiche"), ("Zumba", "Danza"),
         ("Spinning", "Fitness"), ("Functional training", "Fitness"), ("Pugilato", "Sport da combattimento"),
         ("Kickboxing", "Sport da combattimento"), ("Ginnastica posturale", "Discipline olistiche"),
         ("Total body", "Fitness"), ("Danza moderna", "Danza"), ("Stretching", "Discipline olistiche"),
         ("Circuit training", "Fitness"), ("Hip hop", "Danza"), ("Difesa personale", "Sport da combattimento")]
QUALIFICHE = ["Laurea in Scienze motorie", "Diploma ISEF", "Istruttore federale", "Laurea in Scienze motorie", "Personal trainer certificato"]
LIVELLI = ["Base", "Intermedio", "Avanzato"]
GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"]
ORARI = ["09:00", "10:30", "12:30", "17:30", "18:30", "19:30", "20:30"]
COSTI = [30, 35, 38.5, 40, 42.5, 45, 48, 50, 55, 60]
FINE = datetime.date(2026, 9, 30)


def d(s):
    return datetime.date.fromisoformat(s)


def genera(g, t):
    ni, nc, ns, nk = t["istruttori"], t["corsi"], t["soci"], t["iscrizioni"]
    # istruttori: il secondo e il penultimo sono omonimi; l'ultimo, appena assunto, non ha corsi
    istruttori = []
    for i in range(1, ni + 1):
        p = g.persona()
        spec = QUALIFICHE[(i - 1) % len(QUALIFICHE)]
        ass = g.data_tra("2012-09-01", "2022-12-20") if i < ni else d("2026-09-01")
        istruttori.append([i, p["nome"], p["cognome"], spec, ass])
    istruttori[-2][1], istruttori[-2][2] = istruttori[1][1], istruttori[1][2]
    istruttori = [tuple(x) for x in istruttori]
    # corsi: istruttori con 3, 2, 1 corsi; gli omonimi con un corso ciascuno; due corsi «Yoga» e due «Pilates»
    attivi = list(range(1, ni))                                   # l'ultimo istruttore senza corsi
    assegnati = [1, 1, 1, 3, 3, 2, 4, 4, 5, ni - 1] + [None] * max(0, nc - 10)
    assegnati = [a if a is not None and a < ni else None for a in assegnati]
    corsi = []
    nomi = [c[0] for c in CORSI]
    usati_nome_livello = set()
    for k in range(nc):
        if k == 0:
            nome, liv = "Yoga", "Base"
        elif k == 1:
            nome, liv = "Yoga", "Avanzato"
        elif k == 2:
            nome, liv = "Pilates", "Base"
        elif k == 5:
            nome, liv = "Pilates", "Intermedio"
        else:
            nome = nomi[(k + 3) % len(nomi)]
            liv = g.scegli(LIVELLI)
        prove = 0
        while (nome, liv) in usati_nome_livello:
            liv = LIVELLI[(LIVELLI.index(liv) + 1) % 3]
            prove += 1
            if prove % 3 == 0:
                nome = nomi[(nomi.index(nome) + 1) % len(nomi)]
        usati_nome_livello.add((nome, liv))
        ist = assegnati[k] if k < len(assegnati) and assegnati[k] else g.scegli([1, 5] + list(range(6, ni - 1)))
        costo = COSTI[(k * 7 + 3) % len(COSTI)]
        if k == 4:
            costo = 50                                       # confine tondo
        corsi.append((k + 1, nome, liv, g.scegli(GIORNI), g.scegli(ORARI),
                      decimal.Decimal("%.2f" % costo), g.scegli([10, 12, 15, 20, 25]), ist))
    # soci: il primo e il terzultimo sono omonimi (città diverse); circa metà di Bologna
    soci = []
    for i in range(1, ns + 1):
        p = g.persona()
        comune = g.comune(solo_provincia="BO") if g.prob(0.85) else g.comune()
        citta = "Bologna" if g.prob(0.3) else comune[0]
        tel = g.telefono() if g.prob(0.8) else None
        soci.append([i, p["nome"], p["cognome"], g.nascita(19, 68, oggi="2026-09-30"), citta, tel,
                     g.data_tra("2023-01-10", "2026-09-15")])
    soci[-3][1], soci[-3][2] = soci[0][1], soci[0][2]
    soci[0][4], soci[-3][4] = "Bologna", "Casalecchio di Reno"
    # confini dell'anno 2025 e soci di Bologna
    soci[1][6], soci[1][4] = d("2025-01-01"), "Bologna"
    soci[2][6], soci[2][4] = d("2025-12-31"), "Bologna"
    soci[3][6], soci[3][4] = d("2024-12-31"), "Bologna"
    soci[4][6], soci[4][4] = d("2026-01-01"), "Bologna"
    soci[-1][6], soci[-1][4] = d("2025-06-14"), "Bologna"      # di Bologna, del 2025, senza corsi
    soci = [tuple(s) for s in soci]
    # iscrizioni: il quinto socio e gli ultimi due non sono iscritti a nessun corso;
    # gli ultimi due corsi (non degli omonimi) non hanno iscritti
    senza = {soci[-1][0], soci[-2][0], soci[4][0]}
    socio_ok = [s for s in soci if s[0] not in senza]
    c_om1 = next(c[0] for c in corsi if c[7] == 2)                 # corso dell'istruttore 2 (omonimo)
    c_om2 = next(c[0] for c in corsi if c[7] == ni - 1)            # corso dell'istruttore ni-1 (omonimo)
    vuoti = [c[0] for c in corsi if c[0] not in (c_om1, c_om2)][-2:]
    corso_ok = [c[0] for c in corsi if c[0] not in vuoti + [c_om1, c_om2]]
    iscr, coppie = [], set()
    # (socio, corso, attiva): i soci 1, 2, 3 di Bologna hanno più iscrizioni; i corsi dei due istruttori omonimi
    # hanno 1 e 2 iscrizioni attive di soci di Bologna (insieme fanno 3)
    piani = [(soci[0], 1, True), (soci[0], 4, None), (soci[0], c_om1, True), (soci[1], 1, True), (soci[1], 3, None),
             (soci[1], c_om2, True), (soci[2], 2, None), (soci[2], c_om2, True), (soci[2], 7, None),
             (soci[3], 3, None), (soci[-3], 4, None)]
    for s, c, att in piani:
        if (s[0], c) in coppie:
            continue
        coppie.add((s[0], c))
        ini = g.dopo(s[6], 0, 60)
        iscr.append([s, c, min(ini, FINE), att])
    while len(iscr) < nk:
        s = g.scegli(socio_ok)
        c = g.scegli(corso_ok)
        if (s[0], c) in coppie:
            continue
        coppie.add((s[0], c))
        ini = g.dopo(s[6], 0, 300)
        iscr.append([s, c, min(ini, FINE), None])
    righe = []
    for s, c, ini, att in iscr:
        chiusa = (not att) and g.prob(0.35) and ini < d("2026-06-01")
        fine = min(g.dopo(ini, 30, 240), FINE) if chiusa else None
        righe.append((s[0], c, ini, fine))
    righe.sort(key=lambda r: (r[2], r[0]))
    iscrizioni = [(k + 1,) + r for k, r in enumerate(righe)]
    return {"Istruttori": istruttori, "Corsi": corsi, "Soci": soci, "Iscrizioni": iscrizioni}


CONTROLLI = [
    ("un'iscrizione a un corso non precede l'iscrizione alla palestra",
     "SELECT * FROM Iscrizioni i JOIN Soci s ON i.IdSocio = s.IdSocio WHERE i.DataInizio < s.DataIscrizione"),
    ("la fine di un'iscrizione non precede l'inizio",
     "SELECT * FROM Iscrizioni WHERE DataFine < DataInizio"),
    ("nessun socio iscritto due volte allo stesso corso",
     "SELECT IdSocio, IdCorso FROM Iscrizioni GROUP BY IdSocio, IdCorso HAVING COUNT(*) > 1"),
    ("le iscrizioni attive di un corso non superano i posti",
     "SELECT c.IdCorso FROM Corsi c JOIN Iscrizioni i ON c.IdCorso = i.IdCorso WHERE i.DataFine IS NULL "
     "GROUP BY c.IdCorso, c.PostiMax HAVING COUNT(*) > c.PostiMax"),
    ("i soci hanno almeno 16 anni all'iscrizione",
     "SELECT * FROM Soci WHERE DataIscrizione < date(DataNascita, '+16 years')"),
]

TRAPPOLE = [
    "tre soci (il quinto e gli ultimi due) non sono iscritti a nessun corso, e alcuni soci di Bologna hanno più iscrizioni: "
    "una JOIN inutile con Iscrizioni in una query sui soci perde i primi e ripete i secondi",
    "Soci.DataIscrizione (iscrizione alla palestra) e Iscrizioni.DataInizio (iscrizione al corso) sono date diverse: "
    "filtrare l'una al posto dell'altra cambia il risultato",
    "soci iscritti alla palestra esattamente il 2025-01-01 e il 2025-12-31 (e il 2024-12-31, il 2026-01-01): smascherano i confini dell'anno",
    "due corsi non hanno iscritti (LEFT JOIN), l'ultimo istruttore, appena assunto, non ha corsi",
    "due corsi «Yoga» (Base e Avanzato) e due «Pilates»: raggruppare per nome del corso li fonde",
    "il secondo e il penultimo istruttore sono omonimi, con un corso ciascuno: raggruppare per nome dà 2 corsi e supera HAVING >= 2; i loro corsi hanno 1 e 2 iscrizioni attive di soci di Bologna, insieme 3",
    "il primo e il terzultimo socio sono omonimi (Bologna e Casalecchio di Reno)",
    "le iscrizioni attive hanno DataFine NULL: «= NULL» non trova niente, COUNT(DataFine) le salta",
    "alcuni soci hanno Telefono NULL; un corso costa esattamente 50.00",
]
