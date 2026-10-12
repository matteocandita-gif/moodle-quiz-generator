#!/usr/bin/env python3
"""Crea un backup .mbz di un singolo quiz (attività) da ripristinare in Moodle.

Uso:
    python3 crea_mbz.py DOMANDE.xml IMPAGINAZIONE.json USCITA.mbz

DOMANDE.xml        Moodle XML prodotto da crea_xml.py (le domande con il loro contenuto)
IMPAGINAZIONE.json impostazioni del quiz e distribuzione di domande su sezioni e pagine

Il formato dell'impaginazione è in references/formato-impaginazione.md. In breve:

{
  "nome": "Prova quiz",
  "preset": "esercitazione",            # oppure "verifica"
  "impostazioni": {"timelimit": 5400},  # facoltativo: sovrascrive il preset
  "voto_massimo": 10, "voto_sufficienza": 6,
  "sezioni": [
    {"titolo": "", "domande": [{"nome": "L1 - 00 - ...", "pagina": 1, "punti": 0}]},
    {"titolo": "Blocco A", "domande": [...]}
  ]
}

Lo script riproduce la struttura di un backup di attività di Moodle 5.2 (verificata sul
ripristino di backup reali). Si ferma con un errore se trova un tipo di domanda che non
sa scrivere.
"""
import base64
import html
import io
import json
import os
import random
import re
import string
import sys
import tarfile
import time
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from moodle_lib import CAMPO_RE, _dividi_opzioni  # noqa: E402

NULL = "$@NULL@$"
MOODLE_VERSION = "2026042002.02"
MOODLE_RELEASE = "5.2.2+ (Build: 20260903)"
BACKUP_VERSION = "2026042000"
BACKUP_RELEASE = "5.2"

# review*: bit di Moodle. 65536 = durante il tentativo; 4096 = subito dopo il tentativo;
# 256 = più tardi, a quiz ancora aperto; 16 = dopo la chiusura del quiz.
# 69888 = 65536 + 4096 + 256 (come nel quiz formativo di riferimento); 65536 = solo durante il tentativo.
PRESET = {
    "esercitazione": {
        "preferredbehaviour": "interactive", "attempts_number": 0, "timelimit": 0,
        "reviewattempt": 69888, "reviewcorrectness": 69888, "reviewmaxmarks": 69888,
        "reviewmarks": 69888, "reviewspecificfeedback": 69888,
        "reviewgeneralfeedback": 69888, "reviewrightanswer": 69888,
    },
    "verifica": {
        "preferredbehaviour": "deferredfeedback", "attempts_number": 1, "timelimit": 5400,
        "reviewattempt": 65536, "reviewcorrectness": 0, "reviewmaxmarks": 65536,
        "reviewmarks": 0, "reviewspecificfeedback": 0,
        "reviewgeneralfeedback": 0, "reviewrightanswer": 0,
    },
}
COMUNI = {
    "timeopen": 0, "timeclose": 0, "overduehandling": "autosubmit", "graceperiod": 0,
    "canredoquestions": 0, "attemptonlast": 0, "grademethod": 1, "decimalpoints": 2,
    "questiondecimalpoints": -1, "reviewoverallfeedback": 0, "questionsperpage": 1,
    "navmethod": "free", "shuffleanswers": 1, "password": "", "subnet": "",
    "browsersecurity": "-", "delay1": 0, "delay2": 0, "showuserpicture": 0,
    "showblocks": 0, "completionattemptsexhausted": 0, "completionminattempts": 0,
    "allowofflineattempts": 0,
}


class Contatore:
    def __init__(self, inizio):
        self.n = inizio - 1

    def __call__(self):
        self.n += 1
        return self.n


def casuale(n=6):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(n))


def f7(x):
    return "%.7f" % float(x)


def x(testo):
    return escape(testo or "")


def testo_di(el, tag):
    e = el.find(tag)
    if e is None:
        return ""
    t = e.find("text")
    return (t.text or "") if t is not None else (e.text or "")


def formato(el, tag):
    e = el.find(tag)
    return 1 if (e is None or e.get("format", "html") == "html") else 0


# ---------------------------------------------------------------- lettura delle domande

def leggi_domande(percorso):
    radice = ET.parse(percorso).getroot()
    categoria, domande = None, []
    for q in radice.findall("question"):
        t = q.get("type")
        if t == "category":
            categoria = testo_di(q, "category").strip().split("/")[-1]
            continue
        domande.append((t, q))
    if not categoria:
        raise SystemExit("ERRORE: l'XML non contiene la categoria")
    return categoria, domande


# ---------------------------------------------------------------- scrittura delle domande

