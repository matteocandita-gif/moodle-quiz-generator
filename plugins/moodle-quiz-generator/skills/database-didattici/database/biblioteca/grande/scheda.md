# Biblioteca scolastica — taglia grande

La biblioteca dell'istituto presta libri agli studenti. Ogni libro ha un solo autore; un prestito è aperto finché la data di restituzione è vuota.

Nome del database: `biblioteca` · seme 2026 · Autori 40 righe, Libri 120 righe, Studenti 100 righe, Prestiti 300 righe

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

### Autori (40 righe)

| IdAutore | Nome | Cognome | Nazionalita | AnnoNascita |
|---|---|---|---|---|
| 1 | Marta | Monari | Italiana | 1933 |
| 2 | Bianca | Corazza | Italiana | 1982 |
| 3 | Florencia | Gómez | Argentina | 1930 |
| 4 | Rachele | Caruso | Italiana | 1982 |
| 5 | Elena | Martínez | Spagnola | 1964 |

### Libri (120 righe)

| ISBN | Titolo | Genere | AnnoPubblicazione | Pagine | Copie | IdAutore |
|---|---|---|---|---|---|---|
| 9780920544584 | Il vento | Romanzo | 1967 | 95 | 2 | 29 |
| 9784411725007 | Racconti della stazione | Fantasy | 2000 | 250 | 3 | 1 |
| 9783139494357 | Il confine e il giardino | Saggio | 2020 |  | 2 | 18 |
| 9781132637511 | Amore di mezzanotte | Giallo | 1968 | 536 | 1 | 36 |
| 9782706201084 | Un amore lontano | Fantasy | 2021 | 608 | 2 | 12 |

### Studenti (100 righe)

| Matricola | Nome | Cognome | Classe | Email |
|---|---|---|---|---|
| 1001 | Silvia | Donati | 5A | silvia.donati35@studenti.istituto.it |
| 1002 | Bruno | Costantini | 5B | bruno.costantini@studenti.istituto.it |
| 1003 | Ioana | Govoni | 5B | ioana.govoni10@studenti.istituto.it |
| 1004 | Arianna | Vitali | 4A | arianna.vitali@studenti.istituto.it |
| 1005 | Manuel | Kaur | 5B | manuel.kaur@studenti.istituto.it |

### Prestiti (300 righe)

| IdPrestito | ISBN | Matricola | DataPrestito | DataRestituzione |
|---|---|---|---|---|
| 1 | 9781894885055 | 1076 | 2025-09-16 | 2025-09-26 |
| 2 | 9782556547010 | 1014 | 2025-09-16 | 2025-09-23 |
| 3 | 9784681745585 | 1066 | 2025-09-18 | 2025-10-24 |
| 4 | 9787072612309 | 1093 | 2025-09-20 | 2025-10-10 |
| 5 | 9781599229892 | 1082 | 2025-09-20 | 2025-09-30 |
