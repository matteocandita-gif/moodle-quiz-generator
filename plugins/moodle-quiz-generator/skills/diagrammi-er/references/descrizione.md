# La descrizione di un modello E/R (file .er)

Un file di testo, una riga per elemento. Le righe vuote e quelle che cominciano con `#` non contano. Le righe **rientrate** (spazi o tab) appartengono all'entità, all'associazione o alla gerarchia della riga sopra.

Una descrizione minima basta per il diagramma; le righe in più servono solo ai moduli che le usano. La colonna **Modulo** dice chi usa ogni riga: **D** diagramma, **S** schema relazionale, **Doc** documentazione.

```
titolo: Noleggio veicoli
ipotesi: Ogni auto può avere al massimo un conducente incluso
vincolo: Un conducente non può essere assegnato a due auto noleggiate negli stessi giorni

entita Veicolo @ 1 0
    sinistra: *Codice, Marca, Modello, Anno
    descrizione: I veicoli dell'agenzia
    tipo Codice: Testo fisso; lunghezza 7
entita Compagnia assicurativa @ 2.5 0
    sotto: *Codice, Nome
    plurale: Compagnie
entita Auto @ 0.4 1.1
    sinistra: Num_porte, Alimentazione
entita Moto @ 1.6 1.1
    destra: Cilindrata
entita Conducente @ 0.4 2.2
    sinistra: *Cod_f, Nome, Cognome, Email (0,1)

gerarchia Veicolo: Auto, Moto (t,e)
    traduzione: lasciare tutto

associazione assicurato: Veicolo (1,1) -- Compagnia assicurativa (1,N)
    sotto: Tariffa
associazione con: Auto (0,1) -- Conducente (1,N)
```

## Intestazione (facoltativa)

| Riga | Modulo | Significato |
|---|---|---|
| `titolo: …` | tutti | nome della pagina draw.io e titolo della soluzione |
| `traccia:` | soluzione | la traccia dell'esercizio: sulla stessa riga o sulle righe rientrate sotto, una riga per paragrafo (`**grassetto**` e `*corsivo*` ammessi); apre la soluzione completa |
| `griglia: L A` | D | larghezza di una colonna e altezza di una riga, in pixel (predefinite 250 e 170) |
| `ipotesi: …` | Doc | un'ipotesi aggiuntiva; una riga per ipotesi |
| `vincolo: …` | Doc | un vincolo non esprimibile; una riga per vincolo |
| `query: RICHIESTA` | soluzione | una query SQL della soluzione: la richiesta della traccia sulla riga, il codice sulle righe rientrate sotto (i rientri interni restano; i commenti `--` spiegano le scelte); una riga `query:` per query, nell'ordine della traccia |
| `colori: entita=… associazioni=…` | D | da non scrivere nei diagrammi nuovi (valgono entità azzurre e associazioni bianche); solo per ridisegnare com'è una figura esistente del libro: `rosa`, `verde`, `giallo`, `arancio`, `bianco`, `azzurro` |

## Entità

`entita NOME @ COLONNA RIGA` mette il centro del rettangolo nella cella della griglia (dallo 0, anche con decimali: `@ 1.5 0`). La posizione serve solo al diagramma: per lo schema o la documentazione si può scrivere solo `entita NOME`. Il nome va al singolare e può avere spazi.

