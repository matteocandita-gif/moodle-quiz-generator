#!/usr/bin/env python3
"""Rilegge il database di una verifica della dashboard «Correzione verifiche» e calcola i totali, per la tabella finale.

Uso:
    python3 riepilogo.py CARTELLA [--csv=riepilogo.csv]

CARTELLA  l'esportazione di una verifica (ArtifactData list con out_dir di «verifiche/ID/domande» e
          «verifiche/ID/valutazioni»): sotto CARTELLA, …/domande/DNN.json e …/valutazioni/DNN.json.

Stampa una riga per studente con i punti di ogni domanda, il totale e il voto (totale diviso per
il massimo e moltiplicato per 10), le righe ancora senza punteggio, quelle non spuntate come riviste
e quelle da inserire in Moodle non ancora segnate «inserito». Le somme le fa lo script, mai a mano.
"""
import csv
import glob
import json
import os
import sys


def leggi(p):
    d = json.load(open(p, encoding="utf-8"))
    return d.get("data", d)          # out_dir di ArtifactData può avvolgere il corpo


def main():
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    opz = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    if len(arg) != 1:
        sys.exit(__doc__)
    base = arg[0]
    domande = {os.path.basename(f)[:-5]: leggi(f) for f in glob.glob(os.path.join(base, "**", "domande", "*.json"), recursive=True)}
    val = {os.path.basename(f)[:-5]: leggi(f) for f in glob.glob(os.path.join(base, "**", "valutazioni", "*.json"), recursive=True)}
    ids = sorted(domande, key=lambda d: domande[d]["n"])
    massimo = sum(float(domande[d]["max"]) for d in ids)
    studenti = sorted({(r["ord"], c, r["s"]) for d in val for c, r in val[d]["righe"].items()})
    senza, non_riviste, da_moodle, tabella = [], 0, [], []
    for _, c, sigla in studenti:
        riga, tot = [sigla], 0.0
        for d in ids:
            r = val.get(d, {}).get("righe", {}).get(c)
            if not r or r.get("punti") is None:
                senza.append(f"{d} {sigla}")
                riga.append("")
                continue
            p = float(r["punti"])
            tot += p
            riga.append(f"{p:g}".replace(".", ","))
            non_riviste += 0 if r.get("ok") else 1
            manuale = domande[d]["tipo"] == "manuale"
            if (manuale or p != float(r.get("auto") or 0)) and not r.get("inserito"):
                da_moodle.append(f"{d} {sigla}")
        riga += [f"{tot:g}".replace(".", ","), f"{tot / massimo * 10:.2f}".replace(".", ",")]
        tabella.append(riga)
    intest = ["Studente"] + [f"D{domande[d]['n']} ({domande[d]['max']:g})" for d in ids] + [f"Totale ({massimo:g})", "Voto"]
    larg = [max(len(str(x)) for x in col) for col in zip(intest, *tabella)]
    for r in [intest] + tabella:
        print("  ".join(str(x).rjust(w) for x, w in zip(r, larg)))
    voti = [float(r[-1].replace(",", ".")) for r in tabella]
    print(f"\nMedia: {sum(voti) / len(voti):.2f} · sufficienti: {sum(v >= 6 for v in voti)}/{len(voti)}")
    print(f"Senza punteggio: {len(senza)}{' (' + ', '.join(senza[:12]) + ('…' if len(senza) > 12 else '') + ')' if senza else ''}")
    print(f"Non spuntate come riviste: {non_riviste} · da inserire in Moodle e non segnate: {len(da_moodle)}")
    if opz.get("csv"):
        with open(opz["csv"], "w", newline="", encoding="utf-8") as f:
            csv.writer(f, delimiter=";").writerows([intest] + tabella)
        print("CSV:", opz["csv"])


if __name__ == "__main__":
    main()
