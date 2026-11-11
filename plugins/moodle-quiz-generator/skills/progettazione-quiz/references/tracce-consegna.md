# Consegne con controllo automatico

Da leggere quando un'esercitazione chiede di consegnare file (una pagina, la cartella di un sito), già per la scaletta. Fa parte delle regole sulle tracce di `progettazione-quiz` (`SKILL.md`, «Le tracce»): le regole generali restano lì e valgono anche qui; quelle degli esercizi HTML e CSS sono in `tracce-html.md`.

## Quando si usa

- **Nelle esercitazioni ogni consegna di file** è una «Consegna con controllo automatico» (`consegna_auto`): lo studente carica il file, preme **Controlla** e vede, controllo per controllo, che cosa c'è e che cosa manca; può correggere e ricaricare quante volte vuole, e il voto arriva alla consegna. La «Consegna di un file» (`consegna_file`, domanda aperta a correzione manuale) resta per le verifiche.
- **«Esercizio HTML» ed «Esercizio CSS»** (codice scritto nella casella della domanda) restano per gli esercizi brevi su un tag o un costrutto. La consegna con controllo si usa quando lo studente crea o modifica file veri, con Notepad++ e nella cartella del sito.
- **La prima volta** che una classe consegna una cartella, conviene una consegna piccola dello scheletro (cartella, pagine con il solo titolo) prima della consegna finale: imparano a comprimere e caricare su un lavoro breve, e gli errori di cartella e di nomi escono subito invece che alla fine (HTML3, «Preparate la cartella del sito»).
- **Controllato non vuol dire corretto**: i controlli dicono se nei file c'è quello che cercano, non come appare la pagina nel browser né se i testi hanno senso. Lo dice allo studente il promemoria del prototipo, sopra il riquadro di caricamento: non va ripetuto nella traccia.

## Il file da consegnare

- **Un solo file**, con il nome fissato nella riga: una pagina (`index.html`) o la cartella del sito compressa (`sito-scuola.zip`). Nei nomi solo lettere minuscole, numeri, `-`, `_` e il punto: niente spazi, accenti o parentesi, che CodeRunner rifiuta comunque.
- **Lo .zip ha il nome della cartella**: comprimendo la cartella `sito-scuola`, Windows crea da solo `sito-scuola.zip` («Comprimi in file ZIP», oppure «Invia a» e «Cartella compressa»). Prima di comprimere di nuovo si cancella il vecchio `.zip`, altrimenti Windows crea `sito-scuola (1).zip`, che viene rifiutato.
- **Cartelle del sito**: `css` per i fogli di stile, `img` per le immagini, `js` per gli script; le pagine secondarie in una cartella propria quando la consegna lo chiede (per esempio `pagine`).

## La traccia

