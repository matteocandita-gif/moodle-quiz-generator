# Messaggi di errore realistici

Gli studenti lavorano con XAMPP, cioè con **MariaDB**: i messaggi simulati devono essere quelli che vedrebbero lì. Usa solo messaggi di cui sei sicuro; se un caso non è in questo elenco e non conosci il testo esatto, scegli un errore diverso piuttosto che inventarne uno.

I messaggi di connessione (2002, 1045, 1049) e il 1046 li genera il mock da solo: non vanno messi nelle chiavi.

## Errori sui nomi (1146, 1054)

| Errore nel codice | errno | Messaggio |
|---|---|---|
| tabella inesistente | 1146 | `Table 'dblibreria.Libro' doesn't exist` (database e tabella come scritti nella query) |
| colonna inesistente nella SELECT o nell'elenco colonne della INSERT | 1054 | `Unknown column 'Prezo' in 'field list'` |
| colonna inesistente nel WHERE | 1054 | `Unknown column 'Autor' in 'where clause'` |
| colonna inesistente nell'ORDER BY | 1054 | `Unknown column 'Data' in 'order clause'` |
| testo di **una sola parola** senza apici nel WHERE | 1054 | `Unknown column 'Calvino' in 'where clause'` (il DBMS lo legge come nome di colonna) |
| testo di una sola parola senza apici nei VALUES di una INSERT | 1054 | `Unknown column 'Siddharta' in 'field list'` |

Chiavi tipiche (sulla query normalizzata): `'/from libro\b/'`, `'/autore=calvino /'` (senza apici: con gli apici la query contiene `autore='calvino'` e la regex non corrisponde), `'/autori,/'`.

## Errori di sintassi (1064)

Formato:

```
You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near 'TESTO' at line N
```

- `TESTO` è la parte della query **a partire dal punto in cui il parser si blocca** fino alla fine, con maiuscole e spazi originali (i valori del test sostituiti).
- `N` è la riga della stringa della query in cui cade quel punto: se la query nel codice va a capo prima di `VALUES`, un errore nei valori è `at line 2`.
- Siccome il testo dipende dai dati, il messaggio va scritto **per ogni test**.

Casi tipici:

| Errore nel codice | Query risultante (esempio) | near |
|---|---|---|
| valore vuoto prima di `AND` (variabile non letta) | `... WHERE Autore =  AND Prezzo <= 10` | `'AND Prezzo <= 10' at line 1` |
| testo di **più parole** senza apici nei VALUES | `VALUES ('9788806', La Storia, 'Morante', 14)` | `'Storia', 'Morante', 14)' at line 2` |
| apostrofo dentro un testo | `VALUES ('9788809', 'L'isola di Arturo', 'Morante', 13)` | `'isola di Arturo', 'Morante', 13)' at line 2` |
| valore numerico vuoto in fondo ai VALUES | `VALUES ('9788806', 'La Storia', 'Morante', )` | `')' at line 2` |

Con un testo di più parole senza apici nel WHERE (`WHERE Autore = Tomasi di Lampedusa`) il parser si blocca sulla seconda parola: near `'di Lampedusa ...'`.

**Ordine**: MariaDB segnala gli errori di sintassi prima di quelli sui nomi. Se la stessa query ha entrambi i difetti, metti la chiave dell'errore di sintassi prima.

Chiavi tipiche: `'/autore=and /'` (valore vuoto), `'/,la storia,/'` (testo di più parole senza apici: con gli apici diventa `,'la storia',` e la regex non corrisponde).

## Errori di inserimento

| Situazione | errno | Messaggio |
|---|---|---|
| chiave primaria già presente | 1062 | `Duplicate entry '9788804' for key 'PRIMARY'` |
| numero di colonne diverso dal numero di valori | 1136 | `Column count doesn't match value count at row 1` |
| `NULL` esplicito in una colonna NOT NULL | 1048 | `Column 'Email' cannot be null` |
| colonna NOT NULL senza default omessa dall'elenco | 1364 | `Field 'Email' doesn't have a default value` |

Caso classico con AUTO_INCREMENT: lo studente scrive `Id` nell'elenco delle colonne ma non mette il valore corrispondente → 1136.

## Risultati vuoti invece di errori

Non tutti gli sbagli danno errore: una condizione con un valore vuoto ma tra apici (`WHERE Autore = ''`) è valida e restituisce **zero righe**. Mappala su `[]`, così la pagina mostra il suo messaggio «Nessun … trovato»: è un indizio realistico che lo studente deve imparare a leggere.

## Errori di PHP (non del DBMS)

| Errore nel codice | Che cosa compare |
|---|---|
| `mysqli_fetch_array($query)` invece di `$risultato` | `Fatal error: Uncaught TypeError: mysqli_fetch_array(): Argument #1 ($result) must be of type mysqli_result, string given` |
| connessione fallita senza `or die`, poi `mysqli_query($connessione, ...)` | `Fatal error: Uncaught TypeError: mysqli_query(): Argument #1 ($mysql) must be of type mysqli, bool given` |
| chiave inesistente in `$_GET`, `$_POST` o `$riga` | `Warning: Undefined array key "Stato"` e valore `null` |
| query dopo `mysqli_close` | `Fatal error: Uncaught Error: mysqli object is already closed` |

Dove compaiono warning ed errori fatali (nell'output o come errore di esecuzione di CodeRunner) dipende dalla configurazione di Jobe: non metterli mai nell'output atteso. Per un warning, l'errore deve avere anche un effetto osservabile nell'output (per esempio una ricerca che non trova nulla) e va segnalato nelle note per il docente.
