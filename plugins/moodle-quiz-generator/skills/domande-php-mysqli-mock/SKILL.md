---
name: "domande-php-mysqli-mock"
description: "Crea domande CodeRunner PHP con database simulato per gli esercizi PHP/MySQL della SIA e le consegna come file XML pronto da importare in Moodle. Prototipo principale php_mysqli_sqlite (facciata di mysqli, query eseguite davvero su SQLite con il database allegato alla domanda); prototipo php_mysqli_mock (mappa delle query) per le domande esistenti e i casi particolari. Copre debugging con messaggi di errore, debugging di errori silenziosi, scrittura guidata e scrittura completa di pagine che leggono (SELECT) o inseriscono (INSERT) dati, anche con form GET/POST. Nei quiz (verifiche ed esercitazioni) la usano progettazione-quiz per le convenzioni del codice e materiali-moodle per produrre l'XML dalla dashboard: un quiz intero si comincia sempre con progettazione-quiz. Da sola serve per domande PHP sciolte su mysqli, connessione al database, query eseguite da PHP o form che interrogano o riempiono il database, anche se l'utente non nomina i prototipi o l'XML."
---

# Domande CodeRunner PHP con database simulato

Due prototipi, installati nel Moodle dell'utente, eseguono il PHP dello studente su Jobe con una **facciata di mysqli**: funzioni, classi, controllo di server, utente, password e nome del database.

| Prototipo | Le query | Quando |
|---|---|---|
| `php_mysqli_sqlite` | **eseguite davvero** su SQLite (il client `sqlite3` di Jobe, lo stesso delle domande SQL), sul database allegato alla domanda; errori di SQLite così come escono | **tutte le domande nuove**, salvo richiesta diversa |
| `php_mysqli_mock` | cercate in una mappa scritta nel test: risultati e messaggi decisi a mano, in stile MySQL | domande già esistenti; debugging in cui servono i messaggi di MySQL; comportamenti che SQLite non riproduce |

L'XML non si scrive a mano: si scrive un file di specifica in testo semplice, con il codice leggibile, e `scripts/crea_xml.py` lo trasforma nell'XML con la stessa struttura che Moodle esporta, costruendo e allegando i database.

Un quiz o una verifica intera non parte da qui: si progetta con `progettazione-quiz` nella dashboard. Se la domanda fa parte di un quiz progettato nella dashboard «Bozze dei quiz», la specifica la scrive `da_dashboard.py` di `materiali-moodle` e gli output attesi li calcola `php_attesi.py`: qui valgono le convenzioni del codice e delle tipologie.

## Il percorso dei quiz

Ogni quiz Moodle (verifica, esercitazione, ripasso, anche di programmazione) segue un solo percorso, con la dashboard «Bozze dei quiz»:

1. **`progettazione-quiz`**, parte 1, didattica: tipo di quiz, scaletta e tracce nella dashboard, riviste e approvate dall'utente. Per una verifica di programmazione carica `verifiche-programmazione`; il database di un quiz SQL o PHP viene da `database-didattici`.
2. **`materiali-moodle`**, parte 2, tecnica: dal database della dashboard produce XML e `.mbz`; per le domande di programmazione usa `domande-coderunner-js`, `domande-coderunner-sql` e `domande-php-mysqli-mock`.

Nessun'altra skill è un punto di partenza per un quiz. Da sole servono solo per ciò che non diventa un quiz: una domanda singola, una correzione o un controllo (`materiali-moodle` o la skill CodeRunner del linguaggio), domande per la banca o pagine di teoria (`materiali-moodle`), un database per una lezione in phpMyAdmin (`database-didattici`), la conversione delle vecchie domande SQL (`domande-coderunner-sql`).

## File di riferimento

Leggili quando servono:

| File | Leggilo quando |
|---|---|
| `references/prototipo-sqlite.md` | **sempre** per il prototipo sqlite: database allegato, `configure`, che cosa vede lo studente, messaggi di errore verificati, test, calcolo degli output |
| `references/compatibilita.md` | **sempre** prima di scrivere il database, le consegne e le soluzioni sqlite: differenze tra MySQL e SQLite, AUTO_INCREMENT |
| `references/formato-xml.md` | **sempre** prima di scrivere la specifica: sezioni, opzioni, script |
| `references/stile-html.md` | per il testo della domanda: stile di materiali-moodle e il disclaimer del prototipo mock (quello del prototipo sqlite è superato: vale la sezione «Il disclaimer della simulazione» qui sotto) |
| `references/esempio-sqlite.md` | modello di domanda nuova (scrittura completa, prototipo sqlite); il disclaimer da usare però è quello di questa pagina |
| `references/fakedb-api.md` | prototipo mock (mappa delle query, chiavi regex, risultati calcolati); contiene anche lo schema dell'**output normalizzato**, che vale per entrambi |
| `references/errori-mariadb.md` | prototipo mock: i messaggi di MySQL da far comparire |
| `references/esempio-completo.md` | modello di domanda mock (debugging) |

In `assets/` ci sono i template dei due prototipi e l'XML del prototipo sqlite da importare (`PROTOTYPE_php_mysqli_sqlite.xml`). La versione installata su Moodle potrebbe essere stata modificata dall'utente: se il comportamento descritto diverge, vale il suo.

## Prima di scrivere

Per domande sciolte, fuori dalla dashboard. Ricava dalla richiesta, o chiedi in una sola domanda se manca qualcosa di essenziale:

1. **tipologia**: debugging con messaggi, debugging silenzioso, scrittura guidata, scrittura completa;
2. **query**: SELECT, SELECT con dati del form, INSERT;
3. **collocazione**: in quale lezione o blocco va e che cosa gli studenti hanno già visto;
4. **database**: uno del catalogo della skill `database-didattici` (o creato con quella); se l'utente non dice altro e non c'è un database del quiz, `dblibreria` della Libreria Pagina 42 con le tabelle che servono.

Se la domanda precede un esercizio libero, usa un **contesto diverso** da quello dell'esercizio ma la stessa struttura.

## Convenzioni del codice

Il codice che lo studente vede deve somigliare a quello delle lezioni. Salvo indicazioni diverse:

- connessione con i parametri in **quattro variabili**, sempre con questi nomi e in quest'ordine, sotto il commento `// 1. Connessione` e dopo `mysqli_report(MYSQLI_REPORT_OFF);`:
  ```php
  $host = "127.0.0.1";
  $username = "root";
  $password = "";
  $nomedb = "dblibreria";
  $connessione = mysqli_connect($host, $username, $password, $nomedb)
      or die("Connessione non riuscita: " . mysqli_connect_error());
  ```
  (`$nomedb` è il database della domanda). Negli errori voluti dei debug si sbaglia il valore di una variabile (`$nomedb = "db_libreria";`, `$password = "root";`). Anche questa è una scelta del codice che scriviamo noi: i valori passati direttamente a `mysqli_connect` sono corretti, quindi nella risposta dello studente non sono mai un errore;
