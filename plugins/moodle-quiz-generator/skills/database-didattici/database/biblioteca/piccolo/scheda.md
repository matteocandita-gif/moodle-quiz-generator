# Biblioteca scolastica — taglia piccolo

La biblioteca dell'istituto presta libri agli studenti. Ogni libro ha un solo autore; un prestito è aperto finché la data di restituzione è vuota.

Nome del database: `biblioteca` · seme 2026 · Autori 6 righe, Libri 10 righe, Studenti 8 righe, Prestiti 16 righe

## Schema (per le tracce della dashboard)

**Autori** (__IdAutore__, Nome, Cognome, Nazionalita, AnnoNascita)
**Libri** (__ISBN__, Titolo, Genere, AnnoPubblicazione, Pagine, Copie, IdAutore*)
**Studenti** (__Matricola__, Nome, Cognome, Classe, Email)
**Prestiti** (__IdPrestito__, ISBN*, Matricola*, DataPrestito, DataRestituzione)

## Schema (HTML per Moodle)

```html
<p><strong>Autori</strong> (<u>IdAutore</u>, Nome, Cognome, Nazionalita, AnnoNascita)</p>
<p><strong>Libri</strong> (<u>ISBN</u>, Titolo, Genere, AnnoPubblicazione, Pagine, Copie, IdAutore*)</p>
<p><strong>Studenti</strong> (<u>Matricola</u>, Nome, Cognome, Classe, Email)</p>
<p><strong>Prestiti</strong> (<u>IdPrestito</u>, ISBN*, Matricola*, DataPrestito, DataRestituzione)</p>
```

## Righe pensate per smascherare gli errori

- l'ultimo autore non ha libri: una JOIN interna lo perde, una LEFT JOIN lo mostra con NULL
- l'ultimo libro non è mai stato prestato e il penultimo studente non ha prestiti
- il primo e l'ultimo studente hanno lo stesso nome e cognome in classi diverse, e così il secondo e il terzultimo autore: raggruppare per nome invece che per chiave li fonde
- i prestiti aperti hanno DataRestituzione NULL: «= NULL» non trova niente, COUNT(DataRestituzione) li salta
- un prestito cade esattamente il 2026-01-01 (ancora aperto) e uno il 2026-01-31, un libro è del 2000: smascherano > al posto di >= sui confini dei mesi e degli anni
- un libro ha Pagine NULL: SUM e AVG lo ignorano, COUNT(Pagine) lo salta
- il genere Poesia ha esattamente 2 libri: smaschera HAVING COUNT(*) > 2 al posto di >= 2
- «Amore di mezzanotte» e «Un amore lontano»: LIKE 'amore%' trova solo il primo, LIKE '%amore%' entrambi

## Controlli di coerenza (tutti rispettati)

- la restituzione non precede il prestito
- i prestiti aperti di un libro non superano le copie
- gli autori sono nati prima di pubblicare

## Prime righe

### Autori (6 righe)

| IdAutore | Nome | Cognome | Nazionalita | AnnoNascita |
|---|---|---|---|---|
| 1 | Marta | Monari | Italiana | 1933 |
| 2 | Bianca | Corazza | Italiana | 1982 |
| 3 | Florencia | Gómez | Argentina | 1930 |
| 4 | Bianca | Corazza | Italiana | 1982 |
| 5 | Elena | Martínez | Spagnola | 1964 |

### Libri (10 righe)

| ISBN | Titolo | Genere | AnnoPubblicazione | Pagine | Copie | IdAutore |
|---|---|---|---|---|---|---|
| 9781327139357 | Racconti della città | Fantasy | 1989 | 467 | 2 | 3 |
| 9786676307749 | La lettera senza nome | Storico | 2000 | 209 | 3 | 1 |
| 9788698924284 | Il ritorno | Giallo | 2018 |  | 1 | 4 |
| 9783805002643 | Amore di mezzanotte | Storico | 2002 | 557 | 3 | 4 |
| 9789911183700 | Un amore lontano | Storico | 2013 | 603 | 2 | 5 |

### Studenti (8 righe)

| Matricola | Nome | Cognome | Classe | Email |
|---|---|---|---|---|
| 1001 | Giulio | Silvestri | 3A | giulio.silvestri@studenti.istituto.it |
| 1002 | Mario | Costantini | 3B | mario.costantini@studenti.istituto.it |
| 1003 | Paolo | Govoni | 5B | paolo.govoni83@studenti.istituto.it |
| 1004 | Leonardo | Pancaldi | 5A | leonardo.pancaldi@studenti.istituto.it |
| 1005 | Mattia | Fontana | 4B | mattia.fontana4@studenti.istituto.it |

### Prestiti (16 righe)

| IdPrestito | ISBN | Matricola | DataPrestito | DataRestituzione |
|---|---|---|---|---|
| 1 | 9783805002643 | 1002 | 2025-09-17 |  |
| 2 | 9784717480361 | 1006 | 2025-09-25 | 2025-10-31 |
| 3 | 9787080460787 | 1004 | 2025-10-02 | 2025-10-16 |
| 4 | 9781327139357 | 1006 | 2025-10-09 | 2025-10-24 |
| 5 | 9787080460787 | 1002 | 2025-11-10 | 2025-11-30 |
