# Changelog

Le novità di ogni versione di «Moodle: quiz generator». Le righe segnate **Dashboard** cambiano la pagina «Bozze dei quiz», quelle segnate **Editor mappe** la pagina «Mappe dei prerequisiti»: Claude propone di aggiornarle, e quiz e mappe salvati restano.

## 0.6.0 — 24/10/2026

Nuova skill **correzione-verifiche**: correzione di una verifica già svolta, dall'export «Risposte» di Moodle anonimizzato.

- **Nuova correzione**, nella dashboard: si trascina l'Excel «Risposte» di Moodle così com'è, con i nomi; la pagina lo legge nel browser (senza librerie esterne), crea le sigle, scarta email e username, cancella i nomi anche dentro le risposte e salva solo dati anonimi. Facoltativa la tabella Risposte incollata dal browser, abbinata per nome completo, per i tag HTML. Poi in chat «correggi la verifica …» (`leggi_export.py` legge anche una verifica della dashboard; `prepara_revisione.py --esistente`).
- In alternativa, indicazioni per il docente su come preparare l'export a mano: risposte dettagliate in Excel, colonne con email e username eliminate, cognome e nome ridotti alle prime due lettere con `=STRINGA.ESTRAI(A2;1;2)` e incollati come valori (anche nella guida).
- `leggi_export.py` legge l'export (Excel, CSV; una sigla «NA» resta una sigla e non diventa un dato mancante), si ferma se ci sono nomi completi o colonne con email e username e abbina ogni domanda alla riga della dashboard con la traccia più simile.
- `esegui_risposte.py` riesegue le risposte SQL, PHP (`php_mysqli_sqlite`) e JavaScript con prompt con tutti i test, nascosti compresi, e stima il punteggio automatico di Moodle (tutto o niente, oppure frazione dei test con `allornothing: 0`).
- La correzione si fa domanda per domanda, con la griglia della riga e la griglia generale (100 / 80 / 60 / 40%) e i casi già decisi: date confrontate con un numero, pari merito, JOIN interna con IS NULL, GROUP BY sul nome, refusi. Commenti brevi solo dove il punteggio non è pieno.
- Dashboard **«Correzione verifiche»**, privata, una per tutte le verifiche: elenco dalla più recente con l'avanzamento; archiviare (reversibile) ed eliminare (con conferma nella pagina) dal riepilogo della verifica. Dentro una verifica tre viste: **per domanda** (studenti in ordine di cognome, come in Valutazione manuale), **per studente** (tutte le domande, totale e voto) e **riepilogo voti**. Punteggio e commento modificabili, «Copia commento per Moodle» con la frase sull'IA in corsivo, righe da modificare in Moodle evidenziate, studenti in ordine di cognome crescente o decrescente.
- **Importa da Moodle**, nella dashboard: si incolla la tabella «Risposte» copiata dal browser, che ha il codice HTML completo; i nomi diventano le sigle dell'export nel browser dell'utente e non si salvano, si salvano solo le risposte delle domande scelte. La copia dal browser perde a capo e rientri: la pagina li recupera dall'export (controllato su 36 risposte HTML e PHP, nessun carattere perso), e avvisa se una sigla resta senza tentativo.
- **Varianti** (domande casuali per tag): `leggi_export.py` abbina ogni studente alla variante che gli è capitata, `esegui_risposte.py` esegue la sua risposta con i test di quella variante e la pagina mostra la variante accanto alla risposta. Provato su una verifica JavaScript con tre varianti per domanda.
- `riepilogo.py` rilegge il database di una verifica e calcola totali, voti e media, con le righe ancora da rivedere o da inserire in Moodle.

## 0.5.0 — 23/10/2026

Nuova skill **mappe-prerequisiti**: mappe dei prerequisiti (gerarchie di apprendimento) per l'autovalutazione degli studenti.

- Una mappa scompone un traguardo in competenze minime collegate da prerequisiti. In Moodle diventa un'attività Database: lo studente spunta le voci che sa fare e vede quelle che è pronto a imparare; il docente, nella vista elenco, vede il riepilogo della classe (quanti sanno fare ogni voce, chi è pronto, chi no) e la tabella degli studenti.
- **Editor mappe** 1.0.0: la pagina «Mappe dei prerequisiti», privata, per creare e correggere le mappe (voci, prerequisiti, «da saper scrivere» o «da saper leggere»), provarle con «Prova come studente» e scaricare il backup o il preset. Come la dashboard: mappe dalla più recente alla più vecchia, una mappa nuova creata in chat si apre da sola, archiviare ed eliminare nel riquadro in fondo.
- Spunte con i vincoli (attivi di default, si spengono mappa per mappa): una voce si spunta solo dopo i suoi prerequisiti, e togliendo una spunta si tolgono le voci che la richiedono.
- Backup `.mbz` di un'attività già impostata (approvazione richiesta, una scheda per studente, nessun gruppo), da Claude (`scripts/crea_mbz.js`, che controlla la mappa) o dall'editor. Per aggiornare un'attività già in uso si importa il preset: le spunte restano.
- Comando `installa-mappe`: installa o aggiorna l'editor.
- Sorgenti dell'editor in `sviluppo/mappe-prerequisiti`, con lo script che ricostruisce la pagina.

