# API del prototipo php_mysqli_mock (FakeDB con mappa delle query)

_Per il prototipo `php_mysqli_sqlite` vedi `prototipo-sqlite.md`; le sezioni 6, 7 e lo schema «Output normalizzato» valgono anche lì._

## Indice
1. Come gira una domanda
2. FakeDB::configure
3. Normalizzazione e chiavi
4. Formati dei risultati
5. Errori generati automaticamente
6. Funzioni disponibili allo studente
7. Funzioni di supporto per i test
8. Schemi ricorrenti (form, INSERT verificata, risultati calcolati, output normalizzato, chiavi tolleranti)

## 1. Come gira una domanda

Il template del prototipo (copia in `assets/prototipo-mock-template.php`) è un unico file PHP:

```
<?php
[definizioni del mock: costanti MYSQLI_*, classi FakeDB, mysqli, mysqli_result, funzioni mysqli_*]
{{ TEST.testcode }}
?>
{{ STUDENT_ANSWER }}
```

Quindi, per ogni test, nell'ordine: si caricano le definizioni, si esegue il **campo Test** (che configura il database simulato e può impostare `$_GET`/`$_POST`), poi gira il **codice dello studente**, che deve iniziare con `<?php`. Il prototipo **non è combinator**: ogni test è un processo separato, quindi lo stato non passa da un test all'altro e un `die()` non interrompe gli altri test.

Il campo Test e il codice dello studente condividono l'ambito globale: per questo le variabili del campo Test iniziano con `$__`.

## 2. FakeDB::configure

```php
FakeDB::configure([
    'user' => 'root',
    'password' => '',
    'database' => 'dblibreria',
    'unknownQueryError' => 'la query non è quella richiesta: stampala con echo e controllala',
    'queries' => [ /* chiave => risultato */ ],
]);
```

| Opzione | Predefinito | Significato |
|---|---|---|
| `user` | `'root'` | utente accettato |
| `password` | `''` | password accettata |
| `database` | `''` | nome del database esistente |
| `hosts` | `['localhost', '127.0.0.1']` | host accettati |
| `port` | `null` | porta richiesta (`null` = qualsiasi) |
| `queries` | `[]` | query previste e risultati |
| `exceptions` | `false` | `true` = gli errori lanciano `mysqli_sql_exception` (PHP 8.1+ senza `mysqli_report(MYSQLI_REPORT_OFF)`); lo studente lo cambia con `mysqli_report()` |
| `unknownQueryError` | `'Query non riconosciuta dal correttore'` | messaggio di `mysqli_error()` per query non previste (errno 1064) |

Un'opzione sconosciuta lancia un'eccezione: utile per accorgersi dei refusi nel campo Test.

## 3. Normalizzazione e chiavi

Prima del confronto, sia la query dello studente sia le chiavi testuali vengono normalizzate:

1. `trim`, tutto in minuscolo, backtick rimossi;
2. punto e virgola e spazi finali rimossi;
3. sequenze di spazi, tabulazioni e a capo ridotte a uno spazio;
4. spazi attorno a `, = ( ) < >` rimossi.

Esempio: la query su due righe

```
INSERT INTO Libri (ISBN, Titolo, Autore, Prezzo)
          VALUES ('9788806', 'La Storia', 'Morante', 14)
```

diventa `insert into libri(isbn,titolo,autore,prezzo) values('9788806','la storia','morante',14)`.

Attenzione: anche i valori tra apici finiscono in minuscolo, quindi il mock non distingue `'Calvino'` da `'calvino'`.

**Tipi di chiave**

- **testuale**: una query scritta normalmente; viene normalizzata e confrontata per intero.
- **regex**: una stringa che inizia con `/`; viene applicata alla query **normalizzata**, quindi va scritta in minuscolo e senza spazi attorno a `, = ( ) < >`. Esempi: `'/from libro\b/'`, `"/autore='' /"`, `'/,la storia,/'`, `'/autori,/'`.

