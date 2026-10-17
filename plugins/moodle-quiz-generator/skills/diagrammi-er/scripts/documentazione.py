#!/usr/bin/env python3
"""Dal modello E/R (file .er) alla documentazione (glossario dati) in Markdown, nel formato deciso.

Uso:
    python3 documentazione.py MODELLO.er [--uscita=FILE.md]

Parti, come nel libro: ipotesi aggiuntive, documentazione delle entità, documentazione delle
associazioni, vincoli non esprimibili (le parti vuote si omettono).

Colonne:
    entità:       NOME | SINONIMI | DESCRIZIONE | ATTRIBUTO | TIPO DI DATO | VINCOLI
    associazioni: NOME | DESCRIZIONE | TIPO DI ASSOCIAZIONE | ENTITÀ COLLEGATE | ATTRIBUTO | TIPO DI DATO | VINCOLI

Il tipo di dato si sceglie dall'elenco del libro (Testo, Testo fisso, Intero, Decimale, Data, Orario,
Data-ora, Booleano, Elenco); i vincoli lo restringono (lunghezza, valori ammessi, valore > 0). La chiave
primaria entra da sola nei vincoli. Gerarchie ISA: nella descrizione della generalizzazione
«Generalizzazione di A e B (totale, esclusiva)», in quella di ogni specializzazione «Specializzazione
di X»; le specializzazioni riportano solo i loro attributi.

Descrizioni, sinonimi, tipi e vincoli vengono dalla descrizione .er (righe «descrizione:», «sinonimi:»,
«tipo ATTRIBUTO: TIPO; VINCOLI»); quelli che mancano restano «?» e sono elencati come AVVISO.
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from modello_er import leggi, chiave, descr_classificazione  # noqa: E402

TIPI_VALIDI = {"testo", "testo fisso", "intero", "decimale", "data", "orario", "data-ora", "booleano", "elenco"}


def cella(t):
    return (t or "").replace("|", "\\|").replace("\n", " ")


def elenco(nomi):
    return nomi[0] if len(nomi) == 1 else ", ".join(nomi[:-1]) + " e " + nomi[-1]


INTEST_ENTITA = ["NOME", "SINONIMI", "DESCRIZIONE", "ATTRIBUTO", "TIPO DI DATO", "VINCOLI"]
INTEST_ASSOC = ["NOME", "DESCRIZIONE", "TIPO DI ASSOCIAZIONE", "ENTITÀ COLLEGATE", "ATTRIBUTO", "TIPO DI DATO", "VINCOLI"]


def tabelle(m):
    """Struttura comune ai formati: righe di celle; la prima cella di un'entità o associazione è in grassetto
    (le celle sono stringhe; il grassetto si indica con una tupla (testo, True))."""
    avvisi = []
    t = {"entita": [], "associazioni": []}

    gen_di = {}
    spec_di = {}
    for g in m["gerarchie"]:
        gen_di[g["gen"]] = g
        for s_ in g["spec"]:
            spec_di[s_] = g["gen"]

    def tipo_e_vincoli(oggetto, nome_attr, e_chiave, altre_chiavi, deboli):
        tipo, vinc = oggetto["tipi"].get(nome_attr, ("", ""))
        if not tipo:
            avvisi.append("manca il tipo di «%s» (%s): riga «tipo %s: TIPO; VINCOLI»" % (nome_attr, oggetto["nome"], nome_attr))
            tipo = "?"
        elif tipo.lower() not in TIPI_VALIDI:
            avvisi.append("«%s» (%s): il tipo «%s» non è nell'elenco del libro (%s)"
                          % (nome_attr, oggetto["nome"], tipo, ", ".join(sorted(TIPI_VALIDI))))
        v = []
        if e_chiave:
            insieme = [x for x in altre_chiavi if x != nome_attr]
            pezzi = []
            if insieme:
                pezzi.append("a " + elenco(insieme))
            if len(deboli) == 1:
                pezzi.append("all'associazione «%s»" % deboli[0])
            elif deboli:
                pezzi.append("alle associazioni " + elenco(["«%s»" % d for d in deboli]))
            v.append("Chiave primaria, insieme " + " e ".join(pezzi) if pezzi else "Chiave primaria")
        if vinc:
            v.append(vinc)
        return tipo, ", ".join(v) if v else "—"

    for nome, e in m["entita"].items():
        descr = e["descrizione"]
        if nome in gen_di:
            g = gen_di[nome]
            descr = ("Generalizzazione di %s (%s). " % (elenco(g["spec"]), descr_classificazione(g)) + descr).strip()
        if nome in spec_di:
            descr = ("Specializzazione di %s. " % spec_di[nome] + descr).strip()
        if not e["descrizione"]:
            avvisi.append("manca la descrizione di «%s»: riga «descrizione: …»" % nome)
        chiavi = chiave(e)
        attr = e["ordine"] or [("—", False)]
        for i, (a, k) in enumerate(attr):
            if a == "—":
                tipo, vinc = "—", "—"
            else:
                tipo, vinc = tipo_e_vincoli(e, a, k, chiavi, e["deboli"] if k else [])
            if i == 0:
                t["entita"].append([(nome, True), e["sinonimi"] or "—", descr or "?", a, tipo, vinc])
            else:
                t["entita"].append(["", "", "", a, tipo, vinc])

    if m["associazioni"]:
        for a in m["associazioni"]:
            tipo_ass = "%s:%s" % (a["c1"][1], a["c2"][1])
            if tipo_ass == "N:1":
                tipo_ass = "1:N"
            collegate = "%s, %s" % (a["e1"].upper(), a["e2"].upper())
            if not a["descrizione"]:
                avvisi.append("manca la descrizione dell'associazione «%s»: riga «descrizione: …»" % a["nome"])
            attr = a["ordine"] or [("—", False)]
            for i, (x, _) in enumerate(attr):
                if x == "—":
                    tipo, vinc = "—", "—"
                else:
                    tipo, vinc = tipo_e_vincoli(a, x, False, [], [])
                if i == 0:
                    t["associazioni"].append([(a["nome"].upper(), True), a["descrizione"] or "?", tipo_ass,
                                              collegate, x, tipo, vinc])
                else:
                    t["associazioni"].append(["", "", "", "", x, tipo, vinc])
    return t, avvisi


def tabella_md(intest, righe):
    def c(x):
        return "**%s**" % cella(x[0]) if isinstance(x, tuple) else cella(x)
    out = ["| " + " | ".join(intest) + " |", "|" + "---|" * len(intest)]
    out += ["| " + " | ".join(c(x) for x in r) + " |" for r in righe]
    return "\n".join(out)


def documentazione(m):
    """La documentazione in Markdown (ipotesi, entità, associazioni, vincoli non esprimibili)."""
    t, avvisi = tabelle(m)
    parti = []
    if m["ipotesi"]:
        parti.append("**Ipotesi aggiuntive**\n\n" + "\n".join("- " + i for i in m["ipotesi"]))
    parti.append("**Documentazione delle entità**\n\n" + tabella_md(INTEST_ENTITA, t["entita"]))
    if t["associazioni"]:
        parti.append("**Documentazione delle associazioni**\n\n" + tabella_md(INTEST_ASSOC, t["associazioni"]))
    if m["vincoli"]:
        parti.append("**Vincoli non esprimibili**\n\n" + "\n".join("- " + v for v in m["vincoli"]))
    return "\n\n".join(parti) + "\n", avvisi


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        raise SystemExit(__doc__)
    opz = dict(x[2:].split("=", 1) if "=" in x else (x[2:], "1") for x in sys.argv[1:] if x.startswith("--"))
    testo, avvisi = documentazione(leggi(open(a[0], encoding="utf-8").read()))
    for av in avvisi:
        print("AVVISO: " + av, file=sys.stderr)
    if opz.get("uscita"):
        open(opz["uscita"], "w", encoding="utf-8").write(testo)
        print("OK: %s" % opz["uscita"], file=sys.stderr)
    else:
        sys.stdout.write(testo)


if __name__ == "__main__":
    main()
