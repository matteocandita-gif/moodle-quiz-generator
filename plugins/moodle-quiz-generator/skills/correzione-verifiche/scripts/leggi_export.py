#!/usr/bin/env python3
"""Legge l'export «Risposte» di un quiz Moodle (xlsx, csv o ods) e lo abbina alle righe della dashboard.

Uso:
    python3 leggi_export.py EXPORT.xlsx USCITA [--dashboard=CARTELLA --quiz=ID] [--mappa=3=r08,4=r11]
    python3 leggi_export.py VERIFICA/   USCITA [--dashboard=CARTELLA --quiz=ID] [--mappa=…]

EXPORT    il file scaricato da Moodle (Risultati → Risposte), già anonimizzato dall'utente:
          nelle colonne Cognome e Nome ci sono solo le iniziali.
VERIFICA/ in alternativa, una verifica creata con «Nuova correzione» nella dashboard delle correzioni:
          la cartella dell'esportazione (ArtifactData list con out_dir di verifiche/ID/domande e
          verifiche/ID/valutazioni). Sigle e risposte le ha già preparate la pagina, senza nomi.
USCITA    cartella dove scrivere dati.json e un file di lettura per domanda (D01.txt, D02.txt…).
--dashboard, --quiz
          esportazione del database della dashboard (ArtifactData con out_dir: CARTELLA/quiz/ID.json
          e CARTELLA/quiz/ID/domande/*.json). Ogni «Domanda N» dell'export viene abbinata alla riga
          con la traccia più simile; l'abbinamento si stampa e va controllato.
--mappa   abbinamento forzato N=idRiga, per le domande che lo script abbina male (vale per tutte le
          varianti della domanda).

Con le domande casuali (varianti per tag) ogni traccia diversa dell'export viene abbinata alla sua riga:
in dati.json ogni studente ha «righe» (domanda → riga della sua variante) e ogni domanda l'elenco «righe».

Lo script non stampa mai nomi: identifica gli studenti con la sigla «COGNOME NOME» delle colonne
dell'export. Se quelle colonne sembrano contenere nomi completi si ferma e chiede di anonimizzare.
"""
import difflib
import glob
import json
import os
import re
import sys


def leggi_tabella(percorso):
    import pandas as pd
    if percorso.lower().endswith(".csv"):
        return pd.read_csv(percorso, keep_default_na=False)
    return pd.read_excel(percorso, keep_default_na=False)   # «NA» è una sigla, non un dato mancante


def pulisci(testo):
    testo = re.sub(r"[*_`#>|]", " ", str(testo or ""))
    return re.sub(r"\s+", " ", testo).strip().lower()


def da_dashboard(cartella):
    """Studenti e testi delle domande da una verifica creata nella dashboard delle correzioni."""
    dom = {os.path.basename(f)[:-5]: json.load(open(f, encoding="utf-8"))
           for f in glob.glob(os.path.join(cartella, "**", "domande", "*.json"), recursive=True)}
    val = {os.path.basename(f)[:-5]: json.load(open(f, encoding="utf-8"))
           for f in glob.glob(os.path.join(cartella, "**", "valutazioni", "*.json"), recursive=True)}
    if not dom or not val:
        sys.exit("Nella cartella non trovo domande/ e valutazioni/ di una verifica della dashboard.")
    studenti = {}
    for did, d in val.items():
        n = str(dom[did]["n"])
        for k, r in d.get("righe", {}).items():
            s = studenti.setdefault(k, {"sigla": r["s"], "chiave": k, "ord": r["ord"], "stato": "", "tempo": "",
                                        "risposte": {}, "testi": {}})
            s["risposte"][n] = r.get("risposta", "")
            testi = dom[did].get("testi") or [""]
            s["testi"][n] = testi[r.get("variante", 0)] if r.get("variante", 0) < len(testi) else testi[0]
    studenti = sorted(studenti.values(), key=lambda s: s["ord"])
    for s in studenti:
        s.pop("ord")
    num = sorted(int(d["n"]) for d in dom.values())
    return studenti, num


def main():
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    opz = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    if len(arg) != 2:
        sys.exit(__doc__)
    export, uscita = arg
    os.makedirs(uscita, exist_ok=True)
    import pandas as pd
    if os.path.isdir(export):
        studenti, num = da_dashboard(export)
        df = None
    else:
        df = leggi_tabella(export)
    if df is not None:
        studenti, num = da_export(df)
    abbina_e_scrivi(export, uscita, opz, studenti, num)


