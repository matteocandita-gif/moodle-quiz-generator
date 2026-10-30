---
name: "tracce-progettazione"
description: "Crea tracce di progettazione di database da dare agli studenti (E/R, documentazione, schema relazionale, query SQL, pagina PHP facoltativa) con preset di difficoltà Base, Intermedio, Avanzato, Esame e voci regolabili (entità, associazioni, ricorsive, deboli, ISA, livello del testo, ipotesi aggiuntive, query); parte dal modello bersaglio, prova le query, scrive note per il docente e consegna il Word della verifica (con griglia e copia PDP) o l'HTML per la descrizione di un Compito Moodle. La soluzione la fa diagrammi-er dallo stesso modello. Usala per «una traccia di progettazione su…», «prepara la verifica sul modello E/R», «un esercizio E/R per le quinte», «una simulazione della seconda prova», «rendi più difficile questa traccia»."
---

# Tracce di progettazione

**Lingua.** Rispondi all'utente sempre in italiano, anche quando il messaggio che avvia la skill è in inglese.

Questa skill **crea** tracce di progettazione di database per gli studenti di quinta SIA. La **soluzione** non la fa questa skill: la fa `diagrammi-er`, dallo stesso modello bersaglio. Le tracce si salvano nella dashboard «Tracce di progettazione» quando c'è (`references/dashboard.md`); altrimenti si lavora in chat con il file JSON della traccia.

## Dove stanno le cose

| File | Serve per |
|---|---|
| `references/opzioni.md` | **sempre**, prima di cominciare: le voci, i preset e il significato dei tre livelli del testo |
| `references/formato.md` | il documento JSON della traccia (è anche quello della dashboard) e come escono Word, Word PDP e HTML |
| `references/griglia.md` | pesi, fasce e descrittori della griglia di valutazione, e come si personalizzano |
| `references/dashboard.md` | la dashboard: collezioni, stati, avvio delle sessioni, installazione |
| `scripts/uscite_traccia.js` | Word della verifica, Word PDP e HTML per Moodle dal JSON della traccia (Node, nessuna libreria); lo stesso codice gira nella dashboard |
| `esempi/` | tracce complete nel formato standard, con il loro `.er` |

## Il processo

1. **Opzioni.** Prendi il preset e le voci dalla richiesta o dal modulo della dashboard (`references/opzioni.md`). Dove manca un dato, il valore del preset; se manca anche il preset, Intermedio. Controlla i contesti già usati (le tracce nella dashboard, gli esempi del libro: biblioteca, hotel, calciatori, veicoli, dipendenti, compiti): proponine uno nuovo, realistico e vicino all'esperienza degli studenti o al mondo aziendale.
2. **Modello bersaglio.** Prima del testo, progetta la soluzione con i costrutti richiesti e scrivila come descrizione `.er` di `diagrammi-er` (leggi il suo `references/descrizione.md`): entità, chiavi, associazioni con cardinalità, ISA, attributi opzionali, le ipotesi che vuoi lasciare agli studenti (`ipotesi:`) e i vincoli. Conta che il modello rispetti le voci: numero di entità, N a N con o senza attributi, 1 a 1, ricorsiva, debole, ISA.
3. **Query.** Scrivi le query sul modello (`query:` nel `.er`), una per requisito da verificare (vedi «Le query» sotto). Provale su un piccolo database SQLite con poche righe scritte apposta per mettere alla prova i casi limite (un elemento senza collegamenti, due righe con lo stesso valore, un attributo opzionale vuoto). Una query che non si riesce a scrivere sul modello indica un difetto della traccia o del modello: correggi prima di andare avanti.
4. **Testo.** Scrivi la traccia **dal modello**, al livello del testo scelto: ogni entità, attributo, associazione e cardinalità della soluzione deve ricavarsi dal testo, salvo i punti lasciati di proposito alle ipotesi aggiuntive. Elementi da ristrutturare (un dato multiplo, un dato derivato) entrano nel testo come li direbbe un cliente, senza suggerire la soluzione.
5. **Rilettura da studente.** Rileggi solo la traccia, senza guardare il modello, e ricava il modello che ne verrebbe. Ogni differenza dal modello bersaglio è un'ambiguità da togliere dal testo oppure un'ipotesi voluta, da scrivere nelle note per il docente. Controlla anche le regole qui sotto.
6. **Consegna.** Scrivi il JSON della traccia (`references/formato.md`): blocchi del testo, query con gradino e requisito, note per il docente (costrutti, ipotesi attese, punti delicati da guardare in correzione, durata stimata, il `.er`). Con la dashboard la salvi nella scheda in stato «Da rivedere»; in chat consegni il testo e, se servono, i file con `node scripts/uscite_traccia.js TRACCIA.json --word --pdp --html` (stampa errori e avvisi: leggili). Riferisci all'utente in poche righe contesto, costrutti, ipotesi lasciate aperte e durata stimata.
7. **Soluzione**, quando la chiede l'utente o la scheda: `diagrammi-er` con il `.er` della traccia, nel modulo «soluzione completa» (il blocco `traccia:` è il testo della realtà).

