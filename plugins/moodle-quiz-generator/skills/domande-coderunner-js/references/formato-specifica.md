# La specifica, i prototipi e lo script

## I due prototipi

Installati nel Moodle dell'utente; i template sono in `assets/` e le descrizioni che compaiono in Moodle in `assets/descrizione-*.html`.

**«Javascript (con prompt)»** (versione 2), un'esecuzione per test:
1. lo standard input del test, diviso in righe, alimenta `prompt()`;
2. `Math.random()` legge la sequenza fissa di 40 valori (o il parametro `random`) dalla posizione scritta in Extra;
3. esegue la risposta dello studente e **poi** il codice del test (prima, con il parametro `test_prima`);
4. confronto con NearEqualityGrader: ignora maiuscole e differenze di spazi.

**«Javascript (con gapfiller)»**, tutti i test in un'esecuzione:
1. sostituisce gli spazi `{[…]}` del Global extra con le risposte dello studente, in ordine;
2. per ogni test: standard input e random ripartono (random dalla posizione in Extra), poi esegue il codice del test **e poi** il codice completato;
3. confronto esatto (EqualityGrader), tutto o niente.

`scripts/esegui_js.py` costruisce lo stesso programma e lo esegue in Node: sul deposito delle terze ha riprodotto tutti i 908 output attesi delle domande con prompt.

## Formato

```text
=== category
Lezione 4 - JavaScript: i cicli
=== question prompt
=== name
S2 - Scrivere: somma fino allo zero
=== options
esempi: primo
=== note
Per il docente.
=== questiontext
<p>...</p>
=== preload
...scheletro o codice da correggere...
=== answer
...soluzione...
=== test
// Tre numeri e poi 0
=== stdin
4
5
3
0
=== extra
4
=== test HIDE
// Caso nascosto
...
```

| Sezione | Contenuto |
|---|---|
| `category` | categoria delle domande che seguono |
| `question prompt` / `question gapfiller` | apre una domanda del tipo indicato |
| `name`, `questiontext`, `answer` | obbligatorie. Per il gapfiller `answer` contiene le risposte, **una per riga**, nell'ordine degli spazi |
| `code` | solo gapfiller, obbligatoria: il codice con gli spazi `{[6]}` o `{[4-10]}` (va nel Global extra) |
| `preload` | solo prompt: codice precaricato (scheletro o codice da correggere) |
| `test` / `test HIDE` | codice del test; per convenzione inizia con un commento che descrive il caso |
| `stdin`, `extra`, `expected` | dopo un test: standard input (una riga per prompt), posizione random (intero), output atteso scritto a mano (di solito no: lo calcola lo script, e se diverso avvisa e usa il suo) |
| `note`, `generalfeedback` | facoltative |

Nel testo valgono i blocchi `[[codice js]]` e `[[codice semplice]]` (per mostrare la forma dell'output).

## Opzioni

| Opzione | Predefinito | Significato |
|---|---|---|
| `test_prima` | `0` | `1`: il test gira prima della risposta (solo prompt) |
| `random` | | sequenza su misura, es. `0.5, 0.1, 0.9` |
| `esempi` | `primo` | quali test mostrare come esempio: `primo`, `tutti`, `nessuno` (i test HIDE mai) |
| `allornothing` | `1` | `0` per il punteggio parziale per test (solo prompt) |
| `defaultgrade`, `penalty` | `1`, `0` | |
| `answerboxlines` | `18` | righe della casella |
| `hidecheck` | `0` | `1` nasconde il pulsante Controlla |

## Lo script

```bash
python3 scripts/crea_xml.py SPEC.txt USCITA.xml
```

Si ferma se: manca una sezione; il numero di spazi del gapfiller non coincide con le risposte; la soluzione usa `alert` o `document`; la soluzione dà errore o non termina in 5 secondi su un test; Extra non è un intero; un nome è ripetuto.

Avvisa se: un test non ha codice (manca il commento descrittivo); il programma chiede più input di quelli forniti; la sequenza random ricomincia; l'output è vuoto; un array è stampato con `console.log`; compare un decimale lunghissimo; tutti i test hanno lo stesso output.

Per il debugging stampa che cosa vede lo studente eseguendo il codice di partenza con il primo test.

Dopo l'import il controllo definitivo è il **bulk tester** di CodeRunner sulla categoria.

## XML con le altre skill

Se le domande fanno parte di una sequenza di `materiali-moodle`, produci qui il loro XML e uniscilo con `unisci_xml.py` di quella skill.
