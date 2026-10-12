"""Modello: ambulatorio veterinario (4 tabelle). Proprietari 1-N Animali, Animali N-N Veterinari tramite Visite.
Creato per la verifica V5R (quinta SIA): stessa forma di palestra e cinema."""
import datetime
import decimal

NOME = "veterinario"
TITOLO = "Ambulatorio veterinario"
CONTESTO = ("Un ambulatorio veterinario della provincia di Bologna, con pronto soccorso aperto tutti i giorni, "
            "cura gli animali dei suoi clienti. Ogni animale ha un solo proprietario; l'animale viene registrato "
            "come paziente (DataRegistrazione) e poi visitato dai veterinari dell'ambulatorio (tabella Visite).")
SEME = 5103

TABELLE = [
    {"nome": "Proprietari", "colonne": [
        ("IdProprietario", "INT", "PRIMARY KEY"),
        ("Nome", "VARCHAR(40)", "NOT NULL"),
        ("Cognome", "VARCHAR(40)", "NOT NULL"),
        ("Citta", "VARCHAR(40)", "NOT NULL"),
        ("Telefono", "VARCHAR(15)", "NOT NULL")]},
    {"nome": "Animali", "colonne": [
        ("IdAnimale", "INT", "PRIMARY KEY"),
        ("Nome", "VARCHAR(30)", "NOT NULL"),
        ("Specie", "VARCHAR(20)", "NOT NULL"),
        ("Razza", "VARCHAR(40)", ""),
        ("DataNascita", "DATE", "NOT NULL"),
        ("DataRegistrazione", "DATE", "NOT NULL"),
        ("IdProprietario", "INT", "NOT NULL")],
     "esterne": [("IdProprietario", "Proprietari", "IdProprietario")]},
    {"nome": "Veterinari", "colonne": [
        ("IdVeterinario", "INT", "PRIMARY KEY"),
        ("Nome", "VARCHAR(40)", "NOT NULL"),
        ("Cognome", "VARCHAR(40)", "NOT NULL"),
        ("Specializzazione", "VARCHAR(40)", "NOT NULL")]},
    {"nome": "Visite", "colonne": [
        ("IdVisita", "INT", "PRIMARY KEY"),
        ("IdAnimale", "INT", "NOT NULL"),
        ("IdVeterinario", "INT", "NOT NULL"),
        ("Data", "DATE", "NOT NULL"),
        ("Motivo", "VARCHAR(30)", "NOT NULL"),
        ("Costo", "DECIMAL(6,2)", "NOT NULL")],
     "esterne": [("IdAnimale", "Animali", "IdAnimale"), ("IdVeterinario", "Veterinari", "IdVeterinario")]},
]

TAGLIE = {
    "piccolo": {"proprietari": 6, "animali": 10, "veterinari": 5, "visite": 20},
    "medio": {"proprietari": 14, "animali": 25, "veterinari": 7, "visite": 50},
    "grande": {"proprietari": 50, "animali": 80, "veterinari": 10, "visite": 220},
}

RAZZE = {"Cane": ["Labrador", "Pastore tedesco", "Beagle", "Barboncino", "Jack Russell", "Border collie", None],
         "Gatto": ["Europeo", "Persiano", "Siamese", "Maine coon", None],
         "Coniglio": ["Ariete nano", None], "Pappagallo": ["Cocorita", "Calopsite"], "Tartaruga": [None]}
SPECIE = ["Cane", "Cane", "Cane", "Gatto", "Gatto", "Gatto", "Coniglio", "Pappagallo", "Tartaruga"]
NOMI_ANIMALI = ["Luna", "Tigre", "Milo", "Kira", "Briciola", "Pallino", "Nina", "Rocky", "Zeus", "Bianca", "Teo",
                "Lilly", "Oliver", "Cleo", "Birba", "Leo", "Maya", "Toby", "Pepe", "Neve", "Romeo", "Molly",
                "Ciuffo", "Arturo", "Mia", "Stella", "Ugo", "Polpetta", "Charlie", "Gina"]
SPECIALIZZAZIONI = ["Medicina generale", "Chirurgia", "Dermatologia", "Cardiologia", "Medicina generale",
                    "Odontoiatria", "Medicina generale", "Chirurgia", "Oculistica", "Medicina generale"]
# motivo, specializzazione adatta, costo
MOTIVI = {"Medicina generale": [("Vaccinazione", "45.00"), ("Controllo", "40.00"), ("Visita urgente", "80.00")],
          "Chirurgia": [("Intervento", "250.00"), ("Sterilizzazione", "180.00"), ("Controllo", "40.00")],
          "Dermatologia": [("Visita dermatologica", "70.00"), ("Controllo", "40.00")],
          "Cardiologia": [("Ecocardiogramma", "120.00"), ("Controllo", "40.00")],
          "Odontoiatria": [("Pulizia dei denti", "90.00"), ("Estrazione", "150.00")],
          "Oculistica": [("Visita oculistica", "75.00"), ("Controllo", "40.00")]}
FINE = datetime.date(2026, 9, 30)


def d(s):
    return datetime.date.fromisoformat(s)


