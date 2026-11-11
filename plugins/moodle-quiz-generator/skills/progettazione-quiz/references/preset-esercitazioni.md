# Preset delle esercitazioni: ED, EDT, EP, ER

Da leggere quando il tipo di quiz è ED o EDT o EP o ER, dopo `preset.md` (che ha la tabella dei tipi, le impostazioni dell'`.mbz` e le voci comuni a tutti i preset).

**Il voto arriva alla consegna** (ED, EDT, EP, ER): completare l'esercitazione dà subito il voto, senza aspettare la correzione del docente. Per questo:

- ogni consegna di file è una «Consegna con controllo automatico» (`consegna_auto`, regole in `tracce-consegna.md`), mai una «Consegna di un file», che resta per le verifiche;
- le domande da correggere a mano scritte a parole (`esercizio_libero`, `teoria_aperta`, `debug_motivazione`) hanno **0 punti**: lo studente risponde, il docente le legge quando vuole, e il voto non resta in sospeso. La dashboard avvisa se hanno punti. Gli esercizi HTML e CSS (`libero_html`, `libero_css`) danno già i punti a ogni risposta non vuota e restano per gli esercizi brevi nella casella di risposta.

Il voto attesta che il lavoro è stato consegnato (e, nelle consegne di file, che il file c'è ed è in ordine), non che sia corretto.

## La ripetizione (ED, EDT, ER)

Ripetere subito la stessa operazione aiuta a fissarla: la prima volta lo studente capisce il tipo di esercizio, la seconda lo riapplica. Vale per tutte le esercitazioni, già nella scaletta.

- **Domande di comprensione doppie**: una domanda che chiede di **eseguire un procedimento su un caso concreto** (classificare, leggere il codice, riconoscere un errore, prevedere un risultato, «dal risultato al codice») si fa due volte, **sulla stessa pagina del quiz**, ogni volta che serve una conferma di comprensione. La seconda ha la stessa struttura, materiale nuovo e **risposta diversa**: cambia la superficie (elementi, valori, posizione e forma della risposta giusta, errori in punti diversi) e varia ciò che nella prima poteva passare senza capire. Vale meno punti e richiede meno minuti.
- **Non si raddoppia** una domanda su un **principio**, che ha la stessa risposta in ogni contesto (per esempio «perché separare HTML e CSS»): la seconda sarebbe la stessa domanda con la stessa risposta.
- **Feedback delle due domande**: quello della prima spiega il procedimento; quello della seconda dice solo dove si è sbagliato («No: controllate il selettore»), e la spiegazione completa sta nella `correzione`. Nessuno dei due svela l'altra domanda, che sta sulla stessa pagina.
- **Esercizi pratici brevi**, svolti dentro Moodle (CodeRunner, esercizio con controllo): due volte, la prima con lo strumento **suggerito**, la seconda con il solo obiettivo (strumento **non nominato**), su un caso diverso.
- **Esercizi lunghi con una consegna di file**: una volta sola.
- **Esercizio finale**: ha un doppio **per casa**, in un **quiz separato** di tipo EP (non in fondo all'esercitazione), con il titolo che dice che è per casa («1-CSS per casa: …», nome del quiz «Per casa - …»): stessa struttura e stessi criteri dell'esercizio finale, contesto e valori nuovi. La soluzione di riferimento sta nella `correzione`, così lo studente la vede nella revisione dopo la consegna. Le istruzioni del quiz dicono che è il lavoro per casa e che cosa serve.

## ED · Esercitazione con spiegazione di dettaglio

- **Scopo**: spiegare un argomento nuovo e farlo esercitare in una lezione base di due ore. Completarla dà un voto che gli studenti non vedono e che non viene verbalizzato: punteggi con un criterio semplice, senza formalizzare troppo.
- **Progressione**: «Come lavoriamo oggi» in apertura, poi uno o più blocchi; in ogni blocco le parti in quest'ordine: pagina del blocco (introduzione e spiegazione, con l'esempio svolto in un riquadro giallo), esempio svolto da leggere, completamento, debugging, esercizio guidato. In fondo gli esercizi finali. Il debugging viene dopo il completamento. **Ogni blocco chiude con almeno un esercizio libero**, da scrivere da zero (funzione o programma, senza codice da completare né da correggere): non basta il guidato. Il numero di blocchi e di esercizi dipende dall'argomento: non ci sono numeri fissi.
- **Tipologie**: quelle con ED nel catalogo. Debugging: con messaggi e silenzioso con CodeRunner dove si può (JavaScript, SQL, PHP); in HTML «Trova l'errore», perché il browser non dà errori; in CSS anche l'«Esercizio con controllo» con il codice da correggere nella casella (`=== preload`), perché il controllo trova graffe, due punti e punti e virgola sbagliati. Esercizi finali: CodeRunner; in HTML e CSS l'«Esercizio con controllo» quando il controllo automatico basta (una regola, lo stile in linea, un `<style>`), altrimenti «Esercizio HTML» o «Esercizio CSS» (editor di CodeRunner senza test, correzione manuale) per gli esercizi brevi, e la «Consegna con controllo automatico» quando lo studente crea file nel suo computer (una pagina, la cartella del sito).
- **Esercizi finali**: non per forza uno solo. Dove gli esercizi sono brevi se ne fanno altri simili (stessa struttura e difficoltà, contesto diverso). Quando la lezione introduce uno strumento di programmazione (per esempio l'early return) si fanno più esercizi complessivi **(aperto: «complessivi» vuol dire che combinano lo strumento nuovo con argomenti già visti? A14)**.
- **Regole sulle tracce**: estese ed esplicite, in forma impersonale. Lo strumento si può nominare: per ogni esercizio l'utente sceglie nella scaletta se è **suggerito** o **non nominato**. Dove lo strumento non è scontato lo si suggerisce, dove la competenza dovrebbe essere acquisita si dà solo l'obiettivo. Proposta di partenza **(da validare)**: strumento della lezione suggerito nel guidato e nei primi finali, non nominato negli ultimi; strumenti di lezioni precedenti non nominati.
- **Punteggi e tempi**: 100 punti. Pesi per parte **(da validare)**: esempio svolto e completamento 20, debugging 25, esercizio guidato 20, esercizi finali 35; dentro una parte i punti si dividono in parti uguali, il peso dei finali può salire quando si introduce uno strumento. Minuti orientativi **(da validare)**: pagine 10-15 in tutto, esempio svolto e completamento circa 15, debugging 15, guidato 15, finali 25. Una lezione di due ore ha **105 minuti** disponibili (non 90): è il `tempo` da proporre per una ED, e la somma dei minuti deve starci con almeno 5 minuti di margine.
- **Pagine e sezioni**: le pagine di spiegazione stanno dentro il quiz come descrizioni, compresa «Come lavoriamo oggi». Ogni pagina di spiegazione o di esempio svolto ha sulla stessa pagina del quiz la sua prima domanda, e una pagina che chiede di fare qualcosa diventa una domanda con il controllo («Ogni pagina con la sua domanda» e «Pagine che chiedono di fare qualcosa» in `tracce-pagine.md`). Una sezione del quiz per l'introduzione e una per blocco, più quella degli esercizi finali. Le domande complesse (programmazione, esercizi liberi) su una pagina da sole.
- **Sostegno e feedback**: nel debugging il sostegno cala lungo la sequenza: prima quanti errori e dove, poi solo quanti, poi nessuna indicazione. Ogni errore è legato a un concetto della lezione. Feedback su ogni opzione sbagliata, visibile subito.
- **Varianti**: nessuna variante prevista **(da validare, A13)**. Argomenti senza codice: preset EDT.

## EDT · Esercitazione con spiegazione, solo teoria

Deciso il 2026-10-09 dopo il quiz «Internet e il Web» (chiude A12).

- **Scopo**: spiegare un argomento di sola teoria (senza codice) e verificare subito la comprensione. Come ED: voto interno, non visto né verbalizzato.
- **Quando**: se la richiesta mescola teoria e pratica (per esempio «che cos'è il Web» e poi HTML), proponi due quiz, uno EDT per la teoria e uno ED per la pratica, e chiedi all'utente prima di scrivere la scaletta.
- **Progressione**: «Come lavoriamo oggi» (parte 0), poi blocchi; in ogni blocco una o più **pagine di spiegazione** (parte 1), ognuna seguita subito dalle sue **domande di comprensione** (parte 2): la prima sulla stessa pagina del quiz della spiegazione, le altre sulla pagina successiva. Una pagina di spiegazione tratta un argomento, al massimo due: se ne tratta di più si divide, anche dentro lo stesso blocco (B0, poi le sue domande, poi B6 e le sue).
- **Tipologie**: vero/falso, risposta multipla (una o più giuste), risposta breve, completamento di testo, metti in ordine, corrispondenza.
- **Regole sulle domande**: i criteri delle domande di comprensione nella skill `progettazione-quiz`.
- **Punteggi e tempi**: 100 punti, tutti nelle domande di comprensione, a multipli di 5; nei Cloze un campo ogni 5 punti. Pagine senza punti. Tempo da decidere quiz per quiz (30 minuti per «Internet e il Web»), con almeno 5 minuti di margine.
- **Pagine e sezioni**: una sezione per l'introduzione e una per blocco. La prima domanda di una pagina di spiegazione sta sulla stessa pagina del quiz, sotto la spiegazione; le altre insieme sulla pagina che la segue.
- **Sostegno e feedback**: feedback su ogni opzione, visibile subito; non deve svelare la risposta di un'altra domanda della stessa pagina.
- **Nomi**: la pagina di spiegazione ha il prefisso «Spiegazione», come in ED.

## EP · Esercitazione pratica

- **Scopo**: solo esercizi, senza spiegazione; al massimo un richiamo breve degli argomenti, già spiegati in esercitazioni precedenti. Uso tipico: per casa, dopo la spiegazione e qualche esercizio in classe.
- Parti: richiamo breve, completamento, debugging, esercizio guidato, esercizi finali. Quando è il doppio per casa dell'esercizio finale di un'esercitazione («La ripetizione», sopra): una pagina di istruzioni e la sola consegna, 100 punti. Voto interno, indicazione dello strumento, durata e progressione **(aperto, A18)**.

## ER · Esercitazione complessiva di ripasso

- **Scopo**: rara, solo a inizio anno, per recuperare gli argomenti dell'anno precedente. Rispiega gli argomenti e procede come l'esercitazione con spiegazione, con profondità minore.
- **Partenza**: di solito dall'analisi dei quiz già pronti che spiegano gli argomenti da ripassare (export XML o backup `.mbz`, che `materiali-moodle` sa leggere). Da dove si prendono, come diventano scaletta e che cosa vuol dire «profondità minore» **(aperto, A16 e D14)**.
- Pagina del blocco con il prefisso «Ripasso».
