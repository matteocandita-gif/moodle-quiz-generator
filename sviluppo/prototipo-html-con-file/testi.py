"""Testi HTML: descrizione del prototipo e consegne delle due domande di prova."""
import html as _html
import re

from domande import Q1_SOLUZIONE

MONO = '<span style="font-family: monospace;">%s</span>'
TH = 'border: 1px solid #999999; padding: 4px 8px; background-color: #eeeeee; text-align: left;'
TD = 'border: 1px solid #999999; padding: 4px 8px; background-color: #ffffff;'
PRE = ('background-color: #333333; color: #eceff1; padding: 12px; border-radius: 4px; '
       'overflow-x: auto; margin: 8px 0; line-height: 1.5;')


def m(s):
    return MONO % _html.escape(s)


def pre(codice):
    return '<pre style="%s">%s</pre>' % (PRE, _html.escape(codice.strip("\n")))


def tabella(intestazione, righe):
    out = ['<table style="border-collapse: collapse; margin: 8px 0;">', "<thead>", "<tr>"]
    out += ['<th style="%s">%s</th>' % (TH, h) for h in intestazione]
    out += ["</tr>", "</thead>", "<tbody>"]
    for r in righe:
        out.append("<tr>" + "".join('<td style="%s">%s</td>' % (TD, c) for c in r) + "</tr>")
    out += ["</tbody>", "</table>"]
    return "\n".join(out)


def browser(contenuto):
    """Riquadro «Visualizzazione nel browser», come il blocco ```html risultato di da_dashboard.py."""
    contenuto = re.sub(r"<a\b[^>]*>", '<a style="color: #0000ee; text-decoration: underline;">', contenuto)
    pallino = ('<span style="display: inline-block; width: 9px; height: 9px; border-radius: 50%%; '
               'background-color: %s; margin-right: 4px; vertical-align: middle;"></span>')
    return ('<div style="border: 1px solid #999999; border-radius: 6px; margin: 8px 0 16px; '
            'max-width: 100%; overflow: hidden;">\n'
            '<div style="background-color: #e3e3e3; border-bottom: 1px solid #999999; padding: 4px 10px; '
            'font-size: 0.8em; color: #555555;">' + pallino % "#e06c5f" + pallino % "#e5b84f"
            + pallino % "#6cbf6a" + '<span style="margin-left: 8px; vertical-align: middle;">'
            'Visualizzazione nel browser</span></div>\n'
            '<div style="background-color: #ffffff; padding: 8px 14px; overflow-x: auto;">\n'
            + contenuto.strip("\n") + "\n</div>\n</div>")


# ---------------------------------------------------------------- descrizione del prototipo

CODICE = '<span style="font-family: monospace;">%s</span>'

FUNZIONI_HTML = [
    ("struttura_base()", "La pagina ha " + CODICE % "html" + ", " + CODICE % "head" + " con un "
     + CODICE % "title" + " non vuoto, " + CODICE % "body" + "; il head viene prima del body e nessun "
     "elemento della pagina sta fuori dal body."),
    ("tag_chiusi()", "Ogni tag aperto è chiuso, nell'ordine giusto. Indica la riga."),
    ('presente("hr")', "C'è almeno un elemento del tipo indicato."),
    ('almeno(3, "li", dentro="ul")', "Ci sono almeno n elementi; con dentro= contano solo quelli "
     "contenuti nel tag indicato."),
    ('esattamente(1, "h1")', "Ci sono esattamente n elementi (anche con dentro=)."),
    ('attributo("input", "type", "email")', "Almeno un elemento ha l'attributo; se si indica il valore, "
     "con quel valore (maiuscole non contano)."),
    ('tutti_con_attributo("img", "alt")', "Tutti gli elementi del tipo hanno l'attributo non vuoto; se nella "
     "pagina non ce n'è nessuno, il controllo non passa."),
    ('testo("h1", "Libreria Pagina 42")', "Almeno un elemento contiene il testo (maiuscole e spazi "
     "non contano)."),
    ("struttura_come_soluzione()", "La sequenza dei tag è la stessa della soluzione scritta nella risposta "
     "della domanda (nella dashboard la sezione === answer); "
     "il testo non conta, div, span, br, hr sono ignorati, i valori di action, method, id, for, "
     "placeholder, alt sono liberi. È il confronto del prototipo html_test_semantica, ridotto al "
     "primo punto diverso."),
]

