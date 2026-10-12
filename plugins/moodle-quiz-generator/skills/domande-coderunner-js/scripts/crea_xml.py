#!/usr/bin/env python3
"""Genera domande CodeRunner JavaScript (prototipi "Javascript (con prompt)" e
"Javascript (con gapfiller)") da una specifica.

Uso:
    python3 crea_xml.py SPECIFICA.txt USCITA.xml

Per ogni test lo script costruisce il programma come il template del prototipo,
lo esegue in Node con la soluzione e scrive l'output atteso. Controlla le regole
e segnala le trappole tra browser e Node. Formato: references/formato-specifica.md.
"""
import json
import pathlib
import re
import sys
import xml.dom.minidom

QUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import esegui_js as ej  # noqa: E402
import moodle_lib as ml  # noqa: E402

TIPI = {"prompt": "Javascript (con prompt)", "gapfiller": "Javascript (con gapfiller)"}
OPZIONI = {"test_prima": "0", "random": "", "allornothing": "1", "defaultgrade": "1",
           "penalty": "0", "esempi": "primo", "answerboxlines": "18", "hidecheck": "0"}


class Domanda:
    def __init__(self, tipo, categoria):
        self.tipo, self.categoria = tipo, categoria
        self.campi, self.opzioni, self.test = {}, dict(OPZIONI), []


def leggi(testo):
    testo = testo.replace("\r\n", "\n")
    domande, errori = [], []
    categoria, corrente, sezione, righe = None, None, None, []

    def chiudi():
        nonlocal sezione, righe, categoria
        if sezione is None:
            return
        c = "\n".join(righe).strip("\n")
        nome, _, arg = sezione.partition(" ")
        if nome == "category":
            categoria = ml.percorso_categoria(c)
        elif corrente is None:
            errori.append("sezione '%s' prima di '=== question'" % nome)
        elif nome in ("name", "questiontext", "preload", "answer", "code", "generalfeedback"):
            corrente.campi[nome] = c
        elif nome == "note":
            pass
        elif nome == "options":
            for r in c.splitlines():
                if r.strip():
                    k, _, v = r.partition(":")
                    if k.strip() not in OPZIONI:
                        errori.append("%s: opzione sconosciuta '%s'"
                                      % (corrente.campi.get("name", "?"), k.strip()))
                    corrente.opzioni[k.strip()] = v.strip()
        elif nome == "test":
            corrente.test.append({"codice": c, "stdin": "", "extra": "",
                                  "nascosto": "HIDE" in arg.upper(), "atteso": None})
        elif nome in ("stdin", "extra", "expected"):
            if not corrente.test:
                errori.append("%s: '=== %s' senza un test prima" % (corrente.campi.get("name", "?"), nome))
            else:
                corrente.test[-1]["atteso" if nome == "expected" else nome] = c
        else:
            errori.append("sezione sconosciuta: '%s'" % nome)
        sezione, righe = None, []

    for r in testo.split("\n"):
        if r.startswith("=== "):
            chiudi()
            intest = r[4:].strip()
            if intest == "question" or intest.startswith("question "):
                tipo = intest[len("question"):].strip()
                if tipo not in TIPI:
                    errori.append("tipo di domanda '%s': usa 'question prompt' o 'question gapfiller'" % tipo)
                    tipo = "prompt"
                corrente = Domanda(tipo, categoria)
                domande.append(corrente)
            else:
                sezione = intest
        else:
            righe.append(r)
    chiudi()
    return domande, errori


def parametri(d):
    p = {}
    if d.opzioni["test_prima"] == "1":
        p["test_prima"] = True
    if d.opzioni["random"].strip():
        p["random"] = [float(x) for x in re.split(r"[,\s]+", d.opzioni["random"].strip(" []")) if x]
    return p


def _t(tag, contenuto):
    return "    <%s>%s</%s>\n" % (tag, ml.cdata(contenuto) if contenuto else "", tag)


