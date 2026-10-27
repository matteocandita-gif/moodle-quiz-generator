#!/usr/bin/env python3
"""Genera un file Moodle XML da una specifica in testo semplice.

Uso:
    python3 crea_xml.py SPECIFICA.txt OUTPUT.xml

Formato: vedi references/formato-specifica.md. In breve, le righe che iniziano
con "=== " aprono una sezione, tutto il resto è contenuto grezzo:

    === category
    Lezione 6 - JavaScript: i cicli
    === question cloze
    === name
    L6 - B2 - Tracciamento: il ciclo for
    === questiontext
    <p>...</p>
    [[codice js]]
    for (let i = 0; i < 3; i++) { ... }
    [[/codice]]
    === question multichoice
    === name
    ...
    === questiontext
    ...
    === answer 100
    testo della risposta corretta
    === feedback
    Esatto: ...
    === answer 0
    ...

Lo script espande i blocchi [[codice]], controlla le regole (Cloze, stile,
tag vietati, risposte corrette) e si ferma se trova errori.
"""
import pathlib
import sys
import xml.dom.minidom

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import moodle_lib as ml  # noqa: E402

TIPI = {"cloze", "multichoice", "truefalse", "shortanswer", "essay", "description"}

PREDEFINITI = {
    "cloze": {"penalty": "0.3333333"},
    "multichoice": {"defaultgrade": "1", "penalty": "0.3333333", "single": "true",
                    "shuffleanswers": "true", "answernumbering": "abc",
                    "showstandardinstruction": "0"},
    "truefalse": {"defaultgrade": "1", "penalty": "1", "correct": None},
    "shortanswer": {"defaultgrade": "1", "penalty": "0.3333333", "usecase": "0"},
    "essay": {"defaultgrade": "1", "penalty": "0", "responseformat": "plain",
              "responserequired": "1", "responsefieldlines": "25",
              "attachments": "0", "attachmentsrequired": "0", "filetypeslist": ""},
    "description": {},
}


class Domanda:
    def __init__(self, tipo, categoria):
        self.tipo = tipo
        self.categoria = categoria
        self.campi = {}          # name, questiontext, generalfeedback, graderinfo...
        self.opzioni = dict(PREDEFINITI[tipo])
        self.risposte = []       # [fraction, testo, feedback]
        self.feedback_tf = {"true": "", "false": ""}


def leggi_specifica(testo):
    testo = testo.replace("\r\n", "\n")
    domande, errori = [], []
    categoria = None
    corrente = None
    sezione, righe = None, []

    def chiudi():
        nonlocal sezione, righe, categoria
        if sezione is None:
            return
        contenuto = "\n".join(righe).strip("\n")
        nome, _, arg = sezione.partition(" ")
        arg = arg.strip()
        if nome == "category":
            categoria = ml.percorso_categoria(contenuto)
        elif corrente is None:
            errori.append("sezione '%s' prima di '=== question'" % nome)
        elif nome in ("name", "questiontext", "generalfeedback", "graderinfo",
                      "responsetemplate"):
            corrente.campi[nome] = contenuto
        elif nome == "note":
            pass
        elif nome == "options":
            for riga in contenuto.splitlines():
                if riga.strip():
                    k, _, v = riga.partition(":")
                    corrente.opzioni[k.strip()] = v.strip()
        elif nome == "answer":
            if corrente.tipo not in ("multichoice", "shortanswer"):
                errori.append("%s: '=== answer' non previsto per %s"
                              % (corrente.campi.get("name", "?"), corrente.tipo))
            corrente.risposte.append([arg or "0", contenuto, ""])
        elif nome == "feedback":
            if corrente.tipo == "truefalse":
                if arg not in ("true", "false"):
                    errori.append("%s: usa '=== feedback true' o '=== feedback false'"
                                  % corrente.campi.get("name", "?"))
                else:
                    corrente.feedback_tf[arg] = contenuto
            elif corrente.risposte:
                corrente.risposte[-1][2] = contenuto
            else:
                errori.append("%s: '=== feedback' senza una risposta prima"
                              % corrente.campi.get("name", "?"))
        else:
            errori.append("sezione sconosciuta: '%s'" % nome)
        sezione, righe = None, []

    for riga in testo.split("\n"):
        if riga.startswith("=== "):
            chiudi()
            intest = riga[4:].strip()
            if intest == "question" or intest.startswith("question "):
                tipo = intest[len("question"):].strip()
                if tipo not in TIPI:
                    errori.append("tipo di domanda non gestito: '%s' (ammessi: %s)"
                                  % (tipo, ", ".join(sorted(TIPI))))
                    tipo = "description"
                corrente = Domanda(tipo, categoria)
                domande.append(corrente)
            else:
                sezione = intest
        else:
            righe.append(riga)
    chiudi()
    return domande, errori