Le chiavi vengono provate **nell'ordine in cui sono scritte** e vince la prima che corrisponde. Ordine consigliato: errori di sintassi, poi errori sui nomi, poi casi particolari (valori vuoti), infine la query corretta e le sue varianti.

Una query che non corrisponde a nessuna chiave restituisce `false` con errno 1064 e il messaggio di `unknownQueryError`.

## 4. Formati dei risultati

| Valore nella mappa | Effetto |
|---|---|
| lista di righe `[['Col' => 'v', ...], ...]` | SELECT riuscita; `[]` = nessuna riga. I valori vengono convertiti in stringa (tranne `null`), come nel vero mysqli |
| intero `n` | query di modifica riuscita, `mysqli_affected_rows` = n |
| `true` | query di modifica riuscita |
| `['affected' => n, 'insert_id' => id]` | INSERT riuscita, con righe coinvolte e id generato (`mysqli_insert_id`) |
| `['error' => [codice, 'messaggio']]` | errore MySQL simulato: `mysqli_query` restituisce `false`, `mysqli_error` il messaggio |

I nomi delle colonne nelle righe devono essere scritti come nella query (`'Titolo'`, non `'titolo'`): lo studente li usa come chiavi di `$riga[...]`, che in PHP distinguono maiuscole e minuscole.

Il mock **non ordina e non filtra**: le righe vanno scritte già nell'ordine e con il filtro che darebbe la query (oppure calcolate, vedi sezione 8).

## 5. Errori generati automaticamente

La connessione è controllata dal mock con messaggi realistici:

| Situazione | errno | Messaggio |
|---|---|---|
| host non accettato | 2002 | `php_network_getaddresses: getaddrinfo for HOST failed: Name or service not known` |
| porta diversa da quella configurata | 2002 | `Connection refused` |
| utente o password errati | 1045 | `Access denied for user 'UTENTE'@'localhost' (using password: YES)` (oppure `NO` se la password è vuota) |
| database inesistente | 1049 | `Unknown database 'NOME'` |
| query senza database selezionato | 1046 | `No database selected` |

In caso di errore di connessione `mysqli_connect` restituisce `false` e `mysqli_connect_error()` restituisce il messaggio. Passare `false` a `mysqli_query` produce il TypeError vero di PHP (`mysqli_query(): Argument #1 ($mysql) must be of type mysqli, bool given`).

Altri errori PHP riprodotti fedelmente grazie ai type hint: `mysqli_fetch_array(): Argument #1 ($result) must be of type mysqli_result, string given` (se lo studente passa `$query` invece di `$risultato`). Chiamare metodi dopo `mysqli_close` lancia `Error: mysqli object is already closed`.

## 6. Funzioni disponibili allo studente

Procedurali: `mysqli_connect`, `mysqli_connect_error`, `mysqli_connect_errno`, `mysqli_query`, `mysqli_error`, `mysqli_errno`, `mysqli_select_db`, `mysqli_set_charset`, `mysqli_real_escape_string` (equivale ad `addslashes`), `mysqli_affected_rows`, `mysqli_insert_id`, `mysqli_close`, `mysqli_fetch_assoc`, `mysqli_fetch_row`, `mysqli_fetch_array` (predefinito `MYSQLI_BOTH`), `mysqli_fetch_object`, `mysqli_fetch_all` (predefinito `MYSQLI_NUM`), `mysqli_num_rows`, `mysqli_num_fields`, `mysqli_data_seek`, `mysqli_free_result`, `mysqli_report`.

A oggetti: `new mysqli(...)` con `connect_error`, `connect_errno`, `error`, `errno`, `affected_rows`, `insert_id`, `query`, `select_db`, `set_charset`, `real_escape_string`, `close`; `mysqli_result` con `num_rows`, `field_count`, `fetch_*`, `data_seek`, `free` e `foreach` sul risultato.

Costanti: `MYSQLI_ASSOC`, `MYSQLI_NUM`, `MYSQLI_BOTH`, `MYSQLI_REPORT_*`.

**Non disponibili**: prepared statements (`mysqli_prepare`, `bind_param`…), transazioni, `mysqli_multi_query`.

