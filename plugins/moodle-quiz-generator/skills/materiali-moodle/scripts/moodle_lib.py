"""Funzioni comuni agli script della skill materiali-moodle.

- espandi_codice(html): sostituisce i blocchi [[codice LINGUAGGIO]] ... [[/codice]]
  con il <pre> nello stile della skill, con le entità HTML e la colorazione.
- controlla_cloze(html): controlli sulle regole Cloze dell'utente.
- controlla_html(html, tipo): controlli generali (emoji, tag vietati, titoli).
- scrittura dell'XML Moodle (funzioni xml_*).
"""
import html as _html
import re

# ------------------------------------------------------------------ stile

PRE_STYLE = ("background-color: #333333; color: #eceff1; padding: 12px; "
             "border-radius: 4px; overflow-x: auto; margin: 8px 0; "
             "line-height: 1.5;")

COLORI = {
    "keyword": "#ebcb8b",   # parole chiave
    "string": "#a3be8c",    # stringhe e valori di attributo
    "var": "#8fbcbb",       # variabili PHP, attributi HTML, proprietà CSS
    "comment": "#9aa0a6",   # commenti
    "number": "#d08770",    # numeri
    "tag": "#81a1c1",       # tag HTML, selettori CSS
}

# Un campo Cloze: {n:TIPO:...} con eventuali graffe escapate \}
CAMPO_RE = re.compile(r"\{(\d*):([A-Z_]+):((?:\\.|[^}\\])*)\}")

TIPI_CLOZE = {
    "SHORTANSWER", "SA", "MW", "SHORTANSWER_C", "SAC", "MWC",
    "NUMERICAL", "NM",
    "MULTICHOICE", "MC", "MULTICHOICE_V", "MCV", "MULTICHOICE_H", "MCH",
    "MULTICHOICE_S", "MCS", "MULTICHOICE_VS", "MCVS", "MULTICHOICE_HS", "MCHS",
    "MULTIRESPONSE", "MR", "MULTIRESPONSE_H", "MRH",
    "MULTIRESPONSE_S", "MRS", "MULTIRESPONSE_HS", "MRHS",
}
MC_FISSI = {"MULTICHOICE", "MC", "MULTICHOICE_V", "MCV", "MULTICHOICE_H", "MCH"}
MC_MESCOLATI = {"MULTICHOICE_S", "MCS", "MULTICHOICE_VS", "MCVS",
                "MULTICHOICE_HS", "MCHS"}

# ------------------------------------------------------------ colorazione

_KW = {
    "php": r"if|else|elseif|while|for|foreach|as|do|switch|case|default|break|"
           r"continue|function|return|echo|print|isset|empty|die|exit|or|and|"
           r"true|false|null|TRUE|FALSE|NULL|new|require|include|require_once|"
           r"include_once|array|global",
    "js": r"let|const|var|if|else|for|while|do|switch|case|default|break|"
          r"continue|function|return|true|false|null|undefined|new|of|in|"
          r"typeof",
    "sql": r"SELECT|FROM|WHERE|AND|OR|NOT|IN|LIKE|BETWEEN|IS|NULL|ORDER|BY|"
           r"GROUP|HAVING|ASC|DESC|LIMIT|JOIN|INNER|LEFT|RIGHT|OUTER|ON|AS|"
           r"INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|DATABASE|USE|"
           r"DROP|ALTER|ADD|PRIMARY|FOREIGN|KEY|REFERENCES|UNIQUE|DEFAULT|"
           r"AUTO_INCREMENT|AUTOINCREMENT|CASCADE|RESTRICT|DISTINCT|COUNT|SUM|"
           r"AVG|MIN|MAX|INT|INTEGER|VARCHAR|CHAR|DATE|DECIMAL|FLOAT|TEXT|"
           r"BOOLEAN|CHECK|CONSTRAINT|NO|ACTION",
}

