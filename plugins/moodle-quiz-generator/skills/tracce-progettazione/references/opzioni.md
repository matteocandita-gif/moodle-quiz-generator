# Opzioni e preset

Il preset imposta tutte le voci; l'utente può cambiarne qualcuna. Nel JSON della traccia le voci stanno in `opzioni` con le chiavi della prima colonna.

## Le voci

| Chiave | Voce | Valori |
|---|---|---|
| `entita` | entità nella soluzione (comprese quelle nate da una ristrutturazione) | fascia: `3-4`, `5-6`, `7-9` |
| `nn` | associazioni N a N | `1` senza attributi · `1-2` almeno una con attributi · `2+` con attributi |
| `uno_uno` | associazione 1 a 1 | `sì` / `no` / `a scelta` |
| `ricorsiva` | associazione ricorsiva | `sì` / `no` / `a scelta` |
| `debole` | entità debole | `sì` / `no` |
| `isa` | gerarchia ISA | `sì` / `no` / `a scelta` |
| `opzionali` | attributi opzionali (0,1) | `sì` / `no` |
| `ristrutturare` | elementi da ristrutturare | `0`, `1`, `2` (dato multiplo che diventa entità, dato derivato o ridondante da non salvare) |
| `chiavi` | chiavi | `date` dal testo · `in parte` · `da scegliere` |
| `testo` | livello del testo | `guidato` · `intermedio` · `aperto` |
| `ipotesi` | ipotesi aggiuntive richieste | numero, almeno 1 |
| `documentazione` | documentazione da consegnare | `sì` / `no` |
| `sql_tabelle` | definizione SQL di alcune tabelle con i vincoli | `sì` / `no` |
| `query` | numero di query | numero |
| `gradino` | gradino massimo delle query | `1`, `2`, `3` (è un tetto, vedi SKILL.md) |
| `requisiti_query` | requisiti aggiunti dalle query | `0`, `1` |
| `php` | pagina PHP | `no` · `elenco` · `ricerca` (form GET) · `inserimento` (form POST) |

«a scelta» vuol dire: Claude decide in base al contesto e lo scrive nelle note per il docente.

## I preset

| Voce | Base | Intermedio | Avanzato | Esame |
|---|---|---|---|---|
| `entita` | 3-4 | 5-6 | 7-9 | 7-9 |
| `nn` | 1 | 1-2 | 2+ | 2+ |
| `uno_uno` | no | sì | sì | a scelta |
| `ricorsiva` | no | no | sì | a scelta |
| `debole` | no | no | sì | no |
| `isa` | no | sì | sì | a scelta |
| `opzionali` | no | sì | sì | sì |
| `ristrutturare` | 0 | 1 | 2 | 1-2 |
| `chiavi` | date | in parte | da scegliere | da scegliere |
| `testo` | guidato | intermedio | aperto | aperto |
| `ipotesi` | 1 | 2 | 3-4 | 3-4 |
| `documentazione` | sì | sì | sì | sì |
| `sql_tabelle` | no | no | a scelta | sì |
| `query` | 3 | 3-4 | 4-5 | 3-4 |
| `gradino` | 1 | 2 | 3 | 3 |
| `requisiti_query` | 0 | 0 | 1 | 1 |
| `php` | no | no | a scelta | a scelta |

Il preset **Esame** ha anche il formato della simulazione: premessa, «Il candidato, fatte le opportune ipotesi aggiuntive, sviluppi:», realtà raccontata come un caso aziendale (vedi le prove ministeriali SIA: profilo dell'azienda, poi l'elenco di che cosa deve gestire la base di dati).

## I livelli del testo

| Aspetto | Guidato | Intermedio | Aperto |
|---|---|---|---|
| Struttura | «Di ogni X interessano…»: un paragrafo per entità, attributi elencati | paragrafi per argomento; qualche attributo sparso in un altro paragrafo | racconto della realtà o profilo dell'azienda: le entità vanno riconosciute |
| Cardinalità | tutte dette («ogni… uno o più…», «al massimo uno») | quasi tutte dette; una o due da dedurre | da dedurre dalla realtà |
| Sinonimi e rumore | nessuno: un nome per ogni concetto | qualche sinonimo (cliente e acquirente) | sinonimi e informazioni di contesto da non modellare |

Le chiavi seguono la voce `chiavi`, non il livello del testo: «date» vuol dire che il testo dice che cosa identifica ogni entità («identificato da un codice», «il nome, che lo identifica»).

## La durata stimata

La scrivi nelle note per il docente come indicazione, perché l'utente decida se la traccia sta nel tempo che ha. Un riferimento di partenza, da tarare con l'utente: 4 minuti per entità (diagramma), 2 per entità e associazione (documentazione), 10-15 per lo schema relazionale, 5 / 8 / 10 minuti per una query di gradino 1 / 2 / 3, 25-30 per la pagina PHP, più 10 minuti di lettura. Arrotonda ai 5 minuti e confronta con l'uso: una verifica sta di solito in un'ora o due.
