# Prototipo html_con_file: controlla la pagina HTML consegnata dallo studente.
# La pagina arriva come file allegato (.html, oppure .zip con la cartella del sito)
# o, se non ci sono allegati, dalla casella di risposta.
# Ogni test chiama UNA funzione di controllo (elenco nella descrizione del prototipo):
# la funzione stampa OK se il requisito c'è, altrimenti un messaggio per lo studente.
# Output atteso di ogni test: OK.

import os
import posixpath
import re
import shutil
import subprocess
import zipfile
from html.parser import HTMLParser
from urllib.parse import unquote

SEPARATORE = "#<ab@17943918#@>#"
ALLEGATI = [n for n in "{{ ATTACHMENTS }}".split(",") if n.strip()]
RISPOSTA = """{{ STUDENT_ANSWER | e('py') }}"""
SOLUZIONE = """{{ QUESTION.answer | e('py') }}"""
PAGINA = "{{ pagina | default('') }}".strip()   # parametro del template: il file da controllare

CARTELLA = "consegna"
FILE_DI_SISTEMA = {"thumbs.db", "desktop.ini", ".ds_store"}   # li crea il sistema operativo: si ignorano
VUOTI = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
         "param", "source", "track", "wbr"}


# ------------------------------------------------------------ preparazione della consegna

def leggi_testo(percorso):
    """Legge un file di testo: UTF-8 oppure la codifica di Windows (Notepad++ in ANSI)."""
    with open(percorso, "rb") as f:
        dati = f.read()
    for codifica in ("utf-8-sig", "cp1252"):
        try:
            return dati.decode(codifica)
        except UnicodeDecodeError:
            pass
    return dati.decode("utf-8", errors="replace")


def estrai_zip(nome):
    """Estrae lo zip nella cartella della consegna, saltando i percorsi pericolosi."""
    with zipfile.ZipFile(nome) as z:
        for voce in z.infolist():
            percorso = voce.filename.replace("\\", "/")
            if voce.is_dir() or percorso.startswith("/") or ".." in percorso.split("/"):
                continue
            if percorso.startswith("__MACOSX/") or posixpath.basename(percorso).lower() in FILE_DI_SISTEMA:
                continue
            destinazione = os.path.join(CARTELLA, *percorso.split("/"))
            os.makedirs(os.path.dirname(destinazione), exist_ok=True)
            with z.open(voce) as sorgente, open(destinazione, "wb") as uscita:
                shutil.copyfileobj(sorgente, uscita)


def prepara_consegna():
    """Mette tutti i file consegnati in CARTELLA e restituisce (elenco dei file, avviso)."""
    os.makedirs(CARTELLA, exist_ok=True)
    avviso = ""
    for nome in ALLEGATI:
        if nome.lower().endswith(".zip"):
            try:
                estrai_zip(nome)
            except zipfile.BadZipFile:
                avviso = "Il file %s non è un archivio .zip valido." % nome
        else:
            shutil.copy(nome, os.path.join(CARTELLA, nome))
    if not ALLEGATI and RISPOSTA.strip():
        with open(os.path.join(CARTELLA, PAGINA or "index.html"), "w", encoding="utf-8") as f:
            f.write(RISPOSTA)
    file_consegnati = []
    for radice, _, nomi in os.walk(CARTELLA):
        for nome in nomi:
            completo = os.path.join(radice, nome)
            file_consegnati.append(os.path.relpath(completo, CARTELLA).replace(os.sep, "/"))
    return sorted(file_consegnati), avviso


def scegli_pagina(file_consegnati):
    """Trova il file da controllare: PAGINA se indicato, altrimenti l'unico .html in cima."""
    if PAGINA.lower().endswith(".css") and not ALLEGATI:
        # prototipo css_con_test: la casella contiene un foglio di stile, non una pagina
        if PAGINA in file_consegnati:
            return PAGINA, ""
        return None, "La risposta è vuota: scrivi il codice CSS nella casella."
    html = [f for f in file_consegnati if f.lower().endswith((".html", ".htm"))]
    if PAGINA:
        trovati = [f for f in html if posixpath.basename(f) == PAGINA]
        if not trovati:
            simili = [f for f in html if posixpath.basename(f).lower() == PAGINA.lower()]
            if simili:
                return None, ("Il file si deve chiamare %s, tu l'hai chiamato %s: "
                              "attenzione a maiuscole e minuscole." % (PAGINA, posixpath.basename(simili[0])))
            return None, "Non trovo il file %s nella tua consegna." % PAGINA
        # se ce ne sono più di uno (per esempio in più cartelle) si prende quello più in alto
        return min(trovati, key=lambda f: f.count("/")), ""
    if not html:
        return None, "Non trovo nessun file .html nella tua consegna."
    in_cima = min(f.count("/") for f in html)
    candidati = [f for f in html if f.count("/") == in_cima]
    if len(candidati) > 1:
        return None, ("Hai consegnato più pagine (%s) e non so quale controllare."
                      % ", ".join(candidati))
    return candidati[0], ""


# ------------------------------------------------------------ lettura dell'HTML

class Elemento:
    def __init__(self, tag, attributi, genitore, riga):
        self.tag = tag
        self.attributi = attributi
        self.genitore = genitore
        self.riga = riga
        self.figli = []
        self.pezzi_di_testo = []

    def testo(self):
        """Tutto il testo dell'elemento e dei suoi figli, con gli spazi normalizzati."""
        parti = list(self.pezzi_di_testo)
        for figlio in self.figli:
            parti.append(figlio.testo())
        return " ".join(" ".join(parti).split())

    def antenati(self):
        e = self.genitore
        while e is not None:
            yield e
            e = e.genitore