_TOKEN = {
    "php": [
        ("comment", r"//[^\n]*|#[^\n]*|/\*[\s\S]*?\*/"),
        ("string", r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'"),
        ("keyword", r"<\?php|\?>"),
        ("var", r"\$\w+"),
        ("number", r"\b\d+(?:\.\d+)?\b"),
        ("keyword", r"\b(?:%s)\b" % _KW["php"]),
    ],
    "js": [
        ("comment", r"//[^\n]*|/\*[\s\S]*?\*/"),
        ("string", r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`"),
        ("number", r"\b\d+(?:\.\d+)?\b"),
        ("keyword", r"\b(?:%s)\b" % _KW["js"]),
    ],
    "sql": [
        ("comment", r"--[^\n]*"),
        ("string", r"'(?:''|[^'])*'|\"(?:[^\"])*\""),
        ("number", r"\b\d+(?:\.\d+)?\b"),
        ("keyword", r"(?i:\b(?:%s)\b)" % _KW["sql"]),
    ],
}


def _span(tipo, testo_escapato):
    return '<span style="color: %s;">%s</span>' % (COLORI[tipo], testo_escapato)


def _esc(s):
    return _html.escape(s, quote=False)


def _colora_regex(codice, lingua):
    regole = _TOKEN[lingua]
    rx = re.compile("|".join("(?P<t%d>%s)" % (i, r) for i, (_, r) in enumerate(regole)))
    out, pos = [], 0
    for m in rx.finditer(codice):
        out.append(_esc(codice[pos:m.start()]))
        tipo = regole[int(m.lastgroup[1:])][0]
        out.append(_span(tipo, _esc(m.group(0))))
        pos = m.end()
    out.append(_esc(codice[pos:]))
    return "".join(out)


def _colora_html(codice):
    out, pos = [], 0
    for m in re.finditer(r"<!--[\s\S]*?-->|<[^>]+>", codice):
        out.append(_esc(codice[pos:m.start()]))
        tag = m.group(0)
        if tag.startswith("<!--"):
            out.append(_span("comment", _esc(tag)))
        else:
            tm = re.match(r"(</?)([\w!-]+)([\s\S]*?)(/?>)$", tag)
            if not tm:
                out.append(_esc(tag))
            else:
                apre, nome, attr, chiude = tm.groups()
                pezzi = [_span("tag", _esc(apre + nome))]
                p2 = 0
                for am in re.finditer(r'([\w-]+)(\s*=\s*)("[^"]*"|\'[^\']*\'|[^\s>]+)?', attr):
                    pezzi.append(_esc(attr[p2:am.start()]))
                    pezzi.append(_span("var", _esc(am.group(1))))
                    if am.group(2):
                        pezzi.append(_esc(am.group(2)))
                        pezzi.append(_span("string", _esc(am.group(3) or "")))
                    p2 = am.end()
                pezzi.append(_esc(attr[p2:]))
                pezzi.append(_span("tag", _esc(chiude)))
                out.append("".join(pezzi))
        pos = m.end()
    out.append(_esc(codice[pos:]))
    return "".join(out)


def _colora_css(codice):
    out, pos = [], 0
    rx = re.compile(r"(?P<c>/\*[\s\S]*?\*/)|(?P<b>\{[^}]*\})|(?P<s>[^{}/]+(?=\{))")
    for m in rx.finditer(codice):
        out.append(_esc(codice[pos:m.start()]))
        if m.group("c"):
            out.append(_span("comment", _esc(m.group("c"))))
        elif m.group("s"):
            sel = m.group("s")
            lead = len(sel) - len(sel.lstrip())
            trail = len(sel) - len(sel.rstrip())
            out.append(_esc(sel[:lead]) + _span("tag", _esc(sel.strip())) +
                       _esc(sel[len(sel) - trail:] if trail else ""))
        else:
            blocco = m.group("b")
            out.append(re.sub(r"([\w-]+)(\s*:)",
                              lambda x: _span("var", x.group(1)) + x.group(2),
                              _esc(blocco)))
        pos = m.end()
    out.append(_esc(codice[pos:]))
    return "".join(out)


def colora(codice, lingua):
    lingua = (lingua or "").lower()
    if lingua in ("javascript",):
        lingua = "js"
    if lingua in _TOKEN:
        return _colora_regex(codice, lingua)
    if lingua == "html":
        return _colora_html(codice)
    if lingua == "css":
        return _colora_css(codice)
    return _esc(codice)


def _codice_con_campi(codice):
    """Codice che contiene campi Cloze: entità fuori dai campi, campi intatti,
    nessuna colorazione (gli span potrebbero rompere i campi)."""
    out, pos = [], 0
    for m in CAMPO_RE.finditer(codice):
        out.append(_esc(codice[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(_esc(codice[pos:]))
    return "".join(out)


BLOCCO_RE = re.compile(r"\[\[codice(?:\s+([\w-]+))?(?:\s+(semplice))?\]\]\n?([\s\S]*?)\n?\[\[/codice\]\]")


def espandi_codice(testo):
    """Sostituisce i blocchi [[codice LINGUA]] ... [[/codice]] con il <pre>."""
    def sost(m):
        lingua, semplice, codice = m.group(1), m.group(2), m.group(3)
        if CAMPO_RE.search(codice):
            corpo = _codice_con_campi(codice)
        elif semplice:
            corpo = _esc(codice)
        else:
            corpo = colora(codice, lingua)
        return '<pre style="%s">%s</pre>' % (PRE_STYLE, corpo)
    return BLOCCO_RE.sub(sost, testo)


# ---------------------------------------------------------------- controlli

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\uFE0F]")


def _dividi_opzioni(contenuto):
    """Divide il contenuto di un campo sulle ~ non escapate."""
    opzioni, cur, i = [], [], 0
    while i < len(contenuto):
        c = contenuto[i]
        if c == "\\" and i + 1 < len(contenuto):
            cur.append(contenuto[i:i + 2]); i += 2; continue
        if c == "~":
            opzioni.append("".join(cur)); cur = []
        else:
            cur.append(c)
        i += 1
    opzioni.append("".join(cur))
    return opzioni


def _analizza_opzione(op):
    """Restituisce (corretta, testo_senza_feedback)."""
    corretta = op.startswith("=") or bool(re.match(r"%100%", op))
    testo = re.sub(r"^(=|%-?\d+(?:\.\d+)?%)", "", op)
    # il feedback inizia al primo # non escapato
    m = re.search(r"(?<!\\)#", testo)
    if m:
        testo = testo[:m.start()]
    return corretta, testo.strip()


def campi_cloze(html):
    return list(CAMPO_RE.finditer(html))


def controlla_cloze(html):
    errori, avvisi = [], []
    campi = campi_cloze(html)
    if not campi:
        errori.append("nessun campo Cloze nel testo")
        return errori, avvisi

    # graffe: ogni { seguito da n:TIPO: deve chiudersi
    aperture = len(re.findall(r"\{\d*:[A-Z_]+:", html))
    if aperture != len(campi):
        errori.append("campi Cloze non chiusi correttamente (graffe sbilanciate o "
                      "graffa non escapata in una risposta)")

    # campi dentro <pre><code>
    for blocco in re.finditer(r"<pre[^>]*>([\s\S]*?)</pre>", html):
        if CAMPO_RE.search(blocco.group(1)) and re.match(r"\s*<code", blocco.group(1)):
            errori.append("campi Cloze dentro <pre><code>: con i campi nel codice usa "
                          "solo <pre> (l'evidenziatore di sintassi rompe i campi)")

    gruppi = {}
    for n, m in enumerate(campi, 1):
        tipo, contenuto = m.group(2), m.group(3)
        etichetta = "campo %d (%s)" % (n, tipo)
        if tipo not in TIPI_CLOZE:
            errori.append("%s: tipo sconosciuto" % etichetta)
            continue
        if "\\/" in contenuto or '\\"' in contenuto:
            errori.append("%s: barra rovesciata davanti a / o \": nel Moodle "
                          "dell'utente compare allo studente. Si escapano solo } # ~"
                          % etichetta)
        e_menu = tipo in MC_FISSI | MC_MESCOLATI or tipo.startswith(("MULTIRESPONSE", "MR"))
        # le regole su entità e tag valgono per le risposte, non per i feedback
        risposte = " ".join(_analizza_opzione(o)[1] for o in _dividi_opzioni(contenuto))
        if "&amp;" in risposte:
            errori.append("%s: '&amp;' dentro il campo: codifica doppia, lo studente "
                          "vede il codice dell'entità (per l'apostrofo scrivi ' così com'è)"
                          % etichetta)
        elif not e_menu and re.search(r"&(lt|gt|quot|#39|#x27|apos);", risposte):
            errori.append("%s: entità HTML in un campo a risposta: Moodle confronta il "
                          "testo così com'è con quello digitato dallo studente, che non "
                          "coinciderà mai. Scrivi il carattere, oppure sposta il campo"
                          % etichetta)
        if e_menu and re.search(r"<[A-Za-z/!]", risposte):
            errori.append("%s: '<' seguito da una lettera in un'opzione: verrebbe letto "
                          "come un tag. Nei menù scrivi &lt;" % etichetta)
        elif not e_menu and re.search(r"<[A-Za-z/!]", risposte):
            errori.append("%s: risposta che contiene un tag: l'editor la leggerebbe come "
                          "HTML. Metti il campo sul solo nome (es. &lt;{1:SHORTANSWER:=form}&gt;)"
                          % etichetta)
        opzioni = [_analizza_opzione(o) for o in _dividi_opzioni(contenuto)]
        if not any(c for c, _ in opzioni):
            errori.append("%s: nessuna risposta corretta (= o %%100%%)" % etichetta)
        if tipo in ("NUMERICAL", "NM"):
            for c, t in opzioni:
                if c and not re.match(r"^-?\d+(?:\.\d+)?(?::\d+(?:\.\d+)?)?$", t):
                    errori.append("%s: risposta numerica non valida '%s'" % (etichetta, t))
        if tipo in MC_FISSI | MC_MESCOLATI:
            testi = [t for _, t in opzioni]
            chiave = tuple(sorted(testi))
            gruppi.setdefault(chiave, []).append((n, tipo, testi, opzioni))

    for chiave, membri in gruppi.items():
        if len(membri) == 1:
            n, tipo, testi, _ = membri[0]
            if tipo in MC_FISSI:
                avvisi.append("campo %d: menù singolo con MULTICHOICE (ordine fisso): "
                              "usa MULTICHOICE_S, salvo che l'ordine sia voluto" % n)
            continue
        nums = ", ".join(str(m[0]) for m in membri)
        mescolati = [m for m in membri if m[1] in MC_MESCOLATI]
        if mescolati:
            errori.append("campi %s: condividono le stesse opzioni ma usano "
                          "MULTICHOICE_S, che le rimescola in modo diverso in ogni campo: "
                          "usa MULTICHOICE con lo stesso ordine statico ovunque" % nums)
            continue
        ordini = {tuple(m[2]) for m in membri}
        if len(ordini) > 1:
            errori.append("campi %s: stesse opzioni ma in ordine diverso: l'ordine "
                          "deve essere identico in tutti i campi" % nums)
            continue
        ordine = membri[0][2]
        corrette = []
        for m in membri:
            idx = [i for i, (c, _) in enumerate(m[3]) if c]
            corrette.append(idx[0] if idx else -1)
        if len(set(corrette)) == len(corrette) and corrette == sorted(corrette):
            errori.append("campi %s: le opzioni sono nello stesso ordine delle risposte "
                          "corrette: mescolale una volta (ordine statico)" % nums)
    return errori, avvisi


def controlla_html(html, tipo):
    """Controlli generali sul testo di una domanda o di una pagina."""
    errori, avvisi = [], []
    if EMOJI_RE.search(html):
        errori.append("emoji nel testo: lo stile della skill non le usa")
    for tag in ("html", "head", "body", "style", "script"):
        if re.search(r"<%s[\s>]" % tag, html, re.I):
            errori.append("tag <%s>: Moodle vuole un frammento HTML, senza %s" % (tag, tag))
    if tipo not in ("description", "pagina") and re.search(r"<h[12][\s>]", html, re.I):
        avvisi.append("titolo <h1>/<h2> nel testo di una domanda: le domande usano "
                      "lo stile compatto, senza titoli grandi")
    if "[[codice" in html or "[[/codice]]" in html:
        errori.append("blocco [[codice]] non espanso (manca [[/codice]] o la sintassi "
                      "è sbagliata)")
    if tipo != "cloze" and "\\/" in html:
        avvisi.append("barra rovesciata davanti a /: probabilmente un residuo di escaping")
    return errori, avvisi


# ------------------------------------------------------------- scrittura XML

def cdata(testo):
    return "<![CDATA[" + (testo or "").replace("]]>", "]]]]><![CDATA[>") + "]]>"


def esc_xml(testo):
    return _html.escape(testo or "", quote=False)


def xml_categoria(percorso):
    return ('  <question type="category">\n'
            '    <category>\n      <text>%s</text>\n    </category>\n'
            '    <info format="html">\n      <text></text>\n    </info>\n'
            '    <idnumber></idnumber>\n  </question>\n\n' % esc_xml(percorso))


def percorso_categoria(nome):
    nome = nome.strip()
    if nome.startswith("$"):
        return nome
    return "$module$/top/" + nome.strip("/")
