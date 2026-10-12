#!/usr/bin/env python3
"""Dal database della dashboard «Bozze dei quiz» alla specifica di crea_xml.py e
all'impaginazione di crea_mbz.py. Nessuna ritrascrizione a mano: tutto quello che
finisce in Moodle è scritto nella dashboard con le convenzioni di formato-consegna.md.

Uso:
    python3 da_dashboard.py EXPORT QUIZ_ID USCITA [--preset=esercitazione|verifica] [--salta-coderunner]
                            [--varianti=a[,b...]]

EXPORT   cartella con l'esportazione del database (ArtifactData con out_dir):
         EXPORT/quiz/QUIZ_ID.json e EXPORT/quiz/QUIZ_ID/domande/*.json
USCITA   cartella dove scrivere specifica.txt e impaginazione.json

Le righe CodeRunner JavaScript vanno in USCITA/specifica-js.txt, nel formato della skill
domande-coderunner-js: le sezioni del campo «Soluzione e test» più nome, testo, punti e note.
Le righe CodeRunner SQL vanno in USCITA/specifica-sql.txt, nel formato della skill
domande-coderunner-sql, con i database del quiz (campo `database`: {nome: script SQL}) in testa.
Le righe CodeRunner PHP vanno in USCITA/specifica-php.txt, nel formato di domande-php-mysqli-mock (prototipo
php_mysqli_sqlite), con disclaimer, normalizzazione dell'output e FakeDB::configure aggiunti; gli output
attesi non scritti restano @@CALCOLA@@ e li calcola php_attesi.py.
Gli esercizi liberi HTML e CSS (CodeRunner html/css senza test, correzione manuale) e le
corrispondenze, che crea_xml.py non gestisce, vanno direttamente in USCITA/domande-dirette.xml.
Tutta la catena (XML, XML CodeRunner, unione, controllo, .mbz) la esegue genera_quiz.py.

Si ferma con l'elenco degli errori se una riga non rispetta le convenzioni.
--salta-coderunner  lascia fuori le righe CodeRunner di linguaggi non gestiti (si producono con le loro
                    skill e si uniscono con unisci_xml.py).
--varianti=a        verifiche ripetibili: converte solo le varianti indicate (lettera finale della posizione:
                    T1a, Q3a…); le righe senza tag restano tutte. Serve quando le altre varianti non sono ancora
                    scritte: la variante «a» si genera subito, la «b» e la «c» quando servono (recupero).

Nomi e categoria: con una lezione numerica «L<lezione> - <pos> - …» e «Lezione <lezione> - <argomento>»;
con una lezione non numerica (le verifiche, per esempio «V5R», o un codice automatico come «4K7») «V5R - <pos> - …» e «V5R - <argomento>».
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from moodle_lib import CAMPO_RE, cdata, esc_xml, espandi_codice, xml_categoria, percorso_categoria  # noqa: E402

# ---------------------------------------------------------------- catalogo (stesso della dashboard)
# tipologia -> (tipo Moodle, prefisso del nome)
CATALOGO = {
    "istruzioni": ("description", ""), "comelavoriamo": ("description", ""),
    "paginablocco": ("description", "Spiegazione"),
    "vf": ("truefalse", ""), "multipla": ("multichoice", ""), "crocette": ("multichoice", ""),
    "breve": ("shortanswer", ""), "corrispondenza": ("matching", ""),
    "cloze_testo": ("cloze", ""), "ordine": ("cloze", ""), "teoria_aperta": ("essay", ""),
    "esempio_svolto": ("cloze", "Esempio svolto"), "tracciamento": ("cloze", "Tracciamento"),
    "lettura_output": ("cloze", "Tracciamento"), "trova_errore": ("multichoice", "Trova l'errore"),
    "compl_campi": ("cloze", "Completamento"), "guidato": ("cloze", "Esempio guidato"),
    "debug_motivazione": ("essay", "Debug"), "esercizio_libero": ("essay", "Esercizio libero"),
}
CODERUNNER = {"compl_eseguito", "scrittura_scheletro", "debug_msg", "debug_silenzioso", "prog_completo",
              "funzione", "prog_dati", "prog_random", "query", "create_tabelle", "query_due_passi",
              "vincoli", "pagina_php", "campo_prova", "libero_html", "libero_css"}
# esercizi liberi con l'editor di CodeRunner (prototipi html e css): nessun test, correzione manuale
CR_WEB = {"libero_html": "html", "libero_css": "css"}
# prototipo Moodle di ogni esercizio libero. L'HTML lo sceglie il quiz (campo prototipoHtml): di norma php_con_test,
# che ha lo scratchpad (lo studente prova il codice e vede la pagina interpretata; risposta e codice di partenza nel
# formato JSON dello scratchpad); «html» per gli esercizi senza anteprima, in cui il campo serve solo a incollare il
# codice scritto in un editor e provato nel browser.
PROTOTIPO_WEB = {"libero_html": "php_con_test", "libero_css": "css"}
PROTOTIPI_HTML = ("php_con_test", "html")


def prototipo_web(quiz, tipologia):
    """Prototipo CodeRunner di un esercizio libero HTML o CSS, secondo il campo prototipoHtml del quiz."""
    if tipologia == "libero_html":
        p = (quiz.get("prototipoHtml") or "php_con_test").strip()
        if p not in PROTOTIPI_HTML:
            raise ValueError("prototipoHtml '%s' non previsto (solo php_con_test o html)" % p)
        return p
    return PROTOTIPO_WEB[tipologia]
# prefissi del nome per le tipologie CodeRunner (come nel catalogo della dashboard)
PREFISSI_CR = {"compl_eseguito": "Completamento", "scrittura_scheletro": "Scrivere", "debug_msg": "Debug",
               "debug_silenzioso": "Debug", "prog_completo": "Scrivere", "funzione": "Scrivere",
               "prog_dati": "Scrivere", "prog_random": "Scrivere", "query": "Scrivere",
               "create_tabelle": "Scrivere", "query_due_passi": "Scrivere", "vincoli": "Esercizio",
               "pagina_php": "Scrivere", "campo_prova": "Campo di prova",
               "libero_html": "Esercizio libero", "libero_css": "Esercizio libero"}
CR_SQL = {"query", "create_tabelle", "query_due_passi", "vincoli", "campo_prova"}
CR_PHP = {"pagina_php"}
# tipi di quiz in cui la pagina del blocco è un ripasso e non una spiegazione nuova
TIPI_RIPASSO = {"RT", "ER"}
PRESET_MBZ = {"ED": "esercitazione", "EDT": "esercitazione", "EP": "esercitazione", "ER": "esercitazione", "RT": "esercitazione",
              "V": "verifica", "VT": "verifica"}

# ---------------------------------------------------------------- stile HTML (materiali-moodle)
FONT = ("font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 900px; "
        "margin: 0 auto; color: #333333; line-height: 1.6;")
H1S = "color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;"
H2S = "color: #c0392b; margin-top: 30px;"
LISTS = "margin: 0 0 12px;"
BOX = {"blu": ("#c9daf8", "#6d9eeb", "#1c4587"), "giallo": ("#fff2cc", "#f1c232", "#7f6000"),
       "verde": ("#d9ead3", "#93c47d", "#274e13"), "arancio": ("#f9cb9c", "#e69138", "#783f04"),
       "rosso": ("#f4cccc", "#e06666", "#660000")}
TH = "border: 1px solid #999999; padding: 4px 8px; background-color: #eeeeee; text-align: left;"
TD = "border: 1px solid #999999; padding: 4px 8px; background-color: #ffffff;"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inl(t):
    """Testo in linea: `codice`, **grassetto**, *corsivo*. I campi Cloze restano così come sono."""
    campi = []

    def tieni(m):
        campi.append(m.group(0))
        return "\x00%d\x00" % (len(campi) - 1)
    t = CAMPO_RE.sub(tieni, t)
    out = ""
    for p in re.split(r"(`[^`]+`)", t):
        if len(p) > 2 and p[0] == "`" and p[-1] == "`":
            out += '<span style="font-family: monospace;">%s</span>' % esc(p[1:-1])
        else:
            s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", esc(p))
            s = re.sub(r"__(.+?)__", r"<u>\1</u>", s)
            out += re.sub(r"(?<![*\w])\*([^*\s][^*]*)\*(?![*\w])", r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: campi[int(m.group(1))], out)


def P(t, style=""):
    # \x01 = a capo dentro il paragrafo (leggi_blocchi): diventa <br>, come nell'anteprima della dashboard
    return "<p%s>%s</p>" % (' style="%s"' % style if style else "", inl(t).replace("\x01", "<br>\n"))


# ---------------------------------------------------------------- Markdown -> blocchi
OPZ_RE = re.compile(r"^\s*([(\[])\s*(x)?\s*(-?\d+(?:[.,]\d+)?)?\s*%?\s*([)\]])\s+(.*)$")


def leggi_blocchi(src):
    """Restituisce una lista di blocchi (tipo, dati). Tipi: h1 h2 h3 p ul ol code table box opzioni."""
    L = (src or "").replace("\r", "").split("\n")
    out, i = [], 0
    while i < len(L):
        ln = L[i]
        if ln.startswith("```"):
            lang = ln[3:].strip() or "html"
            buf = []
            i += 1
            while i < len(L) and not L[i].startswith("```"):
                buf.append(L[i])
                i += 1
            i += 1
            out.append(("code", (lang, "\n".join(buf))))
            continue
        if not ln.strip():
            i += 1
            continue
        m = re.match(r"^:::(\w+)\s*(.*)$", ln)
        if m:
            col, titolo, buf, livello = m.group(1), m.group(2).strip(), [], 1
            i += 1
            while i < len(L):
                if re.match(r"^:::\w", L[i]):
                    livello += 1
                elif L[i].strip() == ":::":
                    livello -= 1
                    if livello == 0:
                        break
                buf.append(L[i])
                i += 1
            i += 1
            out.append(("box", (col, titolo, leggi_blocchi("\n".join(buf)))))
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", ln)
        if m:
            out.append(("h%d" % len(m.group(1)), m.group(2)))
            i += 1
            continue
        if ln.strip().startswith("|") and i + 1 < len(L) and re.match(r"^\s*\|[\s:|-]+\|\s*$", L[i + 1]):
            celle = lambda l: [c.strip() for c in l.strip().strip("|").split("|")]
            head = celle(ln)
            i += 2
            rows = []
            while i < len(L) and L[i].strip().startswith("|"):
                rows.append(celle(L[i]))
                i += 1
            out.append(("table", (head, rows)))
            continue
        if OPZ_RE.match(ln):
            opz = []
            while i < len(L) and (OPZ_RE.match(L[i]) or re.match(r"^\s*>", L[i]) or
                                  (not L[i].strip() and i + 1 < len(L) and OPZ_RE.match(L[i + 1]))):
                if not L[i].strip():
                    i += 1
                    continue
                m = OPZ_RE.match(L[i])
                if m:
                    perc = m.group(3)
                    opz.append({"multi": m.group(1) == "[", "giusta": bool(m.group(2)),
                                "perc": float(perc.replace(",", ".")) if perc else None,
                                "testo": m.group(5).strip(), "feedback": ""})
                else:
                    fb = re.sub(r"^\s*>\s?", "", L[i]).strip()
                    opz[-1]["feedback"] = (opz[-1]["feedback"] + " " + fb).strip()
                i += 1
            out.append(("opzioni", opz))
            continue
        lista = re.match(r"^\s*([-*]|\d+[.)])\s+", ln)
        if lista:
            ordinata = lista.group(1)[0].isdigit()
            pat = r"^\s*\d+[.)]\s+" if ordinata else r"^\s*[-*]\s+"
            it = []
            while i < len(L) and re.match(pat, L[i]):
                it.append(re.sub(pat, "", L[i]))
                i += 1
            out.append(("ol" if ordinata else "ul", it))
            continue
        buf = [ln]
        i += 1
        while (i < len(L) and L[i].strip() and not L[i].startswith("```") and not L[i].startswith(":::")
               and not re.match(r"^\s*([-*]\s+|\d+[.)]\s+|\||#{1,3}\s)", L[i]) and not OPZ_RE.match(L[i])):
            buf.append(L[i])
            i += 1
        # ogni a capo dentro un paragrafo è un a capo vero (<br>), come nell'anteprima della dashboard;
        # i due spazi finali del Markdown non servono ma non disturbano
        out.append(("p", "\x01".join(r.rstrip() for r in buf)))
    return out


def html_blocchi(bl, in_box=False, pagina=False):
    out = []
    for n, (tipo, dati) in enumerate(bl):
        dopo = bl[n + 1][0] if n + 1 < len(bl) else None
        if tipo == "h1":
            out.append('<h1 style="%s">%s</h1>' % (H1S, inl(dati)))
        elif tipo == "h2":
            out.append('<h2 style="%s">%s</h2>' % (H2S, inl(dati)))
        elif tipo == "h3":
            out.append("<h3>%s</h3>" % inl(dati))
        elif tipo == "p":
            stile = ""
            if in_box:
                stile = "margin: 0;" if dopo is None else ("margin: 0 0 8px;" if dopo == "code" else "")
            elif pagina and dopo is None:
                stile = "margin-bottom: 0;"
            out.append(P(dati, stile))
        elif tipo in ("ul", "ol"):
            out.append('<%s style="%s">\n%s\n</%s>' % (tipo, LISTS, "\n".join("<li>%s</li>" % inl(x) for x in dati), tipo))
        elif tipo == "code":
            lang, codice = dati
            out.append("[[codice %s]]\n%s\n[[/codice]]" % (lang, codice.strip("\n")))
        elif tipo == "table":
            head, rows = dati
            h = "<tr>" + "".join('<th style="%s">%s</th>' % (TH, inl(c)) for c in head) + "</tr>"
            b = "\n".join("<tr>" + "".join('<td style="%s">%s</td>' % (TD, inl(c)) for c in r) + "</tr>" for r in rows)
            out.append('<table style="border-collapse: collapse; margin: 8px 0;">\n<thead>\n%s\n</thead>\n'
                       '<tbody>\n%s\n</tbody>\n</table>' % (h, b))
        elif tipo == "box":
            col, titolo, interni = dati
            if col not in BOX:
                raise ValueError("riquadro di colore sconosciuto «%s» (ammessi: %s)" % (col, ", ".join(BOX)))
            s, b, t = BOX[col]
            out.append('<div style="background-color: %s; border-left: 5px solid %s; padding: 12px 16px; '
                       'border-radius: 4px; margin: 0 0 16px;">\n<p style="margin: 0 0 6px; color: %s;">'
                       '<strong>%s</strong></p>\n%s\n</div>' % (s, b, t, esc(titolo), html_blocchi(interni, in_box=True)))
        elif tipo == "opzioni":
            raise ValueError("opzioni ( ) / [ ] in un tipo di domanda che non le prevede")
    return "\n".join(out)


# ---------------------------------------------------------------- righe -> specifica

def carica(export, qid):
    def dati(p):
        d = json.load(open(p, encoding="utf-8"))
        return d.get("data", d), d.get("id") or os.path.basename(p)[:-5]
    quiz, _ = dati(os.path.join(export, "quiz", qid + ".json"))
    righe = []
    for p in glob.glob(os.path.join(export, "quiz", qid, "domande", "*.json")):
        d, rid = dati(p)
        d["id"] = rid
        righe.append(d)
    righe.sort(key=lambda r: float(r.get("ordine") or 0))
    return quiz, righe


def nome_moodle(quiz, r):
    tipo, pre = CATALOGO.get(r.get("tipologia"), ("", PREFISSI_CR.get(r.get("tipologia"), "")))
    if r.get("tipologia") == "paginablocco" and quiz.get("tipoQuiz") in TIPI_RIPASSO:
        pre = "Ripasso"
    return "%s - %s - %s%s" % (prefisso_lezione(quiz), r.get("pos") or "??", pre + ": " if pre else "", r.get("titolo") or "")


def prefisso_lezione(quiz):
    """«L3» per una lezione numerica; il codice così com'è per le verifiche senza lezione («V5R»)."""
    lez = str(quiz.get("lezione") or "").strip() or "?"
    return ("L" + lez) if lez.isdigit() or lez == "?" else lez


