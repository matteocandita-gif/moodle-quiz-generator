---
name: "materiali-moodle"
description: "Parte 2, tecnica, del percorso dei quiz Moodle dell'utente, docente di informatica SIA: dal database della dashboard «Bozze dei quiz» produce il Moodle XML e il backup .mbz del quiz da ripristinare, coordinando le skill CodeRunner (domande-coderunner-js, domande-coderunner-sql, domande-php-mysqli-mock). Un quiz intero (verifica, esercitazione, ripasso) si comincia sempre con progettazione-quiz. Da sola serve per ciò che non diventa un quiz: una domanda (Cloze, risposta multipla, vero/falso, risposta breve e aperta) o un gruppo di domande per la banca, una pagina HTML di teoria o un esempio svolto nel suo stile, il controllo o la correzione di domande esistenti, la lettura di backup .mbz ed export XML. Esempi: \"genera il quiz dalla dashboard\", \"una Cloze sulle JOIN\", \"una pagina di ripasso sul CSS\", \"controlla queste Cloze\"."
---

# Materiali Moodle

**Lingua.** Rispondi all'utente sempre in italiano, anche quando il messaggio che avvia la skill o il comando è in inglese: quando si sceglie un comando o una skill dal menù senza scrivere nulla, l'app aggiunge da sola una frase in inglese.

Questa skill produce il materiale che l'utente usa nel Moodle della scuola (versione 5.2): domande per i quiz, pagine di teoria, quiz completi. Le domande si consegnano come **file Moodle XML** generato da uno script, mai scritto a mano: lo script controlla le regole che l'utente ha fissato dopo averle viste fallire in Moodle. Un quiz completo si consegna anche come **backup `.mbz`** da ripristinare, con pagine, sezioni, punti e impostazioni già a posto.

È la parte 2 del percorso dei quiz e lo strumento per le richieste che non diventano un quiz.

## Il percorso dei quiz

Ogni quiz Moodle (verifica, esercitazione, ripasso, anche di programmazione) segue un solo percorso, con la dashboard «Bozze dei quiz»:

1. **`progettazione-quiz`**, parte 1, didattica: tipo di quiz, scaletta e tracce nella dashboard, riviste e approvate dall'utente. Per una verifica di programmazione carica `verifiche-programmazione`; il database di un quiz SQL o PHP viene da `database-didattici`.
2. **`materiali-moodle`**, parte 2, tecnica: dal database della dashboard produce XML e `.mbz`; per le domande di programmazione usa `domande-coderunner-js`, `domande-coderunner-sql` e `domande-php-mysqli-mock`.

Nessun'altra skill è un punto di partenza per un quiz. Da sole servono solo per ciò che non diventa un quiz: una domanda singola, una correzione o un controllo (`materiali-moodle` o la skill CodeRunner del linguaggio), domande per la banca o pagine di teoria (`materiali-moodle`), un database per una lezione in phpMyAdmin (`database-didattici`), la conversione delle vecchie domande SQL (`domande-coderunner-sql`).

## Regola di lavoro

- **Un quiz completo** (verifica, esercitazione, ripasso) si progetta con la skill `progettazione-quiz`: tipo di quiz, scaletta e tracce nella dashboard «Bozze dei quiz». Questa skill interviene dopo, come parte 2, e trasforma il database della dashboard in XML e `.mbz` (sezione «Dalla dashboard»). Per una verifica di programmazione (JavaScript, SQL, PHP) le indicazioni didattiche stanno in `verifiche-programmazione`.
- **Un gruppo di domande o pagine** che non diventa un quiz progettato nella dashboard: prima una proposta breve (elenco con nome, tipo, che cosa allena; categoria di destinazione; domande che passano a una skill CodeRunner; distribuzione su pagine), poi i file dopo la conferma.
- **Una richiesta puntuale** (una domanda, una correzione, un controllo) si esegue subito.

Se mancano informazioni essenziali (classe, che cosa hanno già visto gli studenti, lezione di appartenenza), chiedile tutte insieme.

## Dalla dashboard: XML e .mbz

Il database della dashboard è il formato di consegna tra le due parti: tutto quello che va in Moodle è scritto nelle righe con convenzioni precise (riquadri, scelte `(x)` / `( )`, campi Cloze nella sintassi di Moodle, «correzione» separata dalle note interne), e gli script lo trasformano senza ritrascrizioni. Gli script stanno in `scripts/` di questa skill; le convenzioni della traccia in `references/formato-consegna.md` di `progettazione-quiz`.

