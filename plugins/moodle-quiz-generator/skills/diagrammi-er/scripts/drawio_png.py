#!/usr/bin/env python3
"""Disegna in PNG un diagramma .drawio fatto con le forme di disegna_er.py.

Uso:
    python3 drawio_png.py DIAGRAMMA.drawio [USCITA.png] [--scala=1.25] [--pagina=N]

Legge il file così come lo salva draw.io (anche dopo un ritocco a mano: elementi spostati, testi o
cardinalità cambiati, attributi aggiunti copiando quelli che ci sono) e lo disegna con le stesse
coordinate. Riconosce le forme che usa disegna_er.py:

  - rettangolo (entità), rombo (associazione), cerchio (pallino di un attributo), testo, gruppo;
  - linee senza frecce, con punti intermedi; la fine «oval» piena (il pallino della chiave composta) e
    la freccia piena «block» (gerarchie ISA);
  - etichette delle linee (le cardinalità).

Una forma diversa (un'immagine, una freccia, una forma di libreria) non viene ignorata in silenzio:
lo script la elenca e si ferma, salvo --forza. In quel caso conviene esportare il PNG da draw.io.
Il testo usa FreeSans (metriche di Helvetica, il carattere di draw.io) o, in mancanza, DejaVu Sans.

--scala=N  ingrandimento del PNG (predefinito 1.25, come le figure del libro; 2 per la stampa)
--pagina=N se il file ha più pagine, quale disegnare (dalla 1; predefinita la prima)
"""
import base64
import html
import math
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib

from PIL import Image, ImageDraw, ImageFont

SS = 4  # sovracampionamento: si disegna 4 volte più grande e si riduce

