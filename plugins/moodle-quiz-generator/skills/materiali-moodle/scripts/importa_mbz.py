#!/usr/bin/env python3
"""Dal backup di un quiz Moodle (.mbz) al database della dashboard «Bozze dei quiz».

È il percorso inverso di da_dashboard.py: le domande del backup tornano righe della dashboard,
con traccia, correzione e «Soluzione e test» scritti nelle convenzioni di formato-consegna.md.

Uso:
    python3 importa_mbz.py BACKUP.mbz USCITA [--id=ID_QUIZ] [--quiz=TESTO]
    python3 importa_mbz.py BACKUP.mbz USCITA --confronta=EXPORT --id=ID_QUIZ

Modo «quiz nuovo» (predefinito)
    Scrive USCITA/quiz/<id>.json e USCITA/quiz/<id>/domande/rNN.json, nella stessa forma
    dell'esportazione con ArtifactData (out_dir): si caricano nella dashboard con una batch di
    set, e da_dashboard.py li legge così come sono. Scrive anche USCITA/rapporto.md: che cosa è
    stato dedotto, che cosa manca, quali righe vanno riviste e perché.
    --id=ID      id del quiz nella dashboard (predefinito: dal nome del quiz)
    --quiz=TESTO se il backup ha più quiz, quello il cui nome contiene TESTO
    --ordine     segnala anche le domande SQL il cui risultato non ha un ordine unico (ORDER BY
                 assente o con pari merito); senza, il controllo non si fa (vale anche con --confronta)

Modo «confronto con un quiz della dashboard» (--confronta=EXPORT)
    EXPORT è l'esportazione del quiz della dashboard (ArtifactData get/list con out_dir).
    Non scrive niente nella dashboard: produce USCITA/confronto.md con le differenze, posizione
    per posizione, tra la dashboard e il backup, e USCITA/aggiornamenti/<riga>.json con i soli
    campi cambiati di ogni riga (pronti per un update, da fare solo dopo l'ok dell'utente).
    Le domande con più versioni nel backup sono quelle modificate in Moodle: per loro il
    confronto tra la prima versione e l'ultima dice esattamente che cosa è cambiato, senza le
    differenze dovute alla conversione.

Il quiz importato ha tipo «IMP» (importato, senza preset): la dashboard non applica le regole di
un preset; si può sempre scegliere un tipo vero dal menù. Le impostazioni dell'.mbz (verifica o
esercitazione) vengono dal backup (campo presetMbz), il tempo dal limite del quiz.

Che cosa non torna uguale (e lo dice il rapporto, con la riga «da rivedere»):
- immagini: la dashboard non le gestisce; nella traccia resta il segnaposto [immagine: nome];
- colori e formattazioni particolari dell'editor (testo rosso, font): si perdono;
- un a capo dentro un'opzione di risposta multipla diventa « / »;
- nelle domande aperte il feedback generale (visibile allo studente) diventa la correzione,
  che da_dashboard.py mette nelle informazioni per chi corregge;
- minuti, parte, strumento e sostegno non stanno nel backup: restano vuoti.
"""
import base64
import difflib
import hashlib
import html
import json
import os
import pathlib
import re
import sqlite3
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser

NULL = "$@NULL@$"

# ---------------------------------------------------------------- costanti condivise con da_dashboard.py
BOX = {"blu": "#c9daf8", "giallo": "#fff2cc", "verde": "#d9ead3", "arancio": "#f9cb9c", "rosso": "#f4cccc"}
BOX_COL = {v: k for k, v in BOX.items()}
PREFISSI = {  # prefisso del nome -> tipologie possibili (la prima è quella predefinita)
    "Spiegazione": ["paginablocco"], "Ripasso": ["paginablocco"],
    "Esempio svolto": ["esempio_svolto"], "Tracciamento": ["tracciamento", "lettura_output"],
    "Trova l'errore": ["trova_errore"], "Completamento": ["compl_campi", "compl_eseguito"],
    "Esempio guidato": ["guidato"], "Debug": ["debug_msg", "debug_silenzioso", "debug_motivazione"],
    "Esercizio libero": ["esercizio_libero", "libero_html", "libero_css"],
    "Scrivere": ["prog_completo", "funzione", "prog_dati", "prog_random", "query", "create_tabelle",
                 "query_due_passi", "pagina_php", "scrittura_scheletro"],
    "Esercizio": ["vincoli"], "Campo di prova": ["campo_prova"], "Consegna": ["consegna_file"],
}
PAGINE = {"istruzioni", "comelavoriamo", "paginablocco"}
NOME_RE = re.compile(r"^(?P<lez>L\d+|[A-Z][A-Z0-9]*\d[A-Z0-9]*|\d[A-Z][A-Z0-9]*) - (?P<pos>[0-9A-Z]{1,3}[a-z]?) - (?P<resto>.+)$")
NORMALIZZA_INIZIO = "// ---- output normalizzato: spazi e a capo dello studente non contano ----"
CONFIGURA_RE = re.compile(r"\n?FakeDB::configure\(\['user' => 'root', 'password' => '', 'database' => '([^']*)'\]\);\s*$")
STRUTTURA_RE = re.compile(
    r"SELECT name, replace\(upper\(type\), ' \(', '\('\) AS tipo, \"notnull\", pk FROM pragma_table_info\('(\w+)'\);\n"
    r"SELECT \"table\", \"from\", \"to\" FROM pragma_foreign_key_list\('\1'\);")


# ---------------------------------------------------------------- archivio e XML

def estrai(mbz, cartella):
    cartella = pathlib.Path(cartella)
    if zipfile.is_zipfile(mbz):
        with zipfile.ZipFile(mbz) as z:
            z.extractall(cartella)
    else:
        with tarfile.open(mbz) as t:
            membri = [m for m in t.getmembers() if not m.name.startswith("/") and ".." not in m.name]
            try:
                t.extractall(cartella, members=membri, filter="data")
            except TypeError:
                t.extractall(cartella, members=membri)
    return cartella


def tx(el, tag, predef=""):
    v = el.findtext(tag) if el is not None else None
    return predef if v is None or v == NULL else v


# ---------------------------------------------------------------- HTML -> Markdown della dashboard

VUOTI = {"br", "img", "hr", "col", "input", "meta", "link", "wbr"}
BLOCCHI = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "pre", "table", "blockquote",
           "section", "article", "header", "footer", "thead", "tbody", "tr", "td", "th", "colgroup", "dl", "dd", "dt",
           "figure", "center"}


class Nodo:
    def __init__(self, tag, attrs=None, padre=None):
        self.tag, self.attrs, self.padre, self.figli = tag, dict(attrs or {}), padre, []

    def testo(self):
        return "".join(f if isinstance(f, str) else f.testo() for f in self.figli)


