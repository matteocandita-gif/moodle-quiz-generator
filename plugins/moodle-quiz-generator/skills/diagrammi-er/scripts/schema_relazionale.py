#!/usr/bin/env python3
"""Dal modello E/R (file .er) allo schema relazionale, con le regole di traduzione del libro.

Uso:
    python3 schema_relazionale.py MODELLO.er [--formato=libro|quiz] [--uscita=FILE.md]

Regole (capitolo 3 del libro):
  - ogni entità diventa una relazione, con il nome al plurale e la chiave primaria sottolineata;
  - 1 a N: chiave esterna nella relazione dell'entità che partecipa con cardinalità massima 1; gli
    attributi dell'associazione seguono la chiave esterna;
  - 1 a 1: chiave esterna dalla parte con partecipazione obbligatoria (se una delle due è opzionale),
    altrimenti nella prima entità o in quella indicata con «chiave esterna in»; la chiave esterna è unica;
  - N a N: una relazione nuova (Plurale1_Plurale2, o il nome dato con «tabella») con le due chiavi
    esterne, insieme chiave primaria, più gli attributi dell'associazione;
  - entità debole: la chiave esterna verso l'entità che la identifica entra nella chiave primaria, tra
    i primi campi;
  - associazione ricorsiva: chiave esterna verso la stessa relazione (1 a N) o relazione nuova (N a N),
    con nomi che dicono il ruolo («chiave esterna», «chiavi esterne», «tabella»);
  - gerarchie ISA secondo «traduzione»: tutto su, tutto giù o lasciare tutto (predefinita, perché
    funziona sempre); avvisa nei casi che il libro sconsiglia.

Nomi delle chiavi esterne (regola dell'utente): il nome deve dire senza ambiguità a quale campo punta.
Se la chiave puntata ha un nome chiaro (CodCliente, ISBN, Matricola) la chiave esterna si chiama allo
stesso modo; se ha un nome generico (Codice, Id, Numero, Nome, Cod_f) si aggiunge l'entità puntata
(Codice_compagnia); le chiavi composte prendono sempre il nome dell'entità (Nome_comune, Provincia_comune).

Formati: «libro» (Markdown: **Veicoli**(<u>Codice</u>, Marca, Codice_compagnia*), una relazione per
paragrafo) e «quiz» (convenzione della dashboard: Veicoli (__Codice__, Marca, Codice_compagnia*), una
relazione per riga). Le scelte fatte senza indicazioni nella descrizione (plurali, nomi di default,
lato della chiave esterna nell'1 a 1) sono elencate come NOTA o AVVISO: vanno controllate.
"""
import os
import re
import sys
import unicodedata

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from modello_er import leggi, chiave  # noqa: E402

GENERICI = {"codice", "cod", "id", "numero", "num", "nr", "nome", "n", "code", "chiave", "data", "descrizione",
            "tipo", "sigla", "progressivo"}
INVARIABILI = {"auto", "moto", "foto", "radio", "bici", "film", "sport", "bar", "computer", "smartphone", "tablet",
               "software", "hardware", "hotel", "menu", "re", "specie", "serie", "crisi", "analisi", "tesi",
               "ipotesi", "sintesi", "diagnosi", "taxi", "gas", "camion", "quiz", "email", "app", "account",
               "corso", "partner", "server", "router", "file", "web", "sito"}
PREPOSIZIONI = {"di", "d'", "del", "dello", "della", "dei", "degli", "delle", "da", "in", "per", "con", "a",
                "al", "alla", "su", "tra", "fra"}
NOTE, AVVISI = [], []


