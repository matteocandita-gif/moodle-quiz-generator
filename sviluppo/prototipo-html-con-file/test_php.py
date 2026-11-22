"""Prove del prototipo php_sito: pagine PHP eseguite davvero, con GET e POST, invio del modulo,
confronto con la soluzione, errori di PHP e cartella del sito protetta (open_basedir)."""
import json

from prova import esegui
fallite = 0

FORM = """<!DOCTYPE html>
<html><head><title>Iscrizione</title></head>
<body>
<form action="pagine/risultato.php" method="post">
  <label for="nome">Nome</label> <input type="text" id="nome" name="nome" required>
  <label for="eta">Età</label> <input type="number" id="eta" name="eta">
  <input type="hidden" name="corso" value="teatro">
  <input type="checkbox" id="news" name="news" value="si"> <label for="news">Notizie</label>
  <select name="classe"><option value="">--</option><option value="4A">4A</option></select>
  <button>Invia</button>
</form>
<a href="pagine/elenco.php?genere=giallo">Gialli</a>
</body></html>
"""
RISULTATO = """<?php
$nome = htmlspecialchars($_POST["nome"]);
$eta = $_POST["eta"];
if ($eta >= 18) {
    echo "<p>Ciao $nome, sei maggiorenne.</p>";
} else {
    echo "<p>Ciao $nome, sei minorenne.</p>";
}
echo "<p>Corso: $_POST[corso]</p>";
if (isset($_POST["news"])) {
    echo "<p>Riceverai le notizie.</p>";
}
"""
ELENCO = """<?php
$libri = ["giallo" => ["Il nome della rosa", "Assassinio sull'Orient Express"], "fantasy" => ["Lo Hobbit"]];
$genere = $_GET["genere"];
echo "<h1>Libri: $genere</h1>\\n<ul>\\n";
foreach ($libri[$genere] as $titolo) {
    echo "<li>$titolo</li>\\n";
}
echo "</ul>";
"""


def sito(**files):
    f = {"index.html": FORM, "pagine/risultato.php": RISULTATO, "pagine/elenco.php": ELENCO}
    f.update(files)
    return json.dumps({"htmlve": 1, "cartelle": ["pagine"], "files": {k: v for k, v in f.items() if v is not None},
                       "immagini": {}})


SOLUZIONE = sito()


def una(codice, risposta, attesa, titolo, contiene=None, pagina="index.html", lasco=False):
    global fallite
    u = esegui([codice], risposta=risposta, soluzione=SOLUZIONE, pagina=pagina, php=True, lasco=lasco)[0]
    ok = (u == "OK") == attesa and (contiene is None or contiene in u)
    fallite += not ok
    print("%s %-60s %s" % ("  " if ok else "!!", titolo, u.replace("\n", " | ")[:220]))


# pagina eseguita con GET e POST
una('stessa_uscita("pagine/elenco.php", get={"genere": "giallo"})', sito(), True, "GET: stessa uscita della soluzione")
una('stessa_uscita("pagine/risultato.php", post={"nome": "Mario", "eta": "17", "corso": "teatro"})', sito(), True,
    "POST: stessa uscita della soluzione")
una('stessa_uscita("pagine/elenco.php", get={"genere": "fantasy"})',
    sito(**{"pagine/elenco.php": ELENCO.replace("$libri[$genere]", '$libri["giallo"]')}), False,
    "uscita diversa: si vede l'atteso e l'ottenuto", "Lo Hobbit")
una('stessa_uscita("pagine/elenco.php", get={"genere": "giallo"})',
    sito(**{"pagine/elenco.php": ELENCO.replace("<li>$titolo</li>", "<li><b>$titolo</b></li>")}), False,
    "tag diversi, stesso testo: lo dice", "cambiano i tag")
una('stesso_testo("pagine/elenco.php", get={"genere": "giallo"})',
    sito(**{"pagine/elenco.php": ELENCO.replace("<li>$titolo</li>", "<li><b>$titolo</b></li>")}), True,
    "stesso_testo: i tag non contano")
una('stessa_uscita("pagine/elenco.php", get={"genere": "giallo"})',
    sito(**{"pagine/elenco.php": ELENCO.replace('$genere = $_GET["genere"];', '$genere = $_GET["genere"]')}), False,
    "errore di sintassi con la riga", "alla riga")