class Banca:
    """Costruisce questions.xml con id progressivi."""

    def __init__(self, contesto, modulo, categoria_id):
        self.ctx, self.mid, self.cat = contesto, modulo, categoria_id
        self.entry = Contatore(80001)
        self.qid = Contatore(95001)
        self.ans = Contatore(190001)
        self.opt = Contatore(40001)
        self.out = []
        self.ora = int(time.time())
        self.id_per_nome = {}
        # tag delle domande: id inventati alti, che al ripristino Moodle rimappa per nome
        # (tag_condition::restore_filtercondition); non devono coincidere con tag esistenti sul sito
        self.tag_id = {}
        self.tag_entry = {}
        self._tag_xml = ""
        # file allegati alle domande CodeRunner (database SQL): (id domanda, nome, contenuto)
        self.file_domande = []
        self._qid_corrente = None

    def stamp(self):
        return "generato.mbz+%s+%s" % (time.strftime("%y%m%d%H%M%S"), casuale())

    def _blocco(self, qid, entry_id, parent, nome, testo, fmt, gf, gff, defaultmark, penalty,
                qtype, length, plugin, nextversion):
        return f"""      <question_bank_entry id="{entry_id}">
        <questioncategoryid>{self.cat}</questioncategoryid>
        <idnumber>{NULL}</idnumber>
        <ownerid>3</ownerid>
        <nextversion>{nextversion}</nextversion>
        <question_version>
          <question_versions id="{qid}">
            <version>1</version>
            <status>ready</status>
            <questions>
              <question id="{qid}">
                <parent>{parent}</parent>
                <name>{x(nome)}</name>
                <questiontext>{x(testo)}</questiontext>
                <questiontextformat>{fmt}</questiontextformat>
                <generalfeedback>{x(gf)}</generalfeedback>
                <generalfeedbackformat>{gff}</generalfeedbackformat>
                <defaultmark>{f7(defaultmark)}</defaultmark>
                <penalty>{f7(penalty)}</penalty>
                <qtype>{qtype}</qtype>
                <length>{length}</length>
                <stamp>{self.stamp()}</stamp>
                <timecreated>{self.ora}</timecreated>
                <timemodified>{self.ora}</timemodified>
                <createdby>3</createdby>
                <modifiedby>3</modifiedby>
{plugin}                <plugin_qbank_comment_question>
                  <comments>
                  </comments>
                </plugin_qbank_comment_question>
                <plugin_qbank_customfields_question>
                  <customfields>
                  </customfields>
                </plugin_qbank_customfields_question>
                <question_hints>
                </question_hints>
                <tags>
{self._tag_xml if parent == 0 else ""}                </tags>
              </question>
            </questions>
          </question_versions>
        </question_version>
      </question_bank_entry>
"""

    def _risposta(self, testo, fraction, feedback, fmt_testo, fmt_fb=1):
        aid = self.ans()
        return aid, f"""                    <answer id="{aid}">
                      <answertext>{x(testo)}</answertext>
                      <answerformat>{fmt_testo}</answerformat>
                      <fraction>{f7(fraction)}</fraction>
                      <feedback>{x(feedback)}</feedback>
                      <feedbackformat>{fmt_fb}</feedbackformat>
                    </answer>
"""

    def aggiungi(self, tipo, q):
        nome = testo_di(q, "name")
        testo = testo_di(q, "questiontext")
        fmt = formato(q, "questiontext")
        gf = testo_di(q, "generalfeedback")
        gff = formato(q, "generalfeedback")
        dm = float((q.findtext("defaultgrade") or "1"))
        pen = float((q.findtext("penalty") or "0"))
        entry_id, qid = self.entry(), self.qid()
        self._qid_corrente = qid
        self.id_per_nome[nome] = entry_id
        self._tag_xml = ""
        for t in q.findall("tags/tag"):
            raw = (t.findtext("text") or "").strip()
            if not raw:
                continue
            k = raw.lower()
            if k not in self.tag_id:
                self.tag_id[k] = 9900001 + len(self.tag_id)
            self.tag_entry.setdefault(k, []).append(nome)
            self._tag_xml += f"""                  <tag id="{self.tag_id[k]}" contextid="{self.ctx}">
                    <name>{x(k)}</name>
                    <rawname>{x(raw)}</rawname>
                  </tag>
"""
        if tipo == "description":
            self.out.append(self._blocco(qid, entry_id, 0, nome, testo, fmt, gf, gff, 0, 0,
                                         "description", 0, "", 2))
        elif tipo == "essay":
            g = lambda t, d="": q.findtext(t) if q.findtext(t) is not None else d
            plugin = f"""                <plugin_qtype_essay_question>
                  <essay id="{self.opt()}">
                    <responseformat>{g("responseformat", "plain")}</responseformat>
                    <responserequired>{g("responserequired", "1")}</responserequired>
                    <responsefieldlines>{g("responsefieldlines", "15")}</responsefieldlines>
                    <minwordlimit>{g("minwordlimit", "0")}</minwordlimit>
                    <maxwordlimit>{g("maxwordlimit", "0")}</maxwordlimit>
                    <attachments>{g("attachments", "0")}</attachments>
                    <attachmentsrequired>{g("attachmentsrequired", "0")}</attachmentsrequired>
                    <graderinfo>{x(testo_di(q, "graderinfo"))}</graderinfo>
                    <graderinfoformat>{formato(q, "graderinfo")}</graderinfoformat>
                    <responsetemplate>{x(testo_di(q, "responsetemplate"))}</responsetemplate>
                    <responsetemplateformat>1</responsetemplateformat>
                    <filetypeslist>{x(g("filetypeslist"))}</filetypeslist>
                    <maxbytes>{g("maxbytes", "0")}</maxbytes>
                  </essay>
                </plugin_qtype_essay_question>
"""
            self.out.append(self._blocco(qid, entry_id, 0, nome, testo, fmt, gf, gff, dm, 0,
                                         "essay", 1, plugin, 2))
        elif tipo == "multichoice":
            self.out.append(self._multichoice(qid, entry_id, 0, nome, testo, fmt, gf, gff, dm,
                                              pen, q))
        elif tipo == "truefalse":
            risp, ids = [], {}
            for a in q.findall("answer"):
                vero = (a.findtext("text") or "").strip().lower() == "true"
                frac = float(a.get("fraction", "0")) / 100
                aid, xml = self._risposta("Vero" if vero else "Falso", frac,
                                          testo_di(a, "feedback"), 0)
                ids[vero] = aid
                risp.append((vero, xml))
            risp.sort(key=lambda r: not r[0])
            plugin = ("                <plugin_qtype_truefalse_question>\n                  <answers>\n"
                      + "".join(r[1] for r in risp)
                      + f"""                  </answers>
                  <truefalse id="{self.opt()}">
                    <trueanswer>{ids[True]}</trueanswer>
                    <falseanswer>{ids[False]}</falseanswer>
                    <showstandardinstruction>0</showstandardinstruction>
                  </truefalse>
                </plugin_qtype_truefalse_question>
""")
            self.out.append(self._blocco(qid, entry_id, 0, nome, testo, fmt, gf, gff, dm, pen,
                                         "truefalse", 1, plugin, 2))
        elif tipo == "shortanswer":
            risp = "".join(
                self._risposta(testo_di(a, "text"), float(a.get("fraction", "0")) / 100,
                               testo_di(a, "feedback"), 0)[1] for a in q.findall("answer"))
            self.out.append(self._blocco(qid, entry_id, 0, nome, testo, fmt, gf, gff, dm, pen,
                                         "shortanswer", 1,
                                         self._plugin_shortanswer(risp, q.findtext("usecase") == "1"), 2))
        elif tipo == "cloze":
            self._cloze(qid, entry_id, nome, testo, fmt, gf, gff, pen)
        elif tipo == "matching":
            sub = "".join(f"""                    <match id="{self.ans()}">
                      <questiontext>{x(testo_di(sq, "."))}</questiontext>
                      <questiontextformat>{1 if sq.get("format", "html") == "html" else 0}</questiontextformat>
                      <answertext>{x(testo_di(sq, "answer"))}</answertext>
                    </match>
""" for sq in q.findall("subquestion"))
            plugin = f"""                <plugin_qtype_match_question>
                  <matchoptions id="{self.opt()}">
                    <shuffleanswers>{1 if (q.findtext("shuffleanswers") or "true") in ("true", "1") else 0}</shuffleanswers>
                    <correctfeedback>{x(testo_di(q, "correctfeedback"))}</correctfeedback>
                    <correctfeedbackformat>1</correctfeedbackformat>
                    <partiallycorrectfeedback>{x(testo_di(q, "partiallycorrectfeedback"))}</partiallycorrectfeedback>
                    <partiallycorrectfeedbackformat>1</partiallycorrectfeedbackformat>
                    <incorrectfeedback>{x(testo_di(q, "incorrectfeedback"))}</incorrectfeedback>
                    <incorrectfeedbackformat>1</incorrectfeedbackformat>
                    <shownumcorrect>{1 if q.find("shownumcorrect") is not None else 0}</shownumcorrect>
                  </matchoptions>
                  <matches>
{sub}                  </matches>
                </plugin_qtype_match_question>
"""
            self.out.append(self._blocco(qid, entry_id, 0, nome, testo, fmt, gf, gff, dm, pen,
                                         "match", 1, plugin, 2))
        elif tipo == "coderunner":
            self.out.append(self._blocco(qid, entry_id, 0, nome, testo, fmt, gf, gff, dm, pen,
                                         "coderunner", 1, self._plugin_coderunner(q, nome), 2))
        else:
            raise SystemExit("ERRORE: tipo di domanda non gestito da crea_mbz: %s (%s)" % (tipo, nome))

    # CodeRunner: i campi del Moodle XML passano uno a uno nelle opzioni del backup, nello stesso
    # ordine (verificato sul backup «Quiz 2» con i prototipi JavaScript dell'utente). I campi vuoti
    # di questo elenco nel backup diventano NULL (la domanda usa il valore del prototipo).
    CR_CAMPI = ["coderunnertype", "prototypetype", "allornothing", "penaltyregime", "precheck", "hidecheck",
                "showsource", "answerboxlines", "answerboxcolumns", "answerpreload", "globalextra", "useace",
                "resultcolumns", "template", "iscombinatortemplate", "allowmultiplestdins", "answer",
                "validateonsave", "testsplitterre", "language", "acelang", "sandbox", "grader",
                "cputimelimitsecs", "memlimitmb", "sandboxparams", "templateparams", "hoisttemplateparams",
                "extractcodefromjson", "templateparamslang", "templateparamsevalpertry", "templateparamsevald",
                "twigall", "uiplugin", "uiparameters", "attachments", "attachmentsrequired", "maxfilesize",
                "filenamesregex", "filenamesexplain", "displayfeedback", "giveupallowed", "prototypeextra"]
    CR_NULL = {"useace", "resultcolumns", "template", "iscombinatortemplate", "allowmultiplestdins",
               "testsplitterre", "language", "acelang", "sandbox", "grader", "cputimelimitsecs", "memlimitmb",
               "sandboxparams", "uiplugin", "prototypeextra"}

    def _plugin_coderunner(self, q, nome):
        for f in q.findall(".//file"):
            dati = base64.b64decode("".join((f.text or "").split()))
            self.file_domande.append((self._qid_corrente, f.get("name"), dati))
        opz = []
        for c in self.CR_CAMPI:
            v = q.findtext(c)
            if v is None or v == "":
                v = NULL if c in self.CR_NULL else ""
            else:
                v = x(v)
            opz.append("                      <%s>%s</%s>\n" % (c, v, c))
        tcs = []
        for t in q.findall("testcases/testcase"):
            g = lambda f: x(t.findtext(f + "/text") or "")
            tcs.append(f"""                    <coderunner_testcase id="{self.opt()}">
                      <testcode>{g("testcode")}</testcode>
                      <testtype>{t.get("testtype", "0")}</testtype>
                      <expected>{g("expected")}</expected>
                      <useasexample>{t.get("useasexample", "0")}</useasexample>
                      <display>{t.findtext("display/text") or "SHOW"}</display>
                      <hiderestiffail>{t.get("hiderestiffail", "0")}</hiderestiffail>
                      <mark>{float(t.get("mark", "1")):.3f}</mark>
                      <stdin>{g("stdin")}</stdin>
                      <extra>{g("extra")}</extra>
                    </coderunner_testcase>
""")
        return (f"""                <plugin_qtype_coderunner_question>
                  <coderunner_options>
                    <coderunner_option id="{self.opt()}">
""" + "".join(opz) + """                    </coderunner_option>
                  </coderunner_options>
                  <coderunner_testcases>
""" + "".join(tcs) + """                  </coderunner_testcases>
                </plugin_qtype_coderunner_question>
""")

    def _plugin_shortanswer(self, risposte, usecase):
        return f"""                <plugin_qtype_shortanswer_question>
                  <answers>
{risposte}                  </answers>
                  <shortanswer id="{self.opt()}">
                    <usecase>{1 if usecase else 0}</usecase>
                  </shortanswer>
                </plugin_qtype_shortanswer_question>
"""

    def _plugin_multichoice(self, risposte, single, shuffle, layout, numbering, fb, std):
        c, p, i = fb
        return f"""                <plugin_qtype_multichoice_question>
                  <answers>
{risposte}                  </answers>
                  <multichoice id="{self.opt()}">
                    <layout>{layout}</layout>
                    <single>{1 if single else 0}</single>
                    <shuffleanswers>{1 if shuffle else 0}</shuffleanswers>
                    <correctfeedback>{x(c)}</correctfeedback>
                    <correctfeedbackformat>1</correctfeedbackformat>
                    <partiallycorrectfeedback>{x(p)}</partiallycorrectfeedback>
                    <partiallycorrectfeedbackformat>1</partiallycorrectfeedbackformat>
                    <incorrectfeedback>{x(i)}</incorrectfeedback>
                    <incorrectfeedbackformat>1</incorrectfeedbackformat>
                    <answernumbering>{numbering}</answernumbering>
                    <shownumcorrect>0</shownumcorrect>
                    <showstandardinstruction>{std}</showstandardinstruction>
                  </multichoice>
                </plugin_qtype_multichoice_question>
"""

    def _multichoice(self, qid, entry_id, parent, nome, testo, fmt, gf, gff, dm, pen, q):
        risp = "".join(
            self._risposta(testo_di(a, "text"), float(a.get("fraction", "0")) / 100,
                           testo_di(a, "feedback"), 1 if a.get("format", "html") == "html" else 0)[1]
            for a in q.findall("answer"))
        single = (q.findtext("single") or "true") == "true"
        shuffle = (q.findtext("shuffleanswers") or "true") == "true"
        fb = (testo_di(q, "correctfeedback"), testo_di(q, "partiallycorrectfeedback"),
              testo_di(q, "incorrectfeedback"))
        plugin = self._plugin_multichoice(risp, single, shuffle, 0, q.findtext("answernumbering") or "abc",
                                          fb, q.findtext("showstandardinstruction") or 0)
        return self._blocco(qid, entry_id, parent, nome, testo, fmt, gf, gff, dm, pen,
                            "multichoice", 1, plugin, 2)

    # ---- Cloze: una domanda "multianswer" più una domanda per ogni campo
    def _cloze(self, qid, entry_id, nome, testo, fmt, gf, gff, pen):
        campi = list(CAMPO_RE.finditer(testo))
        if not campi:
            raise SystemExit("ERRORE: Cloze senza campi: " + nome)
        parent_testo, figli, somma = [], [], 0.0
        ultimo = 0
        figli_ids = []
        for n, m in enumerate(campi, 1):
            parent_testo.append(testo[ultimo:m.start()] + "{#%d}" % n)
            ultimo = m.end()
            peso = float(m.group(1) or 1)
            somma += peso
            figli_ids.append(self.qid())
            figli.append((m, peso))
        parent_testo.append(testo[ultimo:])
        sequenza = ",".join(str(i) for i in figli_ids)
        plugin = f"""                <plugin_qtype_multianswer_question>
                  <answers>
                  </answers>
                  <multianswer id="{self.opt()}">
                    <question>{qid}</question>
                    <sequence>{sequenza}</sequence>
                  </multianswer>
                </plugin_qtype_multianswer_question>
"""
        self.out.append(self._blocco(qid, entry_id, 0, nome, "".join(parent_testo), fmt, gf, gff,
                                     somma, pen, "multianswer", 1, plugin, 2))
        for (m, peso), fid in zip(figli, figli_ids):
            self.out.append(self._sottodomanda(fid, qid, nome, m, peso))

    def _opzioni(self, contenuto):
        """[(fraction, testo, feedback)] dalle opzioni di un campo Cloze."""
        ris = []
        for op in _dividi_opzioni(contenuto):
            frac = 0.0
            if op.startswith("="):
                frac, op = 1.0, op[1:]
            else:
                mm = re.match(r"%(-?\d+(?:\.\d+)?)%", op)
                if mm:
                    frac, op = float(mm.group(1)) / 100, op[mm.end():]
            mf = re.search(r"(?<!\\)#", op)
            fb = ""
            if mf:
                op, fb = op[:mf.start()], op[mf.end():]
            sciogli = lambda s: re.sub(r"\\([}#~\\])", r"\1", s)
            ris.append((frac, sciogli(op).strip(), sciogli(fb)))
        return ris

    def _sottodomanda(self, fid, parent, nome, m, peso):
        tipo = m.group(2)
        opzioni = self._opzioni(m.group(3))
        entry_id = self.entry()
        testo_campo = m.group(0)
        sh = {"SHORTANSWER", "SA", "MW", "SHORTANSWER_C", "SAC", "MWC"}
        nu = {"NUMERICAL", "NM"}
        mc = {"MULTICHOICE", "MC", "MULTICHOICE_V", "MCV", "MULTICHOICE_H", "MCH", "MULTICHOICE_S",
              "MCS", "MULTICHOICE_VS", "MCVS", "MULTICHOICE_HS", "MCHS"}
        if tipo in sh:
            risp = "".join(self._risposta(t, fr, fb, 0)[1] for fr, t, fb in opzioni)
            plugin = self._plugin_shortanswer(risp, tipo.endswith("_C") or tipo in ("SAC", "MWC"))
            qtype = "shortanswer"
        elif tipo in nu:
            blocchi, records = [], []
            for fr, t, fb in opzioni:
                num, _, tol = t.partition(":")
                aid, xml = self._risposta(num, fr, fb, 0)
                blocchi.append(xml)
                records.append(f"""                    <numerical_record id="{self.opt()}">
                      <answer>{aid}</answer>
                      <tolerance>{tol or 0}</tolerance>
                    </numerical_record>
""")
            plugin = ("                <plugin_qtype_numerical_question>\n                  <answers>\n"
                      + "".join(blocchi) + f"""                  </answers>
                  <numerical_units>
                  </numerical_units>
                  <numerical_options>
                    <numerical_option id="{self.opt()}">
                      <showunits>3</showunits>
                      <unitsleft>0</unitsleft>
                      <unitgradingtype>0</unitgradingtype>
                      <unitpenalty>1.0000000</unitpenalty>
                    </numerical_option>
                  </numerical_options>
                  <numerical_records>
""" + "".join(records) + """                  </numerical_records>
                </plugin_qtype_numerical_question>
""")
            qtype = "numerical"
        elif tipo in mc:
            # Moodle decodifica le entità nelle opzioni dei menù (verificato sul backup «Quiz 2»)
            risp = "".join(self._risposta(html.unescape(t), fr, fb, 1)[1] for fr, t, fb in opzioni)
            layout = 1 if tipo in ("MULTICHOICE_V", "MCV", "MULTICHOICE_VS", "MCVS") else (
                2 if tipo in ("MULTICHOICE_H", "MCH", "MULTICHOICE_HS", "MCHS") else 0)
            shuffle = tipo.endswith("S")
            plugin = self._plugin_multichoice(risp, True, shuffle, layout, "0", ("", "", ""), 0)
            qtype = "multichoice"
        else:
            raise SystemExit("ERRORE: campo Cloze di tipo non gestito: %s (%s)" % (tipo, nome))
        return self._blocco(fid, entry_id, parent, nome, testo_campo, 1, "", 1, peso, 0, qtype, 1,
                            plugin, NULL)