- Che cosa deve contenere il file: requisiti numerati, con in grassetto la parola chiave di ognuno; la struttura della cartella in un blocco ```` ```text ````; il risultato atteso nel riquadro «Visualizzazione nel browser» quando ha più elementi (`tracce-html.md`).
- Le indicazioni di consegna: come si comprime la cartella, il nome esatto del file, **Controlla**, si può correggere e ricaricare. Se la stessa cartella è già stata consegnata in una domanda precedente, ricorda di cancellare il vecchio `.zip`.
- Nessun campo Cloze né opzione: la domanda non ha la casella di risposta, solo il riquadro per caricare il file. Su una pagina del quiz da sola, al massimo con la pagina che la introduce.
- «Come lavoriamo oggi» dice quante consegne ci sono, il nome del file e che si può ricaricare.

## «Soluzione e test»

```text
=== options
nome: sito-scuola.zip
pagina: index.html
=== test 2
cartella_ben_formata(pagine="pagine")
=== extra
La cartella sito-scuola è in ordine: le pagine in pagine/, niente file estranei
=== test 4
link_a("pagine/orari.html")
=== extra
Il menu di index.html ha il link a orari.html
=== test 2
usa_pagina("pagine/orari.html")
link_a("index.html")
=== extra
orari.html ha il link per tornare a index.html
```

- **`=== options`**: `nome` (obbligatorio) è il file che lo studente carica, `.html` o `.zip`. `pagina` (facoltativo, solo con lo `.zip`) è la pagina principale, `index.html` se manca: la cartella in cui si trova è la **cartella del sito**, da cui partono tutti i percorsi scritti nei controlli.
- **`=== test PESO`**: un controllo, cioè una funzione dell'elenco qui sotto; per controllare un'altra pagina del sito, `usa_pagina(...)` su una riga e la funzione sulla riga dopo. Il peso dice quanto vale il controllo rispetto agli altri: la domanda vale i punti della riga, divisi tra i controlli in proporzione ai pesi. Si usano pesi che seguono i criteri della correzione (per esempio i punti di ogni criterio). **Il peso non è mai 0**: con 0 Moodle va in errore quando mostra i risultati («Division by zero»). Un controllo che deve solo dare il messaggio (per esempio `link_validi`) ha peso `0.001`.
- **`=== extra`** dopo ogni test, obbligatorio: la frase che lo studente legge nella colonna «Controllo», il requisito detto in positivo («Il menu di index.html ha il link a orari.html»). L'esito, «OK» o il problema trovato, lo scrive il controllo.
- **Un controllo per requisito**, così chi sbaglia una cosa perde solo quel controllo. Un nome di file sbagliato o una cartella mancante si ripetono in tutti i controlli che li usano: per questo cartella e nomi hanno i loro controlli, all'inizio.
- **`correzione`**: la soluzione di riferimento, che diventa il feedback generale (lo studente la vede nella revisione). I criteri e la corrispondenza tra criteri e controlli vanno nelle note interne.

## I controlli

I controlli leggono i file consegnati, non li eseguono e non guardano la pagina nel browser. Ogni test riparte dalla pagina principale. I messaggi, in italiano e con il numero di riga, dicono che cosa non va anche quando il problema vero è un altro (un `src` che porta a `img/Logo.png` mentre il file si chiama `img/logo.png`, un foglio di stile che non si apre perché il percorso è sbagliato).

<!-- funzioni-html-con-file: inizio (si rigenera con sviluppo/prototipo-html-con-file/crea_prototipo.py: non modificarla a mano) -->
**La pagina HTML**

| Test | Che cosa controlla |
|---|---|
| `struttura_base()` | La pagina ha `html`, `head` con un `title` non vuoto, `body`; il head viene prima del body e nessun elemento della pagina sta fuori dal body. |
| `tag_chiusi()` | Ogni tag aperto è chiuso, nell'ordine giusto. Indica la riga. |
| `presente("hr")` | C'è almeno un elemento del tipo indicato. |
| `almeno(3, "li", dentro="ul")` | Ci sono almeno n elementi; con dentro= contano solo quelli contenuti nel tag indicato. |
| `esattamente(1, "h1")` | Ci sono esattamente n elementi (anche con dentro=). |
| `attributo("input", "type", "email")` | Almeno un elemento ha l'attributo; se si indica il valore, con quel valore (maiuscole non contano). |
| `tutti_con_attributo("img", "alt")` | Tutti gli elementi del tipo hanno l'attributo non vuoto; se nella pagina non ce n'è nessuno, il controllo non passa. |
| `testo("h1", "Libreria Pagina 42")` | Almeno un elemento contiene il testo (maiuscole e spazi non contano). |
| `struttura_come_soluzione()` | La sequenza dei tag è la stessa della soluzione scritta nella risposta della domanda (nella dashboard la sezione === answer); il testo non conta, div, span, br, hr sono ignorati, i valori di action, method, id, for, placeholder, alt sono liberi. È il confronto del prototipo html_test_semantica, ridotto al primo punto diverso. |

**La cartella del sito e i collegamenti**

| Test | Che cosa controlla |
|---|---|
| `cartella_ben_formata()` | Tutti i file stanno nella cartella del sito; i .css nella cartella `css`, le immagini in `img`, i .js in `js` (anche in sottocartelle); nessun file estraneo (.txt, .docx…). Thumbs.db e desktop.ini si ignorano. Domanda per domanda si può chiedere un'altra struttura: `cartella_ben_formata(img="immagini", css="risorse/css")`; con `pagine="pagine"` le pagine diverse dalla principale devono stare nella cartella `pagine`; per non controllare un tipo di file: `js=None`. |
| `nomi_file_corretti()` | Nomi di file e cartelle del sito solo con lettere minuscole senza accento, numeri, - e _: niente spazi. |
| `file_presente("img/logo.png")` | Nella cartella del sito c'è il file. |
| `immagine("img/logo.png")` | Un `img` della pagina mostra quel file. Se il percorso è sbagliato, il messaggio dice perché. |
| `link_a("pagine/contatti.html")` | Un link della pagina porta a quel file. |
| `ancore_valide(2)` | Almeno n link a un punto della pagina (`href="#id"`), ognuno verso un id che esiste, e nessun id ripetuto. Segnala anche `href="id"` senza cancelletto. |
| `link_esterno(nuova_scheda=True)` | C'è un link a un altro sito con l'indirizzo completo (`https://`); con nuova_scheda=True anche `target="_blank"`. Segnala gli indirizzi che cominciano con www senza https://. |
| `uno_tra("p", "ul", "ol")` | C'è almeno un elemento di uno dei tipi indicati (per esempio un paragrafo oppure una lista). |
| `link_validi("index.html", "pagine/contatti.html")` | Ogni href e src relativo delle pagine indicate (link, immagini, CSS, script) porta a un file consegnato; senza argomenti la pagina principale. Segnala maiuscole sbagliate, \ al posto di /, percorsi del PC, percorsi che iniziano con /. |
| `usa_pagina("pagine/contatti.html")` | Da scrivere su una riga prima della funzione di controllo: il controllo si fa su un'altra pagina del sito. Ogni test riparte dalla pagina principale. |

