# Formato di consegna: dalla dashboard a Moodle

La parte 2 non riceve un file a parte: legge il database della dashboard «Bozze dei quiz». Tutto quello che va in Moodle è scritto nelle righe con le convenzioni qui sotto, e `da_dashboard.py` lo trasforma senza ritrascrizioni:

```
ArtifactData get   quiz <id>          out_dir=EXPORT     (quiz)
ArtifactData list  quiz/<id>/domande  out_dir=EXPORT     (righe)
python3 genera_quiz.py EXPORT <id> USCITA --nome="<nome del file>" [--varianti=a] [--immagini=CARTELLA]
```

`--varianti=a` (o `a,b`) converte solo le varianti indicate delle verifiche ripetibili: si usa quando la variante a è completa e le altre hanno solo la sintesi (si fanno dopo, quando l'utente le chiede). Le righe senza tag restano tutte; lo script elenca le righe lasciate fuori.

`genera_quiz.py` esegue in fila, fermandosi al primo errore:
1. `da_dashboard.py` → `specifica.txt`, `specifica-js.txt` (righe CodeRunner JavaScript), `specifica-sql.txt` (righe CodeRunner SQL, con i database del quiz), `specifica-php.txt` (righe CodeRunner PHP, con i database del quiz), `impaginazione.json`;
2. `crea_xml.py` → le domande non CodeRunner;
3. `crea_xml.py` di `domande-coderunner-js` → le domande CodeRunner JavaScript (gli output attesi li calcola Node);
   `crea_xml.py` di `domande-coderunner-sql` → le domande CodeRunner SQL (costruisce i file SQLite, calcola gli output e allega il database a ogni domanda);
   `php_attesi.py` e `crea_xml.py --verifica` di `domande-php-mysqli-mock` → le domande CodeRunner PHP (gli output attesi si calcolano eseguendo la soluzione con PHP e il template del prototipo; se manca il client `sqlite3` lo sostituisce `sqlite3_cli.py`);
   (esercizi HTML e CSS e corrispondenze li scrive direttamente `da_dashboard.py` in `domande-dirette.xml`);
4. `unisci_xml.py` → `<nome>.xml`;
5. `controlla_xml.py`;
6. `crea_mbz.py` → `<nome>.mbz`.

Tutti gli script stanno in `scripts/` di `materiali-moodle`; le cartelle `scripts/` di `domande-coderunner-js`, `domande-coderunner-sql` e `domande-php-mysqli-mock` le cerca da solo accanto a quella skill (o `--js=`, `--sql=`, `--php=CARTELLA`). Tutti i tipi di domanda del catalogo arrivano all'XML e all'`.mbz`.

Lo script si ferma con l'elenco delle righe che non rispettano le convenzioni; la dashboard segnala gli stessi problemi negli avvisi, già in parte 1. Le righe non approvate producono solo un avviso.

## Campi di una riga

| Campo | Va in Moodle | Contenuto |
|---|---|---|
| `traccia` | sì | quello che vede lo studente, in Markdown con le convenzioni sotto |
| `correzione` | sì | domande aperte: indicazioni per chi corregge (criteri, mezzo punto, soluzione); altre domande: feedback generale |
| `coderunner` | sì | solo domande CodeRunner: soluzione, codice di partenza e test (sotto) |
| `tag` | sì | solo verifiche ripetibili: il tag della posizione; le righe con lo stesso tag sono varianti (sotto) |
| `docente` | no | note interne: il ragionamento sulla domanda |
| `nota` | no | spiegazione di una modifica «da rivedere» |
| `sezione`, `pag`, `punti`, `pos`, `titolo`, `tipologia` | sì | sezione del quiz, pagina, punti nel quiz, nome della domanda, tipo Moodle |

Quiz: `database` (solo con domande SQL, vedi sotto); `lezione` e `argomento` danno la categoria («Lezione N - argomento») e i nomi («LN - pos - prefisso: titolo»); le verifiche non hanno un numero di lezione e `lezione` è il loro codice (`V5R`): categoria «V5R - argomento», nomi «V5R - pos - prefisso: titolo»; `tipoQuiz` sceglie le impostazioni dell'.mbz (V e VT: verifica, con il tempo del quiz; gli altri, compreso EDT: esercitazione). Facoltativi: `titoliSezioni` (titolo della sezione nel quiz, se diverso dal nome della sezione), `nomeQuiz`, `voto` (10), `sufficienza` (6).

## Convenzioni della traccia

- Markdown: paragrafi (ogni a capo dentro un paragrafo resta un a capo, `<br>`; la riga vuota apre un nuovo paragrafo: così lo schema relazionale si scrive una relazione per riga, senza righe vuote in mezzo), `**grassetto**`, `*corsivo*`, `__sottolineato__` (la chiave primaria negli schemi delle tabelle), `` `codice` ``, blocchi di codice tra tre apici inversi con il linguaggio (```` ```html ````; con ```` ```html anteprima ```` accanto al codice compare il risultato nel browser, l'HTML stesso interpretato: solo per snippet brevi di tag della lezione, senza script né stili), elenchi `-` e `1.`, tabelle con `|`, titoli `#` e `##`.
- **Immagini**: `![testo alternativo](nome.png)`, anche in una riga a sé o dentro un riquadro, solo nel testo della domanda o della pagina (non nelle opzioni, nei feedback, nella correzione né nei campi Cloze). Si scrive solo il nome del file, senza cartella: le immagini di un quiz stanno tutte in una cartella, indicata nelle `note` del quiz e passata a `genera_quiz.py --immagini=CARTELLA`. Il testo alternativo descrive l'immagine. `da_dashboard.py` la scrive come `<img src="@@PLUGINFILE@@/nome.png">` (larghezza al massimo quella della pagina), `allega_immagini.py` incorpora il file nell'XML e `crea_mbz.py` lo mette nel backup. Nella dashboard l'immagine compare come testo. Per le domande sui diagrammi si disegnano immagini nuove nello stile delle figure del libro, con contesti diversi da quelli delle pagine.
- **Pagine** (tipologie della famiglia «Pagine»): scritte già nella forma finale, in seconda persona plurale. `#` è il titolo della pagina. Riquadri:
  ```
  :::giallo Esempio svolto
  Testo del riquadro, anche con codice.
  :::
  ```
  Colori: blu (definizioni), giallo (esempi svolti), verde, arancio (N.B.), rosso.
- **Scelte** (risposta multipla, vero/falso, risposta breve): un gruppo di righe, una per opzione.
  ```
  (x) risposta giusta
      > feedback della risposta
  ( ) risposta sbagliata
      > feedback
  ```
  Più risposte giuste: `[x]` e `[ ]`; le giuste si dividono il 100% e le sbagliate senza percentuale si dividono una penalità del −100% (con tre sbagliate −33.33333 ciascuna), così chi spunta tutto prende 0. Percentuali esplicite: `[x 50%]`, penalità `[ -50%]`. Le penalità devono sommare −100%: se ne scrivi qualcuna a mano, le sbagliate senza percentuale si dividono quello che manca (lo script si ferma se la somma non torna). La traccia dice «Seleziona tutte le risposte corrette» (l'istruzione standard di Moodle è nascosta). Vero/falso: due opzioni «Vero» e «Falso». Risposta breve: una sola `(x)`, la risposta giusta (si usa solo quando la risposta è una e senza varianti); gli errori prevedibili si scrivono come `( )` con il loro feedback. Non si usa `( ) *` («qualsiasi altra risposta»): nella dashboard sembra un'opzione e non si capisce (lo script la accetta ancora, per le domande vecchie).
- **Corrispondenza**: una riga per coppia, `elemento <-> corrispondenza`; una riga che comincia con `<->`, senza elemento, è una risposta in più che non corrisponde a niente. Il testo fuori dalle righe `<->` è la consegna.
  ```
  `color` <-> Cambia il colore del testo
  `font-size` <-> Cambia la dimensione del carattere
  `text-align` <-> Sposta il testo a sinistra, al centro o a destra
  <-> Cambia la distanza tra una riga e l'altra
  ```
  Almeno 2 elementi e almeno 3 corrispondenze in tutto (regola di Moodle). A sinistra il testo in linea (`` `codice` ``, grassetto); a destra solo testo semplice, perché compare in un menù a tendina. Le corrispondenze si mescolano; la `correzione` diventa il feedback generale; i feedback standard («Risposta corretta.» …) e il numero di risposte giuste sono quelli delle domande dell'utente.
- **Campi Cloze**: nella sintassi di Moodle, dentro il testo o dentro i blocchi di codice: `<{1:SHORTANSWER:=h1}>`, `{1:MULTICHOICE_S:=giusta#Feedback~sbagliata#Feedback}`, `{1:NUMERICAL:=4:0#Feedback}`. Si escapano solo `}` `#` `~`; nei campi a risposta niente tag (il campo contiene il nome del tag, parentesi e barra stanno nel codice). Il peso dei campi è il numero prima dei due punti; nel quiz contano i punti della riga.

## Domande CodeRunner JavaScript

La `traccia` è il testo della domanda, con le stesse convenzioni delle altre ma **senza campi Cloze né opzioni**; gli output d'esempio vanno in blocchi ```` ```semplice ````. La `correzione`, se c'è, diventa il feedback generale. Soluzione e test stanno nel campo `coderunner` («Soluzione e test» nella dashboard), a sezioni `=== nome` come nella specifica di `domande-coderunner-js`:

| Sezione | Contenuto |
|---|---|
| `=== answer` | obbligatoria: la soluzione di riferimento (nel gapfiller una riga per spazio, in ordine) |
| `=== test` | almeno una, meglio tre o più: il codice del test, che comincia con un commento che dice che cosa prova (`// 65 anni: ridotto (caso limite)`); `=== test HIDE` per un test nascosto |
| `=== stdin` | dopo un `=== test`: le risposte ai `prompt`, una per riga |
| `=== extra`, `=== expected` | dopo un `=== test`, solo se servono (di norma l'output atteso lo calcola Node) |
| `=== code` | solo gapfiller: il codice con gli spazi `{[larghezza]}` o `{[predefinita-massima]}` |
| `=== preload` | codice di partenza nella casella (debug: il codice con l'errore; codice parziale: la parte già scritta, per esempio la funzione da usare) |
| `=== options` | opzioni della specifica, una per riga, per esempio `esempi: tutti` (`defaultgrade` viene dai punti della riga) |

Il dettaglio delle sezioni e delle opzioni è in `references/formato-specifica.md` di `domande-coderunner-js`.

Il prototipo è «Javascript (con gapfiller)» se la tipologia è `compl_eseguito` o c'è `=== code`, altrimenti «Javascript (con prompt)». Nei test di un programma con `prompt` il codice del test è spesso solo il commento: i valori stanno in `=== stdin`. Due test con lo stesso output non distinguono nulla: scegli dati che diano output diversi. La dashboard mostra il codice da completare o di partenza nel foglio dello studente e soluzione e test nel riquadro del docente, e segnala negli avvisi le sezioni mancanti, gli spazi che non corrispondono alle risposte, `alert` o `document` nella soluzione.

## Domande CodeRunner SQL

Prototipo `sql_salvemini` (SQLite 3.46 su Jobe). Tipologie `query`, `create_tabelle`, `query_due_passi`, `vincoli`, `campo_prova`; `debug_msg`, `debug_silenzioso` e `scrittura_scheletro` sono SQL quando i test cominciano con `--` o con `[[struttura …]]` (oppure con una sezione `=== linguaggio` che contiene `sql`).

**Il database** sta nel quiz, non nella riga: campo `database` del documento del quiz, un elenco di `{nome, sql}` con lo script come in phpMyAdmin (CREATE TABLE e INSERT). Nella dashboard si scrive nel riquadro «Database del quiz» della scaletta, che mostra tabelle, righe e quali domande lo usano. Il nome (senza spazi) diventa il nome del file allegato (`nome.db`, `nome_struttura.db`, `nome_vuoto.db`). Con un solo database le domande lo usano tutte; con più database ogni riga dice quale con `database: nome` in `=== options`.

**La traccia** è il testo della domanda (senza campi Cloze né opzioni), con lo schema delle tabelle coinvolte: `Libri (__ISBN__, Titolo, Autore, Prezzo, IdEditore*)`. Le regole della skill `domande-coderunner-sql` valgono già qui: tipi e vincoli esatti nelle CREATE, niente costrutti MySQL che SQLite rifiuta. Schema fisso delle query nelle verifiche:

```
Il database contiene:
Istruttori (__IdIstruttore__, Nome, Cognome, ...)
Corsi (__IdCorso__, Nome, Livello, IdIstruttore*)

Breve descrizione, solo di quello che non è ovvio dai nomi (in ogni domanda, anche se il database si ripete).

**Scrivere la query opportuna per ottenere i seguenti dati:**

La richiesta, in un paragrafo a sé.
```

- **Colonne**: nella traccia non serve l'elenco delle colonne da mostrare: lo studente le vede nell'output del primo test (l'esempio di CodeRunner). La soluzione le fissa (stesse colonne, stesso ordine).
- **Ordinamento**: l'output si confronta riga per riga nell'ordine, quindi la soluzione ha sempre un `ORDER BY`, ma la richiesta di ordinare si scrive solo dove fa parte del problema (non in tutte le domande). Se la traccia non lo chiede, lo studente vede l'ordine dal primo test. Le chiavi dell'ordinamento devono dare **un ordine unico, senza pari merito** sui dati del database e delle prove nascoste: se due righe sono alla pari e la traccia non dice come sciogliere il pareggio, un ordine diverso ma giusto risulta sbagliato. Si risolve cambiando i dati (un UPDATE nello script del quiz), scegliendo una chiave unica o scrivendo il secondo criterio nella traccia; se si lascia apposta, va detto nella `correzione` (si corregge a mano).
- **Prove nascoste** con dati in più: `=== test HIDE` seguito da `=== extra` con le INSERT (o gli UPDATE) che aggiungono i casi limite (pari merito, NULL, righe senza collegamenti, confini delle date) prima di eseguire la query.
- **Correzioni dei dati del quiz**: se un controllo trova un problema nei dati (pari merito, un caso limite che manca) si possono aggiungere in fondo allo script del database del quiz righe `UPDATE` o `INSERT`, invece di rigenerare il database; la `docente` della riga dice perché.

**Soluzione e test** («Soluzione e test», sezioni della specifica di `domande-coderunner-sql`):

| Sezione | Contenuto |
|---|---|
| `=== options` | facoltativa: `database: nome`, `dati: pieno | struttura | vuoto` (se manca la dedurrà lo script: CREATE → vuoto, solo INSERT → struttura, altrimenti pieno), `precheck: 1`, `foreign_keys: 0`, `allornothing: 0`, `grader: RegexGrader`, `hidecheck: 1` |
| `=== preload` | codice di partenza nella casella (debug) |
| `=== answer` | obbligatoria: la soluzione |
| `=== test` / `=== test HIDE` | obbligatoria: comincia con un commento `-- …` che dice che cosa si guarda (`-- il risultato della tua query`, poi l'eventuale SELECT sullo stato finale) oppure è `[[struttura Tabella]]` per le CREATE |
| `=== extra`, `=== expected` | dopo un test, solo se servono (l'output atteso lo calcola lo script; `expected` solo con RegexGrader) |

Gli output non si scrivono: li calcola la parte 2 eseguendo la soluzione sul database. Le tipologie, il database giusto per ognuna e la forma dei test sono in `references/tipologie.md` di `domande-coderunner-sql`. La dashboard mostra al docente database, dati e test, e segnala sezioni non previste, database inesistenti, SELECT senza ORDER BY, costrutti MySQL e CREATE controllate con `.schema`.

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

## Esercizi HTML e CSS (CodeRunner senza test)

Tipologie `libero_html` e `libero_css`: esercizi liberi a correzione manuale con l'editor di CodeRunner. L'HTML usa il prototipo scelto nei dati del quiz (campo `prototipoHtml`, «Esercizi HTML»): **con anteprima** il prototipo `php_con_test` del Moodle della scuola, che ha lo **scratchpad** (l'area di prova sotto la risposta mostra la pagina interpretata, come nel browser); **senza anteprima** (`prototipoHtml: html`) il prototipo `html`, in cui il campo serve solo a incollare il codice scritto nell'editor e provato aprendo il file nel browser: si sceglie quando l'esercizio deve far lavorare con editor e browser, e la traccia lo dice nelle indicazioni di svolgimento; il CSS usa il prototipo `css`. Sostituiscono la domanda aperta negli esercizi di HTML e CSS; `esercizio_libero` resta per le risposte senza codice. Negli esercizi HTML la consegna può chiedere anche CSS nel documento o in linea; nel prototipo `css` la risposta è solo il foglio di stile (la pagina HTML, se serve, sta nella traccia).

- `traccia`: la consegna, come per gli altri esercizi. Lo script aggiunge in fondo il riquadro arancio «Attenzione al controllo automatico» (il pulsante salva il codice, non lo corregge; nell'HTML con anteprima spiega anche l'area di prova), salvo che la traccia ne parli già.
- `correzione`: criteri e punti; diventa il **feedback generale** (lo studente lo vede quando le opzioni di revisione lo permettono: subito nelle esercitazioni, alla restituzione nelle verifiche).
- `coderunner` («Soluzione e test»): `=== answer` obbligatoria, la soluzione di riferimento (Moodle la mostra come risposta giusta); `=== preload` facoltativa, il codice di partenza nella casella; `=== options` facoltativa, solo `righe: N` e `colonne: N` della casella (predefinite 18 e 100). Nessun test.

In Moodle la domanda ha un solo test fittizio che si aspetta «codice salvato!» (`php_con_test`) o «codice salvato» (`html` e `css`): al controllo dà pieni punti, e il punteggio vero lo mette il docente correggendo a mano. Con `php_con_test` (non con `html`) risposta e codice di partenza sono nel formato JSON dello scratchpad (`{"answer_code":[…],"test_code":[""],"show_hide":[""],"prefix_ans":["1"]}`): lo scrive `da_dashboard.py`, nella dashboard si scrive solo il codice.

## Consegna di un file

Tipologia `consegna_file`: domanda aperta (essay) senza campo di testo, con un solo file da caricare, obbligatorio, di tipo `.html`, `.htm` o `.css` (le impostazioni le mette `da_dashboard.py`). `traccia`: il file da preparare, con il nome e i requisiti, e come caricarlo; `correzione`: i criteri per chi corregge (in Moodle le informazioni per chi corregge). Si usa per verificare che lo studente abbia creato davvero un file, per esempio la pagina dell'esempio svolto.

## Verifiche ripetibili (domande casuali per tag)

Le varianti di una posizione sono righe con lo stesso `tag` (un tag per posizione, unico nel sito, per esempio `rjs4-T1-assegnamento`; niente spazi) e la posizione con la lettera della variante (`T1a`, `T1b`, …). Le varianti hanno **stessi punti, pagina e sezione** (errore se no), di norma la stessa tipologia e gli stessi minuti, e stanno di seguito nella scaletta. Le pagine (istruzioni) non hanno tag e restano fisse. Nella dashboard le varianti di una posizione si vedono come una riga sola (dettaglio in `dashboard.md`).

In parte 2 tutte le varianti vanno nella banca del quiz con il loro tag (`genera_quiz.py` aggiunge i `<tags>` all'XML); nel `.mbz` ogni posizione diventa una domanda casuale che pesca dalla categoria della lezione una domanda con quel tag, con i punti della posizione. Nel backup gli id dei tag sono inventati (da 9900001): al ripristino Moodle ricrea i tag per nome e aggiorna il filtro. Nella dashboard e nei totali ogni posizione conta una volta; le varianti hanno lo stesso numero di domanda.

## Leggere un backup (.mbz)

`leggi_mbz.py BACKUP.mbz --quiz` mostra la struttura di ogni quiz del backup (di un corso o di una sola attività): tempo, punteggio, sezioni, e per ogni slot pagina, punti e domanda (nome, versione, banca) oppure, per le domande casuali, i tag e la categoria da cui pesca e le domande che corrispondono. Serve per controllare un quiz modificato in Moodle (per esempio la copia PDP): `--domande TESTO` mostra il testo delle domande delle categorie che contengono TESTO (ultima versione). Senza opzioni: sezioni, attività e banche.

`importa_mbz.py` fa il percorso inverso di `da_dashboard.py`: dal backup di un quiz ricava quiz e righe della dashboard, con traccia, correzione e «Soluzione e test» in queste convenzioni (HTML → Markdown, opzioni, campi Cloze, corrispondenze, CodeRunner JavaScript, SQL, PHP, HTML e CSS, database SQLite allegati → script del quiz, domande casuali → varianti con il tag). Con `--confronta` confronta il backup con un quiz della dashboard e riporta le modifiche fatte in Moodle. Uso e casi in `dashboard.md` («Importare un quiz da un backup»). Provato: andata e ritorno della V5R (dashboard → .mbz → dashboard) senza differenze; un quiz vecchio di 30 domande importato e rigenerato con gli stessi output attesi delle 19 CodeRunner SQL. Non torna uguale: le immagini (`importa_mbz.py` non le riporta nella traccia come `![…](…)`), i colori del testo, gli a capo dentro le opzioni (diventano « / »), il feedback generale delle domande aperte (diventa la correzione).

## Prefissi dei nomi

Dal catalogo. La pagina del blocco usa «Spiegazione» nelle esercitazioni con spiegazione e «Ripasso» nel ripasso teorico (RT) e nella complessiva di ripasso (ER).

## Non ancora gestito

Le domande PHP con il prototipo `php_mysqli_mock` (mappa delle query): si fanno con la skill `domande-php-mysqli-mock` e si uniscono gli XML.