# ---------------------------------------------------------------- scrittura dei file del backup

def quiz_xml(L, ids, banca, righe, nome, ora):
    imp = dict(COMUNI)
    imp.update(PRESET[L.get("preset", "esercitazione")])
    imp.update(L.get("impostazioni", {}))
    somma = sum(r["punti"] for r in righe)
    istanze = []
    for i, r in enumerate(righe, 1):
        testa_i = f"""      <question_instance id="{ids['qi']()}">
        <quizid>{ids['quiz']}</quizid>
        <slot>{i}</slot>
        <page>{r['pagina']}</page>
        <displaynumber>{NULL}</displaynumber>
        <requireprevious>0</requireprevious>
        <maxmark>{f7(r['punti'])}</maxmark>
        <quizgradeitemid>{NULL}</quizgradeitemid>
"""
        if r.get("casuale"):
            # domanda casuale: pesca dalla categoria della lezione una domanda con il tag della posizione
            fc = {"filter": {"qtagids": {"name": "qtagids", "jointype": 2,
                                         "values": [banca.tag_id[r["casuale"].lower()]], "filteroptions": []},
                             "category": {"name": "category", "jointype": 1, "values": [ids["cat"]],
                                          "filteroptions": {"includesubcategories": True}}},
                  "cmid": ids["mid"], "courseid": 7, "jointype": 2, "qpage": 0, "qperpage": 1000,
                  "sortdata": [], "cat": "%d,%d" % (ids["cat"], ids["ctx"]), "tabname": "questions"}
            istanze.append(testa_i + f"""        <question_set_reference id="{ids['qs']()}">
          <usingcontextid>{ids['ctx']}</usingcontextid>
          <component>mod_quiz</component>
          <questionarea>slot</questionarea>
          <questionscontextid>{ids['ctx']}</questionscontextid>
          <filtercondition>{x(json.dumps(fc, separators=(",", ":")))}</filtercondition>
        </question_set_reference>
      </question_instance>
""")
            continue
        istanze.append(testa_i + f"""        <question_reference id="{ids['qr']()}">
          <usingcontextid>{ids['ctx']}</usingcontextid>
          <component>mod_quiz</component>
          <questionarea>slot</questionarea>
          <questionbankentryid>{banca.id_per_nome[r['nome']]}</questionbankentryid>
          <version>{NULL}</version>
        </question_reference>
      </question_instance>
""")
    sezioni, slot = [], 1
    for s in L["sezioni"]:
        sezioni.append(f"""      <section id="{ids['sec']()}">
        <firstslot>{slot}</firstslot>
        <heading>{x(s.get('titolo', ''))}</heading>
        <shufflequestions>{1 if s.get('mescola') else 0}</shufflequestions>
      </section>
""")
        slot += len(s["domande"])
    voto = L.get("voto_massimo", 10)
    campi = ["timeopen", "timeclose", "timelimit", "overduehandling", "graceperiod", "preferredbehaviour",
             "canredoquestions", "attempts_number", "attemptonlast", "grademethod", "decimalpoints",
             "questiondecimalpoints", "reviewattempt", "reviewcorrectness", "reviewmaxmarks", "reviewmarks",
             "reviewspecificfeedback", "reviewgeneralfeedback", "reviewrightanswer", "reviewoverallfeedback",
             "questionsperpage", "navmethod", "shuffleanswers"]
    testa = "".join("    <%s>%s</%s>\n" % (c, imp[c], c) for c in campi)
    coda = "".join("    <%s>%s</%s>\n" % (c, imp[c], c) for c in
                   ["password", "subnet", "browsersecurity", "delay1", "delay2", "showuserpicture", "showblocks",
                    "completionattemptsexhausted", "completionminattempts", "allowofflineattempts"])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<activity id="{ids['quiz']}" moduleid="{ids['mid']}" modulename="quiz" contextid="{ids['ctx']}">
  <quiz id="{ids['quiz']}">
    <name>{x(nome)}</name>
    <intro>{x(L.get('intro', ''))}</intro>
    <introformat>1</introformat>
{testa}    <sumgrades>{somma:.5f}</sumgrades>
    <grade>{voto:.5f}</grade>
    <timecreated>{ora}</timecreated>
    <timemodified>{ora}</timemodified>
{coda}    <precreateattempts>{NULL}</precreateattempts>
    <subplugin_quizaccess_seb_quiz>
    </subplugin_quizaccess_seb_quiz>
    <quiz_grade_items>
    </quiz_grade_items>
    <question_instances>
{''.join(istanze)}    </question_instances>
    <sections>
{''.join(sezioni)}    </sections>
    <feedbacks>
      <feedback id="{ids['fb']}">
        <feedbacktext></feedbacktext>
        <feedbacktextformat>1</feedbacktextformat>
        <mingrade>0.00000</mingrade>
        <maxgrade>{voto + 1:.5f}</maxgrade>
      </feedback>
    </feedbacks>
    <overrides>
    </overrides>
    <grades>
    </grades>
    <attempts>
    </attempts>
  </quiz>
