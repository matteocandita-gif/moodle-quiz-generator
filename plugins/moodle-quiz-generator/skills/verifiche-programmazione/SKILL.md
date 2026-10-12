---
name: "verifiche-programmazione"
description: "Regole didattiche dell'utente per le verifiche di programmazione in JavaScript, SQL e PHP (di ripasso o di dettaglio): struttura, taratura del voto, parte avanzata, teoria, debug, tracce, prova del codice durante la verifica, varianti. Non è un percorso a sé: una verifica si crea sempre partendo da progettazione-quiz e dalla dashboard «Bozze dei quiz», e progettazione-quiz carica questa skill quando il quiz è una verifica di programmazione. Le regole valgono anche per una singola domanda da verifica chiesta fuori dalla dashboard."
---

# Verifiche di programmazione

**Lingua.** Rispondi all'utente sempre in italiano, anche quando il messaggio che avvia la skill o il comando è in inglese: quando si sceglie un comando o una skill dal menù senza scrivere nulla, l'app aggiunge da sola una frase in inglese.

Questa skill dice **come deve essere fatta una verifica di programmazione** in JavaScript, SQL o PHP rispetto al suo scopo: che cosa chiedere, come scrivere le tracce, come tarare il voto. Non è un percorso a sé e non produce file: una verifica si crea sempre con il percorso della dashboard (sotto), e questa skill la carica `progettazione-quiz` al passo 1, quando il quiz è una verifica di programmazione (preset V). Se l'utente chiede una verifica e sei partito da qui, passa subito a `progettazione-quiz` e applica queste regole lì. Valgono anche per una singola domanda da verifica chiesta fuori dalla dashboard.

## Il percorso dei quiz

Ogni quiz Moodle (verifica, esercitazione, ripasso, anche di programmazione) segue un solo percorso, con la dashboard «Bozze dei quiz»:

1. **`progettazione-quiz`**, parte 1, didattica: tipo di quiz, scaletta e tracce nella dashboard, riviste e approvate dall'utente. Per una verifica di programmazione carica `verifiche-programmazione`; il database di un quiz SQL o PHP viene da `database-didattici`.
2. **`materiali-moodle`**, parte 2, tecnica: dal database della dashboard produce XML e `.mbz`; per le domande di programmazione usa `domande-coderunner-js`, `domande-coderunner-sql` e `domande-php-mysqli-mock`.

Nessun'altra skill è un punto di partenza per un quiz. Da sole servono solo per ciò che non diventa un quiz: una domanda singola, una correzione o un controllo (`materiali-moodle` o la skill CodeRunner del linguaggio), domande per la banca o pagine di teoria (`materiali-moodle`), un database per una lezione in phpMyAdmin (`database-didattici`), la conversione delle vecchie domande SQL (`domande-coderunner-sql`).

Le indicazioni le ha fissate l'utente correggendo le verifiche prodotte: seguile anche quando una scelta diversa sembrerebbe più comoda. Le sezioni per linguaggio, in fondo, aggiungono solo ciò che cambia.

## Il tipo di verifica

Chiarisci per prima cosa di che verifica si tratta, perché cambia profondità e peso della teoria.

| | Verifica di ripasso | Verifica di dettaglio |
|---|---|---|
| Argomenti | tutti quelli ripassati | uno (o due vicini) |
| Esercizi di scrittura | uno per argomento, **non troppo complesso**: si controlla che lo strumento sia acquisito | più esercizi sullo stesso argomento, di difficoltà crescente, anche più articolati |
| Teoria | domande **facili sui fondamentali** | da concordare con l'utente |

Se l'utente fornisce verifiche degli anni precedenti, leggile: riprendi lo stile delle tracce e il livello, poi ritara rispetto al tipo di verifica.

## La proposta e la taratura del voto

Una tabella con, per ogni domanda: pagina, posizione, argomento, tipo, che cosa chiede, punti, minuti. Totale 100 punti. Nella dashboard la proposta è la scaletta: l'utente la rivede e la approva prima del dettaglio.

