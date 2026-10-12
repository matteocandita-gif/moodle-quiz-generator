---
name: "domande-coderunner-sql"
description: "Crea domande CodeRunner SQL per il Moodle dell'utente (prototipo sql_salvemini, SQLite 3.46 su Jobe) e le consegna come Moodle XML pronto da importare, con il database SQLite costruito e allegato e gli output attesi calcolati eseguendo la soluzione. Copre SELECT, JOIN, GROUP BY, INSERT, UPDATE, DELETE, CREATE TABLE, domande in due passi, debugging, vincoli di integrità, campo di prova e controllo di sintassi. Converte anche le vecchie domande SQL (prototipi sql e sql_foreignkeys) rigenerando gli output per il nuovo SQLite. Nei quiz (verifiche ed esercitazioni) la usano progettazione-quiz per le convenzioni delle tracce e materiali-moodle per produrre l'XML dalla dashboard: un quiz intero si comincia sempre con progettazione-quiz. Da sola serve per domande SQL sciolte e per le conversioni, anche senza nominare CodeRunner, SQLite o l'XML: \"una query sulle JOIN da correggere in automatico\", \"sistema le domande SQL che non passano più\"."
---

# Domande CodeRunner SQL

Le domande SQL dell'utente girano su CodeRunner con il prototipo **`sql_salvemini`**: SQLite 3.46 su Jobe, chiavi esterne attive come in MySQL con InnoDB, controllo di sola sintassi per le verifiche, errori SQL mostrati come output. L'XML non si scrive a mano: si scrive una specifica e lo script costruisce il database, esegue la soluzione con un emulatore del client sqlite3 verificato su Jobe e calcola gli output attesi.

## Il percorso dei quiz

Ogni quiz Moodle (verifica, esercitazione, ripasso, anche di programmazione) segue un solo percorso, con la dashboard «Bozze dei quiz»:

1. **`progettazione-quiz`**, parte 1, didattica: tipo di quiz, scaletta e tracce nella dashboard, riviste e approvate dall'utente. Per una verifica di programmazione carica `verifiche-programmazione`; il database di un quiz SQL o PHP viene da `database-didattici`.
2. **`materiali-moodle`**, parte 2, tecnica: dal database della dashboard produce XML e `.mbz`; per le domande di programmazione usa `domande-coderunner-js`, `domande-coderunner-sql` e `domande-php-mysqli-mock`.

Nessun'altra skill è un punto di partenza per un quiz. Da sole servono solo per ciò che non diventa un quiz: una domanda singola, una correzione o un controllo (`materiali-moodle` o la skill CodeRunner del linguaggio), domande per la banca o pagine di teoria (`materiali-moodle`), un database per una lezione in phpMyAdmin (`database-didattici`), la conversione delle vecchie domande SQL (`domande-coderunner-sql`).

## Regola di lavoro