</activity>"""


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    xml_path, lay_path, out = sys.argv[1:]
    L = json.load(open(lay_path, encoding="utf-8"))
    categoria, domande = leggi_domande(xml_path)
    nome = L["nome"]
    ora = int(time.time())
    mid, quiz_id, ctx, sec_corso = 99001, 9901, 99101, 99201
    cat_top, cat_def, cat_q = 99301, 99302, 99303

    righe = [dict(d, **{"_sez": s.get("titolo", "")}) for s in L["sezioni"] for d in s["domande"]]
    banca = Banca(ctx, mid, cat_q)
    for tipo, q in domande:
        banca.aggiungi(tipo, q)

    # domande fisse (per nome) e casuali (per tag): ogni domanda dell'XML deve essere usata in uno dei due modi
    nomi_xml = [testo_di(q, "name") for _, q in domande]
    casuali = {r["casuale"].lower() for r in righe if r.get("casuale")}
    senza = [r["casuale"] for r in righe if r.get("casuale") and r["casuale"].lower() not in banca.tag_entry]
    pescate = {n for k in casuali for n in banca.tag_entry.get(k, [])}
    fisse = {r["nome"] for r in righe if not r.get("casuale")}
    mancano = [n for n in nomi_xml if n not in fisse and n not in pescate]
    inutili = [n for n in fisse if n not in nomi_xml]
    if mancano or inutili or senza:
        raise SystemExit("ERRORE: domande dell'XML non impaginate: %s; impaginate ma assenti nell'XML: %s; "
                         "posizioni casuali senza domande con quel tag: %s" % (mancano, inutili, senza))

    def cat(i, nome_c, info, parent, ordine):
        return f"""  <question_category id="{i}">
    <name>{x(nome_c)}</name>
    <contextid>{ctx}</contextid>
    <contextlevel>70</contextlevel>
    <contextinstanceid>{mid}</contextinstanceid>
    <info>{x(info)}</info>
    <infoformat>0</infoformat>
    <stamp>{banca.stamp()}</stamp>
    <parent>{parent}</parent>
    <sortorder>{ordine}</sortorder>
    <idnumber>{NULL}</idnumber>
    <question_bank_entries>