FONT_CANDIDATI = [
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/opentype/freefont/FreeSans.otf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]
FONT_GRASSETTO = [
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/opentype/freefont/FreeSansBold.otf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def trova_font(candidati):
    for p in candidati:
        if os.path.exists(p):
            return p
    return None


_FONT = {}


def font(px, grassetto=False):
    chiave = (round(px * 4), grassetto)
    if chiave not in _FONT:
        p = trova_font(FONT_GRASSETTO if grassetto else FONT_CANDIDATI) or trova_font(FONT_CANDIDATI)
        _FONT[chiave] = ImageFont.truetype(p, max(1, int(round(px)))) if p else ImageFont.load_default()
    return _FONT[chiave]


# ---------------------------------------------------------------- lettura del file

def stile(s):
    d = {}
    for parte in (s or "").split(";"):
        if not parte:
            continue
        if "=" in parte:
            k, v = parte.split("=", 1)
            d[k] = v
        else:
            d[parte] = "1"   # forma senza valore: «rhombus», «ellipse», «text», «group»
    return d


def leggi_modello(percorso, pagina=1):
    radice = ET.parse(percorso).getroot()
    if radice.tag == "mxGraphModel":
        return radice
    diagrammi = radice.findall("diagram")
    if not diagrammi:
        raise SystemExit("ERRORE: %s non sembra un file draw.io" % percorso)
    if pagina > len(diagrammi):
        raise SystemExit("ERRORE: il file ha %d pagine" % len(diagrammi))
    d = diagrammi[pagina - 1]
    m = d.find("mxGraphModel")
    if m is not None:
        return m
    # formato compresso di draw.io: base64 + deflate + urlencode
    testo = (d.text or "").strip()
    dati = zlib.decompress(base64.b64decode(testo), -15).decode("utf-8")
    return ET.fromstring(urllib.parse.unquote(dati))


class Cella:
    def __init__(self, el):
        self.id = el.get("id")
        self.parent = el.get("parent")
        self.valore = el.get("value") or ""
        self.st = stile(el.get("style"))
        self.vertex = el.get("vertex") == "1"
        self.edge = el.get("edge") == "1"
        self.source, self.target = el.get("source"), el.get("target")
        g = el.find("mxGeometry")
        self.x = self.y = self.w = self.h = 0.0
        self.relativa = False
        self.punti, self.sp, self.tp, self.offset = [], None, None, (0.0, 0.0)
        if g is not None:
            f = lambda k: float(g.get(k) or 0)
            self.x, self.y, self.w, self.h = f("x"), f("y"), f("width"), f("height")
            self.relativa = g.get("relative") == "1"
            for p in g.findall("mxPoint"):
                xy = (float(p.get("x") or 0), float(p.get("y") or 0))
                if p.get("as") == "sourcePoint":
                    self.sp = xy
                elif p.get("as") == "targetPoint":
                    self.tp = xy
                elif p.get("as") == "offset":
                    self.offset = xy
            arr = g.find("Array")
            if arr is not None:
                self.punti = [(float(p.get("x") or 0), float(p.get("y") or 0)) for p in arr.findall("mxPoint")]


def forma(c):
    s = c.st
    if "group" in s:
        return "gruppo"
    if "text" in s or "edgeLabel" in s:
        return "testo"
    if "rhombus" in s or s.get("shape") == "rhombus":
        return "rombo"
    if "ellipse" in s or s.get("shape") == "ellipse":
        return "cerchio"
    if "shape" in s or "image" in s or any(k in s for k in ("swimlane", "triangle", "cloud", "line")):
        return None
    return "rettangolo"


# ---------------------------------------------------------------- geometria

def origine(celle, cid):
    """Coordinate assolute dell'origine di una cella (somma dei gruppi che la contengono)."""
    x = y = 0.0
    c = celle.get(cid)
    while c is not None and c.vertex:
        x += c.x
        y += c.y
        c = celle.get(c.parent)
    return x, y


def box(celle, c):
    ox, oy = origine(celle, c.parent)
    return ox + c.x, oy + c.y, c.w, c.h


def punto_vincolo(celle, cid, fx, fy, verso):
    """Punto di attacco di una linea a una cella: dal vincolo exitX/exitY, o dal perimetro verso «verso»."""
    x, y, w, h = box(celle, celle[cid])
    if fx is not None and fy is not None:
        return x + float(fx) * w, y + float(fy) * h
    cx, cy = x + w / 2, y + h / 2
    tx, ty = verso
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    f = forma(celle[cid])
    if f == "rombo":
        t = 1 / (abs(dx) / (w / 2) + abs(dy) / (h / 2))
    elif f == "cerchio":
        t = 1 / math.hypot(dx / (w / 2), dy / (h / 2))
    else:
        t = min((w / 2) / abs(dx) if dx else 1e9, (h / 2) / abs(dy) if dy else 1e9)
    return cx + dx * t, cy + dy * t


def percorso_linea(celle, c):
    ox, oy = origine(celle, c.parent)
    medi = [(ox + px, oy + py) for px, py in c.punti]

    def estremo(cid, pfisso, fx, fy, vicino):
        if cid and cid in celle:
            return punto_vincolo(celle, cid, fx, fy, vicino)
        if pfisso is not None:
            return ox + pfisso[0], oy + pfisso[1]
        raise ValueError("linea %s senza estremo" % c.id)

    def centro(cid, pfisso):
        if cid and cid in celle:
            x, y, w, h = box(celle, celle[cid])
            return x + w / 2, y + h / 2
        return (ox + pfisso[0], oy + pfisso[1]) if pfisso else (0, 0)

    verso_s = medi[0] if medi else centro(c.target, c.tp)
    verso_t = medi[-1] if medi else centro(c.source, c.sp)
    a = estremo(c.source, c.sp, c.st.get("exitX"), c.st.get("exitY"), verso_s)
    b = estremo(c.target, c.tp, c.st.get("entryX"), c.st.get("entryY"), verso_t)
    return [a] + medi + [b]


def punto_lungo(pts, frazione):
    lung = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(lung) or 1
    d = tot * frazione
    for i, l in enumerate(lung):
        if d <= l or i == len(lung) - 1:
            t = d / l if l else 0
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t)
        d -= l
    return pts[-1]


# ---------------------------------------------------------------- testo

def testo_semplice(v):
    v = re.sub(r"<br\s*/?>", "\n", v or "", flags=re.I)
    v = re.sub(r"</(div|p)>", "\n", v, flags=re.I)
    v = re.sub(r"<[^>]+>", "", v)
    return html.unescape(v).strip("\n")


def a_capo(testo, f, larghezza):
    righe = []
    for par in testo.split("\n"):
        parole, riga = par.split(" "), ""
        for p in parole:
            prova = (riga + " " + p).strip()
            if riga and f.getlength(prova) > larghezza:
                righe.append(riga)
                riga = p
            else:
                riga = prova
        righe.append(riga)
    return righe


def colore(v, predefinito):
    if not v or v == "none":
        return predefinito if v != "none" else None
    v = v.strip()
    if re.fullmatch(r"#[0-9a-fA-F]{6}", v):
        return v
    if re.fullmatch(r"#[0-9a-fA-F]{3}", v):
        return "#" + "".join(ch * 2 for ch in v[1:])
    return {"black": "#000000", "white": "#ffffff"}.get(v.lower(), predefinito)