def categoria_quiz(quiz):
    lez = str(quiz.get("lezione") or "").strip() or "?"
    arg = quiz.get("argomento") or quiz.get("titolo") or ""
    return ("Lezione %s - %s" % (lez, arg)) if lez.isdigit() or lez == "?" else ("%s - %s" % (lez, arg))


def numero(x):
    return ("%g" % float(x)) if x not in (None, "") else "0"


def sezioni_cr(testo):
    """Sezioni '=== nome arg' del campo «Soluzione e test», in ordine: [(nome, arg, contenuto)]."""
    out, cur = [], None
    for ln in (testo or "").replace("\r", "").split("\n"):
        m = re.match(r"^=== *(\w+)(?:\s+(.*))?$", ln)
        if m:
            cur = [m.group(1).lower(), (m.group(2) or "").strip(), []]
            out.append(cur)
        elif cur is not None:
            cur[2].append(ln)
    return [(n, a, "\n".join(c).strip("\n")) for n, a, c in out]


def linguaggio_cr(r):
    if r.get("tipologia") in CR_WEB:
        return CR_WEB[r["tipologia"]]
    for n, a, c in sezioni_cr(r.get("coderunner")):
        if n == "linguaggio":
            return (c.strip() or a).lower()
    t = r.get("tipologia")
    if t in CR_SQL:
        return "sql"
    if t in CR_PHP:
        return "php"
    # tipologie comuni a più linguaggi (debug, codice parziale): PHP se la soluzione inizia con <?php
    # o i test usano $_GET, $_POST o FakeDB; SQL se i test iniziano con «--» o con [[struttura]];
    # altrimenti JavaScript
    sez = sezioni_cr(r.get("coderunner"))
    for n, a, c in sez:
        if (n == "answer" and c.lstrip().startswith("<?php")) or \
                (n == "test" and re.search(r"\$_(GET|POST)\b|FakeDB::", c)):
            return "php"
    for n, a, c in sez:
        if n == "test":
            if re.match(r"\s*(--|\[\[struttura)", c):
                return "sql"
            break
    return "js"


