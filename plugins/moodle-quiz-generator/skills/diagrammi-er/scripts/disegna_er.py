#!/usr/bin/env python3
"""Dalla descrizione testuale di un diagramma E/R al file .drawio e al PNG, nella notazione del libro.

Uso:
    python3 disegna_er.py DIAGRAMMA.er [CARTELLA] [--scala=1.25] [--solo-drawio]

Scrive nella CARTELLA (predefinita: quella del file .er) DIAGRAMMA.drawio, da aprire e ritoccare in
draw.io, e DIAGRAMMA.png, disegnato da drawio_png.py leggendo il .drawio. Dopo un ritocco in draw.io
il PNG si rifà con:  python3 drawio_png.py DIAGRAMMA.drawio

La descrizione (formato completo in references/descrizione.md della skill):

    titolo: Calciatori e squadre
    colori: entita=rosa associazioni=azzurro
    griglia: 250 170

    entita Calciatore @ 0 0
        sinistra: *IDCalciatore, Nome, Cognome
    entita Squadra @ 2 0
        sopra: *Nome, Citta, PosizioneCampionato

    associazione gioca in: Calciatore (1,1) -- Squadra (1,N)
        sotto: DataIngaggio

- entita NOME @ COLONNA RIGA: posizione sulla griglia (anche con decimali, per esempio 1.5);
- sopra / sotto / sinistra / destra: gli attributi su quel lato; * davanti alla chiave primaria.
  Un solo * = chiave semplice (pallino pieno); più * sullo stesso lato = chiave composta (linea con il
  pallino nero che taglia i loro gambetti);
- identificata da: ASSOC1, ASSOC2  (entità debole): la linea della chiave taglia anche le linee di
  quelle associazioni, che devono arrivare a destra o a sinistra dell'entità;
- associazione NOME: ENTITA1 (min,max) -- ENTITA2 (min,max) [@ COLONNA RIGA]: la cardinalità si
  scrive accanto all'entità a cui si riferisce. Senza @ il rombo va a metà tra le due entità, che
  devono stare sulla stessa riga o sulla stessa colonna. Con la stessa entità ai due lati è un'associazione
  ricorsiva: il rombo va a destra dell'entità (o a sinistra con «@ sinistra»), la prima cardinalità sulla
  linea a gomito, la seconda sulla linea diritta;
- sopra / sotto sotto un'associazione: i suoi attributi.
"""
import html
import math
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from drawio_png import disegna, font, leggi_modello  # noqa: E402
from modello_er import leggi, specializzazioni, etichetta_gerarchia  # noqa: E402

COLORI = {
    "azzurro": ("#dae8fc", "#6c8ebf"),
    "rosa": ("#f8cecc", "#b85450"),
    "verde": ("#d5e8d4", "#82b366"),
    "giallo": ("#fff2cc", "#d6b656"),
    "arancio": ("#ffe6cc", "#d79b00"),
    "bianco": ("#ffffff", "#000000"),
}
FS = 12          # dimensione del testo (come draw.io)
FS_ENTITA = 13
GAMBO_V = 22     # gambetto degli attributi sopra e sotto
GAMBO_O = 18     # gambetto degli attributi a sinistra e a destra
R = 4            # raggio del pallino
H_ENT = 60
W_MIN = 110
DIST_CARD = 32   # distanza della cardinalità dall'entità lungo la linea
LATI = ("sopra", "sotto", "sinistra", "destra")
OPZ = "(0,1)"    # cardinalità dell'attributo opzionale, sul suo gambetto
GAMBO_OPZ = 30   # di quanto si allungano i gambetti di un fianco con un attributo opzionale
PASSO_O, PASSO_OPZ = 18, 30   # distanza tra gli attributi di un fianco, senza e con attributi opzionali


def lw(t, fs=FS):
    return font(fs).getlength(t)


# ---------------------------------------------------------------- lettura della descrizione: modello_er.py

# ---------------------------------------------------------------- celle draw.io

class Modello:
    def __init__(self):
        self.celle = []      # (ordine, xml); le linee prima delle forme
        self.n = 0

    def nuovo_id(self, pref):
        self.n += 1
        return "%s%d" % (pref, self.n)

    def vertice(self, cid, valore, stile, x, y, w, h, parent="1", ordine=1):
        self.celle.append((ordine, '<mxCell id="%s" value="%s" style="%s" vertex="1" parent="%s">'
                                   '<mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry"/></mxCell>'
                           % (cid, html.escape(valore, quote=True), stile, parent, n(x), n(y), n(w), n(h))))

    def linea(self, cid, stile, source=None, target=None, sp=None, tp=None, punti=(), parent="1", figli=""):
        attr = ""
        if source:
            attr += ' source="%s"' % source
        if target:
            attr += ' target="%s"' % target
        g = '<mxGeometry relative="1" as="geometry">'
        if sp:
            g += '<mxPoint x="%s" y="%s" as="sourcePoint"/>' % (n(sp[0]), n(sp[1]))
        if tp:
            g += '<mxPoint x="%s" y="%s" as="targetPoint"/>' % (n(tp[0]), n(tp[1]))
        if punti:
            g += '<Array as="points">%s</Array>' % "".join('<mxPoint x="%s" y="%s"/>' % (n(a), n(b)) for a, b in punti)
        g += "</mxGeometry>"
        self.celle.append((0, '<mxCell id="%s" style="%s" edge="1" parent="%s"%s>%s</mxCell>%s'
                           % (cid, stile, parent, attr, g, figli.replace("__LINEA__", cid))))

    def xml(self, titolo):
        corpo = "".join(x for _, x in sorted(self.celle, key=lambda c: c[0]))
        return ('<mxfile host="disegna_er.py" type="device"><diagram id="er" name="%s">'
                '<mxGraphModel grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
                'page="0" pageScale="1" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
                '%s</root></mxGraphModel></diagram></mxfile>\n' % (html.escape(titolo, quote=True), corpo))