FUNZIONI_CARTELLA = [
    ("cartella_ben_formata()", "Tutti i file stanno nella cartella del sito; i .css nella cartella "
     + CODICE % "css" + ", le immagini in " + CODICE % "img" + ", i .js in " + CODICE % "js"
     + " (anche in sottocartelle); nessun file estraneo (.txt, .docx…). Thumbs.db e desktop.ini si "
     "ignorano. Domanda per domanda si può chiedere un'altra struttura: "
     + CODICE % 'cartella_ben_formata(img="immagini", css="risorse/css")' + "; con "
     + CODICE % 'pagine="pagine"' + " le pagine diverse dalla principale devono stare nella cartella "
     + CODICE % "pagine" + "; per non controllare un tipo di file: " + CODICE % "js=None" + "."),
    ("nomi_file_corretti()", "Nomi di file e cartelle del sito solo con lettere minuscole senza accento, "
     "numeri, - e _: niente spazi."),
    ('file_presente("img/logo.png")', "Nella cartella del sito c'è il file."),
    ('immagine("img/logo.png")', "Un " + CODICE % "img" + " della pagina mostra quel file. Se il "
     "percorso è sbagliato, il messaggio dice perché."),
    ('link_a("pagine/contatti.html")', "Un link della pagina porta a quel file."),
    ("ancore_valide(2)", "Almeno n link a un punto della pagina (" + CODICE % 'href="#id"' + "), ognuno verso un "
     "id che esiste, e nessun id ripetuto. Segnala anche " + CODICE % 'href="id"' + " senza cancelletto."),
    ("link_esterno(nuova_scheda=True)", "C'è un link a un altro sito con l'indirizzo completo (" + CODICE % "https://"
     + "); con nuova_scheda=True anche " + CODICE % 'target="_blank"' + ". Segnala gli indirizzi che "
     "cominciano con www senza https://."),
    ('uno_tra("p", "ul", "ol")', "C'è almeno un elemento di uno dei tipi indicati (per esempio un paragrafo "
     "oppure una lista)."),
    ('link_validi("index.html", "pagine/contatti.html")', "Ogni href e src relativo delle pagine "
     "indicate (link, immagini, CSS, script) porta a un file consegnato; senza argomenti la pagina "
     "principale. Segnala maiuscole sbagliate, \\ al posto di /, percorsi del PC, percorsi che "
     "iniziano con /."),
    ('usa_pagina("pagine/contatti.html")', "Da scrivere su una riga prima della funzione di controllo: "
     "il controllo si fa su un'altra pagina del sito. Ogni test riparte dalla pagina principale."),
]

FUNZIONI_CSS = [
    ('css_collegato("css/stile.css")', "La pagina collega quel foglio di stile con "
     + CODICE % '&lt;link rel="stylesheet"&gt;' + " dentro il head."),
    ("css_senza_errori()", "Nei fogli collegati non ci sono errori di scrittura: graffe mancanti o in "
     "più, dichiarazioni senza i due punti, ; mancante tra due dichiarazioni, commenti non chiusi."),
    ('css_regola("h1", "color")', "C'è una regola per il selettore; se indicate, con la proprietà e con il "
     "valore (" + CODICE % 'css_regola("h1", "color", "red")' + "). Il selettore si scrive come nel CSS "
     "(" + CODICE % '"nav a"' + ", " + CODICE % '".evidenza"' + "); conta anche dentro un gruppo "
     "(" + CODICE % "h1, h2" + ") o un @media. Una dichiarazione scritta male non conta, come nel "
     "browser. Il valore si confronta come testo: " + CODICE % "red" + " e " + CODICE % "#ff0000"
     + " sono diversi, quindi conviene controllare il valore solo quando la consegna lo impone."),
    ('classe("evidenza")', "La classe è usata da un elemento della pagina ed è definita nel CSS."),
    ("classi_coerenti()", "Ogni classe usata nelle pagine indicate (senza argomenti la principale) è "
     "definita nel CSS e viceversa: trova i nomi scritti in modo diverso."),
    ("nessuno_stile_interno()", "Niente " + CODICE % "&lt;style&gt;" + " nella pagina e niente attributi "
     "style: tutto lo stile sta nel file CSS."),
]