1. **Trova la dashboard** dell'utente (`progettazione-quiz`, «La dashboard dell'utente») e lancia gli script direttamente da `scripts/` di questa skill: scrivono solo nella cartella d'uscita e trovano da soli le skill CodeRunner accanto a questa. Leggi `formato-consegna.md` di `progettazione-quiz` se devi capire una traccia.
2. **Esporta il database** con `ArtifactData` sull'URL della dashboard: `list` di `quiz/<id>/domande` e `get` di `quiz` / `<id>`, entrambi con `out_dir` nella stessa cartella di esportazione; se il quiz ha `deposito`, anche `get` di `impostazioni` / `depositi` (vedi «Depositi»).
3. **Genera**: `python3 genera_quiz.py EXPORT <id> USCITA --nome="<nome del quiz>"` (con `--immagini=CARTELLA` se le tracce citano immagini `![…](nome.png)`: le incorpora nell'XML con `allega_immagini.py` e quindi nell'`.mbz`; con `--varianti=a` in una verifica ripetibile di cui è pronta solo la variante a: converte solo quelle righe ed elenca le altre). In un comando: `da_dashboard.py` (specifica, con categoria «Lezione N - argomento» e nomi `L<lezione> - <pos> - <prefisso>: <titolo>`, o «V5R - argomento» e `V5R - <pos> - …` quando la lezione è il codice di una verifica; ogni a capo dentro un paragrafo della traccia diventa `<br>`, e `impaginazione.json` con sezioni, pagine, punti e preset), `crea_xml.py`, le domande CodeRunner JavaScript con `crea_xml.py` di `domande-coderunner-js` (cerca da solo la sua cartella `scripts/`, altrimenti `--js=CARTELLA`), le SQL con `crea_xml.py` di `domande-coderunner-sql` (`--sql=CARTELLA`), le PHP con `php_attesi.py` e `crea_xml.py --verifica` di `domande-php-mysqli-mock` (`--php=CARTELLA`), `unisci_xml.py`, `controlla_xml.py`, `crea_mbz.py`. Si ferma al primo passo che fallisce con l'elenco delle righe che non rispettano le convenzioni, e segnala le righe non ancora approvate. Leggi i messaggi `PRELOAD` delle domande di debug: dicono che cosa vede lo studente al primo tentativo, e deve corrispondere alla traccia.
4. **Consegna** l'XML, il `.mbz` o entrambi, come chiede l'utente (di norma il `.mbz` per un quiz nuovo); se il computer è collegato e l'utente ha indicato una cartella per i quiz generati, salvali anche lì.

I passi si possono anche lanciare uno per uno (`da_dashboard.py`, `crea_xml.py`, `crea_mbz.py`), per esempio per rifare solo l'`.mbz` con un'impaginazione cambiata.

Se una riga non si può realizzare così com'è (un campo che Moodle non accetta, un tipo che lo script non gestisce), **non arrangiarti** con una versione diversa: torna a `progettazione-quiz`, riscrivi la traccia, metti la riga «da rivedere» con la nota e chiedi conferma.