def senza_accenti(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def plurale_parola(p):
    b = p.lower()
    if b in INVARIABILI or not b or b[-1] not in "aeiou" or b[-1] in "àèéìòù":
        return p
    if b.endswith(("ca", "ga")):
        nuovo = p[:-1] + "he"
    elif b.endswith(("cia", "gia")):
        nuovo = p[:-1] + "e" if len(b) > 3 and b[-4] in "aeiou" else p[:-2] + "e"
    elif b.endswith("a"):
        nuovo = p[:-1] + "e"
    elif b.endswith("io"):
        nuovo = p[:-1]
    elif b.endswith("co"):
        nuovo = p[:-1] + ("hi" if len(b) <= 6 else "i")
        AVVISI.append("plurale di «%s»: «%s», controllalo (-ci o -chi)" % (p, nuovo))
    elif b.endswith("go"):
        nuovo = p[:-1] + "hi"
    elif b.endswith(("o", "e")):
        nuovo = p[:-1] + "i"
    else:
        nuovo = p
    return nuovo


def nome_relazione(e):
    """Nome della relazione: il plurale dato con «plurale», o quello calcolato."""
    if e["plurale"]:
        return re.sub(r"\s+", "_", e["plurale"].strip())
    parole = re.findall(r"[^\s']+'?|'", e["nome"])
    out, dopo_prep = [], False
    for w in parole:
        if w.lower() in PREPOSIZIONI:
            dopo_prep = True
            continue
        out.append(w if dopo_prep else plurale_parola(w))
    nome = senza_accenti("_".join(out))
    if nome != e["nome"]:
        NOTE.append("%s → %s" % (e["nome"], nome))
    return nome


def suffisso(nome_entita):
    parole = [w for w in re.findall(r"[^\s']+", nome_entita) if w.lower() not in PREPOSIZIONI]
    return senza_accenti(parole[0].lower()) if parole else senza_accenti(nome_entita.lower())


def generico(attr, nome_entita):
    norm = re.sub(r"[_\s]", "", attr.lower())
    if suffisso(nome_entita) in norm:
        return False
    return norm in GENERICI or len(norm) <= 2 or (len(norm) <= 5 and norm.startswith(("cod", "id", "num", "nr")))


def nome_fk(attr, nome_entita, composta):
    if composta or generico(attr, nome_entita):
        return "%s_%s" % (attr, suffisso(nome_entita))
    return attr


class Campo:
    def __init__(self, nome, pk=False, fk=False, facoltativo=False, opzionale=False):
        # facoltativo: può essere NULL; opzionale: viene da un attributo (0,1) del modello E/R
        self.nome, self.pk, self.fk = nome, pk, fk
        self.facoltativo, self.opzionale = facoltativo or opzionale, opzionale


class Relazione:
    def __init__(self, nome, origine):
        self.nome, self.origine, self.campi = nome, origine, []

    def ha(self, nome):
        return any(c.nome.lower() == nome.lower() for c in self.campi)

    def aggiungi(self, campo, in_testa=False):
        nome, k = campo.nome, 2
        while self.ha(campo.nome):
            campo.nome = "%s%d" % (nome, k)
            k += 1
        if in_testa:
            # in testa, dopo le altre chiavi esterne già messe in testa
            i = 0
            while i < len(self.campi) and self.campi[i].pk and self.campi[i].fk:
                i += 1
            self.campi.insert(i, campo)
        else:
            self.campi.append(campo)

    def chiave(self):
        return [c for c in self.campi if c.pk]


def traduci(m):
    entita = m["entita"]
    rel = {}          # nome entità -> Relazione (le entità che restano)
    vincoli = []
    # ---- gerarchie: chi resta, chi assorbe chi
    assorbita = {}    # specializzazione -> generalizzazione (tutto su)
    duplicata = {}    # generalizzazione -> specializzazioni (tutto giù)
    sotto = {}        # specializzazione -> generalizzazione (lasciare tutto)
    for g in m["gerarchie"]:
        if not g["traduzione"]:
            g["traduzione"] = "tutto"
            NOTE.append("gerarchia di %s: strategia non indicata, uso «lasciare tutto», che funziona sempre"
                        % g["gen"])
        ass_spec = [a["nome"] for a in m["associazioni"] if {a["e1"], a["e2"]} & set(g["spec"])]
        ass_gen = [a["nome"] for a in m["associazioni"] if g["gen"] in (a["e1"], a["e2"])]
        if g["traduzione"] == "su":
            for s_ in g["spec"]:
                assorbita[s_] = g["gen"]
            if ass_spec:
                AVVISI.append("gerarchia di %s: con «tutto su» l'associazione «giù» %s può collegare istanze "
                              "che non sono della specializzazione (il libro consiglia «tutto giù» o «lasciare "
                              "tutto»)" % (g["gen"], ", ".join("«%s»" % x for x in ass_spec)))
        elif g["traduzione"] == "giu":
            duplicata[g["gen"]] = list(g["spec"])
            if g["copertura"] != "t":
                AVVISI.append("gerarchia di %s: è non totale, e con «tutto giù» le istanze che non sono di nessuna "
                              "specializzazione non hanno una tabella (il libro lo esclude)" % g["gen"])
            if ass_gen:
                AVVISI.append("gerarchia di %s: con «tutto giù» l'associazione «su» %s va ripetuta per ogni "
                              "specializzazione, e una chiave esterna verso %s dovrebbe puntare a più "
                              "tabelle (il libro consiglia di evitarlo)" % (g["gen"], ", ".join("«%s»" % x for x in ass_gen), g["gen"]))
        else:
            for s_ in g["spec"]:
                sotto[s_] = g["gen"]

    def ordine_attr(e, solo_chiave=None):
        return [(a, k) for a, k in e["ordine"] if solo_chiave is None or k == solo_chiave]

    # ---- entità
    for nome, e in entita.items():
        if nome in assorbita or nome in duplicata:
            continue
        r = Relazione(nome_relazione(e), nome)
        rel[nome] = r
        if nome in sotto:
            continue           # chiave e campi dopo la generalizzazione
        base = [nome]
        g_su = [g for g in m["gerarchie"] if g["traduzione"] == "giu" and nome in g["spec"]]
        if g_su:
            base = [g_su[0]["gen"], nome]   # tutto giù: prima gli attributi ereditati
        for b in base:
            for a, k in ordine_attr(entita[b]):
                r.aggiungi(Campo(a, pk=k, opzionale=a in entita[b]["opzionali"]))
        if not r.chiave() and not e["deboli"]:
            AVVISI.append("«%s» non ha la chiave primaria" % nome)
    # tutto su: la generalizzazione prende gli attributi delle specializzazioni, opzionali
    for g in m["gerarchie"]:
        if g["traduzione"] != "su":
            continue
        r = rel[g["gen"]]
        fac = []
        for s_ in g["spec"]:
            for a, _ in ordine_attr(entita[s_]):
                r.aggiungi(Campo(a, facoltativo=True))
                fac.append(a)
        if g["campo_tipo"]:
            r.aggiungi(Campo(g["campo_tipo"]))
            vincoli.append("%s.%s: indica la specializzazione (%s)" % (r.nome, g["campo_tipo"], ", ".join(g["spec"])))
        if fac:
            vincoli.append("%s: %s sono opzionali (NULL quando l'istanza non è della specializzazione che li ha)"
                           % (r.nome, ", ".join(fac)))
    # ---- associazioni, dopo le sostituzioni delle gerarchie
    associazioni = []
    for a in m["associazioni"]:
        e1, e2 = assorbita.get(a["e1"], a["e1"]), assorbita.get(a["e2"], a["e2"])
        copie = [(e1, e2)]
        if e1 in duplicata or e2 in duplicata:
            copie = [(x, y) for x in duplicata.get(e1, [e1]) for y in duplicata.get(e2, [e2])]
        for x, y in copie:
            b = dict(a)
            b["e1"], b["e2"] = x, y
            b["copia"] = len(copie) > 1
            b["spec_dup"] = x if x != e1 else (y if y != e2 else "")
            associazioni.append(b)

    # ---- chiavi delle entità deboli e delle specializzazioni (in ordine di dipendenza)
    def pk_di(nome):
        return rel[nome].chiave()

    risolte = {n for n, e in entita.items() if n in rel and not e["deboli"] and n not in sotto}
    identificanti = {}
    for n, e in entita.items():
        if n in rel and e["deboli"]:
            identificanti[n] = [b for b in associazioni if b["nome"] in e["deboli"] and n in (b["e1"], b["e2"])]
    giri = 0
    while len(risolte) < len(rel) and giri < 20:
        giri += 1
        for n in list(rel):
            if n in risolte:
                continue
            if n in sotto:
                gen = sotto[n]
                if gen not in risolte:
                    continue
                r = rel[n]
                proprie = [Campo(a, opzionale=a in entita[n]["opzionali"]) for a, _ in ordine_attr(entita[n])]
                pk = pk_di(gen)
                for c in pk:
                    r.aggiungi(Campo(nome_fk(c.nome, gen, len(pk) > 1), pk=True, fk=True))
                for c in proprie:
                    r.aggiungi(c)
                risolte.add(n)
                continue
            altre = [b["e2"] if b["e1"] == n else b["e1"] for b in identificanti[n]]
            if all(x in risolte for x in altre):
                r = rel[n]
                for b, x in zip(identificanti[n], altre):
                    pk = pk_di(x)
                    for c in pk:
                        nome = b["fk"] if b["fk"] and len(pk) == 1 else nome_fk(c.nome, x, len(pk) > 1)
                        r.aggiungi(Campo(nome, pk=True, fk=True), in_testa=True)
                    b["fatta"] = True
                risolte.add(n)
    if len(risolte) < len(rel):
        raise SystemExit("ERRORE: chiavi che dipendono l'una dall'altra in modo circolare: %s"
                         % ", ".join(sorted(set(rel) - risolte)))

    # ---- associazioni restanti
    extra = []
    for b in associazioni:
        if b.get("fatta"):
            # entità debole: gli attributi dell'associazione seguono la chiave esterna
            debole = b["e1"] if b["e1"] in identificanti and b in identificanti[b["e1"]] else b["e2"]
            for a, _ in b["ordine"]:
                rel[debole].aggiungi(Campo(a, opzionale=a in b["opzionali"]))
            continue
        e1, e2, (min1, max1), (min2, max2) = b["e1"], b["e2"], b["c1"], b["c2"]
        if e1 == e2:
            r = rel[e1]
            pk = pk_di(e1)
            if max1 == "N" and max2 == "N":
                tab = b["tabella"] or re.sub(r"\s+", "_", b["nome"].strip()).capitalize()
                if not b["tabella"]:
                    AVVISI.append("«%s» (N a N ricorsiva): tabella «%s»; un nome più chiaro si dà con «tabella:» "
                                  "(per esempio Colleghi)" % (b["nome"], tab))
                nuova = Relazione(tab, b["nome"])
                nomi = b["fks"] if len(b["fks"]) == 2 and len(pk) == 1 else None
                if not nomi:
                    AVVISI.append("«%s»: le due chiavi esterne verso %s devono avere nomi diversi che dicono il "
                                  "ruolo: indicali con «chiavi esterne: A, B»" % (b["nome"], r.nome))
                for i in (0, 1):
                    for c in pk:
                        nn = nomi[i] if nomi else "%s_%d" % (c.nome, i + 1)
                        nuova.aggiungi(Campo(nn, pk=True, fk=True))
                for a, _ in b["ordine"]:
                    nuova.aggiungi(Campo(a, opzionale=a in b["opzionali"]))
                extra.append(nuova)
            else:
                ruolo = re.findall(r"[^\s']+", b["nome"])[0].lower()
                for c in pk:
                    nn = b["fk"] if b["fk"] and len(pk) == 1 else "%s_%s" % (c.nome, ruolo)
                    if not b["fk"]:
                        AVVISI.append("«%s» (ricorsiva): chiave esterna «%s»; il nome che dice il ruolo si dà con "
                                      "«chiave esterna:»" % (b["nome"], nn))
                    r.aggiungi(Campo(nn, fk=True))
                for a, _ in b["ordine"]:
                    r.aggiungi(Campo(a, opzionale=a in b["opzionali"]))
            continue
        if max1 == "N" and max2 == "N":
            tab = b["tabella"] or "%s_%s" % (rel[e1].nome, rel[e2].nome)
            if b.get("copia") and b["tabella"] and b["spec_dup"]:
                tab = "%s_%s" % (b["tabella"], rel[b["spec_dup"]].nome)
            nuova = Relazione(tab, b["nome"])
            nomi = b["fks"] if len(b["fks"]) == 2 else None
            for i, x in enumerate((e1, e2)):
                pk = pk_di(x)
                for c in pk:
                    nn = nomi[i] if nomi and len(pk) == 1 else nome_fk(c.nome, x, len(pk) > 1)
                    nuova.aggiungi(Campo(nn, pk=True, fk=True))
            for a, _ in b["ordine"]:
                nuova.aggiungi(Campo(a, opzionale=a in b["opzionali"]))
            extra.append(nuova)
            continue
        if max1 == "1" and max2 == "1":
            if b["fk_in"]:
                lato = b["fk_in"]
            elif min1 == "1" and min2 == "0":
                lato = e1
            elif min2 == "1" and min1 == "0":
                lato = e2
            else:
                lato = e1
                NOTE.append("«%s» (1 a 1): chiave esterna in %s (scelta equivalente all'altra; si cambia con "
                            "«chiave esterna in:»)" % (b["nome"], rel[e1].nome))
        else:
            lato = e1 if max1 == "1" else e2
        altro = e2 if lato == e1 else e1
        r = rel[lato]
        pk = pk_di(altro)
        nomi_fk = []
        for c in pk:
            nn = b["fk"] if b["fk"] and len(pk) == 1 else nome_fk(c.nome, altro, len(pk) > 1)
            campo = Campo(nn, fk=True)
            r.aggiungi(campo)
            nomi_fk.append(campo.nome)
        if max1 == "1" and max2 == "1":
            vincoli.append("%s.%s: unico (associazione 1 a 1 «%s»)" % (r.nome, ", ".join(nomi_fk), b["nome"]))
        for a, _ in b["ordine"]:
            r.aggiungi(Campo(a, opzionale=a in b["opzionali"]))
    tutte = list(rel.values()) + extra
    for r in tutte:
        opz = [c.nome for c in r.campi if c.opzionale]
        if opz:
            vincoli.append("%s: %s %s (%s essere NULL)" % (r.nome, ", ".join(opz),
                           "è opzionale" if len(opz) == 1 else "sono opzionali", "può" if len(opz) == 1 else "possono"))
    return tutte, vincoli


def campi_ordinati(r):
    """Prima la chiave primaria (le chiavi esterne che ne fanno parte in testa), poi gli altri campi."""
    return [c for c in r.campi if c.pk and c.fk] + [c for c in r.campi if c.pk and not c.fk] + \
           [c for c in r.campi if not c.pk]


def formatta(relazioni, vincoli, formato):
    righe = []
    for r in relazioni:
        campi = []
        for c in campi_ordinati(r):
            t = c.nome
            if c.pk:
                t = "<u>%s</u>" % t if formato == "libro" else "__%s__" % t
            if c.fk:
                t += "*"
            campi.append(t)
        if formato == "libro":
            righe.append("**%s**(%s)" % (r.nome, ", ".join(campi)))
        else:
            righe.append("%s (%s)" % (r.nome, ", ".join(campi)))
    sep = "\n\n" if formato == "libro" else "\n"
    testo = sep.join(righe)
    if vincoli:
        testo += "\n\n**Vincoli**\n\n" + "\n".join("- " + v for v in vincoli)
    return testo + "\n"


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        raise SystemExit(__doc__)
    opz = dict(x[2:].split("=", 1) if "=" in x else (x[2:], "1") for x in sys.argv[1:] if x.startswith("--"))
    formato = opz.get("formato", "libro")
    if formato not in ("libro", "quiz"):
        raise SystemExit("ERRORE: --formato=libro oppure --formato=quiz")
    m = leggi(open(a[0], encoding="utf-8").read())
    relazioni, vincoli = traduci(m)
    testo = formatta(relazioni, vincoli, formato)
    if NOTE:
        print("NOTA: " + "\nNOTA: ".join(NOTE), file=sys.stderr)
    if AVVISI:
        print("AVVISO: " + "\nAVVISO: ".join(AVVISI), file=sys.stderr)
    if opz.get("uscita"):
        open(opz["uscita"], "w", encoding="utf-8").write(testo)
        print("OK: %s" % opz["uscita"], file=sys.stderr)
    else:
        sys.stdout.write(testo)


if __name__ == "__main__":
    main()