FUNZIONI_JS = [
    ('js_collegato("js/script.js")', "La pagina collega quello script con " + CODICE % '&lt;script src="…"&gt;'
     + ", vuoto."),
    ("js_caricato_dopo_la_pagina()", "Gli script collegati partono dopo il caricamento della pagina: in "
     "fondo al body, oppure nel head con " + CODICE % "defer" + ". Da usare se lo insegni così."),
    ("js_senza_errori()", "Errori di sintassi negli script della pagina (file collegati e script interni), "
     "con la riga e il messaggio in italiano. Usa " + CODICE % "node --check" + " su Jobe; se node non "
     "parte, un controllo più semplice di parentesi, graffe e virgolette."),
    ('js_funzione("mostraOrari")', "C'è una funzione con quel nome: " + CODICE % "function nome(…)"
     + ", " + CODICE % "const nome = function" + " o a freccia. Segnala lo stesso nome con le maiuscole "
     "diverse."),
    ('js_contiene("addEventListener")', "Il codice contiene il testo, senza contare i commenti. Con "
     + CODICE % 'messaggio="…"' + " si sceglie la frase che lo studente vede se manca."),
    ("id_coerenti()", "Ogni id cercato con " + CODICE % "getElementById" + " o " + CODICE % "querySelector"
     + " con # esiste nella pagina: l'errore che lo studente vede solo come «non succede niente»."),
    ("nessuno_script_interno()", "Niente codice dentro " + CODICE % "&lt;script&gt;" + " nella pagina e niente "
     "attributi " + CODICE % "onclick" + ", " + CODICE % "onload" + "…: tutto sta nel file .js."),
    ("diagnosi_node()", "Solo per il docente, in una domanda di prova: dice se node funziona su Jobe."),
]

FUNZIONI_STILE = [
    ("stile_interno()", "C'è un " + CODICE % "&lt;style&gt;" + " con almeno una regola, dentro il head."),
    ("stile_interno_senza_errori()", "Nelle regole scritte nel " + CODICE % "&lt;style&gt;" + " della pagina "
     "non ci sono errori di scrittura (gli stessi di " + CODICE % "css_senza_errori()" + "), con la riga della pagina."),
    ('stile_interno_regola("h1", "color")', "Come " + CODICE % "css_regola" + ", ma sulle regole scritte nel "
     + CODICE % "&lt;style&gt;" + " della pagina."),
    ("in_linea_senza_errori()", "Gli attributi style della pagina sono scritti bene: " + CODICE % "proprietà: valore"
     + " separate da ;, senza graffe."),
    ('in_linea("p", "color")', "Un elemento del tipo indicato ha l'attributo style; se indicate, con la "
     "proprietà e con il valore (" + CODICE % 'in_linea("p", "color", "green")' + ")."),
]

FUNZIONI = FUNZIONI_HTML + FUNZIONI_CARTELLA + FUNZIONI_CSS + FUNZIONI_STILE + FUNZIONI_JS