def domanda_cr(quiz, r):
    """Specifica di domande-coderunner-js per una riga CodeRunner JavaScript."""
    sez = sezioni_cr(r.get("coderunner"))
    if not sez:
        raise ValueError("domanda CodeRunner senza «Soluzione e test»")
    nomi = [n for n, _, _ in sez]
    if "answer" not in nomi or not any(n == "test" for n in nomi):
        raise ValueError("«Soluzione e test» senza === answer o senza === test")
    gap = r.get("tipologia") == "compl_eseguito" or "code" in nomi
    tr = r.get("traccia") or ""
    if CAMPO_RE.search(tr) or any(t == "opzioni" for t, _ in leggi_blocchi(tr)):
        raise ValueError("in una domanda CodeRunner la traccia non ha campi Cloze né opzioni")
    testo = html_blocchi(leggi_blocchi(tr))
    opz = ["defaultgrade: %s" % numero(r.get("punti"))]
    corpo = []
    for n, a, c in sez:
        if n == "linguaggio":
            continue
        if n == "options":
            opz += [l.strip() for l in c.split("\n") if l.strip() and not l.strip().startswith("defaultgrade")]
            continue
        corpo += ["=== %s%s" % (n, (" " + a) if a else ""), c]
    s = ["=== question %s" % ("gapfiller" if gap else "prompt"), "=== name", nome_moodle(quiz, r),
         "=== options"] + opz
    note = (r.get("docente") or "").strip()
    if note:
        s += ["=== note", note]
    s += ["=== questiontext", testo]
    correzione = (r.get("correzione") or "").strip()
    if correzione:
        s += ["=== generalfeedback", html_blocchi(leggi_blocchi(correzione))]
    return "\n".join(s + corpo)


