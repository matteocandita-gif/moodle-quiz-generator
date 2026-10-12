# Il prototipo php_mysqli_sqlite

## Indice
1. Come funziona
2. Il database: allegato, schema o tutti e due
3. FakeDB::configure
4. Che cosa vede lo studente
5. Messaggi di errore (verificati su Jobe)
6. Scrivere i test
7. Calcolare gli output attesi
8. Quando usare la mappa delle query

## 1. Come funziona

Il template (`assets/prototipo-sqlite-template.php`) ha la stessa facciata di mysqli del prototipo mock: funzioni procedurali, classi `mysqli` e `mysqli_result`, costanti, controllo di server, utente, password e nome del database con i messaggi di MySQL (1045, 1049, 2002, 1046). La differenza è nelle query: ogni `mysqli_query` viene **eseguita davvero** con il client `sqlite3` di Jobe (SQLite 3.46, lo stesso delle domande SQL) su un file di lavoro creato all'inizio del test. Il database dura per tutto lo script: un'INSERT seguita da una SELECT vede la riga nuova.

Per ogni query il template lancia `sqlite3` con `.mode json`, `PRAGMA foreign_keys = ON` (salvo `'foreignKeys' => false`), la query, e poi chiede `changes()` e `last_insert_rowid()`, che diventano `mysqli_affected_rows` e `mysqli_insert_id`. Le SELECT (e WITH, VALUES, PRAGMA, EXPLAIN) restituiscono un `mysqli_result` anche quando non hanno righe; le altre istruzioni restituiscono `true`.

Requisiti su Jobe, verificati con la domanda di taratura: client `sqlite3` nel PATH, `proc_open` consentito in PHP, estensione mysqli non caricata. Il prototipo non è combinator: ogni test è un'esecuzione separata, con la sua copia del database.

## 2. Il database: allegato, schema o tutti e due

- **Allegato** (scelta normale): la specifica dichiara il database in una sezione `=== database NOME`; lo script costruisce `NOME.db` e lo allega alla domanda come support file, invisibile allo studente. All'inizio di ogni test il template copia l'**unico** file `.db` allegato; se ce ne sono più di uno, il test deve indicare quale con `'dbfile' => 'NOME.db'`.
- **Schema nel test**: `'schema' => "CREATE TABLE ...; INSERT INTO ...;"`. Serve solo quando non c'è un file allegato.
- **Tutti e due**: lo schema viene eseguito **dopo** la copia del file, quindi può modificare i dati per quel test (`DELETE`, `UPDATE`, una riga in più). È il modo per avere dati diversi da un test all'altro senza allegare più file.

Di solito però basta variare i **dati del form** (`$_GET`, `$_POST`): con un database abbastanza ricco, ricerche diverse danno risultati diversi e lo studente non può adattarsi all'output visibile.

Il database va scritto in SQL che SQLite accetta: vedi `compatibilita.md`, in particolare `Id INTEGER PRIMARY KEY AUTOINCREMENT` per le chiavi automatiche.

## 3. FakeDB::configure

```php
FakeDB::configure([
    'user' => 'root', 'password' => '', 'database' => 'dblibreria',
]);
```

| Opzione | Predefinito | Significato |
|---|---|---|
| `user`, `password`, `database` | `'root'`, `''`, `''` | credenziali e nome del database accettati |
| `hosts` | `['localhost', '127.0.0.1']` | host accettati |
| `port` | `null` | porta richiesta (`null` = qualsiasi) |
| `dbfile` | `''` | file `.db` allegato da copiare; vuoto = l'unico allegato, se c'è |
| `schema` | `''` | SQL eseguito dopo la copia (o su un database vuoto) |
| `foreignKeys` | `true` | chiavi esterne attive, come in MySQL con InnoDB |
| `queries` | `[]` | facoltativa: risultati forzati, stesso formato del mock (sezione 8) |
| `exceptions` | `false` | `true` = errori come eccezioni (PHP 8.1+ senza `mysqli_report`) |

`configure` va chiamato in ogni test: è lui che prepara il database di lavoro. Un errore nello schema ferma il test con «FakeDB: errore nello schema del test».

Funzioni per i test, da usare dopo lo script dello studente (in una `register_shutdown_function`):

- `FakeDB::rows($sql)`: righe di una SELECT sul database di lavoro, con i valori come stringhe;
- `FakeDB::count($tabella)`: numero di righe;
- `FakeDB::executedQueries()`, `FakeDB::connectionClosed()`: come nel mock.

## 4. Che cosa vede lo studente

- Valori come **stringhe**, nel formato di SQLite: un DECIMAL `12.00` diventa `12`, `9.50` diventa `9.5`; le date sono testo; NULL resta `null`.
- `mysqli_fetch_array`, `fetch_assoc`, `fetch_row`, `fetch_object`, `fetch_all`, `foreach` sul risultato, `num_rows`, `data_seek`: come in mysqli.
- `mysqli_real_escape_string` raddoppia l'apice.
- Errori delle query: `mysqli_error` restituisce il messaggio di SQLite così com'è, `mysqli_errno` il codice di SQLite (sotto).

