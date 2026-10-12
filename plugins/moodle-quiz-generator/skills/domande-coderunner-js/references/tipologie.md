# Tipologie di domanda JavaScript

Ricavate dal deposito delle terze dell'utente (348 domande CodeRunner: 301 con prompt, 43 gapfiller, 4 senza test automatici). Gli argomenti seguono il programma di terza: selezione, cicli `for` e `while`, array, funzioni (anche `return` contro `console.log`, early return, variabili locali e globali), esercizi complessivi.

## Con prompt (`=== question prompt`)

| Tipologia | Come si fa | Test |
|---|---|---|
| **Scrittura completa** | lo studente scrive tutto il programma | standard input diversi: un caso tipico, l'altro ramo dell'if, un caso limite (zero, negativo, uguali, nessun elemento) |
| **Con scheletro** | `=== preload` con lo scheletro: dati iniziali (un array), commenti che guidano le parti da scrivere | come sopra |
| **Funzioni** | lo studente scrive la funzione; i test la chiamano: `console.log(maggiore(10, 3));` | il codice del test gira dopo la risposta. Per controllare il `return`, i test stampano il valore restituito: se la funzione stampa invece di restituire, l'output non coincide |
| **Dati dal test** | opzione `test_prima: 1`: il test definisce i dati (`let voti = [6, 8, 7];`) e la risposta li usa | ogni test con dati diversi; la consegna dice quale variabile esiste già |
| **Random** | `Math.random()` dalla sequenza fissa; il campo `=== extra` sceglie da dove partire | un test per punto di partenza; con `random: …` nelle opzioni una sequenza costruita apposta (per esempio un valore che si ripete, per la ricerca) |
| **Debugging** | `=== preload` con il codice sbagliato, `=== answer` corretta | vedi sotto |

## Gapfiller (`=== question gapfiller`)

Il **completamento**: il codice con gli spazi `{[larghezza]}` o `{[predefinita-massima]}` in `=== code`, le risposte una per riga in `=== answer`, nell'ordine degli spazi. Nei depositi si chiama spesso «esercizio guidato».

- Ogni spazio è una parte che lo studente deve saper scrivere (una condizione, l'incremento, il nome dell'array, `push`), non un dettaglio di battitura.
- Il codice del test gira **prima** del codice completato: serve a definire dati (`let nomi = ["Anna", "Luca"];`).
- Il confronto è **esatto** e la domanda vale **tutto o niente**.
- Fai in modo che l'output dipenda dall'input: se ogni test stampa «Fine», una risposta sbagliata può passare. Lo script avvisa quando tutti i test hanno lo stesso output.

## Debugging

Due tipologie, prima quella con messaggi:

1. **Con messaggio**: il codice si ferma con un errore (`ReferenceError: numero is not defined`, `TypeError`, `SyntaxError`). Lo studente legge il messaggio, trova la riga, corregge, riprova.
2. **Silenzioso**: il codice gira ma l'output è sbagliato. Gli errori tipici di terza: `prompt` senza `Number()` (4 e 3 danno 43), `<` invece di `<=`, accumulatore inizializzato dentro il ciclo, `=` invece di `==` o `===` nella condizione, indice che parte da 1, `console.log` dentro la funzione invece di `return`.

Ogni errore riguarda un concetto della lezione. Nel testo indica quanti errori ci sono finché il sostegno lo prevede. Lo script esegue il codice di partenza con il primo test e mostra che cosa vede lo studente per primo: controlla che sia l'errore da cui vuoi farlo partire.

## Convenzioni dell'utente

- **Ogni test inizia con un commento** che descrive il caso: `// Caso con input 45`, `// Numeri uguali`. Lo studente lo vede nella tabella dei risultati.
- **Il primo test è mostrato come esempio** nel testo (`esempi: primo`, predefinito); `esempi: tutti` o `nessuno` se l'utente lo chiede. I test nascosti (`=== test HIDE`) solo nelle verifiche.
- **Tutto o niente** (`allornothing: 1`, predefinito); il punteggio parziale per test solo se richiesto.
- **Da tre a cinque test**, che coprono i rami del programma.
- **L'output richiesto è scritto nella consegna** in un blocco di codice, con la forma esatta (`Da pagare: 18 euro`): il confronto del prototipo con prompt ignora maiuscole e spazi, ma non le parole.

## Testo della domanda

Nello stile compatto delle domande (`stile-html.md`): la situazione in una frase, la consegna con le parole chiave in grassetto, i nomi di variabili e funzioni in monospace, la forma dell'output in un blocco. Se ci sono dati già pronti (preload o `test_prima`), dillo: «l'array `voti` esiste già».

## Fuori da questa skill

- Le domande **senza test automatici** (prototipo «Javascript (senza test automatici)», correzione a mano) e gli esercizi liberi: per i nuovi materiali, risposta aperta con `materiali-moodle`.
- Le **Cloze di lettura del codice** (tracciamento, trova l'errore, completamento con menù): `materiali-moodle`.