class Albero(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.radice = Nodo("root")
        self.cur = self.radice

    def handle_starttag(self, tag, attrs):
        n = Nodo(tag, attrs, self.cur)
        self.cur.figli.append(n)
        if tag not in VUOTI:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.figli.append(Nodo(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.radice and n.tag != tag:
            n = n.padre
        if n is not self.radice:
            self.cur = n.padre
        # un </p> senza apertura (HTML dell'editor) non fa niente

    def handle_data(self, data):
        self.cur.figli.append(data)


def albero(src):
    a = Albero()
    a.feed(src or "")
    a.close()
    return a.radice


def stile(n):
    return (n.attrs.get("style") or "").lower()


def monospace(n):
    return n.tag in ("code", "tt", "kbd", "samp") or "monospace" in stile(n)


class Convertitore:
    """Converte l'HTML di Moodle nel Markdown semplificato della dashboard. Tiene nota di quello
    che si perde (immagini, colori, a capo nelle opzioni) per il rapporto."""

    def __init__(self, campi=None):
        self.perdite = []
        self.immagini = []
        self.campi = campi or {}   # segnaposto Cloze {#n} -> campo originale

    def perdi(self, cosa):
        if cosa not in self.perdite:
            self.perdite.append(cosa)

    # --- testo in linea
    def inline(self, n, in_code=False):
        out = []
        for f in n.figli:
            if isinstance(f, str):
                t = f.replace("\xa0", " ")
                out.append(t if in_code else re.sub(r"[ \t\r\n]+", " ", t))
                continue
            t = f.tag
            if t == "br":
                out.append("\n")
            elif t == "img":
                nome = os.path.basename(html.unescape(f.attrs.get("src") or "immagine")).split("?")[0]
                self.immagini.append(nome)
                self.perdi("immagini (nella traccia resta il segnaposto)")
                out.append(" [immagine: %s] " % nome)
            elif t in ("script", "style"):
                continue
            elif monospace(f) and not in_code:
                c = re.sub(r"\s+", " ", self.inline(f, in_code=True)).strip()
                out.append("`%s`" % c.replace("`", "'") if c else "")
            elif t in ("strong", "b"):
                out.append(self.avvolgi(self.inline(f, in_code), "**"))
            elif t in ("em", "i"):
                out.append(self.avvolgi(self.inline(f, in_code), "*"))
            elif t == "u":
                out.append(self.avvolgi(self.inline(f, in_code), "__"))
            elif t == "a":
                testo = self.inline(f, in_code)
                href = f.attrs.get("href") or ""
                out.append(testo if not href or href in testo or href.startswith("#") else "%s (%s)" % (testo, href))
            elif t in ("table",):
                out.append(" " + " ".join(self.inline(c) for c in f.figli if not isinstance(c, str)) + " ")
            else:
                if "color" in stile(f) and "background" not in stile(f) and not in_code and f.testo().strip():
                    self.perdi("colori del testo")
                out.append(self.inline(f, in_code))
        return "".join(out)

    @staticmethod
    def avvolgi(s, m):
        if not s.strip():
            return s
        # niente marcatori annidati uguali: **a **b** c** diventa **a b c**
        interno = s.strip()
        if m == "**":
            interno = interno.replace("**", "")
        elif m == "__":
            interno = interno.replace("__", "")
        if not re.search(r"\w", interno) or (m in ("**", "*") and "*" in interno) or \
                (m == "__" and "__" in interno):
            return s      # il Markdown della dashboard non sa scriverlo: il testo resta senza marcatore
        if "\n" in interno:   # il Markdown in linea non attraversa gli a capo: un marcatore per riga
            righe = [r.strip() for r in interno.split("\n")]
            interno_m = "\n".join((m + r + m) if r else "" for r in righe)
        else:
            interno_m = m + interno + m
        pre = s[:len(s) - len(s.lstrip())]
        post = s[len(s.rstrip()):]
        return pre + interno_m + post

    @staticmethod
    def pulisci_paragrafo(s):
        righe = [re.sub(r" {2,}", " ", r).strip() for r in s.split("\n")]
        # righe vuote consecutive dentro un paragrafo: un a capo doppio apre un paragrafo nuovo
        out, vuote = [], 0
        for r in righe:
            if r:
                if vuote and out:
                    out.append("")
                out.append(r)
                vuote = 0
            else:
                vuote += 1
        txt = "\n".join(out).strip()
        txt = re.sub(r"(?<!\*)\*\*\*\*(?!\*)", "", txt)
        return txt

    # --- blocchi
    def blocchi(self, n):
        out, buf = [], []

        def chiudi_buf():
            if buf:
                t = self.pulisci_paragrafo(self.inline(_finto(buf)))
                if t:
                    out.append(t)
                buf.clear()
        for f in n.figli:
            if isinstance(f, str) or (f.tag not in BLOCCHI and not (f.tag == "code" and self.codice_a_blocco(f))):
                buf.append(f)
                continue
            chiudi_buf()
            out += self.blocco(f)
        chiudi_buf()
        return out

    def codice_a_blocco(self, n):
        return any(not isinstance(f, str) and f.tag == "br" for f in n.figli) or "\n" in n.testo().strip()

    def blocco(self, n):
        t = n.tag
        if t in ("h1", "h2", "h3"):
            s = self.pulisci_paragrafo(self.inline(n)).replace("\n", " ").replace("**", "")
            return ["%s %s" % ("#" * int(t[1]), s)] if s else []
        if t in ("h4", "h5", "h6"):
            s = self.pulisci_paragrafo(self.inline(n)).replace("\n", " ").replace("**", "")
            return ["**%s**" % s] if s else []
        if t in ("ul", "ol"):
            voci = []
            for i, li in enumerate([c for c in n.figli if not isinstance(c, str) and c.tag == "li"], 1):
                s = self.pulisci_paragrafo(self.inline(li)).replace("\n", " ")
                if s:
                    voci.append(("%d. " % i if t == "ol" else "- ") + s)
            return ["\n".join(voci)] if voci else []
        if t == "pre" or (t == "code"):
            return self.blocco_codice(n)
        if t == "table":
            return self.tabella(n)
        if t == "div":
            an = self.anteprima(n)
            if an:
                return an
            box = self.riquadro(n)
            if box:
                return box
            return self.blocchi(n)
        if t == "p":
            if any(not isinstance(f, str) and f.tag in BLOCCHI for f in n.figli):
                return self.blocchi(n)
            s = self.pulisci_paragrafo(self.inline(n))
            return [s] if s else []
        return self.blocchi(n)

    def anteprima(self, n):
        """Snippet con l'anteprima accanto (```html anteprima di da_dashboard.py): un div flex con il codice
        e un riquadro «Nel browser» che ripete l'HTML interpretato. Torna il blocco di codice con «anteprima»."""
        if "flex" not in stile(n):
            return None
        figli = [f for f in n.figli if not (isinstance(f, str) and not f.strip())]
        if len(figli) != 2 or any(isinstance(f, str) or f.tag != "div" for f in figli):
            return None
        primo = [f for f in figli[1].figli if not (isinstance(f, str) and not f.strip())]
        if not primo or isinstance(primo[0], str) or primo[0].tag != "p" or \
                re.sub(r"\s+", " ", primo[0].testo()).strip() != "Nel browser":
            return None
        codice = self.blocchi(figli[0])
        if len(codice) != 1 or not codice[0].startswith("```"):
            return None
        intestazione, resto = codice[0].split("\n", 1)
        return ["%s anteprima\n%s" % (intestazione if intestazione != "```" else "```html", resto)]

    def riquadro(self, n):
        m = re.search(r"background-color:\s*(#[0-9a-f]{6})", stile(n))
        if not m or "border-left" not in stile(n):
            return None
        colore = BOX_COL.get(m.group(1))
        if not colore:
            return None
        figli = [f for f in n.figli if not (isinstance(f, str) and not f.strip())]
        titolo = ""
        if figli and not isinstance(figli[0], str) and figli[0].tag == "p":
            forte = [f for f in figli[0].figli if not isinstance(f, str)]
            if len(forte) == 1 and forte[0].tag in ("strong", "b"):
                titolo = re.sub(r"\s+", " ", forte[0].testo()).strip()
                figli = figli[1:]
        interno = self.blocchi(_finto(figli))
        return [":::%s %s\n%s\n:::" % (colore, titolo, "\n\n".join(interno))]

    def blocco_codice(self, n):
        # <pre> che contiene una tabella o dei paragrafi (HTML dell'editor): non è codice
        if any(not isinstance(f, str) and f.tag in ("table", "div", "ul", "ol") for f in n.figli) or \
                (any(not isinstance(f, str) and f.tag == "p" and f.testo().strip() for f in n.figli)):
            return self.blocchi(n)
        codice = self.inline(n, in_code=True)
        codice = codice.replace("\r", "").strip("\n")
        righe = [r.rstrip() for r in codice.split("\n")]
        while righe and not righe[-1].strip():
            righe.pop()
        codice = "\n".join(righe)
        if not codice.strip():
            return []
        if "\n" not in codice and len(codice) < 90 and not re.search(r"[;{}=<>()]", codice) and \
                not self.campi_nel_testo(codice):
            return [codice.strip()]      # una frase dentro un <pre>: resta un paragrafo
        lingua = indovina_lingua(codice)
        return ["```%s\n%s\n```" % (lingua, codice)]

    @staticmethod
    def campi_nel_testo(s):
        return bool(re.search(r"\{\d*:[A-Z_]+:", s))

    def tabella(self, n):
        righe = []
        for tr in _cerca(n, "tr"):
            celle = [c for c in tr.figli if not isinstance(c, str) and c.tag in ("td", "th")]
            righe.append([(self.pulisci_paragrafo(self.inline(c)).replace("\n", " ").replace("|", "/"),
                           int(c.attrs.get("colspan") or 1), c.tag == "th") for c in celle])
        righe = [r for r in righe if any(c[0] for c in r)]
        if not righe:
            return []
        out = []
        # una prima riga con una sola cella su più colonne è il titolo della tabella
        larg = max(sum(c[1] for c in r) for r in righe)
        if len(righe[0]) == 1 and righe[0][0][1] > 1 and len(righe) > 1:
            out.append("**%s**" % righe[0][0][0].replace("**", ""))
            righe = righe[1:]
            larg = max(sum(c[1] for c in r) for r in righe)
        if larg == 1:      # tabella di una colonna: un elenco
            return out + ["\n".join("- " + r[0][0] for r in righe)]

        def riga(r):
            celle = []
            for testo, span, _ in r:
                celle += [testo] + [""] * (span - 1)
            celle += [""] * (larg - len(celle))
            return "| " + " | ".join(c or " " for c in celle) + " |"
        out.append("\n".join([riga(righe[0]), "| " + " | ".join(["---"] * larg) + " |"] + [riga(r) for r in righe[1:]]))
        return out

    def markdown(self, src):
        src = self.metti_campi(src or "")
        bl = [b for b in self.blocchi(albero(src)) if b.strip()]
        out = []
        for b in bl:
            m = re.fullmatch(r"`([^`]+)`", b.strip())
            if m and out and out[-1].startswith("```") and out[-1].endswith("\n```"):
                out[-1] = out[-1][:-4] + "\n" + m.group(1) + "\n```"
                continue
            out.append(b)
        return "\n\n".join(out).strip()

    def opzione(self, src):
        """Testo di un'opzione: una riga sola."""
        s = "\n".join(self.blocchi(albero(self.metti_campi(src or ""))))
        s = re.sub(r"```\w*\n?", "", s).strip()
        if "\n" in s:
            self.perdi("a capo dentro un'opzione (diventa « / »)")
            s = " / ".join(r for r in s.split("\n") if r.strip())
        return s

    def metti_campi(self, src):
        if not self.campi:
            return src
        return re.sub(r"\{#(\d+)\}", lambda m: self.campi.get(m.group(1), m.group(0)), src)


def _finto(figli):
    n = Nodo("span")
    n.figli = list(figli)
    return n


def _cerca(n, tag):
    for f in n.figli:
        if isinstance(f, str):
            continue
        if f.tag == tag:
            yield f
        elif f.tag != "table":
            yield from _cerca(f, tag)


def indovina_lingua(codice):
    c = codice.strip()
    if c.startswith("<?php") or re.search(r"\$\w+\s*=|mysqli_", c):
        return "php"
    if re.match(r"(?is)\s*(--|select|insert|update|delete|create|alter|drop)\b", c):
        return "sql"
    if re.match(r"\s*<", c):
        return "html"
    if re.search(r"\b(let|const|var|function|console\.log|prompt)\b", c):
        return "js"
    if re.search(r"^[\w.#:\-\s,>*\[\]=\"']+\{[^}]*:[^}]*;", c, re.M):
        return "css"
    return "semplice"


def testo_semplice(src, lim=None):
    s = re.sub(r"<[^>]+>", " ", html.unescape(src or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return s if lim is None or len(s) <= lim else s[:lim].rsplit(" ", 1)[0] + "…"


# ---------------------------------------------------------------- lettura del backup

class Backup:
    def __init__(self, cartella):
        self.dir = pathlib.Path(cartella)
        self.mb = ET.parse(self.dir / "moodle_backup.xml").getroot()
        self.qx = ET.parse(self.dir / "questions.xml").getroot() if (self.dir / "questions.xml").exists() else None
        self.file_per_item = {}   # (component, filearea, itemid) -> [(nome, percorso)]
        self.include_file = (self.dir / "files").exists()
        if (self.dir / "files.xml").exists():
            for f in ET.parse(self.dir / "files.xml").getroot().iter("file"):
                nome = f.findtext("filename")
                if nome == ".":
                    continue
                h = f.findtext("contenthash") or ""
                p = self.dir / "files" / h[:2] / h
                chiave = (f.findtext("component"), f.findtext("filearea"), f.findtext("itemid"))
                lista = self.file_per_item.setdefault(chiave, [])
                if nome not in [x[0] for x in lista]:
                    lista.append((nome, p if p.exists() else None))
        self.categorie, self.voci, self.domande_id = {}, {}, {}
        if self.qx is not None:
            for c in self.qx.iter("question_category"):
                self.categorie[c.get("id")] = {"nome": tx(c, "name"), "padre": tx(c, "parent"),
                                               "ctx": tx(c, "contextid"), "modulo": tx(c, "contextinstanceid"),
                                               "stamp": tx(c, "stamp")}
                for e in c.iter("question_bank_entry"):
                    versioni = []
                    for v in e.iter("question_versions"):
                        for q in v.findall("questions/question"):
                            versioni.append((int(tx(v, "version", "0") or 0), q))
                            self.domande_id[q.get("id")] = q
                    versioni.sort(key=lambda x: x[0])
                    self.voci[e.get("id")] = {"categoria": c.get("id"), "versioni": versioni}
                # sottodomande dei Cloze e domande senza voce (backup vecchi)
                for q in c.iter("question"):
                    self.domande_id.setdefault(q.get("id"), q)

    def quiz(self):
        out = []
        for a in self.mb.iter("activity"):
            if a.findtext("modulename") == "quiz" and a.findtext("directory"):
                f = self.dir / a.findtext("directory") / "quiz.xml"
                if f.exists():
                    out.append((self.dir / a.findtext("directory"), ET.parse(f).getroot().find("quiz")))
        return out

    def tag_di(self, q):
        return [tx(t, "rawname") or tx(t, "name") for t in q.iter("tag")]

    def file(self, componente, area, item):
        return self.file_per_item.get((componente, area, str(item)), [])


# ---------------------------------------------------------------- database SQLite -> script

def script_da_db(percorso):
    """Script SQL (CREATE TABLE e INSERT, come in phpMyAdmin) che ricrea il database."""
    con = sqlite3.connect("file:%s?mode=ro" % percorso, uri=True)
    pezzi = []
    oggetti = con.execute("SELECT type, name, sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' "
                          "ORDER BY CASE type WHEN 'table' THEN 0 WHEN 'index' THEN 1 ELSE 2 END, rowid").fetchall()
    for tipo, nome, sql in oggetti:
        if tipo != "table":
            continue
        pezzi.append(sql.strip().rstrip(";") + ";")
    for tipo, nome, sql in oggetti:
        if tipo != "table":
            continue
        cur = con.execute('SELECT * FROM "%s"' % nome.replace('"', '""'))
        righe = cur.fetchall()
        if not righe:
            continue
        colonne = [d[0] for d in cur.description]

        def val(v):
            if v is None:
                return "NULL"
            if isinstance(v, (int, float)):
                return repr(v) if isinstance(v, float) else str(v)
            if isinstance(v, bytes):
                return "X'%s'" % v.hex()
            return "'%s'" % str(v).replace("'", "''")
        pezzi.append("INSERT INTO %s (%s) VALUES\n%s;" % (
            nome, ", ".join(colonne), ",\n".join("(%s)" % ", ".join(val(v) for v in r) for r in righe)))
    for tipo, nome, sql in oggetti:
        if tipo in ("index", "view", "trigger"):
            pezzi.append(sql.strip().rstrip(";") + ";")
    con.close()
    return "\n\n".join(pezzi) + "\n"


def contenuto_db(percorso):
    """Impronta del contenuto (schema e righe) per riconoscere database uguali."""
    con = sqlite3.connect("file:%s?mode=ro" % percorso, uri=True)
    h = hashlib.sha1()
    for nome, sql in con.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
        h.update(re.sub(r"\s+", " ", sql or "").encode())
        for r in con.execute('SELECT * FROM "%s" ORDER BY 1' % nome.replace('"', '""')):
            h.update(repr(r).encode())
    con.close()
    return h.hexdigest()


def tabelle_db(percorso):
    con = sqlite3.connect("file:%s?mode=ro" % percorso, uri=True)
    n = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    righe = sum(con.execute('SELECT COUNT(*) FROM "%s"' % t.replace('"', '""')).fetchone()[0] for t in n)
    con.close()
    return n, righe


# ---------------------------------------------------------------- domande -> righe

def opz(q, nome):
    """Elemento delle opzioni del tipo di domanda (coderunner_option, multichoice, …)."""
    return q.find(".//" + nome)


def nome_parti(nome):
    """«V5R - T2a - Scrivere: titolo» -> (lezione, pos, prefisso, titolo) oppure None."""
    m = NOME_RE.match((nome or "").strip())
    if not m:
        return None
    resto = m.group("resto")
    prefisso = ""
    for p in sorted(PREFISSI, key=len, reverse=True):
        if resto.startswith(p + ": "):
            prefisso, resto = p, resto[len(p) + 2:]
            break
    lez = m.group("lez")
    return (lez[1:] if re.match(r"L\d+$", lez) else lez), m.group("pos"), prefisso, resto.strip()


class Importatore:
    def __init__(self, bk):
        self.bk = bk
        self.db = {}           # impronta -> {nome, sql, percorso}
        self.nomi_db = {}      # nome -> impronta
        self.proto_html = set()  # prototipi degli esercizi HTML trovati (php_con_test, html)

    # --- database allegati
    def database_di(self, q):
        """Nome del database allegato alla domanda CodeRunner (aggiunto ai database del quiz) e dati."""
        files = self.bk.file("qtype_coderunner", "datafile", q.get("id"))
        dbf = [(n, p) for n, p in files if n.lower().endswith((".db", ".sqlite", ".sqlite3"))]
        if not dbf:
            return None, None, files
        nome_file, percorso = dbf[0]
        base = re.sub(r"\.(db|sqlite3?)$", "", nome_file, flags=re.I)
        dati = None
        m = re.match(r"(.+)_(struttura|vuoto)$", base)
        if m:
            base, dati = m.group(1), m.group(2)
        base = re.sub(r"[^\w-]+", "_", base).strip("_") or "db"
        if percorso is None:
            return base, dati, files
        if dati:      # struttura o vuoto: il database pieno di solito c'è già; non serve lo script
            if base not in self.nomi_db:
                self.nomi_db.setdefault(base + "_" + dati, None)
            return base, dati, files
        imp = contenuto_db(percorso)
        if imp in self.db:
            return self.db[imp]["nome"], None, files
        nome, k = base, 2
        while nome in self.nomi_db and self.nomi_db[nome] is not None:
            nome, k = "%s%d" % (base, k), k + 1
        self.nomi_db[nome] = imp
        self.db[imp] = {"nome": nome, "sql": script_da_db(percorso), "percorso": percorso}
        return nome, None, files

    # --- una domanda
    def riga(self, q, contesto):
        """Restituisce (campi della riga, perdite, avvisi)."""
        tipo = tx(q, "qtype")
        parti = nome_parti(tx(q, "name"))
        prefisso = parti[2] if parti else ""
        campi_cloze = {}
        if tipo == "multianswer":
            seq = tx(opz(q, "multianswer"), "sequence")
            for i, sid in enumerate([s for s in seq.split(",") if s.strip()], 1):
                sq = self.bk.domande_id.get(sid.strip())
                if sq is not None:
                    campi_cloze[str(i)] = tx(sq, "questiontext")
        conv = Convertitore(campi_cloze)
        avvisi = []
        testo_html = tx(q, "questiontext")
        r = {"traccia": "", "correzione": "", "coderunner": "", "tipologia": ""}
        gf = tx(q, "generalfeedback")
        if tipo == "description":
            r["tipologia"] = "paginablocco"
            r["traccia"] = conv.markdown(testo_html)
        elif tipo in ("multichoice", "truefalse", "shortanswer"):
            r.update(self.scelte(q, tipo, prefisso, conv))
            r["correzione"] = conv.markdown(gf)
        elif tipo == "match":
            r.update(self.corrispondenza(q, conv))
            r["correzione"] = conv.markdown(gf)
        elif tipo == "multianswer":
            r["traccia"] = conv.markdown(testo_html)
            r["tipologia"] = self.tipologia_cloze(prefisso, r["traccia"])
            r["correzione"] = conv.markdown(gf)
        elif tipo == "essay":
            r["traccia"] = conv.markdown(testo_html)
            gi = tx(opz(q, "essay"), "graderinfo")
            r["correzione"] = conv.markdown(gi)
            if testo_semplice(gf):
                if not testo_semplice(gi):
                    r["correzione"] = conv.markdown(gf)
                    conv.perdi("feedback generale della domanda aperta, visibile agli studenti, messo nella correzione "
                               "(da_dashboard.py la scrive nelle informazioni per chi corregge)")
                else:
                    conv.perdi("feedback generale della domanda aperta (c'erano anche le informazioni per chi corregge: "
                               "il feedback generale non è stato importato)")
            r["tipologia"] = {"Debug": "debug_motivazione", "Esercizio libero": "esercizio_libero"}.get(prefisso, "teoria_aperta")
            if tx(opz(q, "essay"), "responseformat") == "noinline" and tx(opz(q, "essay"), "attachments", "0") not in ("0", ""):
                r["tipologia"] = "consegna_file"     # solo un file da caricare, nessun testo
                # tipi di file diversi da quelli predefiniti (.html .htm .css): tornano come «tipi: …» in === options
                tipi = [t if t.startswith(".") else "." + t for t in
                        re.split(r"[\s,;]+", tx(opz(q, "essay"), "filetypeslist").strip().lower()) if t]
                if tipi and sorted(tipi) != sorted([".html", ".htm", ".css"]):
                    r["coderunner"] = "=== options\ntipi: " + " ".join(tipi)
        elif tipo == "coderunner":
            r.update(self.coderunner(q, prefisso, conv, avvisi))
            r["correzione"] = conv.markdown(gf)
        else:
            r["traccia"] = conv.markdown(testo_html)
            avvisi.append("tipo di domanda Moodle «%s» non previsto nella dashboard: importato solo il testo" % tipo)
        return r, conv, avvisi

    def tipologia_cloze(self, prefisso, traccia):
        if prefisso:
            for t in PREFISSI.get(prefisso, []):
                if t in ("esempio_svolto", "tracciamento", "compl_campi", "guidato"):
                    return t
        campi = re.findall(r"\{\d*:([A-Z_]+):((?:\\.|[^}\\])*)\}", traccia)
        menu = [c for t, c in campi if t.startswith("MULTICHOICE") and not t.endswith("_S")]
        if len(menu) > 1 and len({tuple(sorted(re.sub(r"^=|#.*$", "", o) for o in c.split("~"))) for c in menu}) == 1:
            return "ordine"
        if "```" in traccia and re.search(r"```[\s\S]*?\{\d*:[A-Z_]+:", traccia):
            return "compl_campi"
        return "cloze_testo"

    def scelte(self, q, tipo, prefisso, conv):
        risposte = []
        for a in q.iter("answer"):
            if a.find("answertext") is None:
                continue
            risposte.append((float(tx(a, "fraction", "0") or 0) * 100, tx(a, "answertext"), tx(a, "feedback"), a.get("id")))
        if tipo == "truefalse":
            tf = opz(q, "truefalse")
            vero_id = tx(tf, "trueanswer")
            righe = []
            per_id = {x[3]: x for x in risposte}
            for etichetta, aid in (("Vero", vero_id), ("Falso", tx(tf, "falseanswer"))):
                fr, _, fb, _ = per_id.get(aid, (0, "", "", ""))
                righe.append("(%s) %s" % ("x" if fr > 0 else " ", etichetta))
                f = conv.opzione(fb)
                if f:
                    righe.append("    > " + f)
            return {"traccia": conv.markdown(tx(q, "questiontext")) + "\n\n" + "\n".join(righe), "tipologia": "vf"}
        if tipo == "shortanswer":
            righe = []
            for fr, testo, fb, _ in risposte:
                t = testo.strip()
                if fr >= 100:
                    righe.append("(x) " + t)
                elif fr > 0:
                    righe.append("(x %g%%) %s" % (fr, t))
                else:
                    righe.append("( ) " + t)
                f = conv.opzione(fb)
                if f:
                    righe.append("    > " + f)
            return {"traccia": conv.markdown(tx(q, "questiontext")) + "\n\n" + "\n".join(righe), "tipologia": "breve"}
        mc = opz(q, "multichoice")
        singola = tx(mc, "single", "1") in ("1", "true")
        giuste = [x for x in risposte if x[0] > 0]
        sbagliate = [x for x in risposte if x[0] <= 0]
        righe = []
        if singola:
            for fr, testo, fb, _ in risposte:
                marca = "x" if fr >= 100 else (" %g%%" % fr if fr != 0 else " ")
                righe.append("(%s) %s" % (marca.strip() if marca.strip() == "x" else marca, conv.opzione(testo)))
                f = conv.opzione(fb)
                if f:
                    righe.append("    > " + f)
        else:
            quota = 100.0 / len(giuste) if giuste else 0
            uguali_g = all(abs(x[0] - quota) < 0.01 for x in giuste)
            neg = [x[0] for x in sbagliate]
            pen = -100.0 / len(sbagliate) if sbagliate else 0
            uguali_s = all(abs(v - pen) < 0.01 for v in neg)
            for fr, testo, fb, _ in risposte:
                if fr > 0:
                    marca = "x" if uguali_g else "x %g%%" % round(fr, 5)
                else:
                    marca = " " if uguali_s else " %g%%" % round(fr, 5)
                righe.append("[%s] %s" % (marca, conv.opzione(testo)))
                f = conv.opzione(fb)
                if f:
                    righe.append("    > " + f)
        tip = "trova_errore" if prefisso == "Trova l'errore" else ("multipla" if singola else "crocette")
        return {"traccia": conv.markdown(tx(q, "questiontext")) + "\n\n" + "\n".join(righe), "tipologia": tip}

    def corrispondenza(self, q, conv):
        righe = []
        for m in q.iter("match"):
            sx = conv.opzione(tx(m, "questiontext"))
            dx = testo_semplice(tx(m, "answertext"))
            righe.append(("%s <-> %s" % (sx, dx)) if sx else "<-> " + dx)
        return {"traccia": conv.markdown(tx(q, "questiontext")) + "\n\n" + "\n".join(righe), "tipologia": "corrispondenza"}

    # --- CodeRunner
    def coderunner(self, q, prefisso, conv, avvisi):
        o = opz(q, "coderunner_option")
        tipo = tx(o, "coderunnertype")
        test = []
        for t in q.iter("coderunner_testcase"):
            test.append({k: tx(t, k) for k in ("testcode", "testtype", "expected", "useasexample", "display", "stdin", "extra", "mark")})
        test.sort(key=lambda x: 0)   # l'ordine del backup è quello delle domande
        answer, preload = tx(o, "answer"), tx(o, "answerpreload")
        testo = tx(q, "questiontext")
        sez, opzioni = [], []
        tl = tipo.lower()
        if tl in ("sql_salvemini", "sql", "sql_foreignkeys"):
            nome_db, dati, _ = self.database_di(q)
            if tl != "sql_salvemini":
                avvisi.append("prototipo CodeRunner «%s» (vecchio): la parte 2 la rigenera con sql_salvemini" % tipo)
            if nome_db:
                opzioni.append("database: %s" % nome_db)
            else:
                avvisi.append("nessun database allegato alla domanda")
            if dati:
                opzioni.append("dati: %s" % dati)
            if tx(o, "precheck", "0") not in ("0", ""):
                opzioni.append("precheck: 1")
            tp = tx(o, "templateparams")
            if re.search(r'"foreign_keys"\s*:\s*false', tp or ""):
                opzioni.append("foreign_keys: 0")
            if tx(o, "allornothing", "1") == "0":
                opzioni.append("allornothing: 0")
            grader = tx(o, "grader")
            if grader and grader != "EqualityGrader":
                opzioni.append("grader: %s" % grader)
            if tx(o, "hidecheck", "0") == "1":
                opzioni.append("hidecheck: 1")
            if opzioni:
                sez.append(("options", "\n".join(opzioni)))
            if preload.strip():
                sez.append(("preload", preload.strip("\n")))
            sez.append(("answer", answer.strip("\n")))
            for t in test:
                if t["testtype"] == "1":        # controllo di sola sintassi: lo rimette precheck: 1
                    continue
                codice = STRUTTURA_RE.sub(lambda m: "[[struttura %s]]" % m.group(1), t["testcode"].replace("\r", ""))
                sez.append(("test HIDE" if t["display"] == "HIDE" else "test", codice.strip("\n")))
                if t["extra"].strip():
                    sez.append(("extra", t["extra"].strip("\n")))
                if grader == "RegexGrader" and t["expected"].strip():
                    sez.append(("expected", t["expected"].strip("\n")))
            tip = self.tipologia_cr_sql(prefisso, answer, preload)
        elif tl == "php_mysqli_sqlite":
            testo = re.sub(r'<div[^>]*>\s*<p[^>]*>\s*<strong>N\.B\. questa è una simulazione</strong>\s*</p>[\s\S]*?</div>\s*$',
                           "", testo.strip())
            nome_db, dati, _ = self.database_di(q)
            normalizza = all(t["testcode"].lstrip().startswith(NORMALIZZA_INIZIO) for t in test) if test else True
            if tx(o, "allornothing", "1") == "0":
                opzioni.append("allornothing: 0")
            if not normalizza:
                opzioni.append("normalizza: 0")
            for k in ("precheck", "hidecheck"):
                if tx(o, k, "0") not in ("0", ""):
                    opzioni.append("%s: %s" % (k, tx(o, k)))
            db_test = None
            corpo_test = []
            for t in test:
                c = t["testcode"].replace("\r", "")
                if normalizza:
                    i = c.find("});")
                    if c.lstrip().startswith(NORMALIZZA_INIZIO) and i >= 0:
                        c = c[i + 3:].lstrip("\n")
                m = CONFIGURA_RE.search(c)
                if m:
                    db_test = m.group(1)
                    c = c[:m.start()]
                corpo_test.append((t, c.strip("\n")))
            if nome_db or db_test:
                opzioni.append("database: %s" % (nome_db or db_test))
            if opzioni:
                sez.append(("options", "\n".join(opzioni)))
            if preload.strip():
                sez.append(("preload", preload.strip("\n")))
            sez.append(("answer", answer.strip("\n")))
            for t, c in corpo_test:
                sez.append(("test HIDE" if t["display"] == "HIDE" else "test", c))
                if t["extra"].strip():
                    sez.append(("descrizione", t["extra"].strip("\n")))
            tip = {"Debug": "debug_msg"}.get(prefisso, "pagina_php")
            if prefisso == "Scrivere" and preload.strip():
                tip = "pagina_php"
        elif tl in ("php_con_test", "css", "html"):
            def dal_json(s):
                try:
                    return (json.loads(s).get("answer_code") or [""])[0]
                except (ValueError, AttributeError):
                    return s
            if tl == "php_con_test":
                answer, preload = dal_json(answer), dal_json(preload)
            if tl != "css":
                self.proto_html.add(tl)
            for k, v, nome in (("answerboxlines", "18", "righe"), ("answerboxcolumns", "100", "colonne")):
                if tx(o, k, v) not in (v, ""):
                    opzioni.append("%s: %s" % (nome, tx(o, k)))
            if opzioni:
                sez.append(("options", "\n".join(opzioni)))
            if preload.strip():
                sez.append(("preload", preload.strip("\n")))
            sez.append(("answer", answer.strip("\n")))
            tip = "libero_css" if tl == "css" else "libero_html"
            testo = rimuovi_riquadro(testo, "Attenzione al controllo automatico")
        elif tl.startswith("javascript"):
            gap = "gapfiller" in tl
            tp = {}
            try:
                tp = json.loads(tx(o, "templateparams") or "{}") or {}
            except ValueError:
                pass
            if tp.get("test_prima"):
                opzioni.append("test_prima: 1")
            if tp.get("random"):
                opzioni.append("random: %s" % ", ".join("%g" % x for x in tp["random"]))
            esempi = [t["useasexample"] == "1" for t in test if t["display"] != "HIDE"]
            if esempi and all(esempi) and len(esempi) > 1:
                opzioni.append("esempi: tutti")
            elif esempi and not any(esempi):
                opzioni.append("esempi: nessuno")
            if tx(o, "allornothing", "1") == "0":
                opzioni.append("allornothing: 0")
            if tx(o, "hidecheck", "0") == "1":
                opzioni.append("hidecheck: 1")
            if tx(o, "answerboxlines", "18") not in ("18", ""):
                opzioni.append("answerboxlines: %s" % tx(o, "answerboxlines"))
            if opzioni:
                sez.append(("options", "\n".join(opzioni)))
            if gap:
                sez.append(("code", tx(o, "globalextra").strip("\n")))
                try:
                    risposte = json.loads(answer)
                except ValueError:
                    risposte = answer.split("\n")
                sez.append(("answer", "\n".join(risposte)))
            else:
                if preload.strip():
                    sez.append(("preload", preload.strip("\n")))
                sez.append(("answer", answer.strip("\n")))
            for t in test:
                sez.append(("test HIDE" if t["display"] == "HIDE" else "test", t["testcode"].replace("\r", "").strip("\n")))
                if t["stdin"].strip():
                    sez.append(("stdin", t["stdin"].replace("\r", "").strip("\n")))
                if t["extra"].strip():
                    sez.append(("extra", t["extra"].strip()))
            if gap:
                tip = "compl_eseguito"
            elif prefisso == "Debug":
                tip = "debug_msg"
            elif preload.strip():
                tip = "scrittura_scheletro"
            else:
                chiama = any(re.search(r"^\s*[^/\s].*\w+\s*\(", t["testcode"], re.M) for t in test)
                tip = "funzione" if chiama else "prog_completo"
        else:
            avvisi.append("prototipo CodeRunner «%s» non gestito dalla dashboard: soluzione e test importati così come sono" % tipo)
            sez.append(("linguaggio", tipo))
            if preload.strip():
                sez.append(("preload", preload.strip("\n")))
            sez.append(("answer", answer.strip("\n")))
            for t in test:
                sez.append(("test HIDE" if t["display"] == "HIDE" else "test", t["testcode"].strip("\n")))
                for k in ("stdin", "extra", "expected"):
                    if t[k].strip():
                        sez.append((k, t[k].strip("\n")))
            tip = "query" if "sql" in tl else ""
        cr = "\n".join("=== %s\n%s" % (n, c) for n, c in sez)
        return {"traccia": conv.markdown(testo), "coderunner": cr, "tipologia": tip}

    @staticmethod
    def tipologia_cr_sql(prefisso, answer, preload):
        a = answer.upper()
        if prefisso == "Debug":
            return "debug_msg"
        if prefisso == "Campo di prova":
            return "campo_prova"
        if prefisso == "Esercizio":
            return "vincoli"
        if re.search(r"\bCREATE\s+TABLE\b", a):
            return "create_tabelle"
        return "query"


def rimuovi_riquadro(src, titolo):
    i = src.find(titolo)
    if i < 0:
        return src
    inizio = src.rfind("<div", 0, i)
    fine = src.find("</div>", i)
    if inizio < 0 or fine < 0:
        return src
    return (src[:inizio] + src[fine + 6:]).strip()


# ---------------------------------------------------------------- il quiz

def slot_del_quiz(bk, qz):
    sezioni = {}
    for s in qz.iter("section"):
        sezioni[int(tx(s, "firstslot", "0") or 0)] = tx(s, "heading")
    slot = sorted(qz.iter("question_instance"), key=lambda x: int(tx(x, "slot", "0") or 0))
    out, cur = [], ""
    for sl in slot:
        n = int(tx(sl, "slot", "0") or 0)
        if n in sezioni:
            cur = sezioni[n]
        voce = {"slot": n, "pagina": int(tx(sl, "page", "1") or 1), "punti": float(tx(sl, "maxmark", "0") or 0),
                "sezione": cur, "domande": [], "tag": ""}
        ref, sref = sl.find(".//question_reference"), sl.find(".//question_set_reference")
        if ref is not None:
            v = bk.voci.get(tx(ref, "questionbankentryid"))
            if v and v["versioni"]:
                ver = tx(ref, "version")
                scelta = v["versioni"][-1]
                if ver and ver.isdigit():
                    scelta = next((x for x in v["versioni"] if x[0] == int(ver)), scelta)
                voce["domande"].append({"versioni": v["versioni"], "usata": scelta})
            else:
                voce["mancante"] = "domanda di un'altra banca, non inclusa nel backup"
        elif sref is not None:
            try:
                fc = json.loads(tx(sref, "filtercondition") or "{}")
            except ValueError:
                fc = {}
            filtro = fc.get("filter", {})
            tag_id = [str(x) for x in filtro.get("qtagids", {}).get("values", [])]
            nomi_tag = set()
            for q in bk.domande_id.values():
                for t in q.iter("tag"):
                    if t.get("id") in tag_id:
                        nomi_tag.add(tx(t, "rawname") or tx(t, "name"))
            voce["tag"] = sorted(nomi_tag)[0] if nomi_tag else ""
            cand = []
            for v in bk.voci.values():
                ultima = v["versioni"][-1][1] if v["versioni"] else None
                if ultima is not None and nomi_tag and {x.lower() for x in nomi_tag} <= {x.lower() for x in bk.tag_di(ultima)}:
                    cand.append({"versioni": v["versioni"], "usata": v["versioni"][-1]})
            cand.sort(key=lambda d: tx(d["usata"][1], "name"))
            voce["domande"] = cand
            if not cand:
                voce["mancante"] = "domanda casuale senza domande nel backup (tag %s)" % (", ".join(nomi_tag) or "?")
        out.append(voce)
    return out


def importa(bk, cartella_quiz, qz, qid=None):
    imp = Importatore(bk)
    nome_quiz = tx(qz, "name")
    slot = slot_del_quiz(bk, qz)
    verifica = tx(qz, "attempts_number", "0") == "1"
    # lezione dai nomi delle domande, se seguono la convenzione; altrimenti dal nome del quiz
    lezioni = []
    for s in slot:
        for d in s["domande"]:
            p = nome_parti(tx(d["usata"][1], "name"))
            if p:
                lezioni.append(p[0])
    lezione = max(set(lezioni), key=lezioni.count) if lezioni else ""
    convenzione = bool(lezioni) and len(lezioni) == sum(len(s["domande"]) for s in slot)
    if not lezione:
        m = re.match(r"\s*(?:Lezione\s*)?(\d+)\b", nome_quiz)
        lezione = m.group(1) if m else ""
    # argomento dalla categoria delle domande («Lezione N - argomento», «V5R - argomento»)
    cat_di, catid_di = {}, {}
    for v in bk.voci.values():
        for _, q in v["versioni"]:
            cat_di[id(q)] = bk.categorie.get(v["categoria"], {}).get("nome", "")
            catid_di[id(q)] = v["categoria"]
    # banche esterne al quiz (per esempio un deposito): il loro contesto non è quello di un'attività del backup
    propri = set()
    try:
        import xml.etree.ElementTree as ET2
        mb = ET2.parse(str(pathlib.Path(bk.dir) / "moodle_backup.xml")).getroot()
        propri = {a.findtext("contextid") for a in mb.iter("activity")} | {a.findtext("moduleid") for a in mb.iter("activity")}
    except Exception:
        pass
    esterne = {}
    cat = next((cat_di.get(id(d["usata"][1]), "") for s in slot for d in s["domande"]), "")
    m = re.match(r"^(?:Lezione\s+\S+\s+-\s+|[A-Z][A-Z0-9]*\d[A-Z0-9]*\s+-\s+|\d[A-Z][A-Z0-9]*\s+-\s+|\d+\s*-\s*)(.+)$", cat)
    argomento = m.group(1) if m else (cat or nome_quiz)

    righe, rapporto, n = [], [], 0
    lettere, sezioni_viste = {}, []
    contatori = {}
    for s in slot:
        if s["sezione"] not in sezioni_viste:
            sezioni_viste.append(s["sezione"])
    titoli_sez = {}
    for i, h in enumerate(sezioni_viste):
        nome_s = h.strip() or ("Introduzione" if i == 0 else "Sezione %d" % (i + 1))
        titoli_sez[h] = nome_s
        lettere[h] = chr(ord("A") + i) if i < 26 else "Z"
    for s in slot:
        if s.get("mancante") and not s["domande"]:
            rapporto.append("- slot %d (pagina %d): %s: non importato" % (s["slot"], s["pagina"], s["mancante"]))
            continue
        for d in s["domande"]:
            ver_n, q = d["usata"]
            prima = d["versioni"][0][1]
            nome = tx(q, "name")
            parti = nome_parti(nome)
            primo_della_sezione = not any(r["sezione"] == titoli_sez[s["sezione"]] for r in righe)
            campi, conv, avvisi = imp.riga(q, {})
            if tx(q, "qtype") == "description" and not (parti and parti[2]):
                if (parti and parti[1] == "00") or (not parti and not righe and verifica):
                    campi["tipologia"] = "istruzioni" if verifica else "comelavoriamo"
            if parti and convenzione:
                pos, titolo = parti[1], parti[3]
            else:
                lett = lettere[s["sezione"]]
                k = contatori.get(lett, 0)
                if tx(q, "qtype") == "description" and primo_della_sezione:
                    pos = "00" if not righe and lett == "A" and campi["tipologia"] in ("istruzioni", "comelavoriamo") else lett + "0"
                else:
                    k += 1
                    contatori[lett] = k
                    pos = "%s%d" % (lett, k)
                titolo = re.sub(r"\s+", " ", nome).strip()
            n += 1
            perdite = list(conv.perdite)
            nota = []
            if perdite:
                nota.append("Importata da Moodle: " + "; ".join(perdite) + ".")
            nota += avvisi
            if len(d["versioni"]) > 1:
                cambiata = normalizza_html(tx(prima, "questiontext")) != normalizza_html(tx(q, "questiontext")) or \
                    impronta_domanda(prima) != impronta_domanda(q)
                if not cambiata:
                    pass   # versioni che cambiano solo la formattazione: niente da dire
            r = {
                "ordine": n * 10, "sezione": titoli_sez[s["sezione"]], "pos": pos, "pag": s["pagina"],
                "titolo": titolo, "sintesi": sintesi(campi, q), "tipologia": campi["tipologia"],
                "parte": 0 if campi["tipologia"] in PAGINE else 1,
                "punti": numero(s["punti"]) if campi["tipologia"] not in PAGINE else 0,
                "minuti": "", "strumento": "", "sostegno": "",
                "stato": "da-rivedere" if nota else "approvata",
                "traccia": campi["traccia"], "correzione": campi["correzione"], "coderunner": campi["coderunner"],
                "tag": s["tag"] or "", "nota": " ".join(nota),
                "docente": "Importata dal backup «%s»: domanda Moodle «%s» (%s%s)." % (
                    nome_quiz, nome, tx(q, "qtype"), (", v%d di %d" % (ver_n, len(d["versioni"]))) if len(d["versioni"]) > 1 else ""),
            }
            if not s["tag"]:
                r.pop("tag")
            ci = bk.categorie.get(catid_di.get(id(q)), {})
            if ci and ci.get("ctx") not in propri and ci.get("modulo") not in propri:
                # domanda di una banca esterna (deposito): lo stamp serve a riusarla senza doppioni
                r["stampOrigine"] = tx(q, "stamp")
                esterne.setdefault((ci["ctx"], ci["modulo"], ci["nome"], ci["stamp"]), []).append(pos)
            righe.append(r)
            if nota:
                rapporto.append("- %s %s: %s" % (pos, titolo, " ".join(nota)))
    for (ctx_e, mod_e, nome_e, stamp_e), poss in esterne.items():
        rapporto.append("- Domande %s dalla banca esterna (contesto %s, modulo %s), categoria «%s» (stamp %s): "
                        "hanno lo stamp d'origine (stampOrigine); per rigenerarle nel deposito senza doppioni "
                        "scegli il deposito nei dati del quiz e ripristina nel corso del deposito."
                        % (", ".join(poss), ctx_e, mod_e, nome_e, stamp_e))
    dbs = [{"nome": v["nome"], "sql": v["sql"]} for v in imp.db.values()]
    mancano_db = sorted(k for k, v in imp.nomi_db.items() if v is None and not any(k.startswith(d["nome"] + "_") for d in dbs))
    gp = 6
    gf = cartella_quiz / "grades.xml"
    if gf.exists():
        try:
            gp = float(ET.parse(gf).getroot().findtext(".//gradepass") or 0) or 6
        except (ValueError, ET.ParseError):
            pass
    voto = float(tx(qz, "grade", "10") or 10)
    tl = int(tx(qz, "timelimit", "0") or 0)
    quiz = {
        "titolo": nome_quiz, "nomeQuiz": nome_quiz, "tipoQuiz": "IMP", "lezione": lezione, "argomento": argomento,
        "tempo": tl // 60 if tl else "", "fase": "dettaglio-revisione",
        "presetMbz": "verifica" if verifica else "esercitazione",
        "voto": numero(voto), "sufficienza": numero(gp), "titoliSezioni": {v: v for v in titoli_sez.values()},
        "note": "Importato dal backup Moodle «%s» (%s). %d domande in %d sezioni. Tipo «importato»: nessun preset; "
                "minuti, parti e strumento non sono nel backup.%s" % (
                    nome_quiz, "impostazioni da verifica" if verifica else "impostazioni da esercitazione", len(righe),
                    len(titoli_sez), (" Mancano i file allegati (backup senza «Includi file»): database e immagini non importati."
                                      if not bk.include_file else "")),
        "creato": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
    }
    if dbs:
        quiz["database"] = dbs
    if imp.proto_html == {"html"}:
        quiz["prototipoHtml"] = "html"     # esercizi HTML senza anteprima (prototipo html)
    elif len(imp.proto_html) > 1:
        rapporto.append("- Esercizi HTML con prototipi diversi (php_con_test e html): il quiz resta «con anteprima» "
                        "(php_con_test); per generarli tutti con il prototipo html scegli «senza anteprima» nei dati del quiz.")
    qid = qid or slug_id(nome_quiz)
    return qid, quiz, righe, rapporto, imp, mancano_db


def numero(x):
    f = float(x)
    return int(f) if f == int(f) else round(f, 5)


def slug_id(t):
    s = re.sub(r"[^a-z0-9]+", "-", __import__("unicodedata").normalize("NFD", t.lower()).encode("ascii", "ignore").decode())
    return "-".join([p for p in s.split("-") if p][:5]) or "quiz-importato"


def sintesi(campi, q):
    if campi["tipologia"] in PAGINE:
        tit = re.match(r"#\s+(.+)", campi["traccia"])
        return ("Pagina: " + tit.group(1)) if tit else "Pagina: " + testo_semplice(tx(q, "questiontext"), 100)
    testo = campi["traccia"]
    testo = re.sub(r"```[\s\S]*?```", " ", testo)
    testo = "\n".join(l for l in testo.split("\n") if not re.match(r"\s*([(\[]|>|\||:::)", l))
    testo = re.sub(r"[*_`#]", "", testo)
    paragrafi = [p.strip() for p in re.split(r"\n\s*\n", testo) if p.strip()]
    scelto = ""
    for i, p in enumerate(paragrafi):
        if re.search(r"\b(scriver|restituisc|mostr|elenc|calcol|defini|complet|indica|seleziona)", p, re.I):
            scelto = p
            if (p.rstrip().endswith(":") or re.search(r"restituisc\w*\W*$", p)) and i + 1 < len(paragrafi):
                scelto = paragrafi[i + 1]
            break
    if not scelto:
        scelto = paragrafi[-1] if paragrafi else ""
        if len(scelto) < 25 and len(paragrafi) > 1:
            scelto = paragrafi[-2] + " " + scelto
    scelto = re.sub(r"\s+", " ", scelto)
    return scelto if len(scelto) <= 160 else scelto[:160].rsplit(" ", 1)[0] + "…"


def normalizza_html(s):
    s = html.unescape(s or "")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r">\s+<", "><", s)
    return s.strip()


def impronta_domanda(q):
    """Contenuto della domanda che conta (testi, risposte, opzioni CodeRunner, test), senza date e id."""
    via = {"timecreated", "timemodified", "stamp", "version", "id", "createdby", "modifiedby", "hidden", "idnumber",
           "minwordlimit", "maxwordlimit", "contextid"}
    out = []
    for el in q.iter():
        if el.tag in via:
            continue
        t = (el.text or "").strip()
        if t and t != NULL:
            out.append("%s=%s" % (el.tag, normalizza_html(t)))
    return out


# ---------------------------------------------------------------- ordine unico delle query

def _order_by(q):
    """Posizione dell'ORDER BY principale (fuori dalle parentesi e dalle stringhe), oppure -1."""
    prof, pos, i, n = 0, -1, 0, len(q)
    while i < n:
        c = q[i]
        if c == "'":
            j = q.find("'", i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == "(":
            prof += 1
        elif c == ")":
            prof -= 1
        elif prof == 0 and re.match(r"(?i)order\s+by\b", q[i:i + 12]) and (i == 0 or not q[i - 1].isalnum()):
            pos = i
        i += 1
    return pos


def _con_spareggio(q, ncol, verso):
    """La query con, dopo le chiavi dell'ORDER BY, tutte le colonne in ordine crescente o decrescente."""
    q = q.strip().rstrip(";")
    extra = ", ".join("%d %s" % (k, verso) for k in range(1, ncol + 1))
    i = _order_by(q)
    if i < 0:
        return None
    m = re.search(r"(?is)\blimit\b[^()']*$", q[i:])
    if m:
        j = i + m.start()
        return q[:j].rstrip() + ", " + extra + " " + q[j:]
    return q + ", " + extra


def _letture(script, extra, answer, test):
    """Esegue extra e soluzione sul database; restituisce (connessione, query da confrontare)."""
    con = sqlite3.connect(":memory:")
    con.executescript(script)
    if extra.strip():
        con.executescript(extra)
    istr = [x.strip() for x in re.split(r";\s*(?:\n|$)", answer) if x.strip() and not re.fullmatch(r"(--[^\n]*\n?)+", x.strip())]
    select = [x for x in istr if re.match(r"(?is)\s*(--[^\n]*\n\s*)*(select|with)\b", x)]
    altre = [x for x in istr if x not in select]
    if altre:
        con.executescript(";\n".join(altre) + ";")
    return con, select or [x.strip() for x in re.split(r";\s*(?:\n|$)", test) if re.search(r"(?is)\bselect\b", x)]


def ordine_non_unico(coderunner, databases):
    """Per una domanda SQL: True se l'ordine delle righe del risultato non è fissato dalla soluzione:
    manca l'ORDER BY (e le righe sono più d'una), oppure le chiavi dell'ORDER BY hanno pari merito
    (aggiungendo tutte le colonne come spareggio, in ordine crescente o decrescente, il risultato cambia)."""
    sez, test, cur = {}, [], None
    for blocco in re.split(r"^=== ", coderunner or "", flags=re.M):
        if not blocco.strip():
            continue
        nome, _, corpo = blocco.partition("\n")
        nome = nome.split()[0]
        if nome == "test":
            cur = {"test": corpo, "extra": ""}
            test.append(cur)
        elif nome == "extra" and cur is not None:
            cur["extra"] = corpo
        else:
            sez[nome] = corpo
    answer = sez.get("answer", "")
    if not answer.strip() or not databases:
        return False
    nome_db = re.search(r"^database:\s*(\S+)", sez.get("options", ""), re.M)
    script = databases.get(nome_db.group(1)) if nome_db else next(iter(databases.values()))
    if not script or "[[struttura" in "".join(t["test"] for t in test):
        return False
    for t in test or [{"test": "", "extra": ""}]:
        try:
            con, query = _letture(script, t["extra"], answer, t["test"])
        except sqlite3.Error:
            continue
        try:
            for q in query:
                cur = con.execute(q)
                righe = cur.fetchall()
                if len(set(righe)) < 2:
                    continue
                if _order_by(q) < 0:
                    return True
                ncol = len(cur.description)
                asc = con.execute(_con_spareggio(q, ncol, "ASC")).fetchall()
                desc = con.execute(_con_spareggio(q, ncol, "DESC")).fetchall()
                if asc != desc:
                    return True
        except sqlite3.Error:
            pass
        finally:
            con.close()
    return False


# ---------------------------------------------------------------- confronto con la dashboard

CAMPI_CONFRONTO = ["titolo", "tipologia", "sezione", "pag", "punti", "tag", "traccia", "correzione", "coderunner"]


def norm_campo(campo, v):
    if v is None:
        v = ""
    if campo in ("pag", "punti"):
        try:
            return "%g" % float(v or 0)
        except ValueError:
            return str(v)
    s = str(v).replace("\r", "")
    if campo == "coderunner":
        # gli output attesi non stanno nella dashboard (li calcola la parte 2): non contano
        s = re.sub(r"=== expected\n[\s\S]*?(?=\n=== |\Z)", "", s)
    s = "\n".join(r.rstrip() for r in s.split("\n"))
    s = re.sub(r"```\w*", "```", s)            # la lingua del blocco di codice non torna dal backup
    s = re.sub(r"\n\n(?=(?:- |\d+[.)] ))", "\n", s)   # un elenco subito dopo un paragrafo, con o senza riga vuota
    if campo == "coderunner":                  # l'ordine delle opzioni non conta
        s = re.sub(r"(=== options\n)([\s\S]*?)(?=\n=== |\Z)",
                   lambda m: m.group(1) + "\n".join(sorted(l for l in m.group(2).split("\n") if l.strip())), s)
    if campo == "coderunner":                  # tipi di file della consegna: «zip», «.zip», «.ZIP» sono lo stesso
        s = re.sub(r"(?im)^tipi\s*:\s*(.*)$", lambda m: "tipi: " + " ".join(
            t if t.startswith(".") else "." + t for t in re.split(r"[\s,;]+", m.group(1).strip().lower()) if t), s)
    if campo == "coderunner" and not re.search(r"^=== (test|extra|descrizione)\b", s, re.M):
        # senza prove (esercizi HTML e CSS) le sezioni sono indipendenti: answer, preload e options in qualunque ordine
        parti = re.split(r"(?m)^(?==== )", s.strip())
        s = "\n".join(sorted(p.strip("\n") for p in parti if p.strip()))
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def carica_export(export, qid):
    p = pathlib.Path(export) / "quiz" / (qid + ".json")
    d = json.load(open(p, encoding="utf-8"))
    quiz = d.get("data", d)
    righe = []
    for f in sorted((pathlib.Path(export) / "quiz" / qid / "domande").glob("*.json")):
        x = json.load(open(f, encoding="utf-8"))
        r = dict(x.get("data", x))
        r["_id"] = x.get("id") or f.stem
        r["_version"] = x.get("version")
        righe.append(r)
    righe.sort(key=lambda r: float(r.get("ordine") or 0))
    return quiz, righe


def diff_testo(a, b, etichetta_a, etichetta_b):
    righe = list(difflib.unified_diff(a.split("\n"), b.split("\n"), etichetta_a, etichetta_b, lineterm="", n=1))
    return "\n".join(righe[2:]) if righe else ""


def confronta(bk, cartella_quiz, qz, export, qid, uscita):
    quiz_d, righe_d = carica_export(export, qid)
    _, quiz_b, righe_b, rapporto, imp, _ = importa(bk, cartella_quiz, qz, qid)
    per_pos_d = {r.get("pos"): r for r in righe_d}
    dbs_d = {d.get("nome"): d.get("sql") for d in (quiz_d.get("database") or []) if isinstance(d, dict)}
    per_pos_b = {r["pos"]: r for r in righe_b}
    # per le domande con più versioni: conversione della prima versione, per separare le modifiche fatte
    # in Moodle dalle differenze dovute alla conversione
    prime = {}
    for s in slot_del_quiz(bk, qz):
        for d in s["domande"]:
            if len(d["versioni"]) > 1:
                p = nome_parti(tx(d["usata"][1], "name"))
                if p:
                    campi, _, _ = Importatore(bk).riga(d["versioni"][0][1], {"pagina": "istruzioni"})
                    prime[p[1]] = (campi, len(d["versioni"]), d["usata"][0])
    out = ["# Confronto tra la dashboard («%s») e il backup Moodle «%s»" % (qid, tx(qz, "name")), ""]
    agg = {}
    modificate_moodle, diverse, uguali = [], [], []
    for pos, rb in per_pos_b.items():
        rd = per_pos_d.get(pos)
        if rd is None:
            out += ["## %s %s: solo nel backup" % (pos, rb["titolo"]), "", "Nella dashboard non c'è una riga con questa posizione.", ""]
            continue
        cambi = {}
        for c in CAMPI_CONFRONTO:
            if c == "tag" and not rb.get("tag"):
                continue
            if norm_campo(c, rd.get(c)) != norm_campo(c, rb.get(c)):
                cambi[c] = (rd.get(c), rb.get(c))
        if pos in prime and not any(c in cambi for c in ("traccia", "correzione", "coderunner")):
            uguali.append(pos)    # modificata in Moodle ma già riportata nella dashboard
            continue
        if pos in prime:
            campi_v1, nv, vu = prime[pos]
            mod = {}
            for c in ("traccia", "correzione", "coderunner", "tipologia"):
                if norm_campo(c, campi_v1.get(c)) != norm_campo(c, rb.get(c)):
                    mod[c] = (campi_v1.get(c), rb.get(c))
            if mod:
                modificate_moodle.append(pos)
                out += ["## %s %s: modificata in Moodle (v1 → v%d)" % (pos, rb["titolo"], vu), ""]
                for c, (a, b) in mod.items():
                    out += ["%s, dalla versione generata (v1) a quella attuale in Moodle:" % nome_campo(c), "",
                            "```diff", diff_testo(norm_campo(c, a), norm_campo(c, b), "v1", "v%d" % vu) or "(solo spazi)", "```", ""]
                deriva = [c for c in ("traccia", "correzione", "coderunner") if norm_campo(c, campi_v1.get(c)) != norm_campo(c, rd.get(c))]
                if deriva:
                    out += ["Attenzione: anche nella dashboard la riga è cambiata dopo la generazione (%s): l'aggiornamento "
                            "sostituirebbe quelle modifiche." % ", ".join(nome_campo(c).lower() for c in deriva), ""]
                if CONTROLLA_ORDINE and rb.get("coderunner") and dbs_d and ordine_non_unico(rb["coderunner"], dbs_d):
                    out += ["Controllo: con la soluzione attuale l'ordine delle righe del risultato **non è unico** (manca "
                            "l'ORDER BY o ci sono pari merito): CodeRunner confronta le righe nell'ordine, quindi una "
                            "query giusta ordinata diversamente non passa. Se è voluto, va scritto nella correzione.", ""]
                agg[rd["_id"]] = {"campi": {c: rb.get(c) for c in mod if c != "tipologia"}}
            else:
                out += ["## %s %s: %d versioni in Moodle, nessuna modifica di contenuto" % (pos, rb["titolo"], nv), "",
                        "Le versioni successive cambiano solo la formattazione dell'HTML (l'editor di Moodle).", ""]
            continue
        if cambi:
            diverse.append(pos)
            out += ["## %s %s: diversa dalla dashboard" % (pos, rb["titolo"]), ""]
            for c, (a, b) in cambi.items():
                if c in ("traccia", "correzione", "coderunner"):
                    out += [nome_campo(c) + ":", "", "```diff",
                            diff_testo(norm_campo(c, a), norm_campo(c, b), "dashboard", "Moodle") or "(solo spazi)", "```", ""]
                else:
                    out.append("- %s: dashboard «%s», Moodle «%s»" % (nome_campo(c), a, b))
            out.append("")
        else:
            uguali.append(pos)
    solo_d = [r for r in righe_d if r.get("pos") not in per_pos_b]
    testa = ["Posizioni confrontate: %d. Uguali: %d. Modificate in Moodle dopo la generazione: %s. Diverse dalla dashboard "
             "per altri motivi: %s. Righe della dashboard non presenti nel backup: %d%s." % (
                 len(per_pos_b), len(uguali), ", ".join(modificate_moodle) or "nessuna", ", ".join(diverse) or "nessuna",
                 len(solo_d), (" (%s)" % ", ".join(r.get("pos") or r["_id"] for r in solo_d[:12]) + (" …" if len(solo_d) > 12 else "")) if solo_d else ""),
             ""]
    out[2:2] = testa
    os.makedirs(os.path.join(uscita, "aggiornamenti"), exist_ok=True)
    for rid, a in agg.items():
        json.dump(a, open(os.path.join(uscita, "aggiornamenti", rid + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(uscita, "confronto.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    return modificate_moodle, diverse, uguali, solo_d


def nome_campo(c):
    return {"traccia": "Traccia", "correzione": "Correzione", "coderunner": "Soluzione e test", "tipologia": "Tipologia",
            "titolo": "Titolo", "sezione": "Sezione", "pag": "Pagina", "punti": "Punti", "tag": "Tag"}.get(c, c)


# ---------------------------------------------------------------- main

CONTROLLA_ORDINE = False


def main():
    global CONTROLLA_ORDINE
    CONTROLLA_ORDINE = "--ordine" in sys.argv
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) != 2:
        raise SystemExit(__doc__)
    mbz, uscita = a
    o = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    os.makedirs(uscita, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        bk = Backup(estrai(mbz, tmp))
        quiz = bk.quiz()
        if o.get("quiz"):
            quiz = [q for q in quiz if o["quiz"].lower() in tx(q[1], "name").lower()]
        if not quiz:
            raise SystemExit("Nel backup non c'è nessun quiz%s" % (" con «%s» nel nome" % o["quiz"] if o.get("quiz") else ""))
        if len(quiz) > 1:
            raise SystemExit("Il backup ha più quiz: scegline uno con --quiz=TESTO\n- " +
                             "\n- ".join(tx(q[1], "name") for q in quiz))
        cartella_quiz, qz = quiz[0]
        if o.get("confronta"):
            if not o.get("id"):
                raise SystemExit("Con --confronta serve --id=ID del quiz della dashboard")
            mod, div, ug, solo = confronta(bk, cartella_quiz, qz, o["confronta"], o["id"], uscita)
            print("CONFRONTO con %s: %d uguali, modificate in Moodle: %s; diverse: %s -> %s" % (
                o["id"], len(ug), ", ".join(mod) or "nessuna", ", ".join(div) or "nessuna", os.path.join(uscita, "confronto.md")))
            return
        qid, q, righe, rapporto, imp, mancano_db = importa(bk, cartella_quiz, qz, o.get("id"))
        base = pathlib.Path(uscita) / "quiz"
        (base / qid / "domande").mkdir(parents=True, exist_ok=True)
        json.dump(q, open(base / (qid + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for i, r in enumerate(righe, 1):
            json.dump(r, open(base / qid / "domande" / ("r%02d.json" % i), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        visti, tot = set(), 0.0
        for r in righe:
            t = (r.get("tag") or "").lower()
            if t and t in visti:
                continue
            visti.add(t)
            tot += float(r["punti"] or 0)
        rap = ["# Importazione di «%s»" % tx(qz, "name"), "",
               "Quiz `%s`: %d righe, %d sezioni, %g punti, impostazioni da %s, tempo %s." % (
                   qid, len(righe), len(q["titoliSezioni"]), tot, q["presetMbz"],
                   ("%s minuti" % q["tempo"]) if q["tempo"] else "illimitato"), ""]
        if imp.db:
            rap.append("Database ricostruiti dai file allegati: " + ", ".join(
                "%s (%d tabelle, %d righe)" % (v["nome"], len(tabelle_db(v["percorso"])[0]), tabelle_db(v["percorso"])[1])
                for v in imp.db.values()) + ".")
        if mancano_db:
            rap.append("Database allegati senza la versione piena (struttura o vuoto): %s." % ", ".join(mancano_db))
        if not bk.include_file:
            rap.append("**Il backup è senza file**: database e immagini non importati. Rifallo con «Includi file».")
        dbs = {v["nome"]: v["sql"] for v in imp.db.values()}
        ordine = [r["pos"] for r in righe if CONTROLLA_ORDINE and r.get("coderunner") and "database:" in r["coderunner"]
                  and ordine_non_unico(r["coderunner"], dbs)]
        rap += ["", "## Righe da rivedere", ""] + (rapporto or ["Nessuna."])
        if ordine:
            rap += ["", "## Domande SQL con un ordine non unico", "",
                    "Con queste soluzioni l'ordine delle righe del risultato non è fissato (manca l'ORDER BY o ci sono "
                    "pari merito): CodeRunner confronta le righe nell'ordine. Domande: %s." % ", ".join(ordine)]
        open(pathlib.Path(uscita) / "rapporto.md", "w", encoding="utf-8").write("\n".join(rap) + "\n")
        print("OK: quiz %s, %d righe (%d da rivedere), %d database -> %s" % (
            qid, len(righe), sum(1 for r in righe if r["stato"] == "da-rivedere"), len(imp.db), uscita))


if __name__ == "__main__":
    main()