- **Tempo**: la somma dei tempi consigliati sta intorno ai tre quarti del tempo disponibile; il resto serve per provare il codice e rileggere.
- **Parte base e parte avanzata**: una parte base che basta per arrivare all'8 e una parte avanzata che serve per il 9 e il 10. Proponi la divisione dei punti (es. 85/15) e dichiara quanto margine resta per l'8.
- **Gli argomenti della parte avanzata li decide l'utente verifica per verifica**, in ogni linguaggio: chiedili tra le informazioni essenziali, insieme a tipo, argomenti e tempo. Le sezioni per linguaggio danno esempi da proporre, non scelte da applicare da soli.
- **La distinzione base/avanzata è solo del docente**: gli studenti non la vedono. Niente sezioni, etichette o note «per il 10»; le domande avanzate stanno semplicemente in fondo.

## Che cosa non si fa

- **Niente alternative corrette segnate come errori**: una soluzione ammessa in programmazione al pari di quella che usiamo noi non si presenta mai come sbagliata, né nella correzione, né come errore da trovare in un debug, né come distrattore. Le convenzioni dei linguaggi (sotto) valgono per il codice che scriviamo noi, non sono regole imposte agli studenti.
- **Niente codice completo e copiabile** che dia la soluzione di esercizi vicini, nemmeno dentro una domanda di debug o di teoria. I codici da leggere sono brevi (3-8 righe) e semplici.
- **Niente gapfiller** nelle verifiche sommative: gli studenti devono saper scrivere codice completo.
- **Niente strumenti nella traccia**: si dice l'obiettivo, non come raggiungerlo (non «usa return», «usa una LEFT JOIN», «raggruppa per classe», «controlla con mysqli_num_rows»). Si nomina uno strumento solo quando è proprio ciò che la domanda valuta.

## Provare il codice durante la verifica

Il quiz resta in **feedback differito** (impostazioni «verifica» del `.mbz`): le domande di teoria, i Cloze e le risposte multiple non mostrano il feedback fino alla restituzione. Le domande **CodeRunner** seguono le loro opzioni: lo studente esegue il codice e vede il risultato dei test, in tutti i linguaggi. Quindi:

- non nascondere il pulsante di controllo (`hidecheck` resta 0) e non ridurre il controllo alla sola sintassi;
- scrivi i test pensando che lo studente li vede: descrizioni chiare, casi diversi tra loro;
- aggiungi almeno un **test nascosto** con dati diversi da quelli visibili, così una risposta costruita sui valori degli esempi non passa.

## Le tracce degli esercizi

Estese ed esplicite, in forma impersonale, come le scrive l'utente:

> Definire una funzione dal nome `costoNoleggio(ore)` che prende come parametro il numero di ore per cui sono noleggiate le biciclette e restituisce il costo del noleggio. Se il numero di ore è un valore non valido, restituire invece il valore -1.

- La situazione e le regole per intero, con i **casi limite scritti in chiaro**: estremi inclusi o esclusi, valori da cercare scritti esattamente come nel database, dato mancante o non valido e che cosa fare in quel caso.
- La **forma esatta del risultato** in un blocco (output del programma, colonne e ordine delle righe di una query, HTML prodotto da una pagina PHP) e un **esempio svolto**.
- L'ordine degli input, i nomi dei parametri del form, i nomi delle funzioni: dichiarati, perché i test li usano.

## Le domande di teoria

- A **risposta aperta**, sui concetti del programma; nella verifica di ripasso facili e sui fondamentali.
- Contestualizzate: su un codice breve da leggere senza eseguirlo, oppure **subito dopo l'esercizio** a cui si riferiscono («nella domanda precedente …»). In questo caso la domanda resta generica, senza nominare l'esercizio, così funziona con qualunque variante; e sta sulla stessa pagina dell'esercizio.
- Tre o quattro richieste numerate, ciascuna con un verbo: «Indicare che cosa stampa / restituisce…», «Spiegare perché…», «Indicare come correggere…».
- Per il correttore: i punti di ogni richiesta, la risposta attesa, i casi da mezzo punto, le risposte da non accettare.

## Il debug con motivazione

- Frammenti brevi con errori **concettuali** legati all'argomento, mai refusi (esempi nelle sezioni per linguaggio).
- La traccia dice che cosa dovrebbe fare il codice e quanti errori ci sono.
- Per ogni errore: **che cosa succede**, **perché**, **correzione**; la casella di risposta parte con questo schema.
- Per il correttore: un punto per parte, e le righe che *non* sono errori, da non premiare se indicate al posto di quelle vere.