class Lettore(HTMLParser):
    """Costruisce l'albero degli elementi e annota i tag non chiusi o chiusi senza apertura."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.radice = Elemento("#documento", {}, None, 0)
        self.aperti = [self.radice]
        self.elementi = []
        self.problemi_chiusura = []

    def handle_starttag(self, tag, attrs):
        e = Elemento(tag, {n: (v if v is not None else "") for n, v in attrs},
                     self.aperti[-1], self.getpos()[0])
        self.aperti[-1].figli.append(e)
        self.elementi.append(e)
        if tag not in VUOTI:
            self.aperti.append(e)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VUOTI:
            self.aperti.pop()

    def handle_endtag(self, tag):
        if tag in VUOTI:
            return
        aperti = [e.tag for e in self.aperti]
        if tag not in aperti:
            self.problemi_chiusura.append(
                "Riga %d: chiudi </%s>, ma non c'è un <%s> aperto." % (self.getpos()[0], tag, tag))
            return
        while self.aperti[-1].tag != tag:
            e = self.aperti.pop()
            self.problemi_chiusura.append("Riga %d: il tag <%s> non è chiuso." % (e.riga, e.tag))
        self.aperti.pop()

    def handle_data(self, data):
        self.aperti[-1].pezzi_di_testo.append(data)

    def close(self):
        super().close()
        for e in self.aperti[1:]:
            self.problemi_chiusura.append("Riga %d: il tag <%s> non è chiuso." % (e.riga, e.tag))


def usa_pagina(percorso):
    """Legge la pagina indicata (percorso dalla cartella del sito) e la rende quella da controllare."""
    global PAGINA_SCELTA, LETTORE, ELEMENTI
    completo = nel_sito(percorso)
    if completo not in FILE_CONSEGNATI:
        raise ConsegnaIncompleta("Non trovo la pagina %s nella tua consegna." % percorso)
    PAGINA_SCELTA = completo
    LETTORE = Lettore()
    if completo.lower().endswith(".css"):
        LETTORE.close()          # un foglio di stile nella casella: nessun elemento HTML
        ELEMENTI = LETTORE.elementi
        return
    LETTORE.feed(leggi_testo(os.path.join(CARTELLA, completo)))
    LETTORE.close()
    ELEMENTI = LETTORE.elementi


class ConsegnaIncompleta(Exception):
    pass


def nel_sito(percorso):
    """Da un percorso scritto dal docente (relativo alla cartella del sito) al percorso nella consegna."""
    return posixpath.normpath(posixpath.join(SITO, percorso)) if SITO else posixpath.normpath(percorso)


def dal_sito(percorso):
    """Il percorso come lo vede lo studente, a partire dalla cartella del sito."""
    return posixpath.relpath(percorso, SITO) if SITO else percorso


FILE_CONSEGNATI, ERRORE_CONSEGNA = prepara_consegna()
PAGINA_PRINCIPALE, SITO = None, ""
if not ERRORE_CONSEGNA:
    PAGINA_PRINCIPALE, ERRORE_CONSEGNA = scegli_pagina(FILE_CONSEGNATI)
if PAGINA_PRINCIPALE:
    SITO = posixpath.dirname(PAGINA_PRINCIPALE)   # la cartella del sito è quella della pagina principale
PAGINA_SCELTA, LETTORE, ELEMENTI = None, None, []


# ------------------------------------------------------------ funzioni di supporto

def esito(problemi):
    """Stampa OK se non ci sono problemi, altrimenti un problema per riga."""
    if problemi:
        print("\n".join(problemi))
    else:
        print("OK")


def trova(tag, dentro=None):
    elementi = [e for e in ELEMENTI if e.tag == tag]
    if dentro:
        elementi = [e for e in elementi if any(a.tag == dentro for a in e.antenati())]
    return elementi


def descrivi(tag, dentro):
    return "<%s>" % tag + (" dentro <%s>" % dentro if dentro else "")


def risolvi(indirizzo):
    """Il file a cui porta un percorso relativo scritto nella pagina, rispetto alla cartella della pagina."""
    pulito = unquote(indirizzo.split("#")[0].split("?")[0])
    cartella = posixpath.dirname(PAGINA_SCELTA)
    return posixpath.normpath(posixpath.join(cartella, pulito))


def problema_indirizzo(indirizzo):
    """None se il percorso porta a un file consegnato (o è esterno), altrimenti il messaggio."""
    minuscolo = indirizzo.strip().lower()
    if minuscolo.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:", "data:")):
        return None
    if minuscolo == "":
        return "è vuoto"
    if minuscolo.startswith("file:") or (len(minuscolo) > 1 and minuscolo[1] == ":"):
        return "è un percorso del tuo computer: sul server non esiste. Usa un percorso relativo"
    if "\\" in indirizzo:
        return "contiene \\: nei percorsi del web le cartelle si separano con /"
    if indirizzo.startswith("/"):
        return "inizia con /: usa un percorso relativo alla pagina"
    destinazione = risolvi(indirizzo)
    if destinazione in FILE_CONSEGNATI:
        return None
    simili = [f for f in FILE_CONSEGNATI if f.lower() == destinazione.lower()]
    if simili:
        return ("porta a %s, ma il file si chiama %s: sul server maiuscole e minuscole "
                "contano" % (dal_sito(destinazione), dal_sito(simili[0])))
    return "porta a %s, che non c'è nei file consegnati" % dal_sito(destinazione)


def quasi_giusti(tag, nome, destinazione):
    """Per i messaggi: i tag che puntano a un file con lo stesso nome ma con un percorso sbagliato."""
    nome_file = posixpath.basename(destinazione).lower()
    indizi = []
    for e in trova(tag):
        indirizzo = e.attributi.get(nome, "")
        if posixpath.basename(indirizzo.replace("\\", "/")).lower() == nome_file:
            problema = problema_indirizzo(indirizzo) or "porta a %s" % dal_sito(risolvi(indirizzo))
            indizi.append('Riga %d: hai scritto %s="%s", che %s.' % (e.riga, nome, indirizzo, problema))
    return indizi


# ------------------------------------------------------------ funzioni di controllo (una per test)

def struttura_base():
    """La pagina ha html, head con un title non vuoto, e body, nell'ordine giusto."""
    problemi = []
    for tag in ("html", "head", "title", "body"):
        if not trova(tag):
            problemi.append("Manca il tag <%s>." % tag)
    if trova("title") and not trova("title", dentro="head"):
        problemi.append("Il <title> deve stare dentro <head>.")
    if trova("title") and not trova("title")[0].testo():
        problemi.append("Il <title> è vuoto: scrivi il titolo della pagina.")
    if trova("head") and trova("body") and trova("head")[0].riga > trova("body")[0].riga:
        problemi.append("Il <head> deve venire prima del <body>.")
    for e in ELEMENTI:
        if e.tag not in ("html", "head", "title", "meta", "link", "style", "script", "base", "body") \
                and not any(a.tag == "body" for a in e.antenati()) and trova("body"):
            problemi.append("Riga %d: <%s> sta fuori dal <body>." % (e.riga, e.tag))
    esito(problemi)


def tag_chiusi():
    """Ogni tag aperto è chiuso, e nell'ordine giusto."""
    esito(LETTORE.problemi_chiusura)


def almeno(n, tag, dentro=None):
    trovati = len(trova(tag, dentro))
    if trovati >= n:
        esito([])
    else:
        esito(["Ci sono %d elementi %s, ne servono almeno %d." % (trovati, descrivi(tag, dentro), n)])


def esattamente(n, tag, dentro=None):
    trovati = len(trova(tag, dentro))
    if trovati == n:
        esito([])
    else:
        esito(["Ci sono %d elementi %s, ne servono esattamente %d." % (trovati, descrivi(tag, dentro), n)])


def presente(tag, dentro=None):
    if trova(tag, dentro):
        esito([])
    else:
        esito(["Manca un elemento %s." % descrivi(tag, dentro)])


def attributo(tag, nome, valore=None):
    """Almeno un elemento tag ha l'attributo nome (con il valore indicato, se c'è)."""
    elementi = trova(tag)
    if not elementi:
        esito(["Manca un elemento <%s>." % tag])
    elif valore is None:
        if any(nome in e.attributi for e in elementi):
            esito([])
        else:
            esito(["Nessun <%s> ha l'attributo %s." % (tag, nome)])
    elif any(e.attributi.get(nome, "").strip().lower() == valore.lower() for e in elementi):
        esito([])
    else:
        esito(['Nessun <%s> ha %s="%s".' % (tag, nome, valore)])