## 7. Funzioni di supporto per i test

- `FakeDB::executedQueries()`: elenco delle query eseguite dallo studente, nel testo originale.
- `FakeDB::connectionClosed()`: `true` se lo studente ha chiamato `mysqli_close`.
- `FakeDB::normalize($sql)`: normalizza una query come fa il mock (utile per confronti).
- `FakeDB::$log`: registro grezzo (`['connect', host, user, pass, db]`, `['query', sql]`, `['close']`).

Per stampare controlli **dopo** lo script dello studente, anche se termina con `die()`, usa `register_shutdown_function` nel campo Test. Ciò che stampa entra nell'output e va quindi messo anche nell'output atteso.

## 8. Schemi ricorrenti

### Dati del form

```php
$_GET = ['autore' => 'Calvino', 'max' => '15'];   // oppure $_POST = [...]
```

I valori sono stringhe, come quelli che arrivano da un form vero.

### INSERT con verifica dell'inserimento

La riga finale mostra lo stato della tabella dopo l'esecuzione, come se lo studente guardasse PHPMyAdmin.

```php
$_POST = ['isbn' => '9788806', 'titolo' => 'La Storia', 'autore' => 'Morante', 'prezzo' => '14'];
$__attesa = "INSERT INTO Libri (ISBN, Titolo, Autore, Prezzo) VALUES ('9788806', 'La Storia', 'Morante', 14)";
FakeDB::configure([
    'user' => 'root', 'password' => '', 'database' => 'dblibreria',
    'unknownQueryError' => 'la query non è quella richiesta: stampala con echo e controllala',
    'queries' => [
        // ... chiavi per gli errori previsti, prima della query corretta ...
        $__attesa => ['affected' => 1],
    ],
]);
register_shutdown_function(function () use ($__attesa) {
    $eseguite = array_map(['FakeDB', 'normalize'], FakeDB::executedQueries());
    $inserito = in_array(FakeDB::normalize($__attesa), $eseguite, true);
    echo "\n[tabella Libri: " . ($inserito ? 5 : 4) . " libri]";
});
```

Se la query corretta deve fallire (chiave duplicata), la shutdown stampa direttamente il conteggio invariato. La conferma dello studente (`echo "<p>Libro inserito: ..."`) va **senza** `"\n"` finale e la shutdown inizia con `"\n"`, così l'output atteso ha due righe pulite; lo stesso vale per i messaggi di `die`.

### Risultati calcolati (debugging silenzioso e scrittura guidata)

Quando le query sbagliate devono restituire dati plausibili invece di un errore, il campo Test contiene la tabella completa e una funzione che calcola il risultato di ogni variante. Nei test cambiano solo le prime righe (dati del form e tabella); il resto si copia identico.

```php
$_GET = ['stato' => 'Spedito', 'minimo' => '50'];
$__ordini = [
    ['Numero' => '1041', 'Cliente' => 'Rossi', 'Data' => '2026-09-12', 'Totale' => '50.00', 'Stato' => 'Spedito'],
    // ...
];

// ---- da qui in giù il codice è uguale in tutti i test ----
$__risultato = function ($maggioreUguale, $decrescente) use ($__ordini) {
    $righe = [];
    foreach ($__ordini as $o) {
        $totaleOk = $maggioreUguale
            ? (float)$o['Totale'] >= (float)$_GET['minimo']
            : (float)$o['Totale'] > (float)$_GET['minimo'];
        if ($o['Stato'] === $_GET['stato'] && $totaleOk) {
            unset($o['Stato']);          // solo le colonne della SELECT
            $righe[] = $o;
        }
    }
    usort($righe, function ($a, $b) use ($decrescente) {
        return $decrescente ? strcmp($b['Data'], $a['Data']) : strcmp($a['Data'], $b['Data']);
    });
    return $righe;
};
$__inizio = "SELECT Numero, Cliente, Data, Totale FROM Ordini WHERE Stato = '" . $_GET['stato'] . "' AND Totale ";
$__min = $_GET['minimo'];
FakeDB::configure([
    'user' => 'root', 'password' => '', 'database' => 'dblibreria',
    'unknownQueryError' => 'la query non è quella richiesta: stampala con echo e controllala',
    'queries' => [
        "/stato=''/" => [],
        $__inizio . ">= $__min ORDER BY Data DESC" => $__risultato(true, true),
        $__inizio . ">= $__min ORDER BY Data"      => $__risultato(true, false),
        $__inizio . ">= $__min ORDER BY Data ASC"  => $__risultato(true, false),
        $__inizio . "> $__min ORDER BY Data DESC"  => $__risultato(false, true),
        $__inizio . "> $__min ORDER BY Data"       => $__risultato(false, false),
        $__inizio . "> $__min ORDER BY Data ASC"   => $__risultato(false, false),
    ],
]);
```

