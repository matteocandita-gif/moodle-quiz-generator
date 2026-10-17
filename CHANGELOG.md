# Changelog

Le novità di ogni versione di «Moodle: quiz generator». Le righe segnate **Dashboard** cambiano la pagina «Bozze dei quiz»: Claude propone di aggiornarla, e i quiz salvati restano.

## 0.4.0 — 17/10/2026

La skill **diagrammi-er** diventa la skill della progettazione: dalla stessa descrizione testuale (file `.er`) quattro moduli indipendenti, e si produce solo ciò che serve (per un quiz basta il diagramma).

- **Diagramma**: gerarchie ISA (linea a T con la freccia verso la generalizzazione e la classificazione tra parentesi); attributi delle associazioni anche ai lati del rombo; le posizioni sulla griglia servono solo al diagramma.
- **Schema relazionale** (`schema_relazionale.py`): le regole di traduzione del libro (1 a N, 1 a 1, N a N, entità deboli, ricorsive) e le tre strategie per le gerarchie (tutto su, tutto giù, lasciare tutto), con gli avvisi dove il libro le sconsiglia; formato del libro o delle tracce dei quiz. Nomi delle chiavi esterne con la regola dell'autore: mai un nome generico come Codice o Id ripetuto così com'è (Codice_compagnia, Codice_veicolo).
- **Documentazione** (`documentazione.py`): ipotesi aggiuntive, tabelle delle entità (NOME, SINONIMI, DESCRIZIONE, ATTRIBUTO, TIPO DI DATO, VINCOLI) e delle associazioni (con i vincoli anche qui), vincoli non esprimibili; gerarchie con «Generalizzazione di…» e «Specializzazione di…».
- **Soluzione completa** (`soluzione.py`): traccia, ipotesi, diagramma, documentazione e schema in un file solo, in HTML (predefinito, con il diagramma dentro il file) o in Word; Markdown per il libro. La traccia si scrive nella descrizione, nel blocco `traccia:`.
- Esempi nuovi: `hotel.er` (soluzione completa dalla traccia del libro) e `veicoli.er` (gerarchia con associazioni «su» e «giù»).

## 0.3.9 — 17/10/2026

- Nuova skill **diagrammi-er**: disegna diagrammi E/R nella notazione del libro (entità, associazioni, attributi a pallino, chiave semplice e composta, entità deboli, associazioni ricorsive, cardinalità) da una descrizione testuale breve. Produce il file `.drawio`, da aprire e ritoccare in draw.io, e il PNG; dopo un ritocco il PNG si rifà dal `.drawio` con `drawio_png.py`. Colori fissi per i diagrammi nuovi: entità azzurre, associazioni bianche. Entità al singolare: lo script avvisa quando un nome o il verbo di un'associazione sembrano plurali, e quando una linea arriva sul lato degli attributi. Gerarchie ISA e associazioni tra tre entità non sono ancora gestite.
- `progettazione-quiz` e `materiali-moodle`: le domande e le pagine con un diagramma E/R usano la nuova skill, con la descrizione nelle note interne della domanda.

## 0.3.8 — 17/10/2026

- Immagini nelle tracce: nel testo di pagine e domande si scrive `![testo alternativo](nome.png)` e in Moodle diventa un'immagine, larga al massimo quanto la pagina. Le immagini di un quiz stanno tutte in una cartella, indicata nelle note del quiz e passata alla generazione con `--immagini=CARTELLA`.
- Nuovo `allega_immagini.py`: incorpora le immagini nel Moodle XML e si ferma se ne manca una; `crea_mbz.py` le mette nel backup insieme ai database delle domande SQL e PHP. Provato con un ripristino reale (quiz 5PR, 11 immagini).
- `genera_quiz.py`: una `/` nel nome del quiz (per esempio «E/R») non blocca più la generazione.
- Regola in `progettazione-quiz`: nelle pagine le figure del libro; nelle domande che chiedono di leggere un diagramma, immagini nuove disegnate nello stile del libro, con contesti diversi da quelli delle pagine.
- Nella dashboard le immagini compaiono ancora come testo.

## 0.3.7 — 15/10/2026

- «Consegna di un file»: i tipi di file si scelgono riga per riga, con «tipi: .zip» in === options (per esempio la cartella di un sito compressa); senza, restano .html, .htm e .css.
- Importazione da Moodle: la consegna di un file riporta i suoi tipi di file («tipi: .zip») e il titolo senza il prefisso «Consegna:»; nel confronto «zip» e «.zip» sono lo stesso tipo.
- **Dashboard** 0.3.6: nel Dettaglio la consegna di un file ha il campo «Opzioni della consegna» e il foglio dello studente dice quali file si caricano; nell'anteprima degli snippet i link si vedono come link (senza portare altrove); nei dati del quiz, nella Scaletta, si può cambiare il nome del quiz (quello del menù e dell'attività in Moodle).

## 0.3.6 — 12/10/2026