DESCRIZIONE_PROTOTIPO = "\n".join([
    "<p>Prototipo <strong>html_con_file</strong>: controlla la pagina HTML consegnata dallo studente "
    "come <strong>file allegato</strong> (un .html, oppure la cartella del sito compressa in .zip). "
    "Al posto della casella di risposta lo studente vede solo un promemoria e il riquadro per caricare i file. "
    "Ogni test è un requisito: lo studente vede che cosa manca, test per test.</p>",
    "<p>Con il plugin «Moodle: quiz generator» queste domande si scrivono nella dashboard «Bozze dei quiz» come "
    "tipologia «Consegna con controllo automatico» e le genera il plugin. Le indicazioni qui sotto servono per "
    "crearle o modificarle a mano in Moodle.</p>",
    "<p><strong>Come creare una domanda</strong></p>",
    "<ol>",
    "<li>In <em>Allegati</em> scegli il <strong>numero</strong> di file (di solito 1), se sono obbligatori, "
    "il <strong>nome accettato</strong> e la <strong>dimensione massima</strong>. Questi campi non si "
    "ereditano dal prototipo. Il nome conviene fissarlo per ogni consegna, con un'espressione regolare "
    "(ad esempio " + m(r"index\.html") + " oppure " + m(r"libreria\.zip") + ", con il nome della cartella "
    "del sito), e ripeterlo nella <em>Descrizione</em> dei nomi, che lo studente vede accanto al "
    "riquadro di caricamento (accetta HTML: in grassetto, ad esempio "
    + m("<p><strong>Il file deve chiamarsi libreria.zip, tutto minuscolo e senza spazi.</strong></p>")
    + "), e nel testo della domanda. CodeRunner rifiuta comunque i nomi con "
    "caratteri diversi da lettere, numeri, - _ . (spazi, parentesi, lettere accentate): "
    + m("libreria (1).zip") + " non passa.</li>",
    "<li>In <em>Parametri del template</em> scrivi il <strong>nome della pagina</strong> da controllare: "
    + m('{"pagina": "index.html"}') + ". Senza, si controlla l'unico file .html consegnato. "
    "Con lo zip, la cartella del sito è quella in cui si trova la pagina principale.</li>",
    "<li>Per ogni requisito crea un <strong>test</strong>: nel campo <em>Test</em> una funzione di controllo, "
    "in <em>Output atteso</em> " + m("OK") + ", in <em>Extra</em> la frase che lo studente vede nella "
    "colonna «Controllo».</li>",
    "<li>Imposta <strong>Tutto o niente</strong> a No, così ogni requisito vale la sua parte.</li>",
    "<li>Nella <em>Risposta</em> metti la soluzione (codice HTML) oppure allega i file in "
    "<em>Allegati della risposta</em>, così la domanda si controlla al salvataggio.</li>",
    "</ol>",
    "<p><strong>Casella di risposta.</strong> Il prototipo usa l'interfaccia <em>Html</em> con il solo "
    "promemoria del campo <em>Prototype extra</em>: la risposta resta vuota e serve almeno un allegato. "
    "Se in una domanda vuoi anche la casella per incollare il codice, in <em>Personalizza</em> scegli "
    "l'interfaccia <em>Ace</em> e metti gli allegati come facoltativi: se lo studente non allega niente, "
    "si controlla il codice della casella. Il campo <em>Risposta</em> resta testo semplice "
    "(enable_in_editor è false): ci si incolla la soluzione, che usa anche "
    + m("struttura_come_soluzione()") + ".</p>",
    "<p><strong>Funzioni di controllo: la pagina HTML</strong></p>",
    tabella(["Test", "Che cosa controlla"], [(m(f), d) for f, d in FUNZIONI_HTML]),
    "<p><strong>Funzioni di controllo: la cartella del sito e i collegamenti</strong></p>",
    tabella(["Test", "Che cosa controlla"], [(m(f), d) for f, d in FUNZIONI_CARTELLA]),
    "<p><strong>Funzioni di controllo: il CSS</strong></p>",
    tabella(["Test", "Che cosa controlla"], [(m(f), d) for f, d in FUNZIONI_CSS]),
    "<p>I controlli CSS leggono i fogli collegati dalla pagina che si sta controllando. Non vedono "
    "com'è la pagina nel browser: il risultato della cascata, le regole che si sovrascrivono, "
    "i colori che si vedono davvero.</p>",
    "<p><strong>Funzioni di controllo: il CSS nella pagina</strong> (" + m("<style>") + " e attributo style)</p>",
    tabella(["Test", "Che cosa controlla"], [(m(f), d) for f, d in FUNZIONI_STILE]),
    "<p><strong>Funzioni di controllo: il JavaScript</strong></p>",
    tabella(["Test", "Che cosa controlla"], [(m(f), d) for f, d in FUNZIONI_JS]),
    "<p>I controlli JavaScript leggono il codice, non lo eseguono: non dicono se lo script fa quello che "
    "deve. Se " + m("diagnosi_node()") + " dice che node non parte (per esempio per il limite di memoria), "
    "aumenta il limite di memoria del prototipo.</p>",
    "<p><strong>Che cosa vede lo studente.</strong> Sopra il riquadro di caricamento, il promemoria del campo "
    "<em>Prototype extra</em>: «OK» vuol dire che il controllo ha trovato quello che cercava, non che il lavoro "
    "è corretto. Poi, per ogni test, la frase di Extra (colonna «Controllo») e l'esito (colonna «Trovato?»): "
    + m("OK") + ", oppure il problema trovato (ad esempio «Riga 7: hai scritto src=\"img/Logo.png\", "
    "che porta a img/Logo.png, ma il file si chiama img/logo.png»). Se manca il file o il nome è "
    "sbagliato, tutti i test lo dicono.</p>",
    "<p><strong>Codifica.</strong> Il file si legge in UTF-8 oppure nella codifica di Windows "
    "(Notepad++ in ANSI): le lettere accentate non danno errori.</p>",
])