Un quiz o una verifica intera non parte da qui: si progetta con `progettazione-quiz` nella dashboard, e questa skill la usa `materiali-moodle` per produrre le domande. Per un gruppo di domande sciolte (per la banca, non un quiz), prima la proposta: elenco delle domande (nome, tipologia, che cosa allena, difficoltà), il database che userai (dal catalogo di `database-didattici`, o il file dell'utente), il nome della categoria proposto da te. Si produce dopo la conferma. Una domanda singola o una correzione si fa subito.

## Dove trovare che cosa

| File | Leggilo quando |
|---|---|
| `references/tipologie.md` | **sempre**: le tipologie del deposito dell'utente, quale database serve a ognuna, come si scrivono i test |
| `references/compatibilita.md` | **sempre** prima di scrivere consegne e soluzioni: i costrutti MySQL che SQLite rifiuta o tratta in modo diverso |
| `references/formato-specifica.md` | **sempre** prima di produrre l'XML: prototipo, specifica, opzioni, script |
| `references/stile-html.md` | per il testo della domanda (parte «Testo delle domande») |
| `references/esempio-specifica.txt` | modello completo: una domanda per tipologia, con il database |

## Le regole che non si dimenticano

- **Una sola soluzione giusta per l'output**: CodeRunner confronta le righe nell'ordine, quindi la soluzione ordina sempre (`ORDER BY`) e l'ordine deve essere **unico**: nessuna coppia di righe alla pari nelle chiavi d'ordinamento, sui dati del database e delle prove con `=== extra`. Se c'è un pari merito, scegli una chiave che non si ripete, cambia i dati o scrivi il secondo criterio nel testo; `verifica_query.py` di `database-didattici` lo segnala. Colonne: nelle domande del quiz l'elenco non serve, lo studente le vede nel risultato atteso; l'ordinamento si chiede nel testo solo dove fa parte del problema.
- **Prove nascoste con dati in più**: `=== test HIDE` seguito da `=== extra` con le INSERT (o gli UPDATE) che aggiungono confini, casi da escludere, righe senza collegamenti solo per quella prova, senza toccare il database della domanda.
- **CREATE**: il test è `[[struttura Tabella]]`, mai `.schema`. Nel testo indica tipi e vincoli esatti.
- **MySQL contro SQLite**: niente `PRIMARY KEY AUTO_INCREMENT` in quest'ordine, `ENUM`, `NOW()`, `YEAR()`; attenzione a `5/2` = 2 e ai decimali mostrati come `9` e `9.5`. Dettagli in `compatibilita.md`.
- **Database giusto per la tipologia**: vuoto per le CREATE, tabelle senza righe per le INSERT nella tabella padre, pieno per il resto.
- **Gli output non si scrivono a mano**: li calcola lo script. Se un risultato non è quello che ti aspettavi, è la soluzione o la consegna da rivedere.
- **Testo** nello stile compatto delle domande, con lo schema delle tabelle (chiave primaria sottolineata, chiavi esterne con l'asterisco). Nelle query la forma è fissa: «Il database contiene:» con lo schema, una relazione per riga; una breve descrizione solo di ciò che non si capisce dai nomi; **«Scrivere la query opportuna per ottenere i seguenti dati:»** in grassetto, in un paragrafo a sé; la richiesta in un paragrafo separato.

## Produrre le domande

1. Scrivi la specifica in `/home/claude/`, partendo da `references/esempio-specifica.txt`.
2. Dalla cartella della skill: `python3 scripts/crea_xml.py specifica.txt /home/claude/NOME.xml`. Se si ferma, correggi e rilancia. Leggi NOTE e AVVISI: un errore SQL nella soluzione va bene solo nelle domande sui vincoli; nel debugging controlla che il primo messaggio sia quello voluto.
3. Copia l'XML in `/mnt/user-data/outputs/` e presentalo (o passalo a `materiali-moodle` per l'unione, se fa parte di una sequenza).
4. Nel messaggio: categoria, domande per tipologia, note per il docente, e il promemoria: dopo l'import, il **bulk tester** di CodeRunner sulla categoria è il controllo definitivo su Jobe.

Se l'utente non ha ancora installato il prototipo, dagli `assets/PROTOTYPE_sql_salvemini.xml` da importare nella categoria dei prototipi, prima delle domande.

## Convertire le domande vecchie

Le domande del deposito con i prototipi `sql` e `sql_foreignkeys` non passano più dopo l'aggiornamento di SQLite su Jobe (output nel formato vecchio). Con l'export della categoria:

```bash
python3 scripts/rigenera_attesi.py export.xml /mnt/user-data/outputs/NOME-rigenerate.xml --prefisso "Rigenerate"
```

Riporta all'utente il resoconto (domande convertite, domande da controllare e perché) e ricordagli che l'import crea domande nuove: con il prefisso finiscono in categorie separate, e nei quiz vanno sostituite alle vecchie.

## Le altre skill

Questa skill produce solo domande CodeRunner SQL. Pagine, Cloze e altri tipi di domanda sono di `materiali-moodle`, che coordina le sequenze e unisce gli XML. Lo stile HTML si decide lì: `references/stile-html.md` qui è una copia.