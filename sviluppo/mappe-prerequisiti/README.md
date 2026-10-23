# Sorgenti dell'editor «Mappe dei prerequisiti»

La pagina `plugins/moodle-quiz-generator/skills/mappe-prerequisiti/assets/editor.html` si costruisce da questi file:

| File | Che cosa contiene |
|---|---|
| `editor.src.html` | la pagina dell'editor (stile, struttura, logica), con i segnaposto `/*@@RUNTIME@@*/`, `/*@@MOODLE@@*/`, `/*@@PRESET@@*/`, `/*@@MBZ@@*/` |
| `src/lh-runtime.js` | impaginazione a strati e disegno SVG della mappa, senza librerie esterne; usato dall'editor e dall'attività Moodle |
| `src/lh-moodle.js` | collegamento con l'attività Database: spunte dello studente, scheda singola, riepilogo del docente |
| `src/lh-preset.js` | i file del preset dell'attività (modelli, campo `voci`, CSS, JavaScript con la mappa) |
| `src/lh-mbz.js` | il backup `.mbz` dell'attività (modello: backup di Moodle 5.2) e l'archivio tar |

Per ricostruire, dalla radice del repository:

```
node sviluppo/mappe-prerequisiti/costruisci_editor.js
```

Dopo una modifica alza `VERSIONE_PAGINA` in `editor.src.html` (così la skill propone l'aggiornamento agli utenti) e segna la versione nel CHANGELOG con **Editor mappe**. Lo script `scripts/crea_mbz.js` della skill prende il codice da `editor.html`: non ha bisogno di essere ricostruito.
