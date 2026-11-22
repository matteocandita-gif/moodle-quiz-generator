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

## Sito PHP con l'editor (tipologia `sito_php`, prototipo `php_sito`)

Lo studente scrive nell'**editor del sito** (interfaccia `html_sito`, la stessa del «Sito con l'editor», `tracce-html.md`) pagine HTML e PHP: tipicamente la pagina con il modulo e la pagina PHP che riceve i dati, oppure una pagina con link `?id=…` e la pagina che li legge con `$_GET`. Nell'anteprima le pagine HTML si vedono e i moduli si possono inviare: il browser controlla i campi (`required`, `min`, `type="email"`…) e l'anteprima mostra la pagina dell'`action` con i dati che riceverebbe, con il metodo e i `name`; le pagine PHP invece non si eseguono nell'anteprima, le esegue il prototipo quando lo studente preme Controlla. Il prototipo `php_sito` ricrea il sito ed esegue davvero le pagine PHP con `php` su Jobe (errori e avvisi visibili con la pagina e la riga, 5 secondi al massimo, nessun file fuori dal sito). Per ora senza database e senza sessioni, cookie e reindirizzamenti.

- `traccia`: estesa come le altre; le pagine da scrivere con i loro nomi, il modulo (campi e `name`, che i test usano, e il metodo), che cosa deve stampare la pagina PHP nei vari casi. Nessun campo Cloze né opzione.
- `coderunner` («Soluzione e test»): lo stesso formato del «Sito con l'editor» (`tracce-html.md`): `=== options` (`pagina`, anche `index.php`; `controllo`, `immagini`, `aiuti`, `file_pc`, `tollerante`), il sito di riferimento con `=== file PERCORSO`, e per ogni controllo `=== test PESO` con `=== extra`. Oltre a tutte le funzioni dell'HTML, i test hanno quelle delle pagine PHP; ogni richiesta si esegue anche sulla soluzione e si confrontano le uscite (spazi e a capo non contano):

| Test | Che cosa controlla |
|---|---|
| `stessa_uscita("pagine/conferma.php", post={"nome": "Mario"})` | la pagina, eseguita con quei dati (`get=` o `post=`), stampa la stessa cosa della soluzione |
| `stesso_testo("elenco.php", get={"genere": "giallo"})` | come sopra, ma solo il testo visibile: i tag possono essere diversi |
| `invia("index.html", {"nome": "Mario", "eta": "17"})` | compila il modulo dello studente come il browser, lo invia con il suo `method` al suo `action` e confronta l'uscita con la soluzione: trova i `name` diversi tra modulo e PHP, GET al posto di POST, `action` sbagliati |
| `invia("index.html", {"nome": "Mario", "eta": "17"}, cerca=["Mario", "minorenne"])` | con `cerca=` (un testo o una lista; vale anche in `stessa_uscita` e `stesso_testo`) basta che la pagina di arrivo mostri quei dati, come la soluzione: maiuscole, spazi e punteggiatura non contano e il resto del testo è libero |
| `modulo("pagine/conferma.php", "post", ["nome", "eta"])` | il modulo invia a quella pagina, con quel metodo, e ha i campi con quei `name` (ogni argomento si può omettere) |
| `php_senza_errori("conferma.php", post={...})` | la pagina, con quei dati, non stampa errori né avvisi di PHP |
| `usa_uscita("elenco.php", get={...})` / `usa_invio("index.html", {...})` | i controlli che seguono nello stesso test (`almeno`, `testo`, `contiene("Ciao Mario")`…) guardano quello che la pagina stampa |

- **I casi dei test**: come nelle altre domande PHP, dati diversi che portano a rami diversi (un minorenne e un maggiorenne, un campo vuoto), così lo studente non può adattarsi a un solo caso; `invia` per il percorso completo dal modulo alla pagina PHP, `stessa_uscita` per provare la pagina PHP anche con dati che il modulo non permetterebbe.
- La parte 2 esegue ogni test sulla soluzione e si ferma se un controllo non passa: serve `php` sul computer che genera il quiz.

