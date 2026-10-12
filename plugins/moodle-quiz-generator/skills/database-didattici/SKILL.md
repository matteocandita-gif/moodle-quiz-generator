---
name: "database-didattici"
description: "Crea, sceglie e controlla i database di prova per SQL e PHP/MySQL: dati italiani coerenti in tre taglie, script per phpMyAdmin e per la dashboard, SQLite per CodeRunner, catalogo, controllo che i dati smascherino gli errori tipici delle query."
---

# Database didattici

Questa skill dà all'utente i database di prova per SQL e PHP/MySQL: per le domande CodeRunner SQL e PHP (prototipi `sql_salvemini` e `php_mysqli_sqlite`, SQLite su Jobe), per le lezioni e le attività in phpMyAdmin/XAMPP (MySQL), per le verifiche al computer. L'utente non scrive i database a mano: dà i requisiti, la skill li progetta, li genera con dati coerenti e controlla che smascherino gli errori tipici.

## Dove stanno le cose

Tutto il necessario è in questa skill. Copia la cartella della skill in `/home/claude/dbdid/` (gli script scrivono in `../database` e `../catalogo.json`, e la cartella della skill può essere in sola lettura) e lavora lì.

| File | Serve per |
|---|---|
| `scripts/dati_it.py`, `scripts/costruisci.py` | generare un database da un modello (sempre insieme, nella stessa cartella) |
| `scripts/verifica_query.py` | controllare che i dati smascherino gli errori delle query e che l'ordine dei risultati non abbia pari merito |
| `scripts/catalogo.py` | aggiornare `catalogo.json` dopo aver aggiunto o rigenerato un database |
| `references/modello.md` | **sempre** prima di scrivere un modello: formato, Generatore, tipi validi in MySQL e SQLite, come evitare i cicli infiniti |
| `references/regole-dati.md` | **sempre** prima di progettare i dati: coerenza, trappole, pari merito, database paralleli, taglie |
| `modelli/<nome>.py` | i modelli dei database del catalogo (`biblioteca.py` è l'esempio di riferimento; `palestra.py`, `cinema.py`, `veterinario.py` sono tre modelli paralleli) |
| `catalogo.json`, `database/<nome>/<taglia>/…` | il catalogo e i file generati (`.sql` comune, `_mysql.sql`, `scheda.md`, `info.json`); i file SQLite `.db` non ci sono: li rigenera `costruisci.py` con lo stesso modello, identici |
| `assets/catalogo.html` | la pagina «Database didattici» da pubblicare per l'utente |

**Il catalogo dell'utente.** I database della skill sono il punto di partenza comune; quelli che l'utente crea stanno nella sua pagina «Database didattici», un artifact privato che mostra i database con schema, taglie, trappole e i pulsanti per copiare gli script. Cercala con `Artifact` (`action: "list"`, titolo «Database didattici»): se c'è, scarica `catalogo.json` e le cartelle `database/` e `modelli/` che la skill non ha (`action: "read"`, `paths`) nella copia di lavoro. Se non c'è, creala quando serve la prima volta (un database nuovo, o l'utente che vuole sfogliare il catalogo): pubblica `assets/catalogo.html` come pagina, con `catalogo.json` e i file `.sql` di `database/` in `files` (`.sql` con `contentType: "text/plain"`), e dai il link all'utente.

## Riusare o creare

L'utente riusa pochi database fissi, che gli studenti imparano a conoscere, e ne crea di nuovi quando servono. Prima di crearne uno, guarda il catalogo: se un database esistente copre le tabelle e le relazioni che servono all'esercizio, proponi quello (eventualmente con una taglia diversa, o con poche righe aggiunte per una domanda).

Per un database nuovo:

1. **Requisiti.** L'utente dice di solito il numero di tabelle, a volte il contesto, gli argomenti da esercitare (JOIN, GROUP BY, NULL, vincoli…) e la classe. Se manca il contesto, proponi tre alternative in una riga ciascuna, con le tabelle che avrebbero, e scegli lui; se mancano gli argomenti, deducili dalla richiesta e dillo.
2. **Schema.** Proponi in chat lo schema in notazione (`Tabella (__chiave__, Colonna, Esterna*)`), le relazioni (uno a molti, molti a molti con la tabella ponte) e le taglie, prima di generare. Rispetta il livello della classe: in terza al massimo uno a molti, la tabella ponte quando l'hanno vista.
3. **Modello.** Scrivi `modelli/<nome>.py` (`modello.md`), con i dati coerenti, i `CONTROLLI` delle regole del mondo e le `TRAPPOLE` della tabella di `regole-dati.md` adatte allo schema.
4. **Genera** le tre taglie: `python3 costruisci.py ../modelli/<nome>.py --tutte --uscita ../database` (dalla cartella `scripts/`). Si ferma se i dati violano un vincolo, un controllo o i limiti di MySQL: correggi il modello, non i dati generati. Leggi la `scheda.md` della taglia media come la leggerebbe uno studente: nomi, date e quantità devono essere credibili.
5. **Controlla le trappole** con 6-10 query rappresentative degli argomenti richiesti (una per trappola almeno), scritte in una specifica come quella di `domande-coderunner-sql` (`=== database`, `=== question`, `=== name`, `=== answer`, `=== test`), e `python3 verifica_query.py --specifica prove.txt` su ogni taglia. Ogni variante segnata `NO` è un errore tipico che i dati non distinguono dalla soluzione: aggiungi o cambia righe nel modello e rigenera, finché non ne restano. Le righe `(i)` sono informative (varianti equivalenti o ordinamenti). Le righe `PARI MERITO` dicono che l'ORDER BY della soluzione lascia righe alla pari: CodeRunner confronta nell'ordine, quindi una risposta giusta risulterebbe sbagliata; servono valori distinti nelle chiavi d'ordinamento tipiche.
6. **Pubblica e salva**: `python3 catalogo.py ../database ../catalogo.json`, poi ripubblica la pagina «Database didattici» dell'utente (stesso URL) passando in `files` `catalogo.json`, i file nuovi o cambiati della cartella del database (`.sql` con `contentType: "text/plain"`; i `.db` restano fuori) e il modello in `modelli/<nome>.py`: la pagina è l'unico posto in cui il database nuovo resta. Se l'utente vuole anche una copia sul suo computer e il computer è collegato, salvala dove indica.

Nel messaggio finale: schema in notazione, righe per taglia, trappole seminate, esito del controllo delle query, e come usarlo (sotto).

**Database paralleli** per le varianti di una verifica ripetibile (una lettera, un database): stessa forma (per esempio una relazione 1-N più una N-N con la tabella ponte), stesse trappole nelle stesse quantità (padri senza figli, omonimi, confini dell'anno, NULL, una data di registrazione distinta dalla data della tabella ponte), contesti diversi (palestra, cinema, ambulatorio veterinario). Dettaglio in `regole-dati.md`.

## Usarlo

- **Dashboard «Bozze dei quiz»** (domande CodeRunner SQL): lo script comune `<nome>_<taglia>.sql` va nel campo `database` del quiz (riquadro «Database del quiz»), con il nome del database. La parte 2 ne ricava da sola le versioni con le tabelle vuote o senza tabelle. Dopo aver scritto le domande, lancia `verifica_query.py --specifica` sulla `specifica-sql.txt` prodotta da `da_dashboard.py`: per una domanda con un confine suo (una data, una soglia) o per sciogliere un pari merito aggiungi in fondo allo script del quiz le INSERT o gli UPDATE che servono, con un commento `-- righe aggiunte per L5 - B3`, senza toccare il database del catalogo. I casi che servono a una sola prova nascosta vanno invece nel suo `=== extra`.
- **CodeRunner PHP** (`php_mysqli_sqlite`): lo stesso script comune è il database da allegare con `domande-php-mysqli-mock`.
- **phpMyAdmin/XAMPP**: lo script `<nome>_<taglia>_mysql.sql` crea il database `<nome>`, cancella le tabelle se esistono e le ricrea, quindi si può reimportare per ripartire dai dati originali (scheda SQL o Importa). Il pulsante «Copia lo script per phpMyAdmin» del catalogo lo copia già pronto.
- **Tracce**: la notazione dello schema (pulsante «Copia lo schema per le tracce», o la `scheda.md`) va già bene per la dashboard; per Moodle c'è la versione HTML nella scheda.

## Regole che non si dimenticano

- **Coerenza prima di tutto**: date nell'ordine del mondo, nomi coerenti con la nazionalità, quantità che tornano, luoghi con la provincia giusta; ogni regola importante è un `CONTROLLO`.
- **Trappole in tutte le taglie**: padri senza figli, NULL, omonimi, valori sui confini, gruppi con la soglia esatta, testi per LIKE; il controllo con `verifica_query.py` decide se bastano.
- **Compatibili con MySQL e SQLite**: niente ENUM né BOOLEAN, `AUTO_INCREMENT` prima di `PRIMARY KEY`, niente parole riservate, lunghezze rispettate (MySQL rifiuta quello che SQLite accetta). `costruisci.py` controlla, ma non esegue MySQL: la prima volta che un database va in phpMyAdmin, chiedi all'utente di confermare che l'import è riuscito.
- **Riproducibili**: stesso modello e stesso seme danno gli stessi dati; non modificare a mano gli script generati, cambia il modello. Ogni modello ha un seme suo (con lo stesso seme i nomi delle persone si ripetono tra database diversi).
- **Niente cicli infiniti**: un valore unico cercato a caso (combinazioni nome e livello, titoli) può non trovarsi più nella taglia grande; ruota le liste e prova sempre tutte e tre le taglie (`modello.md`).
- **Niente persone reali**: nomi combinati a caso, domini email inventati, mai nomi di studenti o colleghi.

## Le altre skill

| Per | Skill |
|---|---|
| Domande CodeRunner SQL (tipologie, test, prototipo) | `domande-coderunner-sql` |
| Domande CodeRunner PHP con database | `domande-php-mysqli-mock` |
| Quiz completo con la dashboard (il database del quiz si sceglie o si crea qui) | `progettazione-quiz`, `materiali-moodle` |