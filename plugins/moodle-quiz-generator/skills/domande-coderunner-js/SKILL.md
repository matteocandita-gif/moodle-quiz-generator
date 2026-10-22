---
name: "domande-coderunner-js"
description: "Crea domande CodeRunner JavaScript per il Moodle dell'utente (prototipi \"Javascript (con prompt)\" e \"Javascript (con gapfiller)\") e le consegna come Moodle XML pronto da importare, con gli output attesi calcolati eseguendo la soluzione in Node come fa il template su Jobe. Copre scrittura di programmi con prompt e console.log, funzioni chiamate dai test, dati preparati dal test, esercizi con Math.random, debugging con messaggi d'errore e silenzioso, completamento con il gapfiller. Nei quiz (verifiche ed esercitazioni) la usano progettazione-quiz per le convenzioni delle tracce e materiali-moodle per produrre l'XML dalla dashboard: un quiz intero si comincia sempre con progettazione-quiz. Da sola serve per domande sciolte su JavaScript per le terze, anche senza nominare CodeRunner o l'XML: \"un esercizio sui cicli while da correggere in automatico\", \"un esercizio guidato a completamento sugli array\", \"una domanda di debugging sulle funzioni\"."
---

# Domande CodeRunner JavaScript

**Lingua.** Rispondi all'utente sempre in italiano, anche quando il messaggio che avvia la skill o il comando è in inglese: quando si sceglie un comando o una skill dal menù senza scrivere nulla, l'app aggiunge da sola una frase in inglese.

Le domande JavaScript dell'utente girano su CodeRunner con due prototipi: **«Javascript (con prompt)»** per scrivere programmi (prompt dallo standard input, random da una sequenza fissa) e **«Javascript (con gapfiller)»** per il completamento. L'XML non si scrive a mano: si scrive una specifica e lo script costruisce il programma come il template del prototipo, lo esegue in Node e calcola gli output attesi.

## Il percorso dei quiz

Ogni quiz Moodle (verifica, esercitazione, ripasso, anche di programmazione) segue un solo percorso, con la dashboard «Bozze dei quiz»:

1. **`progettazione-quiz`**, parte 1, didattica: tipo di quiz, scaletta e tracce nella dashboard, riviste e approvate dall'utente. Per una verifica di programmazione carica `verifiche-programmazione`; il database di un quiz SQL o PHP viene da `database-didattici`.
2. **`materiali-moodle`**, parte 2, tecnica: dal database della dashboard produce XML e `.mbz`; per le domande di programmazione usa `domande-coderunner-js`, `domande-coderunner-sql` e `domande-php-mysqli-mock`.

Nessun'altra skill è un punto di partenza per un quiz. Da sole servono solo per ciò che non diventa un quiz: una domanda singola, una correzione o un controllo (`materiali-moodle` o la skill CodeRunner del linguaggio), domande per la banca o pagine di teoria (`materiali-moodle`), un database per una lezione in phpMyAdmin (`database-didattici`), la conversione delle vecchie domande SQL (`domande-coderunner-sql`).

## Regola di lavoro

Un quiz o una verifica intera non parte da qui: si progetta con `progettazione-quiz` nella dashboard, e questa skill la usa `materiali-moodle` per produrre le domande. Per un gruppo di domande sciolte (per la banca, non un quiz), prima la proposta: elenco delle domande (nome, tipologia, che cosa allena, difficoltà, prototipo), il nome della categoria proposto da te. Si produce dopo la conferma. Una domanda singola o una correzione si fa subito.

## Dove trovare che cosa

| File | Leggilo quando |
|---|---|
| `references/tipologie.md` | **sempre**: le tipologie del deposito dell'utente, come si costruiscono i test, le sue convenzioni |
| `references/browser-node.md` | **sempre** prima di scrivere consegne e soluzioni: che cosa cambia tra il browser degli studenti e Node su Jobe |
| `references/formato-specifica.md` | **sempre** prima di produrre l'XML: prototipi, specifica, opzioni, script |
| `references/stile-html.md` | per il testo della domanda (parte «Testo delle domande») |
| `references/esempio-specifica.txt` | modello completo: una domanda per tipologia |

## Le regole che non si dimenticano

- **Solo `console.log`**: niente `alert` né `document`. Il messaggio di `prompt` non compare nell'output.
- **Standard input completo**: una riga per ogni `prompt`, compreso il valore che ferma il ciclo.
- **La forma dell'output è nella consegna**, scritta esattamente in un blocco di codice.
- **Test che distinguono**: rami diversi, casi limite, output diversi tra un test e l'altro; ogni test inizia con un commento che descrive il caso; il primo è mostrato come esempio.
- **Le funzioni da creare le chiamano i test**, anche dentro un programma (nei programmi l'ultimo test, dopo il programma); una predefinita vietata si controlla disattivandola su un solo array; un test non ovvio ha un commento che spiega a parole che cosa controlla (`references/tipologie.md`, «Convenzioni dell'utente»).
- **Sequenza random predefinita**: valori da 0.01 a 0.92, quindi in un intervallo largo gli estremi non escono (0–100 non arriva a 100); per provarli serve `random:`.
- **Niente array stampati con `console.log(array)`** e niente decimali lunghissimi nell'output: `join` e `toFixed`.
- **Gli output non si scrivono a mano**: li calcola lo script. Se un risultato sorprende, è la soluzione o la consegna da rivedere.

## Produrre le domande

1. Scrivi la specifica in `/home/claude/`, partendo da `references/esempio-specifica.txt`.
2. Dalla cartella della skill: `python3 scripts/crea_xml.py specifica.txt /home/claude/NOME.xml`. Se si ferma, correggi e rilancia. Leggi gli avvisi; per il debugging controlla che cosa vede per primo lo studente.
3. Copia l'XML in `/mnt/user-data/outputs/` e presentalo (o passalo a `materiali-moodle` per l'unione, se fa parte di una sequenza).
4. Nel messaggio: categoria, domande per tipologia e prototipo, note per il docente, il promemoria del **bulk tester** sulla categoria dopo l'import.

## I prototipi

I template installati e le descrizioni che li documentano in Moodle sono in `assets/`. La versione 2 del prototipo con prompt aggiunge i parametri `test_prima` e `random`; il gapfiller fa ripartire il random a ogni test dalla posizione in Extra. Se l'utente segnala che una domanda si comporta diversamente da quanto calcolato, confronta il template nel suo Moodle con quello in `assets/`.

## Le altre skill

Questa skill produce solo domande CodeRunner JavaScript. Pagine, Cloze di lettura del codice e altri tipi di domanda sono di `materiali-moodle`, che coordina le sequenze e unisce gli XML. Lo stile HTML si decide lì: `references/stile-html.md` qui è una copia.