## 5. Messaggi di errore (verificati su Jobe)

Output della domanda di taratura su Jobe, nel formato `mysqli_errno mysqli_error`:

| Errore nel codice | Che cosa esce |
|---|---|
| tabella inesistente | `1 no such table: Libro` |
| testo senza apici nel WHERE | `1 no such column: Calvino` |
| testo di più parole senza apici | `1 near "Storia": syntax error` |
| apostrofo dentro un testo | `1 near "isola": syntax error` |
| valore mancante in fondo alla query (`Prezzo <= `) | `1 near ";": syntax error` |
| INSERT senza elenco, con meno valori delle colonne | `1 table Libri has 4 columns but 3 values were supplied` |
| chiave primaria duplicata | `19 UNIQUE constraint failed: Libri.ISBN` |
| NULL in una colonna NOT NULL | `19 NOT NULL constraint failed: Libri.Titolo` |
| chiave esterna senza riga corrispondente | `19 FOREIGN KEY constraint failed` |
| database sbagliato in `mysqli_connect` | `1049 Unknown database 'dblibrerie'` (connessione, messaggio di MySQL) |

Gli errori di sintassi e di nomi hanno codice 1, quelli dei vincoli 19. Un'INSERT con elenco delle colonne e numero di valori diverso dà `3 values for 4 columns` (questo messaggio non era nella taratura).

## 6. Scrivere i test

Con il database allegato, il campo Test è corto:

```php
// ---- output normalizzato (solo per la scrittura completa e guidata) ----
ob_start();
register_shutdown_function(function () { /* ... come in fakedb-api.md ... */ });

$_GET = ['sala' => 'Auditorium', 'posti' => '10'];
FakeDB::configure(['user' => 'root', 'password' => '', 'database' => 'dblibreria']);
```

- Ogni test ha una **descrizione** (sezione `=== descrizione`, campo Extra): è ciò che lo studente vede nella colonna della prova al posto del codice del test, con il prototipo impostato con `resultcolumns` = `[["Prova", "extra"], ["Atteso", "expected"], ["Ottenuto", "got"]]`. Una frase breve: «Auditorium, almeno 10 posti liberi», «ISBN che non esiste in Libri».
- Le query equivalenti funzionano tutte: non servono chiavi tolleranti né risultati calcolati. Gli errori silenziosi (`>` invece di `>=`, `ORDER BY` dimenticato) producono da soli il risultato sbagliato: basta che i dati lo rendano visibile (un valore esattamente sulla soglia, righe inserite in un ordine diverso da quello richiesto).
- Per una INSERT, controlla la tabella dopo lo script invece del testo della query:

```php
register_shutdown_function(function () {
    $ultima = FakeDB::rows("SELECT Id, ISBN, Lettore, Voto, Giudizio FROM Recensioni ORDER BY Id DESC LIMIT 1");
    echo "[ultima riga di Recensioni: " . implode(", ", $ultima[0]) . "]";
});
```

  Lo studente lo vede come «PHPMyAdmin dopo l'esecuzione». Con l'output normalizzato, questa `echo` non deve iniziare con `"\n"`.
- Nel debugging, i messaggi sono quelli della tabella della sezione 5: le note per il docente li riportano così come escono.

## 7. Calcolare gli output attesi

La parte dei dati degli output (quali righe, in che ordine, in che formato) si calcola eseguendo le query della soluzione con `scripts/prova_query.py`, che costruisce il database dalla specifica e mostra i valori come li vedrà lo studente:

```bash
python3 scripts/prova_query.py specifica.txt dblibreria "SELECT Data, Titolo FROM Presentazioni WHERE Sala = 'Auditorium' AND PostiLiberi >= 10 ORDER BY Data"
```

`--prima "SQL"` esegue prima lo schema di un test. Il SQLite di Python può essere di una versione leggermente diversa da quello di Jobe: per i casi limite il controllo definitivo resta *Validate on save*. L'HTML intorno ai dati si ricostruisce a mano dalla soluzione.

## 8. Quando usare la mappa delle query

`'queries'` ha la precedenza su SQLite: una query che vi compare restituisce il risultato forzato (stesso formato del mock, `fakedb-api.md` sezione 4), tutte le altre vengono eseguite. Serve raramente: per un messaggio di MySQL che si vuole mostrare apposta in un debugging, o per un comportamento che SQLite non riproduce (una funzione di data di MySQL). Nella domanda di taratura `'/from libro\b/' => ['error' => [1146, "Table 'dblibreria.Libro' doesn't exist"]]` ha dato il messaggio di MySQL al posto di quello di SQLite.