PROMEMORIA = ('<p style="margin: 0 0 6px; color: #555555;">Carica il file nel riquadro qui sotto, poi premi '
              '<strong>Controlla</strong>.</p>\n'
              '<p style="margin: 0; color: #555555;"><strong>Attenzione:</strong> «OK» vuol dire che il controllo '
              'ha trovato quello che cercava, non che il lavoro è corretto. Il controllo non vede com\'è la pagina '
              'nel browser, se i testi hanno senso, se hai scelto i tag giusti per il significato. '
              '<strong>Apri sempre la pagina nel browser</strong> e confrontala con la consegna.</p>')


# ---------------------------------------------------------------- domanda 1

_body_q1 = Q1_SOLUZIONE.split("<body>")[1].split("</body>")[0]

TESTO_Q1 = "\n".join([
    "<p>Crea con Notepad++ la pagina principale della <strong>Libreria Pagina 42</strong>, salvala "
    "con il nome " + m("index.html") + " e <strong>caricala</strong> qui sotto.</p>",
    "<p>La pagina deve avere:</p>",
    "<ul>",
    "<li>il <strong>titolo della scheda</strong> del browser;</li>",
    "<li>il <strong>titolo principale</strong> «Libreria Pagina 42»;</li>",
    "<li>almeno due <strong>sezioni</strong>, ognuna con il suo titolo;</li>",
    "<li>almeno due <strong>paragrafi</strong> di testo;</li>",
    "<li>un <strong>elenco puntato</strong> con almeno tre servizi della libreria;</li>",
    "<li>una <strong>linea orizzontale</strong> tra le sezioni.</li>",
    "</ul>",
    "<p>Un esempio di risultato (i testi puoi sceglierli tu):</p>",
    browser(_body_q1),
    "<p>Premi <strong>Controlla</strong>: la tabella ti dice quali requisiti mancano. Puoi correggere "
    "il file, ricaricarlo e controllare di nuovo.</p>",
])

# ---------------------------------------------------------------- domanda 2

LOGO_FINTO = ('<div style="display: inline-block; width: 120px; height: 40px; background-color: #dddddd; '
              'color: #555555; text-align: center; line-height: 40px; font-size: 0.8em;">logo.png</div>')

