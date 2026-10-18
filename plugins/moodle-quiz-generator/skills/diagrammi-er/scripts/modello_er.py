#!/usr/bin/env python3
"""Lettura della descrizione di un modello E/R (file .er), comune a tutti i moduli della skill.

    from modello_er import leggi
    modello = leggi(open("hotel.er", encoding="utf-8").read())

Il formato completo è in references/descrizione.md. Ogni modulo usa solo le parti che gli servono:
il diagramma le posizioni e i lati degli attributi, lo schema relazionale chiavi e cardinalità (più
plurali e nomi delle chiavi esterne, se dati), la documentazione descrizioni, sinonimi e tipi.
"""
import re

LATI = ("sopra", "sotto", "sinistra", "destra")
COLORI_NOMI = ("azzurro", "rosa", "verde", "giallo", "arancio", "bianco")
STRATEGIE = {"tutto su": "su", "tutto giu": "giu", "tutto giù": "giu", "lasciare tutto": "tutto",
             "tenere tutto": "tutto"}


class Errore(Exception):
    pass


def cardinalita(testo):
    """«(1,N)» -> ("1", "N")."""
    t = testo.strip().strip("()").replace(" ", "")
    m = re.fullmatch(r"([01])\s*,\s*([1nNmM])", t)
    if not m:
        raise Errore("cardinalità «%s»: si scrive (min,max) con min 0 o 1 e max 1 o N" % testo)
    mx = m.group(2).upper()
    return m.group(1), ("N" if mx in ("N", "M") else "1")


def lista(v):
    return [a.strip() for a in v.split(",") if a.strip()]


def lista_attributi(v):
    """«*Cod, Nome, Email (0,1)» -> ["*Cod", "Nome", "Email"], {"Email"}: le virgole dentro le parentesi
    non separano; (0,1) dopo il nome è l'attributo opzionale, con la cardinalità nel diagramma."""
    pezzi, cur, liv = [], "", 0
    for ch in v:
        if ch == "(":
            liv += 1
        elif ch == ")":
            liv -= 1
        if ch == "," and liv == 0:
            pezzi.append(cur)
            cur = ""
        else:
            cur += ch
    pezzi.append(cur)
    nomi, opzionali = [], set()
    for p in (x.strip() for x in pezzi):
        if not p:
            continue
        m = re.fullmatch(r"(.+?)\s*\(([^)]*)\)", p)
        if m:
            card = m.group(2).replace(" ", "").upper()
            nome = m.group(1).strip()
            if card != "0,1":
                raise Errore("attributo «%s (%s)»: la cardinalità di un attributo si scrive solo per quello "
                             "opzionale, (0,1); un attributo con più valori diventa un'entità a parte "
                             "(prima forma normale)" % (nome, m.group(2)))
            if nome.startswith("*"):
                raise Errore("«%s»: un attributo della chiave primaria non può essere opzionale" % nome.lstrip("*"))
            opzionali.add(nome)
            p = nome
        nomi.append(p)
    return nomi, opzionali


def nuova_entita(nome, pos):
    return {"tipo": "entita", "nome": nome, "pos": pos, "attr": {}, "ordine": [], "deboli": [],
            "descrizione": "", "sinonimi": "", "plurale": "", "tipi": {}, "opzionali": set()}


