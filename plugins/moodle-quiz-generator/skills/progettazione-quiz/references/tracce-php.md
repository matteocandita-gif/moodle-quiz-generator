# Tracce delle domande CodeRunner PHP

Da leggere quando il quiz ha domande CodeRunner PHP. Fa parte delle regole sulle tracce di `progettazione-quiz` (`SKILL.md`, «Le tracce»): le regole generali (tracce estese, convenzioni, feedback, correzione e note interne) restano lì e valgono anche qui. Le convenzioni generali della traccia (riquadri, scelte, campi Cloze, immagini) sono in `formato-consegna.md`; il formato del campo «Soluzione e test» di queste domande è qui sotto.

## Domande CodeRunner PHP

Prototipo `php_mysqli_sqlite`: il PHP dello studente gira davvero e le query vanno su SQLite, sul database del quiz (lo stesso campo `database` delle SQL, di solito dal catalogo «Database didattici»). Tipologia `pagina_php`; `debug_msg`, `debug_silenzioso` e `scrittura_scheletro` sono PHP quando la soluzione inizia con `<?php` o i test usano `$_GET`, `$_POST` o `FakeDB`.

**La traccia** è la consegna, estesa come le altre, con l'output HTML atteso in un blocco ```` ```html ````; il nome del database da usare (in `$nomedb`, la variabile passata a `mysqli_connect`) è il nome del database del quiz. Il riquadro «N.B. questa è una simulazione» lo aggiunge la parte 2 in fondo al testo. Le convenzioni del codice (cinque fasi commentate, parametri di connessione in `$host`, `$username`, `$password`, `$nomedb`, `or die` con i messaggi della scuola, `mysqli_fetch_array`) sono quelle di `domande-php-mysqli-mock`.

**Soluzione e test**:

| Sezione | Contenuto |
|---|---|
| `=== options` | facoltativa: `allornothing: 0` (punteggio parziale), `normalizza: 0` (confronta l'output così com'è; di norma spazi e a capo non contano), `database: nome` con più database, `hidecheck`, `precheck` |
| `=== preload` | codice di partenza (debug, scheletro); inizia con `<?php` |
| `=== answer` | obbligatoria: la soluzione, inizia con `<?php` |
| `=== test` / `=== test HIDE` | i dati del form della prova (`$_GET = ['matricola' => '1002'];`), più eventualmente una `register_shutdown_function` che mostra la tabella dopo un'INSERT con `FakeDB::rows`; `FakeDB::configure` e la normalizzazione si aggiungono da soli |
| `=== descrizione` | dopo ogni test: la frase che lo studente vede al posto del codice della prova («Matricola 1004: nessun prestito aperto») |
| `=== expected` | facoltativa: di norma l'output atteso lo calcola la parte 2 eseguendo la soluzione |

La parte 2 stampa anche che cosa vede lo studente eseguendo il codice di partenza (`PRELOAD`): nei debug deve essere il primo errore voluto. I messaggi di SQLite sono quelli della tabella di `references/prototipo-sqlite.md` di `domande-php-mysqli-mock` (verificati su Jobe); in locale li produce la libreria SQLite di Python, quindi il controllo definitivo resta il bulk tester.

## In più, scrivendo le tracce

- Nel codice che scriviamo noi le variabili sono sempre integrate nelle stringhe; lo studente può concatenarle, e non è un errore.
- 3 o 4 test, almeno uno con risultato vuoto o errore.
- `=== options` con `allornothing: 0` nella scrittura completa.
- Gli output li calcola la parte 2: prima di scrivere, verifica la soluzione e il primo errore del codice di partenza.