def databases_quiz(quiz):
    """Database del quiz: campo `database` del documento, [{nome, sql}] (o {nome: sql}): script SQL
    di CREATE e INSERT come in phpMyAdmin."""
    d = quiz.get("database") or {}
    if isinstance(d, str):
        d = {"db": d}
    elif isinstance(d, list):   # come lo salva la dashboard: [{nome, sql}]
        d = {str(x.get("nome") or ""): x.get("sql") or "" for x in d if isinstance(x, dict)}
    out = {k.strip(): v for k, v in d.items() if k.strip() and str(v or "").strip()}
    for k in out:
        if re.search(r"\s", k):
            raise SystemExit("ERRORE: il nome del database «%s» contiene spazi" % k)
    return out


SEZ_SQL = {"answer", "preload", "test", "extra", "expected", "options"}


def domanda_sql(quiz, r):
    """Specifica di domande-coderunner-sql per una riga CodeRunner SQL (prototipo sql_salvemini)."""
    sez = sezioni_cr(r.get("coderunner"))
    if not sez:
        raise ValueError("domanda CodeRunner senza «Soluzione e test»")
    nomi = [n for n, _, _ in sez]
    if "answer" not in nomi or "test" not in nomi:
        raise ValueError("«Soluzione e test» senza === answer o senza === test")
    for n in nomi:
        if n not in SEZ_SQL and n != "linguaggio":
            raise ValueError("sezione === %s non prevista nelle domande SQL (answer, preload, test, extra, "
                             "expected, options)" % n)
    tr = r.get("traccia") or ""
    if CAMPO_RE.search(tr) or any(t == "opzioni" for t, _ in leggi_blocchi(tr)):
        raise ValueError("in una domanda CodeRunner la traccia non ha campi Cloze né opzioni")
    dbs = databases_quiz(quiz)
    opz = ["defaultgrade: %s" % numero(r.get("punti"))]
    corpo = []
    for n, a, c in sez:
        if n == "linguaggio":
            continue
        if n == "options":
            opz += [l.strip() for l in c.split("\n") if l.strip() and not l.strip().startswith("defaultgrade")]
            continue
        corpo += ["=== %s%s" % (n, (" " + a) if a else ""), c]
    scelto = [l.split(":", 1)[1].strip() for l in opz if l.split(":", 1)[0].strip() == "database"]
    if scelto and scelto[-1] not in dbs:
        raise ValueError("database «%s» non definito nel quiz (database del quiz: %s)"
                         % (scelto[-1], ", ".join(dbs) or "nessuno"))
    if not scelto and len(dbs) > 1:
        raise ValueError("il quiz ha più database (%s): indica quale con «database: nome» in === options"
                         % ", ".join(dbs))
    s = ["=== question", "=== name", nome_moodle(quiz, r), "=== options"] + opz
    note = (r.get("docente") or "").strip()
    if note:
        s += ["=== note", note]
    s += ["=== questiontext", html_blocchi(leggi_blocchi(tr))]
    correzione = (r.get("correzione") or "").strip()
    if correzione:
        s += ["=== generalfeedback", html_blocchi(leggi_blocchi(correzione))]
    return "\n".join(s + corpo)


DISCLAIMER_PHP = """<div style="background-color: #f9cb9c; border-left: 5px solid #e69138; padding: 12px 16px; border-radius: 4px; margin: 0 0 16px;">
<p style="margin: 0 0 6px; color: #783f04;"><strong>N.B. questa è una simulazione</strong></p>
<p style="margin: 0 0 6px;">Il tuo codice PHP viene eseguito davvero, ma dietro non c'è un database MySQL permanente: c'è un database di prova, che non conserva le modifiche. A ogni prova riparte sempre dagli stessi dati. Il comportamento e i messaggi d'errore possono essere diversi da quelli di un vero database MySQL.</p>
<p style="margin: 0;">Per realizzare davvero le pagine occorre usare XAMPP con un vero database MySQL.</p>
</div>"""
NORMALIZZA_PHP = """// ---- output normalizzato: spazi e a capo dello studente non contano ----
ob_start();
register_shutdown_function(function () {
    $out = trim((string)ob_get_clean());
    $out = preg_replace('/>\\s+</', '><', $out);
    $out = preg_replace('#(<table[^>]*>|</table>|</tr>|<ul[^>]*>|</ul>|<ol[^>]*>|</ol>|</li>|</p>|</h[1-6]>|<br\\s*/?>)#i', '$1' . "\\n", $out);
    echo rtrim($out) . "\\n";
});
"""
SEZ_PHP = {"answer", "preload", "test", "descrizione", "expected", "options", "linguaggio"}
OPZ_PHP = {"prototipo", "database", "penalty", "allornothing", "penaltyregime", "precheck", "hidecheck",
           "showsource", "answerboxlines", "answerboxcolumns", "validateonsave", "displayfeedback",
           "giveupallowed"}