"""
    chiudi = "    </question_bank_entries>\n  </question_category>\n"
    questions = ('<?xml version="1.0" encoding="UTF-8"?>\n<question_categories>\n'
                 + cat(cat_top, "top", "", 0, 0) + chiudi
                 + cat(cat_def, "Default per " + nome,
                       "La categoria default per le domande condivise nel contesto '%s'." % nome, cat_top, 999) + chiudi
                 + cat(cat_q, categoria, "", cat_top, 999) + "".join(banca.out) + chiudi
                 + "</question_categories>")

    ids = {"qi": Contatore(99401), "qr": Contatore(99501), "qs": Contatore(99551), "sec": Contatore(99601),
           "fb": 99701, "quiz": quiz_id, "mid": mid, "ctx": ctx, "cat": cat_q}
    quiz = quiz_xml(L, ids, banca, righe, nome, ora)

    # file fissi (modello): stessa struttura dei backup di attività di Moodle 5.2
    adir = "activities/quiz_%d" % mid
    voto = L.get("voto_massimo", 10)
    gp = L.get("voto_sufficienza", 0)
    grades = f"""<?xml version="1.0" encoding="UTF-8"?>
<activity_gradebook>
  <grade_items>
    <grade_item id="99801">
      <categoryid>1</categoryid>
      <itemname>{x(nome)}</itemname>
      <itemtype>mod</itemtype>
      <itemmodule>quiz</itemmodule>
      <iteminstance>{quiz_id}</iteminstance>
      <itemnumber>0</itemnumber>
      <iteminfo>{NULL}</iteminfo>
      <idnumber></idnumber>
      <calculation>{NULL}</calculation>
      <gradetype>1</gradetype>
      <grademax>{voto:.5f}</grademax>
      <grademin>0.00000</grademin>
      <scaleid>{NULL}</scaleid>
      <outcomeid>{NULL}</outcomeid>
      <gradepass>{gp:.5f}</gradepass>
      <multfactor>1.00000</multfactor>
      <plusfactor>0.00000</plusfactor>
      <aggregationcoef>0.00000</aggregationcoef>
      <aggregationcoef2>0.00000</aggregationcoef2>
      <weightoverride>0</weightoverride>
      <sortorder>1</sortorder>
      <display>0</display>
      <decimals>{NULL}</decimals>
      <hidden>0</hidden>
      <locked>0</locked>
      <locktime>0</locktime>
      <needsupdate>0</needsupdate>
      <timecreated>{ora}</timecreated>
      <timemodified>{ora}</timemodified>
      <grade_grades>
      </grade_grades>
    </grade_item>
  </grade_items>
  <grade_letters>
  </grade_letters>
