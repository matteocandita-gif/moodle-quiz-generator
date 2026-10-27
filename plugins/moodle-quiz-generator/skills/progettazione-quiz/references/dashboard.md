# La dashboard «Bozze dei quiz»

Una sola pagina pubblicata per utente, riusata per ogni quiz: la sua pagina «Bozze dei quiz» (come trovarla: `progettazione-quiz`, «La dashboard dell'utente»).

Due viste: **Scaletta** (tabella delle righe, avvisi del preset, punti e minuti per parte, approvazione) e **Dettaglio** (per ogni riga il foglio dello studente e il riquadro del docente con risposte, correzione e note interne). L'utente sceglie il quiz da un menù, modifica celle e tracce, cambia lo stato delle righe e la fase del quiz, lascia commenti. Nelle domande CodeRunner mostra il codice da completare o di partenza e, al docente, soluzione e test. È solo anteprima: non esegue le domande.

Nessuna notifica arriva in chat dalla pagina: l'utente lavora nella pagina e poi lo dice in chat. Leggi il database solo quando serve (prima di scrivere, prima della parte 2, quando lui dice di aver fatto modifiche), e leggi i commenti con `ArtifactComments` quando li nomina.

**Commenti.** Un commento lasciato nella pagina non arriva in chat: lo leggi solo quando l'utente te lo dice, e non puoi rispondere né chiuderlo finché il thread non è attivato per Claude. Quando un commento chiede una modifica, l'utente lo invia con «Invia a Claude» (o menziona @claude): così arriva in chat e puoi rispondere nel thread e chiuderlo. Se trovi un thread non attivato, fai la modifica, dillo in chat e ricorda che il thread resta aperto finché non lo chiude lui o non lo invia a Claude. Prima di modificare la riga indicata rileggila: l'utente può averla già cambiata.

## Il database

Si legge e si scrive con `ArtifactData` sull'URL della pagina. Ogni scrittura su un documento esistente porta `if_version` con la versione letta: se l'utente ha modificato la riga nel frattempo la scrittura fallisce, rileggi e rifai. Per più righe usa una `batch` (fino a 50 scritture, atomica), con `file_path` per i campi lunghi.

**Depositi**: documento `impostazioni/depositi`, `{depositi: [{id, nome, corso, contextid, cmid, top_id, top_stamp, categorie: [{nome, id, stamp}]}]}`: le banche dei corsi deposito in cui le domande possono andare direttamente. Lo scrive Claude da un backup (`materiali-moodle`, «Depositi»); la pagina li elenca nelle impostazioni e li propone nei dati del quiz.

**Banca PDP**: documento `impostazioni/pdp`, `{banca: {nome, corso, contextid, cmid, top_id, top_stamp, categoria_id, categoria_nome, categoria_stamp}, domande: {nome: XML della voce}}`: le descrizioni «Riduzione contenuti PDP/PEI -k» e le dichiarazioni della banca condivisa, per le copie PDP (`crea_pdp.py --prepara-banca`).

**Impostazioni**: documento `impostazioni/avvio` con `trigger` (id dell'attività «Avvia quiz dalla dashboard», `trig_…`; vuoto o assente: «Inizia» dà la frase da incollare) e `versione` (la `VERSIONE_PAGINA` con cui è stato scritto). Lo scrive l'installazione; l'utente può cambiare l'id dal riquadro «Impostazioni» della vista iniziale.

**Quiz**: collezione `quiz`, un documento per quiz, id breve in minuscolo con trattini (es. `js-cicli-while`).

| Campo | Contenuto |
|---|---|
| `titolo` | nome breve del quiz (compare nel menù) |
| `tipoQuiz` | sigla del preset: `LIB` (libero, senza preset: regole solo dalla richiesta, impostazioni dell'.mbz in `presetMbz`), `ED`, `EDT`, `SD`, `V`, `VT`, `RT`, `EP`, `ER`; `IMP` per un quiz importato da un backup (nessun preset: la pagina non applica le regole su punti, tempi, parti e tipologie, e non lo propone nel modulo «Nuovo quiz») |
| `lezione` | numero di lezione (solo cifre: nomi `L<lezione> - …`, categoria «Lezione N - argomento»); altrimenti un codice usato così com'è (`V5R - …`, categoria «V5R - argomento»): il codice di una verifica, o quello automatico che la pagina assegna quando il campo resta vuoto nel modulo, tre caratteri che cominciano con la classe (`4K7`) |
| `argomento` | argomento: la categoria Moodle è «Lezione N - argomento» (con un codice: «V5R - argomento») |
| `tempo` | minuti disponibili |
| `fase` | `richiesta` (quiz creato dal modulo «Nuovo quiz», scaletta non ancora scritta), `scaletta-revisione`, `scaletta-approvata`, `dettaglio-revisione`, `dettaglio-approvato` |
| campi del modulo | `classe` (`terza`, `quarta`, `quinta`), `linguaggio` (`teoria`, `html-css`, `javascript`, `sql`, `php`, `misto` o vuoto), `varianti` (1-3, solo V e VT), `avanzata` (argomenti della parte avanzata, solo V), `richiesta` (la richiesta dell'utente a parole), `materiale` (true: l'utente allega dei file in chat), `creato` e `avviato` (date ISO). **`creato` è obbligatorio** anche quando crei tu un quiz in chat (data e ora di adesso): la pagina ordina i quiz per `creato` e un quiz senza data finisce in fondo all'elenco |
| `note` | note generali sul quiz (si vedono nella scaletta) |
| `database` | solo con domande SQL o PHP: elenco di `{nome, sql}`, lo script di CREATE TABLE e INSERT di ogni database (riquadro «Database del quiz» nella scaletta; vedi `formato-consegna.md`) |
| `esportazione` | lo scrive il pulsante «Esporta» e la sessione che genera il backup: `{stato, richiesta, inizio, fine, esito, file}`. `stato` è `richiesta`, `in-corso`, `fatta` o `errore`; `esito` è una riga che la pagina mostra (domande, punti, errori e avvisi, o il motivo dell'errore) |
| `archiviato` | `true` se il quiz è archiviato: esce dall'elenco dei quiz attivi e compare in fondo al menù, tra gli archiviati |
| `prototipoHtml` | solo con esercizi HTML (`libero_html`): `php_con_test` (con anteprima, lo scratchpad; è anche il valore se il campo manca) o `html` (senza anteprima: il campo serve solo a incollare il codice provato nel browser). Nella pagina è «Esercizi HTML», nel modulo «Nuovo quiz» (linguaggio HTML e CSS) e nei dati del quiz; l'importazione da un backup lo mette a `html` se gli esercizi HTML usano quel prototipo |
| `deposito` | facoltativo: l'`id` di un deposito di `impostazioni/depositi`; le domande vanno nella banca di quel deposito invece che in quella del quiz (pagina: «Dove vanno le domande»). La categoria deve esistere già nel deposito e il backup va ripristinato nel corso del deposito: la pagina lo ricorda negli avvisi |
| facoltativi | `titoliSezioni` (oggetto sezione → titolo nel quiz), `nomeQuiz`, `voto` (10), `sufficienza` (6), `presetMbz` (`verifica` o `esercitazione`: le impostazioni dell'.mbz di un quiz `IMP`, prese dal backup) |

**Elenco e apertura automatica.** I quiz sono elencati dal più recente al più vecchio secondo `creato` (quelli senza data in fondo, per titolo). Quando nel database compare un quiz pronto (fase diversa da `richiesta`: scaletta scritta, quiz creato in chat o importato) che quel browser non ha ancora visto, la pagina lo apre da sola nella scaletta; se l'utente sta modificando qualcosa non cambia vista e lo avvisa con un messaggio. Non serve dire all'utente di cercare il quiz nel menù.

**Nuovo quiz dalla pagina.** La vista iniziale («Tutti i quiz») mostra i quiz attivi e il pulsante «Nuovo quiz». Il modulo chiede tipo (il primo è «Libero»), titolo, classe, argomento, tempo (obbligatori), lezione o codice (facoltativo: vuoto, la pagina assegna un codice automatico), linguaggio, comportamento in Moodle (solo per il tipo libero, in `presetMbz`), varianti e parte avanzata (per le verifiche); una guida apribile descrive i tipi, la richiesta a parole e se ci sono file da allegare; il database non si chiede (si decide dopo, se serve). «Inizia» crea `quiz/<id>` in fase `richiesta` e, attraverso il connettore Claude Code Remote, fa partire l'attività programmata «Avvia quiz dalla dashboard» dell'utente (senza orario; il suo id sta nelle impostazioni, sotto) con il messaggio «Quiz da avviare: <id>»: una nuova sessione segue `progettazione-quiz` fino alla scaletta e porta la fase a `scaletta-revisione`. Se l'attività non è configurata o il connettore non è disponibile, la pagina mostra una frase da incollare in chat: «Avvia il quiz «titolo» (id …) dalla dashboard…». In entrambi i casi leggi le scelte dal documento del quiz, non chiederle di nuovo; dove manca un dato decidi e scrivilo nelle `note`; fermati alla scaletta. Se `materiale` è true, prima di scrivere la scaletta aspetta i file. All'inizio di un lavoro sui quiz, se trovi quiz in fase `richiesta` senza righe da più di un'ora, dillo all'utente.

**Esportare dalla pagina.** Quando il quiz è in fase `dettaglio-approvato`, nel riquadro «Avanzamento» compare il pulsante «Esporta». Fa partire la stessa attività programmata di «Inizia», con il messaggio «Quiz da esportare: <id>», e scrive `esportazione` con `stato: "richiesta"`. La sessione segue la sezione «Esportare» del prompt dell'attività (`installazione.md`): genera `.mbz` e XML con `materiali-moodle`, li consegna nella sua chat e scrive l'esito in `esportazione`. Se l'attività non parte, la pagina dà una frase da incollare in chat: «Esporta il quiz «titolo» (id …) dalla dashboard…». In quel caso fai lo stesso lavoro nella chat e scrivi anche tu `esportazione`. Quando generi un quiz in chat, aggiorna `esportazione` nello stesso modo, così la pagina mostra l'ultima esportazione.

**Importare un quiz da un backup.** L'utente dà il backup `.mbz` di un quiz (allegato in chat o in una cartella collegata), fatto con «Includi file» attivo, altrimenti mancano i database delle CodeRunner e le immagini. Due casi:

- **Quiz che non è nella dashboard** (un quiz vecchio da rifare col flusso): `python3 importa_mbz.py BACKUP.mbz USCITA --id=ID` scrive quiz e righe nella forma dell'esportazione (`USCITA/quiz/ID.json`, `USCITA/quiz/ID/domande/rNN.json`) e `USCITA/rapporto.md`. Si caricano con una `batch` di `set` (il quiz e le righe; i campi lunghi con `file_path`). Il quiz ha tipo `IMP`, fase «dettaglio in revisione», i database ricostruiti dagli allegati; le righe convertite senza perdite sono «approvata», le altre «da rivedere» con la `nota` (immagini, a capo nelle opzioni, feedback delle aperte). Minuti, parte e strumento restano vuoti. Di' all'utente che cosa c'è nel rapporto. L'ordine non unico delle query importate non si segnala (lo ha deciso l'utente): il controllo c'è solo con `--ordine`.
- **Quiz che è già nella dashboard** e che l'utente ha corretto in Moodle: `python3 importa_mbz.py BACKUP.mbz USCITA --confronta=EXPORT --id=ID` (EXPORT è l'esportazione del quiz con `ArtifactData`) non scrive niente: produce `USCITA/confronto.md` con le differenze per posizione e `USCITA/aggiornamenti/<riga>.json` con i campi cambiati. Le domande con più versioni nel backup sono quelle modificate in Moodle: il confronto tra la prima versione e l'ultima mostra solo le modifiche dell'utente, non le differenze dovute alla conversione. Mostra le differenze e aggiorna le righe solo dopo il suo ok (rileggile prima, con `if_version`), mettendole «da rivedere» con una `nota` che dice che cosa viene da Moodle.

**Archiviare ed eliminare.** Nella scaletta, il riquadro «Archivia o elimina il quiz» (in fondo, chiuso) archivia o riattiva il quiz (campo `archiviato`) oppure lo elimina definitivamente, righe comprese, con un secondo clic di conferma. La dashboard non deve conservare tutti i quiz: quelli conclusi si archiviano o si eliminano. Se l'utente ti chiede di eliminare un quiz, prima salvane una copia (`ArtifactData list` del quiz e delle righe con `out_dir`, in un .zip da consegnare all'utente, o nella cartella che indica quando il computer è collegato), poi cancella righe e quiz con una `batch` di `delete`. Non archiviare né eliminare un quiz di tua iniziativa.

**Righe**: collezione `quiz/<id>/domande`, id `r01`, `r02`, … in ordine di creazione (le righe aggiunte dall'utente hanno id casuali).

| Campo | Contenuto |
|---|---|
| `ordine` | numero per l'ordinamento (passi di 10; una riga inserita prende un valore intermedio) |
| `sezione` | nome della sezione (es. «Blocco A - Struttura e testo»); le righe della stessa sezione sono consecutive |
| `pos` | posizione: `00` per l'apertura, poi lettera del blocco e numero (`A0` pagina del blocco, `A1`, `A2`…), `D1`… per i finali |
| `pag` | pagina del quiz (le domande sulla stessa pagina hanno lo stesso numero) |
| `titolo` | titolo breve, entra nel nome Moodle |
| `sintesi` | che cosa chiede, in una o due frasi (scaletta) |
| `tipologia` | id del catalogo |
| `parte` | numero della parte del preset (ED: 0 apertura, 1 pagina del blocco, 3 esempio svolto, 4 completamento, 5 debugging, 6 guidato, 7 finali; EDT: 0 apertura, 1 pagina di spiegazione, 2 domande di comprensione; SD: 1 pagina di teoria, 2 domande chiuse, 3 domande aperte; V: 1 base, 2 avanzata; VT e RT: livello di Bloom 1-5) |
| `punti`, `minuti` | numeri |
| `strumento` | `suggerito`, `non-nominato`, `na` (non applicabile) o vuoto |
| `sostegno` | solo debugging: `quanti-dove`, `solo-quanti`, `nulla` |
| `stato` | `proposta`, `da-rivedere`, `approvata` |
| `traccia` | quello che vede lo studente, con le convenzioni di `formato-consegna.md` |
| `correzione` | va in Moodle: indicazioni per chi corregge (aperte) o feedback generale |
| `coderunner` | solo domande CodeRunner («Soluzione e test»): sezioni `=== answer`, `=== test`, `=== stdin`, `=== code`, `=== preload`… come in `formato-consegna.md`; nelle SQL `=== options`, `=== preload`, `=== answer`, `=== test` con `-- commento`, `=== extra`; nelle PHP `=== options`, `=== preload`, `=== answer`, `=== test` con i dati del form e `=== descrizione`; negli esercizi HTML e CSS solo `=== answer`, `=== preload`, `=== options` |
| `tag` | solo verifiche ripetibili: tag della posizione; le righe con lo stesso tag sono varianti (vedi `formato-consegna.md`). Nella scaletta il campo compare nelle verifiche (V, VT) o se una riga ha già un tag |

**Varianti nella pagina.** Nel database resta una riga per variante; la pagina raggruppa le righe con lo stesso tag in una posizione. Nella scaletta ogni posizione è una riga sola, con la posizione senza lettera (`Q1`): pagina, posizione, titolo, tag, tipologia, parte, punti, minuti, strumento e sostegno si modificano lì e la pagina li scrive su tutte le varianti (cambiando la posizione aggiorna la lettera di ognuna). Sotto il titolo, chiusa di default, la riga «▸ 3 varianti: a palestra · b cinema · c veterinario» apre una sottoriga per variante (lettera, database letto da `database:` nelle opzioni o dalla sintesi che comincia con `[nome]`, sintesi, stato) con «Aggiungi variante» (copia i campi comuni con la lettera successiva) ed «Elimina variante»; il cestino della posizione elimina tutte le varianti. Spostare su o giù sposta la posizione intera. «Aggiungi domanda» in un quiz con varianti crea tante varianti quante ne ha la posizione che ne ha di più, con un tag provvisorio (`v5r-nuova-xxxx`) che diventa `v5r-<pos>-<titolo>` appena si scrivono posizione e titolo. Nel dettaglio l'elenco ha una voce per posizione (un pallino per variante) e sopra il foglio le schede a, b, c passano da una variante all'altra; le frecce restano sulla stessa lettera. Quando scrivi tu nel database, mantieni uguali i campi comuni delle varianti e la lettera finale nella `pos`.
| `docente` | note interne, non escono dalla dashboard |
| `nota` | perché la riga è «da rivedere»; si svuota quando viene approvata |
| `pdp` | facoltativo, solo nelle verifiche: `true` se la posizione è tolta nella copia PDP (pagina: «tolta nella PDP», sotto i punti); nelle varianti vale per tutta la posizione. La pagina mostra la riduzione in minuti e avvisa oltre il 30% |
| `stampOrigine` | facoltativo: lo stamp della domanda in un deposito, messo dall'importazione di un backup; generando nel deposito la domanda viene riusata invece di duplicarla. Copiando la riga in un altro quiz, copialo con lei |

## Fasi e stati

- **Fasi del quiz**: scaletta in revisione → scaletta approvata → dettaglio in revisione → dettaglio approvato. Il pulsante di approvazione del dettaglio resta bloccato finché manca una traccia o una riga è «da rivedere»; approvando il dettaglio (pulsante o menù della fase) tutte le righe diventano «approvata». Aggiungere, eliminare o spostare una riga riporta il quiz a «scaletta in revisione».
- **Stati delle righe**: «proposta» = testo tuo non ancora guardato; «da rivedere» = modificato da te o da confermare, con la `nota` che spiega perché; «approvata» = OK dell'utente. L'utente approva nella pagina (riquadro arancione «Approva questa domanda») oppure in chat: in quel caso aggiorni tu lo stato.

## Creare un quiz nuovo

1. `set` del documento `quiz/<id>` con i campi del quiz e `fase: "scaletta-revisione"`.
2. `batch` di `set` delle righe della scaletta, con `traccia`, `correzione`, `coderunner` e `docente` vuoti e `stato: "proposta"`.
3. Di' all'utente di sceglierlo dal menù della pagina. Non serve ripubblicare la pagina.

## Ripubblicare la pagina

Serve solo se cambia la pagina (non i dati). Il sorgente è `assets/dashboard.html` di questa skill: le modifiche si fanno lì, si alza `VERSIONE_PAGINA` e si ripubblica sullo stesso URL come dice `installazione.md` («Aggiornare»); le capacità restano. Prima di pubblicare provala in locale con Playwright, con un finto `window.claude` che restituisce dati congelati (`Object.freeze`): i documenti veri del database arrivano congelati e vanno copiati prima di aggiungere campi.