def n(v):
    """Numero per il file: coordinate al decimo, frazioni (exitX, posizione delle etichette) al millesimo."""
    v = float(v)
    v = round(v, 3) if abs(v) <= 1 else round(v, 1)
    return str(int(v)) if v == int(v) else str(v)


def st_forma(base, colore, extra=""):
    f, s = COLORI[colore]
    return "%swhiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontColor=#000000;%s" % (base, f, s, extra)


ST_LINEA = "endArrow=none;html=1;rounded=0;strokeColor=#000000;"
ST_TESTO = "text;html=1;strokeColor=none;fillColor=none;fontColor=#000000;fontSize=%d;" % FS
ST_CARD = ("edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=%d;"
           "labelBackgroundColor=none;fontColor=#000000;" % FS)


# ---------------------------------------------------------------- impaginazione

DUE_FILE = 5     # da quanti attributi sopra o sotto le etichette si dispongono su due file
GAMBO_FILA = 20  # di quanto è più lungo il gambetto della seconda fila


def file_sopra_sotto(nomi):
    """Fila di ogni attributo di un lato sopra o sotto: 0 vicina al rettangolo, 1 lontana (gambetto più lungo).
    Con molti attributi le etichette si alternano su due file, così il rettangolo non diventa lunghissimo."""
    return [i % 2 if len(nomi) >= DUE_FILE else 0 for i in range(len(nomi))]


def centri_sopra_sotto(nomi, opzionali=()):
    """Centri dei gambetti di un lato sopra o sotto, dal primo: le etichette affiancate a 14 px, più lo
    spazio della cardinalità (0,1) a destra del gambetto di un attributo opzionale. Su due file: le etichette
    della stessa fila restano a 14 px; un'etichetta della fila vicina sta lontana dal gambetto lungo accanto."""
    larg = [lw(a.lstrip("*")) for a in nomi]
    fila = file_sopra_sotto(nomi)
    extra = lambda j: max(0, lw(OPZ) + 6 - larg[j] / 2) if nomi[j] in opzionali else 0
    centri = []
    for i, l in enumerate(larg):
        if not i:
            centri.append(0.0)
            continue
        if not any(fila):
            centri.append(centri[-1] + larg[i - 1] / 2 + 14 + l / 2 + extra(i - 1))
            continue
        vicina = i if fila[i] == 0 else i - 1          # la sua etichetta incontra il gambetto lungo dell'altra
        c = centri[-1] + larg[vicina] / 2 + 8 + (extra(vicina) if vicina == i - 1 else 0)
        if i >= 2:
            c = max(c, centri[i - 2] + larg[i - 2] / 2 + 14 + l / 2 + extra(i - 2))
        centri.append(c)
    return larg, centri


def passi_fianco(nomi, opzionali=()):
    """Spazio verticale di ogni attributo di un fianco: più spazio solo per quelli opzionali, che hanno la
    cardinalità sotto il gambetto."""
    return [PASSO_OPZ if a in opzionali else PASSO_O for a in nomi]


def attributi_lato(lato, nomi, box, gambo, allinea="centro", opzionali=()):
    """Posizioni (in coordinate assolute) di gambetti, pallini ed etichette degli attributi di un lato."""
    x, y, w, h = box
    out = []
    if lato in ("sopra", "sotto"):
        # posizione dei gambetti: si centra l'arco dei gambetti (dal primo all'ultimo), così i gambetti
        # restano dentro il rettangolo anche se le etichette escono
        larg, centri = centri_sopra_sotto(nomi, opzionali)
        fila = file_sopra_sotto(nomi)
        arco = centri[-1]
        if allinea == "sinistra":
            base = x + 12
        elif allinea == "destra":
            base = x + w - 12 - arco
        else:
            base = x + w / 2 - arco / 2
        for a, l, c0, f in zip(nomi, larg, centri, fila):
            cx = base + c0
            y0 = y if lato == "sopra" else y + h
            g = gambo + GAMBO_FILA * f
            yc = y0 - g if lato == "sopra" else y0 + g
            et = (cx - l / 2 - 2, yc - R - 2 - 16, l + 4, 16, "center", "bottom") if lato == "sopra" else \
                 (cx - l / 2 - 2, yc + R + 1, l + 4, 16, "center", "top")
            out.append({"nome": a.lstrip("*"), "chiave": a.startswith("*"), "opzionale": a in opzionali,
                        "attacco": (cx, y0),
                        "fx": (cx - x) / w, "fy": 0 if lato == "sopra" else 1, "pallino": (cx, yc),
                        "etichetta": et})
    else:
        if any(a in opzionali for a in nomi):
            gambo += GAMBO_OPZ
        passi = passi_fianco(nomi, opzionali)
        cur = y + h / 2 - sum(passi) / 2
        for i, a in enumerate(nomi):
            cy = cur + passi[i] / 2
            cur += passi[i]
            x0 = x if lato == "sinistra" else x + w
            xc = x0 - gambo if lato == "sinistra" else x0 + gambo
            l = lw(a.lstrip("*"))
            et = (xc - R - 3 - l - 4, cy - 8, l + 4, 16, "right", "middle") if lato == "sinistra" else \
                 (xc + R + 3, cy - 8, l + 4, 16, "left", "middle")
            out.append({"nome": a.lstrip("*"), "chiave": a.startswith("*"), "opzionale": a in opzionali,
                        "attacco": (x0, cy),
                        "fx": 0 if lato == "sinistra" else 1, "fy": (cy - y) / h, "pallino": (xc, cy),
                        "etichetta": et})
    return out