def tutti_con_attributo(tag, nome):
    """Ogni elemento tag ha l'attributo nome non vuoto (per esempio alt in tutte le img)."""
    if not trova(tag):
        esito(["Nella pagina non c'è nessun <%s>." % tag])
        return
    mancanti = [e for e in trova(tag) if not e.attributi.get(nome, "").strip()]
    esito(["Riga %d: <%s> senza %s." % (e.riga, tag, nome) for e in mancanti])


def testo(tag, parole):
    """Almeno un elemento tag contiene il testo indicato (maiuscole e spazi non contano)."""
    cercato = " ".join(parole.lower().split())
    if any(cercato in e.testo().lower() for e in trova(tag)):
        esito([])
    else:
        esito(["Nessun <%s> contiene il testo «%s»." % (tag, parole)])


def link_validi(*pagine):
    """Ogni href e src relativo porta a un file che c'è davvero nella consegna.
    Senza argomenti controlla la pagina principale; altrimenti le pagine indicate."""
    problemi = []
    for pagina in (pagine or [dal_sito(PAGINA_PRINCIPALE)]):
        usa_pagina(pagina)
        for e in ELEMENTI:
            for nome in ("href", "src"):
                if nome in e.attributi and e.tag in ("a", "img", "link", "script", "source", "iframe"):
                    messaggio = problema_indirizzo(e.attributi[nome])
                    if messaggio:
                        problemi.append('%s, riga %d: %s="%s" %s.'
                                        % (pagina, e.riga, nome, e.attributi[nome], messaggio))
    esito(problemi)


def link_a(destinazione):
    """C'è un <a> il cui href porta al file indicato (percorso dalla cartella del sito)."""
    for e in trova("a"):
        indirizzo = e.attributi.get("href", "")
        if problema_indirizzo(indirizzo) is None and risolvi(indirizzo) == nel_sito(destinazione):
            esito([])
            return
    esito(["Manca un link che porta alla pagina %s." % destinazione] + quasi_giusti("a", "href", destinazione))


def immagine(destinazione):
    """C'è un <img> il cui src porta al file indicato (percorso dalla cartella del sito)."""
    for e in trova("img"):
        indirizzo = e.attributi.get("src", "")
        if problema_indirizzo(indirizzo) is None and risolvi(indirizzo) == nel_sito(destinazione):
            esito([])
            return
    esito(["Manca l'immagine %s." % destinazione] + quasi_giusti("img", "src", destinazione))


def file_presente(percorso):
    """Nella cartella del sito c'è il file indicato (per esempio img/logo.png)."""
    if nel_sito(percorso) in FILE_CONSEGNATI:
        esito([])
        return
    simili = [f for f in FILE_CONSEGNATI if f.lower() == nel_sito(percorso).lower()]
    if simili:
        esito(["Il file %s si deve chiamare %s: maiuscole e minuscole contano." % (dal_sito(simili[0]), percorso)])
    else:
        esito(["Nella consegna manca il file %s." % percorso])


# ------------------------------------------------------------ link: ancore, link esterni, contenuto

def ancore_valide(almeno=1):
    """Ci sono almeno n link a un punto della pagina (href="#id"), ognuno porta a un id che esiste,
    e gli id della pagina sono tutti diversi."""
    problemi = []
    id_visti = {}
    for e in ELEMENTI:
        if "id" in e.attributi:
            identificatore = e.attributi["id"]
            if identificatore in id_visti:
                problemi.append('Riga %d: id="%s" c\'è già alla riga %d: ogni id deve essere unico, '
                                'altrimenti il link porta sempre al primo.' % (e.riga, identificatore, id_visti[identificatore]))
            else:
                id_visti[identificatore] = e.riga
    ancore = [e for e in trova("a") if e.attributi.get("href", "").startswith("#") and len(e.attributi["href"]) > 1]
    for e in ancore:
        destinazione = e.attributi["href"][1:]
        if destinazione not in id_visti:
            simili = [x for x in id_visti if x.lower() == destinazione.lower()]
            problemi.append('Riga %d: href="#%s" cerca l\'id %s, che nella pagina non c\'è%s.'
                            % (e.riga, destinazione, destinazione,
                               " (c'è %s: maiuscole e minuscole contano)" % simili[0] if simili else ""))
    for e in trova("a"):
        indirizzo = e.attributi.get("href", "")
        if not indirizzo.startswith("#") and indirizzo in id_visti:
            problemi.append('Riga %d: href="%s" è il nome di un id: per un punto della pagina ci vuole il '
                            'cancelletto, href="#%s".' % (e.riga, indirizzo, indirizzo))
    if len(ancore) < almeno:
        problemi.append("Ci sono %d link a un punto della pagina (href=\"#...\"), ne servono almeno %d."
                        % (len(ancore), almeno))
    esito(problemi)


def link_esterno(nuova_scheda=False):
    """C'è un link a un altro sito, con l'indirizzo completo (https://); con nuova_scheda=True deve
    aprirsi in una nuova scheda (target="_blank")."""
    esterni = [e for e in trova("a")
               if e.attributi.get("href", "").strip().lower().startswith(("http://", "https://"))]
    if not esterni:
        quasi = [e for e in trova("a") if e.attributi.get("href", "").strip().lower().startswith("www.")]
        esito(["Manca un link a un altro sito, con l'indirizzo completo che comincia con https://."]
              + ['Riga %d: href="%s" comincia con www: senza https:// il browser cerca un file con quel '
                 'nome nella cartella.' % (e.riga, e.attributi["href"]) for e in quasi])
        return
    if nuova_scheda and not any(e.attributi.get("target", "").strip().lower() == "_blank" for e in esterni):
        esito(['Il link a un altro sito (riga %d) si apre nella stessa scheda: aggiungi target="_blank".'
               % esterni[0].riga])
        return
    esito([])


def uno_tra(*tag):
    """C'è almeno un elemento di uno dei tipi indicati, per esempio uno_tra("p", "ul", "ol")."""
    if any(trova(t) for t in tag):
        esito([])
    else:
        esito(["Manca il contenuto: serve almeno un elemento tra %s." % ", ".join("<%s>" % t for t in tag)])



# ------------------------------------------------------------ cartella del sito e nomi dei file

IMMAGINI = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp")
ALTRI_FILE_DEL_SITO = (".html", ".htm", ".css", ".js", ".pdf", ".woff", ".woff2", ".ttf", ".otf",
                       ".mp3", ".mp4", ".ogg", ".webm")


def file_del_sito():
    """I file dentro la cartella del sito, con il percorso visto dalla cartella del sito."""
    return [dal_sito(f) for f in FILE_CONSEGNATI if not dal_sito(f).startswith("../")]