- stile procedurale con le **cinque fasi commentate**: `// 1. Connessione`, `// 2. Scrittura della query`, `// 3. Esecuzione`, `// 4. Chiusura`, `// 5. Elaborazione`;
- `or die` con i messaggi `"Connessione non riuscita: " . mysqli_connect_error()`, `"Errore nella query: " . mysqli_error($connessione)`, `"Errore nell'inserimento: " . mysqli_error($connessione)`;
- `while ($riga = mysqli_fetch_array($risultato))` e controllo `mysqli_num_rows($risultato) == 0`;
- **variabili sempre integrate nelle stringhe** tra virgolette doppie, mai concatenate con il punto, nelle query come negli `echo`: `$query = "SELECT Titolo FROM Libri WHERE Genere = '$genere' ORDER BY Titolo";`, `"VALUES ($matricola, '$nome', '$cognome')"`, `echo "<li>$riga[Titolo] ($riga[AnnoPubblicazione])</li>\n";` (dentro la stringa la chiave dell'array va senza apici); apici intorno ai testi nelle query, numeri senza. Il punto resta solo dove c'è una chiamata di funzione, come nei messaggi di `or die`. Gli esempi dei file in `references/` usano ancora la concatenazione: vale questa regola. È la regola del codice che scriviamo noi (soluzioni, codice di partenza, esempi, testi), non una regola per lo studente: la concatenazione con il punto è corretta, quindi nella sua risposta non è mai un errore, non è un errore da inserire nei debug né un distrattore, e la traccia non la vieta;
- `mysqli_insert_id` dopo `mysqli_query` e prima di `mysqli_close`;
- ogni `echo` che produce una riga termina con `"\n"` nel codice dato allo studente.

## Il database (prototipo sqlite)

- Dichiaralo nella specifica con `=== database dblibreria`, in SQL che SQLite accetta (`compatibilita.md`): lo script costruisce `dblibreria.db` e lo allega a ogni domanda sqlite. Lo stesso database può servire più domande della stessa lezione.
- Rendilo **abbastanza ricco** perché i test diano risultati diversi variando solo i dati del form, e perché gli errori silenziosi si vedano: valori esattamente sulla soglia, righe inserite in un ordine diverso da quello richiesto.
- Chiavi automatiche: `Id INTEGER PRIMARY KEY AUTOINCREMENT`; per far partire gli Id da un numero, inserisci una riga con quell'Id.
- Dati diversi per un singolo test: `'schema' => "DELETE …; INSERT …;"` nel `configure`, eseguito dopo la copia del file.

## Il disclaimer della simulazione

Ogni domanda ha il disclaimer come **ultimo elemento** del testo, copiato senza modifiche (`crea_xml.py` controlla che ci sia il titolo «N.B. questa è una simulazione»). Per il prototipo `php_mysqli_sqlite` vale questo, che sostituisce quello di `references/stile-html.md` e di `references/esempio-sqlite.md` (lo stesso testo lo aggiunge `da_dashboard.py` di `materiali-moodle` alle domande della dashboard):

```html
<div style="background-color: #f9cb9c; border-left: 5px solid #e69138; padding: 12px 16px; border-radius: 4px; margin: 0 0 16px;">
<p style="margin: 0 0 6px; color: #783f04;"><strong>N.B. questa è una simulazione</strong></p>
<p style="margin: 0 0 6px;">Il tuo codice PHP viene eseguito, ma dietro non c'è un database MySQL permanente: c'è un database di prova, che non conserva le modifiche. A ogni prova riparte sempre dagli stessi dati. Il comportamento e i messaggi d'errore possono essere diversi da quelli di un vero database MySQL.</p>
<p style="margin: 0;">Per realizzare davvero le pagine occorre usare XAMPP con un vero database MySQL.</p>
</div>
```

Per il prototipo `php_mysqli_mock` resta quello di `references/stile-html.md`.

## Formato di consegna

1. Scrivi il **file di specifica** (`references/formato-xml.md`), partendo da `references/esempio-sqlite.md`. Per ogni domanda: `name` nella numerazione dell'utente (`L5 - C8 - Scrivere: le presentazioni`), `note` per il docente, `questiontext` in HTML con il disclaimer del prototipo come ultimo elemento (sezione precedente), `preload`, `answer`, test con `descrizione` e output atteso.
2. Calcola le righe degli output attesi con `python3 scripts/prova_query.py specifica.txt dblibreria "SELECT …"` e ricostruisci l'HTML intorno dalla soluzione.
3. Lancia `python3 scripts/crea_xml.py specifica.txt /mnt/user-data/outputs/NOME.xml --verifica` e correggi finché non passa.
4. Presenta l'XML (e la specifica, se l'utente vuole rivederla). Nel messaggio in chat: le **note per il docente** (errori inseriti con il messaggio che li rivela, varianti e casi limite dei test), il promemoria di aprire la domanda importata e salvarla con *Validate on save*, ciò che non hai potuto verificare.

Se l'utente vuole il codice da incollare a mano invece dell'XML, consegna gli stessi contenuti in un file Markdown, una sezione per campo.

## Le tipologie

### Debugging con messaggi

