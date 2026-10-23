# Guida breve

Come si usa «Moodle: quiz generator» giorno per giorno. Per l'installazione vedi il [README](README.md).

Si lavora in due posti: la **dashboard** «Bozze dei quiz» (una pagina tua, privata, dove vedi e correggi i quiz) e la **chat** con Claude (dove chiedi le cose). La pagina non avvisa Claude: quando hai finito di lavorarci, scrivilo in chat.

## Creare un quiz

1. Nella dashboard premi **Nuovo quiz** e compila il modulo. Il primo tipo, **Libero (senza preset)**, non ha regole prefissate: decide tutto la richiesta, e scegli tu se in Moodle si comporta come esercitazione o come verifica. Gli altri tipi li descrive il riquadro «Come scegliere il tipo di quiz», sotto i campi. Lezione o codice sono facoltativi: se li lasci vuoti, il quiz riceve un codice di tre caratteri che comincia con la classe (per esempio 4K7), che dà il nome alle domande e alla categoria in Moodle. La richiesta scrivila come la scriveresti in chat: che cosa vuoi, da che cosa partire, che cosa evitare. Se hai materiale da dare (pagine del manuale, esercitazioni già svolte), spunta la casella dei file.
2. Premi **Inizia**. Claude scrive la scaletta in una sessione a parte, che trovi tra le tue sessioni; le righe compaiono nella dashboard da sole. Se hai spuntato i file, apri quella sessione e allegali lì.
   Se «Inizia» ti dà una frase da copiare, incollala in una chat: succede quando l'avvio automatico non è configurato o il connettore non è autorizzato.
3. Puoi anche partire dalla chat: «prepariamo un'esercitazione sulle JOIN per le quarte, due ore».

## Rivedere e approvare

- **Scaletta.** Controlla righe, tipologie, punti, pagine e sezioni. Puoi cambiare le celle, aggiungere, spostare o togliere righe: le righe che aggiungi le completa Claude. Quando va bene, approvala dalla pagina e scrivi in chat di passare al dettaglio.
- **Dettaglio.** Per ogni domanda vedi il foglio dello studente e, a fianco, risposte, correzione e note interne. Correggi direttamente, oppure commenta. Approvi una domanda alla volta (riquadro «Approva questa domanda») o tutto il dettaglio insieme.
- **Commenti.** Un commento normale resta per te: Claude lo legge quando gli dici di guardarlo. Se vuoi che Claude intervenga, usa **Invia a Claude** o scrivi @claude nel commento.
- Le righe «da rivedere» hanno una nota che spiega che cosa Claude ha deciso o di che cosa è in dubbio: guardale per prime (il pulsante che mostra solo quelle aiuta).

## Generare e caricare in Moodle