Adatta la funzione alle varianti che ti interessano (colonne stampate, condizioni, verso dell'ordinamento) e registra una chiave per ciascuna. Per l'ordinamento di testi usa `strcmp`; per numeri, il confronto tra `(float)`.

### Output normalizzato (scrittura completa e guidata)

Chi scrive il codice da sé va a capo e indenta come vuole, e quasi mai mette `"\n"` alla fine degli `echo`. Per non bocciare una pagina giusta per uno spazio, il campo Test cattura l'output dello studente e lo riscrive in forma canonica: toglie gli spazi e gli a capo tra un tag e l'altro e va a capo dopo i tag di blocco. Va messo **all'inizio** del campo Test, prima di ogni altra `register_shutdown_function`:

```php
// ---- output normalizzato: spazi e a capo dello studente non contano ----
ob_start();
register_shutdown_function(function () {
    $out = trim((string)ob_get_clean());
    $out = preg_replace('/>\s+</', '><', $out);
    $out = preg_replace('#(<table[^>]*>|</table>|</tr>|<ul[^>]*>|</ul>|<ol[^>]*>|</ol>|</li>|</p>|</h[1-6]>|<br\s*/?>)#i', '$1' . "\n", $out);
    echo rtrim($out) . "\n";
});
```

L'output atteso si scrive quindi in forma canonica: un a capo dopo `<table>`, `</table>`, `</tr>`, `<ul>`, `</ul>`, `</li>`, `</p>`, `</hN>`, `<br>`, nessuno altrove. Esempio:

```
<table>
<tr><th>Titolo</th><th>Prezzo</th></tr>
<tr><td>Il barone rampante</td><td>12.00</td></tr>
</table>
```

Non normalizza gli spazi dentro il testo (`<td> Calvino </td>` resta diverso da `<td>Calvino</td>`) né le maiuscole dei tag: la consegna deve indicare la struttura HTML esatta da produrre. Se nello stesso test c'è anche la riga di controllo di una INSERT, la sua `echo` **non** deve iniziare con `"\n"`, perché l'output normalizzato termina già con un a capo.

### Chiavi tolleranti (scrittura completa)

Chi scrive la query da sé può usare varianti equivalenti che il confronto testuale non riconosce. Per la query corretta usa una **regex ancorata** che accetti le varianti innocue più probabili, e se serve una seconda chiave con l'ordine delle condizioni invertito:

```php
// virgolette singole o doppie intorno al testo, ASC facoltativo
'/^select titolo,prezzo from libri where autore=[\'"]calvino[\'"] and prezzo<=15 order by prezzo( asc)?$/' => $__righe,
// stesse condizioni in ordine inverso
'/^select titolo,prezzo from libri where prezzo<=15 and autore=[\'"]calvino[\'"] order by prezzo( asc)?$/' => $__righe,
```

(Dentro una stringa PHP tra apici singoli, l'apice nella classe di caratteri va scritto `\'`.) Le righe vanno in una variabile (`$__righe`) per non ripeterle. Le varianti che cambiano il risultato (colonne diverse, `SELECT *`, condizioni in più) non vanno accettate: la consegna e il disclaimer le escludono, e il messaggio di `unknownQueryError` invita a stampare la query.