def cartella_ben_formata(css="css", img="img", js="js", pagine=None):
    """Tutto sta nella cartella del sito, ogni tipo di file nella sua cartella (anche annidata, come
    "risorse/css"), nessun file estraneo. Per non controllare un tipo si passa None (ad esempio js=None).
    Con pagine="pagine", le pagine diverse dalla principale devono stare in quella cartella."""
    problemi = []
    for f in FILE_CONSEGNATI:
        if dal_sito(f).startswith("../"):
            problemi.append("Il file %s sta fuori dalla cartella del sito." % f)
    principale = dal_sito(PAGINA_PRINCIPALE)
    for f in file_del_sito():
        estensione = posixpath.splitext(f)[1].lower()
        attesa = None
        if estensione == ".css":
            attesa = css
        elif estensione == ".js":
            attesa = js
        elif estensione in IMMAGINI:
            attesa = img
        elif estensione in (".html", ".htm") and f != principale:
            attesa = pagine
        elif estensione not in ALTRI_FILE_DEL_SITO:
            problemi.append("Il file %s non fa parte del sito: toglilo dalla cartella." % f)
            continue
        if attesa and not f.startswith(attesa.strip("/") + "/"):
            problemi.append("Il file %s va nella cartella %s." % (f, attesa.strip("/")))
    esito(problemi)


def nomi_file_corretti():
    """Nomi di file e cartelle del sito: solo lettere minuscole, numeri, - _ . (niente spazi né accenti)."""
    problemi = []
    visti = set()
    for f in file_del_sito():
        parti = f.split("/")
        for i, nome in enumerate(parti):
            percorso = "/".join(parti[:i + 1])
            if percorso in visti:
                continue
            visti.add(percorso)
            cosa = "Il file" if i == len(parti) - 1 else "La cartella"
            if " " in nome:
                problemi.append("%s «%s» ha uno spazio nel nome: usa - oppure _." % (cosa, percorso))
            elif nome != nome.lower():
                problemi.append("%s «%s» ha lettere maiuscole: usa solo minuscole." % (cosa, percorso))
            elif not re.fullmatch(r"[a-z0-9_.-]+", nome):
                problemi.append("%s «%s» ha lettere accentate o simboli: usa solo lettere senza accento, "
                                "numeri, - e _." % (cosa, percorso))
    esito(problemi)


# ------------------------------------------------------------ CSS

class FoglioDiStile:
    """Le regole di un file CSS e i problemi di scrittura trovati leggendolo."""

    def __init__(self, nome, testo):
        self.nome = nome
        self.regole = []      # dizionari: selettori, dichiarazioni [(proprietà, valore)], riga
        self.problemi = []
        self.scritte_male = []   # (proprietà, selettore) delle dichiarazioni che il browser ignora
        if testo.count("/*") > testo.count("*/"):
            self.problemi.append("%s: c'è un commento /* non chiuso con */." % nome)
        # i commenti diventano a capo, così i numeri di riga restano giusti
        testo = re.sub(r"/\*.*?(\*/|$)", lambda m: "\n" * m.group().count("\n"), testo, flags=re.S)
        self.testo = testo
        self.leggi_blocco(0, len(testo))

    def riga(self, posizione):
        return self.testo.count("\n", 0, posizione) + 1

    def chiusura(self, aperta, fine):
        """Posizione della } che chiude la { in posizione aperta, oppure None."""
        profondita = 0
        for i in range(aperta, fine):
            if self.testo[i] == "{":
                profondita += 1
            elif self.testo[i] == "}":
                profondita -= 1
                if profondita == 0:
                    return i
        return None

    def leggi_blocco(self, inizio, fine):
        i = inizio
        while i < fine:
            aperta = self.testo.find("{", i, fine)
            chiusa_sola = self.testo.find("}", i, fine)
            if chiusa_sola != -1 and (aperta == -1 or chiusa_sola < aperta):
                self.problemi.append("%s, riga %d: c'è una } in più." % (self.nome, self.riga(chiusa_sola)))
                i = chiusa_sola + 1
                continue
            if aperta == -1:
                resto = self.testo[i:fine].strip()
                # @import e @charset finiscono con ; e non hanno graffe
                resto = re.sub(r"@(import|charset)[^;]*;", "", resto).strip()
                if resto:
                    self.problemi.append("%s, riga %d: «%s» sta fuori da una regola (mancano le graffe?)."
                                         % (self.nome, self.riga(i + self.testo[i:fine].find(resto[:1])),
                                            resto[:40]))
                return
            intestazione = self.testo[i:aperta].strip()
            intestazione = re.sub(r"^(@(import|charset)[^;]*;\s*)+", "", intestazione).strip()
            chiusa = self.chiusura(aperta, fine)
            riga = self.riga(aperta)
            if chiusa is None:
                # se dopo c'è un'altra regola, l'errore lo segnala leggi_regola in modo più preciso
                if "{" not in self.testo[aperta + 1:fine]:
                    self.problemi.append("%s, riga %d: la regola «%s» non è chiusa con }."
                                         % (self.nome, riga, intestazione[:40]))
                chiusa = fine
            if intestazione.startswith(("@media", "@supports")):
                self.leggi_blocco(aperta + 1, chiusa)
            elif intestazione.startswith("@"):
                pass          # @font-face, @keyframes...: non si controllano
            elif not intestazione:
                self.problemi.append("%s, riga %d: una regola senza selettore prima della {." % (self.nome, riga))
            else:
                self.leggi_regola(intestazione, self.testo[aperta + 1:chiusa], riga)
            i = chiusa + 1

    def leggi_regola(self, intestazione, corpo, riga):
        if "{" in corpo:
            self.problemi.append("%s, riga %d: nella regola «%s» manca la } prima della regola successiva."
                                 % (self.nome, riga, intestazione[:40]))
            # si tiene solo la parte prima della riga in cui comincia la regola successiva
            corpo = corpo[:max(corpo.rfind("\n", 0, corpo.index("{")), 0)]
        dichiarazioni = []
        for pezzo in corpo.split(";"):
            if not pezzo.strip():
                continue
            if ":" not in pezzo:
                self.problemi.append("%s, regola «%s» (riga %d): «%s» non è nella forma proprietà: valore."
                                     % (self.nome, intestazione, riga, " ".join(pezzo.split())[:40]))
                continue
            proprieta, valore = pezzo.split(":", 1)
            proprieta = proprieta.strip().lower()
            valore = " ".join(valore.split())
            valida = True     # il browser ignora le dichiarazioni scritte male
            if "url(" not in valore and re.search(r"\s[a-z-]+\s*:", " " + valore):
                self.problemi.append("%s, regola «%s» (riga %d): manca il ; dopo «%s: %s»."
                                     % (self.nome, intestazione, riga, proprieta,
                                        re.split(r"\s[a-z-]+\s*:", " " + valore)[0].strip()))
                valida = False
            if not valore:
                self.problemi.append("%s, regola «%s» (riga %d): la proprietà %s non ha un valore."
                                     % (self.nome, intestazione, riga, proprieta))
                valida = False
            if valida:
                dichiarazioni.append((proprieta, valore))
            else:
                self.scritte_male.append((proprieta, intestazione))
        selettori = [normalizza_selettore(x) for x in intestazione.split(",")]
        self.regole.append({"selettori": selettori, "dichiarazioni": dichiarazioni, "riga": riga,
                            "testo_selettore": intestazione})


