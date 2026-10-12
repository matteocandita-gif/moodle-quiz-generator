# Il modello di un database

Ogni database del catalogo nasce da un **modello**: un file Python (`modelli/<nome>.py`) che descrive tabelle e vincoli e genera i dati con un seme fisso. `scripts/costruisci.py` lo trasforma negli script SQL, nel file `.db` e nella scheda. L'esempio completo è `modelli/biblioteca.py`: copialo e adattalo.

## Parti del modello

| Nome | Contenuto |
|---|---|
| `NOME` | nome del database: minuscolo, senza spazi né accenti (`biblioteca`, `noleggio_bici`); diventa il nome del database in MySQL e dei file |
| `TITOLO`, `CONTESTO` | nome leggibile e due frasi sul contesto e sulle regole del mondo (servono a chi scrive le tracce) |
| `SEME` | intero; stesso seme, stessi dati a ogni rigenerazione. Ogni modello ha il suo seme (i modelli paralleli di una verifica semi vicini ma distinti, per esempio 5101, 5102, 5103) |
| `TABELLE` | elenco in ordine di creazione (prima i padri): `nome`, `colonne` come `(nome, tipo, vincoli)`, facoltativi `chiave` (composta), `esterne` `(colonna, tabella, colonna)`, `unici` |
| `TAGLIE` | `piccolo`, `medio`, `grande` con i parametri che `genera` legge (di solito il numero di righe per tabella) |
| `genera(g, t)` | restituisce `{tabella: [righe]}`, ogni riga una tupla nell'ordine delle colonne; `g` è il Generatore, `t` i parametri della taglia |
| `CONTROLLI` | `(descrizione, SELECT che trova le righe che violano la regola)`: devono dare 0 righe, altrimenti la costruzione si ferma |
| `TRAPPOLE` | frasi che dicono quali righe smascherano quali errori: finiscono nella scheda e nel catalogo |

## Il Generatore (`g`)

- scelte: `g.scegli(lista)`, `g.campione(lista, k)`, `g.intero(a, b)`, `g.prob(p)`, `g.mescola(lista)`, `g.unico(chiave, funzione)` (valori mai ripetuti: codici, targhe, titoli);
- persone: `g.persona()` → `{sesso, nome, cognome}` italiani; `g.persona_estera("Francese")` nome e cognome coerenti con la nazionalità; `g.email(nome, cognome, dominio)` unica; `g.telefono()`;
- luoghi: `g.comune(solo_provincia="BO", peso_bologna=0.5)` → `(comune, provincia, regione, CAP)`; `g.via()`;
- date e numeri: `g.data_tra("2025-09-15", "2026-06-10")`, `g.dopo(data, min_giorni, max_giorni)`, `g.nascita(eta_min, eta_max)`, `g.importo(5, 40, passo=0.5)` (Decimal);
- liste in `scripts/dati_it.py`: nomi, cognomi (anche di famiglie di origine straniera), comuni con provincia e CAP, vie, materie e indirizzi scolastici, prodotti per categoria, generi di libri, editori, reparti, ruoli, metodi di pagamento, stati degli ordini, sport, colori, marche e modelli di auto. Se manca una lista, aggiungila lì (vale per tutti i modelli) o nel modello (vale solo per quello).

## Tipi e vincoli (validi in MySQL e in SQLite)

- `INT`, `TINYINT`, `DECIMAL(p,s)`, `VARCHAR(n)`, `CHAR(n)`, `DATE`, `DATETIME`, `TEXT`; vincoli `PRIMARY KEY`, `NOT NULL`, `UNIQUE`, `DEFAULT`.
- Contatori: `INT AUTO_INCREMENT PRIMARY KEY` in quest'ordine (l'ordine inverso è un errore in SQLite), ma nei dati si scrivono comunque gli id espliciti, così gli esercizi possono citarli.
- Niente `ENUM`, niente `BOOLEAN` come tipo (usa `TINYINT` con 0/1), niente funzioni di data nei `DEFAULT`.
- Nomi senza spazi né accenti, non parole riservate di MySQL (`Ordine` va bene, `Order`, `Key`, `Group`, `Rank` no). Stile del libro: tabelle al plurale con l'iniziale maiuscola (`Prestiti`), colonne in CamelCase (`DataPrestito`), chiavi `IdTabella` o il codice naturale (`ISBN`, `Matricola`, `Targa`).

## Generare senza cicli infiniti

Quando un valore deve essere unico (combinazioni nome e livello, titoli, codici) e la taglia grande chiede più righe delle combinazioni disponibili, un ciclo «riprova finché non è nuovo» non finisce mai. Ruota le liste (nome `k % len(lista)`, aggiungendo un numero dopo il primo giro) oppure usa `g.unico` con una funzione che ha abbastanza valori, e prova sempre tutte e tre le taglie. Le righe che fanno da trappola si fissano con assegnazioni esplicite (un elenco dei padri a cui vanno le prime righe, valori scritti nelle righe scelte), non con il caso: così restano uguali in tutte le taglie e non spariscono cambiando il seme.

`costruisci.py` controlla lunghezze di VARCHAR/CHAR, precisione di DECIMAL, NOT NULL, chiavi e chiavi esterne: sono gli errori per cui MySQL in modo stretto rifiuterebbe l'import in phpMyAdmin anche se SQLite lo accetta.
