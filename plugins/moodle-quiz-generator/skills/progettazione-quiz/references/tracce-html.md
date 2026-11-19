# Tracce dei quiz di HTML e CSS

Da leggere quando il quiz è di HTML e CSS, già per la scaletta: il risultato nel browser e gli esercizi «dal risultato al codice» decidono anche quali domande ci sono. Fa parte delle regole sulle tracce di `progettazione-quiz` (`SKILL.md`, «Le tracce»): le regole generali (tracce estese, convenzioni, feedback, correzione e note interne) restano lì e valgono anche qui. Le convenzioni generali della traccia (riquadri, scelte, campi Cloze, immagini) sono in `formato-consegna.md`; il formato del campo «Soluzione e test» di queste domande è qui sotto.

## Sito con l'editor (CodeRunner html_con_file, interfaccia html_sito)

Tipologia `sito_html`: lo studente crea dentro la domanda le cartelle e i file del sito (pagine HTML, fogli di stile, script) con l'**editor del sito** (interfaccia `html_sito` di CodeRunner), mette nel sito le immagini fornite dalla domanda e vede l'**anteprima** delle pagine, con i link che funzionano e le immagini che compaiono solo se il percorso è giusto. La risposta è il sito intero, che il template del prototipo `html_con_file` ricrea in una cartella e controlla con gli stessi controlli della consegna con controllo automatico (`tracce-consegna.md`, «I controlli»). Niente file del computer: per questo è la tipologia degli **esercizi di scrittura delle verifiche di HTML e CSS** (dentro Safe Exam Browser). Nelle esercitazioni la consegna dei file resta la «Consegna con controllo automatico» (`consegna_auto`), perché gli studenti devono lavorare con i file del loro computer: il sito con l'editor si usa solo quando l'utente lo chiede creando il quiz, per esempio nell'esercitazione di preparazione alla verifica, così gli studenti vedono l'ambiente della verifica.

- `traccia`: la consegna, estesa ed esplicita come per gli altri esercizi: le pagine e le cartelle che il sito deve avere, il contenuto di ogni pagina, i collegamenti, lo stile. Le **immagini fornite** si mostrano nella traccia con `![testo alternativo](logo.png)`: lo studente le vede e poi le mette nel sito con «+ Immagine»; quelle che la traccia non mostra, lo script le aggiunge in fondo. Nessun campo Cloze né opzione. Nelle verifiche la traccia non dice con che strumento fare le cose (regola delle verifiche), ma può ricordare i pulsanti dell'editor («+ Cartella», «+ File», «+ Immagine», «Sposta»).
- `correzione`: criteri e punti; diventa il **feedback generale** (subito nelle esercitazioni, alla restituzione nelle verifiche).
- **Esercizi a passi** (lo stesso sito che cresce di domanda in domanda): ogni domanda ha il suo sito, e lo studente riparte dal passo prima con «Copia sito» (alla fine del passo) e «Incolla sito» (nella domanda dopo); la traccia lo dice nel primo requisito e nelle indicazioni. Le immagini fornite di un passo si ripetono nelle domande dopo, perché l'anteprima le mostri. Nell'anteprima il pulsante di un modulo non invia i dati: la traccia fa provare le etichette e i menù, non l'invio.
- `coderunner` («Soluzione e test»):

```text
=== options
pagina: index.html
controllo: nascosto
immagini: logo.png, pizza.jpg
aiuti: nessuno
=== test 2
struttura_base()
=== extra
index.html ha la struttura base: html, head con il title, body
=== test 2
cartella_ben_formata(pagine="pagine")
=== extra
I file stanno nelle cartelle giuste: css, img, pagine
=== test 1
usa_pagina("pagine/menu.html")
css_collegato("css/stile.css")
=== extra
menu.html collega il foglio di stile
=== test 2
link_validi("index.html", "pagine/menu.html")
=== extra
Tutti i link e le immagini delle due pagine portano a file che esistono
=== file index.html
<!DOCTYPE html>
<html>
<head>
    <title>Pizzeria Da Mario</title>
    <link rel="stylesheet" href="css/stile.css">
</head>
<body>
    <img src="img/logo.png" alt="Logo della pizzeria">
    <h1>Pizzeria Da Mario</h1>
    <p><a href="pagine/menu.html">Guarda il menu</a></p>
</body>
</html>
=== file pagine/menu.html
…
=== file css/stile.css
h1 {
    color: firebrick;
}
=== immagine img/logo.png
=== immagine img/pizza.jpg
```