una('php_senza_errori("pagine/risultato.php", post={"nome": "Mario"})', sito(), False,
    "avviso di PHP: chiave mancante", "Undefined array key")
una('php_senza_errori("pagine/elenco.php", get={"genere": "giallo"})', sito(), True, "nessun avviso")
una('stessa_uscita("pagine/elenco.php", get={"genere": "giallo"})',
    sito(**{"pagine/elenco.php": "<?php while (true) { }"}), False, "ciclo infinito fermato", "5 secondi")
una('stessa_uscita("pagine/elenco.php", get={"genere": "giallo"})', sito(**{"pagine/elenco.php": None}), False,
    "pagina mancante", "Non trovo la pagina")
una('stessa_uscita("pagine/elenco.php", get={"genere": "giallo"})',
    sito(**{"pagine/elenco.php": '<?php echo file_get_contents("../../__tester__.python3");'}), False,
    "open_basedir: niente file fuori dal sito", "open_basedir")
# controlli sull'uscita
una('usa_uscita("pagine/elenco.php", get={"genere": "giallo"})\nalmeno(2, "li")', sito(), True, "usa_uscita + almeno")
una('usa_uscita("pagine/elenco.php", get={"genere": "giallo"})\ncontiene("Il nome della rosa")', sito(), True,
    "usa_uscita + contiene")
una('usa_uscita("pagine/elenco.php", get={"genere": "giallo"})\ncontiene("Lo Hobbit")', sito(), False,
    "contiene: testo che non c'è", "Lo Hobbit")
una('usa_uscita("pagine/elenco.php", get={"genere": "giallo"})\nalmeno(2, "li")',
    sito(**{"pagine/elenco.php": "<?php echo 'x' . ;"}), False, "usa_uscita con errore fatale: un solo messaggio",
    "si ferma con un errore")
# invio del modulo
una('invia("index.html", {"nome": "Mario", "eta": "17"})', sito(), True, "invio del modulo come la soluzione")
una('invia("index.html", {"nome": "Mario", "eta": "17", "news": "si"})', sito(), True, "invio con una casella spuntata")
una('invia("index.html", {"nome": "Mario", "eta": "17"})', sito(index_html=None) if False else
    sito(**{"index.html": FORM.replace('method="post"', 'method="get"')}), False,
    "modulo con GET, la pagina legge POST", "Undefined array key")
una('invia("index.html", {"nome": "Mario", "eta": "17"})', sito(**{"index.html": FORM.replace('name="nome"', 'name="Nome"')}),
    False, "name diverso: lo dice", 'c\'è name="Nome"')
una('invia("index.html", {"nome": "Mario", "eta": "17"})',
    sito(**{"index.html": FORM.replace('pagine/risultato.php', 'risultato.php')}), False,
    "action che porta a un file che non c'è", "action=")
una('invia("index.html", {"nome": "Mario", "eta": "17"})',
    sito(**{"pagine/risultato.php": RISULTATO.replace('$_POST["eta"]', '$_POST["anni"]')}), False,
    "la pagina legge un name sbagliato", "Undefined array key")
una('usa_invio("index.html", {"nome": "Mario", "eta": "19"})\ncontiene("maggiorenne")', sito(), True,
    "usa_invio + contiene")
una('modulo("pagine/risultato.php", "post", ["nome", "eta"])', sito(), True, "modulo: action, method e campi")
una('modulo("pagine/risultato.php", "post", ["nome", "eta"])',
    sito(**{"index.html": FORM.replace(' method="post"', '')}), False, "modulo senza method", "non ha method")
una('modulo("pagine/risultato.php", "post", ["nome", "cognome"])', sito(), False, "modulo: campo mancante",
    'name="cognome"')
# pagina principale .php
una('struttura_base()', json.dumps({"htmlve": 1, "files": {"index.php": "<!DOCTYPE html><html><head><title>x</title></head><body><?php echo 1; ?></body></html>"}}),
    True, "pagina principale index.php (parametro pagina)", pagina="index.php")

