# Criteri di punteggio e di commento

## La griglia generale

Si applica a ogni domanda di scrittura di codice, dentro la griglia specifica della riga (campo `correzione` della dashboard), quando questa non dice già come dare i punti parziali:

| Risposta | Fino al |
|---|---|
| corretta, salvo errori davvero marginali (una virgola, un punto e virgola) | 100% |
| logica e concetti corretti, con errori di sintassi | 80% |
| errori logici o di sintassi lievi | 60% |
| molto incompleta, o con errori logici o concettuali gravi | 40% |
| non svolta, o solo lo schema vuoto (`SELECT … FROM … WHERE` senza contenuto) | 0 |

- Punteggi a **mezzi punti** sulle domande da 5 punti in su; ai decimi solo dove il massimo è 1 o 2.
- **Errori di battitura**: non si penalizzano (un nome di tabella o di variabile sbagliato di una lettera, un anno scritto 2015 al posto di 2025) se non mostrano un concetto non capito. Se gli studenti potevano provare il codice e il risultato vuoto avrebbe dovuto insospettirli, si toglie al massimo mezzo punto. Se l'utente decide una griglia più severa per chi poteva provare il codice, segui la sua.
- **Le alternative corrette non sono errori**: `BETWEEN` o `>=` e `<=`, `LIKE '2025%'` per un anno, `COUNT(*)` o `COUNT(campo)`, la concatenazione PHP al posto dell'interpolazione, `GROUP BY c.Nome, c.Livello` dove la coppia è unica. Le convenzioni dei linguaggi della skill valgono per il codice che scriviamo noi, non per gli studenti (`verifiche-programmazione`).
- **Risultato giusto per caso**: righe giuste ma con una JOIN inutile, che in altri dati darebbe righe ripetute o perse, oppure un `GROUP BY` che funziona solo con quei dati. Si toglie un punto o un punto e mezzo su 6, spiegando il caso in cui sbaglierebbe.
- **Una sola causa, un solo errore**: se lo stesso errore si ripete in più domande (la data scritta senza apici), si toglie in ognuna, ma il commento lo spiega per intero solo la prima volta e poi lo richiama in breve.

## Casi già decisi dall'utente

Riprendili tali e quali se si ripresentano. Se una verifica nuova li contraddice, chiedi.

- **Data confrontata con un numero** (`DataAssunzione < 2018`, `DataIscrizione = 2025`): MySQL lo accetta convertendo la data, SQLite no, e il correttore restituisce zero righe. È un errore di sintassi con la logica giusta: fino all'80% (4,5 su 6).
- **Date senza apici o in formato italiano** (`2025-01-01`, `01-01-2025`, `2025/01/01` senza apici): errore di sintassi, fino all'80% se il resto è giusto.
- **Pari merito in un altro ordine**, quando la traccia chiede un solo criterio di ordinamento e i dati hanno pari merito: risposta corretta, punteggio pieno, anche se Moodle l'ha messa a 0. Controlla con lo script che l'ordinamento richiesto sia rispettato davvero.
- **JOIN interna con `IS NULL` per «chi non ha»**: l'idea di cercare il campo vuoto è giusta, manca la LEFT JOIN. Vale il 40–50%.
- **Condizione rovesciata** (`IS NOT NULL` per le iscrizioni attive, `>` al posto di `<`): errore logico lieve se tutto il resto è giusto, il 60% circa.
- **GROUP BY sul nome invece che sulla chiave**, quando ci sono omonimi nei dati (corsi Yoga di livelli diversi, due istruttori con lo stesso nome): errore logico, il 60% circa. È di solito la trappola della domanda.
- **Manca il GROUP BY** in una domanda di raggruppamento: è il concetto della domanda, quindi il 40%, anche se JOIN, COUNT e ordinamento sono giusti.
- **Pagina PHP**: si valutano le fasi (lettura dei dati del form, connessione, query, esecuzione, chiusura, elaborazione con il controllo delle righe e il ciclo). Ripartizione usata su 18 punti: dati 2, connessione 3, query 6, esecuzione 2, elaborazione 5. Poi si applica la griglia generale. I tag HTML dentro le `echo` non si vedono nell'export e non si valutano.
- **Teoria aperta**: punti per richiesta, come nella griglia della riga. Una risposta che risponde ad altro vale 0 su quella richiesta, anche se ciò che dice è giusto.

## Il commento

L'utente lo incolla in Moodle per lo studente, che lo legge alla restituzione.