1. A dettaglio approvato, in chat: «genera il quiz». Ricevi il file `.mbz` (e l'XML delle domande, se lo chiedi).
2. Nel corso Moodle: **Ripristina** → carica il file → ripristina **in questo corso**, unendo. Il quiz arriva con sezioni, pagine, punti, impostazioni e domande nella categoria della lezione.
3. Prova il quiz da studente prima di aprirlo alla classe.

**Verifiche.** Arrivano con il feedback differito: durante la prova lo studente vede solo il tentativo. Alla restituzione apri feedback, punteggi e risposte giuste dalle opzioni di revisione del quiz. Le domande CodeRunner mostrano comunque l'esito dei test durante la prova, come devono.

**Verifiche con varianti.** Se nel modulo scegli più varianti, ogni posizione ha più domande con lo stesso tag e il quiz ne pesca una a caso. All'inizio si scrive e si genera solo la variante a; le altre si scrivono quando le chiedi (per esempio per il recupero) e finiscono nelle stesse domande casuali.

**Studenti con PDP.** La copia ridotta o con tempo aggiuntivo si fa su richiesta, dopo aver provato il quiz: chiedila in chat.

## Ho corretto il quiz in Moodle

Capita di sistemare una domanda direttamente in Moodle. Prima di rigenerare il quiz o di scrivere altre varianti, riporta le modifiche nella dashboard, altrimenti la prossima generazione le perde:

1. In Moodle fai il backup del quiz con **Includi file** attivo (serve per i database e le immagini).
2. In chat allega il backup e scrivi «ho corretto il quiz X in Moodle, riporta le modifiche».
3. Claude confronta il backup con la dashboard e ti mostra, domanda per domanda, che cosa è cambiato. Aggiorna le righe solo dopo il tuo ok, e le mette «da rivedere» con una nota.

## Portare nella dashboard un quiz vecchio

Un quiz fatto prima del plugin si importa dal suo backup (sempre con **Includi file**): «importa questo quiz nella dashboard». Claude lo converte in un quiz di tipo «Importato da Moodle», con le righe già scritte, e ti dice quali vanno ricontrollate (di solito quelle con immagini o tipi di domanda particolari).

## Quiz con SQL o PHP

Gli esercizi SQL e PHP lavorano su un database. Si sceglie dal catalogo dei database didattici (quattro pronti, in tre taglie) o se ne crea uno nuovo: dai i requisiti (quante tabelle, il contesto, gli argomenti da esercitare) e Claude propone lo schema prima di generarlo. Il catalogo è una tua pagina, «Database didattici», che Claude crea la prima volta che serve; lo stesso database ha anche lo script per phpMyAdmin, per usarlo a lezione.

## Fuori dalla dashboard

Per una domanda sola o poche domande per la banca non serve la dashboard: «una Cloze sull'ordine delle clausole di una SELECT», «controlla queste domande», «una pagina di ripasso sul box model». Claude consegna il Moodle XML da importare nella banca delle domande.

## Tenere ordinata la dashboard

I quiz conclusi archiviali (riquadro «Archivia o elimina il quiz», in fondo alla scaletta): restano consultabili tra gli archiviati. Eliminare un quiz lo cancella con tutte le righe; se lo chiedi a Claude, prima ne salva una copia.

## Mappe dei prerequisiti

Una mappa dei prerequisiti mostra le competenze di un argomento e quali servono prima di quali. In Moodle diventa un'attività in cui ogni studente spunta ciò che sa fare; tu vedi il riepilogo della classe.

1. La prima volta: «installa l'editor delle mappe» (comando `installa-mappe`). Claude pubblica la tua pagina «Mappe dei prerequisiti», privata.
2. In chat: «una mappa dei prerequisiti sulla progettazione E/R per le quinte», allegando il materiale (un capitolo del libro, il programma). Claude propone le voci e i collegamenti e carica la mappa nell'editor, dove la correggi e la provi con «Prova come studente». Tienila intorno alle 25 voci: per un argomento più grande, due mappe divise per modulo.
3. Per portarla in Moodle: «crea il .mbz della mappa», oppure **Scarica il backup per Moodle** nell'editor (uno .zip con dentro il .mbz). Nel corso: **Ripristina** → carica il .mbz → ripristina in questo corso. L'attività arriva già impostata: ogni studente vede solo la propria scheda.
4. Per cambiare la mappa di un'attività già usata dagli studenti non ripristinare un altro backup: scarica il **Preset** dall'editor e importalo nella stessa attività (scheda Preset). Le spunte restano.

Se gli studenti non vedono «Aggiungi scheda», di solito è la modalità gruppo: con i gruppi separati chi non è in un gruppo non può aggiungere schede.

## Se qualcosa non va

- **«Inizia» non avvia la sessione**: guarda il riquadro **Impostazioni** nella vista iniziale. Se l'avvio non è configurato, chiedi a Claude «configura l'avvio automatico della dashboard»; nel frattempo usa la frase da incollare.
- **Il ripristino in Moodle si lamenta della versione**: Moodle è stato aggiornato. Dai a Claude il backup di un quiz qualsiasi fatto con il Moodle nuovo: aggiorna il generatore.
- **Una domanda generata non è come te l'aspettavi**: correggila nella dashboard, non nell'XML o in Moodle, e rigenera.
