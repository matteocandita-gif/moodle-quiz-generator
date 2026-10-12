# Ambulatorio veterinario — taglia piccolo

Un ambulatorio veterinario della provincia di Bologna, con pronto soccorso aperto tutti i giorni, cura gli animali dei suoi clienti. Ogni animale ha un solo proprietario; l'animale viene registrato come paziente (DataRegistrazione) e poi visitato dai veterinari dell'ambulatorio (tabella Visite).

Nome del database: `veterinario` · seme 5103 · Proprietari 6 righe, Animali 10 righe, Veterinari 5 righe, Visite 20 righe

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

### Proprietari (6 righe)

| IdProprietario | Nome | Cognome | Citta | Telefono |
|---|---|---|---|---|
| 1 | Elena | Orlando | Imola | 382 1201130 |
| 2 | Camilla | Coppola | Bologna | 384 4019446 |
| 3 | Gabriel | Sorrentino | Bologna | 392 4430723 |
| 4 | Michele | Greco | Taranto | 326 1773437 |
| 5 | Camilla | Coppola | Zola Predosa | 370 3869411 |

### Animali (10 righe)

| IdAnimale | Nome | Specie | Razza | DataNascita | DataRegistrazione | IdProprietario |
|---|---|---|---|---|---|---|
| 1 | Luna | Gatto | Europeo | 2018-11-22 | 2019-11-18 | 1 |
| 2 | Tigre | Gatto | Siamese | 2018-09-05 | 2025-01-01 | 1 |
| 3 | Milo | Gatto | Siamese | 2024-01-15 | 2025-12-31 | 1 |
| 4 | Kira | Gatto | Persiano | 2014-09-13 | 2024-12-31 | 3 |
| 5 | Briciola | Gatto | Maine coon | 2022-06-04 | 2026-01-01 | 3 |

### Veterinari (5 righe)

| IdVeterinario | Nome | Cognome | Specializzazione |
|---|---|---|---|
| 1 | Angelo | Grandi | Medicina generale |
| 2 | Thomas | Chen | Chirurgia |
| 3 | Vincenzo | De Santis | Dermatologia |
| 4 | Filippo | Monti | Cardiologia |
| 5 | Rebecca | Ferraro | Medicina generale |

### Visite (20 righe)

| IdVisita | IdAnimale | IdVeterinario | Data | Motivo | Costo |
|---|---|---|---|---|---|
| 1 | 1 | 3 | 2019-11-19 | Controllo | 40 |
| 2 | 1 | 1 | 2019-11-27 | Controllo | 40 |
| 3 | 1 | 1 | 2019-12-23 | Controllo | 40 |
| 4 | 8 | 1 | 2020-06-24 | Visita urgente | 80 |
| 5 | 1 | 1 | 2021-03-09 | Controllo | 40 |
