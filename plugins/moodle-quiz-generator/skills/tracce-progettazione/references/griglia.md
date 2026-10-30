# La griglia di valutazione

La griglia va nel Word della verifica (anche nella copia PDP), su una pagina orizzontale. La genera `scripts/uscite_traccia.js` dalla traccia: le righe delle query sono tante quante le query, la riga della pagina PHP c'è solo se c'è la pagina. Il voto è il punteggio diviso 10, arrotondato al mezzo voto più vicino.

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

- **Query a peso uguale**: il monte delle query si divide in parti uguali, qualunque sia il gradino, per non penalizzare due volte chi è in difficoltà. Le parti sono intere: 30 su 4 query fa 8, 8, 7, 7.
- **Fasce dei livelli** (Insufficiente, Base, Sufficiente, Buono, Ottimo): in proporzione al massimo della riga. 15 dà 0-3, 4-6, 7-9, 10-12, 13-15; 10 dà 0-2, 3-4, 5-6, 7-8, 9-10.
- **Coerenza**: le righe del modello relazionale e delle query dicono che si valutano sul modello dello studente, non sulla soluzione del docente.
- Senza gerarchie ISA nella soluzione la terza riga diventa «Vincoli (cardinalità)», con i descrittori senza ISA.

## Personalizzare

Se l'utente vuole pesi diversi per una verifica, scrivili in `griglia.pesi` della traccia (tutte le chiavi, totale 100): `{"entita": 15, "associazioni": 15, "vincoli": 10, "documentazione": 10, "relazionale": 20, "query": 30, "php": 0}`. Lo script avvisa se il totale non fa 100.

## Descrittori

Sono quelli della griglia dell'utente, adattati (ristrutturazioni nell'Ottimo delle entità, ipotesi aggiuntive nella documentazione), più quelli della pagina PHP. Stanno in `DESCRITTORI` di `scripts/uscite_traccia.js`: per cambiarli si cambia lì, e cambiano per tutte le verifiche.
