#!/usr/bin/env python3
"""Crea la copia PDP di una verifica dal suo backup Moodle (.mbz).

Uso:
    python3 crea_pdp.py --prepara-banca BANCA_QBANK.mbz BANCA_PDP.json
        legge il backup dell'attività «Banca delle domande» con le descrizioni di riduzione e le
        dichiarazioni (es. «Domande per riduzione PDP - DSA») e scrive i dati che servono alla copia:
        contesto e categorie della banca, e le domande così come stanno nel backup (con i loro stamp)

    python3 crea_pdp.py VERIFICA.mbz BANCA_PDP.json USCITA.mbz --togli=T2,Q1 [--pei]
                        [--dichiarazione=mappe|tempo|generica|nessuna] [--nome="..."]
        VERIFICA.mbz   backup della verifica della classe così com'è in Moodle
        --togli        domande da togliere: numeri di slot (come li stampa leggi_mbz.py --quiz) o codici
                       di posizione (T2, Q1…: cercati nel nome delle domande e nei tag delle casuali)
        --pei          descrizioni «Riduzione contenuti PEI -k» invece di «PDP -k»
        --dichiarazione  domanda aperta a 0 punti in apertura, su una pagina sua (predefinita «mappe»:
                       «Dichiarazione - Solo mappe concettuali»)

La copia ha lo stesso contenuto della verifica: le domande tolte restano a 0 punti e, sulla stessa
pagina e subito prima di ciascuna, c'è una descrizione «Riduzione contenuti PDP -k» diversa (un quiz
non può usare due volte la stessa domanda). In apertura la dichiarazione. Le descrizioni e la
dichiarazione restano quelle della banca condivisa (stessi stamp): al ripristino Moodle le riusa, come
riusa le domande della verifica, anche da un corso diverso da quello delle banche (verificato con un
ripristino reale il 25/10/2026). Il backup viene riscritto come lo scrive Moodle (riconfeziona).
"""
import io
import json
import os
import re
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET

NULL = "$@NULL@$"
DICHIARAZIONI = {"mappe": "Dichiarazione - Solo mappe concettuali", "tempo": "Dichiarazione - Tempo aggiuntivo e mappe",
                 "generica": "Dichiarazione - Generica", "nessuna": None}


def estrai(mbz, d):
    with tarfile.open(mbz) as t:
        for m in t.getmembers():
            n = os.path.normpath(m.name)
            if n.startswith("..") or os.path.isabs(n) or m.issym() or m.islnk():
                raise SystemExit("ERRORE: voce sospetta nel backup: %s" % m.name)
        try:
            t.extractall(d, filter="data")
        except TypeError:                     # Python senza filtri di estrazione
            t.extractall(d)


def riconfeziona(d, out):
    """Archivio come quello di Moodle: .ARCHIVE_INDEX per primo, intestazioni USTAR senza PAX
    (una voce in più blocca il ripristino con «progress() value out of range»)."""
    righe = open(os.path.join(d, ".ARCHIVE_INDEX"), encoding="utf-8").read().split("\n")
    testa, voci = righe[0], [r for r in righe[1:] if r.strip()]
    nuove = []
    for r in voci:
        c = r.split("\t")
        if c[1] == "f":
            c[2] = str(os.path.getsize(os.path.join(d, c[0])))
        nuove.append(c)
    indice = testa.split("Count:")[0] + "Count: %d\n" % len(nuove) + "".join("\t".join(c) + "\n" for c in nuove)
    with tarfile.open(out, "w:gz", format=tarfile.USTAR_FORMAT) as t:
        def agg(nome, dati=None):
            ti = tarfile.TarInfo(nome.rstrip("/"))
            ti.mtime, ti.uid, ti.gid, ti.uname, ti.gname = 1792876430, 0, 0, "", ""
            if dati is None:
                ti.type, ti.mode, ti.size = tarfile.DIRTYPE, 0o755, 0
                t.addfile(ti)
            else:
                ti.mode, ti.size = 0o644, len(dati)
                t.addfile(ti, io.BytesIO(dati))
        agg(".ARCHIVE_INDEX", indice.encode("utf-8"))
        for c in nuove:
            agg(c[0], None if c[1] == "d" else open(os.path.join(d, c[0]), "rb").read())