- **Solo se il punteggio non è pieno.** Con il punteggio pieno il campo resta vuoto.
- **Breve e fattuale**: due o quattro frasi. Prima che cosa è giusto, in poche parole, poi ciò che manca o è sbagliato e **la forma corretta**, cioè la condizione, la clausola o il passaggio giusto, scritto in chiaro. Niente lodi generiche, niente «ottimo lavoro ma».
- Per gli errori di sintassi, «Sintassi:» seguito dall'errore e dalla forma corretta, in una frase a parte, così lo studente distingue la logica dalla forma.
- Nella teoria, per le richieste sbagliate o mancanti, la risposta attesa in una o due frasi. Un commento lungo che rispiega tutta la domanda non serve.
- **Paragrafi**: con più richieste, un paragrafo per richiesta (a capo prima di «Richiesta 2: …», «Manca la richiesta 3. …»); la frase «Sintassi:» in un paragrafo a parte; nei commenti lunghi su una pagina intera (HTML, PHP) un paragrafo per ogni parte. Gli a capo si scrivono come \n nel testo: la pagina li copia in Moodle come paragrafi.
- **Un concetto per riga**: gli studenti spesso scorrono il commento senza leggerlo, quindi ogni frase va su una riga sua (il giudizio, l'output atteso, ogni errore con la sua correzione), anche dentro la stessa richiesta e anche nei commenti brevi. Vale anche per il punto e virgola: due concetti scollegati non si uniscono con «;» ma vanno su due righe («Le chiamate vanno fatte con le lezioni lette, `costoCorso(lezioniAnna)`.» / «`console.log=Anna` non stampa, …»). Restano insieme solo le coppie che si spiegano a vicenda (`x` e `y` sono i parametri…; 6 e 8 sono gli argomenti…). I due punti tengono insieme sulla stessa riga la spiegazione e la correzione dello stesso errore. Esempio: «**Richiesta 1:** il codice stampa `Somma: NaN`.» / «Gli errori sono individuati, ma manca il perché: con `i <= voti.length` … la condizione giusta è `i < voti.length`.» / «`somma = 0` dentro il `for` … la riga va tolta dal ciclo.», su tre righe.
- **Testo semplice, con il codice tra apici inversi**: niente altro Markdown (a parte il grassetto, sotto) e niente elenchi, ma ogni pezzo di codice (istruzioni, condizioni, nomi di variabili e di funzioni, testo stampato riportato esattamente) va tra apici inversi: `let i = 0`, `i < voti.length`, `$_GET["giorno"]`. La pagina lo copia in Moodle come codice (`<code>`) e sotto il commento ne mostra l'anteprima; le parole comuni che sono anche nomi di variabili si marcano solo quando indicano la variabile.
- **Blocchi di codice**: quando la correzione ha più di due istruzioni (una funzione con il corpo, un ciclo, un `if` con i rami, un programma) si scrive come blocco, tra una riga ```js e una riga ```, con gli a capo e i rientri, non tutta su una riga. Le spiegazioni brevi possono stare nel blocco come commenti in linea (`// si conta`), oppure si riscrive la frase che introduce il blocco. La pagina lo copia in Moodle come `<pre><code>`.
- **Grassetto: etichette e poche parole chiave**, tra `**` e `**`, per guidare la lettura senza appesantire. In grassetto vanno le etichette all'inizio del paragrafo («**Richiesta 2:**», «**Primo errore:**», «**Frammento A:**», «**Sintassi:**», «**Manca la richiesta 3:**», «**Risposta appena impostata:**»), il giudizio breve nella prima frase («Output e differenza **corretti**.») e al massimo due o tre parole chiave per paragrafo, quelle che dicono l'errore («**che non esiste**», «**riporta la somma a zero a ogni giro**»). Mai dentro il codice, né in linea né nei blocchi, e non nella riga «Clicca su «Mostra/Nascondi soluzione dell'autore»…». La pagina lo copia in Moodle come `<b>`; nella copia come testo semplice gli asterischi si tolgono.
- **La frase sull'IA non va nel commento**: la aggiunge la pagina, in corsivo, quando si copia («Il seguente feedback è stato scritto con l'aiuto di una IA generativa. La valutazione è stata svolta dal docente.»). Se l'utente vuole un'altra frase, si cambia con `--disclaimer` di `prepara_revisione.py`.
- **Risposta non svolta**: «Risposta non svolta.» Se c'è solo lo schema: «Risposta appena impostata: …» e che cosa manca.
- **Domande CodeRunner non svolte o completamente sbagliate** (fino al 20% del massimo, oppure con il codice di un'altra domanda): ogni domanda CodeRunner ha la soluzione dell'autore, quindi niente soluzione intera nel commento. Una o due frasi sull'errore principale (e l'eventuale «Sintassi:»), poi a capo: «Clicca su «Mostra/Nascondi soluzione dell'autore» per vedere un esempio di soluzione corretta.» Per gli errori puntuali, invece, il commento li indica e riporta il pezzo di codice giusto.
- Tono neutro e rispettoso: si parla della risposta, mai dello studente.
