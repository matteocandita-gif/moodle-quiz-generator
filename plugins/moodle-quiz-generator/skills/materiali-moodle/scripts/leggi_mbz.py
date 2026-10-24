#!/usr/bin/env python3
"""Legge un backup di corso Moodle (.mbz) e ne mostra il contenuto.

Uso:
    python3 leggi_mbz.py BACKUP.mbz                 sezioni, attività, banche
    python3 leggi_mbz.py BACKUP.mbz --domande TESTO domande delle categorie il cui
                                                    percorso contiene TESTO (con il testo)
    python3 leggi_mbz.py BACKUP.mbz --quiz          per ogni quiz la struttura: tempo, punteggio,
                                                    sezioni, slot con pagina e punti, domande
                                                    usate (con versioni e banca) e domande casuali
                                                    (con i tag e la categoria da cui pescano)
    python3 leggi_mbz.py BACKUP.mbz --banche        le banche delle domande fuori dalle attività del
                                                    backup (per esempio quella di un deposito), con
                                                    i valori di "banca" per crea_mbz.py
    python3 leggi_mbz.py BACKUP.mbz --estrai DIR    estrae l'archivio in DIR

Funziona sia con il backup di un corso sia con il backup di una singola attività
(per esempio la copia PDP di un quiz): le domande delle banche condivise usate dal
quiz sono incluse in questions.xml.

Il backup è un archivio tar.gz (o zip nelle versioni più vecchie). La struttura
del corso sta in moodle_backup.xml, le attività in activities/<tipo>_<id>/, le
domande di tutte le banche in questions.xml alla radice.
"""
import html
import json
import pathlib
import re
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET
import zipfile


def estrai(mbz, cartella):
    cartella = pathlib.Path(cartella)
    cartella.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(mbz):
        with zipfile.ZipFile(mbz) as z:
            z.extractall(cartella)
    else:
        with tarfile.open(mbz) as t:
            membri = [m for m in t.getmembers()
                      if not m.name.startswith("/") and ".." not in m.name]
            try:
                t.extractall(cartella, members=membri, filter="data")
            except TypeError:                           # Python senza il parametro filter
                t.extractall(cartella, members=membri)
    return cartella


