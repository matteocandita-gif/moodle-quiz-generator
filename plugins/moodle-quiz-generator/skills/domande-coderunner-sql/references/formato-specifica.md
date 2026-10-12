# La specifica, il prototipo e gli script

## Il prototipo sql_salvemini

Tutte le domande nuove usano il prototipo `sql_salvemini`, installato nel Moodle dell'utente (`assets/PROTOTYPE_sql_salvemini.xml`, template in `assets/template-sql_salvemini.py`). A ogni test:

1. copia pulita del database allegato;
2. esegue con il client `sqlite3` di Jobe (SQLite 3.46) le impostazioni `.mode column` e `.headers on`, `PRAGMA foreign_keys = ON` (salvo `{"foreign_keys": false}`), poi il campo Extra, la risposta dello studente (con il `;` finale aggiunto se manca) e il codice del test;
3. stampa i risultati e, in fondo, una riga `ERRORE: messaggio` per ogni errore SQL, senza numeri di riga.

I test di tipo **precheck** eseguono solo la risposta e stampano soltanto gli errori: l'output atteso è vuoto.

Formato dei risultati, verificato su Jobe con `assets/taratura-sql_salvemini.xml` (8 test, tutti passati): una tabella per ogni istruzione che restituisce righe, intestazione e riga di trattini, colonne larghe quanto il valore più lungo, due spazi tra le colonne, tutto allineato a sinistra, NULL come cella vuota, nessuna stampa per i risultati senza righe, nessuna riga vuota tra due risultati. `scripts/emula_sqlite.py` riproduce questo formato.

Le domande vecchie del deposito usano i prototipi `sql` e `sql_foreignkeys`: per convertirle vedi `rigenera_attesi.py` sotto.

## Formato della specifica

Righe `=== ` aprono le sezioni, il resto è contenuto grezzo.

```text
=== category
Lezione 5 - SQL su più tabelle
=== database libreria
CREATE TABLE Editori (...);
CREATE TABLE Libri (...);
INSERT INTO Editori VALUES (...);
INSERT INTO Libri VALUES (...);
=== question
=== name
L5 - B2 - Scrivere: libri ed editori di Milano
=== options
precheck: 1
=== note
Per il docente: non va nell'XML.
=== questiontext
<p>...</p>
=== preload
...codice di partenza (solo per il debugging)...
=== answer
SELECT ...;
=== test
-- il risultato della tua query
=== test HIDE
[[struttura Libri]]
```

| Sezione | Contenuto |
|---|---|
| `category` | categoria delle domande che seguono (`Nome` → `$module$/top/Nome`) |
| `database NOME` | script SQL di creazione e popolamento; più database nello stesso file sono ammessi |
| `question` | apre una domanda |
| `name`, `questiontext`, `answer` | obbligatorie; nel testo valgono i blocchi `[[codice sql]]` |
| `preload` | codice precaricato nella casella di risposta |
| `test` / `test HIDE` | codice del test; `HIDE` lo nasconde. La macro `[[struttura T]]` controlla la struttura della tabella T |
| `extra` | dopo un test: SQL eseguito prima della risposta, in quel test (raro) |
| `expected` | dopo un test: output atteso scritto a mano. Serve solo con `RegexGrader`; negli altri casi lo script lo calcola e avvisa se quello scritto è diverso |
| `generalfeedback`, `note` | facoltative |

## Opzioni

| Opzione | Predefinito | Significato |
|---|---|---|
| `database` | l'unico definito | quale `=== database` usare |
| `database_file` | | un file `.db` esistente al posto di uno definito |
| `dati` | dedotto | `pieno`, `struttura`, `vuoto` (vedi `tipologie.md`) |
| `foreign_keys` | `1` | `0` disattiva le chiavi esterne per questa domanda |
| `precheck` | `0` | `1` aggiunge in testa il test di sola sintassi e attiva il pulsante |
| `allornothing` | `1` | `0` per il punteggio parziale tra più test |
| `defaultgrade`, `penalty` | `1`, `0` | |
| `grader` | del prototipo | `NearEqualityGrader` (ignora maiuscole e spazi) o `RegexGrader` |
| `hidecheck` | `0` | `1` nasconde il pulsante Controlla |
| `answerboxlines` | calcolato | righe della casella |

## Gli script

```bash
python3 scripts/crea_xml.py SPEC.txt USCITA.xml [--cartella-db DIR]
```

Costruisce i database, calcola gli output, incorpora il database, scrive l'XML. Si ferma se: manca una sezione, lo script del database ha errori, la soluzione non passa il proprio controllo di sintassi, un test usa un comando punto non emulato (solo `.schema`, `.mode`, `.headers`, `.width` sono gestiti), un nome è ripetuto. Stampa una **NOTA** se la soluzione produce un errore SQL (giusto solo nelle domande sui vincoli), un **AVVISO** se un test ha output vuoto o se un atteso scritto a mano non coincide, e per il debugging il primo messaggio che vede lo studente. `--cartella-db` salva anche i file `.db`, utili per provarli in phpMyAdmin o DB Browser.

```bash
python3 scripts/rigenera_attesi.py EXPORT.xml USCITA.xml --prefisso "Rigenerate"
```

Converte le domande di un export (prototipi `sql`, `sql_foreignkeys`, template copiati) a `sql_salvemini` e ricalcola gli output: vedi l'intestazione dello script. Riporta le domande da controllare a mano (soluzione mancante, errori SQL nella soluzione, output vuoti, RegexGrader).

Dopo l'import il controllo definitivo è il **bulk tester** di CodeRunner sulla categoria: esegue la soluzione di ogni domanda su Jobe.

## XML con le altre skill

Se le domande SQL fanno parte di una sequenza di `materiali-moodle`, produci qui il loro XML e uniscilo con `unisci_xml.py` di quella skill.