def domanda_php(quiz, r):
    """Specifica di domande-php-mysqli-mock (prototipo php_mysqli_sqlite) per una riga CodeRunner PHP.
    Il disclaimer della simulazione, la normalizzazione dell'output e FakeDB::configure si aggiungono da soli;
    gli output attesi mancanti li calcola php_attesi.py (segnaposto @@CALCOLA@@)."""
    sez = sezioni_cr(r.get("coderunner"))
    if not sez:
        raise ValueError("domanda CodeRunner senza «Soluzione e test»")
    nomi = [n for n, _, _ in sez]
    if "answer" not in nomi or "test" not in nomi:
        raise ValueError("«Soluzione e test» senza === answer o senza === test")
    for n in nomi:
        if n not in SEZ_PHP:
            raise ValueError("sezione === %s non prevista nelle domande PHP (answer, preload, test, descrizione, "
                             "expected, options)" % n)
    tr = r.get("traccia") or ""
    if CAMPO_RE.search(tr) or any(t == "opzioni" for t, _ in leggi_blocchi(tr)):
        raise ValueError("in una domanda CodeRunner la traccia non ha campi Cloze né opzioni")
    dbs = databases_quiz(quiz)
    opz, normalizza, base = ["defaultgrade: %s" % numero(r.get("punti"))], True, None
    for n, a, c in sez:
        if n == "options":
            for l in c.split("\n"):
                k, _, v = l.partition(":")
                k, v = k.strip(), v.strip()
                if not k or k == "defaultgrade":
                    continue
                if k == "normalizza":
                    normalizza = v not in ("0", "no", "false")
                elif k in OPZ_PHP:
                    opz.append("%s: %s" % (k, v))
                    if k == "database":
                        base = v
                else:
                    raise ValueError("opzione «%s» non prevista nelle domande PHP" % k)
    if base is None:
        if len(dbs) != 1:
            raise ValueError("indica il database con «database: nome» in === options (database del quiz: %s)"
                             % (", ".join(dbs) or "nessuno"))
        base = next(iter(dbs))
    if base not in dbs:
        raise ValueError("database «%s» non definito nel quiz" % base)
    s = ["=== question", "=== name", nome_moodle(quiz, r), "=== options"] + opz
    note = (r.get("docente") or "").strip()
    if note:
        s += ["=== note", note]
    s += ["=== questiontext", html_blocchi(leggi_blocchi(tr)) + "\n" + DISCLAIMER_PHP]
    configura = "FakeDB::configure(['user' => 'root', 'password' => '', 'database' => '%s']);" % base
    k = 0
    while k < len(sez):
        n, a, c = sez[k]
        if n in ("preload", "answer"):
            s += ["=== " + n, c]
        elif n == "test":
            codice = c if "FakeDB::configure" in c else c.rstrip() + "\n" + configura
            if normalizza:
                codice = NORMALIZZA_PHP + "\n" + codice
            s += ["=== test%s" % (" HIDE" if "HIDE" in a.upper() else ""), codice]
            desc, atteso = "", None
            while k + 1 < len(sez) and sez[k + 1][0] in ("descrizione", "expected"):
                k += 1
                if sez[k][0] == "descrizione":
                    desc = sez[k][2]
                else:
                    atteso = sez[k][2]
            if desc:
                s += ["=== descrizione", desc]
            s += ["=== expected", atteso if atteso is not None else "@@CALCOLA@@"]
        k += 1
    return "\n".join(s)


AVVISO_WEB = """:::arancio Attenzione al controllo automatico
Il pulsante di controllo sotto il campo della risposta **non esegue alcun test sul codice** e non dice se la pagina è corretta: serve solo a salvare il codice. I requisiti vanno verificati aprendo la pagina nel browser; la correzione la fa il docente.
:::"""
AVVISO_SCRATCHPAD = """:::arancio Attenzione al controllo automatico
Il pulsante di controllo sotto il campo della risposta **non esegue alcun test sul codice** e non dice se la pagina è corretta: serve solo a salvare il codice. Per vedere come appare la pagina usate l'area di prova (scratchpad) sotto la risposta: mostra l'HTML interpretato, come nel browser. La correzione la fa il docente.
:::"""


def json_scratchpad(codice, prefisso=""):
    """Risposta o codice di partenza nel formato del prototipo php_con_test (interfaccia scratchpad)."""
    return json.dumps({"answer_code": [codice], "test_code": [""], "show_hide": [""], "prefix_ans": [prefisso]},
                      ensure_ascii=False)
OPZIONI_WEB = {"answerboxlines": "18", "answerboxcolumns": "100"}


def domanda_web(quiz, r):
    """Domanda CodeRunner html o css senza test (esercizio libero a correzione manuale), già in Moodle XML.
    Struttura copiata dalle domande dell'utente: un solo test fittizio che si aspetta «codice salvato»
    («codice salvato!» nel prototipo php_con_test, che l'utente usa per l'HTML con anteprima perché ha lo scratchpad;
    «codice salvato» nei prototipi html, per l'HTML senza anteprima, e css)."""
    sez = sezioni_cr(r.get("coderunner"))
    val = {n: c for n, _, c in sez}
    for n in val:
        if n not in ("answer", "preload", "options", "linguaggio"):
            raise ValueError("«Soluzione e test» di un esercizio libero HTML/CSS: sezione '=== %s' non prevista "
                             "(solo answer, preload, options)" % n)
    if not val.get("answer", "").strip():
        raise ValueError("manca la soluzione di riferimento (=== answer in «Soluzione e test»)")
    tr = r.get("traccia") or ""
    if not tr.strip():
        raise ValueError("traccia vuota")
    if CAMPO_RE.search(tr) or any(t == "opzioni" for t, _ in leggi_blocchi(tr)):
        raise ValueError("in una domanda CodeRunner la traccia non ha campi Cloze né opzioni")
    proto = prototipo_web(quiz, r["tipologia"])
    scratch = proto == "php_con_test"
    if "controllo automatico" not in tr.lower():
        tr = tr.rstrip() + "\n\n" + (AVVISO_SCRATCHPAD if scratch else AVVISO_WEB)
    testo = espandi_codice(html_blocchi(leggi_blocchi(tr)))
    opz = dict(OPZIONI_WEB)
    for l in val.get("options", "").split("\n"):
        if l.strip():
            k, _, v = l.partition(":")
            k = {"righe": "answerboxlines", "colonne": "answerboxcolumns"}.get(k.strip(), k.strip())
            if k not in OPZIONI_WEB or not v.strip().isdigit():
                raise ValueError("opzione '%s' non prevista (solo righe: N, colonne: N)" % l.strip())
            opz[k] = v.strip()
    corr = (r.get("correzione") or "").strip()
    gf = espandi_codice(html_blocchi(leggi_blocchi(corr))) if corr else ""
    punti = "%.7f" % float(r.get("punti") or 1)

    def t(tag, v):
        return "    <%s>%s</%s>\n" % (tag, v, tag)
    x = ['  <question type="coderunner">\n    <name>\n      <text>%s</text>\n    </name>\n' % esc_xml(nome_moodle(quiz, r)),
         '    <questiontext format="html">\n      <text>%s</text>\n    </questiontext>\n' % cdata(testo),
         '    <generalfeedback format="html">\n      <text>%s</text>\n    </generalfeedback>\n' % (cdata(gf) if gf else ""),
         t("defaultgrade", punti), t("penalty", "0.0000000"), t("hidden", "0"), t("idnumber", ""),
         t("coderunnertype", proto), t("prototypetype", "0"), t("allornothing", "1"),
         t("penaltyregime", "0"), t("precheck", "0"), t("hidecheck", "0"), t("showsource", "0"),
         t("answerboxlines", opz["answerboxlines"]), t("answerboxcolumns", opz["answerboxcolumns"]),
         t("answerpreload", cdata(json_scratchpad(val.get("preload", "").strip("\n"), "1")) if scratch
           else (cdata(val["preload"]) if val.get("preload", "").strip() else "")),
         t("globalextra", ""), t("useace", ""), t("resultcolumns", ""), t("template", ""),
         t("iscombinatortemplate", ""), t("allowmultiplestdins", ""),
         t("answer", cdata(json_scratchpad(val["answer"]) if scratch else val["answer"])),
         t("validateonsave", "1"), t("testsplitterre", ""), t("language", ""), t("acelang", ""),
         t("sandbox", ""), t("grader", ""), t("cputimelimitsecs", ""), t("memlimitmb", ""),
         t("sandboxparams", ""), t("templateparams", ""), t("hoisttemplateparams", "1"),
         t("extractcodefromjson", "1"), t("templateparamslang", "None"), t("templateparamsevalpertry", "0"),
         t("templateparamsevald", "{}"), t("twigall", "0"), t("uiplugin", ""), t("uiparameters", ""),
         t("attachments", "0"), t("attachmentsrequired", "0"), t("maxfilesize", "10240"),
         t("filenamesregex", ""), t("filenamesexplain", ""), t("displayfeedback", "1"),
         t("giveupallowed", "0"), t("prototypeextra", ""),
         '    <testcases>\n      <testcase testtype="0" useasexample="0" hiderestiffail="0" mark="1.0000000" >\n'
         '      <testcode>\n                <text>//</text>\n      </testcode>\n'
         '      <stdin>\n                <text></text>\n      </stdin>\n'
         '      <expected>\n                <text>@@ATTESO@@\n</text>\n      </expected>\n'
         '      <extra>\n                <text></text>\n      </extra>\n'
         '      <display>\n                <text>SHOW</text>\n      </display>\n'
         '    </testcase>\n    </testcases>\n  </question>\n\n']
    return "".join(x).replace("@@ATTESO@@", "codice salvato!" if scratch else "codice salvato")


