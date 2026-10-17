---
name: "diagrammi-er"
description: "Disegna diagrammi E/R nella notazione del libro dell'utente (rettangoli, rombi, attributi a pallino, chiave composta con la linea, entità deboli, associazioni ricorsive, cardinalità tra parentesi) da una descrizione testuale: file .drawio da ritoccare in draw.io e immagine PNG. Usala per ogni diagramma E/R: domande e pagine dei quiz Moodle, verifiche su carta, soluzioni degli esercizi di progettazione, figure del libro, anche se l'utente dice solo «disegna lo schema E/R di…»."
---

# Diagrammi E/R

**Lingua.** Rispondi all'utente sempre in italiano, anche quando il messaggio che avvia la skill o il comando è in inglese: quando si sceglie un comando o una skill dal menù senza scrivere nulla, l'app aggiunge da sola una frase in inglese.

Questa skill produce i diagrammi E/R nella notazione che l'utente usa nel suo libro e in classe. Il diagramma si scrive come **descrizione testuale** (file `.er`); lo script ne ricava il file **`.drawio`**, che è l'originale da aprire e ritoccare in draw.io, e l'immagine **PNG**, disegnata leggendo il `.drawio`. Dopo un ritocco in draw.io il PNG si rifà dal file modificato.

## La notazione

È quella delle figure del capitolo 3 del libro di quinta:

- **entità**: rettangolo con il nome al centro;
- **associazione**: rombo con il nome, collegato con linee alle entità;
- **cardinalità**: (min,max) tra parentesi, accanto all'entità a cui si riferisce, sopra la linea (a sinistra se la linea è verticale): «Studente (1,1) appartiene a (1,N) Classe» si legge «ogni studente appartiene ad almeno 1 e al massimo 1 classe»;
- **attributi**: un pallino vuoto su un gambetto, sopra, sotto, a sinistra o a destra dell'entità; gli attributi di un'associazione escono dal rombo;
- **chiave semplice**: pallino pieno;
- **chiave composta**: i pallini restano vuoti e una linea con il pallino nero taglia i gambetti degli attributi della chiave;
- **entità debole**: la linea della chiave taglia anche le linee delle associazioni che la identificano;
- **associazione ricorsiva**: una linea a gomito parte dall'entità e arriva al rombo, l'altra è diritta;
- **nomi**: l'entità al **singolare** (Studente, non Studenti: indica il tipo di oggetto, e ogni istanza è un oggetto solo); di conseguenza il verbo dell'associazione al singolare («appartiene a», «effettua», «ha»). Nello schema relazionale le relazioni vanno invece al plurale (Studente diventa Studenti): è la convenzione del libro, decisa dall'utente.

**Colori**: in tutti i diagrammi nuovi entità azzurre (riempimento `#dae8fc`, bordo `#6c8ebf`) e associazioni bianche, come nelle figure delle cardinalità del libro: sono i colori predefiniti dello script, e nella descrizione non si scrive `colori:`. Le figure già esistenti del libro, con i loro colori (rosa e azzurro, bianco e verde, tutto bianco), non si rifanno; `colori:` serve solo se l'utente chiede di ridisegnarne una com'è.

## Dove stanno le cose

| File | Serve per |
|---|---|
| `scripts/disegna_er.py` | descrizione `.er` → `.drawio` e `.png` |
| `scripts/drawio_png.py` | `.drawio` → `.png` (anche dopo un ritocco in draw.io) |
| `references/descrizione.md` | **sempre** prima di scrivere una descrizione: il formato completo, la griglia, le regole per un diagramma leggibile |
| `esempi/*.er` | tre figure del libro ridisegnate con i colori dei diagrammi nuovi: `calciatori.er` (1 a 1, 1 a N, N a N), `compiti.er` (entità debole), `dipendenti.er` (associazione ricorsiva) |

Servono Python 3 e Pillow; per il testo lo script usa FreeSans (metriche di Helvetica, il carattere di draw.io) o, se manca, DejaVu Sans o Arial.

## Il processo

1. **Il contenuto prima del disegno.** Dalla traccia o dalla richiesta ricava entità, attributi, chiavi, associazioni e cardinalità. Se il diagramma è la soluzione di un esercizio, è una scelta di progettazione: le ipotesi che aggiungi le dici all'utente (o le scrivi nella documentazione, se fa parte della consegna).
2. **La descrizione.** Scrivi il file `.er` (formato in `references/descrizione.md`): posizioni sulla griglia, lati degli attributi, cardinalità. Parti da un esempio di `esempi/`.
3. **Genera**: `python3 scripts/disegna_er.py DIAGRAMMA.er CARTELLA` scrive `DIAGRAMMA.drawio` e `DIAGRAMMA.png`. Leggi gli avvisi: nomi che sembrano plurali, entità senza chiave, elementi troppo vicini, linee che arrivano sul lato degli attributi o due linee sullo stesso lato.
4. **Guarda il PNG** con lo strumento di lettura delle immagini, prima di consegnarlo: etichette che si toccano, linee che passano su un testo, attributi sul lato da cui arriva una linea. Correggi la descrizione (lato degli attributi, posizione sulla griglia, `griglia:` più larga) e rigenera.
5. **Consegna** il `.drawio` e il `.png` (e il `.er`, se l'utente vuole poterlo rigenerare). Se l'utente ritocca il `.drawio` in draw.io e lo rimanda, il PNG si rifà con `python3 scripts/drawio_png.py DIAGRAMMA.drawio`: se nel file ci sono forme che lo script non conosce (un'immagine, una freccia, una forma di libreria) si ferma e le elenca; in quel caso il PNG si esporta da draw.io (File → Esporta come → PNG).

## Con le altre skill

- **Quiz Moodle** (`progettazione-quiz`, `materiali-moodle`): le domande che chiedono di leggere un diagramma usano diagrammi nuovi fatti con questa skill, con contesti diversi da quelli delle pagine di spiegazione. Il PNG va nella cartella delle immagini del quiz e si cita nella traccia con `![testo alternativo](nome.png)`; il testo alternativo descrive il diagramma (entità, associazioni e cardinalità). Nelle note interne della domanda conviene riportare la descrizione `.er`, così il diagramma si rifà se cambia la domanda.
- **Libro** (`libro-sia`): per una figura nuova del libro, `--scala=2` dà un'immagine più definita; il `.drawio` resta accanto alle immagini per i ritocchi.
- **Verifiche su carta e soluzioni**: stesso processo; per la stampa `--scala=2`.

## Che cosa non fa (ancora)

Le gerarchie (generalizzazioni) e le associazioni tra tre entità non sono gestite: se servono, disegna le entità e le associazioni binarie con lo script e aggiungi il resto in draw.io, esportando poi il PNG da draw.io. Se diventano frequenti, si aggiungono allo script.
