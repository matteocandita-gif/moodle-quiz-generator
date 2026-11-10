"""Le due domande di prova: test (codice, descrizione) e soluzioni."""
import io
import zipfile

# ---------------------------------------------------------------- domanda 1: un solo file
Q1_TEST = [
    ("struttura_base()", "La pagina ha la struttura di base: html, head con il title, body"),
    ("tag_chiusi()", "Ogni tag aperto è chiuso"),
    ('testo("h1", "Libreria Pagina 42")', "Il titolo principale h1 è «Libreria Pagina 42»"),
    ('almeno(2, "h2")', "Ci sono almeno due titoli di sezione h2"),
    ('almeno(2, "p")', "Ci sono almeno due paragrafi"),
    ('almeno(3, "li", dentro="ul")', "C'è un elenco puntato con almeno tre voci"),
    ('presente("hr")', "C'è una linea orizzontale che separa le sezioni"),
]

Q1_SOLUZIONE = """<!DOCTYPE html>
<html>
<head>
<title>Libreria Pagina 42</title>
</head>
<body>
<h1>Libreria Pagina 42</h1>
<p>Siamo una piccola libreria indipendente nel centro di Bologna.</p>
<hr>
<h2>I nostri servizi</h2>
<ul>
<li>Ordini di libri non disponibili</li>
<li>Gruppo di lettura il giovedì sera</li>
<li>Carta regalo</li>
</ul>
<hr>
<h2>Dove siamo</h2>
<p>Via dei Libri 42, Bologna.</p>
</body>
</html>
"""

# ---------------------------------------------------------------- domanda 2: sito in .zip
Q2_TEST = [
    ('file_presente("img/logo.png")', "Nella cartella img c'è il file logo.png"),
    ('file_presente("pagine/contatti.html")', "Nella cartella pagine c'è il file contatti.html"),
    ('immagine("img/logo.png")', "La pagina index.html mostra il logo"),
    ('tutti_con_attributo("img", "alt")', "Ogni immagine di index.html ha il testo alternativo alt"),
    ('link_a("pagine/contatti.html")', "Da index.html c'è un link alla pagina dei contatti"),
    ('usa_pagina("pagine/contatti.html")\nlink_a("index.html")',
     "Da contatti.html c'è un link per tornare a index.html"),
    ('link_validi("index.html", "pagine/contatti.html")',
     "Tutti i link e le immagini delle due pagine portano a file che esistono"),
]

Q2_INDEX = """<!DOCTYPE html>
<html>
<head>
<title>Libreria Pagina 42</title>
</head>
<body>
<img src="img/logo.png" alt="Logo della Libreria Pagina 42">
<h1>Libreria Pagina 42</h1>
<p>Siamo una piccola libreria indipendente nel centro di Bologna.</p>
<p><a href="pagine/contatti.html">Contatti</a></p>
</body>
</html>
"""

Q2_CONTATTI = """<!DOCTYPE html>
<html>
<head>
<title>Contatti - Libreria Pagina 42</title>
</head>
<body>
<img src="../img/logo.png" alt="Logo della Libreria Pagina 42">
<h1>Contatti</h1>
<p>Via dei Libri 42, Bologna.</p>
<p><a href="../index.html">Torna alla pagina principale</a></p>
</body>
</html>
"""

# un PNG minimo valido (1x1)
PNG = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")


def zip_sito(file, cartella="libreria/"):
    """Crea lo zip come lo fa Windows con «Comprimi in cartella ZIP» sulla cartella del sito."""
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, dati in file.items():
            z.writestr(cartella + nome, dati)
    return b.getvalue()


def q2_file_corretti():
    return {"index.html": Q2_INDEX, "pagine/contatti.html": Q2_CONTATTI, "img/logo.png": PNG}

# ---------------------------------------------------------------- domanda 3: sito con CSS in .zip
Q3_TEST = [
    ("cartella_ben_formata()", "La cartella del sito è in ordine: ogni file nella sua cartella, niente file estranei"),
    ("nomi_file_corretti()", "I nomi di file e cartelle sono minuscoli, senza spazi né accenti"),
    ('css_collegato("css/stile.css")', "La pagina collega il foglio di stile css/stile.css"),
    ("css_senza_errori()", "Il foglio di stile è scritto senza errori (graffe, due punti, punto e virgola)"),
    ('css_regola("body", "font-family")', "Il body ha un tipo di carattere"),
    ('css_regola("h1", "color")', "Il titolo principale h1 ha un colore"),
    ('classe("evidenza")', "La classe evidenza è usata nella pagina e definita nel CSS"),
    ("nessuno_stile_interno()", "Tutto lo stile sta nel file CSS, non nella pagina"),
    ("link_validi()", "I collegamenti al CSS e all'immagine portano a file che esistono"),
]

Q3_INDEX = """<!DOCTYPE html>
<html>
<head>
<title>Libreria Pagina 42</title>
<link rel="stylesheet" href="css/stile.css">
</head>
<body>
<img src="img/logo.png" alt="Logo della Libreria Pagina 42">
<h1>Libreria Pagina 42</h1>
<p>Siamo una piccola libreria indipendente nel centro di Bologna.</p>
<p class="evidenza">Questo mese: sconto del 10% sui gialli.</p>
</body>
</html>
"""

Q3_CSS = """/* Stile della Libreria Pagina 42 */
body {
  font-family: Verdana, sans-serif;
  background-color: #fdf6e3;
}

h1 {
  color: #8b0000;
}

.evidenza {
  font-weight: bold;
  color: #d35400;
}
"""


def q3_file_corretti():
    return {"index.html": Q3_INDEX, "css/stile.css": Q3_CSS, "img/logo.png": PNG}

# ---------------------------------------------------------------- domanda 4: sito con JavaScript in .zip
Q4_TEST = [
    ("cartella_ben_formata()", "La cartella del sito è in ordine: ogni file nella sua cartella, niente file estranei"),
    ('js_collegato("js/script.js")', "La pagina collega lo script js/script.js"),
    ("js_caricato_dopo_la_pagina()", "Lo script parte dopo che la pagina è caricata"),
    ("js_senza_errori()", "Lo script non ha errori di sintassi"),
    ('js_funzione("mostraOrari")', "C'è la funzione mostraOrari"),
    ('js_contiene("addEventListener", "Il pulsante non è collegato alla funzione con addEventListener.")',
     "Il clic sul pulsante è collegato con addEventListener"),
    ("id_coerenti()", "Gli id cercati dallo script esistono nella pagina"),
    ("nessuno_script_interno()", "Tutto il JavaScript sta nel file .js, non nella pagina"),
]

Q4_INDEX = """<!DOCTYPE html>
<html>
<head>
<title>Libreria Pagina 42</title>
<link rel="stylesheet" href="css/stile.css">
</head>
<body>
<h1>Libreria Pagina 42</h1>
<button id="pulsante-orari">Mostra gli orari</button>
<p id="orari"></p>
<script src="js/script.js"></script>
</body>
</html>
"""

Q4_JS = """// Mostra gli orari della libreria quando si preme il pulsante
function mostraOrari() {
  let paragrafo = document.getElementById("orari");
  paragrafo.textContent = "Dal martedì al sabato, 9-13 e 15.30-19.30";
}

document.getElementById("pulsante-orari").addEventListener("click", mostraOrari);
"""


def q4_file_corretti():
    return {"index.html": Q4_INDEX, "css/stile.css": Q3_CSS, "js/script.js": Q4_JS}
