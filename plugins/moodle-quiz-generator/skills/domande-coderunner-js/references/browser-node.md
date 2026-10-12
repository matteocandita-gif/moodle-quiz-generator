# Browser e Node

Gli studenti provano il codice nel browser; CodeRunner lo esegue con **Node.js** su Jobe, attraverso i template dei prototipi. Le differenze verificate eseguendo i template:

| Nel browser | Su Jobe | Che cosa fare |
|---|---|---|
| `prompt("Messaggio")` apre una finestra con il messaggio | restituisce la riga successiva dello standard input; il messaggio **non** compare nell'output | l'output atteso contiene solo i `console.log` |
| `prompt` restituisce testo | idem | senza `Number()`, `4 + 3` dà `43`: perfetto per il debugging silenzioso |
| l'utente risponde quante volte serve | se il programma chiede più valori di quelli nello standard input, `prompt` restituisce `undefined` (e `Number(undefined)` è `NaN`) | lo standard input deve contenere tutti i valori, compreso quello che ferma il ciclo; lo script avvisa |
| un ciclo che aspetta un valore valido continua a chiedere | se lo standard input finisce, `prompt` restituisce `undefined` per sempre e il ciclo non termina | lo script si ferma dopo 5 secondi e segnala il ciclo infinito |
| `console.log([1, 2, 3])` mostra `(3) [1, 2, 3]` | stampa `[ 1, 2, 3 ]` | fai stampare gli elementi con un ciclo o con `join(", ")`, oppure `"Array: " + numeri` (che dà `1,2,3`) |
| `alert`, `document.write`, `document.getElementById` | non esistono: `ReferenceError` | solo `console.log`; lo script blocca la domanda |
| `0.1 + 0.2` | `0.30000000000000004` (come nel browser, ma lo studente non se ne accorge) | prezzi e medie con `toFixed(2)`, oppure dati che danno risultati esatti; lo script avvisa |
| `Math.random()` casuale | valori della sequenza fissa, dalla posizione in Extra | gli output attesi si calcolano eseguendo; con `random:` una sequenza su misura |

Il confronto del prototipo con prompt ignora maiuscole e differenze di spazi; quello del gapfiller è esatto.
