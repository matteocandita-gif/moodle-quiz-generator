# Ambulatorio veterinario — taglia grande

Un ambulatorio veterinario della provincia di Bologna, con pronto soccorso aperto tutti i giorni, cura gli animali dei suoi clienti. Ogni animale ha un solo proprietario; l'animale viene registrato come paziente (DataRegistrazione) e poi visitato dai veterinari dell'ambulatorio (tabella Visite).

Nome del database: `veterinario` · seme 5103 · Proprietari 50 righe, Animali 80 righe, Veterinari 10 righe, Visite 220 righe

## Schema (per le tracce della dashboard)

**Proprietari** (__IdProprietario__, Nome, Cognome, Citta, Telefono)
**Animali** (__IdAnimale__, Nome, Specie, Razza, DataNascita, DataRegistrazione, IdProprietario*)
**Veterinari** (__IdVeterinario__, Nome, Cognome, Specializzazione)
**Visite** (__IdVisita__, IdAnimale*, IdVeterinario*, Data, Motivo, Costo)

## Schema (HTML per Moodle)

```html
<p><strong>Proprietari</strong> (<u>IdProprietario</u>, Nome, Cognome, Citta, Telefono)</p>
<p><strong>Animali</strong> (<u>IdAnimale</u>, Nome, Specie, Razza, DataNascita, DataRegistrazione, IdProprietario*)</p>
<p><strong>Veterinari</strong> (<u>IdVeterinario</u>, Nome, Cognome, Specializzazione)</p>
<p><strong>Visite</strong> (<u>IdVisita</u>, IdAnimale*, IdVeterinario*, Data, Motivo, Costo)</p>
```

## Righe pensate per smascherare gli errori

- tre animali (il quinto e gli ultimi due) non sono mai stati visitati, e alcuni gatti registrati nel 2025 hanno più visite: una JOIN inutile con Visite in una query sugli animali perde i primi e ripete i secondi
- Animali.DataRegistrazione e Visite.Data sono date diverse: filtrare l'una al posto dell'altra cambia il risultato
- gatti registrati esattamente il 2025-01-01 e il 2025-12-31 (e il 2024-12-31, il 2026-01-01): smascherano i confini dell'anno
- tre animali senza visite (LEFT JOIN), l'ultimo veterinario non ha ancora visitato
- due animali si chiamano «Luna»: raggruppare per nome dell'animale li fonde
- il secondo e il penultimo proprietario sono omonimi, con un animale ciascuno: raggruppare per nome dà 2 animali e supera HAVING >= 2; i loro animali hanno 1 e 2 visite, delle quali una ciascuno in Medicina generale
- alcuni animali hanno Razza NULL; i costi sono tondi (40.00, 45.00, 80.00…)

## Controlli di coerenza (tutti rispettati)

- una visita non precede la registrazione dell'animale
- un animale è registrato dopo la nascita
- il motivo della visita è coerente con la specializzazione

## Prime righe

### Proprietari (50 righe)

| IdProprietario | Nome | Cognome | Citta | Telefono |
|---|---|---|---|---|
| 1 | Elena | Orlando | Imola | 382 1201130 |
| 2 | Camilla | Coppola | Bologna | 384 4019446 |
| 3 | Gabriel | Sorrentino | Bologna | 392 4430723 |
| 4 | Michele | Greco | Taranto | 326 1773437 |
| 5 | Benedetta | Bertolini | Pianoro | 370 3869411 |

### Animali (80 righe)

| IdAnimale | Nome | Specie | Razza | DataNascita | DataRegistrazione | IdProprietario |
|---|---|---|---|---|---|---|
| 1 | Luna | Gatto | Europeo | 2021-09-03 | 2026-08-30 | 1 |
| 2 | Tigre | Gatto | Maine coon | 2013-09-06 | 2025-01-01 | 1 |
| 3 | Milo | Gatto | Persiano | 2025-09-29 | 2025-12-31 | 1 |
| 4 | Kira | Gatto | Europeo | 2020-01-15 | 2024-12-31 | 3 |
| 5 | Briciola | Gatto | Europeo | 2025-04-19 | 2026-01-01 | 3 |

### Veterinari (10 righe)

| IdVeterinario | Nome | Cognome | Specializzazione |
|---|---|---|---|
| 1 | Roberto | Barbieri | Medicina generale |
| 2 | Youssef | De Santis | Chirurgia |
| 3 | Paolo | Tinti | Dermatologia |
| 4 | Maria | Marchetti | Cardiologia |
| 5 | Carlo | Sala | Medicina generale |

### Visite (220 righe)

| IdVisita | IdAnimale | IdVeterinario | Data | Motivo | Costo |
|---|---|---|---|---|---|
| 1 | 33 | 6 | 2019-02-10 | Estrazione | 150 |
| 2 | 33 | 3 | 2019-05-11 | Visita dermatologica | 70 |
| 3 | 49 | 1 | 2019-11-13 | Controllo | 40 |
| 4 | 49 | 1 | 2019-12-10 | Visita urgente | 80 |
| 5 | 76 | 7 | 2019-12-21 | Vaccinazione | 45 |
