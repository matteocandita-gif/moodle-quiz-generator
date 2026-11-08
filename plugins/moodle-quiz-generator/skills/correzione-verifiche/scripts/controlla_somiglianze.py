#!/usr/bin/env python3
"""Controllo delle somiglianze: trova i candidati e prepara il documento per la dashboard.

Il codice corretto si assomiglia per forza: lo script non cerca codice simile, ma gli stessi errori
rari e le stesse stranezze. Trova solo i CANDIDATI: chi decide che cosa segnalare è Claude, leggendo
le risposte con le regole di references/somiglianze.md. Lavora sulle sole sigle.

1. Cercare i candidati:
    python3 controlla_somiglianze.py CARTELLA --uscita=candidati.json
            [--dashboard=CARTELLA_QUIZ --quiz=ID] [--salta=D03,D04]

2. Preparare il documento dalle voci confermate da Claude:
    python3 controlla_somiglianze.py CARTELLA --esito=esito.json --uscita=documento.json

CARTELLA     l'esportazione della verifica (ArtifactData list con out_dir di «verifiche/ID/domande»,
             «verifiche/ID/valutazioni» e «verifiche/ID/somiglianze»), con i punteggi già caricati.
--dashboard  l'esportazione della dashboard dei quiz (come per esegui_risposte.py): le soluzioni
             dell'autore non contano come errori condivisi.
--salta      domande da non confrontare (le chiuse: una risposta uguale non dimostra nulla).
--esito      l'elenco JSON delle voci confermate; [] se non c'è nulla da segnalare.

Il documento va scritto con un `set` in «verifiche/ID/somiglianze/segnalazioni»: conserva le decisioni
già prese dall'utente («Da approfondire», «Scartata»), che non si riscrivono mai.
"""
import collections
import datetime
import difflib
import glob
import itertools
import json
import math
import os
import re
import statistics
import sys

N_FRAMMENTO = 6            # token consecutivi che formano un frammento
MIN_FRAMMENTI = 3          # sotto questa soglia il frammento in comune è un caso
FRAMMENTI_FORTI = 18       # con tanti frammenti basta una domanda sola
MAX_GRUPPO = 3             # un frammento in più di tre studenti è un errore diffuso, non un indizio
MIN_MESSAGGI = 3           # messaggi uguali non dettati dalla traccia, su almeno due domande
MIN_REFUSI = 2             # un refuso solo può capitare, soprattutto se è un errore comune
MIN_TOKEN_UGUALI = 30      # lunghezza minima per il confronto tra risposte intere
QUASI_UGUALI = 0.75
SCARTO_ALTO = 0.5          # risposta molto migliore del resto della verifica
FRAZIONE_ALTA = 0.8
MIN_ALTRE = 4              # domande valutate necessarie per stimare il resto della verifica

TOKEN = re.compile(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|`[^`]*`|[^\W\d]\w*|\d+(?:[.,]\d+)?|\S')
COMMENTO = re.compile(r'//[^\n]*|/\*.*?\*/', re.S)
PAROLA = re.compile(r"[^\W\d_]{5,}")


def leggi(p):
    d = json.load(open(p, encoding="utf-8"))
    return d.get("data", d)          # out_dir di ArtifactData può avvolgere il corpo


def documenti(base, nome):
    return {os.path.basename(f)[:-5]: leggi(f)
            for f in glob.glob(os.path.join(base, "**", nome, "*.json"), recursive=True)}


def carica(base, salta=()):
    domande = documenti(base, "domande")
    val = documenti(base, "valutazioni")
    if not domande or not val:
        sys.exit("Nella cartella non ci sono domande e valutazioni: esporta la verifica dalla dashboard.")
    return {d: {"max": float(q.get("max") or 0), "n": int(q.get("n") or 0), "testi": q.get("testi") or [],
                "righe": val.get(d, {}).get("righe", {})}
            for d, q in domande.items() if d not in salta and not (q.get("note") or q.get("tipo") == "note")}


def parole_traccia(testo):
    return {t.lower() for t in TOKEN.findall(testo or "") if t[0].isalpha()}


def tokenizza(testo):
    """(forma per il confronto, testo originale): le stringhe restano fuori dallo scheletro del codice."""
    uscita = []
    for t in TOKEN.findall(COMMENTO.sub(" ", testo)):
        uscita.append(('"…"' if t[0] in "\"'`" and len(t) > 1 else t.lower(), t))
    return uscita


