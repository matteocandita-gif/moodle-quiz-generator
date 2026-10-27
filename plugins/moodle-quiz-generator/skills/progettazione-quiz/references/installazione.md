# Installare e aggiornare la dashboard «Bozze dei quiz»

Ogni utente ha la sua dashboard: una pagina pubblicata come artifact privato, con il database dei suoi quiz. La pagina sta in `assets/dashboard.html` di questa skill; i dati stanno nel database della pagina e restano quando la pagina si ripubblica.

## Installare

Si fa quando l'utente lo chiede («installa la dashboard dei quiz», comando `installa-dashboard`) o quando serve la dashboard e non c'è.

1. **Controlla che non ci sia già.** `Artifact` con `action: "list"`: cerca un artifact il cui titolo contiene «Bozze dei quiz». Se c'è, non crearne un'altra: passa ad «Aggiornare».
2. **Pubblica la pagina.** Copia `assets/dashboard.html` nella cartella di lavoro e pubblicala con `Artifact`, con `icon: "checklist"`, una `description` di una riga e queste capacità:
   ```json
   {"db": {}, "comments": {"composer_only": true},
    "mcp": {"servers": [{"server": "Claude Code Remote", "tools": ["fire_trigger"]}]}}
   ```
   L'URL del risultato è la dashboard dell'utente.
3. **Crea l'attività programmata** che il pulsante «Inizia» avvia. Con lo strumento delle attività programmate (`create_trigger` del connettore Claude Code Remote; cercalo con `ToolSearch` se è differito): nome «Avvia quiz dalla dashboard», nessun orario (né `cron_expression` né `run_once_at`), `initiation: "human_request"`, e come prompt il testo della sezione «Prompt dell'attività» qui sotto con l'URL della dashboard al posto di `{URL}`. Annota l'id (`trig_…`) del risultato. Se lo strumento non c'è, salta questo passo: «Inizia» darà all'utente una frase da incollare in chat, e l'attività si può aggiungere dopo.
4. **Salva le impostazioni** nel database della pagina: `ArtifactData` `set` su `impostazioni` / `avvio` con `{"trigger": "<id>", "versione": "<VERSIONE_PAGINA della pagina>"}` (senza attività: solo `versione`).
5. **Verifica**: `ArtifactData` `get` di `impostazioni` / `avvio` e `list` di `quiz` (vuota su una dashboard nuova).
6. **Di' all'utente**, in poche righe: la pagina è pronta; la prima volta che preme «Inizia» la pagina gli chiede di autorizzare il connettore Claude Code Remote (va accettato); il connettore deve essere attivo nel suo account; le sessioni avviate dall'attività compaiono tra le sue sessioni di Claude; l'id dell'attività si può cambiare dalla pagina, nel riquadro «Impostazioni». Di' anche con che impostazione di approvazione è stata creata l'attività (lo dice il risultato): se le sue esecuzioni chiedono approvazione, nelle impostazioni dell'attività si può attivare l'approvazione automatica.

## Configurare l'avvio su una dashboard esistente

Quando l'utente ha già la dashboard ma «Inizia» non avvia la sessione (riquadro «Impostazioni»: avvio automatico non configurato), o chiede di configurarlo.

1. Leggi `impostazioni` / `avvio` della sua dashboard. Se c'è un `trigger`, controlla con lo strumento che elenca le attività programmate (`list_triggers`) che esista ancora e sia attiva: se sì, il problema è il connettore (va autorizzato dalla pagina, al primo «Inizia», e deve essere attivo nell'account), e lo dici.
2. Altrimenti crea l'attività come al passo 3 di «Installare» e scrivi il suo id in `impostazioni` / `avvio` (`update` con `if_version`, o `set` se il documento non c'è).

## Aggiornare

Quando una nuova versione del plugin porta una pagina nuova (la costante `VERSIONE_PAGINA` in `assets/dashboard.html` è diversa da quella della pagina pubblicata), o quando l'utente lo chiede.

1. Leggi la pagina pubblicata (`Artifact`, `action: "read"`) e confronta `VERSIONE_PAGINA`. Se è uguale, non serve niente.
2. Ripubblica `assets/dashboard.html` sullo **stesso URL**, senza `capabilities` (restano quelle salvate). Se la pagina nuova richiede capacità diverse (lo dice il changelog del plugin), passale tutte. I quiz e le impostazioni restano: stanno nel database, non nella pagina.
3. Aggiorna `versione` in `impostazioni` / `avvio` (`update` con `if_version`).
3b. Se il changelog dice che è cambiato il prompt dell'attività programmata, aggiorna anche l'attività: prendi il suo id da `impostazioni` / `avvio` e sostituisci il prompt con il testo di «Prompt dell'attività», con l'URL della dashboard (`update_trigger` del connettore Claude Code Remote; cercalo con `ToolSearch` se è differito). Se lo strumento non c'è, dillo all'utente.
4. Di' all'utente che cosa cambia nella pagina, in una riga.

