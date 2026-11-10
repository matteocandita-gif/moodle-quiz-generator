# Formato di consegna: dalla dashboard a Moodle

La parte 2 non riceve un file a parte: legge il database della dashboard «Bozze dei quiz». Tutto quello che va in Moodle è scritto nelle righe con le convenzioni qui sotto, e `da_dashboard.py` lo trasforma senza ritrascrizioni:

```
ArtifactData get   quiz <id>          out_dir=EXPORT     (quiz)
ArtifactData list  quiz/<id>/domande  out_dir=EXPORT     (righe)
ArtifactData get   impostazioni depositi  out_dir=EXPORT  (solo se il quiz ha «deposito»)
ArtifactData get   impostazioni pdp       out_dir=EXPORT  (solo per la copia PDP: genera_quiz.py … --pdp)
python3 genera_quiz.py EXPORT <id> USCITA --nome="<nome del file>" [--varianti=a] [--immagini=CARTELLA]
```

`--varianti=a` (o `a,b`) converte solo le varianti indicate delle verifiche ripetibili: si usa quando la variante a è completa e le altre hanno solo la sintesi (si fanno dopo, quando l'utente le chiede). Le righe senza tag restano tutte; lo script elenca le righe lasciate fuori.

`genera_quiz.py` esegue in fila, fermandosi al primo errore:
1. `da_dashboard.py` → `specifica.txt`, `specifica-js.txt` (righe CodeRunner JavaScript), `specifica-sql.txt` (righe CodeRunner SQL, con i database del quiz), `specifica-php.txt` (righe CodeRunner PHP, con i database del quiz), `impaginazione.json`;
2. `crea_xml.py` → le domande non CodeRunner;
3. `crea_xml.py` di `domande-coderunner-js` → le domande CodeRunner JavaScript (gli output attesi li calcola Node);
   `crea_xml.py` di `domande-coderunner-sql` → le domande CodeRunner SQL (costruisce i file SQLite, calcola gli output e allega il database a ogni domanda);
   `php_attesi.py` e `crea_xml.py --verifica` di `domande-php-mysqli-mock` → le domande CodeRunner PHP (gli output attesi si calcolano eseguendo la soluzione con PHP e il template del prototipo; se manca il client `sqlite3` lo sostituisce `sqlite3_cli.py`);
   (esercizi HTML e CSS e corrispondenze li scrive direttamente `da_dashboard.py` in `domande-dirette.xml`);
4. `unisci_xml.py` → `<nome>.xml`;
5. `controlla_xml.py`;
6. `crea_mbz.py` → `<nome>.mbz`.

Tutti gli script stanno in `scripts/` di `materiali-moodle`; le cartelle `scripts/` di `domande-coderunner-js`, `domande-coderunner-sql` e `domande-php-mysqli-mock` le cerca da solo accanto a quella skill (o `--js=`, `--sql=`, `--php=CARTELLA`). Tutti i tipi di domanda del catalogo arrivano all'XML e all'`.mbz`.

Lo script si ferma con l'elenco delle righe che non rispettano le convenzioni; la dashboard segnala gli stessi problemi negli avvisi, già in parte 1. Le righe non approvate producono solo un avviso.

## Campi di una riga

| Campo | Va in Moodle | Contenuto |
|---|---|---|
| `traccia` | sì | quello che vede lo studente, in Markdown con le convenzioni sotto |
| `correzione` | sì | domande aperte: indicazioni per chi corregge (criteri, mezzo punto, soluzione); altre domande: feedback generale |
| `coderunner` | sì | solo domande CodeRunner: soluzione, codice di partenza e test (sotto) |
| `tag` | sì | solo verifiche ripetibili: il tag della posizione; le righe con lo stesso tag sono varianti (sotto) |
| `docente` | no | note interne: il ragionamento sulla domanda; nelle verifiche, per gli esercizi CodeRunner, in fondo la riga `Griglia:` con i punti parziali |
| `nota` | no | spiegazione di una modifica «da rivedere» |
| `sezione`, `pag`, `punti`, `pos`, `titolo`, `tipologia` | sì | sezione del quiz, pagina, punti nel quiz, nome della domanda, tipo Moodle |

Quiz: `database` (solo con domande SQL, vedi sotto); `lezione` e `argomento` danno la categoria («Lezione N - argomento») e i nomi («LN - pos - prefisso: titolo»); le verifiche non hanno un numero di lezione e `lezione` è il loro codice (`V5R`): categoria «V5R - argomento», nomi «V5R - pos - prefisso: titolo»; `tipoQuiz` sceglie le impostazioni dell'.mbz (V e VT: verifica, con il tempo del quiz; SD: studio, con il tempo del quiz e la navigazione sequenziale; gli altri, compreso EDT: esercitazione). Facoltativi: `navigazione`, `feedback`, `seb` e `password` (le impostazioni avanzate, in `dashboard.md`: quando mancano decide il tipo di quiz), `titoliSezioni` (titolo della sezione nel quiz, se diverso dal nome della sezione), `nomeQuiz`, `voto` (10), `sufficienza` (6).

## Convenzioni della traccia

- Markdown: paragrafi (ogni a capo dentro un paragrafo resta un a capo, `<br>`; la riga vuota apre un nuovo paragrafo: così lo schema relazionale si scrive una relazione per riga, senza righe vuote in mezzo), `**grassetto**`, `*corsivo*`, `__sottolineato__` (la chiave primaria negli schemi delle tabelle), `` `codice` ``, blocchi di codice tra tre apici inversi con il linguaggio (```` ```html ````; con ```` ```html anteprima ```` accanto al codice compare il risultato nel browser, l'HTML stesso interpretato: solo per snippet brevi di tag della lezione, senza script né stili; con ```` ```html risultato ```` compare il solo risultato, senza il codice, in un riquadro a forma di finestra del browser con la barra «Visualizzazione nel browser»: per esempi svolti, consegne ed esercizi «dal risultato al codice», solo quando l'output ha più elementi; dentro può esserci anche una sola immagine, `![testo alternativo](nome.png)`, per le schermate dei form; per ```` ```js leggere ```` e ```` ```js esempio ```` vedi «Codice da leggere» sotto), elenchi `-` e `1.`, tabelle con `|`, titoli `#` e `##`.
- **Immagini**: `![testo alternativo](nome.png)`, anche in una riga a sé o dentro un riquadro, solo nel testo della domanda o della pagina (non nelle opzioni, nei feedback, nella correzione né nei campi Cloze). Si scrive solo il nome del file, senza cartella: le immagini di un quiz stanno tutte in una cartella, indicata nelle `note` del quiz e passata a `genera_quiz.py --immagini=CARTELLA`. Il testo alternativo descrive l'immagine. `da_dashboard.py` la scrive come `<img src="@@PLUGINFILE@@/nome.png">` (larghezza al massimo quella della pagina), `allega_immagini.py` incorpora il file nell'XML e `crea_mbz.py` lo mette nel backup. Nella dashboard l'immagine compare come testo (dentro un blocco ```` ```html risultato ```` come «Schermata nome.png»). I diagrammi E/R delle domande si fanno con la skill `diagrammi-er`, con contesti diversi da quelli delle pagine.
- **Pagine** (tipologie della famiglia «Pagine»): scritte già nella forma finale, in seconda persona plurale. `#` è il titolo della pagina. Riquadri:
  ```
  :::giallo Esempio svolto
  Testo del riquadro, anche con codice.
  :::
  ```
  Colori: blu (definizioni), giallo (esempi svolti), verde, arancio (N.B.), rosso.
- **Scelte** (risposta multipla, vero/falso, risposta breve): un gruppo di righe, una per opzione.
  ```
  (x) risposta giusta
      > feedback della risposta
  ( ) risposta sbagliata
      > feedback
  ```
  Più risposte giuste: `[x]` e `[ ]`; le giuste si dividono il 100% e le sbagliate senza percentuale si dividono una penalità del −100% (con tre sbagliate −33.33333 ciascuna), così chi spunta tutto prende 0. Percentuali esplicite: `[x 50%]`, penalità `[ -50%]`. Le penalità devono sommare −100%: se ne scrivi qualcuna a mano, le sbagliate senza percentuale si dividono quello che manca (lo script si ferma se la somma non torna). La traccia dice «Seleziona tutte le risposte corrette» (l'istruzione standard di Moodle è nascosta). Vero/falso: due opzioni «Vero» e «Falso». Risposta breve: una sola `(x)`, la risposta giusta (si usa solo quando la risposta è una e senza varianti); gli errori prevedibili si scrivono come `( )` con il loro feedback. Non si usa `( ) *` («qualsiasi altra risposta»): nella dashboard sembra un'opzione e non si capisce (lo script la accetta ancora, per le domande vecchie).
- **Corrispondenza**: una riga per coppia, `elemento <-> corrispondenza`; una riga che comincia con `<->`, senza elemento, è una risposta in più che non corrisponde a niente. Il testo fuori dalle righe `<->` è la consegna.
  ```
  `color` <-> Cambia il colore del testo
  `font-size` <-> Cambia la dimensione del carattere
  `text-align` <-> Sposta il testo a sinistra, al centro o a destra
  <-> Cambia la distanza tra una riga e l'altra
  ```
  Almeno 2 elementi e almeno 3 corrispondenze in tutto (regola di Moodle). A sinistra il testo in linea (`` `codice` ``, grassetto); a destra solo testo semplice, perché compare in un menù a tendina. Le corrispondenze si mescolano; la `correzione` diventa il feedback generale; i feedback standard («Risposta corretta.» …) e il numero di risposte giuste sono quelli delle domande dell'utente.
- **Codice da leggere** (non eseguibile): nella traccia delle domande di lettura (`teoria_aperta`, `debug_motivazione`, `tracciamento`, `lettura_output`, `trova_errore`) i blocchi JavaScript, PHP, SQL e HTML diventano da soli non eseguibili: la parte 2 (`da_dashboard.py`) li marca e il `<pre>` esce identico, con gli stessi colori, ma con alcuni caratteri sosia (lettere cirilliche nelle parole chiave, spazi a larghezza zero dopo gli operatori), circa uno per riga, ciascuno controllato con l'interprete perché da solo blocchi l'esecuzione. Copiato in una domanda CodeRunner o nella console, il codice dà un errore. In HTML c'è uno spazio a larghezza zero nel nome di ogni tag: copiato nell'anteprima o in un file, il browser non riconosce i tag e mostra solo il testo, senza errori. Marcatori sul blocco, da scrivere solo nei casi particolari: ```` ```js leggere ```` per un codice da leggere in un'altra tipologia (per esempio una risposta multipla «che cosa stampa questo codice?»); ```` ```js esempio ```` per un codice di riferimento dentro una domanda di lettura, che gli studenti devono poter copiare e usare. La `correzione`, le pagine, gli esempi svolti e i feedback non si toccano mai. Nella dashboard il codice si vede normale.
- **Campi Cloze**: nella sintassi di Moodle, dentro il testo o dentro i blocchi di codice: `<{1:SHORTANSWER:=h1}>`, `{1:MULTICHOICE_S:=giusta#Feedback~sbagliata#Feedback}`, `{1:NUMERICAL:=4:0#Feedback}`. Si escapano solo `}` `#` `~`; nei campi a risposta niente tag (il campo contiene il nome del tag, parentesi e barra stanno nel codice). Il peso dei campi è il numero prima dei due punti; nel quiz contano i punti della riga.

## Domande CodeRunner ed esercizi HTML e CSS

Il formato del campo «Soluzione e test» e le regole di ogni linguaggio stanno in un file per linguaggio, da leggere solo se il quiz lo riguarda: `tracce-javascript.md` («Domande CodeRunner JavaScript»), `tracce-sql.md` («Domande CodeRunner SQL», con il database del quiz), `tracce-php.md` («Domande CodeRunner PHP»), `tracce-html.md` («Esercizi HTML e CSS»).

## Consegna di un file

Tipologia `consegna_file`: domanda aperta (essay) senza campo di testo, con un solo file da caricare, obbligatorio, di tipo `.html`, `.htm` o `.css` (le impostazioni le mette `da_dashboard.py`). `traccia`: il file da preparare, con il nome e i requisiti, e come caricarlo; `correzione`: i criteri per chi corregge (in Moodle le informazioni per chi corregge). Si usa nelle verifiche, per verificare che lo studente abbia creato davvero un file. Nelle esercitazioni ogni consegna di file è invece una «Consegna con controllo automatico» (`consegna_auto`), con le regole e il formato in `tracce-consegna.md`.

## Verifiche ripetibili (domande casuali per tag)

Le varianti di una posizione sono righe con lo stesso `tag` (un tag per posizione, unico nel sito, per esempio `rjs4-T1-assegnamento`; niente spazi) e la posizione con la lettera della variante (`T1a`, `T1b`, …). Le varianti hanno **stessi punti, pagina e sezione** (errore se no), di norma la stessa tipologia e gli stessi minuti, e stanno di seguito nella scaletta. Le pagine (istruzioni) non hanno tag e restano fisse. Nella dashboard le varianti di una posizione si vedono come una riga sola (dettaglio in `dashboard.md`).

In parte 2 tutte le varianti vanno nella banca del quiz con il loro tag (`genera_quiz.py` aggiunge i `<tags>` all'XML); nel `.mbz` ogni posizione diventa una domanda casuale che pesca dalla categoria della lezione una domanda con quel tag, con i punti della posizione. Nel backup gli id dei tag sono inventati (da 9900001): al ripristino Moodle ricrea i tag per nome e aggiorna il filtro. Nella dashboard e nei totali ogni posizione conta una volta; le varianti hanno lo stesso numero di domanda.

## Leggere un backup (.mbz)

`leggi_mbz.py BACKUP.mbz --quiz` mostra la struttura di ogni quiz del backup (di un corso o di una sola attività): tempo, punteggio, sezioni, e per ogni slot pagina, punti e domanda (nome, versione, banca) oppure, per le domande casuali, i tag e la categoria da cui pesca e le domande che corrispondono. Serve per controllare un quiz modificato in Moodle (per esempio la copia PDP): `--domande TESTO` mostra il testo delle domande delle categorie che contengono TESTO (ultima versione). Senza opzioni: sezioni, attività e banche.

`importa_mbz.py` fa il percorso inverso di `da_dashboard.py`: dal backup di un quiz ricava quiz e righe della dashboard, con traccia, correzione e «Soluzione e test» in queste convenzioni (HTML → Markdown, opzioni, campi Cloze, corrispondenze, CodeRunner JavaScript, SQL, PHP, HTML e CSS, database SQLite allegati → script del quiz, domande casuali → varianti con il tag). Con `--confronta` confronta il backup con un quiz della dashboard e riporta le modifiche fatte in Moodle. Uso e casi in `dashboard.md` («Importare un quiz da un backup»). Provato: andata e ritorno della V5R (dashboard → .mbz → dashboard) senza differenze; un quiz vecchio di 30 domande importato e rigenerato con gli stessi output attesi delle 19 CodeRunner SQL. Non torna uguale: le immagini (`importa_mbz.py` non le riporta nella traccia come `![…](…)`), i colori del testo, gli a capo dentro le opzioni (diventano « / »), il feedback generale delle domande aperte (diventa la correzione).

## Prefissi dei nomi

Dal catalogo. La pagina del blocco usa «Spiegazione» nelle esercitazioni con spiegazione, «Teoria» nell'esercitazione con studio e domande sequenziale (SD) e «Ripasso» nel ripasso teorico (RT) e nella complessiva di ripasso (ER).

## Non ancora gestito

Le domande PHP con il prototipo `php_mysqli_mock` (mappa delle query): si fanno con la skill `domande-php-mysqli-mock` e si uniscono gli XML.
