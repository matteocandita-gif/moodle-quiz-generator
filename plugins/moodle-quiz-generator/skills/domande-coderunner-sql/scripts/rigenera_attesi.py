#!/usr/bin/env python3
"""Converte le domande CodeRunner SQL di un export Moodle (prototipi sql e
sql_foreignkeys, con o senza template copiato) al prototipo sql_salvemini e
ricalcola gli output attesi con l'emulatore di SQLite 3.46.

Uso:
    python3 rigenera_attesi.py EXPORT.xml USCITA.xml [--prefisso "Rigenerate"]

- Le domande diventano sql_salvemini e ereditano template e impostazioni dal
  prototipo (il template copiato viene tolto). Le chiavi esterne restano come
  prima: attive per sql_foreignkeys o template con PRAGMA foreign_keys, spente
  per sql (parametro {"foreign_keys": false}). columnwidths viene tolto: con il
  nuovo SQLite le colonne si allargano da sole.
- I test di tipo precheck restano tali; il grader della domanda resta se era
  NearEqualityGrader o RegexGrader (con RegexGrader gli attesi non si toccano).
- L'interfaccia della domanda (uiplugin, per esempio scratchpad) resta com'era.
- Con --prefisso le categorie diventano $module$/top/PREFISSO/..., così l'import
  non mescola le domande nuove con le vecchie.
Le altre domande del file restano com'erano. Alla fine stampa un resoconto con
le domande da controllare a mano.
"""
import base64
import pathlib
import sys
import tempfile
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import emula_sqlite as em  # noqa: E402

DA_SVUOTARE = ["template", "iscombinatortemplate", "allowmultiplestdins", "testsplitterre",
               "language", "acelang", "sandbox", "cputimelimitsecs", "memlimitmb",
               "sandboxparams", "useace", "resultcolumns"]


def imposta(q, tag, valore):
    el = q.find(tag)
    if el is None:
        el = ET.SubElement(q, tag)
    el.text = valore


def main():
    args = sys.argv[1:]
    prefisso = None
    if "--prefisso" in args:
        i = args.index("--prefisso")
        prefisso = args[i + 1].strip("/")
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__)
        sys.exit(2)
    albero = ET.parse(args[0])
    radice = albero.getroot()
    tmp = pathlib.Path(tempfile.mkdtemp())
    ok, controllare, categoria = 0, [], ""
    for q in radice.findall("question"):
        if q.get("type") == "category":
            el = q.find("category/text")
            categoria = el.text or ""
            if prefisso and categoria.startswith("$module$/top"):
                resto = categoria[len("$module$/top"):]
                el.text = "$module$/top/" + prefisso + resto
            continue
        if q.get("type") != "coderunner":
            continue
        tipo = q.findtext("coderunnertype")
        if tipo not in ("sql", "sql_foreignkeys", "sql_salvemini"):
            continue
        nome = (q.findtext("name/text") or "").strip()
        problemi = []
        risposta = q.findtext("answer") or ""
        tc = q.find("testcases")
        db = [f for f in tc.findall("file") if (f.get("name") or "").endswith(".db")] if tc is not None else []
        if not risposta.strip():
            problemi.append("nessuna soluzione: output non calcolabili")
        if not db:
            problemi.append("nessun database allegato")
        if problemi:
            controllare.append((categoria, nome, problemi))
            continue
        template = q.findtext("template") or ""
        params = (q.findtext("templateparams") or "").strip()
        if tipo == "sql_salvemini":
            fk = '"foreign_keys": false' not in params.replace(" ", "").replace(":", ": ")
        else:
            fk = tipo == "sql_foreignkeys" or "foreign_keys = ON" in template
        grader = q.findtext("grader") or ""
        regex = grader == "RegexGrader"

        percorso = tmp / ("q%d.db" % ok)
        percorso.write_bytes(base64.b64decode(db[0].text or ""))
        risposta_c = em.chiudi_risposta(risposta)
        for n, t in enumerate(tc.findall("testcase"), 1):
            precheck = t.get("testtype") == "1"
            codice = t.findtext("testcode/text") or ""
            extra = t.findtext("extra/text") or ""
            if regex:
                continue
            try:
                righe, err = em.esegui(str(percorso), risposta_c if precheck else
                                       "\n".join([extra, risposta_c, codice]), fk)
            except ValueError as ex:
                problemi.append("test %d: %s" % (n, ex))
                continue
            nuovo = em.formatta_test(righe, err, precheck)
            el = t.find("expected/text")
            if el is None:
                el = ET.SubElement(ET.SubElement(t, "expected"), "text")
            el.text = nuovo
            if err:
                problemi.append("test %d: la soluzione produce %s" % (n, "; ".join(
                    "ERRORE: " + e for e in err)))
            elif not precheck and not righe:
                problemi.append("test %d: output vuoto" % n)
        imposta(q, "coderunnertype", "sql_salvemini")
        imposta(q, "prototypetype", "0")
        for tag in DA_SVUOTARE:
            if q.find(tag) is not None:
                imposta(q, tag, "")
        imposta(q, "grader", grader if grader in ("NearEqualityGrader", "RegexGrader") else "")
        nuovi = "" if fk else '{"foreign_keys": false}'
        imposta(q, "templateparams", nuovi)
        imposta(q, "templateparamsevald", nuovi or "{}")
        if regex:
            problemi.append("RegexGrader: attesi lasciati com'erano")
        ok += 1
        if problemi:
            controllare.append((categoria, nome, problemi))

    albero.write(args[1], encoding="UTF-8", xml_declaration=True)
    print("Domande SQL convertite: %d" % ok)
    print("Da controllare: %d\n" % len(controllare))
    ultima = None
    for cat, nome, prob in controllare:
        if cat != ultima:
            print("== %s" % cat)
            ultima = cat
        print("  %s" % nome)
        for p in prob:
            print("      - %s" % p)


if __name__ == "__main__":
    main()