def scrivi_xml(radice, percorso):
    ET.ElementTree(radice).write(percorso, encoding="UTF-8", xml_declaration=True)


# ------------------------------------------------------------------ banca PDP

def prepara_banca(mbz, out):
    with tempfile.TemporaryDirectory() as d:
        estrai(mbz, d)
        r = ET.parse(os.path.join(d, "questions.xml")).getroot()
        cats = list(r.iter("question_category"))
        dati = None
        for c in cats:
            voci = {}
            for e in c.findall("question_bank_entries/question_bank_entry"):
                vs = sorted(e.iter("question_versions"), key=lambda v: int(v.findtext("version") or 0))
                nome = vs[-1].find(".//question").findtext("name") or ""
                if nome.startswith("Riduzione contenuti") or nome.startswith("Dichiarazione"):
                    voci[nome] = ET.tostring(e, encoding="unicode")
            if not voci:
                continue
            top = next(x for x in cats if x.get("id") == c.findtext("parent")) if c.findtext("parent") != "0" else c
            mb = ET.parse(os.path.join(d, "moodle_backup.xml")).getroot()
            dati = {"banca": {"nome": next((a.findtext("title") for a in mb.iter("activity")
                                            if a.findtext("moduleid") == c.findtext("contextinstanceid")), ""),
                              "corso": mb.findtext(".//original_course_fullname") or "",
                              "contextid": int(c.findtext("contextid")), "cmid": int(c.findtext("contextinstanceid")),
                              "top_id": int(top.get("id")), "top_stamp": top.findtext("stamp"),
                              "categoria_id": int(c.get("id")), "categoria_nome": c.findtext("name"),
                              "categoria_stamp": c.findtext("stamp")},
                    "domande": voci}
            break
        if not dati:
            raise SystemExit("ERRORE: nel backup non trovo domande «Riduzione contenuti…» o «Dichiarazione…»")
    json.dump(dati, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK: banca «%s» (corso «%s»), %d domande -> %s" % (dati["banca"]["nome"], dati["banca"]["corso"],
                                                         len(dati["domande"]), out))
    print("    " + ", ".join(sorted(dati["domande"])))


def leggi_banca(p):
    d = json.load(open(p, encoding="utf-8"))
    return d.get("data", d)


# ------------------------------------------------------------------ copia PDP

def etichette_slot(qi, voci_nome):
    """Testi su cui cercare i codici di posizione: nome della domanda fissa o tag della casuale."""
    et = []
    ref = qi.find("question_reference")
    if ref is not None:
        et.append(voci_nome.get(ref.findtext("questionbankentryid"), ""))
    sref = qi.find("question_set_reference")
    if sref is not None:
        et.append(sref.findtext("filtercondition") or "")
    return et


def corrisponde(codice, testi, tag_nomi):
    c = re.escape(codice.strip())
    for t in testi:
        if re.search(r"(^|\s-\s)%s[a-z]?(\s-\s|$)" % c, t, re.I):
            return True
        for tid in re.findall(r'"qtagids".*?"values":\[([^\]]*)\]', t):
            for x in re.findall(r'"?(\d+)"?', tid):
                if re.search(r"(^|-)%s(-|$)" % c, tag_nomi.get(x, ""), re.I):
                    return True
    return False