def genera(g, t):
    npr, na, nv, nk = t["proprietari"], t["animali"], t["veterinari"], t["visite"]
    # proprietari: il secondo e il penultimo omonimi (città diverse)
    proprietari = []
    for i in range(1, npr + 1):
        p = g.persona()
        comune = g.comune(solo_provincia="BO") if g.prob(0.9) else g.comune()
        citta = "Bologna" if g.prob(0.35) else comune[0]
        proprietari.append([i, p["nome"], p["cognome"], citta, g.telefono()])
    proprietari[-2][1], proprietari[-2][2] = proprietari[1][1], proprietari[1][2]
    proprietari[1][3], proprietari[-2][3] = "Bologna", "Zola Predosa"
    proprietari = [tuple(x) for x in proprietari]
    # animali: proprietari con 3, 2, 1 animali; gli omonimi un animale ciascuno; l'ultimo proprietario
    # ha registrato oggi il cucciolo e non ha ancora altri animali; due animali si chiamano «Luna»
    assegnati = [1, 1, 1, 3, 3, 2, 4, 4, 5, npr - 1, npr]
    animali = []
    for k in range(na):
        prop = assegnati[k] if k < len(assegnati) else g.scegli([5] + list(range(6, npr - 1)))
        specie = g.scegli(SPECIE)
        nome = NOMI_ANIMALI[k % len(NOMI_ANIMALI)]
        if k == 7:
            nome = "Luna"
        nascita = g.data_tra("2010-03-01", "2025-12-31")
        reg = g.data_tra(max(nascita + datetime.timedelta(days=60), d("2019-01-10")), d("2026-09-20"))
        animali.append([k + 1, nome, specie, g.scegli(RAZZE[specie]), nascita, reg, prop])
    # confini dell'anno 2025 e gatti registrati nel 2025
    for k, data in ((1, "2025-01-01"), (2, "2025-12-31"), (3, "2024-12-31"), (4, "2026-01-01"), (na - 1, "2025-06-14")):
        animali[k][2] = "Gatto"
        animali[k][3] = g.scegli(RAZZE["Gatto"])
        animali[k][5] = d(data)
        if animali[k][4] > animali[k][5] - datetime.timedelta(days=60):
            animali[k][4] = animali[k][5] - datetime.timedelta(days=g.intero(90, 2000))
    animali[0][2], animali[0][3] = "Gatto", "Europeo"
    animali = [tuple(a) for a in animali]
    # veterinari: specializzazioni dalla lista; l'ultimo, appena arrivato, non ha ancora visitato
    veterinari = []
    for i in range(1, nv + 1):
        p = g.persona()
        veterinari.append((i, p["nome"], p["cognome"], SPECIALIZZAZIONI[i - 1]))
    spec = {v[0]: v[3] for v in veterinari}
    medici = [v[0] for v in veterinari[:-1] if v[3] == "Medicina generale"]
    altri = [v[0] for v in veterinari[:-1]]
    # visite: il quinto animale e gli ultimi due non sono mai stati visitati
    senza = {animali[-1][0], animali[-2][0], animali[4][0]}
    an_ok = [a for a in animali if a[0] not in senza]
    a_om1 = next(a for a in animali if a[6] == 2)            # animale del proprietario 2 (omonimo)
    a_om2 = next(a for a in animali if a[6] == npr - 1)      # animale del proprietario npr-1 (omonimo)
    piani = [(animali[0], medici[0]), (animali[0], medici[0]), (animali[0], 3), (animali[1], medici[0]),
             (animali[1], 2), (animali[2], medici[-1]), (animali[2], 3), (animali[3], medici[0]),
             (a_om1, medici[0]), (a_om2, medici[0]), (a_om2, 2)]
    vis = list(piani)
    while len(vis) < nk:
        a = g.scegli([x for x in an_ok if x[0] not in (a_om1[0], a_om2[0])])
        v = g.scegli(medici) if g.prob(0.55) else g.scegli(altri)
        vis.append((a, v))
    righe = []
    for a, v in vis:
        data = g.data_tra(a[5], min(FINE, g.dopo(a[5], 0, 500)))
        motivo, costo = g.scegli(MOTIVI[spec[v]])
        righe.append((a[0], v, data, motivo, decimal.Decimal(costo)))
    righe.sort(key=lambda r: (r[2], r[0]))
    visite = [(k + 1,) + r for k, r in enumerate(righe)]
    return {"Proprietari": proprietari, "Animali": animali, "Veterinari": veterinari, "Visite": visite}


CONTROLLI = [
    ("una visita non precede la registrazione dell'animale",
     "SELECT * FROM Visite v JOIN Animali a ON v.IdAnimale = a.IdAnimale WHERE v.Data < a.DataRegistrazione"),
    ("un animale è registrato dopo la nascita",
     "SELECT * FROM Animali WHERE DataRegistrazione <= DataNascita"),
    ("il motivo della visita è coerente con la specializzazione",
     "SELECT * FROM Visite v JOIN Veterinari t ON v.IdVeterinario = t.IdVeterinario "
     "WHERE t.Specializzazione = 'Medicina generale' AND v.Motivo NOT IN ('Vaccinazione', 'Controllo', 'Visita urgente')"),
]

TRAPPOLE = [
    "tre animali (il quinto e gli ultimi due) non sono mai stati visitati, e alcuni gatti registrati nel 2025 hanno più visite: "
    "una JOIN inutile con Visite in una query sugli animali perde i primi e ripete i secondi",
    "Animali.DataRegistrazione e Visite.Data sono date diverse: filtrare l'una al posto dell'altra cambia il risultato",
    "gatti registrati esattamente il 2025-01-01 e il 2025-12-31 (e il 2024-12-31, il 2026-01-01): smascherano i confini dell'anno",
    "tre animali senza visite (LEFT JOIN), l'ultimo veterinario non ha ancora visitato",
    "due animali si chiamano «Luna»: raggruppare per nome dell'animale li fonde",
    "il secondo e il penultimo proprietario sono omonimi, con un animale ciascuno: raggruppare per nome dà 2 animali e supera HAVING >= 2; "
    "i loro animali hanno 1 e 2 visite, delle quali una ciascuno in Medicina generale",
    "alcuni animali hanno Razza NULL; i costi sono tondi (40.00, 45.00, 80.00…)",
]