**Il CSS**

| Test | Che cosa controlla |
|---|---|
| `css_collegato("css/stile.css")` | La pagina collega quel foglio di stile con `<link rel="stylesheet">` dentro il head. |
| `css_senza_errori()` | Nei fogli collegati non ci sono errori di scrittura: graffe mancanti o in più, dichiarazioni senza i due punti, ; mancante tra due dichiarazioni, commenti non chiusi. |
| `css_regola("h1", "color")` | C'è una regola per il selettore; se indicate, con la proprietà e con il valore (`css_regola("h1", "color", "red")`). Il selettore si scrive come nel CSS (`"nav a"`, `".evidenza"`); conta anche dentro un gruppo (`h1, h2`) o un @media. Una dichiarazione scritta male non conta, come nel browser. Il valore si confronta come testo: `red` e `#ff0000` sono diversi, quindi conviene controllare il valore solo quando la consegna lo impone. |
| `classe("evidenza")` | La classe è usata da un elemento della pagina ed è definita nel CSS. |
| `classi_coerenti()` | Ogni classe usata nelle pagine indicate (senza argomenti la principale) è definita nel CSS e viceversa: trova i nomi scritti in modo diverso. |
| `nessuno_stile_interno()` | Niente `<style>` nella pagina e niente attributi style: tutto lo stile sta nel file CSS. |

**Il CSS nella pagina: `<style>` e attributo style**

| Test | Che cosa controlla |
|---|---|
| `stile_interno()` | C'è un `<style>` con almeno una regola, dentro il head. |
| `stile_interno_senza_errori()` | Nelle regole scritte nel `<style>` della pagina non ci sono errori di scrittura (gli stessi di `css_senza_errori()`), con la riga della pagina. |
| `stile_interno_regola("h1", "color")` | Come `css_regola`, ma sulle regole scritte nel `<style>` della pagina. |
| `in_linea_senza_errori()` | Gli attributi style della pagina sono scritti bene: `proprietà: valore` separate da ;, senza graffe. |
| `in_linea("p", "color")` | Un elemento del tipo indicato ha l'attributo style; se indicate, con la proprietà e con il valore (`in_linea("p", "color", "green")`). |

**Il JavaScript**

| Test | Che cosa controlla |
|---|---|
| `js_collegato("js/script.js")` | La pagina collega quello script con `<script src="…">`, vuoto. |
| `js_caricato_dopo_la_pagina()` | Gli script collegati partono dopo il caricamento della pagina: in fondo al body, oppure nel head con `defer`. Da usare se lo insegni così. |
| `js_senza_errori()` | Errori di sintassi negli script della pagina (file collegati e script interni), con la riga e il messaggio in italiano. Usa `node --check` su Jobe; se node non parte, un controllo più semplice di parentesi, graffe e virgolette. |
| `js_funzione("mostraOrari")` | C'è una funzione con quel nome: `function nome(…)`, `const nome = function` o a freccia. Segnala lo stesso nome con le maiuscole diverse. |
| `js_contiene("addEventListener")` | Il codice contiene il testo, senza contare i commenti. Con `messaggio="…"` si sceglie la frase che lo studente vede se manca. |
| `id_coerenti()` | Ogni id cercato con `getElementById` o `querySelector` con # esiste nella pagina: l'errore che lo studente vede solo come «non succede niente». |
| `nessuno_script_interno()` | Niente codice dentro `<script>` nella pagina e niente attributi `onclick`, `onload`…: tutto sta nel file .js. |
| `diagnosi_node()` | Solo per il docente, in una domanda di prova: dice se node funziona su Jobe. |
<!-- funzioni-html-con-file: fine -->

## Il prototipo in Moodle

Le domande usano il prototipo CodeRunner `html_con_file`, che deve essere installato nel Moodle una volta: lo dice `righe-coderunner.md` di `materiali-moodle`, che genera le domande.