def genera(d):
    o, p = d.opzioni, parametri(d)
    pj = json.dumps(p) if p else ""
    risposta = (json.dumps(d.risposte, ensure_ascii=False) if d.tipo == "gapfiller"
                else d.campi["answer"])
    x = ['  <question type="coderunner">\n',
         "    <name>\n      <text>%s</text>\n    </name>\n" % ml.esc_xml(d.campi["name"]),
         '    <questiontext format="html">\n      <text>%s</text>\n    </questiontext>\n'
         % ml.cdata(d.campi["questiontext"]),
         '    <generalfeedback format="html">\n      <text>%s</text>\n    </generalfeedback>\n'
         % (ml.cdata(d.campi["generalfeedback"]) if d.campi.get("generalfeedback") else ""),
         "    <defaultgrade>%s</defaultgrade>\n    <penalty>%s</penalty>\n" % (o["defaultgrade"], o["penalty"]),
         "    <hidden>0</hidden>\n    <idnumber></idnumber>\n",
         "    <coderunnertype>%s</coderunnertype>\n    <prototypetype>0</prototypetype>\n" % TIPI[d.tipo],
         "    <allornothing>%s</allornothing>\n    <penaltyregime>0</penaltyregime>\n" % o["allornothing"],
         "    <precheck>0</precheck>\n    <hidecheck>%s</hidecheck>\n    <showsource>0</showsource>\n" % o["hidecheck"],
         "    <answerboxlines>%s</answerboxlines>\n    <answerboxcolumns>100</answerboxcolumns>\n" % o["answerboxlines"],
         _t("answerpreload", d.campi.get("preload", "")),
         _t("globalextra", d.campi.get("code", "") if d.tipo == "gapfiller" else ""),
         "    <useace></useace>\n    <resultcolumns></resultcolumns>\n    <template></template>\n",
         "    <iscombinatortemplate></iscombinatortemplate>\n    <allowmultiplestdins></allowmultiplestdins>\n",
         _t("answer", risposta),
         "    <validateonsave>1</validateonsave>\n    <testsplitterre></testsplitterre>\n",
         "    <language></language>\n    <acelang></acelang>\n    <sandbox></sandbox>\n    <grader></grader>\n",
         "    <cputimelimitsecs></cputimelimitsecs>\n    <memlimitmb></memlimitmb>\n    <sandboxparams></sandboxparams>\n",
         "    <templateparams>%s</templateparams>\n" % ml.esc_xml(pj),
         "    <hoisttemplateparams>1</hoisttemplateparams>\n    <extractcodefromjson>1</extractcodefromjson>\n",
         "    <templateparamslang>None</templateparamslang>\n    <templateparamsevalpertry>0</templateparamsevalpertry>\n",
         "    <templateparamsevald>%s</templateparamsevald>\n" % ml.esc_xml(pj or "{}"),
         "    <twigall>0</twigall>\n    <uiplugin></uiplugin>\n    <uiparameters></uiparameters>\n",
         "    <attachments>0</attachments>\n    <attachmentsrequired>0</attachmentsrequired>\n",
         "    <maxfilesize>10240</maxfilesize>\n    <filenamesregex></filenamesregex>\n    <filenamesexplain></filenamesexplain>\n",
         "    <displayfeedback>1</displayfeedback>\n    <giveupallowed>0</giveupallowed>\n    <prototypeextra></prototypeextra>\n",
         "    <testcases>\n"]
    for n, t in enumerate(d.test):
        esempio = (not t["nascosto"]) and (o["esempi"] == "tutti" or (o["esempi"] == "primo" and n == 0))
        x.append('      <testcase testtype="0" useasexample="%d" hiderestiffail="0" mark="1.0000000" >\n' % esempio)
        for tag, val in (("testcode", t["codice"]), ("stdin", t["stdin"]), ("expected", t["atteso"]),
                         ("extra", t["extra"])):
            x.append("      <%s>\n        <text>%s</text>\n      </%s>\n" % (tag, ml.cdata(val) if val else "", tag))
        x.append("      <display>\n        <text>%s</text>\n      </display>\n    </testcase>\n"
                 % ("HIDE" if t["nascosto"] else "SHOW"))
    x.append("    </testcases>\n  </question>\n\n")
    return "".join(x)