def leggi(testo):
    m_ = {"titolo": "Diagramma E/R", "colori": {"entita": "azzurro", "associazioni": "bianco"},
          "griglia": (250, 170), "entita": {}, "associazioni": [], "gerarchie": [],
          "ipotesi": [], "vincoli": [], "traccia": []}
    corrente = None
    for n, riga in enumerate(testo.splitlines(), 1):
        if not riga.strip() or riga.strip().startswith("#"):
            continue
        rientrata = riga[:1] in (" ", "\t")
        r = riga.strip()
        try:
            if not rientrata:
                corrente = None
                m = re.match(r"traccia\s*:\s*(.*)$", r, re.I)
                if m:
                    # la traccia: sulla stessa riga o sulle righe rientrate sotto (una riga per paragrafo)
                    if m.group(1).strip():
                        m_["traccia"].append(m.group(1).strip())
                    corrente = {"tipo": "traccia"}
                    continue
                m = re.match(r"(titolo|colori|griglia|ipotesi|vincolo)\s*:\s*(.*)$", r, re.I)
                if m:
                    k, v = m.group(1).lower(), m.group(2).strip()
                    if k == "titolo":
                        m_["titolo"] = v
                    elif k == "ipotesi":
                        m_["ipotesi"].append(v)
                    elif k == "vincolo":
                        m_["vincoli"].append(v)
                    elif k == "griglia":
                        a, b = v.split()
                        m_["griglia"] = (float(a), float(b))
                    else:
                        for parte in v.replace(",", " ").split():
                            kk, vv = parte.split("=")
                            kk = {"entità": "entita"}.get(kk.lower(), kk.lower())
                            if kk not in ("entita", "associazioni") or vv.lower() not in COLORI_NOMI:
                                raise Errore("colori: si scrive entita=… associazioni=… con %s" % ", ".join(COLORI_NOMI))
                            m_["colori"][kk] = vv.lower()
                    continue
                m = re.match(r"entit[aà]\s+(.+?)\s*(?:@\s*(-?[\d.]+)\s+(-?[\d.]+))?\s*$", r, re.I)
                if m:
                    nome = m.group(1).strip().strip('"')
                    if nome in m_["entita"]:
                        raise Errore("entità «%s» scritta due volte" % nome)
                    pos = (float(m.group(2)), float(m.group(3))) if m.group(2) else None
                    corrente = nuova_entita(nome, pos)
                    m_["entita"][nome] = corrente
                    continue
                m = re.match(r"associazione\s+(.+?)\s*:\s*(.+?)\s*(\([^)]*\))\s*--\s*(.+?)\s*(\([^)]*\))"
                             r"\s*(?:@\s*(.+))?$", r, re.I)
                if m:
                    corrente = {"tipo": "associazione", "nome": m.group(1).strip().strip('"'),
                                "e1": m.group(2).strip().strip('"'), "c1": cardinalita(m.group(3)),
                                "e2": m.group(4).strip().strip('"'), "c2": cardinalita(m.group(5)),
                                "pos": (m.group(6) or "").strip(), "attr": {}, "ordine": [],
                                "descrizione": "", "tipi": {}, "opzionali": set(), "fk": "", "fks": [], "tabella": "", "fk_in": ""}
                    m_["associazioni"].append(corrente)
                    continue
                m = re.match(r"gerarchia\s+(.+?)\s*:\s*(.+?)\s*\(\s*(n?t)\s*,\s*(n?e)\s*\)\s*$", r, re.I)
                if m:
                    corrente = {"tipo": "gerarchia", "gen": m.group(1).strip().strip('"'),
                                "spec": lista(m.group(2)), "copertura": m.group(3).lower(),
                                "esclusivita": m.group(4).lower(), "traduzione": "", "campo_tipo": ""}
                    m_["gerarchie"].append(corrente)
                    continue
                if re.match(r"gerarchia\b", r, re.I):
                    raise Errore("gerarchia: si scrive «gerarchia GENERALE: SPEC1, SPEC2 (t,e)» con (t,e), "
                                 "(t,ne), (nt,e) o (nt,ne)")
                raise Errore("riga non riconosciuta")
            if corrente is None:
                raise Errore("riga rientrata fuori da un'entità, un'associazione, una gerarchia o la traccia")
            tipo = corrente["tipo"]
            if tipo == "traccia":
                m_["traccia"].append(r)
                continue
            m = re.match(r"(sopra|sotto|sinistra|destra|attributi)\s*:\s*(.*)$", r, re.I)
            if m and tipo in ("entita", "associazione"):
                lato = m.group(1).lower()
                if lato == "attributi":
                    lato = "sotto"
                nomi, opz = lista_attributi(m.group(2))
                corrente["opzionali"] |= opz
                corrente["attr"].setdefault(lato, []).extend(nomi)
                corrente["ordine"].extend((a.lstrip("*"), a.startswith("*")) for a in nomi)
                continue
            m = re.match(r"tipo\s+(.+?)\s*:\s*(.*)$", r, re.I)
            if m and tipo in ("entita", "associazione"):
                parti = m.group(2).split(";", 1)
                corrente["tipi"][m.group(1).strip()] = (parti[0].strip(), parti[1].strip() if len(parti) > 1 else "")
                continue
            m = re.match(r"(descrizione|sinonimi|plurale|identificata da|chiave esterna in|chiave esterna|"
                         r"chiavi esterne|tabella|traduzione|campo tipo)\s*:\s*(.*)$", r, re.I)
            if m:
                k, v = m.group(1).lower(), m.group(2).strip()
                ammessi = {"entita": ("descrizione", "sinonimi", "plurale", "identificata da"),
                           "associazione": ("descrizione", "chiave esterna", "chiavi esterne", "tabella",
                                            "chiave esterna in"),
                           "gerarchia": ("traduzione", "campo tipo")}[tipo]
                if k not in ammessi:
                    raise Errore("«%s» non si usa in %s" % (k, {"entita": "un'entità", "associazione":
                                                               "un'associazione", "gerarchia": "una gerarchia"}[tipo]))
                if k == "identificata da":
                    corrente["deboli"] = lista(v)
                elif k == "chiavi esterne":
                    corrente["fks"] = lista(v)
                elif k == "chiave esterna":
                    corrente["fk"] = v
                elif k == "chiave esterna in":
                    corrente["fk_in"] = v
                elif k == "traduzione":
                    if v.lower() not in STRATEGIE:
                        raise Errore("traduzione: tutto su, tutto giù o lasciare tutto")
                    corrente["traduzione"] = STRATEGIE[v.lower()]
                elif k == "campo tipo":
                    corrente["campo_tipo"] = v
                else:
                    corrente[k] = v
                continue
            raise Errore("riga non riconosciuta")
        except Errore as e:
            raise SystemExit("ERRORE riga %d: %s\n    %s" % (n, e, riga))
        except ValueError:
            raise SystemExit("ERRORE riga %d: valori non validi\n    %s" % (n, riga))
    controlla(m_)
    return m_


