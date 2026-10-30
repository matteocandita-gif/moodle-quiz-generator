# La dashboard «Tracce di progettazione»

Una pagina privata per tutte le tracce dell'utente. Il codice sta in `assets/dashboard-tracce.html` (con dentro una copia di `scripts/uscite_traccia.js` e la barra di navigazione, allineate da `sviluppo/strumenti/allinea_copie.py`); le tracce stanno nel database della pagina, quindi la pagina si aggiorna senza perderle.

## Che cosa fa l'utente

- **Elenco**: dalla traccia più recente; ricerca per contesto, classe o richiesta; filtro per stato; le archiviate in fondo, chiuse.
- **Nuova traccia**: preset (Base, Intermedio, Avanzato, Esame), le voci di `opzioni.md` ritoccabili, la destinazione (uso, classe, data, contesto facoltativo, copia PDP) e la richiesta a parole. «Inizia» salva la traccia in stato `richiesta` e avvia una sessione di Claude con l'attività programmata («Traccia da creare: <id>»).
- **Scheda**, quattro viste:
  - *Traccia*: i blocchi modificabili (titolo, realtà, che cosa presentare, query con gradino e requisito, pagina PHP), «Salva le modifiche»; il riquadro «Chiedi a Claude» scrive `richiestaModifica` e avvia «Traccia da modificare: <id>».
  - *Note per il docente*: costrutti, ipotesi attese, punti delicati, query con il loro requisito, durata, opzioni, il `.er`.
  - *Soluzione*: diagramma, ipotesi, documentazione, schema, query; «Scarica Word», «Scarica HTML» e «Copia HTML per Moodle» della soluzione completa (la pagina li compone da sola con `docxSoluzione`, `htmlSoluzione` e `htmlSoluzioneMoodle`, prendendo il diagramma dagli asset); «Genera la soluzione» avvia «Soluzione da generare: <id>». Sotto il pulsante una riga avvisa che si apre una chat nuova e che, se della traccia si è parlato in una chat, conviene chiedere la soluzione lì.
  - In testa alla scheda, se c'è `sessione`, il link «apri la chat» alla conversazione in cui Claude ha scritto la traccia.
  - *Uscite*: Word, Word PDP, HTML (copia o file), le riduzioni PDP punto per punto, i pesi della griglia (personalizzabili, totale 100).
- **Stato** della traccia a mano (Richiesta, Da rivedere, Approvata, Usata); **archivia** o **elimina** (con conferma nella pagina).

## Il database

