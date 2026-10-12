# Palestra — taglia piccolo

Una palestra della provincia di Bologna organizza corsi tenuti dai suoi istruttori. Ogni corso ha un solo istruttore; un socio si iscrive alla palestra (DataIscrizione) e poi a uno o più corsi (tabella Iscrizioni). Un'iscrizione a un corso è attiva finché DataFine è vuota.

Nome del database: `palestra` · seme 5101 · Istruttori 6 righe, Corsi 10 righe, Soci 12 righe, Iscrizioni 20 righe

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

### Istruttori (6 righe)

| IdIstruttore | Nome | Cognome | Qualifica | DataAssunzione |
|---|---|---|---|---|
| 1 | Giulia | De Santis | Laurea in Scienze motorie | 2021-07-25 |
| 2 | Erica | Costantini | Diploma ISEF | 2022-11-10 |
| 3 | Tommaso | Villa | Istruttore federale | 2022-05-16 |
| 4 | Giulia | Grasso | Laurea in Scienze motorie | 2014-12-17 |
| 5 | Erica | Costantini | Personal trainer certificato | 2017-06-05 |

### Corsi (10 righe)

| IdCorso | Nome | Livello | Giorno | Orario | CostoMensile | PostiMax | IdIstruttore |
|---|---|---|---|---|---|---|---|
| 1 | Yoga | Base | Sabato | 19:30 | 40 | 10 | 1 |
| 2 | Yoga | Avanzato | Martedì | 18:30 | 30 | 12 | 1 |
| 3 | Pilates | Base | Venerdì | 17:30 | 50 | 10 | 1 |
| 4 | Kickboxing | Base | Giovedì | 17:30 | 42.5 | 15 | 3 |
| 5 | Ginnastica posturale | Intermedio | Giovedì | 17:30 | 50 | 15 | 3 |

### Soci (12 righe)

| IdSocio | Nome | Cognome | DataNascita | Citta | Telefono | DataIscrizione |
|---|---|---|---|---|---|---|
| 1 | Fabio | D'Amico | 1991-03-17 | Bologna |  | 2024-10-31 |
| 2 | Samuele | De Santis | 1984-04-06 | Bologna | 364 8740894 | 2025-01-01 |
| 3 | Camilla | Donati | 1998-08-11 | Bologna | 395 7103905 | 2025-12-31 |
| 4 | Chiara | Villa | 1974-04-20 | Bologna | 395 1096099 | 2024-12-31 |
| 5 | Riccardo | Esposito | 1998-08-08 | Bologna | 396 0200040 | 2026-01-01 |

### Iscrizioni (20 righe)

| IdIscrizione | IdSocio | IdCorso | DataInizio | DataFine |
|---|---|---|---|---|
| 1 | 7 | 4 | 2023-11-29 |  |
| 2 | 7 | 7 | 2023-12-14 |  |
| 3 | 7 | 3 | 2024-03-26 |  |
| 4 | 1 | 6 | 2024-11-21 |  |
| 5 | 1 | 4 | 2024-11-28 |  |