## Le istruzioni per gli studenti

Brevi, perché nessuno le legge se sono lunghe: niente elenco delle domande né punteggi per domanda.

- La verifica contiene domande di **teoria** e di **pratica**; durata.
- Il codice si può provare con il pulsante della domanda e si vede il risultato dei test; la valutazione considera anche test che non si vedono.
- Come viene valutato il codice: **correttezza sintattica** (un codice che non parte non supera i test), leggibilità (indentazione, nomi chiari, niente codice inutile o commentato) e i criteri del linguaggio (sotto).

## Verifiche ripetibili

Quando l'utente chiede più varianti per domanda:

- le varianti della stessa posizione sono **equivalenti**: stessa struttura, difficoltà, tempo e punti; cambiano contesto, dati e codice;
- prima di scriverle, una tabella con i contesti scelti per ogni posizione nelle varie varianti, così l'utente vede ripetizioni o squilibri;
- si scrivono insieme, dopo che la prima variante è stata provata davvero: di norma si fa e si prova la variante a, e le altre si scrivono quando l'utente le chiede (per la verifica di recupero);
- la realizzazione (righe con lo stesso `tag` nella dashboard, domande casuali per tag nel `.mbz`) è in `progettazione-quiz` e `materiali-moodle`.

## Studenti con PDP

Per gli studenti con PDP (DSA) la verifica si adatta in uno dei due modi, scelto con l'utente verifica per verifica:

- **tempo aggiuntivo**: stessa verifica, più tempo con la deroga del singolo utente nelle impostazioni del quiz;
- **riduzione dei contenuti** fino al 30% del carico, misurato in minuti consigliati e non in numero di domande: si tolgono **domande intere**, senza cambiare il contenuto di quelle che restano. Quali togliere (e se tenere la parte avanzata) lo decide l'utente.

La riduzione si fa in una **copia PDP** del quiz: in apertura la dichiarazione «Solo mappe concettuali»; al posto di ogni domanda tolta, sulla stessa pagina e prima della domanda, una delle descrizioni «Riduzione contenuti PDP -1…-5» della banca condivisa «Domande per riduzione PDP - DSA» (corso «Quinte SIA - Deposito»); la domanda tolta resta nel quiz a 0 punti. La copia non si genera insieme al quiz: l'utente la chiede dopo, quando è sicuro che il quiz funziona (la generazione da script è un punto aperto da provare con un ripristino; intanto la fa l'utente in Moodle).

## JavaScript

- **Argomenti** (terza): input e calcoli, selezione, cicli `while` e `for`, contatori e accumulatori, array, funzioni (parametri, `return` contro `console.log`), condizioni di guardia ed early return, visibilità delle variabili.
- **Parte avanzata**: la decide l'utente; esempi già usati: condizioni di guardia ed early return, visibilità delle variabili. Quando lo strumento è ciò che si valuta, la traccia lo nomina («Usare condizioni di guardia ed early return per ottenere un codice pulito»).
- **Tracce**: «Scrivere un programma che chieda all'utente prima … e poi …»; esempio con il calcolo per esteso («con 10 km e 2 bagagli il totale è 4 + 20 + 2 = 26 euro»). **Solo funzioni**: «Nello svolgimento scrivere esclusivamente la definizione della funzione: le chiamate sono già presenti nei test», con una tabella chiamata → valore restituito al posto di codice di esempio. **Funzione e programma principale**: la traccia descrive entrambi; l'ultimo test chiama anche direttamente la funzione, e la traccia lo dice (il nome deve essere esatto).
- **Teoria facile**: assegnamento, if consecutivi ed else if, ciclo che non termina, `return` contro `console.log`.
- **Debug**: indice da 1, `<=` sulla lunghezza, accumulatore azzerato nel ciclo, variabile locale usata fuori dal blocco, parametro modificato al posto della globale.
- **Criteri nelle istruzioni**: condizioni di guardia e visibilità delle variabili dove servono.

## SQL