# controllo tollerante (parametro lasco)
NOMI_SUOI = {"index.html": FORM.replace('name="nome"', 'name="Nome"').replace('name="eta"', 'name="anni"'),
             "pagine/risultato.php": RISULTATO.replace('$_POST["nome"]', '$_POST["Nome"]').replace('$_POST["eta"]', '$_POST["anni"]')}
una('invia("index.html", {"nome": "Mario", "eta": "17"})', sito(**NOMI_SUOI), True,
    "lasco: name diversi ma coerenti con la sua pagina PHP", lasco=True)
una('invia("index.html", {"nome": "Mario", "eta": "17"})', sito(**NOMI_SUOI), False,
    "senza lasco: gli stessi name diversi si segnalano", 'name="nome"')
POSIZIONE = {"index.html": FORM.replace('name="nome"', 'name="n1"').replace('name="eta"', 'name="n2"')
             .replace('<label for="nome">Nome</label>', '').replace('<label for="eta">Età</label>', ''),
             "pagine/risultato.php": RISULTATO.replace('$_POST["nome"]', '$_POST["n1"]').replace('$_POST["eta"]', '$_POST["n2"]')}
una('invia("index.html", {"nome": "Mario", "eta": "17"})', sito(**POSIZIONE), True,
    "lasco: campi senza etichetta trovati per posizione", lasco=True)
ALTRA_PAGINA = {"index.html": FORM.replace("pagine/risultato.php", "php/Conferma.php"), "pagine/risultato.php": None,
                "php/Conferma.php": RISULTATO}
una('invia("index.html", {"nome": "Mario", "eta": "17"})', sito(**ALTRA_PAGINA), True,
    "lasco: pagina PHP con un altro nome (segue l'action)", lasco=True)
una('stessa_uscita("pagine/risultato.php", post={"nome": "Mario", "eta": "17", "corso": "teatro"})',
    sito(**ALTRA_PAGINA), True, "lasco: stessa_uscita trova la pagina seguendo il modulo", lasco=True)
una('stessa_uscita("pagine/elenco.php", get={"genere": "giallo"})',
    sito(**{"pagine/elenco.php": None, "Pagine/Elenco.php": ELENCO}), True,
    "lasco: maiuscole diverse nel percorso", lasco=True)
una('modulo("pagine/risultato.php", "post", ["nome", "eta"])', sito(**dict(NOMI_SUOI, **{
    "index.html": NOMI_SUOI["index.html"].replace("pagine/risultato.php", "pagine/ok.php"), "pagine/ok.php": "<?php echo 1;"})),
    True, "lasco: modulo con action e name diversi", lasco=True)
una('modulo("pagine/risultato.php", "post", ["nome", "eta"])',
    sito(**{"index.html": FORM.replace(' method="post"', '')}), False, "lasco: il method resta controllato",
    "non ha method", lasco=True)
PAROLE = {"pagine/risultato.php": RISULTATO.replace('"<p>Ciao $nome, sei minorenne.</p>"', '"<p>ciao $nome sei MINORENNE</p>"')}
una('invia("index.html", {"nome": "Mario", "eta": "17"})', sito(**PAROLE), True,
    "lasco: punteggiatura e maiuscole non contano", lasco=True)
una('invia("index.html", {"nome": "Mario", "eta": "17"})', sito(**PAROLE), False,
    "senza lasco: la stessa uscita si segnala", "doveva mostrare")
ALTRE_PAROLE = {"pagine/risultato.php": '<?php echo "<h1>Benvenuto " . $_POST["nome"] . "!</h1><p>Hai " . $_POST["eta"] . " anni: " . ($_POST["eta"] >= 18 ? "maggiorenne" : "minorenne") . "</p>";'}
una('invia("index.html", {"nome": "Mario", "eta": "17"}, cerca=["Mario", "minorenne"])', sito(**ALTRE_PAROLE), True,
    "cerca: solo i dati contano", lasco=True)
una('invia("index.html", {"nome": "Mario", "eta": "17"}, cerca=["Mario", "minorenne"])',
    sito(**{"pagine/risultato.php": ALTRE_PAROLE["pagine/risultato.php"].replace('"maggiorenne" : "minorenne"', '"minorenne" : "maggiorenne"')}),
    False, "cerca: dato sbagliato, lo dice", "non trovo «minorenne»", lasco=True)
