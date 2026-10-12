# MySQL e SQLite

_Copia del file della skill `domande-coderunner-sql`: il prototipo `php_mysqli_sqlite` usa lo stesso client sqlite3 di Jobe, quindi valgono le stesse differenze. In fondo, le note proprie delle domande PHP._

Gli studenti imparano MySQL (XAMPP, phpMyAdmin); CodeRunner esegue **SQLite 3.46**. Molte differenze non contano, alcune fanno fallire una risposta che in MySQL sarebbe giusta. Verificate eseguendo SQLite.

## Funziona come in MySQL

- `INT AUTO_INCREMENT PRIMARY KEY` (SQLite legge AUTO_INCREMENT come parte del tipo), `VARCHAR(n)`, `CHAR(n)`, `DATE`, `DECIMAL(p,s)`, `INT(5)`.
- Stringhe tra virgolette doppie (`"testo"`) oltre che tra apici.
- `CONCAT('a', 'b')`, `LIMIT n`, `LIMIT inizio, n`.
- `LIKE` ignora maiuscole e minuscole, come in MySQL con le collation normali.
- Chiavi esterne: con il prototipo `sql_salvemini` sono attive, come in MySQL con InnoDB.

## Fallisce o si comporta diversamente

| In MySQL | In SQLite | Che cosa fare |
|---|---|---|
| `id INT PRIMARY KEY AUTO_INCREMENT` | **errore di sintassi** | nel testo delle CREATE: «scrivi AUTO_INCREMENT prima di PRIMARY KEY», oppure non chiederlo |
| `ENUM('a','b')` | errore di sintassi | non chiederlo; usa VARCHAR |
| `NOW()`, `CURDATE()`, `YEAR(data)`, `MONTH(data)`, `DATEDIFF` | funzione inesistente | evita domande sulle funzioni di data; se servono, confronta le date come testo (`data_nascita < '2000-01-01'`) |
| `5/2` = 2.5 | `5/2` = **2** (divisione intera tra interi) | nelle medie e nelle percentuali usa colonne decimali o `AVG`, oppure un N.B.; `AVG` restituisce già un decimale |
| `DECIMAL(6,2)` mostra `9.00` | mostra **`9`**, e `9.50` come **`9.5`** | normale: gli output attesi calcolati dallo script lo riproducono. Se il testo cita i prezzi, scrivili nella forma che vedrà lo studente |
| `ROUND(x, 2)` mostra `10.40` | mostra `10.4` | come sopra |
| `CREATE DATABASE`, `USE` | non esistono | domanda a risposta breve fuori da CodeRunner |
| `SHOW TABLES`, `DESCRIBE Tabella` | non esistono | per mostrare la struttura usa le pagine o il campo di prova con `SELECT * FROM pragma_table_info('Tabella')` |
| `ALTER TABLE ... MODIFY` / `CHANGE` | non esistono | SQLite accetta solo `ADD COLUMN`, `DROP COLUMN`, `RENAME TO` e `RENAME COLUMN`: chiedi solo queste |
| `TRUNCATE TABLE` | non esiste | `DELETE FROM Tabella` |
| `IF(cond, a, b)` | non esiste nella 3.46 | `CASE WHEN … THEN … ELSE … END`, che vale in entrambi |
| confronto stringhe con `=` | distingue le maiuscole (`'calvino' = 'Calvino'` è falso) | MySQL di solito no: scrivi nel testo i valori esatti da cercare |

Quando una consegna porta naturalmente a uno di questi costrutti, o la riformuli o aggiungi un N.B. nel testo. Non lasciare che lo studente scopra la differenza dal messaggio di errore, a meno che non sia proprio l'obiettivo.

## Note per le domande PHP (php_mysqli_sqlite)

- **AUTO_INCREMENT e `mysqli_insert_id`**: nello schema del database scrivi `Id INTEGER PRIMARY KEY AUTOINCREMENT`. La forma `INT AUTO_INCREMENT PRIMARY KEY` crea la tabella ma `Id` non diventa automatico (in SQLite solo una colonna di tipo esattamente `INTEGER PRIMARY KEY` lo è): omettendo `Id` nella INSERT resterebbe vuoto e `mysqli_insert_id` restituirebbe un numero che non c'entra. Per far partire gli Id da un numero preciso, inserisci nello schema una riga con quell'Id: AUTOINCREMENT continua dal più alto.
- **Valori nei risultati**: arrivano allo studente come stringhe, nel formato di SQLite: `12` e `9.5` per un DECIMAL, le date come testo `AAAA-MM-GG`, NULL come `null`.
- **`mysqli_real_escape_string`** raddoppia l'apice (`L''isola`), che vale sia in SQLite sia in MySQL; la barra rovesciata di MySQL in SQLite non funzionerebbe.
- **Confronto tra testi** con `=`: distingue le maiuscole. Nei test usa nei dati del form gli stessi valori del database (le opzioni di un `<select>` sono la scelta più sicura).
