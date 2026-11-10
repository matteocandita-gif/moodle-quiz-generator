# Tipi di quiz e preset

Ogni quiz ha un tipo, e il tipo porta con sé un **preset**: le regole che la scaletta deve rispettare. La dashboard controlla le regole misurabili negli avvisi (punti, minuti, sequenza delle parti, sostegno del debugging, strumento); le altre le applichi tu scrivendo scaletta e tracce.

Ogni preset ha otto voci: scopo, progressione, tipologie, regole sulle tracce, punteggi e tempi, pagine e sezioni, sostegno e feedback, varianti. Le voci marcate **(da validare)** sono proposte non ancora provate su un quiz reale: applicale, ma dillo nella proposta. Le voci marcate **(aperto)** non sono decise: chiedi all'utente quando servono.

**Il preset di ogni tipo sta nel file della colonna «File del preset»: dopo questo file leggi quello del tipo scelto, e solo quello.**

| Sigla | Tipo | Impostazioni dell'.mbz | File del preset |
|---|---|---|---|
| LIB | Libero (senza preset) | scelte nel modulo (`presetMbz`) | qui sotto |
| ED | Esercitazione con spiegazione di dettaglio | esercitazione | `preset-esercitazioni.md` |
| EDT | Esercitazione con spiegazione, solo teoria | esercitazione | `preset-esercitazioni.md` |
| SD | Esercitazione con studio e domande sequenziale | studio | `preset-studio.md` |
| V | Verifica di programmazione (sottotipi: ripasso, dettaglio) | verifica | `preset-verifiche.md` |
| VT | Verifica teorica | verifica | `preset-verifiche.md` |
| RT | Ripasso teorico (verifica formativa) | esercitazione | `preset-verifiche.md` |
| EP | Esercitazione pratica | esercitazione | `preset-esercitazioni.md` |
| ER | Esercitazione complessiva di ripasso | esercitazione | `preset-esercitazioni.md` |

Impostazioni dell'.mbz, verificate su backup reali del Moodle della scuola (5.2):

- **esercitazione**: comportamento interattivo con più tentativi, tentativi illimitati, nessun limite di tempo, revisione completa durante il tentativo, subito dopo e a quiz aperto (risposte, punteggi, feedback, risposta giusta);
- **verifica**: feedback differito, un tentativo, tempo pari al tempo del quiz, durante la prova si vede solo il tentativo e il punteggio massimo; feedback, punteggi e risposte giuste si aprono dopo, alla restituzione, cambiando le opzioni di revisione del quiz (ricordalo nel messaggio di consegna);
- **studio**: navigazione sequenziale (non si torna alle pagine precedenti), feedback differito, un tentativo, tempo pari al tempo del quiz (40 minuti se manca); durante il tentativo nessuna verifica, revisione completa (risposte, punteggi, feedback, risposta giusta) subito dopo la consegna e dopo, finché il quiz è aperto. Provato con un ripristino reale il 24/10/2026.

**Impostazioni avanzate**: scorrimento, feedback, Safe Exam Browser e password le valorizza il tipo di quiz e si cambiano quiz per quiz nel pannello della pagina (campi `navigazione`, `feedback`, `seb`, `password`, in `dashboard.md`). Il tipo dà: scorrimento libero, forzato solo in SD; feedback immediato nelle esercitazioni, differito in verifiche e SD; SEB con file nelle verifiche di programmazione, manuale nelle verifiche teoriche, nessuno altrove; nessuna password.

Voto del quiz: 10, sufficienza 6, salvo indicazione diversa nel quiz della dashboard.

## LIB · Libero (senza preset)

- **Scopo**: un quiz che non rientra negli altri tipi, o per cui l'utente non vuole regole prefissate. È il primo tipo del modulo «Nuovo quiz».
- **Regole**: nessun preset. Tipologie, numero di domande, parti, punti, tempi e struttura vengono solo dalla `richiesta` del quiz; dove la richiesta non dice niente, scegli tu in modo ragionevole e scrivilo nelle `note`. Valgono comunque le regole generali di questa skill (domande di comprensione, tracce, convenzioni, pagine del quiz) e, per una verifica di programmazione, `verifiche-programmazione`. La dashboard non controlla punti, tempi, parti né tipologie: ammette tutte quelle del catalogo; usa le parti 0 (pagina) e 1 (domanda).
- **Impostazioni dell'.mbz**: le sceglie l'utente nel modulo, nel campo `presetMbz` del quiz (`esercitazione` o `verifica`, di norma `esercitazione`).
