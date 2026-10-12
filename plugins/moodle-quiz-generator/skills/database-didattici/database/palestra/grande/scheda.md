# Palestra — taglia grande

Una palestra della provincia di Bologna organizza corsi tenuti dai suoi istruttori. Ogni corso ha un solo istruttore; un socio si iscrive alla palestra (DataIscrizione) e poi a uno o più corsi (tabella Iscrizioni). Un'iscrizione a un corso è attiva finché DataFine è vuota.

Nome del database: `palestra` · seme 5101 · Istruttori 15 righe, Corsi 30 righe, Soci 100 righe, Iscrizioni 220 righe

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

### Istruttori (15 righe)

| IdIstruttore | Nome | Cognome | Qualifica | DataAssunzione |
|---|---|---|---|---|
| 1 | Giulia | De Santis | Laurea in Scienze motorie | 2021-07-25 |
| 2 | Erica | Costantini | Diploma ISEF | 2022-11-10 |
| 3 | Tommaso | Villa | Istruttore federale | 2022-05-16 |
| 4 | Giulia | Grasso | Laurea in Scienze motorie | 2014-12-17 |
| 5 | Giada | Hu | Personal trainer certificato | 2017-06-05 |

### Corsi (30 righe)

| IdCorso | Nome | Livello | Giorno | Orario | CostoMensile | PostiMax | IdIstruttore |
|---|---|---|---|---|---|---|---|
| 1 | Yoga | Base | Venerdì | 12:30 | 40 | 20 | 1 |
| 2 | Yoga | Avanzato | Sabato | 12:30 | 30 | 15 | 1 |
| 3 | Pilates | Base | Venerdì | 20:30 | 50 | 12 | 1 |
| 4 | Kickboxing | Intermedio | Sabato | 20:30 | 42.5 | 12 | 3 |
| 5 | Ginnastica posturale | Avanzato | Martedì | 20:30 | 50 | 20 | 3 |

### Soci (100 righe)

| IdSocio | Nome | Cognome | DataNascita | Citta | Telefono | DataIscrizione |
|---|---|---|---|---|---|---|
| 1 | Alessandro | Musiani | 1962-03-05 | Bologna | 398 1933748 | 2023-04-28 |
| 2 | Chiara | Cavazza | 1965-02-08 | Bologna | 350 2244035 | 2025-01-01 |
| 3 | Noemi | Selmi | 2004-03-02 | Bologna | 395 6827549 | 2025-12-31 |
| 4 | Stefano | Guerra | 1985-10-02 | Bologna | 322 3217004 | 2024-12-31 |
| 5 | Andrei | Gatti | 1988-11-20 | Bologna | 345 5769045 | 2026-01-01 |

### Iscrizioni (220 righe)

| IdIscrizione | IdSocio | IdCorso | DataInizio | DataFine |
|---|---|---|---|---|
| 1 | 22 | 3 | 2023-02-21 |  |
| 2 | 14 | 16 | 2023-02-27 | 2023-08-22 |
| 3 | 81 | 23 | 2023-03-24 |  |
| 4 | 16 | 14 | 2023-04-11 | 2023-11-13 |
| 5 | 1 | 4 | 2023-05-07 |  |
