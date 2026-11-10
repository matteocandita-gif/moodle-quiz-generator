# Moodle: quiz generator — istruzioni per chi lavora nel repository

Rispondi sempre in italiano. Il repository lo modifica solo Claude, su richiesta dell'autore (Matteo Candita): lui non lavora mai da solo su GitHub.

## Che cosa c'è

- `plugins/moodle-quiz-generator/`: il plugin che ricevono l'autore e i colleghi (skill, comandi, pagine in `assets/`).
- `sviluppo/`: strumenti che restano nel repository e non vanno ai colleghi.
- `CHANGELOG.md`, `README.md`, `GUIDA.md`, `PANORAMICA.md`: documenti per chi usa il plugin.

## Regole per le modifiche

1. **Prima di una modifica grossa, proponila** all'autore e aspetta il suo ok.
2. **File condivisi**: alcuni file stanno in più skill. Si modifica solo l'originale, poi `python3 sviluppo/strumenti/allinea_copie.py`. Le copie cominciano con una riga «COPIA di …»: non toccarle. Il blocco «Il percorso dei quiz», uguale in sei skill, sta tra due commenti `percorso-dei-quiz` e si modifica solo in `sviluppo/strumenti/percorso-dei-quiz.md`. Le regole comuni a tutte le domande si modificano solo in `materiali-moodle/references/regole-comuni.md`.
3. **Una regola in un posto solo**: prima di scriverla cerca se esiste già (`grep`), e aggiorna quella. In `SKILL.md` sta ciò che vale sempre; ciò che serve solo a volte sta in un file di `references/`, citato nella tabella dei file di riferimento con la condizione per leggerlo.
4. **Spostare testo da un file all'altro**: dopo lo spostamento controlla che non si sia perso niente con `python3 sviluppo/strumenti/equivalenza.py CARTELLA_DI_PRIMA CARTELLA_DI_DOPO` (salva prima una copia della skill).
5. **Pagine** (`assets/*.html`): se cambi una pagina alza la sua `VERSIONE_PAGINA`. L'editor delle mappe si rigenera con `node sviluppo/mappe-prerequisiti/costruisci_editor.js`.

## Prima di ogni rilascio

1. `python3 sviluppo/prove/prova_tutto.py` deve dire «TUTTO A POSTO». Se segnala un problema, segui il suo «CHE COSA FARE». **Non modificare lo script delle prove e non aggiornare il risultato atteso per farlo passare**: le istruzioni sono in `sviluppo/prove/README.md`.
2. Versione in `plugins/moodle-quiz-generator/.claude-plugin/plugin.json`: i rilasci intermedi sono correzioni (0.13.7 → 0.13.8); la versione minore (0.14.0) si alza solo a fine di un blocco di lavoro, quando lo dice l'autore. Se cambia solo `sviluppo/`, la versione non si alza.
3. `CHANGELOG.md`: una voce in cima, con la data e le novità in parole semplici (lo leggono i colleghi).
4. Commit con il messaggio `0.13.8: che cosa cambia in una riga`, poi `git push origin main`. Si pubblica solo quando l'autore lo chiede.
5. Nella risposta all'autore: che cosa è cambiato, l'esito delle prove, che cosa deve fare lui (di solito niente; se è cambiata una pagina, aggiornarla).