def da_export(df):
    import pandas as pd
    if "Cognome" not in df.columns:
        sys.exit("Nell'export manca la colonna Cognome: è l'export «Risposte» di Moodle?")
    sensibili = [c for c in df.columns if re.search(r"e-?mail|username|nome utente|identificativo|id number", str(c), re.I)]
    if sensibili:
        sys.exit(f"L'export ha colonne con dati personali ({', '.join(map(str, sensibili))}): chiedi all'utente di "
                 "eliminarle (sezione «Preparare l'export» della skill) prima di procedere.")
    nomi = [str(x) for x in list(df["Cognome"]) + list(df.get("Nome", [])) if str(x).strip()]
    lunghi = [n for n in nomi if len(n.strip()) > 3]
    if lunghi:
        sys.exit(f"{len(lunghi)} celle di Cognome/Nome hanno più di 3 caratteri: l'export non sembra "
                 "anonimizzato. Chiedi all'utente di lasciare solo le iniziali prima di procedere.")
    num = sorted(int(m.group(1)) for c in df.columns if (m := re.fullmatch(r"Domanda (\d+)", str(c))))
    studenti = []
    for _, r in df.iterrows():
        sigla = f"{'' if pd.isna(r['Cognome']) else r['Cognome']} {'' if pd.isna(r.get('Nome')) else r.get('Nome')}".strip()
        studenti.append({
            "sigla": sigla,
            "chiave": re.sub(r"[^A-Za-z0-9]+", "-", sigla).strip("-") or f"S{len(studenti)+1}",
            "stato": str(r.get("Stato", "")),
            "tempo": str(r.get("Tempo impiegato", "")),
            "risposte": {str(k): ("" if pd.isna(r.get(f"Risposta data {k}")) else str(r.get(f"Risposta data {k}")))
                         for k in num},
            "testi": {str(k): ("" if pd.isna(r.get(f"Domanda {k}")) else str(r.get(f"Domanda {k}"))) for k in num},
        })
    chiavi = [s["chiave"] for s in studenti]
    if len(set(chiavi)) != len(chiavi):
        sys.exit("Due studenti hanno la stessa sigla: chiedi all'utente di distinguerli nell'export (es. «MA AN2»).")
    return studenti, num


def abbina_e_scrivi(export, uscita, opz, studenti, num):

    righe = {}
    if opz.get("dashboard") and opz.get("quiz"):
        for f in glob.glob(os.path.join(opz["dashboard"], "quiz", opz["quiz"], "domande", "*.json")):
            r = json.load(open(f, encoding="utf-8"))
            if r.get("tipologia") not in ("istruzioni", "descrizione") and r.get("punti", 0):
                righe[os.path.basename(f)[:-5]] = r
    forzate = dict(x.split("=") for x in opz.get("mappa", "").split(",") if "=" in x)
    def migliore(testo):
        t = pulisci(testo)[:600]
        return max(((difflib.SequenceMatcher(None, t, pulisci(r.get("traccia", ""))[:600]).ratio(), rid)
                    for rid, r in righe.items()))
    domande = {}
    for k in num:
        testi = [s["testi"][str(k)] for s in studenti if s["testi"][str(k)]]
        varianti = sorted(set(testi), key=testi.index)
        per_testo = {}                                   # con le domande casuali ogni variante ha la sua riga
        if forzate.get(str(k)):
            per_testo = {t: (None, forzate[str(k)]) for t in varianti}
        elif righe:
            per_testo = {t: migliore(t) for t in varianti}
        for s in studenti:
            s.setdefault("righe", {})[str(k)] = per_testo.get(s["testi"][str(k)], (None, None))[1]
        usate = []
        for t in varianti:
            sim, rid = per_testo.get(t, (None, None))
            if rid and rid not in [u[1] for u in usate]:
                usate.append((sim, rid))
        riga = usate[0][1] if usate else None
        info = righe.get(riga, {})
        punti = {righe[r].get("punti") for _, r in usate if r in righe}
        domande[str(k)] = {"n": k, "riga": riga, "righe": [r for _, r in usate], "pos": info.get("pos", ""),
                           "titolo": info.get("titolo", ""), "punti": info.get("punti"),
                           "tipologia": info.get("tipologia", ""), "varianti": len(varianti),
                           "somiglianza": round(min(x for x, _ in usate), 2) if usate and usate[0][0] is not None else None}
        if len(punti) > 1:
            print(f"ATTENZIONE D{k:02d}: le varianti abbinate hanno punti diversi {sorted(punti)}: controlla l'abbinamento")
        basse = [f"{righe[r].get('pos', r)} {x:.2f}" for x, r in usate if x is not None and x < 0.6]
        print(f"D{k:02d} → " + ", ".join(f"{r} {righe.get(r, {}).get('pos', '')}" for _, r in usate) +
              f" · {info.get('titolo', '')} ({info.get('punti', '?')} punti, {info.get('tipologia', '?')}; "
              f"varianti: {len(varianti)}){'  ← somiglianza bassa: ' + ', '.join(basse) if basse else ''}")
        if len(usate) < len(varianti):
            print(f"   ATTENZIONE: {len(varianti)} varianti nell'export ma {len(usate)} righe diverse nella dashboard")
    for s in studenti:
        s.pop("testi")
    json.dump({"export": os.path.basename(export), "domande": domande, "studenti": studenti},
              open(os.path.join(uscita, "dati.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k in num:
        with open(os.path.join(uscita, f"D{k:02d}.txt"), "w", encoding="utf-8") as f:
            for s in studenti:
                rv = s["righe"].get(str(k))
                pv = righe.get(rv, {}).get("pos", "")
                f.write(f"\n##### {s['sigla']}{'   [' + pv + ']' if len(domande[str(k)]['righe']) > 1 else ''}\n{s['risposte'][str(k)]}\n")
    print(f"\n{len(studenti)} studenti, {len(num)} domande: dati.json e D01.txt… in {uscita}")


if __name__ == "__main__":
    main()