COPPIA_RE = re.compile(r"^\s*(.*?)\s*<->\s*(.*?)\s*$")
FB_MATCH = ("<p>Risposta corretta.</p>", "<p>Risposta parzialmente esatta.</p>", "<p>Risposta errata.</p>")


def coppie_traccia(tr):
    """Separa le righe «sinistra <-> destra» (fuori dai blocchi di codice) dal resto della traccia."""
    coppie, resto, fence = [], [], False
    for ln in (tr or "").replace("\r", "").split("\n"):
        if ln.startswith("```"):
            fence = not fence
        m = None if fence else COPPIA_RE.match(ln)
        if m and "<->" in ln:
            coppie.append((m.group(1), m.group(2)))
        else:
            resto.append(ln)
    return coppie, "\n".join(resto)


def domanda_match(quiz, r):
    """Corrispondenza, già in Moodle XML (crea_xml.py non la gestisce): struttura copiata dalle domande
    dell'utente. Righe «elemento <-> corrispondenza»; senza elemento a sinistra è una risposta in più."""
    coppie, resto = coppie_traccia(r.get("traccia"))
    if CAMPO_RE.search(resto) or any(t == "opzioni" for t, _ in leggi_blocchi(resto)):
        raise ValueError("in una corrispondenza la traccia non ha campi Cloze né opzioni")
    domande = [c for c in coppie if c[0]]
    if len(domande) < 2 or len(coppie) < 3:
        raise ValueError("una corrispondenza vuole almeno 2 righe «elemento <-> corrispondenza» e almeno 3 "
                         "corrispondenze in tutto (le righe «<-> …» senza elemento sono risposte in più)")
    for a, b in coppie:
        if not b:
            raise ValueError("riga «%s <->» senza corrispondenza a destra" % a)
        if "`" in b or "<" in b or "**" in b:
            raise ValueError("la corrispondenza «%s» è testo semplice (compare in un menù): niente codice, tag "
                             "o grassetto" % b)
    sx = [a for a, _ in domande]
    if len(set(sx)) != len(sx):
        raise ValueError("due righe con lo stesso elemento a sinistra")
    testo = espandi_codice(html_blocchi(leggi_blocchi(resto)))
    corr = (r.get("correzione") or "").strip()
    gf = espandi_codice(html_blocchi(leggi_blocchi(corr))) if corr else ""
    fbx = lambda tag, t: '    <%s format="html">\n      <text>%s</text>\n    </%s>\n' % (tag, cdata(t), tag)
    x = ['  <question type="matching">\n    <name>\n      <text>%s</text>\n    </name>\n' % esc_xml(nome_moodle(quiz, r)),
         '    <questiontext format="html">\n      <text>%s</text>\n    </questiontext>\n' % cdata(testo),
         '    <generalfeedback format="html">\n      <text>%s</text>\n    </generalfeedback>\n' % (cdata(gf) if gf else ""),
         "    <defaultgrade>%.7f</defaultgrade>\n" % float(r.get("punti") or 1),
         "    <penalty>0.3333333</penalty>\n    <hidden>0</hidden>\n    <idnumber></idnumber>\n",
         "    <shuffleanswers>true</shuffleanswers>\n",
         fbx("correctfeedback", FB_MATCH[0]), fbx("partiallycorrectfeedback", FB_MATCH[1]),
         fbx("incorrectfeedback", FB_MATCH[2]), "    <shownumcorrect/>\n"]
    for a, b in coppie:
        x.append('    <subquestion format="html">\n      <text>%s</text>\n      <answer>\n        <text>%s</text>\n'
                 '      </answer>\n    </subquestion>\n' % (cdata(inl(a)) if a else "", esc_xml(b)))
    x.append("  </question>\n\n")
    return "".join(x)