def esegui_test(d, t, codice_risposta=None):
    p = parametri(d)
    if d.tipo == "prompt":
        prog = ej.programma_prompt(codice_risposta if codice_risposta is not None else d.campi["answer"],
                                   t["codice"], t["stdin"], t["extra"], p.get("random"), p.get("test_prima", False))
    else:
        prog = ej.programma_gapfiller(d.campi["code"], d.risposte,
                                      {"testcode": t["codice"], "stdin": t["stdin"], "extra": t["extra"]},
                                      p.get("random"))
    return ej.esegui(prog)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    domande, errori = leggi(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    pezzi, nomi, cat = [], {}, object()
    for d in domande:
        nome = d.campi.get("name", "").strip() or "(senza nome)"
        nomi[nome] = nomi.get(nome, 0) + 1
        avvisa = lambda m: print("AVVISO  %s: %s" % (nome, m))
        richieste = ["name", "questiontext", "answer"] + (["code"] if d.tipo == "gapfiller" else [])
        mancanti = [s for s in richieste if not d.campi.get(s, "").strip()]
        if mancanti:
            errori.append("%s: mancano %s" % (nome, ", ".join(mancanti)))
            continue
        if not d.test:
            errori.append("%s: nessun test" % nome)
            continue
        d.campi["name"] = nome
        d.campi["questiontext"] = ml.espandi_codice(d.campi["questiontext"])
        e, a = ml.controlla_html(d.campi["questiontext"], "coderunner")
        errori += ["%s: %s" % (nome, x) for x in e]
        for x in a:
            avvisa(x)
        if d.tipo == "gapfiller":
            d.risposte = d.campi["answer"].split("\n")
            if d.opzioni["test_prima"] == "1":
                errori.append("%s: test_prima non vale per il gapfiller (il test gira già prima)" % nome)
            ng = ej.conta_gap(d.campi["code"])
            if ng != len(d.risposte):
                errori.append("%s: %d spazi {[…]} nel codice ma %d risposte (una per riga)"
                              % (nome, ng, len(d.risposte)))
                continue
        sorgente = d.campi.get("code", "") if d.tipo == "gapfiller" else d.campi["answer"]
        if re.search(r"\balert\s*\(|\bdocument\.", sorgente):
            errori.append("%s: alert e document non esistono in Node: usa console.log" % nome)
            continue
        if d.opzioni["random"].strip():
            try:
                parametri(d)
            except ValueError:
                errori.append("%s: 'random' deve essere un elenco di numeri" % nome)
                continue
        uscite = []
        for n, t in enumerate(d.test, 1):
            if t["extra"].strip() and not re.fullmatch(r"\d+", t["extra"].strip()):
                errori.append("%s, test %d: Extra deve essere un numero intero (posizione nella sequenza random)" % (nome, n))
                continue
            if not t["codice"].strip():
                avvisa("test %d senza codice: per convenzione inizia con un commento che descrive il caso" % n)
            r = esegui_test(d, t)
            if r["timeout"]:
                errori.append("%s, test %d: il programma non termina (ciclo infinito? lo standard input "
                              "contiene il valore che ferma il ciclo?)" % (nome, n))
                continue
            if r["errore"]:
                errori.append("%s, test %d: la soluzione dà errore: %s" % (nome, n, r["errore"]))
                continue
            if r["prompt_oltre"]:
                avvisa("test %d: il programma chiede più input di quelli nello standard input "
                       "(prompt ha restituito undefined)" % n)
            if r["random_ricomincia"]:
                avvisa("test %d: la sequenza random è finita e ricomincia dall'inizio" % n)
            out = r["output"]
            if not out.strip():
                avvisa("test %d: output vuoto" % n)
            if re.search(r"^\[ .* \]$|^\[\]$", out, re.M):
                avvisa("test %d: un array stampato con console.log: Node lo scrive '[ 1, 2, 3 ]', "
                       "diverso dal browser; meglio un ciclo o join()" % n)
            lungo = re.search(r"\d+\.\d{10,}", out)
            if lungo:
                avvisa("test %d: un decimale con molte cifre (%s): valuta toFixed()" % (n, lungo.group(0)))
            if t["atteso"] is not None and t["atteso"].strip() != out.strip():
                avvisa("test %d: l'output scritto a mano è diverso da quello calcolato, uso quello "
                       "calcolato:\n%s" % (n, out))
            t["atteso"] = out
            uscite.append(re.sub(r"\s+", " ", out.lower()).strip())
        if len(uscite) > 1 and len(set(uscite)) == 1:
            avvisa("tutti i test hanno lo stesso output: non distinguono una soluzione giusta da una "
                   "che stampa sempre la stessa cosa")
        if d.tipo == "prompt" and d.campi.get("preload", "").strip():
            r = esegui_test(d, d.test[0], codice_risposta=d.campi["preload"])
            primo = (r["errore"] or ("non termina" if r["timeout"] else None)
                     or (r["output"].strip().splitlines() or ["(nessun output)"])[0])
            print("PRELOAD %s: con il codice di partenza e il primo test lo studente vede: %s" % (nome, primo))
        if d.categoria != cat:
            if d.categoria:
                pezzi.append(ml.xml_categoria(d.categoria))
            cat = d.categoria
        if not any(e.startswith(nome + ":") or e.startswith(nome + ",") for e in errori):
            pezzi.append(genera(d))
    for n, c in nomi.items():
        if c > 1:
            errori.append("nome ripetuto %d volte: %s" % (c, n))
    if errori:
        print("\nERRORI (XML non generato):")
        for e in errori:
            print("  - " + e)
        sys.exit(1)
    testo = '<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n' + "".join(pezzi) + "</quiz>\n"
    xml.dom.minidom.parseString(testo.encode("utf-8"))
    pathlib.Path(sys.argv[2]).write_text(testo, encoding="utf-8")
    print("\nOK: %d domande -> %s" % (len(domande), sys.argv[2]))


if __name__ == "__main__":
    main()