una('invia("index.html", {"nome": "Mario", "eta": "17"}, cerca="Lo Hobbit")', sito(), False,
    "cerca: dato che la soluzione non mostra", "Errore nella domanda", lasco=True)
una('stessa_uscita("pagine/elenco.php", get={"genere": "giallo"}, cerca="Il nome della rosa")', sito(), True,
    "cerca anche senza lasco")
una('invia("index.html", {"nome": "Mario", "eta": "17", "classe": "4A"}, cerca="Mario")',
    sito(**{"index.html": FORM.replace('<option value="4A">4A</option>', '<option value="quarta">4A</option>')}), True,
    "lasco: opzione del menù con un altro value", lasco=True)
una('struttura_base()', sito(**{"index.html": None, "Index.html": FORM}), True,
    "lasco: pagina principale con la maiuscola", lasco=True)
# pagina PHP aperta direttamente: i dati prendono i nomi del modulo o dei link dello studente
una('php_senza_errori("pagine/risultato.php", post={"nome": "Mario", "eta": "15", "corso": "teatro"})',
    sito(**NOMI_SUOI), True, "lasco: php_senza_errori con i name dello studente", lasco=True)
una('stessa_uscita("pagine/risultato.php", post={"nome": "Mario", "eta": "17", "corso": "teatro"})',
    sito(**dict(POSIZIONE, **{"index.html": POSIZIONE["index.html"].replace("pagine/risultato.php", "php/ok.php"),
                              "pagine/risultato.php": None, "php/ok.php": POSIZIONE["pagine/risultato.php"]})),
    True, "lasco: stessa_uscita con altra pagina e name per posizione", lasco=True)
LINK_SUO = {"index.html": FORM.replace("pagine/elenco.php?genere=giallo", "pagine/elenco.php?tipo=giallo"),
            "pagine/elenco.php": ELENCO.replace('$_GET["genere"]', '$_GET["tipo"]')}
una('stessa_uscita("pagine/elenco.php", get={"genere": "fantasy"})', sito(**LINK_SUO), True,
    "lasco: GET con il nome del link dello studente (?tipo=)", lasco=True)
una('usa_uscita("pagine/elenco.php", get={"genere": "giallo"})\nalmeno(2, "li")', sito(**LINK_SUO), True,
    "lasco: usa_uscita con il nome del link dello studente", lasco=True)
una('php_senza_errori("pagine/risultato.php", post={"nome": "Mario", "eta": "15", "corso": "teatro"})',
    sito(**NOMI_SUOI), False, "senza lasco: i name diversi danno l'avviso", "Undefined array key")


# consegna come .zip allegato (tipologia consegna_php): con o senza la cartella del sito nello zip
def zip_del_sito(prefisso, **files):
    import io
    import zipfile
    f = {"index.html": FORM, "pagine/risultato.php": RISULTATO, "pagine/elenco.php": ELENCO}
    f.update(files)
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for n, c in f.items():
            if c is not None:
                z.writestr(prefisso + n, c)
    return b.getvalue()


for prefisso, file_zip, attesa, titolo in [
        ("", {}, ["OK", "OK"], "zip senza cartella"),
        ("torneo/", {}, ["OK", "OK"], "zip con la cartella del sito"),
        ("Torneo/", NOMI_SUOI, ["OK", "OK"], "zip con name diversi, lasco")]:
    u = esegui(['invia("index.html", {"nome": "Ada", "eta": "20"})',
                'stessa_uscita("pagine/elenco.php", get={"genere": "giallo"})'],
               allegati={"torneo.zip": zip_del_sito(prefisso, **file_zip)}, soluzione=SOLUZIONE, pagina="index.html",
               php=True, lasco=bool(file_zip))
    ok = u == attesa
    fallite += not ok
    print("%s %-60s %s" % ("  " if ok else "!!", titolo, " | ".join(u)[:220]))


# pagine con il database (parametro database: facciata di mysqli su SQLite, come php_mysqli_sqlite)
import sqlite3 as _sqlite3
import tempfile as _tempfile


