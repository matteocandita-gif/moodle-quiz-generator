# Tracce delle domande CodeRunner SQL

Da leggere quando il quiz ha domande CodeRunner SQL. Fa parte delle regole sulle tracce di `progettazione-quiz` (`SKILL.md`, «Le tracce»): le regole generali (tracce estese, convenzioni, feedback, correzione e note interne) restano lì e valgono anche qui. Le convenzioni generali della traccia (riquadri, scelte, campi Cloze, immagini) sono in `formato-consegna.md`; il formato del campo «Soluzione e test» di queste domande è qui sotto.

## Domande CodeRunner SQL

Prototipo `sql_salvemini` (SQLite 3.46 su Jobe). Tipologie `query`, `create_tabelle`, `query_due_passi`, `vincoli`, `campo_prova`; `debug_msg`, `debug_silenzioso` e `scrittura_scheletro` sono SQL quando i test cominciano con `--` o con `[[struttura …]]` (oppure con una sezione `=== linguaggio` che contiene `sql`).

**Il database** sta nel quiz, non nella riga: campo `database` del documento del quiz, un elenco di `{nome, sql}` con lo script come in phpMyAdmin (CREATE TABLE e INSERT). Nella dashboard si scrive nel riquadro «Database del quiz» della scaletta, che mostra tabelle, righe e quali domande lo usano. Il nome (senza spazi) diventa il nome del file allegato (`nome.db`, `nome_struttura.db`, `nome_vuoto.db`). Con un solo database le domande lo usano tutte; con più database ogni riga dice quale con `database: nome` in `=== options`.

**La traccia** è il testo della domanda (senza campi Cloze né opzioni), con lo schema delle tabelle coinvolte: `Libri (__ISBN__, Titolo, Autore, Prezzo, IdEditore*)`. Le regole della skill `domande-coderunner-sql` valgono già qui: tipi e vincoli esatti nelle CREATE, niente costrutti MySQL che SQLite rifiuta. Schema fisso delle query nelle verifiche:

```
Il database contiene:
Istruttori (__IdIstruttore__, Nome, Cognome, ...)
Corsi (__IdCorso__, Nome, Livello, IdIstruttore*)

Breve descrizione, solo di quello che non è ovvio dai nomi (in ogni domanda, anche se il database si ripete).

**Scrivere la query opportuna per ottenere i seguenti dati:**

La richiesta, in un paragrafo a sé.
```

- **Colonne**: nella traccia non serve l'elenco delle colonne da mostrare: lo studente le vede nell'output del primo test (l'esempio di CodeRunner). La soluzione le fissa (stesse colonne, stesso ordine).
- **Ordinamento**: l'output si confronta riga per riga nell'ordine, quindi la soluzione ha sempre un `ORDER BY`, ma la richiesta di ordinare si scrive solo dove fa parte del problema (non in tutte le domande). Se la traccia non lo chiede, lo studente vede l'ordine dal primo test. Le chiavi dell'ordinamento devono dare **un ordine unico, senza pari merito** sui dati del database e delle prove nascoste: se due righe sono alla pari e la traccia non dice come sciogliere il pareggio, un ordine diverso ma giusto risulta sbagliato. Si risolve cambiando i dati (un UPDATE nello script del quiz), scegliendo una chiave unica o scrivendo il secondo criterio nella traccia; se si lascia apposta, va detto nella `correzione` (si corregge a mano).
- **Prove nascoste** con dati in più: `=== test HIDE` seguito da `=== extra` con le INSERT (o gli UPDATE) che aggiungono i casi limite (pari merito, NULL, righe senza collegamenti, confini delle date) prima di eseguire la query.
- **Correzioni dei dati del quiz**: se un controllo trova un problema nei dati (pari merito, un caso limite che manca) si possono aggiungere in fondo allo script del database del quiz righe `UPDATE` o `INSERT`, invece di rigenerare il database; la `docente` della riga dice perché.

**Soluzione e test** («Soluzione e test», sezioni della specifica di `domande-coderunner-sql`):

| Sezione | Contenuto |
|---|---|
| `=== options` | facoltativa: `database: nome`, `dati: pieno | struttura | vuoto` (se manca la dedurrà lo script: CREATE → vuoto, solo INSERT → struttura, altrimenti pieno), `precheck: 1`, `foreign_keys: 0`, `allornothing: 0`, `grader: RegexGrader`, `hidecheck: 1` |
| `=== preload` | codice di partenza nella casella (debug) |
| `=== answer` | obbligatoria: la soluzione |
| `=== test` / `=== test HIDE` | obbligatoria: comincia con un commento `-- …` che dice che cosa si guarda (`-- il risultato della tua query`, poi l'eventuale SELECT sullo stato finale) oppure è `[[struttura Tabella]]` per le CREATE |
| `=== extra`, `=== expected` | dopo un test, solo se servono (l'output atteso lo calcola lo script; `expected` solo con RegexGrader) |

Gli output non si scrivono: li calcola la parte 2 eseguendo la soluzione sul database. Le tipologie, il database giusto per ognuna e la forma dei test sono in `references/tipologie.md` di `domande-coderunner-sql`. La dashboard mostra al docente database, dati e test, e segnala sezioni non previste, database inesistenti, SELECT senza ORDER BY, costrutti MySQL e CREATE controllate con `.schema`.

## In più, scrivendo le tracce

- Lo script da mettere nel campo `database` del quiz è quello comune del database scelto con `database-didattici`.
- Nello schema della traccia: una tabella per riga, chiave primaria sottolineata (`__IdCorso__`), asterisco sulle chiavi esterne.
- La breve descrizione si ripete in ogni domanda perché con le domande casuali non si sa quale lo studente vede per prima.
- Le eccezioni all'ordine unico le decide l'utente.
- Di norma un solo test visibile: per le SELECT il risultato della query, per le modifiche la SELECT sullo stato finale. Nelle verifiche in più un `=== test HIDE` con `=== extra`.
- Dopo aver scritto le domande, controlla con `verifica_query.py` di `database-didattici` (sulla `specifica-sql.txt` di `da_dashboard.py`, o domanda per domanda) che i dati smascherino gli errori tipici e che non ci siano pari merito; per un confine proprio di una domanda aggiungi in fondo allo script del quiz poche INSERT o UPDATE commentate (`-- righe aggiunte per L5 - B3`).
- Verifica soluzione e codice di partenza con SQLite prima di scriverli.