## 0.4.2 — 22/10/2026

- **Dashboard** 0.3.8: l'elenco dei quiz va dal più recente al più vecchio (data di creazione; i quiz senza data in fondo); quando compare un quiz nuovo, pronto, la pagina lo apre da sola nella scaletta (se si sta modificando qualcosa avvisa soltanto, e il quiz resta in cima all'elenco). Nel modulo «Nuovo quiz» un'esercitazione con spiegazione propone 105 minuti; la guida dei tipi dice «una lezione di due ore: 105 minuti».
- `progettazione-quiz`: il campo `creato` è obbligatorio anche per i quiz creati in chat, perché l'elenco si ordina con quello. Preset ED: una lezione di due ore ha 105 minuti disponibili, non 90 (con almeno 5 minuti di margine). Ogni blocco di un'ED chiude con almeno un esercizio libero, da scrivere da zero.
- `domande-coderunner-js`, regole sui test:
  - le funzioni da creare si controllano chiamandole nei test, anche dentro un programma (l'ultimo test, dopo il programma), con una «Nota bene» nella traccia;
  - una funzione predefinita vietata (`includes`, `indexOf`…) si controlla con un test che la disattiva su un solo array, non su tutti;
  - un test che fa qualcosa di non ovvio ha un commento che spiega a parole che cosa controlla e quale riga dell'output è il risultato;
  - la sequenza random predefinita va da 0.01 a 0.92: in un intervallo largo gli estremi non escono (0–100 non arriva a 100); per provarli serve `random:`.

## 0.4.1 — 18/10/2026

Skill **diagrammi-er**:

- **Attributo opzionale**: si scrive `Email (0,1)` nella descrizione; nel diagramma la cardinalità (0,1) sta sul gambetto (sotto per gli attributi ai fianchi, a destra per quelli sopra e sotto), nella documentazione «Opzionale» tra i vincoli, nello schema relazionale il vincolo «può essere NULL». Non vale per la chiave primaria.
- **Strumenti che non si usano**: niente associazioni ternarie né attributi multipli. Un legame tra tre entità diventa un'entità collegata alle tre con associazioni 1 a N (mai tre associazioni binarie); un attributo con più valori diventa un'entità a parte (lo script rifiuta una cardinalità diversa da (0,1) su un attributo). Le tracce da dare agli studenti evitano le realtà con legami tra tre entità, salvo un punto opzionale in un'esercitazione difficile.
- **Query SQL nella soluzione completa**: blocchi `query:` nella descrizione (la richiesta sulla riga, il codice sotto) e una parte «Query SQL» nell'HTML, nel Word e nel Markdown; la skill controlla prima che il modello permetta tutte le query e le prova su un piccolo database SQLite.
- **Più linee sullo stesso lato di un'entità**, per le entità collegate a molte altre: ogni linea parte di fronte al suo rombo, con un avviso se viene obliqua o troppo vicina a un'altra; `larghezza:` allarga il rettangolo quando servono più attacchi.
- Nella strategia «tutto su» gli attributi delle specializzazioni sono detti «opzionali», come nel libro.

`progettazione-quiz`: per le tracce e le domande di progettazione rimanda alle regole di `diagrammi-er`, anche quando la domanda non ha un diagramma.

## 0.4.0 — 17/10/2026

La skill **diagrammi-er** diventa la skill della progettazione: dalla stessa descrizione testuale (file `.er`) quattro moduli indipendenti, e si produce solo ciò che serve (per un quiz basta il diagramma).

- **Diagramma**: gerarchie ISA (linea a T con la freccia verso la generalizzazione e la classificazione tra parentesi); attributi delle associazioni anche ai lati del rombo; le posizioni sulla griglia servono solo al diagramma.
- **Schema relazionale** (`schema_relazionale.py`): le regole di traduzione del libro (1 a N, 1 a 1, N a N, entità deboli, ricorsive) e le tre strategie per le gerarchie (tutto su, tutto giù, lasciare tutto), con gli avvisi dove il libro le sconsiglia; formato del libro o delle tracce dei quiz. Nomi delle chiavi esterne con la regola dell'autore: mai un nome generico come Codice o Id ripetuto così com'è (Codice_compagnia, Codice_veicolo).
- **Documentazione** (`documentazione.py`): ipotesi aggiuntive, tabelle delle entità (NOME, SINONIMI, DESCRIZIONE, ATTRIBUTO, TIPO DI DATO, VINCOLI) e delle associazioni (con i vincoli anche qui), vincoli non esprimibili; gerarchie con «Generalizzazione di…» e «Specializzazione di…».
- **Soluzione completa** (`soluzione.py`): traccia, ipotesi, diagramma, documentazione e schema in un file solo, in HTML (predefinito, con il diagramma dentro il file) o in Word; Markdown per il libro. La traccia si scrive nella descrizione, nel blocco `traccia:`.
- Esempi nuovi: `hotel.er` (soluzione completa dalla traccia del libro) e `veicoli.er` (gerarchia con associazioni «su» e «giù»).

## 0.3.9 — 17/10/2026

- Nuova skill **diagrammi-er**: disegna diagrammi E/R nella notazione del libro (entità, associazioni, attributi a pallino, chiave semplice e composta, entità deboli, associazioni ricorsive, cardinalità) da una descrizione testuale breve. Produce il file `.drawio`, da aprire e ritoccare in draw.io, e il PNG; dopo un ritocco il PNG si rifà dal `.drawio` con `drawio_png.py`. Colori fissi per i diagrammi nuovi: entità azzurre, associazioni bianche. Entità al singolare: lo script avvisa quando un nome o il verbo di un'associazione sembrano plurali, e quando una linea arriva sul lato degli attributi. Gerarchie ISA e associazioni tra tre entità non sono ancora gestite.
- `progettazione-quiz` e `materiali-moodle`: le domande e le pagine con un diagramma E/R usano la nuova skill, con la descrizione nelle note interne della domanda.

## 0.3.8 — 17/10/2026

- Immagini nelle tracce: nel testo di pagine e domande si scrive `![testo alternativo](nome.png)` e in Moodle diventa un'immagine, larga al massimo quanto la pagina. Le immagini di un quiz stanno tutte in una cartella, indicata nelle note del quiz e passata alla generazione con `--immagini=CARTELLA`.
- Nuovo `allega_immagini.py`: incorpora le immagini nel Moodle XML e si ferma se ne manca una; `crea_mbz.py` le mette nel backup insieme ai database delle domande SQL e PHP. Provato con un ripristino reale (quiz 5PR, 11 immagini).
- `genera_quiz.py`: una `/` nel nome del quiz (per esempio «E/R») non blocca più la generazione.
- Regola in `progettazione-quiz`: nelle pagine le figure del libro; nelle domande che chiedono di leggere un diagramma, immagini nuove disegnate nello stile del libro, con contesti diversi da quelli delle pagine.
- Nella dashboard le immagini compaiono ancora come testo.

## 0.3.7 — 15/10/2026

- «Consegna di un file»: i tipi di file si scelgono riga per riga, con «tipi: .zip» in === options (per esempio la cartella di un sito compressa); senza, restano .html, .htm e .css.
- Importazione da Moodle: la consegna di un file riporta i suoi tipi di file («tipi: .zip») e il titolo senza il prefisso «Consegna:»; nel confronto «zip» e «.zip» sono lo stesso tipo.
- **Dashboard** 0.3.6: nel Dettaglio la consegna di un file ha il campo «Opzioni della consegna» e il foglio dello studente dice quali file si caricano; nell'anteprima degli snippet i link si vedono come link (senza portare altrove); nei dati del quiz, nella Scaletta, si può cambiare il nome del quiz (quello del menù e dell'attività in Moodle).

