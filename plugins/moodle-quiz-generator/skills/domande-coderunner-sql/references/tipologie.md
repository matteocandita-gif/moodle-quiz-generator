# Tipologie di domanda SQL

Ricavate dal deposito delle quarte dell'utente (388 domande). Per ognuna: che cosa fa lo studente, quale database serve, come si costruisce il test. Gli output attesi li calcola sempre lo script.

## Il database

Ogni domanda ha **un solo** file `.db` allegato; a ogni test il prototipo ne usa una copia pulita. Lo script lo costruisce dalla sezione `=== database NOME` (CREATE e INSERT come in phpMyAdmin) in tre versioni:

| `dati:` | Contenuto | Per |
|---|---|---|
| `pieno` | tabelle e righe | SELECT, UPDATE, DELETE, vincoli |
| `struttura` | tabelle senza righe | INSERT in una tabella senza chiavi esterne |
| `vuoto` | nessuna tabella | CREATE da zero |

Se l'opzione manca, lo script deduce: CREATE TABLE nella soluzione → `vuoto`; solo INSERT → `struttura`; altrimenti `pieno`. Per una **INSERT in una tabella figlia** (con chiave esterna) usa `dati: pieno`, altrimenti la riga padre non esiste e l'inserimento fallisce; il test allora filtra sulla riga inserita. Per una **CREATE di una tabella che punta a tabelle esistenti** usa `dati: pieno`.

Un database esistente dell'utente si allega con `database_file: percorso.db`.

## Scrivere una query

| Tipologia | Test | Note |
|---|---|---|
| SELECT | `-- il risultato della tua query` | il test non aggiunge codice: si confronta il risultato della risposta. Chiedi sempre un `ORDER BY`, o il confronto dipende dall'ordine casuale delle righe |
| INSERT | `SELECT * FROM Tabella;` (o filtrata sulla chiave inserita) | controlla lo stato finale |
| UPDATE | `SELECT` delle colonne toccate, su tutte le righe | così si vede anche se l'UPDATE ha modificato righe che non doveva (WHERE dimenticata) |
| DELETE | `SELECT` sulla tabella intera, o un `COUNT(*)` | idem |
| CREATE | `[[struttura Tabella]]` | la macro diventa due query su `pragma_table_info` e `pragma_foreign_key_list`: nomi, tipi, NOT NULL, chiave primaria, chiavi esterne. Passa anche con spazi o a capo diversi. Indica nel testo tipi e vincoli esatti |
| In due passi | `SELECT` sullo stato finale | lo studente scrive prima la SELECT che trova l'id, poi l'UPDATE o DELETE che lo usa; l'output contiene il risultato della prima e lo stato finale |
| Dati a scelta | `SELECT COUNT(*) ...` con JOIN | quando la consegna lascia scegliere i valori: si controlla solo ciò che è richiesto (es. due dipendenti collegati all'azienda giusta) |

**Mai** controllare una CREATE con `.schema`: confronta il testo scritto dallo studente, e uno spazio diverso fa fallire una risposta giusta.

## Debugging

La risposta parte con codice sbagliato (`=== preload`) e lo studente lo corregge. Errori legati ai concetti della lezione:

- nome di tabella o di colonna sbagliato (messaggio «no such table», «no such column»);
- INSERT in ordine sbagliato rispetto alla chiave esterna (con `foreign_keys` attive: «FOREIGN KEY constraint failed»);
- JOIN mancante o sui campi sbagliati (nessun messaggio: risultato sbagliato);
- `=` al posto di `LIKE`, `>` al posto di `>=`, WHERE dimenticata (risultato sbagliato).

Prima i debugging **con messaggi**, poi quelli **silenziosi**; nel testo indica quanti errori ci sono finché il sostegno lo prevede. Lo script mostra che cosa vede per primo lo studente eseguendo il codice di partenza: controlla che sia il primo errore che vuoi far trovare.

## Vincoli di integrità

La risposta attesa è un errore del DBMS: lo studente cancella o modifica un record padre e osserva che cosa succede.

- Il prototipo stampa l'errore in fondo all'output come `ERRORE: FOREIGN KEY constraint failed`.
- Aggiungi al test una SELECT (un `COUNT(*)`) per mostrare che i dati non sono cambiati.
- Per ON DELETE CASCADE o SET NULL, il test è la SELECT sulla tabella figlia dopo la cancellazione.

## Campo di prova

Una domanda che accetta qualsiasi risposta, per esplorare il database durante una verifica: `grader: RegexGrader`, un test con `=== expected` uguale a `.*`, punteggio basso (`defaultgrade: 0.5`) o zero.

## Verifiche

- **Varianti** per l'estrazione casuale: stesse domande con dati o condizioni diverse, nomi `… 1`, `… 2`, `… 3`, nella stessa categoria.
- **Precheck**: con `precheck: 1` lo script aggiunge il test di sola sintassi; i test che valutano vanno nascosti (`=== test HIDE`), così lo studente non vede il risultato atteso.
- `hidecheck: 1` nasconde il pulsante Controlla, se l'utente vuole solo il controllo di sintassi durante la prova.

## Testo della domanda

- Lo **schema** delle tabelle coinvolte, chiave primaria sottolineata e chiavi esterne con l'asterisco: `Libri (<u>ISBN</u>, Titolo, Autore, Prezzo, IdEditore*)`.
- Per le SELECT di tracciamento o se servono i valori, una tabella HTML con alcune righe (stile in `stile-html.md`).
- Consegna con le parole chiave in grassetto: che colonne, quale condizione, quale ordine.
- Se la risposta potrebbe usare un costrutto che SQLite non accetta, un N.B. (vedi `compatibilita.md`).