def consegna_zip(cartella):
    return ("<p>Quando hai finito, <strong>comprimi la cartella</strong> " + m(cartella)
            + " (clic destro sulla cartella, «Comprimi in file ZIP», oppure «Invia a» e «Cartella compressa») "
            "e carica qui sotto il file, che deve chiamarsi " + m(cartella + ".zip") + ": è il nome che Windows "
            "gli dà da solo se la cartella si chiama " + m(cartella) + ". Premi <strong>Controlla</strong>: "
            "la tabella ti dice che cosa non va. Puoi correggere, comprimere di nuovo e ricaricare: prima "
            "cancella il vecchio .zip, altrimenti Windows crea " + m(cartella + " (1).zip") + ", che non viene "
            "accettato.</p>")


TESTO_Q2 = "\n".join([
    "<p>Crea il sito della <strong>Libreria Pagina 42</strong> in una cartella " + m("libreria")
    + ", con questa struttura:</p>",
    pre("libreria\n├── index.html\n├── img\n│   └── logo.png\n└── pagine\n    └── contatti.html"),
    "<p>Come " + m("logo.png") + " va bene un'immagine qualsiasi, rinominata.</p>",
    "<p>Il sito deve avere:</p>",
    "<ul>",
    "<li>in " + m("index.html") + " il <strong>logo</strong>, con il suo testo alternativo;</li>",
    "<li>in " + m("index.html") + " un <strong>link</strong> alla pagina dei contatti;</li>",
    "<li>in " + m("contatti.html") + " un link per <strong>tornare</strong> alla pagina principale;</li>",
    "<li><strong>percorsi</strong> che funzionano anche quando il sito viene spostato su un server.</li>",
    "</ul>",
    "<p>La pagina principale potrebbe essere così:</p>",
    browser(LOGO_FINTO + "\n<h1>Libreria Pagina 42</h1>\n<p>Siamo una piccola libreria indipendente "
            "nel centro di Bologna.</p>\n<p><a href=\"pagine/contatti.html\">Contatti</a></p>"),
    consegna_zip("libreria"),
])

# ---------------------------------------------------------------- domanda 3

TESTO_Q3 = "\n".join([
    "<p>Dai uno stile al sito della <strong>Libreria Pagina 42</strong> con un foglio di stile esterno. "
    "Prepara la cartella " + m("libreria") + " con questa struttura:</p>",
    pre("libreria\n├── index.html\n├── css\n│   └── stile.css\n└── img\n    └── logo.png"),
    "<p>Il sito deve avere:</p>",
    "<ul>",
    "<li>il foglio di stile " + m("stile.css") + " nella cartella " + m("css") + ", <strong>collegato</strong> "
    "alla pagina;</li>",
    "<li>un <strong>tipo di carattere</strong> per tutta la pagina;</li>",
    "<li>un <strong>colore</strong> per il titolo principale;</li>",
    "<li>un paragrafo <strong>in evidenza</strong>, in grassetto e colorato, con la classe " + m("evidenza")
    + ";</li>",
    "<li><strong>tutto lo stile</strong> nel file CSS, niente stile scritto dentro la pagina;</li>",
    "<li>nomi di file e cartelle <strong>minuscoli</strong>, senza spazi né accenti.</li>",
    "</ul>",
    "<p>La pagina potrebbe essere così (colori e carattere puoi sceglierli tu):</p>",
    browser('<div style="font-family: Verdana, sans-serif; background-color: #fdf6e3; padding: 4px 8px;">\n'
            + LOGO_FINTO + '\n<h1 style="color: #8b0000;">Libreria Pagina 42</h1>\n'
            '<p>Siamo una piccola libreria indipendente nel centro di Bologna.</p>\n'
            '<p style="font-weight: bold; color: #d35400;">Questo mese: sconto del 10% sui gialli.</p>\n</div>'),
    consegna_zip("libreria"),
])

# ---------------------------------------------------------------- domanda 4