## 0.3.6 — 12/10/2026

- Importazione da Moodle (`importa_mbz.py`): gli snippet con l'anteprima accanto tornano nella dashboard come ```` ```html anteprima ```` (prima tornavano come codice, «Nel browser» e un elenco). Nel confronto con la dashboard, negli esercizi HTML e CSS l'ordine delle sezioni di «Soluzione e test» non conta più.

## 0.3.5 — 12/10/2026

- Nomi delle domande in Moodle: se il titolo comincia già con un prefisso («Trova l'errore: …», «Consegna: …», «Esempio svolto: …»), il generatore non lo ripete più.
- Regola in `progettazione-quiz`: il codice HTML di tracce, correzioni e soluzioni si scrive indentato di 4 spazi.
- **Dashboard** 0.3.5: la pagina riapre dove era stata lasciata, nello stesso browser: vista (tutti i quiz, scaletta, dettaglio), quiz, domanda scelta nel dettaglio e posizione di scorrimento.

## 0.3.4 — 12/10/2026

- Snippet HTML con l'anteprima accanto: un blocco ```` ```html anteprima ```` mostra il codice e, a fianco, come lo mostra il browser (nella dashboard e in Moodle). Regola didattica in `progettazione-quiz`: nella pagina di teoria la prima volta che compaiono tag con un effetto da capire (liste, tabelle), mai nell'esempio svolto.
- **Dashboard** 0.3.4: anteprima degli snippet nel Dettaglio.

## 0.3.3 — 12/10/2026

- **Dashboard** 0.3.3: nel Dettaglio l'elenco delle domande non torna più in cima a ogni clic e la domanda scelta resta visibile; l'elenco resta fermo mentre la domanda scorre e occupa tutta l'altezza visibile della finestra (ha una sua barra solo se è più lungo); scegliendo una domanda, la pagina risale all'inizio della domanda.

## 0.3.2 — 12/10/2026

- **Dashboard** 0.3.2: una pagina di spiegazione può stare sulla stessa pagina del quiz di una domanda complessa (per esempio i passi da seguire e la consegna del file): l'avviso «le domande di programmazione stanno su una pagina da sole» conta solo le domande.

## 0.3.1 — 12/10/2026

- Nuova tipologia **Consegna di un file** (`consegna_file`): domanda aperta senza testo, con un file da caricare (.html, .htm, .css). Serve a verificare che gli studenti abbiano creato davvero il file, per esempio la pagina dell'esempio svolto.
- **Dashboard** 0.3.1: la tipologia nel catalogo e nel dettaglio.
- L'importazione da un backup riconosce le domande aperte con solo il file da caricare.

## 0.3.0 — 12/10/2026

- **Dashboard** 0.3.0: scelta «Esercizi HTML» nei dati del quiz e nel modulo «Nuovo quiz» (con linguaggio HTML e CSS): **con anteprima** (prototipo `php_con_test`, con l'area di prova) o **senza anteprima** (prototipo `html`: il campo serve solo a incollare il codice scritto nell'editor e provato nel browser). Il dettaglio mostra il prototipo scelto.
- La generazione del quiz usa il prototipo scelto (campo `prototipoHtml`); senza scelta resta `php_con_test`.
- L'importazione da un backup riconosce gli esercizi HTML con il prototipo `html` e imposta il quiz «senza anteprima».

## 0.2.0 — 12/10/2026

- **Dashboard** 0.2.0: nel modulo «Nuovo quiz» il primo tipo è «Libero (senza preset)», senza regole su tipi, quantità, punti e tempi, con la scelta del comportamento in Moodle (esercitazione o verifica).
- **Dashboard**: riquadro «Come scegliere il tipo di quiz» con la descrizione di ogni tipo.
- **Dashboard**: lezione o codice facoltativi; se mancano, il quiz riceve un codice di tre caratteri che comincia con la classe (per esempio 4K7).
- Un codice che comincia con una cifra non è più preso per un numero di lezione: «Lezione N» solo per i numeri.

## 0.1.1 — 12/10/2026

- Claude risponde sempre in italiano, anche quando un comando o una skill si avvia dal menù (l'app aggiunge da sola una frase in inglese).

## 0.1.0 — 12/10/2026

Prima versione del plugin, nata dalle skill usate finora a scuola.

- Sette skill: `progettazione-quiz`, `materiali-moodle`, `verifiche-programmazione`, `domande-coderunner-js`, `domande-coderunner-sql`, `domande-php-mysqli-mock`, `database-didattici`.
- Comando `installa-dashboard`: pubblica la dashboard dell'utente, crea l'attività programmata che avvia i quiz, salva le impostazioni; aggiorna una dashboard esistente senza toccare i quiz.
- **Dashboard** 0.1.0: l'avvio dei quiz legge l'attività dalle impostazioni della pagina (riquadro «Impostazioni» nella vista iniziale); benvenuto al primo avvio; tipo «Importato da Moodle» per i quiz portati da un backup.
- Importazione di un quiz da un backup `.mbz` e confronto tra un backup e la dashboard, per riportare le correzioni fatte in Moodle.
- Catalogo dei database didattici dentro il plugin (biblioteca, palestra, cinema, veterinario, in tre taglie); ogni utente ha la sua pagina «Database didattici» per quelli che crea.