def db_torneo():
    with _tempfile.TemporaryDirectory() as d:
        f = d + "/dbtorneo.db"
        con = _sqlite3.connect(f)
        con.executescript("""CREATE TABLE Iscritti (Id INTEGER PRIMARY KEY AUTOINCREMENT, Nome TEXT NOT NULL,
                             Eta INTEGER NOT NULL, Categoria TEXT NOT NULL);
                             INSERT INTO Iscritti (Nome, Eta, Categoria) VALUES ('Anna', 16, 'Junior'), ('Luca', 18, 'Senior');""")
        con.commit()
        con.close()
        return open(f, "rb").read()


CONNESSIONE = """mysqli_report(MYSQLI_REPORT_OFF);
$host = "127.0.0.1";
$username = "root";
$password = "";
$nomedb = "dbtorneo";
$connessione = mysqli_connect($host, $username, $password, $nomedb)
    or die("Connessione non riuscita: " . mysqli_connect_error());
"""
FORM_DB = """<!DOCTYPE html>
<html><head><title>Iscrizione</title></head><body>
<form action="pagine/iscrivi.php" method="post">
  <label for="nome">Nome</label> <input type="text" id="nome" name="nome" required>
  <label for="eta">Età</label> <input type="number" id="eta" name="eta" required>
  <button>Iscriviti</button>
</form>
<a href="pagine/elenco.php">Elenco</a> <a href="pagine/categoria.php?categoria=Junior">Junior</a>
</body></html>
"""
ISCRIVI = """<?php
""" + CONNESSIONE + """$nome = $_POST["nome"];
$eta = $_POST["eta"];
if ($eta >= 18) {
    $categoria = "Senior";
} else {
    $categoria = "Junior";
}
$query = "INSERT INTO Iscritti (Nome, Eta, Categoria) VALUES ('$nome', $eta, '$categoria')";
mysqli_query($connessione, $query) or die("Errore nell'inserimento: " . mysqli_error($connessione));
mysqli_close($connessione);
echo "<p>Iscrizione registrata: $nome, categoria $categoria</p>";
"""
ELENCO_DB = """<?php
""" + CONNESSIONE + """$risultato = mysqli_query($connessione, "SELECT Nome, Categoria FROM Iscritti ORDER BY Nome")
    or die("Errore nella query: " . mysqli_error($connessione));
mysqli_close($connessione);
echo "<ul>\\n";
while ($riga = mysqli_fetch_array($risultato)) {
    echo "<li>$riga[Nome] ($riga[Categoria])</li>\\n";
}
echo "</ul>\\n";
"""
CATEGORIA_DB = """<?php
""" + CONNESSIONE + """$categoria = $_GET["categoria"];
$risultato = mysqli_query($connessione, "SELECT Nome FROM Iscritti WHERE Categoria = '$categoria' ORDER BY Nome")
    or die("Errore nella query: " . mysqli_error($connessione));
echo "<h1>$categoria</h1>\\n";
while ($riga = mysqli_fetch_array($risultato)) {
    echo "<p>$riga[Nome]</p>\\n";
}
"""


def sito_db(**files):
    f = {"index.html": FORM_DB, "pagine/iscrivi.php": ISCRIVI, "pagine/elenco.php": ELENCO_DB,
         "pagine/categoria.php": CATEGORIA_DB}
    f.update(files)
    return json.dumps({"htmlve": 1, "cartelle": ["pagine"], "files": {k: v for k, v in f.items() if v is not None},
                       "immagini": {}})


DB = db_torneo()
SOLUZIONE_DB = sito_db()


def con_db(codici, risposta, attese, titolo, contiene=None, lasco=False):
    global fallite
    u = esegui(codici if isinstance(codici, list) else [codici], risposta=risposta, soluzione=SOLUZIONE_DB,
               pagina="index.html", php=True, lasco=lasco, database="dbtorneo", supporto={"dbtorneo.db": DB})
    attese = attese if isinstance(attese, list) else [attese]
    ok = [(x == "OK") == a for x, a in zip(u, attese)] == [True] * len(attese) and len(u) == len(attese) \
        and (contiene is None or contiene in " ".join(u))
    fallite += not ok
    print("%s %-60s %s" % ("  " if ok else "!!", titolo, " || ".join(x.replace("\n", " | ") for x in u)[:260]))