def normalizza_selettore(selettore):
    selettore = " ".join(selettore.split())
    return re.sub(r"\s*([>+~])\s*", r" \1 ", selettore).lower()


def fogli_della_pagina():
    """I fogli di stile collegati dalla pagina con <link rel="stylesheet"> che esistono nella consegna."""
    if PAGINA_SCELTA and PAGINA_SCELTA.lower().endswith(".css"):
        # prototipo css_con_test: il foglio è la risposta scritta nella casella
        return [FoglioDiStile(dal_sito(PAGINA_SCELTA), leggi_testo(os.path.join(CARTELLA, PAGINA_SCELTA)))]
    fogli = []
    for e in trova("link"):
        if "stylesheet" in e.attributi.get("rel", "").lower():
            indirizzo = e.attributi.get("href", "")
            if problema_indirizzo(indirizzo) is None and not indirizzo.lower().startswith(("http:", "https:")):
                percorso = risolvi(indirizzo)
                fogli.append(FoglioDiStile(dal_sito(percorso), leggi_testo(os.path.join(CARTELLA, percorso))))
    return fogli


def avviso_errori(fogli):
    """Se il CSS ha errori di scrittura, una regola può sparire: lo si dice allo studente."""
    if any(f.problemi for f in fogli):
        return ["Nel CSS ci sono errori di scrittura, che possono far sparire le regole: "
                "guarda il controllo degli errori del CSS."]
    return []


def senza_fogli():
    """Il messaggio quando non c'è un foglio di stile da leggere, con il motivo più probabile."""
    for e in trova("link"):
        indirizzo = e.attributi.get("href", "")
        if "stylesheet" in e.attributi.get("rel", "").lower():
            return ['Non riesco ad aprire il foglio di stile collegato alla riga %d: href="%s" %s.'
                    % (e.riga, indirizzo, problema_indirizzo(indirizzo) or "non si legge")]
        if indirizzo.lower().endswith(".css"):
            return ['Riga %d: il <link> al foglio di stile non ha rel="stylesheet", quindi il browser '
                    'non lo usa.' % e.riga]
    if trova("style"):
        return ["Lo stile è scritto dentro <style> nella pagina, non in un file CSS collegato."]
    return ['La pagina non collega nessun foglio di stile (manca il <link rel="stylesheet"> nel <head>).']


def css_collegato(percorso):
    """La pagina collega il foglio di stile indicato (percorso dalla cartella del sito)."""
    for e in trova("link"):
        indirizzo = e.attributi.get("href", "")
        if problema_indirizzo(indirizzo) is None and risolvi(indirizzo) == nel_sito(percorso):
            if "stylesheet" not in e.attributi.get("rel", "").lower():
                esito(['Riga %d: il <link> a %s non ha rel="stylesheet".' % (e.riga, percorso)])
            elif not any(a.tag == "head" for a in e.antenati()):
                esito(["Riga %d: il <link> al foglio di stile deve stare dentro <head>." % e.riga])
            else:
                esito([])
            return
    esito(["La pagina non collega il foglio di stile %s." % percorso] + quasi_giusti("link", "href", percorso))


def css_senza_errori():
    """Nei fogli di stile collegati non ci sono errori di scrittura (graffe, due punti, punto e virgola)."""
    fogli = fogli_della_pagina()
    if not fogli:
        esito(senza_fogli())
        return
    esito([p for foglio in fogli for p in foglio.problemi])


def css_regola(selettore, proprieta=None, valore=None):
    """Nei fogli collegati c'è una regola per il selettore; se indicate, con la proprietà e il valore."""
    fogli = fogli_della_pagina()
    if not fogli:
        esito(senza_fogli())
        return
    regola_nei_fogli(fogli, selettore, proprieta, valore)


def regola_nei_fogli(fogli, selettore, proprieta=None, valore=None):
    """Il controllo di css_regola sui fogli indicati (file collegati, oppure lo stile scritto nella pagina)."""
    cercato = normalizza_selettore(selettore)
    regole = [r for f in fogli for r in f.regole if cercato in r["selettori"]]
    if not regole:
        esito(["Nel CSS non c'è una regola per %s." % selettore] + avviso_errori(fogli))
        return
    if proprieta is None:
        esito([])
        return
    valori = [v for r in regole for p, v in r["dichiarazioni"] if p == proprieta.lower()]
    scritta_male = any(p == proprieta.lower() and normalizza_selettore(x) == cercato
                       for f in fogli for p, sel in f.scritte_male for x in sel.split(","))
    if not valori and scritta_male:
        esito(["Nella regola per %s la proprietà %s è scritta male, quindi il browser la ignora: "
               "guarda il controllo degli errori del CSS." % (selettore, proprieta)])
    elif not valori:
        esito(["La regola per %s non ha la proprietà %s." % (selettore, proprieta)] + avviso_errori(fogli))
    elif valore is not None and " ".join(valore.lower().split()) not in [v.lower() for v in valori]:
        esito(['Nella regola per %s, %s vale "%s": qui serve "%s".' % (selettore, proprieta, valori[-1], valore)])
    else:
        esito([])


def classi_nel_css(fogli):
    """Nome della classe -> riga e file della prima regola che la definisce."""
    definite = {}
    for f in fogli:
        for r in f.regole:
            for nome in re.findall(r"\.([A-Za-z_][\w-]*)", r["testo_selettore"]):
                definite.setdefault(nome, "%s, riga %d" % (f.nome, r["riga"]))
    return definite


def classe(nome):
    """La classe è usata da almeno un elemento della pagina ed è definita nel CSS collegato."""
    problemi = []
    if not any(nome in e.attributi.get("class", "").split() for e in ELEMENTI):
        problemi.append('Nessun elemento della pagina ha class="%s".' % nome)
    fogli = fogli_della_pagina()
    if not fogli:
        problemi += senza_fogli()
    elif nome not in classi_nel_css(fogli):
        problemi.append("Nel CSS non c'è una regola per la classe .%s." % nome)
        problemi += avviso_errori(fogli)
    esito(problemi)


def classi_coerenti(*pagine):
    """Ogni classe usata nelle pagine è definita nel CSS, e ogni classe del CSS è usata in una pagina:
    trova i nomi scritti in modo diverso. Senza argomenti controlla la pagina principale."""
    usate = {}
    definite = {}
    for pagina in (pagine or [dal_sito(PAGINA_PRINCIPALE)]):
        usa_pagina(pagina)
        for e in ELEMENTI:
            for nome in e.attributi.get("class", "").split():
                usate.setdefault(nome, "%s, riga %d" % (pagina, e.riga))
        definite.update(classi_nel_css(fogli_della_pagina()))
    problemi = []
    for nome, dove in usate.items():
        if nome not in definite:
            problemi.append('%s: la classe "%s" non è definita nel CSS. Controlla come l\'hai scritta, '
                            'anche maiuscole e minuscole.' % (dove, nome))
    for nome, dove in definite.items():
        if nome not in usate:
            problemi.append("%s: la classe .%s è nel CSS ma nessun elemento la usa." % (dove, nome))
    esito(problemi)


