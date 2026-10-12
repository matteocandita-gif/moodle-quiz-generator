# Biblioteca scolastica — taglia medio

La biblioteca dell'istituto presta libri agli studenti. Ogni libro ha un solo autore; un prestito è aperto finché la data di restituzione è vuota.

Nome del database: `biblioteca` · seme 2026 · Autori 15 righe, Libri 40 righe, Studenti 30 righe, Prestiti 50 righe

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

### Autori (15 righe)

| IdAutore | Nome | Cognome | Nazionalita | AnnoNascita |
|---|---|---|---|---|
| 1 | Marta | Monari | Italiana | 1933 |
| 2 | Bianca | Corazza | Italiana | 1982 |
| 3 | Florencia | Gómez | Argentina | 1930 |
| 4 | Rachele | Caruso | Italiana | 1982 |
| 5 | Elena | Martínez | Spagnola | 1964 |

### Libri (40 righe)

| ISBN | Titolo | Genere | AnnoPubblicazione | Pagine | Copie | IdAutore |
|---|---|---|---|---|---|---|
| 9788421018738 | Il silenzio perduto | Fantasy | 1998 | 591 | 1 | 3 |
| 9787843355507 | Il silenzio | Saggio | 2000 | 534 | 3 | 1 |
| 9784717480361 | Racconti della notte | Saggio | 2015 |  | 2 | 6 |
| 9784037861054 | Amore di mezzanotte | Storico | 2004 | 362 | 2 | 14 |
| 9784923573028 | Un amore lontano | Romanzo | 2017 | 104 | 1 | 14 |

### Studenti (30 righe)

| Matricola | Nome | Cognome | Classe | Email |
|---|---|---|---|---|
| 1001 | Alberto | Fabbri | 4A | alberto.fabbri@studenti.istituto.it |
| 1002 | Gabriele | Ricci | 3A | gabriele.ricci@studenti.istituto.it |
| 1003 | Stefano | Giordano | 4A | stefano.giordano@studenti.istituto.it |
| 1004 | Eleonora | Biagi | 3B | eleonora.biagi@studenti.istituto.it |
| 1005 | Fabio | Galli | 4A | fabio.galli35@studenti.istituto.it |

### Prestiti (50 righe)

| IdPrestito | ISBN | Matricola | DataPrestito | DataRestituzione |
|---|---|---|---|---|
| 1 | 9784717480361 | 1016 | 2025-09-18 | 2025-10-13 |
| 2 | 9785965912761 | 1016 | 2025-09-23 | 2025-10-09 |
| 3 | 9786470912414 | 1005 | 2025-09-28 | 2025-10-06 |
| 4 | 9788668757732 | 1002 | 2025-10-02 | 2025-10-24 |
| 5 | 9785965912761 | 1024 | 2025-10-02 | 2025-10-13 |
