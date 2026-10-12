# Palestra — taglia medio

Una palestra della provincia di Bologna organizza corsi tenuti dai suoi istruttori. Ogni corso ha un solo istruttore; un socio si iscrive alla palestra (DataIscrizione) e poi a uno o più corsi (tabella Iscrizioni). Un'iscrizione a un corso è attiva finché DataFine è vuota.

Nome del database: `palestra` · seme 5101 · Istruttori 9 righe, Corsi 18 righe, Soci 30 righe, Iscrizioni 50 righe

## Schema (per le tracce della dashboard)

**Istruttori** (__IdIstruttore__, Nome, Cognome, Qualifica, DataAssunzione)
**Corsi** (__IdCorso__, Nome, Livello, Giorno, Orario, CostoMensile, PostiMax, IdIstruttore*)
**Soci** (__IdSocio__, Nome, Cognome, DataNascita, Citta, Telefono, DataIscrizione)
**Iscrizioni** (__IdIscrizione__, IdSocio*, IdCorso*, DataInizio, DataFine)

## Schema (HTML per Moodle)

```html
<p><strong>Istruttori</strong> (<u>IdIstruttore</u>, Nome, Cognome, Qualifica, DataAssunzione)</p>
<p><strong>Corsi</strong> (<u>IdCorso</u>, Nome, Livello, Giorno, Orario, CostoMensile, PostiMax, IdIstruttore*)</p>
<p><strong>Soci</strong> (<u>IdSocio</u>, Nome, Cognome, DataNascita, Citta, Telefono, DataIscrizione)</p>
<p><strong>Iscrizioni</strong> (<u>IdIscrizione</u>, IdSocio*, IdCorso*, DataInizio, DataFine)</p>
```

## Righe pensate per smascherare gli errori

- tre soci (il quinto e gli ultimi due) non sono iscritti a nessun corso, e alcuni soci di Bologna hanno più iscrizioni: una JOIN inutile con Iscrizioni in una query sui soci perde i primi e ripete i secondi
- Soci.DataIscrizione (iscrizione alla palestra) e Iscrizioni.DataInizio (iscrizione al corso) sono date diverse: filtrare l'una al posto dell'altra cambia il risultato
- soci iscritti alla palestra esattamente il 2025-01-01 e il 2025-12-31 (e il 2024-12-31, il 2026-01-01): smascherano i confini dell'anno
- due corsi non hanno iscritti (LEFT JOIN), l'ultimo istruttore, appena assunto, non ha corsi
- due corsi «Yoga» (Base e Avanzato) e due «Pilates»: raggruppare per nome del corso li fonde
- il secondo e il penultimo istruttore sono omonimi, con un corso ciascuno: raggruppare per nome dà 2 corsi e supera HAVING >= 2; i loro corsi hanno 1 e 2 iscrizioni attive di soci di Bologna, insieme 3
- il primo e il terzultimo socio sono omonimi (Bologna e Casalecchio di Reno)
- le iscrizioni attive hanno DataFine NULL: «= NULL» non trova niente, COUNT(DataFine) le salta
- alcuni soci hanno Telefono NULL; un corso costa esattamente 50.00

## Controlli di coerenza (tutti rispettati)

- un'iscrizione a un corso non precede l'iscrizione alla palestra
- la fine di un'iscrizione non precede l'inizio
- nessun socio iscritto due volte allo stesso corso
- le iscrizioni attive di un corso non superano i posti
- i soci hanno almeno 16 anni all'iscrizione

## Prime righe

### Istruttori (9 righe)

| IdIstruttore | Nome | Cognome | Qualifica | DataAssunzione |
|---|---|---|---|---|
| 1 | Giulia | De Santis | Laurea in Scienze motorie | 2021-07-25 |
| 2 | Erica | Costantini | Diploma ISEF | 2022-11-10 |
| 3 | Tommaso | Villa | Istruttore federale | 2022-05-16 |
| 4 | Giulia | Grasso | Laurea in Scienze motorie | 2014-12-17 |
| 5 | Giada | Hu | Personal trainer certificato | 2017-06-05 |

### Corsi (18 righe)

| IdCorso | Nome | Livello | Giorno | Orario | CostoMensile | PostiMax | IdIstruttore |
|---|---|---|---|---|---|---|---|
| 1 | Yoga | Base | Mercoledì | 17:30 | 40 | 20 | 1 |
| 2 | Yoga | Avanzato | Sabato | 20:30 | 30 | 15 | 1 |
| 3 | Pilates | Base | Giovedì | 18:30 | 50 | 20 | 1 |
| 4 | Kickboxing | Base | Giovedì | 19:30 | 42.5 | 10 | 3 |
| 5 | Ginnastica posturale | Base | Martedì | 19:30 | 50 | 15 | 3 |

### Soci (30 righe)

| IdSocio | Nome | Cognome | DataNascita | Citta | Telefono | DataIscrizione |
|---|---|---|---|---|---|---|
| 1 | Chiara | Vitali | 1998-08-08 | Bologna | 396 0200040 | 2026-06-25 |
| 2 | Chiara | Orlando | 1971-09-23 | Bologna | 331 7317074 | 2025-01-01 |
| 3 | Maria | Monari | 1994-09-20 | Bologna | 357 8092488 | 2025-12-31 |
| 4 | Noemi | Galli | 1973-08-11 | Bologna | 345 1464208 | 2024-12-31 |
| 5 | Ivan | Biagi | 2003-11-15 | Bologna | 382 8817525 | 2026-01-01 |

### Iscrizioni (50 righe)

| IdIscrizione | IdSocio | IdCorso | DataInizio | DataFine |
|---|---|---|---|---|
| 1 | 8 | 7 | 2023-05-07 |  |
| 2 | 21 | 8 | 2023-10-06 |  |
| 3 | 21 | 13 | 2023-11-12 |  |
| 4 | 20 | 11 | 2023-11-17 |  |
| 5 | 7 | 3 | 2023-11-18 |  |
