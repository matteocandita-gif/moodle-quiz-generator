# La facciata FakeDB: mappa delle query, formati, funzioni

_Il prototipo `php_mysqli_sqlite` è descritto in `prototipo-sqlite.md` (database allegato, `FakeDB::configure`, test, messaggi). Qui: la mappa `queries` per i risultati forzati (sezioni 1 e 2), gli errori di connessione, le funzioni per lo studente e per i test, gli schemi del form e dell'output normalizzato. Il vecchio prototipo `php_mysqli_mock`, che rispondeva solo con la mappa, è stato tolto nella 0.15.0._

## Indice
1. Normalizzazione e chiavi della mappa
2. Formati dei risultati
3. Errori generati automaticamente
4. Funzioni disponibili allo studente
5. Funzioni di supporto per i test
6. Schemi ricorrenti (dati del form, output normalizzato)

## 1. Normalizzazione e chiavi della mappa

Una query dello studente si confronta con le chiavi della mappa `queries` dopo averle normalizzate tutte e due:

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

Attenzione: anche i valori tra apici finiscono in minuscolo, quindi una chiave non distingue `'Calvino'` da `'calvino'`.

**Tipi di chiave**

- **testuale**: una query scritta normalmente; viene normalizzata e confrontata per intero.
- **regex**: una stringa che inizia con `/`; viene applicata alla query **normalizzata**, quindi va scritta in minuscolo e senza spazi attorno a `, = ( ) < >`. Esempi: `'/from libro\b/'`, `"/autore='' /"`, `'/,la storia,/'`, `'/autori,/'`.

Le chiavi vengono provate **nell'ordine in cui sono scritte** e vince la prima che corrisponde. Ordine consigliato: errori di sintassi, poi errori sui nomi, poi casi particolari (valori vuoti), infine la query corretta e le sue varianti.

Una query che non corrisponde a nessuna chiave viene eseguita davvero su SQLite.

## 2. Formati dei risultati

| Valore nella mappa | Effetto |
|---|---|
| lista di righe `[['Col' => 'v', ...], ...]` | SELECT riuscita; `[]` = nessuna riga. I valori vengono convertiti in stringa (tranne `null`), come nel vero mysqli |
| intero `n` | query di modifica riuscita, `mysqli_affected_rows` = n |
| `true` | query di modifica riuscita |
| `['affected' => n, 'insert_id' => id]` | INSERT riuscita, con righe coinvolte e id generato (`mysqli_insert_id`) |
| `['error' => [codice, 'messaggio']]` | errore MySQL simulato: `mysqli_query` restituisce `false`, `mysqli_error` il messaggio |

I nomi delle colonne nelle righe devono essere scritti come nella query (`'Titolo'`, non `'titolo'`): lo studente li usa come chiavi di `$riga[...]`, che in PHP distinguono maiuscole e minuscole.

Un risultato forzato **non si ordina e non si filtra**: le righe vanno scritte già nell'ordine e con il filtro che darebbe la query.

## 3. Errori generati automaticamente

La connessione è controllata dalla facciata, con i messaggi di MySQL:

| Situazione | errno | Messaggio |
|---|---|---|
| host non accettato | 2002 | `php_network_getaddresses: getaddrinfo for HOST failed: Name or service not known` |
| porta diversa da quella configurata | 2002 | `Connection refused` |
| utente o password errati | 1045 | `Access denied for user 'UTENTE'@'localhost' (using password: YES)` (oppure `NO` se la password è vuota) |
| database inesistente | 1049 | `Unknown database 'NOME'` |
| query senza database selezionato | 1046 | `No database selected` |

In caso di errore di connessione `mysqli_connect` restituisce `false` e `mysqli_connect_error()` restituisce il messaggio. Passare `false` a `mysqli_query` produce il TypeError vero di PHP (`mysqli_query(): Argument #1 ($mysql) must be of type mysqli, bool given`).

Altri errori PHP riprodotti fedelmente grazie ai type hint: `mysqli_fetch_array(): Argument #1 ($result) must be of type mysqli_result, string given` (se lo studente passa `$query` invece di `$risultato`). Chiamare metodi dopo `mysqli_close` lancia `Error: mysqli object is already closed`.

## 4. Funzioni disponibili allo studente

Procedurali: `mysqli_connect`, `mysqli_connect_error`, `mysqli_connect_errno`, `mysqli_query`, `mysqli_error`, `mysqli_errno`, `mysqli_select_db`, `mysqli_set_charset`, `mysqli_real_escape_string` (equivale ad `addslashes`), `mysqli_affected_rows`, `mysqli_insert_id`, `mysqli_close`, `mysqli_fetch_assoc`, `mysqli_fetch_row`, `mysqli_fetch_array` (predefinito `MYSQLI_BOTH`), `mysqli_fetch_object`, `mysqli_fetch_all` (predefinito `MYSQLI_NUM`), `mysqli_num_rows`, `mysqli_num_fields`, `mysqli_data_seek`, `mysqli_free_result`, `mysqli_report`.

A oggetti: `new mysqli(...)` con `connect_error`, `connect_errno`, `error`, `errno`, `affected_rows`, `insert_id`, `query`, `select_db`, `set_charset`, `real_escape_string`, `close`; `mysqli_result` con `num_rows`, `field_count`, `fetch_*`, `data_seek`, `free` e `foreach` sul risultato.

Costanti: `MYSQLI_ASSOC`, `MYSQLI_NUM`, `MYSQLI_BOTH`, `MYSQLI_REPORT_*`.

**Non disponibili**: prepared statements (`mysqli_prepare`, `bind_param`…), transazioni, `mysqli_multi_query`.

## 5. Funzioni di supporto per i test

- `FakeDB::executedQueries()`: elenco delle query eseguite dallo studente, nel testo originale.
- `FakeDB::connectionClosed()`: `true` se lo studente ha chiamato `mysqli_close`.
- `FakeDB::normalize($sql)`: normalizza una query come le chiavi della mappa (utile per confronti).
- `FakeDB::$log`: registro grezzo (`['connect', host, user, pass, db]`, `['query', sql]`, `['close']`).

Per stampare controlli **dopo** lo script dello studente, anche se termina con `die()`, usa `register_shutdown_function` nel campo Test. Ciò che stampa entra nell'output e va quindi messo anche nell'output atteso.

## 6. Schemi ricorrenti

### Dati del form

```php
$_GET = ['autore' => 'Calvino', 'max' => '15'];   // oppure $_POST = [...]
```

I valori sono stringhe, come quelli che arrivano da un form vero.

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
