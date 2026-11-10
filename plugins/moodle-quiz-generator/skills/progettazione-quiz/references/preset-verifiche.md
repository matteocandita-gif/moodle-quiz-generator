# Preset delle verifiche e del ripasso teorico: V, VT, RT

Da leggere quando il tipo di quiz è V o VT o RT, dopo `preset.md` (che ha la tabella dei tipi, le impostazioni dell'`.mbz` e le voci comuni a tutti i preset).

## V · Verifica di programmazione

- **Scopo**: valutare. Due sottotipi, **ripasso** (tutti gli argomenti ripassati, un esercizio non troppo complesso per argomento, teoria facile sui fondamentali) e **dettaglio** (uno o due argomenti vicini, più esercizi di difficoltà crescente).
- **Regole didattiche**: carica `verifiche-programmazione` (JavaScript, SQL, PHP), che decide struttura, taratura del voto, teoria, debug e tracce. Gli argomenti della parte avanzata (quelli per il 9 e il 10) li decide l'utente verifica per verifica: chiedili tra le informazioni essenziali. Per HTML e CSS, senza correzione automatica, restano lettura del codice, «Trova l'errore» ed «Esercizio HTML» / «Esercizio CSS» a correzione manuale **(da ripensare, A3)**. Teoria nella verifica di dettaglio: da concordare **(aperto, A4)**.
- **Regole sulle tracce**: consegne chiare sull'obiettivo, **senza** indicare gli strumenti da usare, salvo ciò che è oggetto della valutazione. Niente codice completo e copiabile che dia la soluzione di esercizi simili. Niente gapfiller nelle verifiche sommative: devono saper scrivere codice completo. Esercizio libero a correzione manuale ammesso, con indicazioni per il correttore e punti per criterio.
- **Punteggi e tempi**: 100 punti, parte base 85 e parte avanzata 15. La somma dei tempi consigliati sta intorno ai tre quarti del tempo disponibile; il resto serve per provare il codice e rileggere.
- **Pagine e sezioni**: istruzioni in apertura; niente sezioni che rivelino la parte avanzata.
- **Sostegno e feedback**: feedback scritto in tutte le domande, nascosto durante la prova e svelato alla restituzione (impostazioni «verifica»). Le domande CodeRunner seguono le loro opzioni anche con il feedback differito: lo studente prova il codice e vede il risultato dei test (in tutti i linguaggi); non si nasconde il pulsante di controllo, salvo negli esercizi HTML e CSS, che hanno un test fittizio.
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
