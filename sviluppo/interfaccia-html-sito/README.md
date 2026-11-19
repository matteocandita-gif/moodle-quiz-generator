# Interfaccia `html_sito` di CodeRunner

L'editor del sito delle domande «Sito con l'editor» (tipologia `sito_html`): un'interfaccia di CodeRunner (come Ace, Html, Table) in cui lo studente crea cartelle e file del sito, li scrive con l'editor Ace di CodeRunner e vede l'anteprima delle pagine. Resta nel repository: ai colleghi arriva solo l'interfaccia costruita, in `plugins/moodle-quiz-generator/skills/materiali-moodle/assets/interfaccia-html-sito/`, con lo script di installazione (istruzioni in `materiali-moodle/references/interfaccia-html-sito.md`).

## I file

| File | Che cosa contiene |
|---|---|
| `modulo.js` | il codice dell'interfaccia (modulo AMD `qtype_coderunner/ui_html_sito`, con i segnaposto `__VERSIONE__` e `__STILE__`): **si modifica qui** |
| `stile.css` | lo stile, che `build.py` mette dentro il modulo |
| `build.py` | costruisce `ui_html_sito.js` negli asset del plugin, con la versione scritta in testa allo script |
| `prova/prova-coderunner.html` | pagina di prova: simula una domanda CodeRunner (wrapper dell'interfaccia, `sync()` ogni 2 secondi e all'invio, salvataggio automatico del quiz nel localStorage, revisione in sola lettura, Ctrl-Alt-M); usa l'asset costruito |
| `prova/ace/` | Ace (ace-builds, licenza BSD) solo per la pagina di prova: in Moodle Ace lo carica CodeRunner |

## Modificare l'interfaccia

1. Modifica `modulo.js` o `stile.css`.
2. Alza `VERSIONE` in `build.py` e lancia `python3 build.py`.
3. Prova con `prova/prova-coderunner.html` (serve un piccolo server, per esempio `python3 -m http.server` dalla radice del repository, poi `/sviluppo/interfaccia-html-sito/prova/prova-coderunner.html`; con `?aiuti=1` gli aiuti e il caricamento di immagini, con `?attempt=1` la copia nel browser).
4. Nel CHANGELOG: che l'interfaccia è cambiata e che l'amministratore deve rilanciare `installa.sh` e svuotare le cache.

## Cose da sapere

- **Il nome deve contenere «html»**: CodeRunner carica Ace solo per le interfacce il cui nome contiene `ace`, `html` o `scratchpad`.
- **CodeRunner trova le interfacce** cercando `ui_*.js` in `amd/src`; Moodle carica il modulo da `amd/build/*.min.js`. Per questo `installa.sh` copia lo stesso file nei due posti (non serve minificarlo). Il `define` ha il nome del modulo, così funziona anche quando Moodle unisce più moduli in una risposta.
- **Metodi richiesti dal wrapper** di CodeRunner (`userinterfacewrapper.js`): costruttore `(textareaId, w, h, params)` solo sincrono e leggero, `failed()`, `failMessage()`, `getElement()`, `sync()` (ogni `syncIntervalSecs()` secondi e all'invio del modulo), `destroy()`, `resize(w, h)`, `hasFocus()`, `allowFullScreen()`, `setAllowFullScreen()`; facoltativo `postInsert()`, dove si crea Ace (l'elemento è già nella pagina).
- **Sola lettura**: il wrapper non la passa all'interfaccia; si legge dall'attributo `readonly` della textarea.
- **Altezza**: il contenitore del wrapper cresce con l'editor; `resize()` segue solo i ridimensionamenti voluti (più di 30 px), per non entrare in un ciclo con l'altezza del contenitore.
- **Sicurezza**: l'anteprima è un iframe `srcdoc` con `sandbox="allow-scripts"` senza `allow-same-origin`: il codice dello studente non può leggere la pagina di Moodle. Le immagini e i CSS entrano nella pagina come data URL e testo; un `<base>` verso un indirizzo inesistente impedisce le richieste al server di Moodle.
- **Formato della risposta**: `{"htmlve": 1, "versione", "salvato", "cartelle", "files", "immagini"}`. La chiave `htmlve` resta così anche se il nome dell'interfaccia è cambiato: il template di `html_con_file` (`sviluppo/prototipo-html-con-file/template.py`, `sito_dall_editor`) la cerca.