# ---------------------------------------------------------------- disegno

def disegna(modello, scala=1.0, forza=False):
    celle = {}
    ordine = []
    for el in modello.iter("mxCell"):
        c = Cella(el)
        celle[c.id] = c
        ordine.append(c)
    # UserObject/object: draw.io avvolge la cella quando le si danno proprietà
    for obj in list(modello.iter("UserObject")) + list(modello.iter("object")):
        el = obj.find("mxCell")
        if el is not None:
            c = celle.get(el.get("id")) or Cella(el)
            c.id = obj.get("id")
            c.valore = obj.get("label") or ""
            celle[c.id] = c
            ordine.append(c)

    sconosciute = []
    elementi = []   # (tipo, dati) in coordinate assolute
    for c in ordine:
        if c.id in ("0", "1") and not c.vertex and not c.edge:
            continue
        if c.vertex and c.relativa and c.parent in celle and celle[c.parent].edge:
            elementi.append(("etichetta", c))
            continue
        if c.vertex:
            f = forma(c)
            if f is None:
                sconosciute.append("%s («%s», stile %s)" % (c.id, testo_semplice(c.valore)[:30], ";".join(c.st)[:60]))
            elif f != "gruppo":
                elementi.append((f, c))
        elif c.edge:
            frecce = [c.st.get(k) for k in ("startArrow", "endArrow")]
            if c.st.get("endArrow") is None or any(f not in (None, "none", "oval", "block") for f in frecce):
                # in draw.io una linea senza endArrow ha la freccia classica
                sconosciute.append("%s (linea con una freccia: in questa notazione le linee non hanno frecce)" % c.id)
            elementi.append(("linea", c))
    if sconosciute and not forza:
        raise SystemExit("ERRORE: forme che questo script non disegna (esporta il PNG da draw.io, "
                         "o usa --forza per saltarle):\n  " + "\n  ".join(sconosciute))

    # misura: bounding box di tutto, testi compresi
    s = SS * scala
    disegni = []   # funzioni (draw, trasf) da chiamare dopo aver fissato la tela
    xs, ys = [], []

    def ingombro(x0, y0, x1, y1):
        xs.extend([x0, x1])
        ys.extend([y0, y1])

    for tipo, c in elementi:
        if tipo in ("rettangolo", "rombo", "cerchio", "testo"):
            x, y, w, h = box(celle, c)
            ingombro(x, y, x + w, y + h)
            t = testo_semplice(c.valore)
            if t:
                fs = float(c.st.get("fontSize") or 12)
                f = font(fs)
                righe = a_capo(t, f, w - 6) if c.st.get("whiteSpace") == "wrap" and w > 10 else t.split("\n")
                lw = max(f.getlength(r) for r in righe)
                lh = fs * 1.2 * len(righe)
                al = c.st.get("align", "center")
                tx = x + (w - lw) / 2 if al == "center" else (x if al == "left" else x + w - lw)
                va = c.st.get("verticalAlign", "middle")
                ty = y + (h - lh) / 2 if va == "middle" else (y if va == "top" else y + h - lh)
                ingombro(tx, ty, tx + lw, ty + lh)
        elif tipo == "linea":
            pts = percorso_linea(celle, c)
            for px, py in pts:
                ingombro(px - 4, py - 4, px + 4, py + 4)
        elif tipo == "etichetta":
            linea = celle[c.parent]
            pts = percorso_linea(celle, linea)
            px, py = punto_lungo(pts, (c.x + 1) / 2)
            px += c.offset[0]
            py += c.offset[1]
            t = testo_semplice(c.valore)
            fs = float(c.st.get("fontSize") or 11)
            lw = font(fs).getlength(t)
            ingombro(px - lw / 2, py - fs, px + lw / 2, py + fs)
    if not xs:
        raise SystemExit("ERRORE: il diagramma è vuoto")
    margine = 10
    x0, y0 = min(xs) - margine, min(ys) - margine
    W = int(math.ceil((max(xs) + margine - x0) * s))
    H = int(math.ceil((max(ys) + margine - y0) * s))
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    T = lambda px, py: ((px - x0) * s, (py - y0) * s)
    spess = lambda c: max(1, int(round(float(c.st.get("strokeWidth") or 1) * s)))

    def scrivi(c, x, y, w, h, testo):
        if not testo:
            return
        fs = float(c.st.get("fontSize") or 12)
        f = font(fs * s, c.st.get("fontStyle") == "1")
        col = colore(c.st.get("fontColor"), "#000000")
        fm = font(fs)
        righe = a_capo(testo, fm, w - 6) if c.st.get("whiteSpace") == "wrap" and w > 10 else testo.split("\n")
        lh = fs * 1.2
        al = c.st.get("align", "center")
        va = c.st.get("verticalAlign", "middle")
        tot = lh * len(righe)
        ty = y + (h - tot) / 2 if va == "middle" else (y if va == "top" else y + h - tot)
        for i, r in enumerate(righe):
            lw = fm.getlength(r)
            tx = x + (w - lw) / 2 if al == "center" else (x + 2 if al == "left" else x + w - lw - 2)
            cx, cy = T(tx, ty + lh * i + lh / 2)
            d.text((cx, cy), r, font=f, fill=col, anchor="lm")

    # prima le linee, poi le forme (che coprono gli estremi), poi le etichette: come in draw.io
    # quando le linee stanno prima nel file; l'ordine del file resta dentro ogni gruppo
    for tipo, c in elementi:
        if tipo != "linea":
            continue
        pts = [T(*p) for p in percorso_linea(celle, c)]
        col = colore(c.st.get("strokeColor"), "#000000")
        d.line(pts, fill=col, width=spess(c), joint="curve")
        for estremo, prima, chiave in ((pts[-1], pts[-2], "endArrow"), (pts[0], pts[1], "startArrow")):
            if c.st.get(chiave) == "block":
                # freccia piena (gerarchie ISA): triangolo con la punta sull'estremo
                lung = float(c.st.get("endSize" if chiave == "endArrow" else "startSize") or 6) * s
                dx, dy = estremo[0] - prima[0], estremo[1] - prima[1]
                l = math.hypot(dx, dy) or 1
                ux, uy = dx / l, dy / l
                bx, by = estremo[0] - ux * lung, estremo[1] - uy * lung
                mezza = lung * 0.45
                d.polygon([estremo, (bx - uy * mezza, by + ux * mezza), (bx + uy * mezza, by - ux * mezza)],
                          fill=col, outline=col)
            if c.st.get(chiave) == "oval":
                r = float(c.st.get("endSize" if chiave == "endArrow" else "startSize") or 6) / 2 * s
                piena = c.st.get("endFill" if chiave == "endArrow" else "startFill", "1") != "0"
                d.ellipse([estremo[0] - r, estremo[1] - r, estremo[0] + r, estremo[1] + r],
                          fill=col if piena else "white", outline=col, width=spess(c))
    for tipo, c in elementi:
        if tipo not in ("rettangolo", "rombo", "cerchio", "testo"):
            continue
        x, y, w, h = box(celle, c)
        a, b = T(x, y)
        a2, b2 = T(x + w, y + h)
        riemp = colore(c.st.get("fillColor"), "#ffffff")
        bordo = colore(c.st.get("strokeColor"), "#000000")
        if tipo == "rettangolo":
            d.rectangle([a, b, a2, b2], fill=riemp, outline=bordo, width=spess(c))
        elif tipo == "rombo":
            d.polygon([((a + a2) / 2, b), (a2, (b + b2) / 2), ((a + a2) / 2, b2), (a, (b + b2) / 2)],
                      fill=riemp, outline=bordo, width=spess(c))
        elif tipo == "cerchio":
            d.ellipse([a, b, a2, b2], fill=riemp, outline=bordo, width=spess(c))
        scrivi(c, x, y, w, h, testo_semplice(c.valore))
    for tipo, c in elementi:
        if tipo != "etichetta":
            continue
        pts = percorso_linea(celle, celle[c.parent])
        px, py = punto_lungo(pts, (c.x + 1) / 2)
        px += c.offset[0]
        py += c.offset[1]
        t = testo_semplice(c.valore)
        fs = float(c.st.get("fontSize") or 11)
        f = font(fs * s)
        d.text(T(px, py), t, font=f, fill=colore(c.st.get("fontColor"), "#000000"), anchor="mm")
    return img.resize((max(1, round(W / SS)), max(1, round(H / SS))), Image.LANCZOS)


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        raise SystemExit(__doc__)
    opz = dict(x[2:].split("=", 1) if "=" in x else (x[2:], "1") for x in sys.argv[1:] if x.startswith("--"))
    src = a[0]
    out = a[1] if len(a) > 1 else os.path.splitext(src)[0] + ".png"
    img = disegna(leggi_modello(src, int(opz.get("pagina", 1))), float(opz.get("scala", 1.25)), "forza" in opz)
    img.save(out)
    print("OK: %s (%dx%d)" % (out, img.width, img.height))


if __name__ == "__main__":
    main()