Lo studente trova la pagina con 3 (al massimo 4) errori di categorie diverse, che la **fermano** con un messaggio: lo legge, capisce in quale fase si è fermata, corregge, riprova. Gli errori emergono **uno alla volta** e ognuno è legato a un concetto della lezione (nomi di tabelle o colonne, apici, `$_GET`/`$_POST`, variabile sbagliata, colonne e valori di una INSERT, chiave duplicata o esterna). Con il prototipo sqlite i messaggi sono quelli veri di SQLite (`prototipo-sqlite.md`, sezione 5): riportali così nelle note. Un errore senza messaggio (il `while` mancante) può affiancarli.

### Debugging silenzioso

La pagina gira ma mostra la cosa sbagliata: `>` invece di `>=`, `ORDER BY` mancante o al contrario, colonna sbagliata stampata, `name` del form diverso dalla chiave in `$_GET`. Con il prototipo sqlite basta che il database renda visibile ogni errore; con il mock servono i risultati calcolati (`fakedb-api.md`). Nel testo indica quanti errori ci sono e invita a confrontare l'output riga per riga.

### Scrittura guidata e completa

Lo studente scrive la pagina da uno scheletro (commenti delle cinque fasi) o da zero (preload vuoto).

- **Consegna precisa** su ciò che il correttore confronta: struttura HTML esatta dell'output, testo dei messaggi, colonne e ordinamento. Nomi delle variabili e stile restano liberi.
- **Output normalizzato** in testa al campo Test (`fakedb-api.md`, «Output normalizzato»): spazi e a capo dello studente non contano; l'output atteso va scritto in forma canonica.
- Con il prototipo sqlite qualsiasi query equivalente funziona: non servono chiavi tolleranti.
- 3 o 4 test con dati del form diversi, almeno un caso con risultato vuoto o un vincolo violato; valuta un test `HIDE` e `allornothing: 0`.
- Per una INSERT, mostra dopo lo script l'ultima riga della tabella con `FakeDB::rows` (`prototipo-sqlite.md`, sezione 6).

### Sostegno decrescente

In una sequenza, riduci le indicazioni nel testo: prima quanti errori e in quale fase, poi solo quanti, poi nulla.

## Scrivere i test

- Ogni test chiama `FakeDB::configure([...])` con `user`, `password`, `database`; con il prototipo sqlite il database allegato viene copiato da solo.
- I dati del form si simulano con `$_GET = [...]` o `$_POST = [...]`; le variabili di appoggio iniziano con `$__`.
- Ogni test ha una `descrizione` breve: lo studente vede quella, non il codice del test.
- Gli output con l'HTML della soluzione vanno controllati a mano; le righe con `prova_query.py`.

## Verifica prima di consegnare

1. `crea_xml.py --verifica` controlla la specifica, l'HTML e i database; se PHP e sqlite3 ci sono, esegue la soluzione su ogni test. Dove manca il client `sqlite3` (nell'ambiente di Claude), `sqlite3_cli.py` di `materiali-moodle` (pagina della dashboard) lo sostituisce: mettilo nel PATH come comando `sqlite3`.
2. Se non ci sono, calcola le righe con `prova_query.py` e ripercorri a mano la soluzione: formato dei numeri (12, 9.5), ordine delle righe, a capo o forma canonica, testo dei messaggi.
3. Nel debugging, per ogni errore controlla quale messaggio produce e che gli errori emergano nell'ordine voluto.

Se non hai potuto eseguire il codice, dillo all'utente.

## Limiti da tenere presenti

- **sqlite**: messaggi in inglese di SQLite, decimali come 12 e 9.5, confronto tra testi che distingue le maiuscole, niente funzioni di data di MySQL (`compatibilita.md`). Il disclaimer avvisa solo in generale che comportamento e messaggi possono essere diversi: se una consegna risente di una di queste differenze (prezzi citati nel testo, ricerca di un testo con maiuscole diverse, un messaggio d'errore da riconoscere), dillo nel testo della domanda.
- **mock**: confronta il testo delle query, quindi le query equivalenti scritte in altro modo non vengono riconosciute.
- **Entrambi**: niente prepared statements, transazioni, query multiple; avvisi ed errori fatali di PHP compaiono a seconda della configurazione di Jobe e non vanno mai nell'output atteso; l'estensione mysqli non deve essere caricata su Jobe.