def nessuno_stile_interno():
    """Tutto lo stile sta nel file CSS: niente <style> nella pagina e niente attributi style."""
    problemi = ["Riga %d: c'è un <style> nella pagina: lo stile va nel file CSS." % e.riga for e in trova("style")]
    problemi += ['Riga %d: <%s> ha l\'attributo style: lo stile va nel file CSS.' % (e.riga, e.tag)
                 for e in ELEMENTI if "style" in e.attributi]
    esito(problemi)


# ------------------------------------------------------------ CSS nella pagina: <style> e attributo style

def fogli_interni():
    """Lo stile scritto nei <style> della pagina, letto come un foglio di stile (righe come nella pagina)."""
    fogli = []
    for e in trova("style"):
        testo_style = "".join(e.pezzi_di_testo)
        fogli.append(FoglioDiStile("<style>", "\n" * (e.riga - 1) + testo_style))
    return fogli


def senza_style():
    """Il messaggio quando la pagina non ha un <style>, con il motivo più probabile."""
    if any("style" in e.attributi for e in ELEMENTI):
        return ["Nella pagina non c'è un <style>: lo stile è scritto con l'attributo style dentro i tag."]
    if any("stylesheet" in e.attributi.get("rel", "").lower() for e in trova("link")):
        return ["Nella pagina non c'è un <style>: lo stile è in un file CSS collegato con <link>."]
    return ["Nella pagina non c'è un <style> con le regole CSS (va dentro <head>)."]


def stile_interno():
    """C'è un <style> con almeno una regola, dentro <head>."""
    elementi_style = trova("style")
    if not elementi_style:
        esito(senza_style())
        return
    problemi = ["Riga %d: il <style> deve stare dentro <head>." % e.riga
                for e in elementi_style if not any(a.tag == "head" for a in e.antenati())]
    if not problemi and not any(f.regole for f in fogli_interni()):
        problemi = ["Riga %d: il <style> è vuoto: scrivi dentro le regole CSS." % elementi_style[0].riga]
    esito(problemi)


def stile_interno_senza_errori():
    """Nello stile scritto nel <style> della pagina non ci sono errori di scrittura."""
    fogli = fogli_interni()
    if not fogli:
        esito(senza_style())
        return
    esito([p for foglio in fogli for p in foglio.problemi])


def stile_interno_regola(selettore, proprieta=None, valore=None):
    """Nel <style> della pagina c'è una regola per il selettore; se indicate, con la proprietà e il valore."""
    fogli = fogli_interni()
    if not fogli:
        esito(senza_style())
        return
    regola_nei_fogli(fogli, selettore, proprieta, valore)


def leggi_style(e):
    """Le dichiarazioni dell'attributo style di un elemento: (dichiarazioni valide, problemi, proprietà scritte male)."""
    testo_style = e.attributi.get("style", "")
    dichiarazioni, problemi, scritte_male = [], [], []
    dove = "Riga %d, attributo style di <%s>" % (e.riga, e.tag)
    if "{" in testo_style or "}" in testo_style:
        problemi.append("%s: nell'attributo style non ci vanno le graffe, solo proprietà: valore;" % dove)
        testo_style = testo_style.replace("{", " ").replace("}", " ")
    if not testo_style.strip():
        problemi.append("%s: è vuoto." % dove)
    for pezzo in testo_style.split(";"):
        if not pezzo.strip():
            continue
        if ":" not in pezzo:
            problemi.append("%s: «%s» non è nella forma proprietà: valore." % (dove, " ".join(pezzo.split())[:40]))
            continue
        proprieta, valore = pezzo.split(":", 1)
        proprieta = proprieta.strip().lower()
        valore = " ".join(valore.split())
        valida = True
        if "url(" not in valore and re.search(r"\s[a-z-]+\s*:", " " + valore):
            problemi.append("%s: manca il ; dopo «%s: %s»." % (dove, proprieta,
                                                              re.split(r"\s[a-z-]+\s*:", " " + valore)[0].strip()))
            valida = False
        if not valore:
            problemi.append("%s: la proprietà %s non ha un valore." % (dove, proprieta))
            valida = False
        if valida:
            dichiarazioni.append((proprieta, valore))
        else:
            scritte_male.append(proprieta)
    return dichiarazioni, problemi, scritte_male


def in_linea_senza_errori():
    """Gli attributi style della pagina sono scritti bene: proprietà: valore, separate da ;."""
    con_style = [e for e in ELEMENTI if "style" in e.attributi]
    if not con_style:
        esito(["Nella pagina nessun tag ha l'attributo style."])
        return
    esito([p for e in con_style for p in leggi_style(e)[1]])


def in_linea(tag, proprieta=None, valore=None):
    """Un elemento del tipo indicato ha l'attributo style; se indicate, con la proprietà e il valore."""
    elementi_tag = trova(tag)
    if not elementi_tag:
        esito(["Nella pagina non c'è nessun <%s>." % tag])
        return
    con_style = [e for e in elementi_tag if "style" in e.attributi]
    if not con_style:
        esito(["Nessun <%s> ha l'attributo style." % tag])
        return
    if proprieta is None:
        esito([])
        return
    letti = [(e, leggi_style(e)) for e in con_style]
    valori = [(e, v) for e, (dich, _, _) in letti for p, v in dich if p == proprieta.lower()]
    scritta_male = [e for e, (_, _, male) in letti if proprieta.lower() in male]
    if not valori and scritta_male:
        esito(["Riga %d: nell'attributo style di <%s> la proprietà %s è scritta male, quindi il browser "
               "la ignora: guarda il controllo degli errori." % (scritta_male[0].riga, tag, proprieta)])
    elif not valori:
        esito(["L'attributo style di <%s> non ha la proprietà %s." % (tag, proprieta)])
    elif valore is not None and " ".join(valore.lower().split()) not in [v.lower() for _, v in valori]:
        e, v = valori[-1]
        esito(['Riga %d: nell\'attributo style di <%s>, %s vale "%s": qui serve "%s".'
               % (e.riga, tag, proprieta, v, valore)])
    else:
        esito([])



# ------------------------------------------------------------ JavaScript

def togli_commenti_js(codice):
    """Il codice senza commenti (// e /* */), con gli a capo al loro posto; le stringhe restano."""
    risultato = []
    i, n = 0, len(codice)
    while i < n:
        c = codice[i]
        if c in "\"'`":
            fine = i + 1
            while fine < n and codice[fine] != c and not (c != "`" and codice[fine] == "\n"):
                fine += 2 if codice[fine] == "\\" else 1
            risultato.append(codice[i:fine + 1])
            i = fine + 1
        elif codice.startswith("//", i):
            fine = codice.find("\n", i)
            i = n if fine == -1 else fine
        elif codice.startswith("/*", i):
            fine = codice.find("*/", i + 2)
            fine = n if fine == -1 else fine + 2
            risultato.append("\n" * codice.count("\n", i, fine))
            i = fine
        else:
            risultato.append(c)
            i += 1
    return "".join(risultato)


