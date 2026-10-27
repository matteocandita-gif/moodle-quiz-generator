# Changelog

Le novità di ogni versione di «Moodle: quiz generator». Le righe segnate **Dashboard** cambiano la pagina «Bozze dei quiz», quelle segnate **Editor mappe** la pagina «Mappe dei prerequisiti»: Claude propone di aggiornarle, e quiz e mappe salvati restano.

## 0.8.5 — 27/10/2026

Codice da leggere non eseguibile:

- Nelle **domande di lettura** (teoria su un codice, debug con motivazione, tracciamento, lettura dell'output, trova l'errore) il codice JavaScript, PHP e SQL della traccia esce **identico a schermo ma non eseguibile**: lettere cirilliche nelle parole chiave e spazi a larghezza zero dopo gli operatori, circa uno per riga. Copiato in una domanda CodeRunner o nella console dà un errore di sintassi. Ogni sostituzione è controllata con l'interprete (`node --check`, `php -l`, SQLite): da sola blocca il codice, quindi correggerne una non basta. I colori non cambiano.
- **Mai** negli esempi da usare come riferimento: pagine, esempi svolti, correzione, feedback.
- Marcatori nella traccia per i casi particolari: ```` ```js leggere ```` (codice da leggere in un'altra tipologia) e ```` ```js esempio ```` (codice di riferimento dentro una domanda di lettura). Regola in `verifiche-programmazione`, formato in `formato-consegna.md`, funzione `rendi_non_eseguibile` in `moodle_lib.py`.

Correzione delle verifiche, versione PDP nella stessa verifica:

- Dashboard **«Correzione verifiche»**: in «Importa da Moodle» il riquadro **«Aggiungi studenti da un altro export (versione PDP)»**. Si trascinano l'export «Risposte» della copia PDP (anche con i nomi: restano nel browser) e, consigliato, l'export «Valutazioni» della copia, di cui si legge solo l'intestazione.
  - Le colonne si abbinano alle domande della verifica **per somiglianza del testo** (parole e codice), perché la copia ha tracce riscritte e domande in più (la dichiarazione sulle mappe, le descrizioni): l'abbinamento si controlla e si corregge nell'anteprima.
  - Le **domande escluse** sono quelle a 0 punti nell'export «Valutazioni»; senza quel file, quelle non svolte da nessuno. Avviso se i punti della copia non sono in proporzione con quelli della verifica.
  - Reimportando, gli studenti PDP con la stessa sigla si sostituiscono, non si duplicano; i nuovi vanno in coda alla classe, in ordine di sigla.
- Nelle viste: le domande escluse sono schede tratteggiate, senza punteggio e senza niente da inserire in Moodle; il voto degli studenti PDP è sul loro massimo ridotto; nel riepilogo l'etichetta PDP e «×» per le escluse; media e istogramma senza chi non ha ancora punteggi.
- Nelle schede il **titolo della variante** che lo studente ha avuto davvero (domande casuali e copie PDP), non quello della prima.
- `riepilogo.py` conta le domande escluse; nella skill: le proposte per gli studenti PDP si scrivono solo con `update`.

## 0.8.4 — 27/10/2026

Correzione delle verifiche:

- **Resoconti** per il docente, su richiesta: uno per studente e uno della classe, con l'andamento e gli errori ricorrenti (regole in `resoconti.md`). Si leggono e si modificano nella dashboard «Correzione verifiche», nella vista per studente e nel riepilogo voti. A correzione finita in Moodle i voti si prendono dall'export «Valutazioni».
- Dashboard **«Correzione verifiche»**: nel riepilogo voti l'istogramma dei voti a fasce di mezzo voto, con la linea della sufficienza, media, mediana e sufficienti.
- **Commenti più facili da scorrere** (`criteri.md`):
  - un concetto per riga, anche nei commenti brevi;
  - due concetti scollegati non si uniscono con il punto e virgola;
  - grassetto per le etichette («**Richiesta 2:**») e per poche parole chiave. La pagina lo copia in Moodle come grassetto.

Dashboard dei quiz:

- **Dashboard** 0.3.13: pulsante **«Esporta»** nel riquadro «Avanzamento», attivo solo con il dettaglio approvato. Avvia la stessa attività programmata di «Inizia» con «Quiz da esportare: <id>»: la sessione genera il backup `.mbz` e il Moodle XML, li consegna nella sua chat (con la notifica) e scrive l'esito nel quiz (campo `esportazione`). La pagina mostra se l'esportazione è richiesta, in corso, fatta o non riuscita; se l'attività non parte, dà la frase da incollare in chat.
- **Prompt dell'attività cambiato** (`installazione.md`): ha la sezione «Esportare». Con l'aggiornamento della dashboard Claude aggiorna anche il prompt dell'attività programmata già creata (`update_trigger`).
- `materiali-moodle`: dopo una generazione dalla dashboard si scrive l'esito in `esportazione`, anche quando si genera in chat.

## 0.8.3 — 26/10/2026

Correzione delle verifiche: il codice nei commenti si vede come codice.

- **Codice in linea** tra apici inversi (`let i = 0`): «Copia commento per Moodle» lo incolla come `<code>`, nel testo semplice gli apici si tolgono. Sotto il commento la pagina mostra l'anteprima.
- **Blocchi di codice**: quando la correzione ha più di due istruzioni si scrive come blocco, tra una riga ```js e una riga ```, con a capo e rientri; arriva in Moodle come `<pre><code>`. Le spiegazioni brevi possono stare nel codice come commenti in linea.
- **CodeRunner non svolte o completamente sbagliate** (fino al 20% del massimo, o con il codice di un'altra domanda): niente soluzione intera nel commento, una o due frasi sull'errore principale e il rimando «Clicca su «Mostra/Nascondi soluzione dell'autore» per vedere un esempio di soluzione corretta.»
- Dashboard **«Correzione verifiche»**: nelle domande automatiche una riga con lo stesso punteggio ma un commento da dare è segnata «commento da inserire».

## 0.8.2 — 26/10/2026

Correzione delle verifiche: commenti a paragrafi e niente più spunta «Rivisto».

- **Commenti a paragrafi**: con più richieste un paragrafo per richiesta, «Sintassi:» in un paragrafo a parte, un paragrafo per parte nei commenti lunghi sulle pagine HTML e PHP (regola in `criteri.md`).
- Dashboard **«Correzione verifiche»**: «Copia commento per Moodle» trasforma ogni riga del commento in un paragrafo, che arriva così nell'editor di Moodle (prima gli a capo si perdevano).
- Dashboard **«Correzione verifiche»**: tolta la spunta «Rivisto». Una riga è a posto quando ha il punteggio e, se va riportata in Moodle, è segnata «Inserito»; schede, elenco e intestazione mostrano quante righe restano da inserire o senza punteggio. `prepara_revisione.py` e `riepilogo.py` allineati.

## 0.8.1 — 25/10/2026

**Esercitazione con studio e domande sequenziale**: nuovo nome del tipo «Studio e domande» (la sigla resta SD), in linea con gli altri tipi, e regole sulle parti e sulle domande.

- Teoria divisa in **parti brevi, una per nucleo**: il numero di parti e di domande non è fisso, lo decide il materiale di partenza.
- Le **chiuse** verificano tutti gli aspetti di **conoscenza e comprensione puntuale** della parte, a cominciare dalle **definizioni**: per ogni definizione importante una chiusa che viene prima delle altre (riconoscere la definizione giusta, riformulata, tra opzioni che cambiano un solo elemento essenziale; trovare l'elemento mancante o scambiato; dire quali casi rientrano). Con gli appunti davanti non basta cercare la stessa frase.
- L'**aperta** (di norma una per parte) verifica l'**esposizione** del concetto generale: spiegarlo collegandone gli elementi dentro una situazione nuova o per un destinatario, mai riscrivere una definizione né riassumere la pagina. Nelle indicazioni per chi corregge i criteri dell'esposizione; una risposta che ricopia la teoria senza collegarla né rispondere alla situazione vale al massimo metà dei punti.
- **Dashboard** 0.3.12: nuovo nome e nuova guida del tipo; avviso sulle aperte che sembrano chiedere una definizione o un elenco, nota se una parte ha più di un'aperta.

## 0.8.0 — 25/10/2026

**Copia PDP delle verifiche**, generata dal plugin. Verificata con ripristini reali nel Moodle della scuola: la copia si aggancia alle domande della verifica e alle descrizioni della banca condivisa (riferimenti, non copie), anche da un corso diverso da quello delle banche.

- `crea_pdp.py`: le posizioni tolte restano a 0 punti, prima di ognuna una «Riduzione contenuti PDP -k» diversa (o PEI), in apertura la dichiarazione «Solo mappe concettuali» (o «Tempo aggiuntivo e mappe», «Generica»), nome con «(PDP)». Due modalità: **dalla dashboard** (`genera_quiz.py … --pdp`), quando le domande della verifica stanno in un deposito registrato, oppure **dal backup** della verifica ripristinata, sempre possibile.
- Quali domande togliere si decide in progettazione: nella dashboard, nelle verifiche, la casella **«tolta nella PDP»** sotto i punti di ogni riga (per le varianti, di tutta la posizione); gli avvisi mostrano la riduzione in minuti consigliati e avvisano oltre il 30%.
- La banca delle descrizioni PDP («Domande per riduzione PDP - DSA», deposito delle terze) è salvata nella dashboard (`impostazioni/pdp`): non serve rimandarla. La skill `verifiche-programmazione` diceva per errore che stava nel deposito delle quinte.
- `leggi_mbz.py --banche` mostra anche le attività «Banca delle domande» contenute nel backup (backup dei corsi deposito o di una singola banca).
- **Dashboard** 0.3.11: casella «tolta nella PDP» e avvisi della copia PDP.

## 0.7.0 — 24/10/2026

**Depositi**: le domande possono andare direttamente nella banca di un corso deposito, senza spostarle a mano. Regole verificate con ripristini reali nel Moodle della scuola.

- Moodle scrive in una banca che sta fuori dal backup solo se si ripristina **nel corso in cui la banca sta** (altrimenti mette tutto, nascosto, nella banca di sistema) e **non crea categorie nuove** lì: la categoria deve esistere già. Due casi funzionano: una categoria nota del deposito, oppure la categoria che un quiz della dashboard ha creato nella sua banca e che hai spostato tu nel deposito; i quiz successivi con la stessa categoria la ritrovano.
- Le domande già presenti nel deposito vengono **riusate senza doppioni**. Gli identificativi (stamp) di categorie e domande ora sono stabili: la categoria dal nome, la domanda dal contenuto (una domanda cambiata diventa una domanda nuova). Rigenerare un quiz o farne la copia PDP nel deposito non duplica le domande invariate.
- Nelle impostazioni della dashboard i **depositi** registrati (`impostazioni/depositi`), che Claude scrive da un backup con `leggi_mbz.py --banche`; nei dati del quiz «Dove vanno le domande»: la banca del quiz (come prima) o un deposito.
- Importando un quiz da un backup, le domande che vengono da un deposito tengono lo stamp d'origine (`stampOrigine`): rigenerate nel deposito si riusano.
- `crea_mbz.py`: impaginazione `banca` (contesto, modulo, categoria «top» e, se c'è, la categoria esistente) e `stamp`; `leggi_mbz.py --banche`.
- **Dashboard** 0.3.10: scelta del deposito nei dati del quiz, elenco dei depositi nelle impostazioni, avvisi se la categoria non è tra quelle note del deposito e promemoria del corso in cui ripristinare.

## 0.6.1 — 24/10/2026

Nuovo tipo di quiz **Studio e domande** (sigla SD), provato con due bozze ripristinate in Moodle.

- La teoria è divisa in parti: gli studenti leggono e prendono appunti, poi rispondono alle domande su quella parte, prima le chiuse (vero/falso, risposta multipla, corrispondenza, risposta breve; niente completamenti, che suggerirebbero la risposta aperta) e poi le aperte. Formativo, senza versione PDP.
- Impostazioni dell'.mbz, preset nuovo **studio**: navigazione sequenziale (non si torna alla teoria), un tentativo, feedback differito, tempo unico gestito dagli studenti (40 minuti se il quiz non dice altro); durante il tentativo nessuna verifica, revisione completa subito dopo la consegna e dopo, a quiz aperto.
- Pagine e nomi: la pagina di teoria sta da sola su una pagina del quiz, apre (la prima) con «Come si svolge» e chiude con «Prima di andare avanti»; le chiuse di una parte insieme sulla pagina dopo, ogni aperta su una pagina sua; una sezione per parte; la pagina di teoria ha il prefisso «Teoria».
- Voto ed elementi di valutazione compaiono solo dopo la correzione delle aperte (limite di Moodle): l'esito delle chiuse si vede subito domanda per domanda; la consegna lo ricorda.
- **Dashboard** 0.3.9: il tipo «Studio e domande» nel modulo «Nuovo quiz» e nella guida dei tipi, con 40 minuti proposti; avvisi se una parte di teoria non ha domande chiuse o aperte, se una chiusa viene dopo l'aperta, se la teoria condivide la pagina con una domanda o se una domanda viene prima della prima teoria.

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