**Righe CodeRunner**: la traccia è il testo della domanda, soluzione e test stanno nel campo `coderunner` della riga («Soluzione e test», sezioni `=== answer`, `=== test`, `=== stdin`, `=== code`, `=== preload`… descritte in `formato-consegna.md` di `progettazione-quiz`). Le **JavaScript** le converte `genera_quiz.py` e finiscono nell'XML e nell'`.mbz` con le altre. Gli **esercizi HTML e CSS** (`libero_html`, `libero_css`: editor di CodeRunner senza test, correzione manuale) li scrive direttamente `da_dashboard.py`, con la «Correzione» nel feedback generale e il riquadro «Attenzione al controllo automatico» aggiunto in fondo al testo. L'HTML usa il prototipo scelto nel campo `prototipoHtml` del quiz: di norma `php_con_test`, con anteprima, che ha lo scratchpad (lo studente vede la pagina interpretata): risposta e codice di partenza nel formato JSON dello scratchpad, test fittizio «codice salvato!»; con `prototipoHtml: html`, senza anteprima, il prototipo `html` (il campo serve solo a incollare il codice scritto nell'editor e provato nel browser; test «codice salvato»); il CSS usa il prototipo `css` (test «codice salvato»). Le **SQL** le converte `genera_quiz.py` con `crea_xml.py` di `domande-coderunner-sql` (la cerca da sola, altrimenti `--sql=CARTELLA`): il database sta nel campo `database` del quiz (riquadro «Database del quiz» della scaletta, script di CREATE TABLE e INSERT), lo script costruisce il file SQLite pieno, solo struttura o vuoto per ogni domanda, calcola gli output e lo allega; nell'`.mbz` il file allegato va in `files.xml` e `files/` (verificato con un ripristino reale e il bulk tester). Leggi i messaggi `PRELOAD` (primo errore del debug) e `NOTA` (soluzione che produce un errore: giusto solo nei vincoli). Le **PHP** (prototipo `php_mysqli_sqlite`, stesso campo `database` del quiz) le converte `genera_quiz.py` con la skill `domande-php-mysqli-mock` (`--php=CARTELLA` se non la trova): `da_dashboard.py` aggiunge disclaimer della simulazione, normalizzazione dell'output e `FakeDB::configure`, `php_attesi.py` calcola gli output attesi eseguendo la soluzione con PHP e il template del prototipo (dove manca il client `sqlite3` usa `sqlite3_cli.py`, che dà gli stessi messaggi verificati su Jobe), `crea_xml.py --verifica` ricontrolla. Leggi i `PRELOAD` dei debug PHP: il primo errore che vede lo studente.

**Corrispondenze**: `crea_xml.py` non le gestisce; dalla dashboard le scrive direttamente `da_dashboard.py` (righe `elemento <-> corrispondenza` della traccia, convenzione in `formato-consegna.md` di `progettazione-quiz`) e finiscono nell'XML e nell'`.mbz`. Fuori dalla dashboard, per una corrispondenza isolata, scrivi la riga nella forma della dashboard e passa da `da_dashboard.py`, oppure scrivi l'XML copiando la struttura di `domanda_match`.

**Domande PHP con il prototipo `php_mysqli_mock`** (mappa delle query, per le domande vecchie o i messaggi di MySQL): producile con `domande-php-mysqli-mock`, lancia `genera_quiz.py` con `--salta-coderunner` e unisci gli XML con `unisci_xml.py`. Se una riga CodeRunner ha «Soluzione e test» vuoto o incompleto, o un quiz con domande SQL o PHP non ha il database, scrivilo tu in parte 1 (`progettazione-quiz`, database con `database-didattici`) prima di generare.

## Il backup .mbz

**Leggere** un backup: `references/backup-mbz.md` e `scripts/leggi_mbz.py`. `--quiz` mostra per ogni quiz tempo, punteggio, sezioni e, slot per slot, pagina, punti e domanda (nome, versione, banca) o, per le domande casuali, i tag e la categoria da cui pescano con le domande che corrispondono; `--domande TESTO` mostra il testo (ultima versione) delle domande delle categorie che contengono TESTO. Funziona sul backup di un corso e su quello di una singola attività, comprese le domande delle banche condivise usate dal quiz.

**Riallineare la dashboard**: se l'utente ha corretto domande direttamente in Moodle (non è un passaggio obbligatorio, ma può capitare), prima di rigenerare o di scrivere altre varianti chiedi il backup del quiz (con «Includi file») e confrontalo con la dashboard con `scripts/importa_mbz.py --confronta`: la procedura è in `progettazione-quiz` («Modifiche fatte in Moodle»). Lo stesso script importa nella dashboard un quiz vecchio (`--id=ID`, tipo `IMP`). Le domande che il quiz prende da un deposito tengono lo stamp d'origine (`stampOrigine`) e il rapporto dice da quale banca vengono: se il deposito è registrato, metti `deposito` nel quiz, così rigenerandolo (o facendone la copia PDP) nel corso del deposito le domande si riusano senza doppioni.

