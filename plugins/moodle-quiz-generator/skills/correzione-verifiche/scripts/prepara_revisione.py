#!/usr/bin/env python3
"""Prepara i documenti di una verifica per la dashboard «Correzione verifiche» dalle proposte di correzione.

Uso:
    python3 prepara_revisione.py LAVORO --id=v5r-5q --titolo="V5R · 5Q SIA" --sottotitolo="Verifica di ripasso SQL e PHP"
                                 [--quiz=ID_DASHBOARD_QUIZ] [--disclaimer="…"] [--solo=D11]
    python3 prepara_revisione.py LAVORO --id=prova-5q --esistente    (verifica creata con «Nuova correzione»)

LAVORO   la cartella di leggi_export.py, con dati.json, esiti.json (se c'è) e voti/DNN.json:
         una proposta per domanda, scritta da Claude, nella forma
         {"criteri": "…", "voti": {"AL-IU": [5, "commento"], …}}
         (chiave dello studente come in dati.json; vale anche la sigla con lo spazio).
         Una domanda senza file voti resta «in attesa» (punteggio vuoto).

--id      identificativo della verifica nella dashboard (lettere, cifre, trattini): quiz e classe,
          per esempio v5r-5q, perché la stessa verifica può essere corretta in più classi.

Scrive in LAVORO/revisione/:
- verifica.json           il documento della verifica (collezione «verifiche»): titolo, sottotitolo,
                          numero di studenti, data, quiz della dashboard, frase sull'IA
- domande/DNN.json        un documento per domanda (collezione «verifiche/ID/domande»)
- valutazioni/DNN.json    le righe degli studenti di quella domanda («verifiche/ID/valutazioni»)
e stampa le voci del batch per ArtifactData. --solo=D11,D12 rigenera solo quelle domande (e non il
documento della verifica). --esistente: la verifica c'è già nella dashboard (creata dall'utente con
«Nuova correzione»): non riscrive il suo documento, solo domande e valutazioni, e i `set` vanno fatti
con `if_version` (le versioni le dà un `list`).
"""
import datetime
import json
import os
import re
import sys

DISCLAIMER = ("Il seguente feedback è stato scritto con l'aiuto di una IA generativa. "
              "La valutazione è stata svolta dal docente.")


def main():
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    opz = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    esistente = "--esistente" in sys.argv
    if len(arg) != 1 or "id" not in opz or ("titolo" not in opz and not esistente):
        sys.exit(__doc__)
    vid = opz["id"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,60}", vid):
        sys.exit("--id: solo lettere, cifre, trattini e trattini bassi")
    lavoro = arg[0]
    dati = json.load(open(os.path.join(lavoro, "dati.json"), encoding="utf-8"))
    p_esiti = os.path.join(lavoro, "esiti.json")
    esiti = json.load(open(p_esiti, encoding="utf-8")) if os.path.exists(p_esiti) else {}
    solo = set(opz["solo"].split(",")) if opz.get("solo") else None
    out = os.path.join(lavoro, "revisione")
    for d in ("domande", "valutazioni"):
        os.makedirs(os.path.join(out, d), exist_ok=True)

    voci, mancanti = [], []
    for k, dom in sorted(dati["domande"].items(), key=lambda x: int(x[0])):
        did = f"D{int(k):02d}"
        if solo and did not in solo:
            continue
        p_voti = os.path.join(lavoro, "voti", did + ".json")
        prop = json.load(open(p_voti, encoding="utf-8")) if os.path.exists(p_voti) else {}
        voti = {kk.replace(" ", "-"): v for kk, v in prop.get("voti", {}).items()}
        auto = esiti.get(k)
        massimo = dom.get("punti") or prop.get("max")
        if massimo is None:
            sys.exit(f"{did}: punti sconosciuti (riga della dashboard non abbinata): mettili in voti/{did}.json come «max».")
        json.dump({"n": int(k), "breve": dom.get("pos") or f"D{k}", "titolo": dom.get("titolo") or f"Domanda {k}",
                   "max": massimo, "tipo": "auto" if auto else "manuale",
                   "criteri": prop.get("criteri", "") or ("IN ATTESA: proposte non ancora scritte." if not voti else "")},
                  open(os.path.join(out, "domande", did + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
        righe = {}
        for i, s in enumerate(dati["studenti"]):
            p, c = voti.get(s["chiave"], [None, ""])
            if voti and s["chiave"] not in voti:
                mancanti.append(f"{did} {s['sigla']}")
            if p is not None and not (0 <= float(p) <= float(massimo)):
                sys.exit(f"{did} {s['sigla']}: {p} fuori da 0–{massimo}")
            ea = (auto or {}).get("studenti", {}).get(s["chiave"], {})
            righe[s["chiave"]] = {"s": s["sigla"], "ord": i, "risposta": s["risposte"][k],
                                  "esito": ea.get("esito", "" if voti else "in attesa"),
                                  "auto": ea.get("auto"), "punti": p, "commento": c or "",
                                  "ok": False, "inserito": False}
        json.dump({"righe": righe}, open(os.path.join(out, "valutazioni", did + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False)
        voci += [(f"verifiche/{vid}/domande", did, os.path.join(out, "domande", did + ".json")),
                 (f"verifiche/{vid}/valutazioni", did, os.path.join(out, "valutazioni", did + ".json"))]

    if not solo and not esistente:
        json.dump({"titolo": opz["titolo"], "sottotitolo": opz.get("sottotitolo", ""), "quiz": opz.get("quiz", ""),
                   "studenti": len(dati["studenti"]), "disclaimer": opz.get("disclaimer", DISCLAIMER),
                   "creato": datetime.date.today().isoformat(), "archiviata": False,
                   "avanzamento": {"righe": 0, "riviste": 0}},
                  open(os.path.join(out, "verifica.json"), "w", encoding="utf-8"), ensure_ascii=False)
        voci.insert(0, ("verifiche", vid, os.path.join(out, "verifica.json")))
    if mancanti:
        print("ATTENZIONE, studenti senza proposta:", ", ".join(mancanti))
    batch = [{"op": "set", "collection": c, "doc_id": d, "file_path": os.path.abspath(f)} for c, d, f in voci]
    print(json.dumps(batch, ensure_ascii=False))
    print(f"\n{len(batch)} documenti in {out}")


if __name__ == "__main__":
    main()