Non modificare la pagina pubblicata a mano: le modifiche si fanno in `assets/dashboard.html` del plugin e arrivano a tutti con l'aggiornamento.

## Prompt dell'attività

```
Lavoro su un quiz Moodle partito dalla dashboard «Bozze dei quiz» dell'utente ({URL}). Di solito un messaggio successivo a questo dice che cosa fare:
- «Quiz da esportare: <id>»: il pulsante «Esporta» chiede il backup di un quiz con il dettaglio approvato. Segui solo la sezione «Esportare» in fondo, non i passi numerati.
- «Quiz da avviare: <id>», oppure nessun messaggio: il pulsante «Inizia» ha appena creato un quiz in fase `richiesta`. Segui i passi numerati.

1. Carica la skill `progettazione-quiz` e segui il suo processo (parte 1): leggi i file di riferimento che la skill indica (preset.md, catalogo.md, dashboard.md, formato-consegna.md) e, per una verifica di programmazione, anche la skill `verifiche-programmazione`. La dashboard è quella dell'indirizzo qui sopra.
2. Trova il quiz da avviare. Se hai l'id, leggi `quiz/<id>`. Se l'id manca, leggi la collezione `quiz` e prendi i quiz in fase `richiesta` che non hanno il campo `inLavorazione` (o lo hanno più vecchio di un'ora) e non hanno righe in `quiz/<id>/domande`: avviali tutti, uno dopo l'altro, dal più vecchio (campo `creato`). Un quiz che non è in fase `richiesta`, o che non esiste, non si tocca.
3. Prima di lavorare su un quiz, segna che lo stai facendo: `update` del documento con `inLavorazione` uguale alla data e ora attuali (ISO), con `if_version` della versione appena letta. Se la scrittura fallisce perché il documento è cambiato, rileggilo: se ora ha `inLavorazione` recente, lo sta già facendo un'altra sessione e lo lasci.
4. Il documento contiene le scelte del modulo «Nuovo quiz»: `tipoQuiz`, `titolo`, `lezione` (numero o codice della verifica), `classe`, `argomento`, `tempo`, `linguaggio`, `varianti`, `avanzata` (argomenti della parte avanzata), `richiesta` (la richiesta dell'utente a parole) e `materiale` (true se l'utente deve allegare dei file). Usale così come sono, senza chiederle di nuovo.
5. Se `materiale` è true, non scrivere la scaletta: scrivi nelle `note` del quiz che aspetti i file in questa sessione, lascia la fase `richiesta` e fermati con un messaggio che lo dice.
6. Altrimenti scrivi la scaletta come dice la skill: le righe in `quiz/<id>/domande` (con le varianti per tag se `varianti` è maggiore di 1), le scelte e i dubbi nelle `note` del quiz, poi porta la fase a `scaletta-revisione` e togli `inLavorazione`. Non scrivere le tracce: ci si ferma alla scaletta, che l'utente rivede nella dashboard.
7. L'utente non è presente mentre lavori: non fare domande. Dove manca un dato prendi la scelta più ragionevole e scrivila nelle `note`. Se il quiz avrà bisogno di un database (SQL o PHP), non sceglierlo né crearlo: scrivi nelle `note` che la scelta del database va fatta dopo, insieme all'utente.
8. Alla fine scrivi un messaggio breve: il quiz creato, quante righe, le scelte principali e i dubbi da guardare nella dashboard.

Esportare («Quiz da esportare: <id>»)
- Carica la skill `materiali-moodle` e segui «Dalla dashboard: XML e .mbz». Leggi `quiz/<id>`: se la fase non è `dettaglio-approvato`, non generare niente e scrivi nel quiz `esportazione` con `stato: "errore"` e l'esito «Il dettaglio non è approvato».
- Prima di cominciare: `update` del quiz con `esportazione` uguale a `{stato: "in-corso", richiesta: <quella che c'è>, inizio: <data e ora ISO>, fine: null, esito: null, file: null}` (con `if_version`).
- Genera il backup `.mbz` e il Moodle XML con `genera_quiz.py`, con il nome del quiz (`nomeQuiz`, o la lezione e il titolo come nei quiz già generati: `<lezione> - <titolo>`). Se il quiz ha `deposito` e righe con il campo `pdp`, genera anche la copia PDP. Se le tracce citano immagini, cercale come dicono le note del quiz: se non le trovi in questa sessione, non generare un backup senza immagini.
- Non cambiare le righe né le tracce. Se lo script trova errori, il backup non si consegna: si scrive l'errore.
- Consegna i file in questa sessione con `SendUserFile` (prima il `.mbz`, poi l'XML).
- Alla fine scrivi nel quiz `esportazione` con `stato: "fatta"` (oppure `"errore"`), `fine` (data e ora ISO), `file` (il nome del `.mbz`) ed `esito`: una riga con domande, punti, errori e avvisi del controllo, oppure il motivo dell'errore. La dashboard mostra questa riga.
- L'utente non è presente: non fare domande. Chiudi con un messaggio breve: i file, l'esito del controllo, gli avvisi da guardare.
```