def domanda(quiz, r):
    """Restituisce il testo della specifica per una riga."""
    tip = r.get("tipologia")
    if tip in CODERUNNER:
        raise ValueError("tipologia CodeRunner: si crea con le skill domande-coderunner-*, non da questo script")
    if tip not in CATALOGO:
        raise ValueError("tipologia mancante o sconosciuta: %r" % tip)
    tipo = CATALOGO[tip][0]
    if tipo == "matching":
        raise ValueError("la corrispondenza non è ancora supportata da crea_xml.py (D1)")
    tr = r.get("traccia") or ""
    if re.search(r"\[\[\d+\]\]", tr):
        raise ValueError("segnaposto [[n]] nella traccia: i campi vanno scritti nella sintassi Cloze di Moodle")
    bl = leggi_blocchi(tr)
    opz = [d for t, d in bl if t == "opzioni"]
    corpo = [b for b in bl if b[0] != "opzioni"]
    correzione = (r.get("correzione") or "").strip()
    s = ["=== question %s" % tipo, "=== name", nome_moodle(quiz, r)]
    opzioni, risposte, extra = {}, [], []
    punti = numero(r.get("punti"))
    if tipo == "description":
        testo = '<div style="%s">\n%s\n</div>' % (FONT, html_blocchi(corpo, pagina=True))
    else:
        testo = html_blocchi(corpo)
    if tipo == "cloze":
        if not CAMPO_RE.search(tr):
            raise ValueError("Cloze senza campi")
        if opz:
            raise ValueError("opzioni ( ) / [ ] in una Cloze: i menù si scrivono come campi MULTICHOICE_S")
    elif tipo in ("multichoice", "truefalse", "shortanswer"):
        if len(opz) != 1:
            raise ValueError("servono le opzioni ( ) / [ ] (un solo gruppo), trovati %d gruppi" % len(opz))
        o = opz[0]
        if not any(x["giusta"] or (x["perc"] or 0) > 0 for x in o):
            raise ValueError("nessuna opzione segnata come giusta: (x) o [x]")
        if tipo == "multichoice":
            multi = any(x["multi"] for x in o)
            giuste = [x for x in o if x["giusta"] and x["perc"] is None]
            assegnati = sum(x["perc"] for x in o if x["perc"] and x["perc"] > 0)
            quota = (100 - assegnati) / len(giuste) if giuste else 0
            # più risposte giuste: le penalità sommano -100%, così chi spunta tutto prende 0;
            # le sbagliate senza percentuale si dividono quello che manca alle penalità scritte a mano
            sbagliate = [x for x in o if not x["giusta"] and x["perc"] is None]
            scritte = sum(x["perc"] for x in o if x["perc"] is not None and x["perc"] < 0)
            penale = 0
            if multi and sbagliate and scritte > -100:
                penale = (-100 - scritte) / len(sbagliate)
            for x in o:
                fr = x["perc"] if x["perc"] is not None else (quota if x["giusta"] else penale)
                risposte.append(((("%.5f" % round(fr, 5)).rstrip("0").rstrip(".")), inl(x["testo"]), inl(x["feedback"])))
            opzioni["defaultgrade"] = punti
            if multi:
                opzioni["single"] = "false"
                negative = sum(float(fr) for fr, _, _ in risposte if float(fr) < 0)
                if any(float(fr) <= 0 for fr, _, _ in risposte) and abs(negative + 100) > 0.5:
                    raise ValueError("più risposte giuste: le penalità delle sbagliate devono sommare -100%% (ora %g%%)" % negative)
        elif tipo == "truefalse":
            vero = [x for x in o if x["testo"].lower().startswith("vero")]
            falso = [x for x in o if x["testo"].lower().startswith("falso")]
            if not (vero and falso):
                raise ValueError("vero/falso: servono le due opzioni «Vero» e «Falso»")
            opzioni["defaultgrade"] = punti
            opzioni["correct"] = "true" if vero[0]["giusta"] else "false"
            extra += ["=== feedback true", inl(vero[0]["feedback"]), "=== feedback false", inl(falso[0]["feedback"])]
        else:
            for x in o:
                fr = x["perc"] if x["perc"] is not None else (100 if x["giusta"] else 0)
                risposte.append((("%g" % fr), x["testo"], inl(x["feedback"])))
            opzioni["defaultgrade"] = punti
    elif tipo == "essay":
        if opz:
            raise ValueError("opzioni ( ) / [ ] in una domanda aperta")
        opzioni["defaultgrade"] = punti
    if opzioni:
        s += ["=== options"] + ["%s: %s" % kv for kv in opzioni.items()]
    note = (r.get("docente") or "").strip()
    if note:
        s += ["=== note", note]
    s += ["=== questiontext", testo]
    if correzione and tipo not in ("essay", "description"):
        s += ["=== generalfeedback", html_blocchi(leggi_blocchi(correzione))]
    for fr, t, fb in risposte:
        s += ["=== answer %s" % fr, t, "=== feedback", fb]
    s += extra
    if tipo == "essay":
        if correzione:
            s += ["=== graderinfo", html_blocchi(leggi_blocchi(correzione))]
    return "\n".join(s)


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) != 3:
        raise SystemExit(__doc__)
    export, qid, usc = a
    quiz, righe = carica(export, qid)
    var = next((x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--varianti=")), "")
    if var:
        scelte = {v.strip().lower() for v in var.split(",") if v.strip()}
        tolte = [r.get("pos") or r["id"] for r in righe
                 if (r.get("tag") or "").strip() and (r.get("pos") or "")[-1:].lower() not in scelte]
        righe = [r for r in righe if not (r.get("pos") or r["id"]) in tolte]
        print("Varianti %s: %d righe lasciate fuori (%s)" % (",".join(sorted(scelte)), len(tolte), ", ".join(tolte)))
    preset = None
    for x in sys.argv[1:]:
        if x.startswith("--preset="):
            preset = x.split("=", 1)[1]
    # quiz importati da un backup (tipo «IMP», senza preset): le impostazioni vengono dal backup (presetMbz)
    preset = preset or PRESET_MBZ.get(quiz.get("tipoQuiz")) or quiz.get("presetMbz") or "esercitazione"
    os.makedirs(usc, exist_ok=True)

    salta = "--salta-coderunner" in sys.argv
    saltate = [r for r in righe if salta and r.get("tipologia") in CODERUNNER and linguaggio_cr(r) not in ("js", "sql", "php")]
    tutte = righe
    righe = [r for r in righe if r not in saltate]
    errori, spec, spec_js, spec_sql, spec_php, web = [], [], [], [], [], []
    for r in righe:
        try:
            if r.get("tipologia") in CR_WEB:
                web.append(domanda_web(quiz, r))
            elif CATALOGO.get(r.get("tipologia"), ("",))[0] == "matching":
                web.append(domanda_match(quiz, r))
            elif r.get("tipologia") in CODERUNNER:
                lg = linguaggio_cr(r)
                if lg == "sql":
                    spec_sql.append(domanda_sql(quiz, r))
                elif lg == "php":
                    spec_php.append(domanda_php(quiz, r))
                elif lg != "js":
                    raise ValueError("CodeRunner %s: linguaggio non gestito (JavaScript, SQL, PHP)" % lg.upper())
                else:
                    spec_js.append(domanda_cr(quiz, r))
            else:
                spec.append(domanda(quiz, r))
        except ValueError as e:
            errori.append("%s (%s): %s" % (r.get("pos") or r["id"], r.get("titolo") or "", e))
    non_ok = [r.get("pos") or r["id"] for r in righe if r.get("stato") != "approvata"]
    # varianti delle verifiche ripetibili: righe con lo stesso tag = una posizione casuale del quiz
    gruppi, avvisi_tag = {}, []
    for r in tutte:
        t = (r.get("tag") or "").strip()
        if t:
            gruppi.setdefault(t.lower(), []).append(r)
            if CATALOGO.get(r.get("tipologia"), ("",))[0] == "description":
                errori.append("%s: una pagina non può avere un tag (le pagine restano fisse)" % (r.get("pos") or r["id"]))
            if re.search(r"\s", t):
                errori.append("%s: tag «%s» con spazi: usa trattini (es. rjs4-T1-assegnamento)" % (r.get("pos") or r["id"], t))
    for k, g in gruppi.items():
        nomi = ", ".join(r.get("pos") or r["id"] for r in g)
        for campo, cosa in (("punti", "punti"), ("pag", "pagina"), ("sezione", "sezione")):
            if len({str(r.get(campo) or "") for r in g}) > 1:
                errori.append("varianti del tag %s (%s) con %s diversi: devono essere uguali" % (g[0]["tag"], nomi, cosa))
        if len(g) < 2:
            avvisi_tag.append("tag %s con una sola variante (%s): la posizione pesca sempre la stessa domanda" % (g[0]["tag"], nomi))
        if len({r.get("tipologia") for r in g}) > 1:
            avvisi_tag.append("varianti del tag %s (%s) di tipologie diverse" % (g[0]["tag"], nomi))
        pos = [i for i, r in enumerate(tutte) if r in g]
        if pos[-1] - pos[0] + 1 != len(g):
            avvisi_tag.append("varianti del tag %s (%s) non consecutive nella scaletta" % (g[0]["tag"], nomi))
    if errori:
        raise SystemExit("ERRORI nelle righe:\n- " + "\n- ".join(errori))

    categoria = categoria_quiz(quiz)
    open(os.path.join(usc, "specifica.txt"), "w", encoding="utf-8").write(
        "=== category\n%s\n%s\n" % (categoria, "\n".join(spec)))
    pjs = os.path.join(usc, "specifica-js.txt")
    if spec_js:
        open(pjs, "w", encoding="utf-8").write("=== category\n%s\n%s\n" % (categoria, "\n\n".join(spec_js)))
    elif os.path.exists(pjs):
        os.remove(pjs)
    psql = os.path.join(usc, "specifica-sql.txt")
    if spec_sql:
        dbs = databases_quiz(quiz)
        if not dbs:
            raise SystemExit("ERRORE: il quiz ha domande SQL ma nessun database (campo «database» del quiz)")
        open(psql, "w", encoding="utf-8").write(
            "=== category\n%s\n" % categoria
            + "".join("=== database %s\n%s\n" % (k, v.strip()) for k, v in dbs.items())
            + "\n" + "\n\n".join(spec_sql) + "\n")
    elif os.path.exists(psql):
        os.remove(psql)
    pphp = os.path.join(usc, "specifica-php.txt")
    if spec_php:
        dbs = databases_quiz(quiz)
        if not dbs:
            raise SystemExit("ERRORE: il quiz ha domande PHP ma nessun database (campo «database» del quiz)")
        open(pphp, "w", encoding="utf-8").write(
            "=== category\n%s\n" % categoria
            + "".join("=== database %s\n%s\n" % (k, v.strip()) for k, v in dbs.items())
            + "\n" + "\n\n".join(spec_php) + "\n")
    elif os.path.exists(pphp):
        os.remove(pphp)
    pweb = os.path.join(usc, "domande-dirette.xml")
    if web:
        open(pweb, "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n'
                                                + xml_categoria(percorso_categoria(categoria)) + "".join(web) + "</quiz>\n")
    elif os.path.exists(pweb):
        os.remove(pweb)

    titoli = quiz.get("titoliSezioni") or {}
    sezioni, cur, visti, tag_nomi = [], None, set(), {}
    for r in tutte:
        t = (r.get("tag") or "").strip()
        if t:
            tag_nomi[nome_moodle(quiz, r)] = t
            if t.lower() in visti:
                continue
            visti.add(t.lower())
        if cur is None or cur["_k"] != r.get("sezione"):
            sez = r.get("sezione") or ""
            cur = {"_k": sez, "titolo": titoli.get(sez, sez), "domande": []}
            sezioni.append(cur)
        voce = {"casuale": t} if t else {"nome": nome_moodle(quiz, r)}
        voce.update({"pagina": int(float(r.get("pag") or 1)), "punti": float(r.get("punti") or 0)})
        cur["domande"].append(voce)
    ptag = os.path.join(usc, "tag.json")
    if tag_nomi:
        json.dump(tag_nomi, open(ptag, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    elif os.path.exists(ptag):
        os.remove(ptag)
    # la prima sezione del quiz è senza titolo se è l'introduzione
    for s in sezioni:
        del s["_k"]
    imp = {"nome": quiz.get("nomeQuiz") or quiz.get("titolo") or categoria, "preset": preset,
           "voto_massimo": quiz.get("voto", 10), "voto_sufficienza": quiz.get("sufficienza", 6),
           "sezioni": sezioni}
    if preset == "verifica" and quiz.get("tempo"):
        imp["impostazioni"] = {"timelimit": int(float(quiz["tempo"])) * 60}
    json.dump(imp, open(os.path.join(usc, "impaginazione.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK: %d domande (%d CodeRunner JavaScript, %d CodeRunner SQL, %d CodeRunner PHP, %d scritte direttamente in XML: esercizi HTML/CSS e corrispondenze), %d sezioni, %g punti, preset %s -> %s"
          % (len(spec) + len(spec_js) + len(spec_sql) + len(spec_php) + len(web), len(spec_js), len(spec_sql), len(spec_php), len(web), len(sezioni), sum(d["punti"] for s in sezioni for d in s["domande"]), preset, usc))
    if gruppi:
        print("VERIFICA RIPETIBILE: %d posizioni casuali per tag, %d varianti in tutto" % (len(gruppi), sum(len(g) for g in gruppi.values())))
    for a in avvisi_tag:
        print("ATTENZIONE: " + a)
    if non_ok:
        print("ATTENZIONE: righe non ancora approvate: " + ", ".join(non_ok))
    if saltate:
        print("RIGHE CODERUNNER LASCIATE FUORI (da produrre con le loro skill e unire all'XML; "
              "l'.mbz va rifatto con l'XML unito): " + ", ".join("%s %s" % (r.get("pos"), r.get("titolo")) for r in saltate))


if __name__ == "__main__":
    main()