**Copia PDP** di una verifica (regole didattiche in `verifiche-programmazione`, «Studenti con PDP»; verificato con ripristini reali il 25/10/2026). `crea_pdp.py` ricava la copia da un backup della verifica: le posizioni tolte restano a 0 punti, prima di ognuna la descrizione «Riduzione contenuti PDP -k» (`--pei` per le PEI), in apertura la dichiarazione (`--dichiarazione=mappe`, predefinita, `tempo`, `generica`, `nessuna`), nome con «(PDP)». Descrizioni e dichiarazioni sono quelle della banca condivisa, con i loro stamp: al ripristino Moodle le riusa, anche da un corso diverso da quello della banca. I loro dati stanno nella dashboard in `impostazioni/pdp` (si rifanno con `crea_pdp.py --prepara-banca BACKUP_DELLA_BANCA.mbz OUT.json` e `ArtifactData set` con `file_path`). Due modalità:

- **dalla dashboard** (preferita): se il quiz ha `deposito`, esporta anche `impostazioni` / `pdp` e lancia `genera_quiz.py … --pdp` (con le stesse `--varianti` della verifica); toglie le posizioni segnate «tolta nella PDP» (campo `pdp` delle righe). La verifica rigenerata ha gli stamp della verifica vera (stabili, o `stampOrigine`), quindi la copia si aggancia alle sue domande. Senza `deposito` lo script si ferma: le domande stanno nella banca del quiz e servono contesto e identificativi che assegna Moodle al ripristino;
- **dal backup** della verifica ripristinata (sempre possibile): `crea_pdp.py VERIFICA.mbz BANCA_PDP.json USCITA.mbz --togli=T2,Q1` (numeri di slot di `leggi_mbz.py --quiz`, o codici di posizione cercati nei nomi e nei tag).

Ripristino della copia: nel corso della verifica. Ricorda all'utente di controllare che nella banca di sistema non compaiano domande nuove (le descrizioni e le domande della verifica sono riferimenti).

**Creare** un quiz: `crea_mbz.py DOMANDE.xml IMPAGINAZIONE.json USCITA.mbz` produce il backup di una singola attività quiz, con la struttura di Moodle 5.2.2 verificata su backup reali dell'utente e ripristinata con successo. Le domande stanno nella banca del quiz stesso, nella categoria della lezione. Tipi gestiti: descrizione, Cloze (campi a risposta breve, numerici, menù), risposta multipla, vero/falso, risposta breve, aperta, corrispondenza, CodeRunner JavaScript, HTML, CSS, SQL e PHP (le opzioni si copiano dall'XML, verificato su backup reali; i database allegati delle SQL e delle PHP diventano file del backup, come le immagini del testo delle domande, componente `question`, area `questiontext`). Domande casuali per tag: le posizioni con varianti (vedi «Verifiche ripetibili»).

L'impaginazione dice nome del quiz, preset, voto (10) e sufficienza (6), e per ogni sezione il titolo e le domande con pagina e punti. Preset:

- **esercitazione**: comportamento interattivo, tentativi illimitati, nessun limite di tempo, revisione completa subito;
- **verifica**: feedback differito, un tentativo, tempo del quiz, durante la prova solo il tentativo e il punteggio massimo; alla restituzione l'utente apre feedback e risposte dalle opzioni di revisione (ricordalo nella consegna). Le domande CodeRunner seguono le loro opzioni anche con il feedback differito: lo studente prova il codice e vede il risultato dei test;
- **studio** (tipo «Studio e domande», SD): navigazione sequenziale, feedback differito, un tentativo, tempo del quiz (40 minuti se manca); durante il tentativo nessuna verifica, revisione completa subito dopo la consegna e dopo, a quiz aperto. Nella consegna ricorda che voto ed elementi di valutazione compaiono solo dopo la correzione delle aperte («Valutazione manuale», per domanda), mentre l'esito delle chiuse si vede subito domanda per domanda.

Il preset viene dal tipo di quiz della dashboard; `impostazioni` nell'impaginazione sovrascrive singoli campi del quiz (es. `{"timelimit": 5400}`).

**Depositi** (domande direttamente nella banca di un corso deposito, verificato con ripristini reali il 24/10/2026). Di norma le domande stanno nella banca del quiz e l'utente le sposta poi nel deposito. Se il quiz della dashboard ha `deposito`, invece, vanno nella banca qbank di quel deposito (impaginazione `banca`, scritta da `da_dashboard.py`). Regole di Moodle:

- il ripristino scrive in una banca esterna al backup **solo se si ripristina nel corso in cui la banca sta**; altrimenti mette tutto, nascosto, nella banca delle domande condivisa di sistema (il quiz funziona lo stesso);
- **non crea categorie nuove** in una banca esterna: la categoria deve esistere già, riconosciuta per stamp. Due casi: una categoria nota del deposito (registrata con il suo stamp), oppure la categoria che un quiz della dashboard ha creato nella sua banca e l'utente ha spostato nel deposito: lo stamp della categoria è stabile, ricavato dal nome, quindi i quiz successivi con la stessa categoria la ritrovano. Una categoria nuova si crea solo come oggi: ripristino nella banca del quiz e spostamento a mano;
- le domande che ritrova per stamp le **riusa senza doppioni**. Gli stamp delle domande sono stabili: impronta del contenuto (una domanda cambiata ne ha uno nuovo e diventa una domanda nuova), oppure lo stamp d'origine (`stampOrigine` della riga) per le domande importate da un backup che stanno già nel deposito.

**Registrare un deposito**: l'utente manda il backup di un quiz che usa la banca del deposito (o il backup del corso). `leggi_mbz.py BACKUP --banche` stampa contesto, modulo, categoria «top» e categorie con i loro stamp. Scrivi o aggiorna con `ArtifactData` sull'URL della dashboard il documento `impostazioni/depositi`: `{depositi: [{id, nome, corso, contextid, cmid, top_id, top_stamp, categorie: [{nome, id, stamp}]}]}` (`id` breve, per esempio `quinte`; `corso` il nome del corso in cui ripristinare). Quando l'utente crea o sposta categorie nel deposito, aggiornale da un backup nuovo. Nella consegna di un quiz con `deposito`, ricorda di ripristinare nel corso del deposito e riporta gli avvisi `DEPOSITO:` dello script.

Ripristino: nel corso, Ripristina → carica il file → ripristina in questo corso (unisci). Se Moodle viene aggiornato e il ripristino si lamenta della versione, chiedi all'utente un backup fresco di un quiz qualsiasi e aggiorna le costanti di versione in `crea_mbz.py`.

## Distribuzione su pagine

Con la dashboard pagine e sezioni sono già nelle righe e finiscono nel `.mbz`. Per una proposta fuori dalla dashboard, ogni quiz dice come le domande si dividono in pagine.

- **Su una pagina da sole**: le domande complesse, in particolare quelle di programmazione (CodeRunner, debug, esercizi liberi) e le domande aperte con un codice proprio.
- **Sulla stessa pagina**: le domande che hanno bisogno di un contesto che sta in un'altra domanda (un codice, una tabella, una pagina di teoria a cui rispondono, l'esercizio a cui si riferisce una domanda di teoria), sempre; le domande brevi e veloci (vero/falso, risposta multipla rapida) quando condividono lo stesso contesto.
- **Sezioni**: quando il quiz ha parti distinte che lo studente deve vedere (istruzioni, blocchi di una lezione), proponi le intestazioni di sezione di Moodle e la posizione da cui parte ciascuna; compaiono nel blocco di navigazione. Nelle verifiche niente sezioni che rivelino la parte avanzata.

Forma della proposta: nella tabella del tracciato una colonna **Pag.** (le domande sulla stessa pagina hanno lo stesso numero) e una riga di separazione in grassetto all'inizio di ogni sezione:

| Pag. | Pos. | Domanda | Tipo |
|---|---|---|---|
| **— Sezione: Blocco A —** | | | |
| 2 | A1 | Variabili e assegnamento | Teoria |
| 3 | A2 | Il ciclo stampa 5 righe | Vero/falso |
| 3 | A3 | i vale 5 all'uscita | Vero/falso |
| 4 | A4 | Input e calcoli | CodeRunner |

Quando consegni solo l'XML ricorda come applicarla: Ripagina (una domanda per pagina, se è il caso) e poi le intestazioni di sezione nelle posizioni indicate.

## Verifiche ripetibili

Quando l'utente vuole una verifica con più varianti per domanda, il quiz pesca a caso per **tag**:

- tutte le domande e le varianti stanno nella **categoria della lezione**; ogni posizione del quiz è una domanda casuale da quella categoria filtrata per tag;
- **un tag per posizione** (argomento e tipo), non per tipologia generica, con un prefisso che lo renda unico nel sito (es. `rjs4-T1-assegnamento`), senza spazi;
- posizioni con la lettera della variante: `T1a`, `T1b`, `T1c`;
- le varianti della stessa posizione hanno **stessa struttura, difficoltà, tempo e punti**; cambiano contesto e codice;
- le pagine di istruzioni restano domande fisse, senza tag.

**Dalla dashboard** le varianti sono righe con lo stesso campo `tag` (convenzioni in `formato-consegna.md` di `progettazione-quiz`): `genera_quiz.py` aggiunge i `<tags>` all'XML e `crea_mbz.py` crea una domanda casuale per tag con i punti della posizione. Nel backup gli id dei tag sono inventati (da 9900001) e al ripristino Moodle li ricrea per nome. La struttura viene da un backup reale dell'utente (`question_set_reference` con `filtercondition`) ed è stata verificata con un ripristino.

**Fuori dalla dashboard** gli script di `scripts/` non scrivono i tag: aggiungili all'XML finale (`<tags><tag><text>…</text></tag></tags>` prima di `</question>`), verifica con `controlla_xml.py` e, consegnando solo l'XML, elenca all'utente le domande casuali da creare nel quiz. Se una modifica cambia la struttura (posizioni, tag, punti, ordine), elenca all'utente che cosa cambiare nel quiz prima dell'import.

## Dove trovare che cosa

Leggi solo i file che servono alla richiesta:

| File | Leggilo quando |
|---|---|
| `references/stile-html.md` | **sempre** prima di scrivere HTML: pagine con titoli e riquadri, testo compatto delle domande, codice, tabelle, registro |
| `references/cloze.md` | scrivi o correggi Cloze: sintassi, le sette regole dell'utente, le quattro famiglie con esempi |
| `references/domande.md` | risposta multipla, vero/falso, risposta breve, aperta, descrizioni |
| `references/pagine.md` | scrivi pagine: struttura della lezione, pagina «Come lavoriamo oggi», pagina di un blocco, siti dimostrativi |
| `references/sequenza.md` | prepari un'esercitazione completa, soprattutto con codice: le sette parti, il debugging, chi fa che cosa. Per il PHP con database le domande nuove usano il prototipo `php_mysqli_sqlite` (la tabella del file dice ancora `php_mysqli_mock`, che resta per le domande esistenti) |
| `references/formato-specifica.md` | **sempre** prima di produrre l'XML: formato della specifica, opzioni, script |
| `references/backup-mbz.md` | l'utente carica un backup `.mbz` da leggere |
| `references/esempio-specifica.txt` | modello di specifica con una domanda per famiglia: copia la forma |
| `assets/modello-pagina.html` | modello di pagina completa |
| `formato-consegna.md` di `progettazione-quiz` | converti dalla dashboard: convenzioni della traccia, corrispondenze, campo «Soluzione e test» delle CodeRunner (JavaScript, SQL e PHP, con il database del quiz), varianti per tag, campi che vanno in Moodle |

## Le regole che non si dimenticano

Valgono anche per una risposta veloce in chat:

- **Tracce degli esercizi**: estese ed esplicite, in forma impersonale come le scrive l'utente («Definire una funzione dal nome … che prende come parametro … e restituisce …; se … restituire invece …»), con regole, casi limite, forma dell'output ed esempio svolto. Nelle **verifiche** dicono l'obiettivo e non gli strumenti, salvo ciò che è oggetto della valutazione; nelle **esercitazioni** lo strumento è suggerito o non nominato esercizio per esercizio, come deciso nella scaletta (in una richiesta fuori dalla dashboard, chiedilo). Vale anche per le domande prodotte con le skill CodeRunner, anche dove i loro riferimenti parlano di testo compatto.
- **Cloze**: escaping solo di `}` `#` `~` (mai `\/` né `\"`); menù singoli `MULTICHOICE_S`; menù con le stesse opzioni `MULTICHOICE` con ordine statico identico e diverso da quello delle risposte giuste; campi dentro il codice solo in `<pre>` senza `<code>`; niente entità né tag nelle risposte dei campi a risposta breve: nei completamenti HTML il campo contiene il nome del tag e parentesi angolari e barra stanno nel codice.
- **HTML**: frammento senza `<head>`, `<body>`, `<style>`, `<script>`; stili inline; niente emoji; pagine con titoli e riquadri, domande compatte.
- **Feedback**: ogni opzione sbagliata spiega perché è sbagliata.
- **Risposta multipla**: una sola giusta quando l'affermazione vera è una, più giuste (`single: false`, penalità sulle sbagliate che sommata fa −100%) quando sono più d'una, un'opzione per affermazione; dettaglio in `references/domande.md`.
- **Alternative ammesse**: una soluzione ugualmente corretta in programmazione (la concatenazione dove noi interpoliamo, un costrutto equivalente) non è mai un'opzione sbagliata né una risposta rifiutata in un campo: è un'alternativa che non suggeriamo. Nei campi Cloze va accettata; nei feedback «una riga corretta è…», non «la riga giusta è…».
- **Nomi**: `L<lezione> - <blocco><numero> - <tipo>: <titolo>`; nelle verifiche, che hanno un codice al posto del numero di lezione, `V5R - <pos> - <tipo>: <titolo>` e categoria «V5R - argomento». La pagina di un blocco si chiama «Spiegazione» nelle esercitazioni con spiegazione e «Ripasso» nei ripassi.
- **Studenti**: mai nomi completi nei materiali o nelle analisi, solo iniziali.