</activity_gradebook>"""
    module = f"""<?xml version="1.0" encoding="UTF-8"?>
<module id="{mid}" version="2026042000">
  <modulename>quiz</modulename>
  <sectionid>{sec_corso}</sectionid>
  <sectionnumber>1</sectionnumber>
  <idnumber></idnumber>
  <added>{ora}</added>
  <score>0</score>
  <indent>0</indent>
  <visible>1</visible>
  <visibleoncoursepage>1</visibleoncoursepage>
  <visibleold>1</visibleold>
  <groupmode>0</groupmode>
  <groupingid>0</groupingid>
  <completion>0</completion>
  <completiongradeitemnumber>{NULL}</completiongradeitemnumber>
  <completionpassgrade>0</completionpassgrade>
  <completionview>0</completionview>
  <completionexpected>0</completionexpected>
  <availability>{NULL}</availability>
  <showdescription>0</showdescription>
  <downloadcontent>1</downloadcontent>
  <lang></lang>
  <enableaitools>{NULL}</enableaitools>
  <enabledaiactions>{NULL}</enabledaiactions>
  <tags>
  </tags>
</module>"""
    inforef = f"""<?xml version="1.0" encoding="UTF-8"?>
<inforef>
  <grade_itemref>
    <grade_item>
      <id>99801</id>
    </grade_item>
  </grade_itemref>
  <question_categoryref>
    <question_category>
      <id>{cat_top}</id>
    </question_category>
    <question_category>
      <id>{cat_def}</id>
    </question_category>
    <question_category>
      <id>{cat_q}</id>
    </question_category>
  </question_categoryref>
