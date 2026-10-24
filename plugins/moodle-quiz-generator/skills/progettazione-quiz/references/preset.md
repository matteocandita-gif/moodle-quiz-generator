# Tipi di quiz e preset

Ogni quiz ha un tipo, e il tipo porta con sé un **preset**: le regole che la scaletta deve rispettare. La dashboard controlla le regole misurabili negli avvisi (punti, minuti, sequenza delle parti, sostegno del debugging, strumento); le altre le applichi tu scrivendo scaletta e tracce.

Ogni preset ha otto voci: scopo, progressione, tipologie, regole sulle tracce, punteggi e tempi, pagine e sezioni, sostegno e feedback, varianti. Le voci marcate **(da validare)** sono proposte non ancora provate su un quiz reale: applicale, ma dillo nella proposta. Le voci marcate **(aperto)** non sono decise: chiedi all'utente quando servono.

| Sigla | Tipo | Impostazioni dell'.mbz |
|---|---|---|
| LIB | Libero (senza preset) | scelte nel modulo (`presetMbz`) |
| ED | Esercitazione con spiegazione di dettaglio | esercitazione |
| EDT | Esercitazione con spiegazione, solo teoria | esercitazione |
| SD | Studio e domande | studio |
| V | Verifica di programmazione (sottotipi: ripasso, dettaglio) | verifica |
| VT | Verifica teorica | verifica |
| RT | Ripasso teorico (verifica formativa) | esercitazione |
| EP | Esercitazione pratica | esercitazione |
| ER | Esercitazione complessiva di ripasso | esercitazione |

Impostazioni dell'.mbz, verificate su backup reali del Moodle della scuola (5.2):

- **esercitazione**: comportamento interattivo con più tentativi, tentativi illimitati, nessun limite di tempo, revisione completa durante il tentativo, subito dopo e a quiz aperto (risposte, punteggi, feedback, risposta giusta);
- **verifica**: feedback differito, un tentativo, tempo pari al tempo del quiz, durante la prova si vede solo il tentativo e il punteggio massimo; feedback, punteggi e risposte giuste si aprono dopo, alla restituzione, cambiando le opzioni di revisione del quiz (ricordalo nel messaggio di consegna);
- **studio**: navigazione sequenziale (non si torna alle pagine precedenti), feedback differito, un tentativo, tempo pari al tempo del quiz (40 minuti se manca); durante il tentativo nessuna verifica, revisione completa (risposte, punteggi, feedback, risposta giusta) subito dopo la consegna e dopo, finché il quiz è aperto. Provato con un ripristino reale il 24/10/2026.

Voto del quiz: 10, sufficienza 6, salvo indicazione diversa nel quiz della dashboard.

## LIB · Libero (senza preset)

- **Scopo**: un quiz che non rientra negli altri tipi, o per cui l'utente non vuole regole prefissate. È il primo tipo del modulo «Nuovo quiz».
- **Regole**: nessun preset. Tipologie, numero di domande, parti, punti, tempi e struttura vengono solo dalla `richiesta` del quiz; dove la richiesta non dice niente, scegli tu in modo ragionevole e scrivilo nelle `note`. Valgono comunque le regole generali di questa skill (domande di comprensione, tracce, convenzioni, pagine del quiz) e, per una verifica di programmazione, `verifiche-programmazione`. La dashboard non controlla punti, tempi, parti né tipologie: ammette tutte quelle del catalogo; usa le parti 0 (pagina) e 1 (domanda).
- **Impostazioni dell'.mbz**: le sceglie l'utente nel modulo, nel campo `presetMbz` del quiz (`esercitazione` o `verifica`, di norma `esercitazione`).

## ED · Esercitazione con spiegazione di dettaglio

