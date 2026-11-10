# Quiz già in Moodle: aggiornarlo e riallineare la dashboard

Da leggere quando il quiz è già in Moodle: gli studenti l'hanno svolto e va aggiornato, oppure l'utente ha corretto delle domande direttamente lì. Fa parte di `materiali-moodle`: il percorso, i passi della generazione e le regole generali stanno in `SKILL.md`.

## Aggiornare un quiz già in Moodle

Un quiz che gli studenti hanno già svolto **non si elimina**: resta per lo storico, con i suoi tentativi e le sue domande. In Moodle un quiz con tentativi ha la struttura bloccata: non si aggiungono né si tolgono domande e non si cambiano ordine e pagine. Si possono cambiare i testi (Moodle crea una nuova versione della stessa domanda, e i tentativi fatti restano sulla vecchia) e i punti (Moodle ricalcola i voti).

Per la versione nuova, da far svolgere a un'altra classe o l'anno dopo, l'utente fa una **copia del quiz** nel corso deposito e la aggiorna a mano, senza duplicare le domande. Dopo aver aggiornato le righe nella dashboard e rigenerato l'XML, prepara:

1. una **pagina** (artefatto) con in cima la tabella del quiz finale, presa da `impaginazione.json`: pagina, domanda, punti e che cosa fare (invariata, incolla il testo, domanda nuova da importare, sposta, togli, punti cambiati); sotto, i testi delle domande cambiate (il `<questiontext>` dell'XML), ognuno con il pulsante «Copia HTML» e le istruzioni: Modifica, modalità sorgente (HTML), seleziona tutto, incolla, salva;
2. un **XML con le sole domande nuove**, con in testa la categoria del quiz; nell'importazione l'utente toglie la spunta a «Ottieni categoria dal file»;
3. l'elenco delle domande da **togliere** dalla copia: una pagina che diventa domanda cambia tipo, quindi è una domanda nuova e la vecchia descrizione si toglie.

Le domande con immagini nel testo non si aggiornano incollando: l'immagine va caricata nell'editor dopo aver incollato. Se il quiz non ha tentativi, è più semplice ripristinare il backup `.mbz` completo.

**Riallineare la dashboard**: se l'utente ha corretto domande direttamente in Moodle (non è un passaggio obbligatorio, ma può capitare), prima di rigenerare o di scrivere altre varianti chiedi il backup del quiz (con «Includi file») e confrontalo con la dashboard con `scripts/importa_mbz.py --confronta`: la procedura è in `dashboard.md` di `progettazione-quiz` («Modifiche fatte in Moodle»). Lo stesso script importa nella dashboard un quiz vecchio (`--id=ID`, tipo `IMP`). Le domande che il quiz prende da un deposito tengono lo stamp d'origine (`stampOrigine`) e il rapporto dice da quale banca vengono: se il deposito è registrato, metti `deposito` nel quiz, così rigenerandolo (o facendone la copia PDP) nel corso del deposito le domande si riusano senza doppioni.
