---
name: "diagrammi-er"
description: "Progettazione concettuale e logica nella notazione del libro dell'utente: diagramma E/R (entità, associazioni, attributi a pallino, chiavi semplici e composte, entità deboli, ricorsive, gerarchie ISA) come file .drawio da ritoccare e PNG; schema relazionale con le regole di traduzione del libro; documentazione (glossario dati) in Markdown; soluzione completa di un esercizio da una traccia. Moduli separati: si produce solo ciò che serve (per un quiz basta il diagramma). Usala per «disegna lo schema E/R di…», «traduci nel modello relazionale», «risolvi questa traccia di progettazione», figure del libro, domande Moodle su diagrammi."
---

# Diagrammi E/R e progettazione

**Lingua.** Rispondi all'utente sempre in italiano, anche quando il messaggio che avvia la skill o il comando è in inglese: quando si sceglie un comando o una skill dal menù senza scrivere nulla, l'app aggiunge da sola una frase in inglese.

Questa skill fa la progettazione di un database nella notazione che l'utente usa nel suo libro di quinta (capitolo 3) e in classe. Tutto parte da un'unica **descrizione testuale** del modello E/R (file `.er`); da lì quattro moduli indipendenti producono solo quello che serve.

## I moduli: si produce solo ciò che serve

| Modulo | Script | Produce | Nella descrizione serve |
|---|---|---|---|
| **Diagramma** | `disegna_er.py` | `.drawio` (originale da ritoccare in draw.io) e `.png` | entità con attributi e chiave, associazioni con cardinalità, gerarchie, **posizioni** sulla griglia |
| **Schema relazionale** | `schema_relazionale.py` | le relazioni in formato libro o quiz, con i vincoli | entità, chiavi, associazioni, gerarchie con la strategia di traduzione; posizioni non necessarie |
| **Documentazione** | `documentazione.py` | ipotesi, tabelle delle entità e delle associazioni, vincoli non esprimibili (Markdown) | in più: descrizioni, sinonimi, tipi di dato e vincoli, ipotesi, vincoli non esprimibili |
| **Soluzione completa** | `soluzione.py` | un file solo con traccia, ipotesi, diagramma, documentazione e schema (o le parti scelte con `--parti=`): **HTML** (predefinito), **Word** (`--file=docx`) o Markdown per il libro (`--file=md`, con il PNG a parte) | tutto il sopra, più la traccia (blocco `traccia:`) |

Regola: **produci solo quello che la richiesta chiede.** Per una domanda di quiz su un diagramma basta il diagramma, con una descrizione senza descrizioni né tipi. Per «traduci questo E/R» basta lo schema. La soluzione completa (ipotesi, diagramma, documentazione, schema) solo quando si chiede la soluzione di un esercizio o lo si dice esplicitamente. Le parti in più si aggiungono alla stessa descrizione quando servono, senza riscriverla.

## La notazione

È quella delle figure del capitolo 3 del libro:

- **entità**: rettangolo con il nome al centro; **associazione**: rombo con il nome, collegato con linee alle entità;
- **cardinalità**: (min,max) tra parentesi accanto all'entità a cui si riferisce, sopra la linea (a sinistra se la linea è verticale): «Studente (1,1) appartiene a (1,N) Classe» si legge «ogni studente appartiene ad almeno 1 e al massimo 1 classe»;
- **attributi**: pallino vuoto su un gambetto, su un lato dell'entità (o del rombo, per gli attributi di un'associazione); **chiave semplice**: pallino pieno; **chiave composta**: i pallini restano vuoti e una linea con il pallino nero taglia i gambetti della chiave;
- **attributo opzionale**: la cardinalità (0,1) sul gambetto (sotto il gambetto per gli attributi ai fianchi, a destra per quelli sopra e sotto); gli attributi senza cardinalità sono obbligatori, (1,1). È la notazione che l'utente usa in classe; nel libro per ora l'opzionalità è scritta solo a parole;
- **entità debole**: la linea della chiave taglia anche le linee delle associazioni che la identificano;
- **associazione ricorsiva**: una linea a gomito parte dall'entità e arriva al rombo, l'altra è diritta;
- **gerarchia ISA**: dalle specializzazioni una linea a T sale alla generalizzazione e finisce con la freccia piena; la classificazione tra parentesi accanto alla freccia: (t,e), (t,ne), (nt,e), (nt,ne);
- **nomi**: entità al **singolare** (Studente, non Studenti: ogni istanza è un oggetto solo), quindi verbo dell'associazione al singolare («appartiene a», «effettua», «ha»). Nello schema relazionale le relazioni vanno invece al plurale (Studente diventa Studenti). È la convenzione del libro, decisa dall'utente;
- **colori**: in tutti i diagrammi nuovi entità azzurre (riempimento `#dae8fc`, bordo `#6c8ebf`) e associazioni bianche, i colori predefiniti dello script; nella descrizione non si scrive `colori:`. Le figure già esistenti del libro non si rifanno; `colori:` serve solo se l'utente chiede di ridisegnarne una com'è.