def messaggi(testo):
    """Le stringhe e i commenti: li scrive lo studente, se la traccia non li detta."""
    uscita = [c.strip(" /*\n\t") for c in COMMENTO.findall(testo)]
    uscita += [t[1:-1] for t in TOKEN.findall(COMMENTO.sub(" ", testo)) if t[0] in "\"'`" and len(t) > 2]
    return {m.strip() for m in uscita if len(m.strip()) >= 8}


def soluzioni(cartella, quiz):
    """I testi delle soluzioni dell'autore, tutte insieme: il codice corretto non è un errore condiviso."""
    uscita = []
    for f in glob.glob(os.path.join(cartella, "quiz", quiz, "domande", "*.json")):
        codice = leggi(f).get("coderunner") or ""
        m = re.search(r"^=== answer\n(.*?)(?=^=== |\Z)", codice, re.S | re.M)
        if m:
            uscita.append(m.group(1))
    return uscita


def frazione(riga, massimo):
    try:
        return float(riga.get("punti")) / massimo if massimo else None
    except (TypeError, ValueError):
        return None


def valide(q):
    return {k: r for k, r in q["righe"].items()
            if not r.get("esclusa") and len(str(r.get("risposta") or "").strip()) >= 20}


def normalizza_varianti(q, r, tokens):
    """I nomi della propria variante diventano segnaposto: così due varianti si possono confrontare."""
    if len(q["testi"]) < 2 or r.get("variante") in (None, ""):
        return [t[0] for t in tokens]
    try:
        propri = parole_traccia(q["testi"][int(r["variante"])])
    except (IndexError, ValueError):
        return [t[0] for t in tokens]
    altri = set().union(*[parole_traccia(t) for i, t in enumerate(q["testi"]) if i != int(r["variante"])])
    specifici = propri - altri
    return ["§" if t[0] in specifici else t[0] for t in tokens]


def frammenti_di(chiave):
    return {tuple(chiave[i:i + N_FRAMMENTO]) for i in range(max(0, len(chiave) - N_FRAMMENTO + 1))}


def tratti(tok, chiave, comuni, quanti=3):
    """I tratti più lunghi del testo originale coperti dai frammenti in comune."""
    coperti = [False] * len(tok)
    for i in range(max(0, len(chiave) - N_FRAMMENTO + 1)):
        if tuple(chiave[i:i + N_FRAMMENTO]) in comuni:
            coperti[i:i + N_FRAMMENTO] = [True] * N_FRAMMENTO
    uscita, att = [], []
    for c, t in zip(coperti + [False], tok + [("", "")]):
        if c:
            att.append(t[1])
        elif att:
            uscita.append(" ".join(att))
            att = []
    return sorted(uscita, key=len, reverse=True)[:quanti]


def errori_condivisi(dati, testi_buoni):
    """Coppie che condividono frammenti rari, assenti da tracce, soluzioni e risposte a punteggio pieno."""
    buoni_autore = set()
    for t in testi_buoni:
        buoni_autore |= frammenti_di([x[0] for x in tokenizza(t)])
    coppie = collections.defaultdict(dict)
    uguali = []
    for d, q in dati.items():
        righe = valide(q)
        tok = {k: tokenizza(str(r["risposta"])) for k, r in righe.items()}
        chiavi = {k: normalizza_varianti(q, righe[k], tok[k]) for k in righe}
        fr = {k: frammenti_di(chiavi[k]) for k in righe}
        dettati = set(buoni_autore)
        for t in q["testi"]:
            dettati |= frammenti_di([x[0] for x in tokenizza(t)])
        pieni = {k for k, r in righe.items() if (frazione(r, q["max"]) or 0) >= 1}
        for k in pieni:
            dettati |= fr[k]
        df = collections.Counter(g for v in fr.values() for g in v)
        for a, b in itertools.combinations(sorted(righe), 2):
            comuni = {g for g in fr[a] & fr[b] if g not in dettati and df[g] <= MAX_GRUPPO}
            if len(comuni) >= MIN_FRAMMENTI:
                coppie[(a, b)][d] = {"quanti": len(comuni), "punti": {a: righe[a].get("punti"), b: righe[b].get("punti")},
                                     "frammenti": {a: tratti(tok[a], chiavi[a], comuni), b: tratti(tok[b], chiavi[b], comuni)},
                                     "risposte": {a: righe[a]["risposta"], b: righe[b]["risposta"]}}
            # risposte intere quasi uguali, anche corrette: nomi e forma sono dello studente
            lung = min(len(chiavi[a]), len(chiavi[b]))
            if lung >= MIN_TOKEN_UGUALI:
                propri = fr[a] | fr[b]
                sim = len((fr[a] & fr[b]) - dettati) / max(1, len(propri - dettati))
                if sim >= QUASI_UGUALI:
                    uguali.append({"studenti": [a, b], "domanda": d, "somiglianza": round(sim, 2),
                                   "risposte": {a: righe[a]["risposta"], b: righe[b]["risposta"]}})
    return coppie, uguali