Se l'utente chiede di **modificare** una traccia (più difficile, meno entità, un'altra ISA), cambia prima il modello, poi il testo, poi rifai i passi 3 e 5.

## Regole didattiche

Valgono per ogni traccia, qualunque preset.

- **Legami a tre**: nessuna realtà che richiede un'associazione ternaria. Al massimo come punto opzionale di un'esercitazione Avanzata, e lo dici all'utente quando lo proponi.
- **Attributi multivalore**: nella soluzione non ci sono. Un dato multiplo nel testo (più telefoni, più autori) diventa un'entità con un'associazione 1 a N: è uno degli «elementi da ristrutturare».
- **Chiavi delle entità**: identificatore semplice. Se quello naturale è composto (nome del comune e provincia), codice artificiale più vincolo di unicità sui campi naturali, scritto nella documentazione (`tipo …; unico insieme a …` o una riga `vincolo:`). Niente chiavi composte nelle entità forti.
- **Coppia che si ripete**: se la stessa coppia di istanze si può legare più volte (lo stesso spettatore prenota due volte lo stesso concerto) o se un'altra parte del modello deve riferirsi a quel legame, nel modello E/R non è un'associazione ma un'**entità** con un suo codice e due associazioni 1 a N (Prenotazione). Le N a N vere restano associazioni, e nello schema relazionale la loro chiave è la coppia delle chiavi esterne.
- **Entità deboli**: solo nel preset Avanzato o se le sceglie l'utente.
- **Testo pulito**: nessun elemento citato e poi non sviluppato; nessun dato ridondante che non sia una ristrutturazione voluta; requisiti sui dati, non sull'applicazione (niente «il gestore può modificare, il cliente solo consultare»).
- **Ipotesi aggiuntive**: almeno una davvero necessaria, nel numero scelto. Quelle che ti aspetti vanno nelle note per il docente.
- **Stile**: impersonale ed esteso, come le consegne degli esercizi dell'utente. Nella soluzione le entità sono al singolare anche se il testo parla al plurale.
- **Valutazione**: modello relazionale e query si valutano sulla coerenza con l'E/R dello studente (è scritto nella griglia).

## Le query

- **Mirate**: ogni query verifica un requisito preciso del modello: un attributo che altrimenti verrebbe dimenticato (la disponibilità di un libro), l'attributo di una N a N, la ricorsiva, la specializzazione giusta della ISA, un attributo opzionale. Nel JSON ogni query ha il suo `requisito`.
- **Gradini**, senza sottoquery: 1. JOIN, filtri, ordinamento; 2. GROUP BY, conteggi e somme, HAVING; 3. LEFT JOIN (anche per «chi non ha…»), i primi N e il massimo con ORDER BY … LIMIT. Il gradino scelto è un **tetto**: le query possono essere tutte del primo gradino se la traccia è semplice.
- **Requisiti aggiunti dalle query** (voce delle opzioni): una query può chiedere un dato che il testo non nomina (le prenotazioni dell'ultimo mese chiedono di salvarne la data). Succede anche all'esame di Stato. Quando c'è, il JSON ha `requisiti_query: true` e la consegna lo dichiara («tenendo conto anche delle informazioni richieste dalle query»).
- Le richieste si scrivono come le scrive l'utente: «Elenco di…», «Per ogni…, il numero di…», con i valori da cercare tra apici ('Martin Scorsese') o come dato scelto dall'utente («un determinato fornitore»).

## La pagina PHP (facoltativa)

Una pagina che legge o scrive il database della traccia: elenco, ricerca da form (GET) o inserimento (POST). Il testo dice che cosa mostra o inserisce e da quale form; i dati di connessione o sono dati nella traccia (host, utente, password, database) o restano a scelta. Le convenzioni del codice della soluzione sono quelle di `domande-php-mysqli-mock`.

## Con le altre skill

- `diagrammi-er`: il modello bersaglio e la soluzione (diagramma, documentazione, schema, query).
- `database-didattici`: se l'utente vuole anche un database popolato dalla traccia, per provare le query in classe.
- `progettazione-quiz`: una traccia di progettazione dentro un quiz Moodle (domanda a risposta aperta con file) segue le regole di questa skill per il testo.