## Produrre le domande

1. Scrivi la specifica (`references/formato-specifica.md`) in `/home/claude/`, con il codice grezzo nei blocchi `[[codice LINGUAGGIO]]`. Con la dashboard la specifica la scrive `da_dashboard.py`.
2. Lancia `python3 scripts/crea_xml.py specifica.txt /home/claude/NOME.xml` dalla cartella della skill. Se si ferma, correggi la specifica e rilancia. Gli avvisi non bloccano, ma valuta se hanno ragione.
3. Se ci sono domande CodeRunner, producile con la skill indicata in `references/sequenza.md`, poi unisci: `python3 scripts/unisci_xml.py /mnt/user-data/outputs/NOME.xml prima.xml seconda.xml …`, nell'ordine della sequenza. Lancia `controlla_xml.py` anche sull'XML delle altre skill.
4. Presenta l'XML (o l'`.mbz`). Nel messaggio: categoria, numero di domande per tipo, distribuzione su pagine e sezioni da impostare (solo per l'XML), note per il docente, eventuali avvisi rimasti, e per le verifiche quando aprire la revisione. Ricorda che l'import crea sempre domande nuove.

**Domanda singola**: se l'utente vuole il testo da incollare, dagli l'HTML già espanso (passalo da `crea_xml.py` o da `espandi_html.py` per avere il `<pre>` pronto), più risposte e feedback.

## Produrre le pagine

- **Dentro un quiz**: domanda `description` nella specifica, insieme agli esercizi.
- **Attività Pagina o Area di testo e media**: scrivi l'HTML con i blocchi `[[codice]]` e lancia `python3 scripts/espandi_html.py sorgente.html /mnt/user-data/outputs/NOME.html`; presenta il file, che l'utente incolla nell'editor in modalità sorgente.

## Controllare materiale esistente

`python3 scripts/controlla_xml.py FILE.xml --avvisi` controlla un export con le stesse regole. Riporta all'utente ogni problema con il nome della domanda e che cosa vede lo studente (es. «nel feedback compare \/»). Le pagine fatte prima di questa skill possono avere emoji o lo stile vecchio: segnalalo una volta, senza elencarlo per ogni pagina.

Per correggere: estrai le domande da modificare nella specifica, correggi, rigenera. L'utente reimporta e sostituisce le vecchie nei quiz.

## Le altre skill

| Per | Skill |
|---|---|
| Progettazione di un quiz completo (parte 1: preset, scaletta, tracce, dashboard) | `progettazione-quiz` |
| Indicazioni didattiche delle verifiche di programmazione (JavaScript, SQL, PHP) | `verifiche-programmazione` |
| CodeRunner JavaScript | `domande-coderunner-js` |
| CodeRunner SQL (SQLite) | `domande-coderunner-sql` |
| CodeRunner PHP con database simulato | `domande-php-mysqli-mock` |
| Database di prova (catalogo, creazione, controllo delle query) | `database-didattici` |
| Diagrammi E/R (immagini per pagine e domande) | `diagrammi-er` |
| Capitoli del libro di testo | `libro-sia` |