| Riga rientrata | Modulo | Significato |
|---|---|---|
| `sopra: A, B` · `sotto: …` · `sinistra: …` · `destra: …` | tutti | attributi su quel lato (sopra e sotto da sinistra a destra, ai lati dall'alto in basso); l'ordine delle righe è anche l'ordine dei campi nello schema e nella documentazione |
| `attributi: A, B` | tutti | attributi senza lato (per lo schema o la documentazione; nel diagramma vanno sotto) |
| `*` davanti a un attributo | tutti | fa parte della chiave primaria |
| `(0,1)` dopo un attributo | tutti | attributo opzionale (`destra: Email (0,1), Telefono`): nel diagramma la cardinalità sul gambetto, nella documentazione «Opzionale» tra i vincoli, nello schema il vincolo «può essere NULL»; non per la chiave primaria. Un attributo con più valori non si scrive: diventa un'entità a parte |
| `identificata da: ASSOC1, ASSOC2` | tutti | entità debole: la chiave comprende anche le chiavi delle entità collegate da queste associazioni |
| `descrizione: …` | Doc | descrizione dell'entità |
| `sinonimi: …` | Doc | sinonimi presenti nel testo (Utente, Stanza) |
| `tipo ATTRIBUTO: TIPO; VINCOLI` | Doc | tipo di dato dall'elenco del libro e vincoli (`tipo PrezzoNotte: Decimale; valore > 0`); la chiave primaria si aggiunge da sola |
| `plurale: …` | S | nome della relazione, se il plurale calcolato non va (`plurale: Compagnie`) |
| `larghezza: N` | D | larghezza minima del rettangolo in pixel, quando su un lato arrivano più linee e i rombi devono stargli di fronte (`larghezza: 420`) |

- Un solo `*`: chiave semplice, pallino pieno. Più `*`: chiave composta; nel diagramma gli attributi della chiave stanno **sullo stesso lato**.
- Entità debole: nel diagramma gli attributi della chiave stanno **sopra o sotto**, e le associazioni di `identificata da` arrivano **ai fianchi** dell'entità.
- Le specializzazioni di una gerarchia non hanno `*`: ereditano la chiave della generalizzazione.

## Associazioni

`associazione NOME: ENTITA1 (min,max) -- ENTITA2 (min,max) [@ COLONNA RIGA]`

- Il nome (verbo al singolare) è tutto quello che sta prima dei due punti, anche con spazi.
- Ogni cardinalità si scrive **accanto all'entità a cui si riferisce**: `Studente (1,1) -- Classe (1,N)`.
- Nel diagramma, senza posizione, il rombo va a metà tra le due entità, che devono stare sulla stessa riga o colonna; altrimenti `@ COLONNA RIGA`.
- Stessa entità ai due lati: **ricorsiva**. Il rombo va a destra (`@ sinistra` per metterlo a sinistra); la prima cardinalità va sulla linea a gomito, la seconda sulla linea diritta.

| Riga rientrata | Modulo | Significato |
|---|---|---|
| `sopra: …` · `sotto: …` · `sinistra: …` · `destra: …` · `attributi: …` | tutti | attributi dell'associazione (per un rombo tra due entità in colonna usa `sinistra` o `destra`) |
| `descrizione: …` · `tipo ATTRIBUTO: TIPO; VINCOLI` | Doc | come per le entità |
| `chiave esterna: NOME` | S | nome della chiave esterna (1 a N, 1 a 1, ricorsiva 1 a N: `chiave esterna: id_capo`) |
| `chiavi esterne: A, B` | S | N a N: i nomi delle due chiavi esterne, nell'ordine delle entità (obbligatori nella N a N ricorsiva: `chiavi esterne: Id_seguace, Id_seguito`) |
| `tabella: NOME` | S | N a N: nome della relazione nuova (predefinito Plurale1_Plurale2; per le ricorsive un nome che dica il legame: `tabella: Colleghi`) |
| `chiave esterna in: ENTITA` | S | 1 a 1: in quale relazione va la chiave esterna, quando entrambe le partecipazioni sono obbligatorie o entrambe opzionali |

## Gerarchie ISA

`gerarchia GENERALIZZAZIONE: SPEC1, SPEC2 (t,e)` con la classificazione: `t` totale o `nt` non totale, `e` esclusiva o `ne` non esclusiva. Generalizzazione e specializzazioni sono entità scritte con `entita`; nel diagramma le specializzazioni stanno sotto la generalizzazione (riga più in basso).

| Riga rientrata | Modulo | Significato |
|---|---|---|
| `traduzione: tutto su` · `tutto giù` · `lasciare tutto` | S | strategia di traduzione (predefinita «lasciare tutto», che funziona sempre); lo script avvisa nei casi che il libro sconsiglia: «tutto giù» con una gerarchia non totale o con un'associazione sulla generalizzazione, «tutto su» con un'associazione su una specializzazione |
| `campo tipo: NOME` | S | con «tutto su», un campo che dice di quale specializzazione è l'istanza (Opzione 2 del libro) |

Con «lasciare tutto» ogni specializzazione ha come chiave la chiave esterna verso la generalizzazione, con il nome secondo la regola delle chiavi esterne (Codice di Veicolo diventa Codice_veicolo).

## Regole per un diagramma leggibile

- Due entità collegate distano almeno una colonna (o una riga): rombo e cardinalità devono starci. Se lo script avvisa «molto vicina», allarga `griglia:` o allontana le entità.
- Gli attributi vanno sui lati da cui **non** arrivano linee: lo script avvisa quando una linea arriva sul lato degli attributi.
- Su un lato possono arrivare più linee (un'entità collegata a molte altre): ognuna parte dal punto del lato di fronte al suo rombo, quindi i rombi vanno messi con `@` di fronte al lato, a una distanza di almeno 40 px l'uno dall'altro; se il lato è troppo corto si allarga l'entità con `larghezza:`. Lo script avvisa quando una linea verrebbe obliqua o due linee sono troppo vicine. Una generalizzazione ha la gerarchia sotto, una specializzazione sopra.
- Tra due righe di entità con attributi sotto e sopra servono più di 170 px: usa righe a 1.4 o 1.5.
- Molti attributi su un lato allargano molto il rettangolo: dividili tra due lati.
- Nomi delle entità al **singolare** e verbo delle associazioni al singolare, anche se la traccia parla al plurale: lo script avvisa quando un nome sembra plurale. Attributi senza spazi, come nel libro (`DataNascita`, `Ore_settimanali`).

## Ritocchi in draw.io

Ogni entità è un **gruppo** con i suoi attributi e la linea della chiave: si sposta con un trascinamento e le linee la seguono. Le cardinalità e la classificazione delle gerarchie sono attaccate alle linee. Si possono cambiare testi, cardinalità, colori, posizioni; si può aggiungere un attributo copiando uno esistente del gruppo. Il PNG si rifà con `drawio_png.py`, che si ferma se trova forme che non conosce. I ritocchi in draw.io cambiano solo il disegno: se cambiano il contenuto (un attributo, una cardinalità), va aggiornata anche la descrizione `.er`, da cui vengono schema e documentazione.