def specializzazioni(m):
    return {s for g in m["gerarchie"] for s in g["spec"]}


def controlla(m):
    nomi = m["entita"]
    for a in m["associazioni"]:
        for e in (a["e1"], a["e2"]):
            if e not in nomi:
                raise SystemExit("ERRORE: l'associazione «%s» cita l'entità «%s», che non c'è" % (a["nome"], e))
        if a["fk_in"] and a["fk_in"] not in (a["e1"], a["e2"]):
            raise SystemExit("ERRORE: «%s»: «chiave esterna in» deve essere una delle due entità" % a["nome"])
    for g in m["gerarchie"]:
        for e in [g["gen"]] + g["spec"]:
            if e not in nomi:
                raise SystemExit("ERRORE: la gerarchia di «%s» cita l'entità «%s», che non c'è" % (g["gen"], e))
        if not g["spec"]:
            raise SystemExit("ERRORE: la gerarchia di «%s» non ha specializzazioni" % g["gen"])
    spec = specializzazioni(m)
    for nome, e in nomi.items():
        for a in e["deboli"]:
            if not any(x["nome"] == a and nome in (x["e1"], x["e2"]) for x in m["associazioni"]):
                raise SystemExit("ERRORE: «%s» è identificata da «%s», che non è un'associazione collegata a «%s»"
                                 % (nome, a, nome))
        if nome in spec and any(k for _, k in e["ordine"]):
            raise SystemExit("ERRORE: «%s» è una specializzazione: eredita la chiave della generalizzazione, "
                             "non ne ha una sua (togli *)" % nome)


def chiave(e):
    return [a for a, k in e["ordine"] if k]


def etichetta_gerarchia(g):
    return "(%s,%s)" % (g["copertura"], g["esclusivita"])


def descr_classificazione(g):
    return "%s, %s" % ("totale" if g["copertura"] == "t" else "non totale",
                       "esclusiva" if g["esclusivita"] == "e" else "non esclusiva")