def controlla(d):
    errori, avvisi = [], []
    nome = d.campi.get("name", "").strip()
    if not nome:
        errori.append("manca il nome")
    qt = d.campi.get("questiontext", "")
    if not qt.strip():
        errori.append("manca il testo")
    e, a = ml.controlla_html(qt, d.tipo)
    errori += e; avvisi += a
    for campo in ("generalfeedback", "graderinfo"):
        if d.campi.get(campo):
            e, a = ml.controlla_html(d.campi[campo], "description")
            errori += ["%s: %s" % (campo, x) for x in e]
    if d.tipo == "cloze":
        e, a = ml.controlla_cloze(qt)
        errori += e; avvisi += a
    elif d.tipo == "multichoice":
        if len(d.risposte) < 2:
            errori.append("servono almeno due risposte")
        frazioni = [float(r[0]) for r in d.risposte]
        if d.opzioni.get("single", "true") == "true":
            if frazioni.count(100) != 1:
                errori.append("risposta singola: serve esattamente una risposta a 100")
        elif abs(sum(f for f in frazioni if f > 0) - 100) > 0.5:
            errori.append("risposta multipla: le frazioni positive devono sommare 100")
        elif abs(sum(f for f in frazioni if f < 0) + 100) > 0.5:
            errori.append("risposta multipla: le frazioni negative devono sommare -100 (chi spunta tutto deve prendere 0)")
        if not any(r[2].strip() for r in d.risposte if float(r[0]) <= 0):
            avvisi.append("nessun feedback sulle risposte sbagliate: di solito spiegano "
                          "l'errore")
    elif d.tipo == "shortanswer":
        if not any(float(r[0]) == 100 for r in d.risposte):
            errori.append("serve almeno una risposta a 100")
    elif d.tipo == "truefalse":
        if d.opzioni.get("correct") not in ("true", "false"):
            errori.append("indica 'correct: true' o 'correct: false' in === options")
    elif d.tipo == "essay":
        if not d.campi.get("graderinfo", "").strip():
            avvisi.append("manca graderinfo: le indicazioni per chi corregge aiutano")
    return errori, avvisi


def _testo(tag, contenuto, formato="html", indent="    "):
    return ('%s<%s format="%s">\n%s  <text>%s</text>\n%s</%s>\n'
            % (indent, tag, formato, indent, ml.cdata(contenuto) if contenuto else "",
               indent, tag))