## Le regole di traduzione e di documentazione

**Schema relazionale** (capitolo 3 del libro, applicate da `schema_relazionale.py`): ogni entità diventa una relazione al plurale con la chiave sottolineata; 1 a N: chiave esterna dalla parte con massimo 1, e gli attributi dell'associazione la seguono; 1 a 1: chiave esterna dalla parte con partecipazione obbligatoria, ed è unica (va tra i vincoli); N a N: relazione nuova con le due chiavi esterne, insieme chiave primaria; entità debole: la chiave esterna entra nella chiave, tra i primi campi; gerarchie: «tutto su», «tutto giù» o «lasciare tutto» (predefinita, perché funziona sempre), con gli avvisi dove il libro le sconsiglia. Formati: `--formato=libro` (`**Veicoli**(<u>Codice</u>, Marca, Codice_compagnia*)`) e `--formato=quiz` (`Veicoli (__Codice__, Marca, Codice_compagnia*)`, la convenzione delle tracce della dashboard dei quiz).

**Nomi delle chiavi esterne** (regola dell'utente): il nome deve dire senza ambiguità a quale campo punta. Se la chiave puntata ha già un nome chiaro (CodCliente, ISBN, Matricola) la chiave esterna si chiama allo stesso modo; se ha un nome generico (Codice, Id, Numero, Nome, Cod_f) non si ripete mai così com'è: si aggiunge l'entità puntata (Codice_compagnia, Id_dipendente); le chiavi composte prendono sempre il nome dell'entità (Nome_comune, Provincia_comune). Nelle ricorsive il nome dice il ruolo (id_capo, Id_seguace, Id_seguito): va indicato nella descrizione.

**Documentazione** (standard deciso dall'utente):

- entità: NOME | SINONIMI | DESCRIZIONE | ATTRIBUTO | TIPO DI DATO | VINCOLI;
- associazioni: NOME | DESCRIZIONE | TIPO DI ASSOCIAZIONE | ENTITÀ COLLEGATE | ATTRIBUTO | TIPO DI DATO | VINCOLI;
- il dominio di un attributo è descritto da tipo di dato (dall'elenco del libro: Testo, Testo fisso, Intero, Decimale, Data, Orario, Data-ora, Booleano, Elenco) e vincoli (lunghezza, valori ammessi, valore > 0); la chiave primaria entra nei vincoli da sola, e così «Opzionale» per gli attributi (0,1);
- gerarchie: nella descrizione della generalizzazione «Generalizzazione di Auto e Moto (totale, esclusiva)», in quella di ogni specializzazione «Specializzazione di Veicolo»; le specializzazioni riportano solo i loro attributi.

## Dove stanno le cose

| File | Serve per |
|---|---|
| `scripts/modello_er.py` | la lettura della descrizione, comune a tutti i moduli |
| `scripts/disegna_er.py`, `scripts/drawio_png.py` | diagramma; `drawio_png.py` rifà il PNG da un `.drawio` ritoccato in draw.io |
| `scripts/schema_relazionale.py` | schema relazionale |
| `scripts/documentazione.py` | documentazione |
| `scripts/soluzione.py` | soluzione completa in un file solo: HTML (diagramma dentro il file, si stampa o si salva in PDF dal browser), Word, Markdown |
| `references/descrizione.md` | **sempre** prima di scrivere una descrizione: il formato completo, quali righe servono a quale modulo, le regole per un diagramma leggibile |
| `esempi/*.er` | `calciatori.er` (1 a 1, 1 a N, N a N), `compiti.er` (entità debole), `dipendenti.er` (ricorsiva), `veicoli.er` (gerarchia ISA con associazioni «su» e «giù»), `hotel.er` (soluzione completa: ipotesi, tipi, vincoli) |

Servono Python 3 e Pillow (più python-docx per il file Word); per il testo dei PNG lo script usa FreeSans (metriche di Helvetica, il carattere di draw.io) o, se manca, DejaVu Sans o Arial.

## Il processo

1. **Dalla traccia al modello** (se si parte da una traccia). Copia la traccia nel blocco `traccia:` della descrizione, così entra nella soluzione. La progettazione concettuale la fai tu: entità, attributi, chiavi, associazioni con cardinalità, gerarchie. Ogni scelta che la traccia non impone diventa un'**ipotesi aggiuntiva** (riga `ipotesi:`), e i vincoli che il diagramma non può esprimere diventano righe `vincolo:`. Nomi delle entità al singolare anche se la traccia parla al plurale.
2. **La descrizione.** Scrivi il file `.er` (formato in `references/descrizione.md`) con solo le righe che servono ai moduli richiesti; parti dall'esempio più vicino in `esempi/`.
3. **Genera** con lo script del modulo (o `soluzione.py --parti=…`). Leggi NOTE e AVVISI: plurali calcolati, nomi di default delle chiavi esterne nelle ricorsive, lato della chiave esterna in un 1 a 1, strategie sconsigliate, tipi o descrizioni mancanti, nomi che sembrano plurali, linee sul lato degli attributi. Dove una scelta automatica non va, correggi la descrizione (`plurale:`, `chiave esterna:`, `tabella:`, `chiave esterna in:`, `traduzione:`) e rigenera.
4. **Guarda il PNG** con lo strumento di lettura delle immagini prima di consegnarlo: etichette che si toccano, linee su un testo. Correggi posizioni e lati e rigenera.
5. **Consegna** solo i prodotti richiesti (per la soluzione completa l'HTML, o il Word se l'utente vuole ritoccarla prima di darla agli studenti; prima di consegnare un Word convertilo in PDF e guardane le pagine), più il `.er` se l'utente vuole poter rigenerare. Riferisci le scelte fatte (ipotesi, strategie, nomi delle chiavi esterne) in poche righe. Se l'utente ritocca il `.drawio` e lo rimanda, il PNG si rifà con `python3 scripts/drawio_png.py DIAGRAMMA.drawio`; se ci sono forme che lo script non conosce si ferma, e il PNG si esporta da draw.io.

## Con le altre skill

- **Quiz Moodle** (`progettazione-quiz`, `materiali-moodle`): le domande che chiedono di leggere un diagramma usano diagrammi nuovi fatti con il solo modulo diagramma, con contesti diversi da quelli delle pagine di spiegazione. Il PNG va nella cartella delle immagini del quiz e si cita nella traccia con `![testo alternativo](nome.png)` (il testo alternativo descrive entità, associazioni e cardinalità); la descrizione `.er` va nelle note interne della domanda. Per le tracce SQL lo schema si scrive con `--formato=quiz`.
- **Libro** (`libro-sia`): per una figura nuova `--scala=2`; il `.drawio` resta accanto alle immagini per i ritocchi; la documentazione e lo schema in formato libro sono già Markdown.
- **Verifiche su carta e soluzioni**: soluzione completa o solo le parti che servono; per la stampa `--scala=2`.

## Che cosa non fa (ancora)

Le associazioni tra tre entità (ternarie) non sono gestite: se servono, disegna il resto con lo script e aggiungile in draw.io, esportando poi il PNG da draw.io.