- **Argomenti**: SELECT con WHERE e ORDER BY, funzioni di aggregazione, GROUP BY e HAVING, JOIN su due o più tabelle, INSERT, UPDATE, DELETE, CREATE TABLE con chiavi e vincoli.
- **Parte avanzata**: la decide l'utente; esempi da proporre: «chi non ha…» (LEFT JOIN), conteggi e somme per gruppo su più tabelle con condizione sul gruppo (GROUP BY e HAVING con JOIN), modifiche che dipendono da un'altra tabella. NOT IN e subquery non sono nel programma: non proporle.
- **Il database**: dal catalogo di `database-didattici` (di norma la taglia realistica, 20-50 righe). Senza varianti, uno solo per tutta la verifica; con le varianti, **uno per lettera** (a, b, c), database paralleli con la stessa forma e trappole equivalenti, e lo studente li vede mescolati: lo schema va in testa a ogni domanda. Prima di consegnare, controlla le soluzioni con `verifica_query.py`: ogni errore tipico deve cambiare il risultato e l'ordine del risultato non deve avere pari merito, altrimenti sistema i dati del database del quiz (INSERT o UPDATE commentati in fondo allo script).
- **Tracce**: forma fissa delle query («Il database contiene:», schema, breve descrizione del non ovvio, **«Scrivere la query opportuna per ottenere i seguenti dati:»**, richiesta in un paragrafo a sé; dettaglio in `formato-consegna.md` della dashboard). Niente elenco delle colonne: lo studente le vede nel risultato atteso. L'ordinamento si chiede solo dove serve, ma l'ordine della soluzione deve essere unico (nessun pari merito sui dati, prove nascoste comprese). Valori da cercare scritti esattamente come nel database (il confronto distingue le maiuscole); per le CREATE tipi e vincoli esatti; nessun costrutto che SQLite rifiuta (`compatibilita.md` di `domande-coderunner-sql`). Non dire quale clausola usare.
- **Teoria facile**: chiave primaria e chiave esterna, differenza tra WHERE e HAVING, che cosa restituisce una JOIN rispetto a una LEFT JOIN su due righe date, che cosa fa una query letta senza eseguirla.
- **Debug**: JOIN senza condizione o sui campi sbagliati, WHERE dimenticata in un UPDATE, `= NULL` al posto di `IS NULL`, condizione sul gruppo messa nel WHERE, `>` al posto di `>=` su una soglia.
- **Criteri nelle istruzioni**: la query deve dare esattamente le colonne e l'ordine del risultato atteso; alias e indentazione chiari.

## PHP

- **Argomenti**: pagine che ricevono dati da un form (GET e POST), connessione al database, SELECT e INSERT eseguite da PHP, elaborazione dei risultati in HTML, messaggi di errore con `or die`.
- **Convenzioni del codice** (quelle di `domande-php-mysqli-mock`): le cinque fasi commentate; **variabili sempre integrate nelle stringhe**, mai concatenate con il punto (il punto solo per le chiamate di funzione), nel codice che scriviamo noi: lo studente può concatenare, e non è un errore né un criterio di valutazione; `mysqli_report(MYSQLI_REPORT_OFF)`; database e credenziali dichiarati nella traccia.
- **Parte avanzata**: la decide l'utente; esempi da proporre: validazione dei dati del form con messaggio e nessuna query, pagina di dettaglio raggiunta da un link con parametro, più query nella stessa pagina (controllo prima dell'inserimento, `mysqli_insert_id`), query con JOIN o aggregati.
- **Tracce**: nomi dei parametri del form, HTML esatto dell'output in un blocco, testo esatto dei messaggi (nessun risultato, inserimento riuscito, errore). Non dire quali funzioni usare.
- **Test**: dati del form diversi in ogni test, almeno un caso con risultato vuoto o inserimento rifiutato; output normalizzato (spazi e a capo non contano).
- **Teoria facile**: differenza tra GET e POST, che cosa succede se mancano gli apici intorno a un testo nella query, a che cosa serve `or die`, in quale fase si è fermata una pagina dato un messaggio d'errore.
- **Debug**: nome del database o della tabella sbagliato, apici mancanti, chiave di `$_GET` diversa dal `name` del form, `if` al posto di `while` nella lettura dei risultati (si vede una riga sola), valori della INSERT nell'ordine sbagliato.
- **Criteri nelle istruzioni**: le cinque fasi riconoscibili, output HTML esatto. Lo stile delle stringhe (integrazione o concatenazione) non è un criterio.