</inforef>"""
    # file allegati (database SQL delle domande CodeRunner): voci in files.xml + contenuto in files/xx/hash
    import hashlib
    CON_FILE = 1 if banca.file_domande else 0
    blob = {}
    fx = ""
    fid = 99801
    for qid_f, nome_f, dati_f in banca.file_domande:
        h = hashlib.sha1(dati_f).hexdigest()
        blob["files/%s/%s" % (h[:2], h)] = dati_f
        for fn, hh, sz, mt in ((nome_f, h, len(dati_f), "document/unknown"),
                               (".", "da39a3ee5e6b4b0d3255bfef95601890afd80709", 0, NULL)):
            fx += f"""  <file id="{fid}">
    <contenthash>{hh}</contenthash>
    <contextid>{ctx}</contextid>
    <component>qtype_coderunner</component>
    <filearea>datafile</filearea>
    <itemid>{qid_f}</itemid>
    <filepath>/</filepath>
    <filename>{x(fn)}</filename>
    <userid>{NULL}</userid>
    <filesize>{sz}</filesize>
    <mimetype>{mt}</mimetype>
    <status>0</status>
    <timecreated>{ora}</timecreated>
    <timemodified>{ora}</timemodified>
    <source>{NULL}</source>
    <author>{NULL}</author>
    <license>{NULL}</license>
    <sortorder>0</sortorder>
    <repositorytype>{NULL}</repositorytype>
    <repositoryid>{NULL}</repositoryid>
    <reference>{NULL}</reference>
  </file>
"""
            fid += 1
    files_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<files>\n' + fx + '</files>'
    bname = "backup-moodle2-activity-%d-quiz%d-%s-nu-nf.mbz" % (mid, mid, time.strftime("%Y%m%d-%H%M"))
    backup = f"""<?xml version="1.0" encoding="UTF-8"?>
