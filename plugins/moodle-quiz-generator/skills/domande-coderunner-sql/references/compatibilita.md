# MySQL e SQLite

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
