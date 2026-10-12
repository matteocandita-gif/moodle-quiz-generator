# Esempio completo con il prototipo mock: debugging (SELECT con form)

Questa è la domanda reale «L5 - C7 - Debug: la ricerca», ricostruita dall'XML esportato dal Moodle dell'utente: passandola a `scripts/crea_xml.py` si riottiene lo stesso XML (verificato campo per campo, a parte `answerboxlines`, che lo script calcola dalla lunghezza del preload). Usala come modello di livello di dettaglio: testo HTML con disclaimer, note per il docente, preload, soluzione, tre test con dati diversi e un caso limite (nessun risultato).

Tutto ciò che sta sotto la linea è il contenuto del file di specifica.

---

```text
=== question
=== name
L5 - C7 - Debug: la ricerca
=== options
prototipo: mock
=== note
Errori inseriti, nell'ordine in cui lo studente li incontra:
1. $_POST al posto di $_GET: $autore vuoto, query "Autore =  AND ..." -> errore di sintassi near 'AND Prezzo <= 10'
   (piu' il warning Undefined array key, se Jobe lo mostra). Se lo studente aggiunge prima gli apici: Autore = '' -> nessun risultato.
2. apici mancanti intorno all'autore -> Unknown column 'Pirandello' in 'where clause'
3. mysqli_fetch_array($query) invece di $risultato -> TypeError di PHP
=== questiontext
<p dir="ltr">Il form di ricerca invia con il metodo <strong>GET</strong> alla pagina cerca.php i campi <strong>autore</strong> e <strong>max</strong>. La pagina deve mostrare titolo e prezzo dei libri di quell'autore che costano al massimo max euro, oppure «Nessun libro trovato». Database dblibreria, tabella Libri, server 127.0.0.1, utente root, password vuota.</p>
<p dir="ltr">Il codice contiene <strong>3 errori</strong>. Premi <strong>Controlla</strong> e leggi i messaggi: alcuni arrivano dal DBMS, altri da PHP. Se un errore riguarda la query, ricorda il trucco della lezione: stampa la query con <code dir="ltr">echo $query;</code> per vedere esattamente che cosa arriva al DBMS.</p>
<div style="border: 1px solid #e69138; border-radius: 4px; margin: 12px 0;">
<p style="background-color: #e69138; margin: 0; padding: 6px 16px; color: #ffffff;"><strong>N.B. questa è una simulazione</strong></p>
<div style="background-color: #f9cb9c; padding: 12px 16px;">
<p>Non c'è un vero database: il correttore finge di essere il DBMS e risponde con i dati e i messaggi di errore che darebbe MySQL. Serve solo per imparare a leggere gli errori e a correggere il codice. Il codice corretto funziona allo stesso modo anche con XAMPP e PHPMyAdmin.</p>
<p>Poiché la simulazione riconosce le query confrontandone il testo, scrivi la query <strong>esattamente come chiede la consegna</strong>, senza aggiungere colonne, alias o condizioni (per esempio, non usare <span style="font-family: monospace;">SELECT *</span>).</p>
</div>
</div>
=== preload
<?php
mysqli_report(MYSQLI_REPORT_OFF);

// Lettura dei dati del form
$autore = $_POST["autore"];
$max = $_GET["max"];

// 1. Connessione
$host = "127.0.0.1"; 
$username = "root"; 
$password = ""; 
$nomedb = "dblibreria";
$connessione = mysqli_connect($host, $username, $password, $nomedb)
    or die("Connessione non riuscita: " . mysqli_connect_error());

// 2. Scrittura della query
$query = "SELECT Titolo, Prezzo FROM Libri WHERE Autore = " . $autore . " AND Prezzo <= " . $max;

// 3. Esecuzione
$risultato = mysqli_query($connessione, $query)
    or die("Errore nella query: " . mysqli_error($connessione));

// 4. Chiusura
mysqli_close($connessione);

// 5. Elaborazione
if (mysqli_num_rows($risultato) == 0) {
    echo "<p>Nessun libro trovato</p>\n";
} else {
    while ($riga = mysqli_fetch_array($query)) {
        echo "<p>" . $riga["Titolo"] . " - " . $riga["Prezzo"] . " euro</p>\n";
    }
}
?>
=== answer
<?php
mysqli_report(MYSQLI_REPORT_OFF);

// Lettura dei dati del form
$autore = $_GET["autore"];
$max = $_GET["max"];

// 1. Connessione
$connessione = mysqli_connect("127.0.0.1", "root", "", "dblibreria")
    or die("Connessione non riuscita: " . mysqli_connect_error());

// 2. Scrittura della query
$query = "SELECT Titolo, Prezzo FROM Libri WHERE Autore = '" . $autore . "' AND Prezzo <= " . $max;

// 3. Esecuzione
$risultato = mysqli_query($connessione, $query)
    or die("Errore nella query: " . mysqli_error($connessione));

// 4. Chiusura
mysqli_close($connessione);

// 5. Elaborazione
if (mysqli_num_rows($risultato) == 0) {
    echo "<p>Nessun libro trovato</p>\n";
} else {
    while ($riga = mysqli_fetch_array($risultato)) {
        echo "<p>" . $riga["Titolo"] . " - " . $riga["Prezzo"] . " euro</p>\n";
    }
}
?>
=== test
$_GET = ['autore' => 'Pirandello', 'max' => '10'];
FakeDB::configure([
    'user' => 'root', 'password' => '', 'database' => 'dblibreria',
    'unknownQueryError' => 'la query non è quella richiesta: stampala con echo e controllala',
    'queries' => [
        '/autore=and /' => ['error' => [1064, "You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near 'AND Prezzo <= 10' at line 1"]],
        "/autore='' /" => [],
        '/autore=pirandello /' => ['error' => [1054, "Unknown column 'Pirandello' in 'where clause'"]],
        "SELECT Titolo, Prezzo FROM Libri WHERE Autore = 'Pirandello' AND Prezzo <= 10" => [
            ['Titolo' => 'Il fu Mattia Pascal', 'Prezzo' => '9.50'],
        ],
    ],
]);
=== expected
<p>Il fu Mattia Pascal - 9.50 euro</p>

=== test
$_GET = ['autore' => 'Calvino', 'max' => '15'];
FakeDB::configure([
    'user' => 'root', 'password' => '', 'database' => 'dblibreria',
    'unknownQueryError' => 'la query non è quella richiesta: stampala con echo e controllala',
    'queries' => [
        '/autore=and /' => ['error' => [1064, "You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near 'AND Prezzo <= 15' at line 1"]],
        "/autore='' /" => [],
        '/autore=calvino /' => ['error' => [1054, "Unknown column 'Calvino' in 'where clause'"]],
        "SELECT Titolo, Prezzo FROM Libri WHERE Autore = 'Calvino' AND Prezzo <= 15" => [
            ['Titolo' => 'Il barone rampante',    'Prezzo' => '12.00'],
            ['Titolo' => 'Il visconte dimezzato', 'Prezzo' => '10.50'],
        ],
    ],
]);
=== expected
<p>Il barone rampante - 12.00 euro</p>
<p>Il visconte dimezzato - 10.50 euro</p>

=== test
$_GET = ['autore' => 'Rothfuss', 'max' => '10'];
FakeDB::configure([
    'user' => 'root', 'password' => '', 'database' => 'dblibreria',
    'unknownQueryError' => 'la query non è quella richiesta: stampala con echo e controllala',
    'queries' => [
        '/autore=and /' => ['error' => [1064, "You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near 'AND Prezzo <= 10' at line 1"]],
        "/autore='' /" => [],
        '/autore=rothfuss /' => ['error' => [1054, "Unknown column 'Rothfuss' in 'where clause'"]],
        "SELECT Titolo, Prezzo FROM Libri WHERE Autore = 'Rothfuss' AND Prezzo <= 10" => [],
    ],
]);
=== expected
<p>Nessun libro trovato</p>

```