def messaggi_condivisi(dati):
    per_coppia = collections.defaultdict(lambda: collections.defaultdict(set))
    for d, q in dati.items():
        traccia = " ".join(q["testi"]).lower()
        uso = collections.defaultdict(set)
        for k, r in valide(q).items():
            for m in messaggi(str(r["risposta"])):
                if m.lower() not in traccia:
                    uso[m.lower()].add(k)
        for m, ks in uso.items():
            if 2 <= len(ks) <= MAX_GRUPPO:
                for a, b in itertools.combinations(sorted(ks), 2):
                    per_coppia[(a, b)][d].add(m)
    return {c: {d: sorted(v) for d, v in dd.items()} for c, dd in per_coppia.items()
            if len(dd) >= 2 and sum(len(v) for v in dd.values()) >= MIN_MESSAGGI}


def e_refuso(w, giusta):
    """Il refuso sta dentro la parola; se cambia solo la fine è un'altra forma («diverso», «diverse»)."""
    if w in giusta or giusta in w:
        return False
    return len(os.path.commonprefix([w, giusta])) < min(len(w), len(giusta)) - 3


def refusi_condivisi(dati):
    """Parole rare, quasi uguali a una parola comune, scritte allo stesso modo da pochi studenti."""
    uso, tracce = collections.defaultdict(set), set()
    for q in dati.values():
        for t in q["testi"]:
            tracce |= {w.lower() for w in PAROLA.findall(t)}
        for k, r in valide(q).items():
            for w in PAROLA.findall(COMMENTO.sub(" ", str(r["risposta"]))):
                uso[w.lower()].add(k)
    comuni = [w for w, ks in uso.items() if len(ks) >= 5] + sorted(tracce)
    uscita = collections.defaultdict(list)
    for w, ks in uso.items():
        if 2 <= len(ks) <= MAX_GRUPPO and w not in tracce:
            simili = [c for c in difflib.get_close_matches(w, comuni, n=5, cutoff=0.8) if c != w]
            giusta = next((c for c in simili if e_refuso(w, c)), None)
            if giusta and not any(c.startswith(w[:-2]) for c in simili):
                for a, b in itertools.combinations(sorted(ks), 2):
                    uscita[(a, b)].append(f"{w} (per {giusta})")
    return uscita


def residui_variante(dati):
    """Nomi tipici di un'altra variante nella risposta di chi non l'aveva: la sua traccia non li suggerisce."""
    uscita = []
    for d, q in dati.items():
        if len(q["testi"]) < 2:
            continue
        righe = {k: r for k, r in valide(q).items() if r.get("variante") not in (None, "")}
        parole = {k: {t[0] for t in tokenizza(str(r["risposta"])) if t[0][0].isalpha() and len(t[0]) >= 4}
                  for k, r in righe.items()}
        gruppi = collections.defaultdict(list)
        for k, r in righe.items():
            gruppi[int(r["variante"])].append(k)
        tracce = [parole_traccia(t) for t in q["testi"]]
        tipici = {}
        for v, ks in gruppi.items():
            if v >= len(tracce):
                continue
            uso = collections.Counter(w for k in ks for w in parole[k])
            tipici[v] = {w for w, n in uso.items() if w in tracce[v] and n / len(ks) >= 0.3}
        for k, r in righe.items():
            v = int(r["variante"])
            if v >= len(tracce):
                continue
            compagni = collections.Counter(w for c in gruppi[v] for w in parole[c])
            for u, tip in tipici.items():
                if u == v:
                    continue
                strani = sorted(w for w in (parole[k] & tip) - tracce[v] if compagni[w] <= 2)
                if strani:
                    uscita.append({"studente": k, "domanda": d, "sua_variante": v, "altra_variante": u,
                                   "nomi": strani, "risposta": r["risposta"]})
    return uscita