def crea_copia(mbz, banca_json, out, togli, pei=False, dich="mappe", nome=None):
    B = leggi_banca(banca_json)
    pref = "Riduzione contenuti PEI -" if pei else "Riduzione contenuti PDP -"
    descr = sorted([n for n in B["domande"] if n.startswith(pref)], key=lambda n: int(n.rsplit("-", 1)[1]))
    nome_dich = DICHIARAZIONI[dich]
    if nome_dich and nome_dich not in B["domande"]:
        raise SystemExit("ERRORE: nella banca non c'è «%s»" % nome_dich)
    with tempfile.TemporaryDirectory() as d:
        estrai(mbz, d)
        qx = os.path.join(d, "questions.xml")
        qroot = ET.parse(qx).getroot()
        voci_nome = {}
        for e in qroot.iter("question_bank_entry"):
            vs = sorted(e.iter("question_versions"), key=lambda v: int(v.findtext("version") or 0))
            if vs:
                voci_nome[e.get("id")] = vs[-1].find(".//question").findtext("name") or ""
        tag_nomi = {t.get("id"): t.findtext("rawname") or t.findtext("name") or "" for t in qroot.iter("tag") if t.get("id")}
        quiz_xml = next(os.path.join(d, "activities", x, "quiz.xml") for x in os.listdir(os.path.join(d, "activities"))
                        if x.startswith("quiz_"))
        act = ET.parse(quiz_xml)
        quiz = act.getroot().find("quiz")
        qis = quiz.find("question_instances")
        slots = sorted(qis.findall("question_instance"), key=lambda q: int(q.findtext("slot")))
        # domande da togliere
        da_togliere = set()
        for t in [x.strip() for x in togli.split(",") if x.strip()]:
            if t.isdigit():
                if not 1 <= int(t) <= len(slots):
                    raise SystemExit("ERRORE: lo slot %s non esiste (la verifica ne ha %d)" % (t, len(slots)))
                da_togliere.add(int(t))
            else:
                trovati = [int(q.findtext("slot")) for q in slots if corrisponde(t, etichette_slot(q, voci_nome), tag_nomi)]
                if len(trovati) != 1:
                    raise SystemExit("ERRORE: il codice %s corrisponde a %d slot (%s): usa il numero dello slot"
                                     % (t, len(trovati), trovati))
                da_togliere.add(trovati[0])
        if len(da_togliere) > len(descr):
            raise SystemExit("ERRORE: %d domande da togliere ma solo %d descrizioni «%sk» nella banca"
                             % (len(da_togliere), len(descr), pref))
        # nuova sequenza degli slot
        ctx = next((q.find(x).findtext("usingcontextid") for q in slots for x in ("question_reference", "question_set_reference")
                    if q.find(x) is not None), None)
        quizid = slots[0].findtext("quizid")
        nid = [max(int(e.get("id")) for e in act.getroot().iter() if e.get("id") and e.get("id").isdigit() and
                   e.tag in ("question_instance", "question_reference", "question_set_reference"))]

        def nuovo_slot(entry_id, pagina):
            nid[0] += 1
            qi = ET.Element("question_instance", id=str(nid[0]))
            for tag, val in (("quizid", quizid), ("slot", "0"), ("page", str(pagina)), ("displaynumber", NULL),
                             ("requireprevious", "0"), ("maxmark", "0.0000000"), ("quizgradeitemid", NULL)):
                ET.SubElement(qi, tag).text = val
            nid[0] += 1
            ref = ET.SubElement(qi, "question_reference", id=str(nid[0]))
            for tag, val in (("usingcontextid", ctx), ("component", "mod_quiz"), ("questionarea", "slot"),
                             ("questionbankentryid", str(entry_id)), ("version", NULL)):
                ET.SubElement(ref, tag).text = val
            return qi

        entry_di = {}
        for n, xml in B["domande"].items():
            entry_di[n] = ET.fromstring(xml).get("id")
        spost = 1 if nome_dich else 0
        nuovi, origine, usate = [], {}, []
        if nome_dich:
            nuovi.append(nuovo_slot(entry_di[nome_dich], 1))
            usate.append(nome_dich)
        k = 0
        for q in slots:
            s, p = int(q.findtext("slot")), int(q.findtext("page")) + spost
            if s in da_togliere:
                nuovi.append(nuovo_slot(entry_di[descr[k]], p))
                origine[id(nuovi[-1])] = s
                usate.append(descr[k])
                k += 1
                q.find("maxmark").text = "0.0000000"
            q.find("page").text = str(p)
            origine[id(q)] = s
            nuovi.append(q)
        for q in list(qis):
            qis.remove(q)
        nuovo_numero = {}
        for i, q in enumerate(nuovi, 1):
            q.find("slot").text = str(i)
            qis.append(q)
            s = origine.get(id(q))
            if s is not None and s not in nuovo_numero:
                nuovo_numero[s] = i          # la descrizione prima della domanda tolta apre la sua sezione
        for sez in quiz.findall("sections/section"):
            fs = int(sez.findtext("firstslot"))
            sez.find("firstslot").text = "1" if fs == 1 else str(nuovo_numero[fs])
        somma = sum(float(q.findtext("maxmark")) for q in nuovi)
        quiz.find("sumgrades").text = "%.5f" % somma
        vecchio = quiz.findtext("name")
        nuovo_nome = nome or (vecchio + " (PDP)")
        quiz.find("name").text = nuovo_nome
        scrivi_xml(act.getroot(), quiz_xml)
        # nomi in moodle_backup.xml e nel registro dei voti
        for f in ("moodle_backup.xml", os.path.join(os.path.dirname(quiz_xml), "grades.xml")):
            p = os.path.join(d, f)
            if os.path.exists(p):
                s = open(p, encoding="utf-8").read()
                s = s.replace(">%s<" % escape_xml(vecchio), ">%s<" % escape_xml(nuovo_nome))
                open(p, "w", encoding="utf-8").write(s)
        # domande della banca PDP in questions.xml, con i loro stamp
        b = B["banca"]
        cats = {c.get("id"): c for c in qroot.iter("question_category")}

        def categoria(cid, nome_c, parent, stamp, ordine):
            if str(cid) in cats:
                return cats[str(cid)]
            c = ET.SubElement(qroot, "question_category", id=str(cid))
            for tag, val in (("name", nome_c), ("contextid", str(b["contextid"])), ("contextlevel", "70"),
                             ("contextinstanceid", str(b["cmid"])), ("info", ""), ("infoformat", "1"), ("stamp", stamp),
                             ("parent", str(parent)), ("sortorder", str(ordine)), ("idnumber", NULL)):
                ET.SubElement(c, tag).text = val
            ET.SubElement(c, "question_bank_entries")
            cats[str(cid)] = c
            return c
        categoria(b["top_id"], "top", 0, b["top_stamp"], 0)
        cat = categoria(b["categoria_id"], b["categoria_nome"], b["top_id"], b["categoria_stamp"], 999)
        if cats[str(b["categoria_id"])].findtext("stamp") != b["categoria_stamp"]:
            raise SystemExit("ERRORE: la categoria %s del backup non è quella della banca PDP" % b["categoria_id"])
        presenti = {e.get("id") for e in qroot.iter("question_bank_entry")}
        contenitore = cat.find("question_bank_entries")
        for n in usate:
            e = ET.fromstring(B["domande"][n])
            if e.get("id") in presenti:
                continue
            e.find("questioncategoryid").text = str(b["categoria_id"])
            contenitore.append(e)
        scrivi_xml(qroot, qx)
        # inforef del quiz: le categorie usate
        inf = os.path.join(os.path.dirname(quiz_xml), "inforef.xml")
        ir = ET.parse(inf).getroot()
        qcr = ir.find("question_categoryref")
        if qcr is None:
            qcr = ET.SubElement(ir, "question_categoryref")
        gia = {x.findtext("id") for x in qcr.iter("question_category")}
        for cid in (b["top_id"], b["categoria_id"]):
            if str(cid) not in gia:
                ET.SubElement(ET.SubElement(qcr, "question_category"), "id").text = str(cid)
        scrivi_xml(ir, inf)
        riconfeziona(d, out)
    print("OK: «%s», %d slot (%d tolte a 0 punti: slot originali %s), punteggio massimo %g -> %s"
          % (nuovo_nome, len(nuovi), len(da_togliere), ", ".join(str(x) for x in sorted(da_togliere)), somma, out))
    print("    aggiunte: " + ", ".join(usate))
    print("    ripristino: nel corso della verifica; descrizioni e domande della verifica vengono riusate")


def escape_xml(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    if a[0] == "--prepara-banca":
        if len(a) != 3:
            raise SystemExit(__doc__)
        return prepara_banca(a[1], a[2])
    pos = [x for x in a if not x.startswith("--")]
    opt = dict(x[2:].split("=", 1) if "=" in x else (x[2:], "1") for x in a if x.startswith("--"))
    if len(pos) != 3 or "togli" not in opt:
        raise SystemExit(__doc__)
    dich = opt.get("dichiarazione", "mappe")
    if dich not in DICHIARAZIONI:
        raise SystemExit("ERRORE: --dichiarazione può essere " + ", ".join(DICHIARAZIONI))
    crea_copia(pos[0], pos[1], pos[2], opt["togli"], pei="pei" in opt, dich=dich, nome=opt.get("nome"))


if __name__ == "__main__":
    main()