<moodle_backup>
  <information>
    <name>{bname}</name>
    <moodle_version>{MOODLE_VERSION}</moodle_version>
    <moodle_release>{MOODLE_RELEASE}</moodle_release>
    <backup_version>{BACKUP_VERSION}</backup_version>
    <backup_release>{BACKUP_RELEASE}</backup_release>
    <backup_date>{ora}</backup_date>
    <mnet_remoteusers>0</mnet_remoteusers>
    <include_files>{CON_FILE}</include_files>
    <include_file_references_to_external_content>0</include_file_references_to_external_content>
    <original_wwwroot>https://salvemini.synology.me/moodle</original_wwwroot>
    <original_site_identifier_hash>8568b3483d0e2ab302ef2738533ac213</original_site_identifier_hash>
    <original_course_id>7</original_course_id>
    <original_course_format>multitopic</original_course_format>
    <original_course_fullname>Quarte SIA - Deposito</original_course_fullname>
    <original_course_shortname>QuarteSIAdep</original_course_shortname>
    <original_course_startdate>1753308000</original_course_startdate>
    <original_course_enddate>1784844000</original_course_enddate>
    <original_course_contextid>272</original_course_contextid>
    <original_system_contextid>1</original_system_contextid>
    <details>
      <detail backup_id="{''.join(random.choice('0123456789abcdef') for _ in range(32))}">
        <type>activity</type>
        <format>moodle2</format>
        <interactive>1</interactive>
        <mode>70</mode>
        <execution>2</execution>
        <executiontime>0</executiontime>
      </detail>
    </details>
    <contents>
      <activities>
        <activity>
          <moduleid>{mid}</moduleid>
          <sectionid>{sec_corso}</sectionid>
          <modulename>quiz</modulename>
          <title>{x(nome)}</title>
          <directory>{adir}</directory>
          <insubsection></insubsection>
        </activity>
      </activities>
    </contents>
    <settings>
""" + "".join(f"""      <setting>
        <level>root</level>
        <name>{n}</name>
        <value>{v}</value>
      </setting>
""" for n, v in [("filename", bname), ("users", 0), ("anonymize", 0), ("role_assignments", 0),
                 ("activities", 1), ("blocks", 0), ("files", CON_FILE), ("filters", 0), ("comments", 0),
                 ("badges", 0), ("calendarevents", 0), ("userscompletion", 0), ("logs", 0),
                 ("grade_histories", 0), ("groups", 0), ("competencies", 0), ("customfield", 0),
                 ("contentbankcontent", 0), ("xapistate", 0), ("legacyfiles", 0)]) + f"""      <setting>
        <level>activity</level>
        <activity>quiz_{mid}</activity>
        <name>quiz_{mid}_included</name>
        <value>1</value>
      </setting>
      <setting>
        <level>activity</level>
        <activity>quiz_{mid}</activity>
        <name>quiz_{mid}_userinfo</name>
        <value>0</value>
      </setting>
    </settings>
  </information>
</moodle_backup>"""
    vuoti = {
        "completion.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<course_completion>\n</course_completion>',
        "files.xml": files_xml,
        "groups.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<groups>\n  <groupcustomfields>\n  </groupcustomfields>\n  <groupings>\n    <groupingcustomfields>\n    </groupingcustomfields>\n  </groupings>\n</groups>',
        "outcomes.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<outcomes_definition>\n</outcomes_definition>',
        "roles.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<roles_definition>\n</roles_definition>',
        "scales.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<scales_definition>\n</scales_definition>',
        adir + "/grade_history.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<grade_history>\n  <grade_grades>\n  </grade_grades>\n</grade_history>',
        adir + "/roles.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<roles>\n  <role_overrides>\n  </role_overrides>\n  <role_assignments>\n  </role_assignments>\n</roles>',
    }
    files = {adir + "/grades.xml": grades, adir + "/module.xml": module, adir + "/inforef.xml": inforef,
             adir + "/quiz.xml": quiz, "moodle_backup.xml": backup, "questions.xml": questions,
             "moodle_backup.log": ""}
    files.update(vuoti)
    ordine = ([adir + "/" + n for n in ("grade_history.xml", "grades.xml", "module.xml", "inforef.xml",
                                        "quiz.xml", "roles.xml")]
              + ["completion.xml", "files.xml", "groups.xml", "moodle_backup.xml", "outcomes.xml",
                 "questions.xml", "roles.xml", "scales.xml", "moodle_backup.log"])

    # tar.gz con .ARCHIVE_INDEX per primo, come fa Moodle
    voci = [("activities/", None), (adir + "/", None)] + [(p, files[p].encode("utf-8")) for p in ordine]
    if blob:
        cart = sorted({"files/"} | {"files/%s/" % k.split("/")[1] for k in blob})
        voci += [(c, None) for c in cart] + [(k, v) for k, v in sorted(blob.items())]
    indice = "Moodle archive file index. Count: %d\n" % len(voci)
    for p, dati in voci:
        indice += "%s\t%s\t%s\t%s\n" % (p, "d" if dati is None else "f", 0 if dati is None else len(dati),
                                        "?" if dati is None else ora)
    with tarfile.open(out, "w:gz") as tar:
        def aggiungi(p, dati, cartella=False):
            ti = tarfile.TarInfo(p.rstrip("/"))
            ti.mtime = ora
            ti.uid = ti.gid = 0
            if cartella:
                ti.type, ti.mode, ti.size = tarfile.DIRTYPE, 0o755, 0
                tar.addfile(ti)
            else:
                ti.mode, ti.size = 0o644, len(dati)
                tar.addfile(ti, io.BytesIO(dati))
        aggiungi(".ARCHIVE_INDEX", indice.encode("utf-8"))
        for p, dati in voci:
            aggiungi(p, dati, cartella=dati is None)

    n_cas = sum(1 for r in righe if r.get("casuale"))
    print("OK: %d posizioni%s, %d domande nella banca (%d voci), %d sezioni, %.1f punti -> %s"
          % (len(righe), " (%d casuali per tag)" % n_cas if n_cas else "", len(domande), len(banca.out),
             len(L["sezioni"]), sum(r["punti"] for r in righe), out))


if __name__ == "__main__":
    main()