def script_della_pagina():
    """Gli script della pagina: [(nome per i messaggi, codice, percorso del file o None, riga di partenza)]."""
    script = []
    for e in trova("script"):
        indirizzo = e.attributi.get("src")
        if indirizzo is not None:
            if problema_indirizzo(indirizzo) is None and not indirizzo.lower().startswith(("http:", "https:")):
                percorso = risolvi(indirizzo)
                script.append((dal_sito(percorso), leggi_testo(os.path.join(CARTELLA, percorso)),
                               os.path.join(CARTELLA, percorso), 1))
        elif e.testo().strip():
            codice = "".join(e.pezzi_di_testo)
            # il codice comincia sulla riga del tag <script>: i numeri di riga diventano quelli della pagina
            script.append((dal_sito(PAGINA_SCELTA), codice, None, e.riga))
    return script


def senza_script():
    for e in trova("script"):
        if "src" in e.attributi:
            return ['Non riesco ad aprire lo script collegato alla riga %d: src="%s" %s.'
                    % (e.riga, e.attributi["src"], problema_indirizzo(e.attributi["src"]) or "non si legge")]
    return ["La pagina non collega nessuno script (manca <script src=\"...\">)."]


def js_collegato(percorso):
    """La pagina collega lo script indicato (percorso dalla cartella del sito)."""
    for e in trova("script"):
        indirizzo = e.attributi.get("src", "")
        if problema_indirizzo(indirizzo) is None and risolvi(indirizzo) == nel_sito(percorso):
            if e.testo().strip():
                esito(["Riga %d: un <script> con src deve essere vuoto: il codice scritto dentro viene "
                       "ignorato." % e.riga])
            else:
                esito([])
            return
    esito(["La pagina non collega lo script %s." % percorso] + quasi_giusti("script", "src", percorso))


def js_caricato_dopo_la_pagina():
    """Gli script collegati partono dopo che la pagina è caricata: in fondo al body, oppure con defer."""
    problemi = []
    for e in trova("script"):
        if "src" not in e.attributi or "defer" in e.attributi or e.attributi.get("type") == "module":
            continue
        if any(a.tag == "head" for a in e.antenati()):
            problemi.append("Riga %d: lo script è nel <head> senza defer, quindi parte prima che la pagina sia "
                            "caricata e non trova gli elementi. Mettilo in fondo al <body> oppure aggiungi "
                            "defer." % e.riga)
    esito(problemi)


TRADUZIONI_NODE = [
    (r"missing \) after argument list", "manca una ) dopo gli argomenti della funzione"),
    (r"missing \) after condition", "manca una ) dopo la condizione"),
    (r"Unexpected end of input", "il codice finisce prima del previsto: probabilmente manca una } o una )"),
    (r"Invalid or unexpected token", "c'è un carattere non valido, oppure una stringa senza le virgolette di chiusura"),
    (r"Unexpected identifier '?([^']*)'?", r"la parola \1 non va bene in questo punto: forse manca un operatore, "
                                          r"una virgola o un punto e virgola"),
    (r"Unexpected string", "una stringa non va bene in questo punto: forse manca un + o una virgola"),
    (r"Unexpected number", "un numero non va bene in questo punto: forse manca un operatore o una virgola"),
    (r"Unexpected token '?([^']*)'?", r"il simbolo \1 non va bene in questo punto"),
    (r"Identifier '([^']*)' has already been declared", r"la variabile \1 è dichiarata due volte"),
    (r"Unexpected token", "c'è un simbolo che non va bene in questo punto"),
]


def traduci_errore(messaggio):
    for inglese, italiano in TRADUZIONI_NODE:
        if re.fullmatch(inglese, messaggio):
            return re.sub(inglese, italiano, messaggio)
    return messaggio


def trova_node():
    for comando in ("node", "nodejs", "/usr/bin/node", "/usr/local/bin/node", "/usr/bin/nodejs"):
        if shutil.which(comando) or os.path.exists(comando):
            return shutil.which(comando) or comando
    return None


def controlla_con_node(nome, codice, riga_partenza):
    """Errore di sintassi trovato da node --check: messaggio, '' se il codice è giusto, None se node non va."""
    node = trova_node()
    if not node:
        return None
    with open("__controllo__.js", "w", encoding="utf-8") as f:
        f.write(codice)
    try:
        r = subprocess.run([node, "--check", "__controllo__.js"], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode == 0:
        return ""
    errore = re.search(r"^SyntaxError: (.*)$", r.stderr, re.M)
    riga = re.search(r"__controllo__\.js:(\d+)", r.stderr)
    if not errore or not riga:
        return None          # node non è partito (per esempio per il limite di memoria): si usa il ripiego
    numero = int(riga.group(1)) + riga_partenza - 1
    righe = codice.split("\n")
    testo_riga = righe[int(riga.group(1)) - 1].strip() if int(riga.group(1)) <= len(righe) else ""
    return "%s, riga %d: %s.%s (%s)" % (nome, numero, traduci_errore(errore.group(1)),
                                        " Nella riga c'è: %s" % testo_riga if testo_riga else "",
                                        "SyntaxError: " + errore.group(1))


def controlla_parentesi(nome, codice, riga_partenza):
    """Ripiego senza node: parentesi, graffe e quadre che si chiudono, stringhe chiuse sulla stessa riga."""
    coppie = {")": "(", "]": "[", "}": "{"}
    aperte = []
    riga = 1
    i, n = 0, len(codice)
    while i < n:
        c = codice[i]
        if c == "\n":
            riga += 1
        elif c in "\"'`":
            fine = i + 1
            while fine < n and codice[fine] != c and not (c != "`" and codice[fine] == "\n"):
                fine += 2 if codice[fine] == "\\" else 1
            if fine >= n or codice[fine] != c:
                return "%s, riga %d: una stringa non ha le virgolette di chiusura." % (nome, riga + riga_partenza - 1)
            riga += codice.count("\n", i, fine)
            i = fine
        elif codice.startswith("//", i):
            fine = codice.find("\n", i)
            i = n if fine == -1 else fine
            continue
        elif codice.startswith("/*", i):
            fine = codice.find("*/", i + 2)
            fine = n if fine == -1 else fine + 2
            riga += codice.count("\n", i, fine)
            i = fine
            continue
        elif c in "([{":
            aperte.append((c, riga))
        elif c in ")]}":
            if not aperte or aperte[-1][0] != coppie[c]:
                return ("%s, riga %d: la %s non chiude niente, oppure prima manca una chiusura."
                        % (nome, riga + riga_partenza - 1, c))
            aperte.pop()
        i += 1
    if aperte:
        simbolo, dove = aperte[-1]
        return "%s, riga %d: la %s aperta qui non è mai chiusa." % (nome, dove + riga_partenza - 1, simbolo)
    return ""


def js_senza_errori():
    """Gli script della pagina non hanno errori di sintassi (con node --check se c'è, altrimenti un ripiego)."""
    script = script_della_pagina()
    if not script:
        esito(senza_script())
        return
    problemi = []
    for nome, codice, _, riga_partenza in script:
        messaggio = controlla_con_node(nome, codice, riga_partenza)
        if messaggio is None:
            messaggio = controlla_parentesi(nome, codice, riga_partenza)
        elif "Unexpected end of input" in messaggio:
            # node dice solo che il codice finisce prima: le parentesi dicono dove si apre quella non chiusa
            dove = controlla_parentesi(nome, codice, riga_partenza)
            if dove:
                messaggio += " " + dove
        if messaggio:
            problemi.append(messaggio)
    esito(problemi)


def diagnosi_node():
    """Solo per il docente: dice se node funziona su Jobe (in una domanda di prova, output atteso qualsiasi)."""
    node = trova_node()
    if not node:
        print("node non trovato: js_senza_errori() usa il controllo delle parentesi")
        return
    r = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=20)
    print("node %s (%s), codice di uscita %d %s" % (r.stdout.strip(), node, r.returncode, r.stderr.strip()[:200]))