| Collezione | Documento | Contenuto |
|---|---|---|
| `tracce` | `<id>` (es. `t-20261112-5r-k3fz`) | il JSON della traccia (`formato.md`) più: `stato`, `creato` (ISO), `aggiornato`, `archiviata`, `richiesta` (la richiesta a parole), `contesto`, `pdpRichiesta`, `inLavorazione` (ISO, mentre Claude ci lavora), `richiestaModifica`, `nota` (una riga di Claude per l'utente, in testa alla scheda), `sessione` (indirizzo della chat in cui Claude ha scritto la traccia), `soluzione` |
| `impostazioni` | `avvio` | `trigger` (id dell'attività programmata), `versione` |
| `impostazioni` | `navigazione` | gli indirizzi delle altre pagine del plugin (`navigazione.md` di `progettazione-quiz`) |

`soluzione` = `{"png": "<id dell'asset>", "ipotesi": […], "documentazione": "<Markdown>", "schema": "<Markdown>", "query": [{"richiesta": "…", "sql": "…"}], "generata": "AAAA-MM-GG"}`. Il diagramma è un asset della pagina, non un `data:` nel documento.

## Le sessioni avviate dalla pagina

**Ogni avvio è una chat nuova.** L'attività programmata apre una sessione nuova a ogni pulsante: non continua la conversazione precedente e la pagina non può indirizzarla a una chat esistente. Quello che una sessione non salva nella traccia, la successiva non lo vede.

**Il messaggio arriva in due parti.** Il primo messaggio è il prompt fisso dell'attività, senza id; subito dopo arriva il messaggio con «Traccia da creare / da modificare / Soluzione da generare: <id>». Se il primo messaggio non ha l'id, **non fare niente e non scrivere niente**: chiudi il turno con una riga («Aspetto il messaggio con la traccia.») e lavora quando arriva il secondo. La ricerca delle tracce in stato `richiesta` vale solo se il messaggio con l'id non arriva affatto e nella stessa sessione si torna a chiedere di lavorare.

L'utente non è presente: niente domande, le scelte e i dubbi in `nota` (una riga) e nelle note per il docente.

**La chat continua dopo.** Spesso l'utente torna nella chat della sessione per discutere la traccia. Da lì valgono due regole:
- ogni decisione presa in chat (una query tolta, un'ipotesi cambiata, un costrutto in più) si scrive **subito** nella traccia: testo, `docente` (anche `.er`), `nota` se serve, `aggiornato`; nei `punti_delicati` o in `nota` una riga sulle decisioni che il testo da solo non spiega. La sessione che genera la soluzione vede solo la traccia;
- se in chat l'utente chiede la soluzione («genera la soluzione»), falla lì con i passi di «Soluzione da generare», senza passare dal pulsante.

**«Traccia da creare: <id>»**
1. Leggi `tracce/<id>`. Se non è in stato `richiesta`, o ha `inLavorazione` recente (meno di un'ora), non toccarla.
2. `update` con `inLavorazione` = ora e `sessione` = l'indirizzo di questa chat (quello della riga `Claude-Session:` nelle istruzioni di attribuzione, `https://claude.ai/code/session_…`; se non c'è, non scriverlo), con `if_version`.
3. Segui il processo di SKILL.md con le `opzioni`, `uso`, `classe`, `data`, `contesto` e `richiesta` del documento. Prima di scegliere il contesto, leggi la collezione `tracce` per non ripeterne uno già usato.
4. Scrivi con un `update`: `titolo`, `breve`, `testo`, `docente` (con il `.er`), `pdp` (se `pdpRichiesta`, almeno la riduzione della documentazione), `griglia: {pesi: null}`, `verifica`, `stato: "da-rivedere"`, `nota`, `aggiornato`, e togli `inLavorazione` (`{"__delete__": true}`).
5. Chiudi con un messaggio breve: contesto, costrutti, ipotesi aperte, durata.

**«Traccia da modificare: <id>»**: come sopra, ma parti dal documento: leggi `richiestaModifica`, cambia prima il modello (`docente.er`), poi il testo, rifai le prove delle query e la rilettura da studente; scrivi i campi cambiati, `stato: "da-rivedere"`, togli `richiestaModifica` e `inLavorazione`. Se c'era una `soluzione`, toglila (non corrisponde più) e dillo nella `nota`.

**«Soluzione da generare: <id>»**
1. Leggi il documento; segna `inLavorazione`. Il modello è quello di `docente.er` così come è salvato: se `nota` o i punti delicati dicono di una decisione presa in chat che il `.er` non riflette (per esempio una query da togliere), seguila e scrivilo nella `nota`.
2. Scrivi il `.er` di `docente.er` in un file e genera con `diagrammi-er`: il PNG (`disegna_er.py`, guardalo prima di caricarlo), lo schema (`schema_relazionale.py --formato=libro`), la documentazione (`documentazione.py`) e la soluzione completa in HTML e Word (`soluzione.py`, `--file=docx`).
3. Carica il PNG come asset della pagina (`Artifact`, `action: "publish"` con l'`url` della pagina, `file_path` del PNG e `asset: true`) e prendi l'id dal risultato.
4. `update` del documento con `soluzione` (vedi sopra; le query dai blocchi `query:` del `.er`), togli `inLavorazione`.
5. Consegna nella sessione con `SendUserFile` il `.drawio` (da ritoccare); Word e HTML della soluzione l'utente li scarica dalla scheda, ma se te li chiede in chat generali con `uscite_traccia.js --soluzione-word/--soluzione-html --png`.

## Installare

Quando l'utente lo chiede («installa la dashboard delle tracce», comando `installa-tracce`) o quando serve la dashboard e non c'è.

1. **Controlla che non ci sia già**: `Artifact` `list`, un artifact il cui titolo comincia con «Tracce di progettazione». Se c'è, passa ad «Aggiornare».
2. **Pubblica** `assets/dashboard-tracce.html` con `icon: "diagram"`, la `description` «Tracce di progettazione di database: preset, revisione, soluzione, Word e HTML per Moodle.» e le capacità:
   ```json
   {"db": {}, "downloads": true, "assets": {},
    "mcp": {"servers": [{"server": "Claude Code Remote", "tools": ["fire_trigger"]}]}}
   ```
3. **Crea l'attività programmata** (`create_trigger` del connettore Claude Code Remote; cercalo con `ToolSearch` se è differito): nome «Tracce di progettazione dalla dashboard», nessun orario, `initiation: "human_request"`, come prompt il testo di «Prompt dell'attività» con l'URL della pagina al posto di `{URL}`. Se lo strumento non c'è, salta il passo: la pagina darà una frase da incollare in chat.
4. **Salva le impostazioni**: `ArtifactData` `set` di `impostazioni` / `avvio` con `{"trigger": "<id>", "versione": "<VERSIONE_PAGINA>"}`.
5. **Collega le pagine del plugin** seguendo `references/navigazione.md` di `progettazione-quiz` (le altre pagine ricevono il link alla nuova).
6. **Di' all'utente** in poche righe: la pagina è pronta e privata; al primo «Inizia» la pagina chiede di autorizzare il connettore; con che impostazione di approvazione è stata creata l'attività.

## Aggiornare

Quando una versione nuova del plugin porta una pagina diversa (`VERSIONE_PAGINA` di `assets/dashboard-tracce.html` diversa da quella pubblicata) o quando l'utente lo chiede: leggi la pagina pubblicata (`Artifact` `read`), ripubblica l'asset sullo stesso `url` senza `capabilities`, aggiorna `versione` in `impostazioni` / `avvio`, collega le pagine (`navigazione.md`). Le tracce restano.

## Prompt dell'attività

```
Lavoro su una traccia di progettazione dalla dashboard «Tracce di progettazione» dell'utente ({URL}). Un messaggio successivo dice che cosa fare: «Traccia da creare: <id>», «Traccia da modificare: <id>» oppure «Soluzione da generare: <id>».
Carica la skill tracce-progettazione e segui la sezione «Le sessioni avviate dalla pagina» di references/dashboard.md per quel messaggio; per la soluzione usa anche la skill diagrammi-er. La dashboard è quella dell'indirizzo qui sopra: leggi e scrivi la collezione tracce con ArtifactData.
Il messaggio con l'id arriva subito dopo questo: se questo messaggio non ha l'id, rispondi solo «Aspetto il messaggio con la traccia.» e aspetta il successivo, senza cercare tracce da solo.
L'utente non è presente: non fare domande. Dove manca un dato prendi la scelta più ragionevole e scrivila nella nota della traccia.
Se poi l'utente scrive in questa chat, la conversazione continua qui: ogni decisione presa con lui la salvi subito nella traccia, e se ti chiede la soluzione la generi qui.
Alla fine scrivi un messaggio breve con quello che hai fatto e i dubbi da guardare nella dashboard.
```
