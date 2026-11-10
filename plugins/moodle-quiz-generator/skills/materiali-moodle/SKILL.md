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

Per le richieste fuori dalla dashboard (gruppo di domande o pagine, richiesta puntuale, controllo di materiale esistente) leggi `references/fuori-dashboard.md`: come si producono domande e pagine, come si propone la distribuzione su pagine, come si controlla un export.

## Dalla dashboard: XML e .mbz

Il database della dashboard è il formato di consegna tra le due parti: tutto quello che va in Moodle è scritto nelle righe con convenzioni precise (riquadri, scelte `(x)` / `( )`, campi Cloze nella sintassi di Moodle, «correzione» separata dalle note interne), e gli script lo trasformano senza ritrascrizioni. Gli script stanno in `scripts/` di questa skill; le convenzioni della traccia in `references/formato-consegna.md` di `progettazione-quiz`.

1. **Trova la dashboard** dell'utente (`progettazione-quiz`, «La dashboard dell'utente») e lancia gli script direttamente da `scripts/` di questa skill: scrivono solo nella cartella d'uscita e trovano da soli le skill CodeRunner accanto a questa. Leggi `formato-consegna.md` di `progettazione-quiz` se devi capire una traccia.
2. **Esporta il database** con `ArtifactData` sull'URL della dashboard: `list` di `quiz/<id>/domande` e `get` di `quiz` / `<id>`, entrambi con `out_dir` nella stessa cartella di esportazione; se il quiz ha `deposito`, anche `get` di `impostazioni` / `depositi` (vedi «Depositi»); se il pannello «Impostazioni avanzate» dà SEB con file (di norma le verifiche di programmazione), anche `get` di `impostazioni` / `seb` (vedi «Safe Exam Browser»); per le verifiche anche `get` di `impostazioni` / `note` (vedi «Domanda delle note»).
3. **Genera**: `python3 genera_quiz.py EXPORT <id> USCITA --nome="<nome del quiz>"` (con `--immagini=CARTELLA` se le tracce citano immagini `![…](nome.png)`: le incorpora nell'XML con `allega_immagini.py` e quindi nell'`.mbz`; con `--varianti=a` in una verifica ripetibile di cui è pronta solo la variante a: converte solo quelle righe ed elenca le altre). In un comando: `da_dashboard.py` (specifica, con categoria «Lezione N - argomento» e nomi `L<lezione> - <pos> - <prefisso>: <titolo>`, o «V5R - argomento» e `V5R - <pos> - …` quando la lezione è il codice di una verifica; ogni a capo dentro un paragrafo della traccia diventa `<br>`, e `impaginazione.json` con sezioni, pagine, punti e preset), `crea_xml.py`, le domande CodeRunner JavaScript con `crea_xml.py` di `domande-coderunner-js` (cerca da solo la sua cartella `scripts/`, altrimenti `--js=CARTELLA`), le SQL con `crea_xml.py` di `domande-coderunner-sql` (`--sql=CARTELLA`), le PHP con `php_attesi.py` e `crea_xml.py --verifica` di `domande-php-mysqli-mock` (`--php=CARTELLA`), `unisci_xml.py`, `controlla_xml.py`, `crea_mbz.py`. Si ferma al primo passo che fallisce con l'elenco delle righe che non rispettano le convenzioni, e segnala le righe non ancora approvate. Leggi i messaggi `PRELOAD` delle domande di debug: dicono che cosa vede lo studente al primo tentativo, e deve corrispondere alla traccia.
4. **Consegna** l'XML, il `.mbz` o entrambi, come chiede l'utente (di norma il `.mbz` per un quiz nuovo); se il computer è collegato e l'utente ha indicato una cartella per i quiz generati, salvali anche lì.

5. **Esito nella dashboard**: alla fine scrivi nel quiz il campo `esportazione` (`stato` `fatta` o `errore`, `fine`, `file`, `esito` in una riga). La pagina lo mostra accanto al pulsante «Esporta», che fa partire questo stesso lavoro in una sessione dell'attività programmata (`dashboard.md` di `progettazione-quiz`, «Esportare dalla pagina»).

**Prima di generare, leggi i file che riguardano il quiz**, e solo quelli:

- il quiz è una **verifica** (o si chiede la copia PDP): `references/verifiche.md` (copia PDP, domanda delle note, Safe Exam Browser, varianti per tag);
- il quiz ha **`deposito`**: `references/depositi.md`;
- il quiz ha righe **CodeRunner** o **corrispondenze**: `references/righe-coderunner.md`;
- il quiz è **già in Moodle** (svolto dagli studenti, o corretto lì dall'utente): `references/aggiornare-quiz.md`.

I passi si possono anche lanciare uno per uno (`da_dashboard.py`, `crea_xml.py`, `crea_mbz.py`), per esempio per rifare solo l'`.mbz` con un'impaginazione cambiata.

Se una riga non si può realizzare così com'è (un campo che Moodle non accetta, un tipo che lo script non gestisce), **non arrangiarti** con una versione diversa: torna a `progettazione-quiz`, riscrivi la traccia, metti la riga «da rivedere» con la nota e chiedi conferma.

## Il backup .mbz

**Leggere** un backup: `references/backup-mbz.md` e `scripts/leggi_mbz.py`. `--quiz` mostra per ogni quiz tempo, punteggio, sezioni e, slot per slot, pagina, punti e domanda (nome, versione, banca) o, per le domande casuali, i tag e la categoria da cui pescano con le domande che corrispondono; `--domande TESTO` mostra il testo (ultima versione) delle domande delle categorie che contengono TESTO. Funziona sul backup di un corso e su quello di una singola attività, comprese le domande delle banche condivise usate dal quiz.

**Creare** un quiz: `crea_mbz.py DOMANDE.xml IMPAGINAZIONE.json USCITA.mbz` produce il backup di una singola attività quiz, con la struttura di Moodle 5.2.2 verificata su backup reali dell'utente e ripristinata con successo. Le domande stanno nella banca del quiz stesso, nella categoria della lezione. Tipi gestiti: descrizione, Cloze (campi a risposta breve, numerici, menù), risposta multipla, vero/falso, risposta breve, aperta, corrispondenza, CodeRunner JavaScript, HTML, CSS, SQL e PHP (le opzioni si copiano dall'XML, verificato su backup reali; i database allegati delle SQL e delle PHP diventano file del backup, come le immagini del testo delle domande, componente `question`, area `questiontext`). Domande casuali per tag: le posizioni con varianti (vedi «Verifiche ripetibili»).

L'impaginazione dice nome del quiz, preset, voto (10) e sufficienza (6), e per ogni sezione il titolo e le domande con pagina e punti. Preset:

- **esercitazione**: comportamento interattivo, tentativi illimitati, nessun limite di tempo, revisione completa subito;
- **verifica**: feedback differito, un tentativo, tempo del quiz, durante la prova solo il tentativo e il punteggio massimo; alla restituzione l'utente apre feedback e risposte dalle opzioni di revisione (ricordalo nella consegna). Le domande CodeRunner seguono le loro opzioni anche con il feedback differito: lo studente prova il codice e vede il risultato dei test;
- **studio** (tipo «Esercitazione con studio e domande sequenziale», SD): navigazione sequenziale, feedback differito, un tentativo, tempo del quiz (40 minuti se manca); durante il tentativo nessuna verifica, revisione completa subito dopo la consegna e dopo, a quiz aperto. Nella consegna ricorda che voto ed elementi di valutazione compaiono solo dopo la correzione delle aperte («Valutazione manuale», per domanda), mentre l'esito delle chiuse si vede subito domanda per domanda.

Il preset viene dal tipo di quiz della dashboard; `impostazioni` nell'impaginazione sovrascrive singoli campi del quiz (es. `{"timelimit": 5400}`). Le impostazioni avanzate del quiz della dashboard (`navigazione`, `feedback`, `seb`, `password`, in `dashboard.md` di `progettazione-quiz`) valgono con qualsiasi preset: `da_dashboard.py` scrive in `impostazioni` `navmethod` e `password`, e nell'impaginazione `feedback` e `seb`. Se `feedback` è diverso da quello del preset, `crea_mbz.py` cambia insieme comportamento e opzioni di revisione: `immediato` come il preset esercitazione, `differito` come il preset studio; tentativi e tempo restano quelli del preset.

Ripristino: nel corso, Ripristina → carica il file → ripristina in questo corso (unisci). Se Moodle viene aggiornato e il ripristino si lamenta della versione, chiedi all'utente un backup fresco di un quiz qualsiasi e aggiorna le costanti di versione in `crea_mbz.py`.

## Dove trovare che cosa

Leggi solo i file che servono alla richiesta:

| File | Leggilo quando |
|---|---|
| `references/verifiche.md` | generi una verifica o la sua copia PDP: «Copia PDP», «Domanda delle note», «Safe Exam Browser», «Verifiche ripetibili» |
| `references/depositi.md` | il quiz ha `deposito`, o c'è un deposito da registrare: «Depositi», «Registrare un deposito» |
| `references/righe-coderunner.md` | il quiz ha domande CodeRunner o corrispondenze: «Righe CodeRunner», «Corrispondenze», prototipo `php_mysqli_mock` |
| `references/aggiornare-quiz.md` | il quiz è già in Moodle: «Aggiornare un quiz già in Moodle», «Riallineare la dashboard» |
| `references/fuori-dashboard.md` | la richiesta non viene dalla dashboard: «Distribuzione su pagine», «Produrre le domande», «Produrre le pagine», «Controllare materiale esistente» |
| `references/stile-html.md` | **sempre** prima di scrivere HTML: pagine con titoli e riquadri, testo compatto delle domande, codice, tabelle, registro |
| `references/cloze.md` | scrivi o correggi Cloze: sintassi, le sette regole dell'utente, le quattro famiglie con esempi |
| `references/domande.md` | risposta multipla, vero/falso, risposta breve, aperta, descrizioni |
| `references/pagine.md` | scrivi pagine: struttura della lezione, pagina «Come lavoriamo oggi», pagina di un blocco, siti dimostrativi |
| `references/sequenza.md` | prepari un'esercitazione completa, soprattutto con codice: le sette parti, il debugging, chi fa che cosa. |
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
| Capitoli del libro di testo | `libro-sia` (skill personale dell'autore, fuori dal plugin: solo se è installata) |