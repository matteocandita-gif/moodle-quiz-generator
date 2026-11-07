# La griglia di valutazione

La griglia va nel Word della verifica (anche nella copia PDP), su una pagina orizzontale. La genera `scripts/uscite_traccia.js` dalla traccia. Livelli, descrittori predefiniti, fasce e voto stanno nel modulo comune `scripts/griglia.js`, lo stesso che usano le pagine del plugin: non duplicarli altrove.

Una griglia è un elenco di **righe**, ognuna con macroarea, area, punti massimi e i cinque descrittori dei livelli (Insufficiente, Base, Sufficiente, Buono, Ottimo). Le fasce dei livelli non si scrivono: si calcolano dai punti. Il voto è il punteggio diviso il totale, per 10, arrotondato al mezzo voto più vicino (con il totale a 100: il punteggio diviso 10).

Le righe vengono da due strade:

1. **Dai pesi** (la strada normale): lo script costruisce le righe dalle aree qui sotto, con i pesi predefiniti o quelli di `griglia.pesi`.
2. **Personalizzate**: le righe salvate in `griglia.righe` della traccia. Quando ci sono, valgono loro e i pesi non contano più. Servono quando una verifica ha bisogno di un nome, di un descrittore o di una riga che i pesi non danno.

## Pesi predefiniti (totale 100)

| Area | Senza PHP | Con PHP | Chiave in `griglia.pesi` |
|---|---|---|---|
| Entità e attributi | 15 | 15 | `entita` |
| Associazioni | 15 | 15 | `associazioni` |
| Vincoli (cardinalità, ISA) | 15 | 10 | `vincoli` |
| Documentazione tecnica | 10 | 10 | `documentazione` |
| Modello relazionale | 15 | 15 | `relazionale` |
| Interrogazioni SQL | 30 | 20 | `query` |
| Pagina PHP | — | 15 | `php` |
| Domanda aperta | 0 | 0 | `aperta` |

- **Query a peso uguale**: il monte delle query si divide in parti uguali, qualunque sia il gradino, per non penalizzare due volte chi è in difficoltà. Le parti sono intere: 30 su 4 query fa 8, 8, 7, 7.
- **Fasce dei livelli**: in proporzione al massimo della riga. 15 dà 0-3, 4-6, 7-9, 10-12, 13-15; 10 dà 0-2, 3-4, 5-6, 7-8, 9-10.
- **Coerenza**: le righe del modello relazionale e delle query dicono che si valutano sul modello dello studente, non sulla soluzione del docente.
- Senza gerarchie ISA nella soluzione la terza riga diventa «Vincoli (cardinalità)», con i descrittori senza ISA.

## La domanda aperta

Una domanda di teoria (per esempio sul capitolo 3 del libro) sta in fondo alla realtà, in grassetto «**Domanda aperta (10 punti).**», e **entra nella griglia** con la riga «Domanda aperta»: si dà un peso a `aperta` e si tolgono gli stessi punti ad altre aree, così il totale resta 100. Esempio con 10 punti e senza PHP: `{"entita": 15, "associazioni": 15, "vincoli": 10, "documentazione": 10, "relazionale": 15, "query": 25, "php": 0, "aperta": 10}`. La risposta attesa va nei punti delicati delle note per il docente e, nella soluzione, in fondo allo schema relazionale («**Risposta alla domanda aperta**»). Non scrivere più «che si sommano a quelli della griglia»: era il modo di prima, con la griglia a 90.

## Personalizzare

- **Solo i punti**: scrivi in `griglia.pesi` della traccia tutte le chiavi, totale 100. Lo script avvisa se il totale non fa 100.
- **Righe, nomi e descrittori**: dalla dashboard, vista *Uscite*, «Personalizza le righe» copia le righe della griglia attuale in `griglia.righe`, dove si cambiano nome, punti e descrittori, si aggiungono, si spostano e si tolgono righe; «Torna alla griglia dai pesi» le elimina. In chat, scrivi `griglia.righe` con il formato qui sotto, partendo da `U.righePredefinite(traccia)` di `uscite_traccia.js`.

```json
{"macro": "Domanda aperta", "area": "Fasi del ciclo di vita", "max": 10,
 "descrittori": ["…", "…", "…", "…", "…"], "tipo": "aperta"}
```

`macro` è la prima colonna (righe consecutive con la stessa macro si uniscono nel Word); con `area` vuota la riga occupa le due colonne. `max` a `null` fa una riga di sola descrizione, come «Query SQL – Descrizione». `descrittori` a `null` lascia solo le fasce, come nelle righe delle singole query. `tipo` dice da dove viene la riga (`entita`, `query`, `aperta`, `personale`…).

- Le righe personalizzate sono una fotografia: se poi cambi il numero di query della traccia, la griglia non si aggiorna da sola e lo script lo segnala. Rivedi la griglia o torna ai pesi.

## Descrittori

Sono quelli della griglia dell'utente, adattati (ristrutturazioni nell'Ottimo delle entità, ipotesi aggiuntive nella documentazione), più quelli della pagina PHP e della domanda aperta. Stanno in `DESCRITTORI` di `scripts/griglia.js`: per cambiarli per tutte le verifiche si cambia lì; per una sola verifica si personalizzano le righe. Nello stesso modulo ci sono i descrittori delle competenze delle verifiche di programmazione (`teoria`, `lettura`, `debug`, `scrittura`), per le griglie che verranno in «Bozze dei quiz».