con_db('stessa_uscita("pagine/elenco.php")', sito_db(), True, "db: elenco dal database come la soluzione")
con_db('stessa_uscita("pagine/categoria.php", get={"categoria": "Senior"})', sito_db(), True, "db: GET e WHERE")
con_db('invia("index.html", {"nome": "Mario", "eta": "17"})', sito_db(), True, "db: invio con INSERT")
con_db('invia("index.html", {"nome": "Mario", "eta": "17"})\nstessa_tabella("SELECT Nome, Eta, Categoria FROM Iscritti ORDER BY Id")',
       sito_db(), True, "db: stessa_tabella dopo l'invio")
con_db('invia("index.html", {"nome": "Mario", "eta": "17"})\nstessa_tabella("SELECT Nome, Eta, Categoria FROM Iscritti ORDER BY Id")',
       sito_db(**{"pagine/iscrivi.php": ISCRIVI.replace("$eta >= 18", "$eta >= 16")}), False,
       "db: categoria sbagliata nella tabella", "invece dà 3 righe")
con_db('usa_invio("index.html", {"nome": "Mario", "eta": "17"})\nusa_uscita("pagine/elenco.php")\ncontiene("Mario (Junior)")',
       sito_db(), True, "db: le richieste dello stesso test si sommano")
con_db(['invia("index.html", {"nome": "Mario", "eta": "17"})',
        'esito([] if righe_del_database("SELECT COUNT(*) FROM Iscritti") == [["2"]] else ["non riparte"])'],
       sito_db(), [True, True], "db: ogni test riparte dal database allegato")
con_db('stessa_uscita("pagine/elenco.php")', sito_db(**{"pagine/elenco.php": ELENCO_DB.replace("FROM Iscritti", "FROM Iscritto")}),
       False, "db: tabella sbagliata, messaggio di SQLite", "no such table: Iscritto")
con_db('stessa_uscita("pagine/elenco.php")', sito_db(**{"pagine/elenco.php": ELENCO_DB.replace('"dbtorneo"', '"torneo"')}),
       False, "db: nome del database sbagliato", "Unknown database 'torneo'")
con_db('stessa_uscita("pagine/elenco.php")', sito_db(**{"pagine/elenco.php": ELENCO_DB.replace('"dbtorneo"', '"torneo"')}),
       True, "db, lasco: nome del database libero", lasco=True)
con_db('stessa_uscita("pagine/elenco.php")', sito_db(**{"pagine/elenco.php": ELENCO_DB.replace('$password = "";', '$password = "root";')}),
       False, "db, lasco: password sbagliata resta un errore", "Access denied", lasco=True)
NOMI_DB = {"index.html": FORM_DB.replace('name="nome"', 'name="giocatore"').replace('name="eta"', 'name="anni"'),
           "pagine/iscrivi.php": ISCRIVI.replace('$_POST["nome"]', '$_POST["giocatore"]').replace('$_POST["eta"]', '$_POST["anni"]')}
con_db('invia("index.html", {"nome": "Mario", "eta": "17"}, cerca=["Mario", "Junior"])\nstessa_tabella("SELECT Nome, Eta, Categoria FROM Iscritti ORDER BY Id")',
       sito_db(**NOMI_DB), True, "db, lasco: name diversi, invio e tabella", lasco=True)
con_db('php_senza_errori("pagine/iscrivi.php", post={"nome": "Mario", "eta": "17"})\nstessa_tabella("SELECT Nome FROM Iscritti ORDER BY Id")',
       sito_db(**NOMI_DB), True, "db, lasco: pagina aperta direttamente con i suoi name", lasco=True)
con_db('stessa_tabella("SELECT Nome FROM Iscritto")', sito_db(), False, "db: query del test sbagliata", "Errore nella domanda")


import facciata
ok = facciata.nel_template() == facciata.originale()
fallite += not ok
print("%s %-60s %s" % ("  " if ok else "!!", "facciata di mysqli uguale all'originale", "" if ok else "rilancia crea_prototipo.py"))

print("PROVE PHP FALLITE:", fallite)
