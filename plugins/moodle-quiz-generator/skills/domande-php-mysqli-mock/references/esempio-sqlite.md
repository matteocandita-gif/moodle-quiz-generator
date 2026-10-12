# Esempio completo con il prototipo sqlite: scrittura completa (SELECT con form)

La domanda «L5 - C8 - Scrivere: le presentazioni» nella versione per `php_mysqli_sqlite`: database dichiarato nella specifica e allegato, campo Test corto (output normalizzato, dati del form, `configure`), una descrizione per ogni test, output attesi calcolati con `prova_query.py`. È il modello per le domande nuove.

Tutto ciò che sta sotto la linea è il contenuto del file di specifica.

---

```text
=== category
Ripasso quarta in quinta/Lezione 5 - PHP e database
=== database dblibreria
CREATE TABLE Presentazioni (
  Id INTEGER PRIMARY KEY AUTOINCREMENT,
  Titolo VARCHAR(100) NOT NULL,
  Ospite VARCHAR(50) NOT NULL,
  Data DATE NOT NULL,
  Sala VARCHAR(20) NOT NULL,
  PostiLiberi INT NOT NULL
);
INSERT INTO Presentazioni (Titolo, Ospite, Data, Sala, PostiLiberi) VALUES
('Le strade del sale', 'Marta Ferri', '2026-11-08', 'Auditorium', 25),
('Cucina di mare', 'Paolo Neri', '2026-10-22', 'Giardino', 40),
('Il quaderno blu', 'Elena Sarti', '2026-10-18', 'Auditorium', 10),
('Orti in città', 'Sara Galli', '2026-10-20', 'Giardino', 30),
('La notte dei racconti', 'Anna Bruni', '2026-10-28', 'Mansarda', 12),
('Numeri primi', 'Davide Conti', '2026-10-25', 'Auditorium', 4),
('Api e fiori', 'Marco Villa', '2026-10-14', 'Giardino', 20),
('Viaggio a nord', 'Giulia Rocca', '2026-10-30', 'Auditorium', 15),
('Sentieri', 'Fabio Testa', '2026-10-17', 'Giardino', 8),
('Fumetti a merenda', 'Luca Bassi', '2026-11-05', 'Mansarda', 6),
('Erbario', 'Chiara Moro', '2026-11-03', 'Giardino', 22),
('Poesia ad alta voce', 'Irene Fabbri', '2026-11-12', 'Auditorium', 30);
=== question
=== name
L5 - C8 - Scrivere: le presentazioni
=== options
answerboxlines: 30
=== note
Scrittura completa, prototipo php_mysqli_sqlite: la query dello studente viene eseguita sul database allegato
dblibreria.db (tabella Presentazioni, 12 righe), quindi qualsiasi query equivalente funziona. Output normalizzato.
Tutti i test usano lo stesso database e cambiano solo i dati del form. Con > invece di >= mancano le presentazioni
con i posti uguali al minimo (decisivo nel test 4, nascosto); senza ORDER BY le righe escono nell'ordine di inserimento.
=== questiontext
<p>La libreria organizza presentazioni di libri in tre sale. Nel database <strong>dblibreria</strong> la tabella <strong>Presentazioni</strong> contiene:</p>
<p><span style="font-family: monospace;">Presentazioni (<u>Id</u>, Titolo, Ospite, Data, Sala, PostiLiberi)</span></p>
<p>Il form qui sotto invia con il metodo <strong>GET</strong> alla pagina <span style="font-family: monospace;">presentazioni.php</span> la sala scelta e il numero minimo di posti liberi:</p>
[[codice html]]
<form action="presentazioni.php" method="GET">
  <label>Sala:</label>
  <select name="sala">
    <option>Auditorium</option>
    <option>Giardino</option>
    <option>Mansarda</option>
  </select>
  <label>Posti liberi almeno:</label> <input type="number" name="posti">
  <input type="submit" value="Cerca">
</form>
[[/codice]]
<p>Scrivi <strong>tutto il codice</strong> della pagina <span style="font-family: monospace;">presentazioni.php</span>, da <span style="font-family: monospace;">&lt;?php</span> in poi. La pagina si connette a dblibreria (server 127.0.0.1, utente root, password vuota) e mostra data, titolo, ospite e posti liberi delle presentazioni <strong>di quella sala</strong> che hanno <strong>almeno</strong> quel numero di posti liberi, <strong>dalla più vicina alla più lontana</strong> nel tempo, in una tabella con questa struttura (qui con una sola presentazione):</p>
[[codice html]]
<table>
<tr><th>Data</th><th>Titolo</th><th>Ospite</th><th>Posti liberi</th></tr>
<tr><td>2026-10-28</td><td>La notte dei racconti</td><td>Anna Bruni</td><td>12</td></tr>
</table>
[[/codice]]
<p>Se non c'è nessuna presentazione, la pagina stampa solo <span style="font-family: monospace;">&lt;p&gt;Nessuna presentazione trovata&lt;/p&gt;</span>.</p>
<p>Il correttore confronta l'output della tua pagina con quello atteso: tag e testi devono essere <strong>esattamente</strong> questi (anche <span style="font-family: monospace;">&lt;table&gt;</span> senza attributi), mentre spazi e a capo non contano. Se compare un errore della query, stampala con <span style="font-family: monospace;">echo $query;</span> e controllala.</p>
<div style="background-color: #f9cb9c; border-left: 5px solid #e69138; padding: 12px 16px; border-radius: 4px; margin: 0 0 16px;">
<p style="margin: 0 0 6px; color: #783f04;"><strong>N.B. questa è una simulazione</strong></p>
<p style="margin: 0 0 6px;">Il tuo codice PHP viene eseguito davvero, e anche le query: ma il database non è MySQL, è <strong>SQLite</strong>, un DBMS più semplice che usa quasi lo stesso SQL. Per questo i messaggi di errore sono quelli di SQLite, in inglese e diversi da quelli che vedresti con XAMPP (per esempio <span style="font-family: monospace;">no such table: Libro</span> invece di <span style="font-family: monospace;">Table 'dblibreria.Libro' doesn't exist</span>).</p>
<p style="margin: 0;">Anche qualche risultato è diverso: i prezzi compaiono come 12 e 9.5 invece di 12.00 e 9.50, e i testi confrontati con = distinguono le maiuscole. Il codice corretto funziona allo stesso modo anche con XAMPP.</p>
</div>
=== answer
<?php
mysqli_report(MYSQLI_REPORT_OFF);

// Lettura dei dati del form
$sala = $_GET["sala"];
$posti = $_GET["posti"];

// 1. Connessione
$connessione = mysqli_connect("127.0.0.1", "root", "", "dblibreria")
    or die("Connessione non riuscita: " . mysqli_connect_error());

// 2. Scrittura della query
$query = "SELECT Data, Titolo, Ospite, PostiLiberi FROM Presentazioni
          WHERE Sala = '" . $sala . "' AND PostiLiberi >= " . $posti . "
          ORDER BY Data";

// 3. Esecuzione
$risultato = mysqli_query($connessione, $query)
    or die("Errore nella query: " . mysqli_error($connessione));

// 4. Chiusura
mysqli_close($connessione);

// 5. Elaborazione
if (mysqli_num_rows($risultato) == 0) {
    echo "<p>Nessuna presentazione trovata</p>\n";
} else {
    echo "<table>\n";
    echo "<tr><th>Data</th><th>Titolo</th><th>Ospite</th><th>Posti liberi</th></tr>\n";
    while ($riga = mysqli_fetch_array($risultato)) {
        echo "<tr><td>" . $riga["Data"] . "</td><td>" . $riga["Titolo"] . "</td><td>"
            . $riga["Ospite"] . "</td><td>" . $riga["PostiLiberi"] . "</td></tr>\n";
    }
    echo "</table>\n";
}
?>
=== test
// ---- output normalizzato: spazi e a capo dello studente non contano ----
ob_start();
register_shutdown_function(function () {
    $out = trim((string)ob_get_clean());
    $out = preg_replace('/>\s+</', '><', $out);
    $out = preg_replace('#(<table[^>]*>|</table>|</tr>|<ul[^>]*>|</ul>|<ol[^>]*>|</ol>|</li>|</p>|</h[1-6]>|<br\s*/?>)#i', '$1' . "\n", $out);
    echo rtrim($out) . "\n";
});

$_GET = ['sala' => 'Auditorium', 'posti' => '10'];
FakeDB::configure(['user' => 'root', 'password' => '', 'database' => 'dblibreria']);
=== descrizione
Auditorium, almeno 10 posti liberi
=== expected
<table>
<tr><th>Data</th><th>Titolo</th><th>Ospite</th><th>Posti liberi</th></tr>
<tr><td>2026-10-18</td><td>Il quaderno blu</td><td>Elena Sarti</td><td>10</td></tr>
<tr><td>2026-10-30</td><td>Viaggio a nord</td><td>Giulia Rocca</td><td>15</td></tr>
<tr><td>2026-11-08</td><td>Le strade del sale</td><td>Marta Ferri</td><td>25</td></tr>
<tr><td>2026-11-12</td><td>Poesia ad alta voce</td><td>Irene Fabbri</td><td>30</td></tr>
</table>
=== test
// ---- output normalizzato: spazi e a capo dello studente non contano ----
ob_start();
register_shutdown_function(function () {
    $out = trim((string)ob_get_clean());
    $out = preg_replace('/>\s+</', '><', $out);
    $out = preg_replace('#(<table[^>]*>|</table>|</tr>|<ul[^>]*>|</ul>|<ol[^>]*>|</ol>|</li>|</p>|</h[1-6]>|<br\s*/?>)#i', '$1' . "\n", $out);
    echo rtrim($out) . "\n";
});

$_GET = ['sala' => 'Giardino', 'posti' => '20'];
FakeDB::configure(['user' => 'root', 'password' => '', 'database' => 'dblibreria']);
=== descrizione
Giardino, almeno 20 posti liberi
=== expected
<table>
<tr><th>Data</th><th>Titolo</th><th>Ospite</th><th>Posti liberi</th></tr>
<tr><td>2026-10-14</td><td>Api e fiori</td><td>Marco Villa</td><td>20</td></tr>
<tr><td>2026-10-20</td><td>Orti in città</td><td>Sara Galli</td><td>30</td></tr>
<tr><td>2026-10-22</td><td>Cucina di mare</td><td>Paolo Neri</td><td>40</td></tr>
<tr><td>2026-11-03</td><td>Erbario</td><td>Chiara Moro</td><td>22</td></tr>
</table>
=== test
// ---- output normalizzato: spazi e a capo dello studente non contano ----
ob_start();
register_shutdown_function(function () {
    $out = trim((string)ob_get_clean());
    $out = preg_replace('/>\s+</', '><', $out);
    $out = preg_replace('#(<table[^>]*>|</table>|</tr>|<ul[^>]*>|</ul>|<ol[^>]*>|</ol>|</li>|</p>|</h[1-6]>|<br\s*/?>)#i', '$1' . "\n", $out);
    echo rtrim($out) . "\n";
});

$_GET = ['sala' => 'Mansarda', 'posti' => '15'];
FakeDB::configure(['user' => 'root', 'password' => '', 'database' => 'dblibreria']);
=== descrizione
Mansarda, almeno 15 posti liberi: nessuna
=== expected
<p>Nessuna presentazione trovata</p>
=== test HIDE
// ---- output normalizzato: spazi e a capo dello studente non contano ----
ob_start();
register_shutdown_function(function () {
    $out = trim((string)ob_get_clean());
    $out = preg_replace('/>\s+</', '><', $out);
    $out = preg_replace('#(<table[^>]*>|</table>|</tr>|<ul[^>]*>|</ul>|<ol[^>]*>|</ol>|</li>|</p>|</h[1-6]>|<br\s*/?>)#i', '$1' . "\n", $out);
    echo rtrim($out) . "\n";
});

$_GET = ['sala' => 'Mansarda', 'posti' => '12'];
FakeDB::configure(['user' => 'root', 'password' => '', 'database' => 'dblibreria']);
=== descrizione
Mansarda, almeno 12 posti liberi
=== expected
<table>
<tr><th>Data</th><th>Titolo</th><th>Ospite</th><th>Posti liberi</th></tr>
<tr><td>2026-10-28</td><td>La notte dei racconti</td><td>Anna Bruni</td><td>12</td></tr>
</table>
```
