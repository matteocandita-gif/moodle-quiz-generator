# Come è cresciuto il plugin

Una panoramica delle funzioni del plugin «Moodle: quiz generator». Non corrisponde versione per versione: il registro dettagliato è in `CHANGELOG.md`.

## Progettare un quiz

- Si parte dalla dashboard «Bozze dei quiz»: scegli il tipo di quiz, Claude propone la scaletta con punti, tempi e distribuzione sulle pagine, poi scrive le tracce. Tu approvi o correggi passo per passo.
- Ci sono preset per i tipi di quiz di uso corrente: esercitazione con spiegazione (anche solo teoria), esercitazione pratica, complessiva di ripasso, ripasso teorico, verifica di programmazione e verifica teorica. C'è anche un tipo libero, senza regole.
- **Nuovo template: Esercitazione con studio e domande sequenziale.** La teoria è in parti brevi e, dopo ogni parte, ci sono le domande, senza poter tornare indietro. Le chiuse verificano definizioni e dettagli. L'aperta verifica l'esposizione del concetto generale, senza chiedere una definizione da riscrivere.
- Le verifiche di programmazione hanno regole didattiche proprie per struttura, taratura del voto e parte avanzata. Si possono fare verifiche ripetibili con varianti.

## Domande

- Cloze, risposta multipla, vero/falso, risposta breve, corrispondenza e risposta aperta, più la consegna di un file.
- Domande di codice a correzione automatica con CodeRunner: JavaScript, SQL e PHP/MySQL. Per SQL e PHP girano su database didattici di prova, con dati italiani coerenti, in tre taglie.
- Pagine di teoria con riquadri, snippet HTML con l'anteprima accanto e immagini.

## Progettazione dei database

- Diagrammi E/R nella notazione del libro, come file `.drawio` e PNG.
- Schema relazionale con le regole di traduzione del libro, documentazione della base di dati e soluzione completa di una traccia. I moduli si usano separatamente: per un quiz basta il diagramma.

## Consegna in Moodle

- Backup `.mbz` pronto da ripristinare, con le impostazioni giuste per ogni tipo di quiz.
- **Depositi**: le domande vanno direttamente nella banca del corso deposito, e quelle già presenti sono riusate senza doppioni.
- **Copia PDP**: la scegli in progettazione con la casella «tolta nella PDP» e la ottieni dalla dashboard o da un backup.
- Importazione di un quiz da un backup e confronto con la dashboard, per riportare le correzioni fatte in Moodle.

## Correzione delle verifiche

- Si parte dall'export di Moodle con i nomi tolti nel browser.
- Claude riesegue le risposte di codice con i test, propone punteggi e commenti domanda per domanda e prepara la dashboard di correzione per domanda o per studente.

## Mappe dei prerequisiti

- Mappe di autovalutazione per gli studenti, in un'attività Database di Moodle. Il docente vede il riepilogo della classe. C'è un editor per crearle e provarle.