def genera_domanda(d):
    o = d.opzioni
    x = ['  <question type="%s">\n' % d.tipo,
         '    <name>\n      <text>%s</text>\n    </name>\n' % ml.esc_xml(d.campi["name"].strip()),
         _testo("questiontext", d.campi.get("questiontext", "")),
         _testo("generalfeedback", d.campi.get("generalfeedback", ""))]
    if d.tipo == "description":
        x.append("    <defaultgrade>0.0000000</defaultgrade>\n    <penalty>0.0000000</penalty>\n")
    elif d.tipo == "cloze":
        x.append("    <penalty>%s</penalty>\n" % o["penalty"])
    else:
        x.append("    <defaultgrade>%s</defaultgrade>\n    <penalty>%s</penalty>\n"
                 % (o["defaultgrade"], o["penalty"]))
    x.append("    <hidden>0</hidden>\n    <idnumber></idnumber>\n")

    if d.tipo == "multichoice":
        x.append("    <single>%s</single>\n    <shuffleanswers>%s</shuffleanswers>\n"
                 "    <answernumbering>%s</answernumbering>\n"
                 "    <showstandardinstruction>%s</showstandardinstruction>\n"
                 % (o["single"], o["shuffleanswers"], o["answernumbering"],
                    o["showstandardinstruction"]))
        for t in ("correctfeedback", "partiallycorrectfeedback", "incorrectfeedback"):
            x.append(_testo(t, ""))
        for fr, testo, fb in d.risposte:
            x.append('    <answer fraction="%s" format="html">\n      <text>%s</text>\n'
                     % (fr, ml.cdata(testo)))
            x.append(_testo("feedback", fb, indent="      "))
            x.append("    </answer>\n")
    elif d.tipo == "shortanswer":
        x.append("    <usecase>%s</usecase>\n" % o["usecase"])
        for fr, testo, fb in d.risposte:
            x.append('    <answer fraction="%s" format="moodle_auto_format">\n'
                     '      <text>%s</text>\n' % (fr, ml.esc_xml(testo)))
            x.append(_testo("feedback", fb, indent="      "))
            x.append("    </answer>\n")
    elif d.tipo == "truefalse":
        giusta = o["correct"]
        for valore in ("true", "false"):
            fr = "100" if valore == giusta else "0"
            x.append('    <answer fraction="%s" format="moodle_auto_format">\n'
                     '      <text>%s</text>\n' % (fr, valore))
            x.append(_testo("feedback", d.feedback_tf[valore], indent="      "))
            x.append("    </answer>\n")
    elif d.tipo == "essay":
        x.append("    <responseformat>%s</responseformat>\n"
                 "    <responserequired>%s</responserequired>\n"
                 "    <responsefieldlines>%s</responsefieldlines>\n"
                 "    <minwordlimit>0</minwordlimit>\n    <maxwordlimit>0</maxwordlimit>\n"
                 "    <attachments>%s</attachments>\n"
                 "    <attachmentsrequired>%s</attachmentsrequired>\n"
                 "    <maxbytes>0</maxbytes>\n    <filetypeslist>%s</filetypeslist>\n"
                 % (o["responseformat"], o["responserequired"], o["responsefieldlines"],
                    o["attachments"], o["attachmentsrequired"], o["filetypeslist"]))
        x.append(_testo("graderinfo", d.campi.get("graderinfo", "")))
        x.append(_testo("responsetemplate", d.campi.get("responsetemplate", "")))
    x.append("  </question>\n\n")
    return "".join(x)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    spec = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    domande, errori = leggi_specifica(spec)
    avvisi_lettura, da_leggere = [], 0
    for d in domande:
        ml.AVVISI_LETTURA.clear()
        da_leggere += sum(1 for m in ml.BLOCCO_RE.finditer(d.campi.get("questiontext", ""))
                          if m.group(2) == "leggere")
        for campo in ("questiontext", "generalfeedback", "graderinfo", "responsetemplate"):
            if campo in d.campi:
                d.campi[campo] = ml.espandi_codice(d.campi[campo])
        for r in d.risposte:
            r[1] = ml.espandi_codice(r[1])
            r[2] = ml.espandi_codice(r[2])
        nome = d.campi.get("name", "(senza nome)").strip()
        avvisi_lettura += ["%s: %s" % (nome, a) for a in ml.AVVISI_LETTURA]

    nomi = {}
    tot_avvisi = 0
    for x in avvisi_lettura:
        print("AVVISO  %s" % x); tot_avvisi += 1
    for d in domande:
        e, a = controlla(d)
        nome = d.campi.get("name", "(senza nome)").strip()
        nomi[nome] = nomi.get(nome, 0) + 1
        for x in e:
            errori.append("%s: %s" % (nome, x))
        for x in a:
            print("AVVISO  %s: %s" % (nome, x)); tot_avvisi += 1
    for n, c in nomi.items():
        if c > 1:
            errori.append("nome ripetuto %d volte: %s" % (c, n))
    if errori:
        print("\nERRORI (XML non generato):")
        for e in errori:
            print("  - " + e)
        sys.exit(1)

    out = ['<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n']
    cat_corrente = object()
    for d in domande:
        if d.categoria != cat_corrente:
            if d.categoria:
                out.append(ml.xml_categoria(d.categoria))
            cat_corrente = d.categoria
        out.append(genera_domanda(d))
    out.append("</quiz>\n")
    xml_testo = "".join(out)
    xml.dom.minidom.parseString(xml_testo.encode("utf-8"))  # ben formato?
    pathlib.Path(sys.argv[2]).write_text(xml_testo, encoding="utf-8")
    conteggio = {}
    for d in domande:
        conteggio[d.tipo] = conteggio.get(d.tipo, 0) + 1
    print("\nOK: %d domande (%s), %d avvisi -> %s" % (
        len(domande), ", ".join("%s %d" % kv for kv in sorted(conteggio.items())),
        tot_avvisi, sys.argv[2]))
    if da_leggere:
        print("Codici da leggere resi non eseguibili: %d" % da_leggere)


if __name__ == "__main__":
    main()