- **`=== options`**, tutte facoltative:
  - `pagina`: la pagina principale, da cui partono i controlli (predefinita `index.html`; deve esserci tra i file della soluzione);
  - `controllo: nascosto` (predefinito nelle **verifiche**: niente pulsante Verifica e niente risultati durante il tentativo, il punteggio si calcola alla consegna) oppure `controllo: visibile` (predefinito nelle esercitazioni: lo studente preme Verifica, vede che cosa c'è e che cosa manca e corregge);
  - `immagini`: i nomi delle immagini fornite, separati da virgole. I file stanno nella cartella delle immagini del quiz (come le altre immagini delle tracce): vanno nel testo della domanda e anche tra i file di supporto, così il template controlla le immagini vere;
  - `aiuti`: gli aiuti dell'editor Ace, `nessuno` (predefinito), `tutti`, oppure una lista tra `chiusura` (chiusura automatica di tag e virgolette), `completamento` (proposte di tag e proprietà mentre si scrive), `errori` (errori di sintassi segnati nel margine);
  - `file_pc: sì`: si lavora anche con i file del computer: «Scarica .zip» scarica il sito, «Importa» aggiunge nella cartella selezionata file sciolti (.html, .css, .js, immagini) o il contenuto di uno .zip (i file che ci sono già si sostituiscono solo dopo conferma; i nomi si sistemano in minuscolo, senza spazi né accenti), e «+ Immagine» carica anche immagini dal computer (massimo 500 KB l'una). Per le esercitazioni che si finiscono a casa o che partono da file del computer. Mai nelle verifiche: riapre il file system del PC dentro SEB (la parte 2 si ferma). `carica_immagini: sì` è il nome vecchio della stessa opzione.
- **La soluzione come sito**: `=== file PERCORSO` con il contenuto del file (una sezione per file), `=== immagine PERCORSO` per un'immagine fornita messa nel sito (con un nome diverso: `=== immagine img/marchio.png logo.png`), `=== cartella PERCORSO` per una cartella vuota. Percorsi con lettere minuscole, numeri, `- _ .`, come nell'editor. La soluzione è quella che lo studente vede come risposta giusta; la parte 2 la esegue con i controlli e si ferma se non li supera tutti.
- **`=== test PESO`** con **`=== extra`**: come nella consegna con controllo automatico (`tracce-consegna.md`), un controllo per requisito, il peso mai 0, la frase dell'extra detta in positivo. Le funzioni partono dalla pagina principale; per controllare un'altra pagina si comincia il test con `usa_pagina("pagine/menu.html")`.
- **Niente codice di partenza**: lo studente parte da un sito vuoto (nelle verifiche è la regola; nelle esercitazioni una struttura da completare si dà nella traccia).

In Moodle la domanda è una CodeRunner `html_con_file` personalizzata: interfaccia `html_sito`, nessun allegato, i parametri dell'interfaccia dalle opzioni (aiuti, immagini, caricamento), «Nascondi Verifica» e «Forza nascondi» sul feedback con il controllo nascosto. L'interfaccia `html_sito` va installata una volta sul server Moodle (`interfaccia-html-sito.md` di `materiali-moodle`).

## Esercizi con controllo (CodeRunner css_con_test)

Tipologia `esercizio_controllo`: lo studente scrive il codice nella casella di risposta e i controlli del prototipo `css_con_test` gli dicono che cosa va e che cosa no, con il numero di riga («regola «p» (riga 2): manca il ; dopo «color: blue»»). Sono gli stessi controlli della consegna con controllo automatico (`tracce-consegna.md`, «I controlli»), applicati al testo della casella invece che a un file. Si usa per gli esercizi brevi che il controllo può verificare: scrivere una regola CSS, correggere una regola sbagliata, dare uno stile in linea a un tag, scrivere il `<style>` di una piccola pagina. Quando serve un sito intero (più pagine, cartelle, immagini) si usa il sito con l'editor nelle verifiche e la consegna con controllo automatico nelle esercitazioni.

- `traccia`: la consegna, come per gli altri esercizi (che cosa scrivere, su quali elementi, con quali proprietà). Nessun campo Cloze né opzione.
- `correzione`: diventa il feedback generale (di solito una soluzione commentata o il perché della regola).
- `coderunner` («Soluzione e test»):

```text
=== options
risposta: css
controllo: visibile
=== answer
p {
    color: blue;
    font-size: 18px;
}
=== test 1
css_senza_errori()
=== extra
La regola è scritta senza errori: graffe, due punti, punto e virgola
=== test 2
css_regola("p", "color", "blue")
=== extra
I paragrafi hanno il testo blu
=== test 1
css_regola("p", "font-size")
=== extra
I paragrafi hanno una dimensione del testo
```

- **`=== options`**: `risposta: css` (predefinito: la casella contiene un foglio di stile, che si controlla con `css_senza_errori()` e `css_regola(...)`) oppure `risposta: html` (codice HTML, anche solo un pezzo di pagina: si controlla con le funzioni della pagina, `in_linea(...)`, `in_linea_senza_errori()`, `stile_interno(...)` e le altre); `controllo: visibile` (predefinito: pulsante **Verifica** e tabella dei controlli, lo studente corregge e riprova) oppure `controllo: nascosto` (niente Verifica e niente risultati durante il tentativo, il punteggio si calcola alla consegna, come in una verifica); `righe: N` per l'altezza della casella (predefinite 8 per il CSS, 12 per l'HTML).
- **`=== answer`** obbligatoria: la soluzione di riferimento. La parte 2 la esegue con i controlli e si ferma se non li supera tutti, quindi un controllo sbagliato si scopre prima di Moodle.
- **`=== preload`** facoltativa: il codice già scritto nella casella, per esempio una regola con un errore da correggere (debugging). Mai nelle verifiche (regola delle verifiche di programmazione).
- **`=== test PESO`** con **`=== extra`**: come nella consegna con controllo automatico (`tracce-consegna.md`), un controllo per requisito, il peso mai 0, la frase dell'extra detta in positivo. Il controllo degli errori di scrittura (`css_senza_errori()`, `in_linea_senza_errori()`, `stile_interno_senza_errori()`) va sempre per primo: è quello che spiega perché gli altri non passano.
- **Il valore si confronta come testo**: `css_regola("p", "color", "blue")` non accetta `#0000ff`. Si controlla il valore solo quando la traccia lo impone; altrimenti basta la proprietà.

## Le altre regole

- **Codice indentato**: il codice HTML nelle tracce, nelle correzioni e nelle soluzioni si scrive indentato di 4 spazi, come nei modelli dell'utente: head e body a filo con html, il loro contenuto rientrato, e un livello in più dentro ul, ol, table e tr. Gli spazi arrivano così come sono nella dashboard e in Moodle.
- **Risultato nel browser** (HTML): il risultato si mostra, perché lo studente deve abituarsi a collegare codice e pagina. Nelle pagine di spiegazione lo snippet ha accanto il risultato (```` ```html anteprima ````, con l'etichetta «Nel browser») ogni volta che un tag ha un effetto visibile da capire: per le liste uno snippet per tipo, per le tabelle una tabellina. Negli esempi svolti il codice e sotto il solo risultato; nelle consegne il risultato atteso, anche parziale (una tabella con le prime righe), senza il codice: per entrambi il blocco ```` ```html risultato ````, che in Moodle è un riquadro a forma di finestra con la barra «Visualizzazione nel browser», così la scritta non si confonde con la pagina. Il risultato non serve quando l'output è una semplice scritta o un solo elemento (un paragrafo, un titolo), né per i tag di cui basta dire l'effetto (grassetto, corsivo): serve quando ci sono più elementi (titoli e paragrafi, liste, tabelle). Per i **form** e per le pagine con **immagini** il risultato è una schermata (`![testo alternativo](nome.png)` dentro il blocco ```` ```html risultato ````): nei form perché la pagina del quiz Moodle è già un form e i campi veri si confonderebbero con le risposte, nelle immagini perché i file del sito d'esempio in Moodle non ci sono. Le schermate si fanno con Chromium e Playwright da pagine vere, in italiano (LANG=it_IT.UTF-8) e con un valore nei campi data, così il formato è giorno/mese/anno. Le immagini dei siti d'esempio le disegni tu (illustrazioni semplici, per esempio con Pillow: un logo, uno scaffale, un frutto), mai foto prese dal web né persone; anche un'immagine che non si trova (icona rotta e testo di alt) si mostra così. I **link** nel riquadro si scrivono normali: `da_dashboard.py` li disegna con colore e sottolineatura del browser ma senza indirizzo, così un clic non fa uscire dal quiz. Con le schermate il quiz non si aggiorna in Moodle incollando il testo: le immagini vanno caricate (vedi `aggiornare-quiz.md` di `materiali-moodle`).
- **Dal risultato al codice** (HTML, già dalla prima esercitazione sui tag): domande in cui lo studente vede il risultato e risale al codice che lo produce. Due forme, da scegliere volta per volta secondo quanto conta la lettura del codice: una **risposta multipla** tra codici quasi uguali (di solito quattro, che differiscono per un tag, una chiusura, un annidamento: per letture più complesse), oppure una **Cloze di lettura** del risultato o della schermata (menù e risposte brevi su quali elementi o tipi di campo si vedono: per il riconoscimento semplice). Il risultato è un blocco ```` ```html risultato ````; i codici delle opzioni sono blocchi ```` ```html ````.
- **Figure e schermate nelle pagine di spiegazione** (regola dell'11/11/2026, sostituisce quella del 09/11): la cornice «Visualizzazione nel browser» (blocco ```` ```html risultato ````) si usa **solo per esempi di pagine web**: risultati, schermate di pagine e di form, figure del libro che mostrano una pagina nel browser. Le altre immagini (figure del libro che spiegano un concetto, schemi e diagrammi disegnati apposta) si mettono nel testo come immagini semplici, `![testo alternativo](nome.png)`, senza cornice: così lo studente riconosce sempre che cosa è una pagina vista nel browser. Nelle pagine di teoria conviene usarle: una figura o uno schema dà un appoggio visivo alla spiegazione.
- **Risultato di una pagina con lo stile** (CSS): un `<style>` nel testo di una domanda cambierebbe tutta la pagina del quiz, quindi il risultato si scrive con l'HTML equivalente con lo stile in linea (`<p style="color: blue;">`); lo sfondo di tutta la pagina con un `<div>` colorato intorno al contenuto.