def stile(testo):
    righe = [x.strip() for x in testo.splitlines() if x.strip()]
    if not righe:
        return {}
    istr = [x for x in righe if not x.endswith(("{", "}"))]
    return {"punto_e_virgola": round(sum(x.endswith(";") for x in istr) / max(1, len(istr)), 2),
            "spazi_attorno_a_=": round(len(re.findall(r"\s=\s", testo)) / max(1, len(re.findall(r"=", testo))), 2),
            "commenti": len(COMMENTO.findall(testo))}


def fuori_linea(dati):
    """Risposte molto migliori di ciò che ci si aspetta da quello studente, a parità di difficoltà."""
    fr = collections.defaultdict(dict)
    for d, q in dati.items():
        for k, r in q["righe"].items():
            f = frazione(r, q["max"])
            if not r.get("esclusa") and f is not None:
                fr[k][d] = f
    media = {d: statistics.mean(fr[k][d] for k in fr if d in fr[k]) for d in dati if any(d in fr[k] for k in fr)}
    generale = statistics.mean(media.values())
    uscita = []
    for k, v in fr.items():
        if len(v) <= MIN_ALTRE:
            continue
        for d, f in v.items():
            altre = {u: w for u, w in v.items() if u != d}
            capacita = statistics.mean(w - (media[u] - generale) for u, w in altre.items())
            attesa = min(1, max(0, capacita + media[d] - generale))
            if f < FRAZIONE_ALTA or f - attesa < SCARTO_ALTO:
                continue
            testo = str(dati[d]["righe"][k].get("risposta") or "")
            if len(testo.strip()) < 20:
                continue
            altrove = set()
            for u in altre:
                altrove |= {t[0] for t in tokenizza(str(dati[u]["righe"][k].get("risposta") or ""))}
            classe = collections.Counter(t for r in valide(dati[d]).values()
                                         for t in {x[0] for x in tokenizza(str(r["risposta"]))})
            nuovi = sorted(t for t in {x[0] for x in tokenizza(testo)} - altrove
                           if t[0].isalpha() and classe[t] <= 2 and t not in " ".join(dati[d]["testi"]).lower())
            deboli = {u: {"punti": dati[u]["righe"][k].get("punti"), "max": dati[u]["max"],
                          "commento": dati[u]["righe"][k].get("commento"), "risposta": dati[u]["righe"][k].get("risposta")}
                      for u, w in sorted(altre.items()) if w < 0.6}
            stili = [stile(str(dati[u]["righe"][k].get("risposta") or "")) for u in altre]
            uscita.append({"studente": k, "domanda": d, "frazione": round(f, 2), "attesa": round(attesa, 2),
                           "scarto": round(f - attesa, 2), "media_altrove": round(statistics.mean(altre.values()), 2),
                           "risposta": testo, "nuovi_rispetto_al_resto": nuovi, "stile_qui": stile(testo),
                           "stile_altrove": [s for s in stili if s], "altre_deboli": deboli})
    return sorted(uscita, key=lambda x: -x["scarto"])