# nel riquadro del risultato il pulsante è disegnato con uno span: un <button> vero dentro la pagina del quiz,
# che è un form, lo invierebbe
PULSANTE_FINTO = ('<span style="display: inline-block; border: 1px solid #767676; border-radius: 3px; '
                  'background-color: #efefef; padding: 1px 8px; font-size: 0.9em;">Mostra gli orari</span>')

TESTO_Q4 = "\n".join([
    "<p>Aggiungi al sito della <strong>Libreria Pagina 42</strong> un pulsante che mostra gli orari. "
    "Prepara la cartella " + m("libreria") + " con questa struttura:</p>",
    pre("libreria\n├── index.html\n├── css\n│   └── stile.css\n└── js\n    └── script.js"),
    "<p>Il sito deve avere:</p>",
    "<ul>",
    "<li>lo script " + m("script.js") + " nella cartella " + m("js") + ", <strong>collegato</strong> in fondo "
    "alla pagina;</li>",
    "<li>un <strong>pulsante</strong> «Mostra gli orari» e, sotto, un paragrafo vuoto;</li>",
    "<li>una <strong>funzione</strong> " + m("mostraOrari") + " che scrive gli orari nel paragrafo;</li>",
    "<li>il <strong>clic</strong> sul pulsante collegato alla funzione con " + m("addEventListener") + ";</li>",
    "<li><strong>tutto il JavaScript</strong> nel file " + m("script.js") + ", niente codice dentro la pagina.</li>",
    "</ul>",
    "<p>Dopo il clic sul pulsante, la pagina potrebbe essere così:</p>",
    browser('<h1>Libreria Pagina 42</h1>\n<p>' + PULSANTE_FINTO + '</p>\n'
            '<p>Dal martedì al sabato, 9-13 e 15.30-19.30</p>'),
    consegna_zip("libreria"),
])


# ---------------------------------------------------------------- prototipo css_con_test

DESCRIZIONE_CSS_CON_TEST = "\n".join([
    "<p>Prototipo <strong>css_con_test</strong>: controlla il codice CSS o HTML che lo studente scrive nella "
    "<strong>casella di risposta</strong>, con le stesse funzioni di controllo del prototipo "
    "<strong>html_con_file</strong> (stesso template). Serve agli esercizi brevi: una regola CSS, un tag con "
    "l'attributo style, una piccola pagina con il " + m("&lt;style&gt;") + ".</p>",
    "<p>Con il plugin «Moodle: quiz generator» queste domande si scrivono nella dashboard «Bozze dei quiz» come "
    "tipologia «Esercizio con controllo» e le genera il plugin.</p>",
    "<p><strong>Che cosa scrive lo studente</strong>: lo decide il parametro del template "
    + m('{"pagina": "stile.css"}') + " (predefinito): la casella contiene un foglio di stile, e "
    + m("css_senza_errori()") + " e " + m('css_regola(...)') + " lo controllano. Con "
    + m('{"pagina": "index.html"}') + " la casella contiene codice HTML (anche solo un pezzo di pagina) e si "
    "usano le funzioni della pagina, dello stile in linea e del " + m("&lt;style&gt;") + "; per l'HTML conviene "
    "scegliere nella domanda il linguaggio dell'editor html.</p>",
    "<p><strong>Controllo visibile o nascosto</strong>: con il pulsante Verifica e i risultati dei test visibili "
    "lo studente corregge da solo; con Verifica nascosto (" + m("Nascondi Verifica") + ") e "
    + m("Mostra feedback: Forza nascondi") + " il punteggio si calcola alla consegna senza mostrare i controlli, "
    "come in una verifica.</p>",
    "<p>Ogni test è un requisito: nel campo <em>Test</em> una funzione di controllo, in <em>Output atteso</em> "
    + m("OK") + ", in <em>Extra</em> la frase che lo studente vede nella colonna «Controllo». Le funzioni sono "
    "quelle descritte nel prototipo html_con_file; quelle sui file della cartella del sito qui non servono.</p>",
])