def testo_semplice(s, lim=None):
    s = re.sub(r"<[^>]+>", " ", html.unescape(s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return s if lim is None or len(s) <= lim else s[:lim] + "…"


def struttura(radice):
    mb = ET.parse(radice / "moodle_backup.xml").getroot()
    info = mb.find("information")
    print("Corso: %s" % (info.findtext("original_course_fullname") or "?"))
    print("Moodle: %s\n" % (info.findtext("moodle_release") or "?"))
    sezioni = {}
    for s in mb.iter("section"):
        sid = s.findtext("sectionid")
        if sid:
            sezioni[sid] = s.findtext("title") or ""
    attivita = {}
    for a in mb.iter("activity"):
        if not a.findtext("modulename"):               # elementi omonimi nelle impostazioni
            continue
        attivita.setdefault(a.findtext("sectionid"), []).append(
            (a.findtext("modulename"), a.findtext("title"), a.findtext("directory")))
    if not sezioni:                                     # backup di una singola attività
        for elenco in attivita.values():
            for mod, tit, _ in elenco:
                print("Attività: %-12s %s" % (mod, tit))
    for sid, titolo in sezioni.items():
        elenco = attivita.get(sid, [])
        print("== %s (%d attività)" % (titolo or "(senza titolo)", len(elenco)))
        for mod, tit, _ in elenco:
            print("   %-12s %s" % (mod, tit))
    return attivita


def leggi_domande(radice):
    """Restituisce (categorie, voci, tag): categorie id -> dati, voci id entry -> domanda
    (ultima versione, con il numero di versioni e i tag), tag id -> nome."""
    f = radice / "questions.xml"
    if not f.exists():
        return {}, {}, {}
    qx = ET.parse(f).getroot()
    categorie, voci, tag = {}, {}, {}
    for c in qx.iter("question_category"):
        cid = c.get("id")
        categorie[cid] = {"nome": c.findtext("name") or "", "padre": c.findtext("parent"),
                          "contesto": c.findtext("contextid"), "livello": c.findtext("contextlevel"),
                          "domande": []}
        for e in c.iter("question_bank_entry"):
            versioni = []
            for v in e.iter("question_versions"):
                for q in v.iter("question"):
                    versioni.append((int(v.findtext("version") or 0), q))
            if not versioni:
                continue
            _, q = max(versioni, key=lambda x: x[0])
            tq = []
            for t in q.iter("tag"):
                nome = t.findtext("rawname") or t.findtext("name") or ""
                tag[t.get("id")] = nome
                tq.append(nome)
            d = {"nome": q.findtext("name") or "", "tipo": q.findtext("qtype") or "",
                 "testo": q.findtext("questiontext") or "", "categoria": cid,
                 "versioni": len(versioni), "ultima": max(x[0] for x in versioni), "tag": tq}
            voci[e.get("id")] = d
            categorie[cid]["domande"].append(d)
        # backup più vecchi (prima di Moodle 4): domande direttamente nella categoria
        if not categorie[cid]["domande"]:
            for q in c.iter("question"):
                d = {"nome": q.findtext("name") or "", "tipo": q.findtext("qtype") or "",
                     "testo": q.findtext("questiontext") or "", "categoria": cid,
                     "versioni": 1, "ultima": 1, "tag": []}
                categorie[cid]["domande"].append(d)
    return categorie, voci, tag


def percorso(categorie, cid):
    parti, visti = [], set()
    while cid in categorie and cid not in visti:
        visti.add(cid)
        parti.append(categorie[cid]["nome"])
        cid = categorie[cid]["padre"]
    return "/".join(reversed(parti))


def banche(categorie):
    print("\n== Banche delle domande")
    for cid, c in categorie.items():
        if not c["domande"]:
            continue
        tipi = {}
        for d in c["domande"]:
            tipi[d["tipo"]] = tipi.get(d["tipo"], 0) + 1
        print("   %-60s %3d  (%s)" % (percorso(categorie, cid)[:60], len(c["domande"]),
                                       ", ".join("%s %d" % kv for kv in sorted(tipi.items()))))


def elenca_domande(categorie, filtro):
    for cid, c in categorie.items():
        p = percorso(categorie, cid)
        if filtro.lower() not in p.lower() or not c["domande"]:
            continue
        print("\n== %s" % p)
        for d in c["domande"]:
            print("\n-- [%s] %s\n%s" % (d["tipo"], d["nome"], testo_semplice(d["testo"], 600)))


def numero(x):
    try:
        f = float(x)
    except (TypeError, ValueError):
        return x or "?"
    return ("%d" % f) if f == int(f) else ("%g" % f)


def descrivi_casuale(sref, categorie, voci, tag):
    """Testo per una domanda casuale: tag richiesti, categoria e quante domande corrispondono."""
    try:
        fc = json.loads(sref.findtext("filtercondition") or "{}")
    except ValueError:
        fc = {}
    filtro = fc.get("filter", {})
    tag_id = [str(v) for v in filtro.get("qtagids", {}).get("values", [])]
    cat = [str(v) for v in filtro.get("category", {}).get("values", [])]
    if not cat and fc.get("questioncategoryid"):          # formato di Moodle 4.0-4.2
        cat = [str(fc["questioncategoryid"])]
    sotto = filtro.get("category", {}).get("filteroptions", {}).get("includesubcategories",
                                                                     fc.get("includingsubcategories"))
    nomi_tag = [tag.get(t, "tag %s" % t) for t in tag_id]
    cat_ok = set(cat)
    if sotto:
        cambiato = True
        while cambiato:
            cambiato = False
            for cid, c in categorie.items():
                if c["padre"] in cat_ok and cid not in cat_ok:
                    cat_ok.add(cid)
                    cambiato = True
    cand = [d for d in voci.values() if (not cat or d["categoria"] in cat_ok)
            and all(n.lower() in [x.lower() for x in d["tag"]] for n in nomi_tag)]
    dove = ", ".join(percorso(categorie, c) if c in categorie else "categoria %s (non nel backup)" % c
                     for c in cat) or "?"
    return "CASUALE tag %s da %s%s: %d domande (%s)" % (
        "+".join(nomi_tag) or "(nessuno)", dove, " e sottocategorie" if sotto else "", len(cand),
        ", ".join(d["nome"] + (" v%d" % d["ultima"] if d["versioni"] > 1 else "") for d in cand[:6]) + (" …" if len(cand) > 6 else ""))


def quiz(radice, attivita, categorie, voci, tag):
    """Per ogni quiz: impostazioni principali, sezioni, slot (pagina, punti, domanda)."""
    for elenco in attivita.values():
        for mod, titolo, cartella in elenco:
            if mod != "quiz" or not cartella:
                continue
            f = radice / cartella / "quiz.xml"
            if not f.exists():
                continue
            qz = ET.parse(f).getroot().find("quiz")
            tl = int(qz.findtext("timelimit") or 0)
            print("\n== Quiz: %s" % (qz.findtext("name") or titolo))
            print("   tempo %s, punteggio massimo %s, voto su %s, navigazione %s" % (
                ("%d min" % (tl // 60)) if tl else "illimitato", numero(qz.findtext("sumgrades")),
                numero(qz.findtext("grade")), qz.findtext("navmethod") or "?"))
            sezioni = {}
            for sz in qz.iter("section"):
                sezioni[int(sz.findtext("firstslot") or 0)] = (sz.findtext("heading") or "",
                                                              sz.findtext("shufflequestions") == "1")
            slot = sorted(qz.iter("question_instance"), key=lambda x: int(x.findtext("slot") or 0))
            totale = 0.0
            for sl in slot:
                n = int(sl.findtext("slot") or 0)
                if n in sezioni:
                    h, mescola = sezioni[n]
                    print("   -- sezione «%s»%s" % (h or "(senza titolo)", ", domande mescolate" if mescola else ""))
                punti = sl.findtext("maxmark")
                try:
                    totale += float(punti)
                except (TypeError, ValueError):
                    pass
                ref = sl.find(".//question_reference")
                sref = sl.find(".//question_set_reference")
                if ref is not None:
                    d = voci.get(ref.findtext("questionbankentryid"))
                    ver = ref.findtext("version")
                    ver = "sempre l'ultima" if ver in (None, "", "$@NULL@$") else "fissata alla v%s" % ver
                    if d:
                        c = categorie.get(d["categoria"], {})
                        desc = "[%s] %s (v%d di %d, %s)" % (d["tipo"], d["nome"], d["ultima"],
                                                                  d["versioni"], ver)
                        if c.get("contesto") and c.get("livello") == "70":
                            desc += " dalla banca %s" % percorso(categorie, d["categoria"])
                    else:
                        desc = "voce %s di un'altra banca (non nel backup)" % ref.findtext("questionbankentryid")
                elif sref is not None:
                    desc = descrivi_casuale(sref, categorie, voci, tag)
                else:                                   # backup prima di Moodle 4
                    desc = "domanda %s" % (sl.findtext("questionid") or "?")
                print("   %2d p.%-2s %5s pt  %s" % (n, sl.findtext("page") or "?", numero(punti), desc))
            print("   totale punti degli slot: %s" % numero(totale))


def banche_esterne(radice):
    """Banche (contesti) delle categorie che non appartengono alle attività del backup."""
    import xml.etree.ElementTree as ET
    mb = ET.parse(str(pathlib.Path(radice) / "moodle_backup.xml")).getroot()
    # le banche dei quiz del backup non contano; contano le banche esterne e le attività «Banca delle domande» (qbank)
    att = [a for a in mb.iter("activity") if a.findtext("moduleid")]
    propri = {a.findtext("moduleid") for a in att if a.findtext("modulename") != "qbank"}
    titoli_qbank = {a.findtext("moduleid"): a.findtext("title") for a in att if a.findtext("modulename") == "qbank"}
    cats = []
    for c in ET.parse(str(pathlib.Path(radice) / "questions.xml")).getroot().iter("question_category"):
        cats.append({"id": int(c.get("id")), "nome": c.findtext("name") or "", "ctx": c.findtext("contextid"),
                     "livello": c.findtext("contextlevel"), "modulo": c.findtext("contextinstanceid"),
                     "stamp": c.findtext("stamp") or "", "parent": c.findtext("parent"),
                     "domande": len(list(c.iter("question_bank_entry")))})
    per = {}
    for c in cats:
        per.setdefault(c["ctx"], []).append(c)
    trovate = 0
    for ctx, cs in per.items():
        if cs[0]["modulo"] in propri:
            continue
        trovate += 1
        top = next((c for c in cs if c["parent"] == "0"), None)
        tit = titoli_qbank.get(cs[0]["modulo"])
        print("== Banca%s: contesto %s, modulo %s (livello %s)" % (" «%s» (attività del backup)" % tit if tit else "",
                                                                  ctx, cs[0]["modulo"], cs[0]["livello"]))
        for c in cs:
            print("   categoria %d «%s», %d domande, stamp %s" % (c["id"], c["nome"], c["domande"], c["stamp"]))
        if top:
            print('   "banca": %s' % json.dumps({"contextid": int(ctx), "cmid": int(cs[0]["modulo"]),
                                                  "top_id": top["id"], "top_stamp": top["stamp"]}, ensure_ascii=False))
            for c in cs:
                if c is not top:
                    print('   per la categoria «%s»: "categoria_id": %d, "categoria_stamp": "%s"' % (c["nome"], c["id"], c["stamp"]))
    if not trovate:
        print("Nessuna banca fuori dalle attività del backup: le domande stanno tutte nelle banche dei quiz.")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    mbz = args[0]
    if "--estrai" in args:
        dest = args[args.index("--estrai") + 1]
        estrai(mbz, dest)
        print("Estratto in %s" % dest)
        return
    with tempfile.TemporaryDirectory() as tmp:
        radice = estrai(mbz, tmp)
        categorie, voci, tag = leggi_domande(radice)
        if "--domande" in args:
            elenca_domande(categorie, args[args.index("--domande") + 1])
        elif "--banche" in args:
            banche_esterne(radice)
        elif "--quiz" in args:
            attivita = struttura(radice)
            quiz(radice, attivita, categorie, voci, tag)
        else:
            struttura(radice)
            banche(categorie)


if __name__ == "__main__":
    main()