def dimensioni_entita(e):
    w = max(W_MIN, lw(e["nome"], FS_ENTITA) + 36, e.get("larghezza", 0))
    for lato in ("sopra", "sotto"):
        nomi = e["attr"].get(lato, [])
        if len(nomi) > 1:
            _, centri = centri_sopra_sotto(nomi, e["opzionali"])
            w = max(w, centri[-1] + 24)
    h = H_ENT
    for lato in ("sinistra", "destra"):
        nomi = e["attr"].get(lato, [])
        h = max(h, sum(passi_fianco(nomi, e["opzionali"])) + 10)
    return w, h


def impagina(diag):
    gx, gy = diag["griglia"]
    senza = [e["nome"] for e in diag["entita"].values() if e["pos"] is None]
    if senza:
        raise SystemExit("ERRORE: per il diagramma ogni entità ha bisogno della posizione (entita NOME @ COLONNA "
                         "RIGA): manca a %s" % ", ".join(senza))
    for e in diag["entita"].values():
        w, h = dimensioni_entita(e)
        c, r = e["pos"]
        e["box"] = (c * gx - w / 2, r * gy - h / 2, w, h)
        e["centro"] = (c * gx, r * gy)
    # entità di grandezza paragonabile: un rettangolo molto più largo o più alto degli altri si nota subito
    ws = sorted(e["box"][2] for e in diag["entita"].values())
    hs = sorted(e["box"][3] for e in diag["entita"].values())
    if len(ws) >= 3:
        mw, mh = ws[len(ws) // 2], hs[len(hs) // 2]
        for e in diag["entita"].values():
            w, h = e["box"][2], e["box"][3]
            if w > 2.2 * mw:
                print("AVVISO: «%s» è molto più larga delle altre entità (%d px, di solito %d): dividi gli attributi "
                      "sopra e sotto, o togli «larghezza:» se non serve" % (e["nome"], w, mw))
            if h > 2 * mh:
                print("AVVISO: «%s» è molto più alta delle altre entità (%d px, di solito %d): sposta qualche "
                      "attributo sopra o sotto" % (e["nome"], h, mh))
    for a in diag["associazioni"]:
        e1, e2 = diag["entita"][a["e1"]], diag["entita"][a["e2"]]
        tw = lw(a["nome"])
        rw, rh = max(90, min(tw + 44, 130)), (50 if tw + 44 <= 130 else 60)
        a["dim"] = (rw, rh)
        if e1 is e2:
            x, y, w, h = e1["box"]
            a["ricorsiva"] = True
            sinistra = a["pos"].lower() == "sinistra"
            a["lato_ric"] = "sinistra" if sinistra else "destra"
            cx = x - 60 - rw / 2 if sinistra else x + w + 60 + rw / 2
            a["centro"] = (cx, y + h / 2)
            continue
        a["ricorsiva"] = False
        if a["pos"]:
            try:
                c, r = [float(v) for v in a["pos"].split()]
            except ValueError:
                raise SystemExit("ERRORE: posizione dell'associazione «%s»: @ COLONNA RIGA" % a["nome"])
            a["centro"] = (c * gx, r * gy)
        else:
            (x1, y1), (x2, y2) = e1["centro"], e2["centro"]
            if abs(y1 - y2) < 1:
                b1, b2 = e1["box"], e2["box"]
                sx, dx = (b1, b2) if x1 < x2 else (b2, b1)
                a["centro"] = ((sx[0] + sx[2] + dx[0]) / 2, y1)
            elif abs(x1 - x2) < 1:
                b1, b2 = e1["box"], e2["box"]
                su, giu = (b1, b2) if y1 < y2 else (b2, b1)
                a["centro"] = (x1, (su[1] + su[3] + giu[1]) / 2)
            else:
                raise SystemExit("ERRORE: «%s» collega entità che non stanno sulla stessa riga né sulla stessa "
                                 "colonna: indica dove va il rombo con @ COLONNA RIGA" % a["nome"])


def collegamento(e, centro_rombo, dim_rombo):
    """Lati di attacco tra un'entità e un rombo: (exitX, exitY) sull'entità, (entryX, entryY) sul rombo, asse."""
    x, y, w, h = e["box"]
    cx, cy = x + w / 2, y + h / 2
    rx, ry = centro_rombo
    dx, dy = rx - cx, ry - cy
    if abs(dx) / (w / 2 + dim_rombo[0] / 2) >= abs(dy) / (h / 2 + dim_rombo[1] / 2):
        if dx > 0:
            return (1, 0.5), (0, 0.5), "o"
        return (0, 0.5), (1, 0.5), "o"
    if dy > 0:
        return (0.5, 1), (0.5, 0), "v"
    return (0.5, 0), (0.5, 1), "v"


NOMI_LATO = {(1, 0.5): "destra", (0, 0.5): "sinistra", (0.5, 1): "sotto", (0.5, 0): "sopra"}


def lati_condivisi(diag):
    """Lati di un'entità su cui arrivano più linee di associazioni: {(entità, lato): [nomi]}."""
    uso = {}
    for a in diag["associazioni"]:
        if a.get("ricorsiva"):
            continue
        for nome_e in (a["e1"], a["e2"]):
            (ex, ey), _, _ = collegamento(diag["entita"][nome_e], a["centro"], a["dim"])
            uso.setdefault((nome_e, NOMI_LATO[(ex, ey)]), []).append(a["nome"])
    return {k: v for k, v in uso.items() if len(v) > 1}


def attacco_condiviso(e, lato, centro_rombo):
    """Su un lato condiviso da più linee ognuna parte dal punto del lato di fronte al suo rombo (proiezione
    del centro del rombo sul lato, tenuta lontana dagli spigoli): con il rombo allineato la linea resta dritta.
    Restituisce (exitX, exitY) e se la proiezione è stata spostata (linea obliqua)."""
    x, y, w, h = e["box"]
    rx, ry = centro_rombo
    if lato in ("sopra", "sotto"):
        f = (rx - x) / w
        fc = min(max(f, 0.1), 0.9)
        return (fc, 0 if lato == "sopra" else 1), abs(fc - f) > 1e-6
    f = (ry - y) / h
    fc = min(max(f, 0.15), 0.85)
    return (0 if lato == "sinistra" else 1, fc), abs(fc - f) > 1e-6


# ---------------------------------------------------------------- costruzione del .drawio

def controlla_lati(diag):
    """Avvisa quando una linea arriva sul lato dove stanno gli attributi, o quando più linee sullo stesso lato
    sono troppo vicine o non partono di fronte al loro rombo."""
    nomi_lato = NOMI_LATO
    condivisi = lati_condivisi(diag)
    usati = {nome: [] for nome in diag["entita"]}
    for a in diag["associazioni"]:
        if a["ricorsiva"]:
            # il gomito parte dall'alto, ma gli attributi sopra si spostano dalla parte opposta
            usati[a["e1"]] += [("sopra*", a["nome"]), (a["lato_ric"], a["nome"])]
            continue
        for nome_e in (a["e1"], a["e2"]):
            (ex, ey), _, _ = collegamento(diag["entita"][nome_e], a["centro"], a["dim"])
            usati[nome_e].append((nomi_lato[(ex, ey)], a["nome"]))
    for g in diag["gerarchie"]:
        _, gy0, _, gh = diag["entita"][g["gen"]]["box"]
        for sp in g["spec"]:
            _, sy0, _, sh = diag["entita"][sp]["box"]
            sotto = sy0 > gy0
            usati[g["gen"]].append(("sotto" if sotto else "sopra", "gerarchia"))
            usati[sp].append(("sopra" if sotto else "sotto", "gerarchia"))
    avvisi = []
    for nome, lati in usati.items():
        e = diag["entita"][nome]
        visti = {}
        for lato, nome_a in lati:
            gomito = lato.endswith("*")
            lato = lato.rstrip("*")
            if lato in e["attr"] and not gomito:
                avvisi.append("«%s»: la linea di «%s» arriva %s, dove ci sono gli attributi: spostali su un altro lato"
                              % (nome, nome_a, {"sopra": "sopra", "sotto": "sotto"}.get(lato, "a " + lato)))
            if lato in visti and visti[lato] != nome_a and "gerarchia" in (visti[lato], nome_a):
                avvisi.append("«%s»: la linea di «%s» arriva sullo stesso lato della gerarchia (%s): sposta un'entità "
                              "o un rombo" % (nome, nome_a if visti[lato] == "gerarchia" else visti[lato], lato))
            visti.setdefault(lato, nome_a)
    # lati condivisi da più associazioni: linee dritte e abbastanza distanti
    for (nome, lato), nomi_a in condivisi.items():
        e = diag["entita"][nome]
        punti = []
        for a in diag["associazioni"]:
            if a.get("ricorsiva") or a["nome"] not in nomi_a or nome not in (a["e1"], a["e2"]):
                continue
            (fx, fy), spostato = attacco_condiviso(e, lato, a["centro"])
            if spostato:
                avvisi.append("«%s»: il rombo di «%s» non sta di fronte al lato %s dell'entità e la linea viene "
                              "obliqua: spostalo (@ COLONNA RIGA) o allarga l'entità" % (nome, a["nome"], lato))
            x, y, w, h = e["box"]
            punti.append(x + fx * w if lato in ("sopra", "sotto") else y + fy * h)
        punti.sort()
        if any(b - q < 40 for q, b in zip(punti, punti[1:])):
            avvisi.append("«%s»: sul lato %s le linee di %s partono troppo vicine: allontana i rombi"
                          % (nome, lato, " e ".join("«%s»" % x for x in nomi_a)))
    for av in avvisi:
        print("AVVISO: " + av)
    return avvisi


SINGOLARI_IN_I = {"analisi", "crisi", "tesi", "ipotesi", "sintesi", "diagnosi", "taxi", "bici", "brindisi",
                  "alibi", "safari", "kiwi", "mini", "maxi", "wifi", "partner"}


def controlla_nomi(diag):
    """Entità al singolare, verbo delle associazioni al singolare (convenzione del libro)."""
    for nome in diag["entita"]:
        ultima = re.split(r"[\s_]+", nome.strip())[-1].lower()
        if len(ultima) > 3 and ultima.endswith("i") and ultima not in SINGOLARI_IN_I:
            print("AVVISO: «%s» sembra un plurale: il nome dell'entità va al singolare (se è già singolare, "
                  "ignora l'avviso)" % nome)
    for a in diag["associazioni"]:
        prima = a["nome"].split()[0].lower() if a["nome"].split() else ""
        if len(prima) > 4 and re.search(r"(ano|ono|nno)$", prima):
            print("AVVISO: l'associazione «%s» sembra avere il verbo al plurale: con le entità al singolare il "
                  "verbo va al singolare (effettua, comprende, ha)" % a["nome"])


def costruisci(diag):
    impagina(diag)
    controlla_lati(diag)
    condivisi = lati_condivisi(diag)
    controlla_nomi(diag)
    M = Modello()
    ce, ca = diag["colori"]["entita"], diag["colori"]["associazioni"]
    id_ent, id_ass, linee_ass = {}, {}, {}

    # associazioni: rombo (con i suoi attributi in un gruppo) e linee verso le entità
    for a in diag["associazioni"]:
        rw, rh = a["dim"]
        cx, cy = a["centro"]
        rid = M.nuovo_id("a")
        id_ass[id(a)] = rid
        a["box"] = (cx - rw / 2, cy - rh / 2, rw, rh)
        gruppo = None
        if a["attr"]:
            gruppo = M.nuovo_id("g")
            pezzi = []
            for lato, nomi in a["attr"].items():
                k = len(nomi)
                for i, nome in enumerate(nomi):
                    nome = nome.lstrip("*")
                    l = lw(nome)
                    if lato in ("sopra", "sotto"):
                        fx = 0.5 if k == 1 else 0.3 + 0.4 * i / (k - 1)
                        # punto sul perimetro del rombo
                        off = abs(fx - 0.5) * 2
                        fy = (0.5 - 0.5 * (1 - off)) if lato == "sopra" else (0.5 + 0.5 * (1 - off))
                        px, py = cx - rw / 2 + fx * rw, cy - rh / 2 + fy * rh
                        pc = (px, py - GAMBO_V) if lato == "sopra" else (px, py + GAMBO_V)
                        et = (pc[0] - l / 2 - 2, pc[1] - R - 18, l + 4, 16, "center", "bottom") if lato == "sopra" \
                            else (pc[0] - l / 2 - 2, pc[1] + R + 1, l + 4, 16, "center", "top")
                    else:
                        fy = 0.5 if k == 1 else 0.35 + 0.3 * i / (k - 1)
                        fx = abs(fy - 0.5) if lato == "sinistra" else 1 - abs(fy - 0.5)
                        px, py = cx - rw / 2 + fx * rw, cy - rh / 2 + fy * rh
                        go = GAMBO_O + (GAMBO_OPZ if any(x in a["opzionali"] for x in nomi) else 0)
                        pc = (px - go, py) if lato == "sinistra" else (px + go, py)
                        et = (pc[0] - R - 3 - l - 4, pc[1] - 8, l + 4, 16, "right", "middle") if lato == "sinistra" \
                            else (pc[0] + R + 3, pc[1] - 8, l + 4, 16, "left", "middle")
                    pezzi.append((nome, fx, fy, pc, et, lato))
            xs = [a["box"][0], a["box"][0] + rw] + [p[4][0] for p in pezzi] + [p[4][0] + p[4][2] for p in pezzi]
            ys = [a["box"][1], a["box"][1] + rh] + [p[4][1] for p in pezzi] + [p[4][1] + p[4][3] for p in pezzi]
            gx0, gy0 = min(xs), min(ys)
            M.vertice(gruppo, "", "group;", gx0, gy0, max(xs) - gx0, max(ys) - gy0, ordine=1)
            M.vertice(rid, a["nome"], st_forma("rhombus;", ca, "fontSize=%d;" % FS),
                      a["box"][0] - gx0, a["box"][1] - gy0, rw, rh, parent=gruppo, ordine=2)
            for nome, fx, fy, pc, et, lato in pezzi:
                pid, lid, tid = M.nuovo_id("p"), M.nuovo_id("l"), M.nuovo_id("t")
                M.vertice(pid, "", "ellipse;html=1;aspect=fixed;fillColor=#ffffff;strokeColor=#000000;",
                          pc[0] - R - gx0, pc[1] - R - gy0, 2 * R, 2 * R, parent=gruppo, ordine=3)
                entra = {"sopra": (0.5, 1), "sotto": (0.5, 0), "sinistra": (1, 0.5), "destra": (0, 0.5)}[lato]
                M.linea(lid, ST_LINEA + "exitX=%s;exitY=%s;exitDx=0;exitDy=0;exitPerimeter=0;entryX=%s;entryY=%s;"
                        "entryDx=0;entryDy=0;" % (n(fx), n(fy), n(entra[0]), n(entra[1])),
                        source=rid, target=pid, parent=gruppo,
                        figli=opz_xml(M, lato) if nome in a["opzionali"] else "")
                M.vertice(tid, nome, ST_TESTO + "align=%s;verticalAlign=%s;" % (et[4], et[5]),
                          et[0] - gx0, et[1] - gy0, et[2], et[3], parent=gruppo, ordine=4)
        else:
            M.vertice(rid, a["nome"], st_forma("rhombus;", ca, "fontSize=%d;" % FS), *a["box"], ordine=2)

    # entità: rettangolo, attributi, chiave composta, in un gruppo per entità
    for nome, e in diag["entita"].items():
        x, y, w, h = e["box"]
        eid = M.nuovo_id("e")
        id_ent[nome] = eid
        ric = [a["lato_ric"] for a in diag["associazioni"] if a.get("ricorsiva") and a["e1"] == nome]
        allinea = "sinistra" if "destra" in ric else ("destra" if "sinistra" in ric else "centro")
        attr = {lato: attributi_lato(lato, e["attr"][lato], e["box"], GAMBO_V if lato in ("sopra", "sotto") else GAMBO_O,
                                     allinea if lato == "sopra" else "centro", e["opzionali"])
                for lato in LATI if lato in e["attr"]}
        chiavi = [(lato, p) for lato, ps in attr.items() for p in ps if p["chiave"]]
        lati_chiave = {lato for lato, _ in chiavi}
        if not chiavi and nome not in specializzazioni(diag):
            print("AVVISO: l'entità «%s» non ha la chiave primaria (* davanti all'attributo)" % nome)
        if len(lati_chiave) > 1:
            raise SystemExit("ERRORE: «%s»: gli attributi della chiave composta vanno sullo stesso lato" % nome)
        composta = len(chiavi) > 1 or bool(e["deboli"])
        linea_chiave = None
        if e["deboli"] and not chiavi:
            raise SystemExit("ERRORE: «%s» è identificata da un'associazione ma non ha attributi con *" % nome)
        if composta:
            lato = chiavi[0][0]
            xs_k = [p["pallino"][0] for _, p in chiavi]
            ys_k = [p["pallino"][1] for _, p in chiavi]
            if lato in ("sopra", "sotto"):
                yl = (y - GAMBO_V * 0.5) if lato == "sopra" else (y + h + GAMBO_V * 0.5)
                if not e["deboli"]:
                    linea_chiave = [(max(xs_k) + 8, yl), (min(xs_k) - 24, yl)]
                else:
                    lati_ass = []
                    for nome_a in e["deboli"]:
                        aa = [a for a in diag["associazioni"] if a["nome"] == nome_a and nome in (a["e1"], a["e2"])]
                        if not aa:
                            raise SystemExit("ERRORE: «%s» è identificata da «%s», che non è un'associazione "
                                             "collegata a «%s»" % (nome, nome_a, nome))
                        (ex, ey), _, asse = collegamento(e, aa[0]["centro"], aa[0]["dim"])
                        if asse != "o":
                            raise SystemExit("ERRORE: «%s»: l'associazione «%s» deve arrivare a destra o a "
                                             "sinistra dell'entità (entità debole)" % (nome, nome_a))
                        lati_ass.append("sinistra" if ex == 0 else "destra")
                    ym = y + h / 2
                    xsx, xdx = x - 8, x + w + 8
                    if "sinistra" in lati_ass and "destra" in lati_ass:
                        pts = [(xsx, ym - 10), (xsx, yl), (xdx, yl), (xdx, ym)]
                    elif "destra" in lati_ass:
                        pts = [(min(xs_k) - 10, yl), (xdx, yl), (xdx, ym)]
                    else:
                        pts = [(max(xs_k) + 8, yl), (xsx, yl), (xsx, ym)]
                    linea_chiave = pts
            else:
                if e["deboli"]:
                    raise SystemExit("ERRORE: «%s»: con «identificata da» gli attributi della chiave vanno "
                                     "sopra o sotto" % nome)
                xl = (x - GAMBO_O * 0.5) if lato == "sinistra" else (x + w + GAMBO_O * 0.5)
                linea_chiave = [(xl, max(ys_k) + 6), (xl, min(ys_k) - 20)]
        # gruppo: ingombro di entità, etichette e linea della chiave
        xs, ys = [x, x + w], [y, y + h]
        for ps in attr.values():
            for p in ps:
                ex, ey, ew, eh = p["etichetta"][:4]
                xs += [ex, ex + ew, p["pallino"][0] - R, p["pallino"][0] + R]
                ys += [ey, ey + eh, p["pallino"][1] - R, p["pallino"][1] + R]
        if linea_chiave:
            xs += [p[0] - 3 for p in linea_chiave] + [p[0] + 3 for p in linea_chiave]
            ys += [p[1] - 3 for p in linea_chiave] + [p[1] + 3 for p in linea_chiave]
        if not attr:
            M.vertice(eid, nome, st_forma("rounded=0;", ce, "fontSize=%d;" % FS_ENTITA), x, y, w, h, ordine=2)
            continue
        gid = M.nuovo_id("g")
        gx0, gy0 = min(xs), min(ys)
        M.vertice(gid, "", "group;", gx0, gy0, max(xs) - gx0, max(ys) - gy0, ordine=1)
        M.vertice(eid, nome, st_forma("rounded=0;", ce, "fontSize=%d;" % FS_ENTITA), x - gx0, y - gy0, w, h,
                  parent=gid, ordine=2)
        for lato, ps in attr.items():
            for p in ps:
                pid, lid, tid = M.nuovo_id("p"), M.nuovo_id("l"), M.nuovo_id("t")
                pieno = p["chiave"] and not composta
                M.vertice(pid, "", "ellipse;html=1;aspect=fixed;fillColor=%s;strokeColor=#000000;"
                          % ("#000000" if pieno else "#ffffff"),
                          p["pallino"][0] - R - gx0, p["pallino"][1] - R - gy0, 2 * R, 2 * R, parent=gid, ordine=3)
                entra = {"sopra": (0.5, 1), "sotto": (0.5, 0), "sinistra": (1, 0.5), "destra": (0, 0.5)}[lato]
                M.linea(lid, ST_LINEA + "exitX=%s;exitY=%s;exitDx=0;exitDy=0;exitPerimeter=0;entryX=%s;entryY=%s;"
                        "entryDx=0;entryDy=0;" % (n(p["fx"]), n(p["fy"]), n(entra[0]), n(entra[1])),
                        source=eid, target=pid, parent=gid, figli=opz_xml(M, lato) if p["opzionale"] else "")
                ex, ey, ew, eh, al, va = p["etichetta"]
                M.vertice(tid, p["nome"], ST_TESTO + "align=%s;verticalAlign=%s;" % (al, va),
                          ex - gx0, ey - gy0, ew, eh, parent=gid, ordine=4)
        if linea_chiave:
            kid = M.nuovo_id("k")
            rel = [(px - gx0, py - gy0) for px, py in linea_chiave]
            M.linea(kid, "endArrow=oval;endFill=1;endSize=6;startArrow=none;html=1;rounded=0;strokeColor=#000000;",
                    sp=rel[0], tp=rel[-1], punti=rel[1:-1], parent=gid)

    # linee delle associazioni, con le cardinalità
    for a in diag["associazioni"]:
        rid = id_ass[id(a)]
        e1, e2 = diag["entita"][a["e1"]], diag["entita"][a["e2"]]
        if a["ricorsiva"]:
            x, y, w, h = e1["box"]
            cx, cy = a["centro"]
            sin = a["lato_ric"] == "sinistra"
            fx = 0.25 if sin else 0.75
            ygom = y - 40
            # linea a gomito: dall'alto dell'entità al vertice alto del rombo
            pts = [(x + fx * w, ygom), (cx, ygom)]
            lung = (y - ygom) + abs(cx - (x + fx * w)) + (a["box"][1] - ygom)
            card1 = card_xml(M, a["c1"], -1 + 2 * 14 / lung, (-22 if not sin else 22, 0))
            M.linea(M.nuovo_id("l"), ST_LINEA + "exitX=%s;exitY=0;exitDx=0;exitDy=0;exitPerimeter=0;entryX=0.5;"
                    "entryY=0;entryDx=0;entryDy=0;" % n(fx), source=id_ent[a["e1"]], target=rid, punti=pts,
                    figli=card1[1], **card1[0])
            # linea diritta: dal fianco dell'entità al vertice laterale del rombo
            lung = abs((x if sin else x + w) - (a["box"][0] + (a["box"][2] if sin else 0)))
            card2 = card_xml(M, a["c2"], -1 + 2 * DIST_CARD / max(lung, 1), (0, -10))
            M.linea(M.nuovo_id("l"), ST_LINEA + "exitX=%s;exitY=0.5;exitDx=0;exitDy=0;exitPerimeter=0;entryX=%s;"
                    "entryY=0.5;entryDx=0;entryDy=0;" % (0 if sin else 1, 1 if sin else 0),
                    source=id_ent[a["e2"]], target=rid, figli=card2[1], **card2[0])
            continue
        for e, nome_e, card in ((e1, a["e1"], a["c1"]), (e2, a["e2"], a["c2"])):
            (exx, exy), (enx, eny), asse = collegamento(e, a["centro"], a["dim"])
            if (nome_e, NOMI_LATO[(exx, exy)]) in condivisi:
                (exx, exy), _ = attacco_condiviso(e, NOMI_LATO[(exx, exy)], a["centro"])
            x, y, w, h = e["box"]
            ax, ay = x + exx * w, y + exy * h
            bx, by = a["box"][0] + enx * a["dim"][0], a["box"][1] + eny * a["dim"][1]
            lung = math.dist((ax, ay), (bx, by)) or 1
            if asse == "o":
                dist, off = DIST_CARD, (0, -10)
            else:
                dist, off = 16, (-22, 0)
            if lung < dist + 12:
                print("AVVISO: «%s» è molto vicina a «%s»: allarga la griglia" % (a["nome"], nome_e))
            cx_ = card_xml(M, card, -1 + 2 * min(dist, lung / 2) / lung, off)
            M.linea(M.nuovo_id("l"), ST_LINEA + "exitX=%s;exitY=%s;exitDx=0;exitDy=0;exitPerimeter=0;entryX=%s;"
                    "entryY=%s;entryDx=0;entryDy=0;" % (n(exx), n(exy), n(enx), n(eny)),
                    source=id_ent[nome_e], target=rid, figli=cx_[1], **cx_[0])
    # gerarchie ISA: dalle specializzazioni una linea a T che sale alla generalizzazione, con la freccia
    for g in diag["gerarchie"]:
        gen = diag["entita"][g["gen"]]
        gx0, gy0, gw, gh = gen["box"]
        gcx = gx0 + gw / 2
        specs = [diag["entita"][s_] for s_ in g["spec"]]
        sotto = all(sp["box"][1] > gy0 for sp in specs)
        if sotto:
            bordo_g = gy0 + gh
            bordo_s = min(sp["box"][1] for sp in specs)
        else:
            bordo_g = gy0
            bordo_s = max(sp["box"][1] + sp["box"][3] for sp in specs)
        ymid = (bordo_g + bordo_s) / 2
        if abs(bordo_s - bordo_g) < 50:
            print("AVVISO: la gerarchia di «%s» ha le specializzazioni troppo vicine: allontanale" % g["gen"])
        etichetta = etichetta_gerarchia(g)
        for i, sp in enumerate(specs):
            sx0, sy0, sw, sh = sp["box"]
            scx = sx0 + sw / 2
            punti = [] if abs(scx - gcx) < 1 else [(scx, ymid), (gcx, ymid)]
            lung = abs(ymid - (sy0 if sotto else sy0 + sh)) + abs(scx - gcx) + abs(bordo_g - ymid)
            figli = ""
            if i == 0:
                frac = 1 - 2 * min(18, abs(bordo_g - ymid) / 2) / max(lung, 1)
                figli = card_xml(M, "", 0, (0, 0))[1]
                lid = M.nuovo_id("c")
                figli = ('<mxCell id="%s" value="%s" style="%s" vertex="1" connectable="0" parent="__LINEA__">'
                         '<mxGeometry x="%s" relative="1" as="geometry"><mxPoint x="%s" y="0" as="offset"/>'
                         '</mxGeometry></mxCell>' % (lid, etichetta, ST_CARD + "align=left;", n(frac),
                                                     n(8 + lw(etichetta) / 2)))
            M.linea(M.nuovo_id("l"), "endArrow=block;endFill=1;endSize=10;html=1;rounded=0;strokeColor=#000000;"
                    "exitX=0.5;exitY=%s;exitDx=0;exitDy=0;exitPerimeter=0;entryX=0.5;entryY=%s;entryDx=0;"
                    "entryDy=0;" % (0 if sotto else 1, 1 if sotto else 0),
                    source=id_ent[sp["nome"]], target=id_ent[g["gen"]], punti=punti, figli=figli)
    return M.xml(diag["titolo"])


def opz_xml(M, lato):
    """La cardinalità (0,1) di un attributo opzionale, figlia del suo gambetto: sotto il gambetto per gli
    attributi ai fianchi, a destra per quelli sopra e sotto (come nelle figure dell'autore)."""
    off = (0, 8) if lato in ("sinistra", "destra") else (lw(OPZ) / 2 + 5, 0)
    return card_xml(M, OPZ, 0, off)[1]


def card_xml(M, testo, x, offset):
    """Etichetta della cardinalità come figlia della linea (si sposta con lei in draw.io)."""
    if not testo:
        return {}, ""
    if isinstance(testo, tuple):
        testo = "(%s,%s)" % testo
    t = testo if testo.startswith("(") else "(%s)" % testo
    lid = M.nuovo_id("c")
    # l'id della linea non è ancora noto: si usa un segnaposto sostituito da linea()
    figlio = ('<mxCell id="%s" value="%s" style="%s" vertex="1" connectable="0" parent="__LINEA__">'
              '<mxGeometry x="%s" relative="1" as="geometry"><mxPoint x="%s" y="%s" as="offset"/></mxGeometry>'
              '</mxCell>' % (lid, html.escape(t), ST_CARD, n(x), n(offset[0]), n(offset[1])))
    return {}, figlio


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        raise SystemExit(__doc__)
    opz = dict(x[2:].split("=", 1) if "=" in x else (x[2:], "1") for x in sys.argv[1:] if x.startswith("--"))
    src = a[0]
    cartella = a[1] if len(a) > 1 else os.path.dirname(os.path.abspath(src))
    os.makedirs(cartella, exist_ok=True)
    base = os.path.join(cartella, os.path.splitext(os.path.basename(src))[0])
    diag = leggi(open(src, encoding="utf-8").read())
    open(base + ".drawio", "w", encoding="utf-8").write(costruisci(diag))
    print("OK: %s.drawio" % base)
    if "solo-drawio" not in opz:
        img = disegna(leggi_modello(base + ".drawio"), float(opz.get("scala", 1.25)))
        img.save(base + ".png")
        print("OK: %s.png (%dx%d)" % (base, img.width, img.height))


if __name__ == "__main__":
    main()
