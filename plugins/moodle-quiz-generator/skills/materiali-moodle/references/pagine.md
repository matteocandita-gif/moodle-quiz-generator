# Le pagine di una lezione

Le pagine servono a ripassare o spiegare prima degli esercizi. Possono essere:

- **descrizioni dentro il quiz** (tipo `description` nella specifica): la scelta abituale per le esercitazioni, perché pagina ed esercizi stanno nello stesso quiz e lo studente li trova in ordine;
- **attività Pagina** o **Area di testo e media** del corso: un file `.html` preparato con `scripts/espandi_html.py`.

Lo stile è quello delle pagine in `stile-html.md`: contenitore, `h1`, sezioni `h2`, riquadri.

## La lezione

Una lezione è divisa in **blocchi** indicati da una lettera (A, B, C, D). Ogni blocco ha la sua pagina e i suoi esercizi.

| Elemento | Nome (esempio) | Contenuto |
|---|---|---|
| apertura | `L5 - 00 - Come lavoriamo oggi` | da dove ripartiamo, l'elenco dei blocchi con una riga ciascuno, il rimando ai siti dimostrativi |
| pagina del blocco | `L5 - B0 - Ripasso: leggere dal database` | teoria ed esempio svolto del blocco |
| esercizi del blocco | `L5 - B1 - …`, `L5 - B2 - …` | nell'ordine in cui vanno svolti |

I nomi seguono sempre lo schema `L<lezione> - <blocco><numero> - <tipo>: <titolo>`. Il tipo dice che cosa fa lo studente: `Ripasso`, `Esercizio`, `Tracciamento`, `Completamento`, `Scrivere`, `Esempio svolto`, `Esempio guidato`, `Debug`, `Trova l'errore`, `Esercizio libero`. Le domande brevi di teoria hanno solo il titolo (`L5 - B2 - Che cosa restituisce mysqli_fetch_array`).

## La pagina «Come lavoriamo oggi»

Breve, senza riquadri:

1. `h1` con il titolo della lezione;
2. un paragrafo: da dove ripartiamo e che cosa aggiungiamo oggi;
3. l'elenco dei blocchi (`<ol>`), ognuno con il titolo in grassetto e una riga di contenuto;
4. dove trovare il materiale: siti dimostrativi da guardare, capitoli del libro.

## La pagina di un blocco

1. `h1`: `Blocco B - titolo`.
2. Un paragrafo di apertura: che cosa fa la pagina o il programma di cui parliamo.
3. Le sezioni `h2` con la teoria: definizioni nei riquadri blu, tabelle di dati, schemi.
4. Riquadro giallo **Esempio svolto**: il codice completo e, sotto, la spiegazione delle righe importanti.
5. Riquadro arancione **N.B.** per le semplificazioni didattiche da dichiarare (per esempio `or die`: «un sito vero gestisce gli errori in un altro modo»).
6. Riquadro giallo **Guardalo in azione**: il rimando alla tappa del sito dimostrativo, con che cosa provare.
7. Riquadro verde **Da rileggere sul manuale**: il capitolo del libro.
8. Riquadro arancione **Prima di andare avanti**: tre domande a cui lo studente deve saper rispondere dopo la lettura.

Non tutte le pagine hanno tutti i riquadri: «Guardalo in azione» solo se esiste una tappa pertinente, «N.B.» solo se c'è qualcosa da dichiarare. L'ordine invece resta questo.

## I siti dimostrativi

- **Il web dietro le quinte** (`https://salvemini.synology.me/webdemo/`): richiesta e risposta, PHP, form GET e POST, PHP e MySQL, divisi in tappe. Rimanda alla tappa precisa quando la pagina tratta lo stesso argomento.
- Un sito analogo per JavaScript è in costruzione: chiedi all'utente l'indirizzo prima di citarlo.

Non inventare indirizzi di tappe: se non conosci quello giusto, chiedilo o rimanda alla pagina principale del sito.

## Esempio di pagina

`assets/modello-pagina.html` è una pagina completa nello stile della skill, con i blocchi `[[codice]]` da espandere: partire da lì è più rapido che scrivere da zero.
