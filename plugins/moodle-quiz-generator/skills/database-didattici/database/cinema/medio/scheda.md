# Cinema — taglia medio

Un cinema di Bologna con tre sale vende i biglietti ai clienti con la tessera del cinema. Ogni film ha un solo regista; il cliente fa la tessera (DataTessera) e poi compra i biglietti (tabella Biglietti). Il prezzo dipende dall'orario: 16:00 6.50 euro, 18:30 7.50 euro, 21:00 9.00 euro.

Nome del database: `cinema` · seme 5102 · Registi 9 righe, Film 18 righe, Clienti 30 righe, Biglietti 50 righe

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

### Registi (9 righe)

| IdRegista | Nome | Cognome | Nazionalita | AnnoNascita |
|---|---|---|---|---|
| 1 | Mario | Rinaldi | Italiana | 1966 |
| 2 | Hannah | Müller | Tedesca | 1954 |
| 3 | Martina | Guerra | Italiana | 1954 |
| 4 | James | Evans | Inglese | 1958 |
| 5 | Isabel | Fernández | Spagnola | 1962 |

### Film (18 righe)

| IdFilm | Titolo | Genere | Durata | AnnoUscita | IdRegista |
|---|---|---|---|---|---|
| 1 | Il ritorno | Drammatico | 104 | 2026 | 1 |
| 2 | La casa sul lago | Commedia | 126 | 2025 | 1 |
| 3 | Ultima fermata | Avventura | 126 | 2025 | 1 |
| 4 | Notte di luglio | Fantascienza | 126 | 2025 | 3 |
| 5 | Le stelle di Marte | Thriller | 126 | 2025 | 3 |

### Clienti (30 righe)

| IdCliente | Nome | Cognome | DataNascita | Citta | Email | DataTessera |
|---|---|---|---|---|---|---|
| 1 | Fabio | Montanari | 1971-11-29 | Bologna |  | 2025-01-20 |
| 2 | Ivan | Caruso | 1957-01-10 | Bologna |  | 2025-01-01 |
| 3 | Omar | Martini | 1969-07-27 | Bologna |  | 2025-12-31 |
| 4 | Simone | Grassi | 1994-05-12 | Bologna | simone.grassi@libero.it | 2024-12-31 |
| 5 | Ambra | Battaglia | 1953-07-01 | Bologna | ambra.battaglia@gmail.com | 2026-01-01 |

### Biglietti (50 righe)

| IdBiglietto | IdFilm | IdCliente | DataProiezione | Ora | Sala | Prezzo |
|---|---|---|---|---|---|---|
| 1 | 3 | 17 | 2025-01-20 | 21:00 | Sala 3 | 9 |
| 2 | 4 | 1 | 2025-01-23 | 16:00 | Sala 1 | 6.5 |
| 3 | 4 | 1 | 2025-01-23 | 18:30 | Sala 2 | 7.5 |
| 4 | 2 | 16 | 2025-01-27 | 18:30 | Sala 1 | 7.5 |
| 5 | 4 | 1 | 2025-01-29 | 16:00 | Sala 1 | 6.5 |