### Controllo tollerante (`tollerante: sì`)

Predefinito nelle esercitazioni (`tollerante: no` per toglierlo), spento nelle verifiche (`tollerante: sì` per accenderlo): serve perché gli studenti non perdano tempo a ricopiare esattamente nomi e frasi della traccia. Con il controllo tollerante:

- **le pagine** si trovano anche con maiuscole diverse, in un'altra cartella del sito o seguendo l'`action` del modulo e i link dello studente: se la traccia dice `pagine/conferma.php` e lo studente ha scritto `php/iscrizione.php`, con il suo modulo che porta lì, va bene;
- **i campi del modulo** si abbinano a quelli della traccia per `name`, poi per etichetta (`<label>`), poi per posizione, e si inviano con i `name` dello studente: conta che il suo modulo e la sua pagina PHP funzionino insieme. Anche i test che aprono direttamente la pagina PHP (`stessa_uscita`, `php_senza_errori`, `usa_uscita`…) le mandano i dati con i nomi che lo studente usa nel modulo, o nei link `?…`, che portano a quella pagina. Per menù, caselle e pulsanti di opzione si sceglie la sua opzione corrispondente;
- **l'uscita** si confronta parola per parola (tag, punteggiatura e maiuscole non contano); con `cerca=` solo sui dati indicati. Nelle esercitazioni conviene scrivere i test di `invia` con `cerca=`, con i dati che contano (il nome inviato, la categoria calcolata): così lo studente scrive le frasi come vuole;
- gli avvisi `Deprecated` e `Notice` non contano; `Warning` ed errori sì. Il `method` resta controllato da `modulo(…)`.

Con il controllo esatto (`tollerante: no`) i nomi di pagine e campi devono essere quelli della traccia e l'uscita quella della soluzione (spazi e a capo esclusi).

## Consegna PHP (.zip) (tipologia `consegna_php`, prototipo `php_sito`)

Lo studente fa il sito con **XAMPP** (o un altro editor sul suo computer), comprime la cartella e carica lo `.zip` nella domanda, come nella consegna con controllo automatico dell'HTML (`tracce-consegna.md`). Lo stesso prototipo `php_sito` ricrea il sito dallo zip (con le pagine nella cartella principale o dentro una cartella) ed esegue i controlli come nel sito PHP con l'editor; niente editor nella domanda, al suo posto un promemoria. Solo nelle esercitazioni (dentro SEB non si caricano file del computer).

- `traccia`: come nel sito PHP con l'editor, più il nome dello `.zip` da caricare.
- `coderunner`: lo stesso formato, con `=== options` `nome: torneo.zip` (obbligatorio: minuscole, numeri, `-` `_`, estensione `.zip`), `pagina`, `controllo`, `tollerante`; niente `immagini`, `aiuti`, `file_pc` né `=== immagine` (le immagini sono nello zip). Il sito di riferimento con `=== file` serve ai controlli; nelle esercitazioni la parte 2 lo mette anche nel feedback generale, file per file, così dopo la consegna lo studente vede una soluzione.
- Le risposte non si rieseguono nella correzione delle verifiche: lo `.zip` non è nell'export di Moodle.

Lo stesso lavoro si può consegnare anche con l'editor: nel «Sito PHP con l'editor» con `file_pc: sì` lo studente importa lo `.zip` con «Importa» e preme Verifica.

## In più, scrivendo le tracce

- Nel codice che scriviamo noi le variabili sono sempre integrate nelle stringhe; lo studente può concatenarle, e non è un errore.
- 3 o 4 test, almeno uno con risultato vuoto o errore.
- `=== options` con `allornothing: 0` nella scrittura completa.
- Gli output li calcola la parte 2: prima di scrivere, verifica la soluzione e il primo errore del codice di partenza.