def js_funzione(nome):
    """Nel JavaScript della pagina c'è una funzione con quel nome (function, function anonima o freccia)."""
    script = script_della_pagina()
    if not script:
        esito(senza_script())
        return
    codice = "\n".join(togli_commenti_js(c) for _, c, _, _ in script)
    n = re.escape(nome)
    modelli = [r"\bfunction\s+%s\s*\(" % n,
               r"\b%s\s*=\s*(async\s+)?function\b" % n,
               r"\b%s\s*=\s*(async\s*)?(\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>" % n]
    if any(re.search(m, codice) for m in modelli):
        esito([])
        return
    simili = sorted({m.group(1) for m in re.finditer(r"\bfunction\s+([A-Za-z_$][\w$]*)", codice)
                     if m.group(1).lower() == nome.lower()})
    esito(["Nel JavaScript non c'è una funzione chiamata %s." % nome]
          + ["C'è %s: maiuscole e minuscole contano." % x for x in simili])


def js_contiene(testo, messaggio=None):
    """Il JavaScript della pagina contiene il testo indicato (senza contare i commenti).
    Con messaggio= si sceglie la frase che vede lo studente se manca."""
    script = script_della_pagina()
    if not script:
        esito(senza_script())
        return
    if any(testo in togli_commenti_js(c) for _, c, _, _ in script):
        esito([])
    else:
        esito([messaggio or "Nel JavaScript non c'è «%s»." % testo])


def id_coerenti():
    """Ogni id cercato dal JavaScript (getElementById, querySelector con #) esiste nella pagina."""
    script = script_della_pagina()
    if not script:
        esito(senza_script())
        return
    id_pagina = {e.attributi["id"] for e in ELEMENTI if "id" in e.attributi}
    problemi = []
    for nome, codice, _, riga_partenza in script:
        pulito = togli_commenti_js(codice)
        cercati = [(m.start(), m.group(1), 'getElementById("%s")' % m.group(1))
                   for m in re.finditer(r"getElementById\(\s*[\"'`]([^\"'`]+)[\"'`]\s*\)", pulito)]
        for m in re.finditer(r"querySelector(?:All)?\(\s*[\"'`]([^\"'`]+)[\"'`]\s*\)", pulito):
            for identificatore in re.findall(r"#([A-Za-z_][\w-]*)", m.group(1)):
                cercati.append((m.start(), identificatore, 'querySelector("%s")' % m.group(1)))
        for posizione, identificatore, chiamata in cercati:
            if identificatore in id_pagina:
                continue
            riga = pulito.count("\n", 0, posizione) + riga_partenza
            simili = [x for x in id_pagina if x.lower() == identificatore.lower()]
            problemi.append("%s, riga %d: %s cerca l'id %s, che nella pagina non c'è%s."
                            % (nome, riga, chiamata, identificatore,
                               " (c'è %s: maiuscole e minuscole contano)" % simili[0] if simili else ""))
    esito(problemi)


def nessuno_script_interno():
    """Tutto il JavaScript sta nei file .js: niente codice dentro <script> e niente attributi onclick, onload..."""
    problemi = ["Riga %d: c'è del codice dentro <script> nella pagina: il JavaScript va nel file .js." % e.riga
                for e in trova("script") if "src" not in e.attributi and e.testo().strip()]
    for e in ELEMENTI:
        for nome in e.attributi:
            if nome.startswith("on"):
                problemi.append("Riga %d: <%s> ha l'attributo %s: gli eventi si collegano nel file .js "
                                "(addEventListener)." % (e.riga, e.tag, nome))
    esito(problemi)



# Confronto con la soluzione: riprende il prototipo html_test_semantica del collega.
def struttura_come_soluzione(ignora=("div", "span", "br", "hr"),
                             valore_libero=("action", "method", "id", "for", "placeholder", "alt")):
    """I tag (tranne quelli in ignora) sono gli stessi della soluzione, nello stesso ordine; il testo non conta."""
    def sequenza(lettore):
        risultato = []
        for e in lettore.elementi:
            if e.tag in ignora:
                continue
            attributi = " ".join(
                '%s="%s"' % (n, "*" if n in valore_libero else v) for n, v in sorted(e.attributi.items()))
            risultato.append(("<%s %s>" % (e.tag, attributi)).replace(" >", ">"))
        return risultato
    lettore_soluzione = Lettore()
    lettore_soluzione.feed(SOLUZIONE)
    lettore_soluzione.close()
    attesa, data = sequenza(lettore_soluzione), sequenza(LETTORE)
    for i, (a, d) in enumerate(zip(attesa, data)):
        if a != d:
            esito(["Il tag numero %d della pagina è %s, ma qui ci vuole %s." % (i + 1, d, a)])
            return
    if len(data) < len(attesa):
        esito(["Dopo %s mancano altri tag: il prossimo è %s." % (data[-1] if data else "l'inizio", attesa[len(data)])])
    elif len(data) > len(attesa):
        esito(["Ci sono tag in più: dal tag %s in poi la soluzione non ne ha altri." % data[len(attesa)]])
    else:
        esito([])


def esegui_test(codice):
    if ERRORE_CONSEGNA:
        print(ERRORE_CONSEGNA)
        return
    try:
        usa_pagina(dal_sito(PAGINA_PRINCIPALE))   # ogni test riparte dalla pagina principale
        exec(codice, globals())
    except ConsegnaIncompleta as errore:
        print(errore)
    except Exception as errore:
        print("Errore nel controllo (avvisa l'insegnante): %s" % errore)


# ------------------------------------------------------------ i test della domanda
{% for TEST in TESTCASES %}
esegui_test("""{{ TEST.testcode | e('py') }}""")
{% if not loop.last %}print(SEPARATORE)
{% endif %}
{% endfor %}
