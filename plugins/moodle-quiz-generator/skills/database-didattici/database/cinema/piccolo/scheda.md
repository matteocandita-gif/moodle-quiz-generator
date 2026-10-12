# Cinema — taglia piccolo

Un cinema di Bologna con tre sale vende i biglietti ai clienti con la tessera del cinema. Ogni film ha un solo regista; il cliente fa la tessera (DataTessera) e poi compra i biglietti (tabella Biglietti). Il prezzo dipende dall'orario: 16:00 6.50 euro, 18:30 7.50 euro, 21:00 9.00 euro.

Nome del database: `cinema` · seme 5102 · Registi 6 righe, Film 10 righe, Clienti 12 righe, Biglietti 20 righe

## Schema (per le tracce della dashboard)

**Registi** (__IdRegista__, Nome, Cognome, Nazionalita, AnnoNascita)
**Film** (__IdFilm__, Titolo, Genere, Durata, AnnoUscita, IdRegista*)
**Clienti** (__IdCliente__, Nome, Cognome, DataNascita, Citta, Email, DataTessera)
**Biglietti** (__IdBiglietto__, IdFilm*, IdCliente*, DataProiezione, Ora, Sala, Prezzo)

## Schema (HTML per Moodle)

```html
<p><strong>Registi</strong> (<u>IdRegista</u>, Nome, Cognome, Nazionalita, AnnoNascita)</p>
<p><strong>Film</strong> (<u>IdFilm</u>, Titolo, Genere, Durata, AnnoUscita, IdRegista*)</p>
<p><strong>Clienti</strong> (<u>IdCliente</u>, Nome, Cognome, DataNascita, Citta, Email, DataTessera)</p>
<p><strong>Biglietti</strong> (<u>IdBiglietto</u>, IdFilm*, IdCliente*, DataProiezione, Ora, Sala, Prezzo)</p>
```

## Righe pensate per smascherare gli errori

- tre clienti (il quinto e gli ultimi due) non hanno comprato biglietti, e alcuni clienti di Bologna ne hanno più d'uno: una JOIN inutile con Biglietti in una query sui clienti perde i primi e ripete i secondi
- Clienti.DataTessera e Biglietti.DataProiezione sono date diverse: filtrare l'una al posto dell'altra cambia il risultato
- clienti con la tessera fatta esattamente il 2025-01-01 e il 2025-12-31 (e il 2024-12-31, il 2026-01-01): smascherano i confini dell'anno
- due film non hanno venduto biglietti (LEFT JOIN), l'ultimo regista non ha film
- due film si intitolano «Il ritorno» (1998 e uno recente, registi diversi): raggruppare per titolo li fonde
- il secondo e il penultimo regista sono omonimi, con un film ciascuno: raggruppare per nome dà 2 film e supera HAVING >= 2; i loro film hanno 1 e 2 biglietti di clienti di Bologna, insieme 3
- il primo e il terzultimo cliente sono omonimi (Bologna e San Lazzaro di Savena)
- alcuni clienti hanno Email NULL; i prezzi sono 6.50, 7.50 e 9.00 secondo l'orario

## Controlli di coerenza (tutti rispettati)

- un biglietto non precede la tessera del cliente
- un film non si proietta prima dell'anno di uscita
- il prezzo dipende dall'orario
- i registi hanno almeno 25 anni all'uscita del film

## Prime righe

### Registi (6 righe)

| IdRegista | Nome | Cognome | Nazionalita | AnnoNascita |
|---|---|---|---|---|
| 1 | Mario | Rinaldi | Italiana | 1966 |
| 2 | Hannah | Müller | Tedesca | 1954 |
| 3 | Martina | Guerra | Italiana | 1954 |
| 4 | James | Evans | Inglese | 1958 |
| 5 | Hannah | Müller | Tedesca | 1962 |

### Film (10 righe)

| IdFilm | Titolo | Genere | Durata | AnnoUscita | IdRegista |
|---|---|---|---|---|---|
| 1 | Il ritorno | Drammatico | 126 | 2026 | 1 |
| 2 | La casa sul lago | Commedia | 104 | 2026 | 1 |
| 3 | Ultima fermata | Avventura | 100 | 2026 | 1 |
| 4 | Notte di luglio | Fantascienza | 120 | 2025 | 3 |
| 5 | Le stelle di Marte | Thriller | 104 | 2025 | 3 |

### Clienti (12 righe)

| IdCliente | Nome | Cognome | DataNascita | Citta | Email | DataTessera |
|---|---|---|---|---|---|---|
| 1 | Veronica | Venturi | 1962-07-07 | Bologna |  | 2023-03-14 |
| 2 | Francesca | Tinti | 1986-07-15 | Bologna | francesca.tinti20@outlook.it | 2025-01-01 |
| 3 | Veronica | Corazza | 1967-04-01 | Bologna | veronica.corazza41@virgilio.it | 2025-12-31 |
| 4 | Andrea | Bianchini | 1993-02-14 | Bologna |  | 2024-12-31 |
| 5 | Kevin | Piras | 1976-10-14 | Bologna | kevin.piras82@gmail.com | 2026-01-01 |

### Biglietti (20 righe)

| IdBiglietto | IdFilm | IdCliente | DataProiezione | Ora | Sala | Prezzo |
|---|---|---|---|---|---|---|
| 1 | 7 | 1 | 2025-01-17 | 18:30 | Sala 3 | 7.5 |
| 2 | 4 | 1 | 2025-01-18 | 21:00 | Sala 2 | 9 |
| 3 | 5 | 8 | 2025-02-07 | 21:00 | Sala 3 | 9 |
| 4 | 5 | 10 | 2025-02-25 | 16:00 | Sala 3 | 6.5 |
| 5 | 9 | 2 | 2025-03-11 | 16:00 | Sala 3 | 6.5 |