- Importazione da Moodle (`importa_mbz.py`): gli snippet con l'anteprima accanto tornano nella dashboard come ```` ```html anteprima ```` (prima tornavano come codice, «Nel browser» e un elenco). Nel confronto con la dashboard, negli esercizi HTML e CSS l'ordine delle sezioni di «Soluzione e test» non conta più.

## 0.3.5 — 12/10/2026

- Nomi delle domande in Moodle: se il titolo comincia già con un prefisso («Trova l'errore: …», «Consegna: …», «Esempio svolto: …»), il generatore non lo ripete più.
- Regola in `progettazione-quiz`: il codice HTML di tracce, correzioni e soluzioni si scrive indentato di 4 spazi.
- **Dashboard** 0.3.5: la pagina riapre dove era stata lasciata, nello stesso browser: vista (tutti i quiz, scaletta, dettaglio), quiz, domanda scelta nel dettaglio e posizione di scorrimento.

## 0.3.4 — 12/10/2026

- Snippet HTML con l'anteprima accanto: un blocco ```` ```html anteprima ```` mostra il codice e, a fianco, come lo mostra il browser (nella dashboard e in Moodle). Regola didattica in `progettazione-quiz`: nella pagina di teoria la prima volta che compaiono tag con un effetto da capire (liste, tabelle), mai nell'esempio svolto.
- **Dashboard** 0.3.4: anteprima degli snippet nel Dettaglio.

## 0.3.3 — 12/10/2026

- **Dashboard** 0.3.3: nel Dettaglio l'elenco delle domande non torna più in cima a ogni clic e la domanda scelta resta visibile; l'elenco resta fermo mentre la domanda scorre e occupa tutta l'altezza visibile della finestra (ha una sua barra solo se è più lungo); scegliendo una domanda, la pagina risale all'inizio della domanda.

## 0.3.2 — 12/10/2026

- **Dashboard** 0.3.2: una pagina di spiegazione può stare sulla stessa pagina del quiz di una domanda complessa (per esempio i passi da seguire e la consegna del file): l'avviso «le domande di programmazione stanno su una pagina da sole» conta solo le domande.

## 0.3.1 — 12/10/2026

- Nuova tipologia **Consegna di un file** (`consegna_file`): domanda aperta senza testo, con un file da caricare (.html, .htm, .css). Serve a verificare che gli studenti abbiano creato davvero il file, per esempio la pagina dell'esempio svolto.
- **Dashboard** 0.3.1: la tipologia nel catalogo e nel dettaglio.
- L'importazione da un backup riconosce le domande aperte con solo il file da caricare.

## 0.3.0 — 12/10/2026

- **Dashboard** 0.3.0: scelta «Esercizi HTML» nei dati del quiz e nel modulo «Nuovo quiz» (con linguaggio HTML e CSS): **con anteprima** (prototipo `php_con_test`, con l'area di prova) o **senza anteprima** (prototipo `html`: il campo serve solo a incollare il codice scritto nell'editor e provato nel browser). Il dettaglio mostra il prototipo scelto.
- La generazione del quiz usa il prototipo scelto (campo `prototipoHtml`); senza scelta resta `php_con_test`.
- L'importazione da un backup riconosce gli esercizi HTML con il prototipo `html` e imposta il quiz «senza anteprima».

## 0.2.0 — 12/10/2026

- **Dashboard** 0.2.0: nel modulo «Nuovo quiz» il primo tipo è «Libero (senza preset)», senza regole su tipi, quantità, punti e tempi, con la scelta del comportamento in Moodle (esercitazione o verifica).
- **Dashboard**: riquadro «Come scegliere il tipo di quiz» con la descrizione di ogni tipo.
- **Dashboard**: lezione o codice facoltativi; se mancano, il quiz riceve un codice di tre caratteri che comincia con la classe (per esempio 4K7).
- Un codice che comincia con una cifra non è più preso per un numero di lezione: «Lezione N» solo per i numeri.

## 0.1.1 — 12/10/2026

- Claude risponde sempre in italiano, anche quando un comando o una skill si avvia dal menù (l'app aggiunge da sola una frase in inglese).

## 0.1.0 — 12/10/2026

Prima versione del plugin, nata dalle skill usate finora a scuola.

- Sette skill: `progettazione-quiz`, `materiali-moodle`, `verifiche-programmazione`, `domande-coderunner-js`, `domande-coderunner-sql`, `domande-php-mysqli-mock`, `database-didattici`.
- Comando `installa-dashboard`: pubblica la dashboard dell'utente, crea l'attività programmata che avvia i quiz, salva le impostazioni; aggiorna una dashboard esistente senza toccare i quiz.
- **Dashboard** 0.1.0: l'avvio dei quiz legge l'attività dalle impostazioni della pagina (riquadro «Impostazioni» nella vista iniziale); benvenuto al primo avvio; tipo «Importato da Moodle» per i quiz portati da un backup.
- Importazione di un quiz da un backup `.mbz` e confronto tra un backup e la dashboard, per riportare le correzioni fatte in Moodle.
- Catalogo dei database didattici dentro il plugin (biblioteca, palestra, cinema, veterinario, in tre taglie); ogni utente ha la sua pagina «Database didattici» per quelli che crea.
