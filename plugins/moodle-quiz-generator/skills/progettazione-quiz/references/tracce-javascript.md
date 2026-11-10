# Tracce delle domande CodeRunner JavaScript

Da leggere quando il quiz ha domande CodeRunner JavaScript. Fa parte delle regole sulle tracce di `progettazione-quiz` (`SKILL.md`, «Le tracce»): le regole generali (tracce estese, convenzioni, feedback, correzione e note interne) restano lì e valgono anche qui. Le convenzioni generali della traccia (riquadri, scelte, campi Cloze, immagini) sono in `formato-consegna.md`; il formato del campo «Soluzione e test» di queste domande è qui sotto.

## Domande CodeRunner JavaScript

La `traccia` è il testo della domanda, con le stesse convenzioni delle altre ma **senza campi Cloze né opzioni**; gli output d'esempio vanno in blocchi ```` ```semplice ````. La `correzione`, se c'è, diventa il feedback generale. Soluzione e test stanno nel campo `coderunner` («Soluzione e test» nella dashboard), a sezioni `=== nome` come nella specifica di `domande-coderunner-js`:

| Sezione | Contenuto |
|---|---|
| `=== answer` | obbligatoria: la soluzione di riferimento (nel gapfiller una riga per spazio, in ordine) |
| `=== test` | almeno tre: il codice del test, che comincia con un commento che dice che cosa prova (`// 65 anni: ridotto (caso limite)`); `=== test HIDE` per un test nascosto |
| `=== stdin` | dopo un `=== test`: le risposte ai `prompt`, una per riga |
| `=== extra`, `=== expected` | dopo un `=== test`, solo se servono (di norma l'output atteso lo calcola Node) |
| `=== code` | solo gapfiller: il codice con gli spazi `{[larghezza]}` o `{[predefinita-massima]}` |
| `=== preload` | codice di partenza nella casella (debug: il codice con l'errore; codice parziale: la parte già scritta, per esempio la funzione da usare) |
| `=== options` | opzioni della specifica, una per riga, per esempio `esempi: tutti` (`defaultgrade` viene dai punti della riga) |

Il dettaglio delle sezioni e delle opzioni è in `references/formato-specifica.md` di `domande-coderunner-js`.

Il prototipo è «Javascript (con gapfiller)» se la tipologia è `compl_eseguito` o c'è `=== code`, altrimenti «Javascript (con prompt)». Nei test di un programma con `prompt` il codice del test è spesso solo il commento: i valori stanno in `=== stdin`. Due test con lo stesso output non distinguono nulla: scegli dati che diano output diversi. La dashboard mostra il codice da completare o di partenza nel foglio dello studente e soluzione e test nel riquadro del docente, e segnala negli avvisi le sezioni mancanti, gli spazi che non corrispondono alle risposte, `alert` o `document` nella soluzione.

## In più, scrivendo le tracce

- Scegli dati di test che, oltre a dare output diversi tra loro, coprano i casi limite.
- Verifica soluzione e codice di partenza con Node prima di scriverli.
- Le convenzioni JavaScript (niente `alert` né `document`, `prompt` e `console.log`) sono quelle di `domande-coderunner-js`.