- **Scopo**: spiegare un argomento nuovo e farlo esercitare in una lezione base di due ore. Completarla dà un voto che gli studenti non vedono e che non viene verbalizzato: punteggi con un criterio semplice, senza formalizzare troppo.
- **Progressione**: «Come lavoriamo oggi» in apertura, poi uno o più blocchi; in ogni blocco le parti in quest'ordine: pagina del blocco (introduzione e spiegazione, con l'esempio svolto in un riquadro giallo), esempio svolto da leggere, completamento, debugging, esercizio guidato. In fondo gli esercizi finali. Il debugging viene dopo il completamento. **Ogni blocco chiude con almeno un esercizio libero**, da scrivere da zero (funzione o programma, senza codice da completare né da correggere): non basta il guidato. Il numero di blocchi e di esercizi dipende dall'argomento: non ci sono numeri fissi.
- **Tipologie**: quelle con ED nel catalogo. Debugging: con messaggi e silenzioso con CodeRunner dove si può (JavaScript, SQL, PHP); in HTML e CSS solo «Trova l'errore», perché il browser non dà errori. Esercizi finali: CodeRunner; in HTML e CSS, dove non c'è correzione automatica, «Esercizio HTML» o «Esercizio CSS» (editor di CodeRunner senza test, correzione manuale).
- **Esercizi finali**: non per forza uno solo. Dove gli esercizi sono brevi se ne fanno altri simili (stessa struttura e difficoltà, contesto diverso). Quando la lezione introduce uno strumento di programmazione (per esempio l'early return) si fanno più esercizi complessivi **(aperto: «complessivi» vuol dire che combinano lo strumento nuovo con argomenti già visti? A14)**.
- **Regole sulle tracce**: estese ed esplicite, in forma impersonale. Lo strumento si può nominare: per ogni esercizio l'utente sceglie nella scaletta se è **suggerito** o **non nominato**. Dove lo strumento non è scontato lo si suggerisce, dove la competenza dovrebbe essere acquisita si dà solo l'obiettivo. Proposta di partenza **(da validare)**: strumento della lezione suggerito nel guidato e nei primi finali, non nominato negli ultimi; strumenti di lezioni precedenti non nominati.
- **Punteggi e tempi**: 100 punti. Pesi per parte **(da validare)**: esempio svolto e completamento 20, debugging 25, esercizio guidato 20, esercizi finali 35; dentro una parte i punti si dividono in parti uguali, il peso dei finali può salire quando si introduce uno strumento. Minuti orientativi **(da validare)**: pagine 10-15 in tutto, esempio svolto e completamento circa 15, debugging 15, guidato 15, finali 25. Una lezione di due ore ha **105 minuti** disponibili (non 90): è il `tempo` da proporre per una ED, e la somma dei minuti deve starci con almeno 5 minuti di margine.
- **Pagine e sezioni**: le pagine di spiegazione stanno dentro il quiz come descrizioni, compresa «Come lavoriamo oggi». Una sezione del quiz per l'introduzione e una per blocco, più quella degli esercizi finali. Le domande complesse (programmazione, esercizi liberi) su una pagina da sole.
- **Sostegno e feedback**: nel debugging il sostegno cala lungo la sequenza: prima quanti errori e dove, poi solo quanti, poi nessuna indicazione. Ogni errore è legato a un concetto della lezione. Feedback su ogni opzione sbagliata, visibile subito.
- **Varianti**: nessuna variante prevista **(da validare, A13)**. Argomenti senza codice: preset EDT.

## EDT · Esercitazione con spiegazione, solo teoria

Deciso il 2026-10-09 dopo il quiz «Internet e il Web» (chiude A12).

- **Scopo**: spiegare un argomento di sola teoria (senza codice) e verificare subito la comprensione. Come ED: voto interno, non visto né verbalizzato.
- **Quando**: se la richiesta mescola teoria e pratica (per esempio «che cos'è il Web» e poi HTML), proponi due quiz, uno EDT per la teoria e uno ED per la pratica, e chiedi all'utente prima di scrivere la scaletta.
- **Progressione**: «Come lavoriamo oggi» (parte 0), poi blocchi; in ogni blocco una o più **pagine di spiegazione** (parte 1), ognuna seguita subito dalle sue **domande di comprensione** (parte 2), sulla pagina del quiz successiva. Una pagina di spiegazione tratta un argomento, al massimo due: se ne tratta di più si divide, anche dentro lo stesso blocco (B0, poi le sue domande, poi B6 e le sue).
- **Tipologie**: vero/falso, risposta multipla (una o più giuste), risposta breve, completamento di testo, metti in ordine, corrispondenza.
- **Regole sulle domande**: i criteri delle domande di comprensione nella skill `progettazione-quiz`.
- **Punteggi e tempi**: 100 punti, tutti nelle domande di comprensione, a multipli di 5; nei Cloze un campo ogni 5 punti. Pagine senza punti. Tempo da decidere quiz per quiz (30 minuti per «Internet e il Web»), con almeno 5 minuti di margine.
- **Pagine e sezioni**: una sezione per l'introduzione e una per blocco. Le domande di una pagina di spiegazione stanno insieme sulla pagina del quiz che la segue.
- **Sostegno e feedback**: feedback su ogni opzione, visibile subito; non deve svelare la risposta di un'altra domanda della stessa pagina.
- **Nomi**: la pagina di spiegazione ha il prefisso «Spiegazione», come in ED.

## SD · Studio e domande

Deciso il 2026-10-24 con due bozze di prova ripristinate in Moodle.

- **Scopo**: dare un tempo di studio, in cui gli studenti leggono la teoria e prendono appunti, e un tempo per rispondere alle domande su quella teoria, senza poterla rileggere mentre rispondono (possono usare i loro appunti). Formativa.
- **Progressione**: la teoria è divisa in **parti**, una pagina di teoria per parte (parte 1). Dopo ogni pagina di teoria le sue domande: prima le **chiuse** (parte 2), poi le **aperte** (parte 3). Ogni concetto della pagina ha domande chiuse e almeno una aperta. Niente pagina «Come lavoriamo oggi»: la prima pagina di teoria apre con il riquadro arancio «Come si svolge» (teoria a parti, domande dopo ogni parte, niente ritorno indietro, risposte giuste solo dopo la consegna, tempo unico gestito da loro). Ogni pagina di teoria chiude con il riquadro arancio «Prima di andare avanti»: passando alla pagina successiva non si torna più alla teoria, quindi prendere gli appunti.
- **Tipologie**: chiuse: vero/falso, risposta multipla (una o più giuste), corrispondenza, risposta breve. **Niente completamenti** (completamento di testo, metti in ordine): suggerirebbero le parole della risposta aperta, che deve basarsi solo su teoria e appunti. Aperte: teoria a risposta aperta, correzione a mano.
- **Regole sulle domande**: i criteri delle domande di comprensione nella skill `progettazione-quiz`. Le chiuse non svelano la risposta dell'aperta della stessa parte, nemmeno nei feedback (che però si vedono solo dopo la consegna).
- **Punteggi e tempi**: nessun totale fisso; le aperte valgono più delle chiuse (nelle bozze di prova 1 punto la chiusa, 2 l'aperta). Il docente può dividere le aperte e le chiuse in due elementi di valutazione del quiz, ma Moodle non mostra voti né elementi finché le aperte non sono valutate: gli studenti vedono subito l'esito domanda per domanda delle chiuse. Tempo unico, gestito dagli studenti: di norma **40 minuti** in tutto (il campo `tempo` del quiz).
- **Pagine e sezioni**: una sezione per parte («Parte 1 - argomento»). La pagina di teoria sta da sola su una pagina del quiz (altrimenti la si vede mentre si risponde); le chiuse di una parte insieme sulla pagina successiva; ogni aperta su una pagina sua. Nomi: la pagina di teoria ha il prefisso «Teoria».
- **Sostegno e feedback**: feedback su ogni opzione sbagliata e indicazioni per chi corregge sulle aperte, visibili solo dopo la consegna (impostazioni «studio»). Il docente legge in classe alcune risposte aperte alla fine dell'attività.
- **Varianti**: nessuna. Nessuna versione PDP: è un'attività formativa, il tempo in più non serve.

## V · Verifica di programmazione

- **Scopo**: valutare. Due sottotipi, **ripasso** (tutti gli argomenti ripassati, un esercizio non troppo complesso per argomento, teoria facile sui fondamentali) e **dettaglio** (uno o due argomenti vicini, più esercizi di difficoltà crescente).
- **Regole didattiche**: carica `verifiche-programmazione` (JavaScript, SQL, PHP), che decide struttura, taratura del voto, teoria, debug e tracce. Gli argomenti della parte avanzata (quelli per il 9 e il 10) li decide l'utente verifica per verifica: chiedili tra le informazioni essenziali. Per HTML e CSS, senza correzione automatica, restano lettura del codice, «Trova l'errore» ed «Esercizio HTML» / «Esercizio CSS» a correzione manuale **(da ripensare, A3)**. Teoria nella verifica di dettaglio: da concordare **(aperto, A4)**.
- **Regole sulle tracce**: consegne chiare sull'obiettivo, **senza** indicare gli strumenti da usare, salvo ciò che è oggetto della valutazione. Niente codice completo e copiabile che dia la soluzione di esercizi simili. Niente gapfiller nelle verifiche sommative: devono saper scrivere codice completo. Esercizio libero a correzione manuale ammesso, con indicazioni per il correttore e punti per criterio.
- **Punteggi e tempi**: 100 punti, parte base 85 e parte avanzata 15. La somma dei tempi consigliati sta intorno ai tre quarti del tempo disponibile; il resto serve per provare il codice e rileggere.
- **Pagine e sezioni**: istruzioni in apertura; niente sezioni che rivelino la parte avanzata.
- **Sostegno e feedback**: feedback scritto in tutte le domande, nascosto durante la prova e svelato alla restituzione (impostazioni «verifica»). Le domande CodeRunner seguono le loro opzioni anche con il feedback differito: lo studente prova il codice e vede il risultato dei test (in tutti i linguaggi); non si nasconde il pulsante di controllo.
- **Varianti**: verifiche ripetibili con varianti per tag: righe con lo stesso `tag` nella scaletta, stessi punti e stessa struttura, cambiano contesto e codice (`formato-consegna.md`). Il `.mbz` le gestisce: ogni posizione è una domanda casuale per tag.

## VT · Verifica teorica

- **Scopo**: valutare la teoria, con richieste su livelli di Bloom. Esiste una sola verifica teorica: non c'è una teorica di ripasso con voto.
- **Punteggi** **(da validare, A5)**: ricordare 20, comprendere 30, applicare 20, analizzare 15, valutare/creare 15. Base 85, margine 5 per l'8.
- **Livelli**: la corrispondenza tipologia → livello è tipica, il livello si assegna domanda per domanda; valutare e creare solo se pertinenti **(da validare, A6)**. La differenza con le verifiche di programmazione (base/avanzata per argomento) resta **(da validare, A7)**. Nella dashboard il livello è il campo `parte` (1-5).
- Il resto come la verifica di programmazione: feedback nascosto fino alla restituzione, tempi intorno ai tre quarti.

## RT · Ripasso teorico (verifica formativa)

- **Scopo**: verificare e spiegare insieme. Nessun voto. Gli studenti hanno già studiato: serve a consolidare la teoria.
- **Feedback**: risposte e spiegazioni visibili subito, anche sulla risposta giusta e non solo sulle sbagliate. Tentativi e modalità del quiz **(aperto, A17)**: per ora si usano le impostazioni «esercitazione»; ricordale nel messaggio di consegna.
- Livelli di Bloom come la verifica teorica, senza pesi fissi. Progressione, pagine e regole sulle tracce **(aperto, A9)**.

## EP · Esercitazione pratica

- **Scopo**: solo esercizi, senza spiegazione; al massimo un richiamo breve degli argomenti, già spiegati in esercitazioni precedenti. Uso tipico: per casa, dopo la spiegazione e qualche esercizio in classe.
- Parti: richiamo breve, completamento, debugging, esercizio guidato, esercizi finali. Voto interno, indicazione dello strumento, durata e progressione **(aperto, A18)**.

## ER · Esercitazione complessiva di ripasso

- **Scopo**: rara, solo a inizio anno, per recuperare gli argomenti dell'anno precedente. Rispiega gli argomenti e procede come l'esercitazione con spiegazione, con profondità minore.
- **Partenza**: di solito dall'analisi dei quiz già pronti che spiegano gli argomenti da ripassare (export XML o backup `.mbz`, che `materiali-moodle` sa leggere). Da dove si prendono, come diventano scaletta e che cosa vuol dire «profondità minore» **(aperto, A16 e D14)**.
- Pagina del blocco con il prefisso «Ripasso».