def cerca(base, opz):
    dati = carica(base, set(filter(None, opz.get("salta", "").split(","))))
    testi = soluzioni(opz["dashboard"], opz["quiz"]) if opz.get("dashboard") and opz.get("quiz") else []
    coppie, uguali = errori_condivisi(dati, testi)
    msg, ref = messaggi_condivisi(dati), refusi_condivisi(dati)
    simili = []
    for c in set(coppie) | set(msg) | set(ref):
        dd = coppie.get(c, {})
        qui = sum(x["quanti"] for x in dd.values())
        passa = len(dd) >= 2 or any(x["quanti"] >= FRAMMENTI_FORTI for x in dd.values()) or c in msg \
            or len(ref.get(c, [])) >= MIN_REFUSI
        if passa:
            simili.append({"studenti": list(c), "frammenti_rari": qui, "domande": dd, "messaggi_uguali": msg.get(c, {}),
                           "refusi_uguali": ref.get(c, [])})
    simili.sort(key=lambda x: -(x["frammenti_rari"] + 5 * len(x["refusi_uguali"]) + sum(len(v) for v in x["messaggi_uguali"].values())))
    return {"risposte_confrontate": sum(len(valide(q)) for q in dati.values()), "simili": simili,
            "quasi_uguali": uguali, "residui_variante": residui_variante(dati), "fuori_linea": fuori_linea(dati)}


def documento(base, esito):
    dati = carica(base)
    sigle = {k for q in dati.values() for k in q["righe"]}
    prima = documenti(base, "somiglianze").get("segnalazioni", {}).get("voci", {})
    voci = {i: v for i, v in prima.items() if v.get("decisione")}      # le decisioni dell'utente restano
    for v in esito:
        if v.get("tipo") not in ("simili", "fuori-linea"):
            sys.exit(f"Tipo sconosciuto: {v.get('tipo')}")
        ignoti = [k for k in v["studenti"] if k not in sigle] + [d for d in v["domande"] + v.get("confronto", []) if d not in dati]
        if ignoti:
            sys.exit(f"Studenti o domande inesistenti: {ignoti}")
        if not (v.get("motivo") or "").strip() or re.search(r"\bcopi", v["motivo"], re.I):
            sys.exit(f"Il motivo descrive che cosa si vede, senza parlare di copiature: {v.get('motivo')!r}")
        chi = sorted(v["studenti"])
        i = re.sub(r"[^\w-]", "_", ("simili-" + "-".join(chi)) if v["tipo"] == "simili" else f"fuori-{chi[0]}-{v['domande'][0]}")
        voci[i] = {**v, "studenti": chi, "decisione": voci.get(i, {}).get("decisione", "")}
    return {"aggiornato": datetime.date.today().isoformat(),
            "confrontate": sum(len(valide(q)) for q in dati.values()), "voci": voci}


def riassunto(c):
    print(f"Risposte confrontate: {c['risposte_confrontate']}")
    print(f"Coppie candidate: {len(c['simili'])}; risposte quasi uguali: {len(c['quasi_uguali'])}; "
          f"nomi di altre varianti: {len(c['residui_variante'])}; risposte fuori linea: {len(c['fuori_linea'])}")
    for s in c["simili"][:15]:
        print(f"  {' ~ '.join(s['studenti'])}: {s['frammenti_rari']} frammenti in {sorted(s['domande'])}, "
              f"messaggi {sum(len(v) for v in s['messaggi_uguali'].values())}, refusi {s['refusi_uguali'][:3]}")
    for s in c["quasi_uguali"][:10]:
        print(f"  quasi uguali {' ~ '.join(s['studenti'])} in {s['domanda']}: {s['somiglianza']}")
    for s in c["residui_variante"][:10]:
        print(f"  {s['studente']} in {s['domanda']} (variante {s['sua_variante']}): {s['nomi']} dalla variante {s['altra_variante']}")
    for s in c["fuori_linea"]:
        print(f"  {s['studente']} in {s['domanda']}: {s['frazione']} contro {s['attesa']} attesi, "
              f"{len(s['altre_deboli'])} risposte deboli altrove, nuovi {s['nuovi_rispetto_al_resto'][:6]}")


def main():
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    opz = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    if len(arg) != 1 or "uscita" not in opz:
        sys.exit(__doc__)
    if "esito" in opz:
        doc = documento(arg[0], json.load(open(opz["esito"], encoding="utf-8")))
        print(f"{len(doc['voci'])} voci, {doc['confrontate']} risposte confrontate")
    else:
        doc = cerca(arg[0], opz)
        riassunto(doc)
    json.dump(doc, open(opz["uscita"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
