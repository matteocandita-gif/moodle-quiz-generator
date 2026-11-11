# Prototipi CodeRunner `html_con_file` e `css_con_test`

Il prototipo delle domande «Consegna con controllo automatico» (tipologia `consegna_auto`): lo studente carica un file `.html` o la cartella del sito compressa in `.zip`, e un template Python controlla HTML, cartella, CSS e JavaScript con una funzione per test. Dallo stesso template nasce anche il prototipo `css_con_test` (tipologia `esercizio_controllo`): niente allegati, il codice CSS o HTML si scrive nella casella di risposta e il parametro del template `pagina` dice che cosa contiene (`stile.css`, predefinito: un foglio di stile; `index.html`: codice HTML). Resta nel repository: ai colleghi arrivano solo i prototipi costruiti, `prototipo-html-con-file.xml` e `prototipo-css-con-test.xml` in `plugins/moodle-quiz-generator/skills/materiali-moodle/assets/`.

## I file

| File | Che cosa contiene |
|---|---|
| `template.py` | il template del prototipo (Python con poche righe Twig in testa e in fondo): **si modifica qui** |
| `testi.py` | la descrizione del prototipo in Moodle, con le tabelle delle funzioni, il promemoria per gli studenti e i testi delle domande di prova |
| `crea_prototipo.py` | costruisce l'XML dei due prototipi negli asset del plugin e la tabella delle funzioni in `progettazione-quiz/references/tracce-consegna.md` (tra i commenti `funzioni-html-con-file`); con `--prove DIR` anche quattro domande di prova da importare in Moodle |
| `prova.py` | esegue il template come CodeRunner su Jobe: rende le righe Twig, copia gli allegati, lancia Python, divide l'output con il separatore dei test |
| `domande.py` | i test e i file delle domande di prova (pagina, sito con link, sito con CSS, sito con JavaScript) |
| `test_*.py`, `prove.py` | le prove: `python3 prove.py` le lancia tutte e dice «TUTTO A POSTO» (`test_stile.py`: CSS nella casella, stile in linea, `<style>` nella pagina) |

## Modificare il prototipo

1. Modifica `template.py` (e `testi.py` per la descrizione e le tabelle).
2. **Solo aggiunte**: una funzione nuova sì, ma le funzioni esistenti non cambiano nome, argomenti né esito. Le domande in Moodle prendono il template dal prototipo: cambiare una funzione cambia il voto di tutte le domande che la usano, anche nei quiz già svolti.
3. Aggiungi le prove della funzione nuova in un `test_*.py` (consegne giuste e sbagliate, con l'esito atteso), e mettilo in `SERIE` di `prove.py`.
4. `python3 prove.py` deve dire «TUTTO A POSTO».
5. `python3 crea_prototipo.py`, poi le prove del plugin (`python3 sviluppo/prove/prova_tutto.py`).
6. Nel CHANGELOG: che il prototipo è cambiato (cambiando il template cambiano tutti e due) e che va reimportato in Moodle (Banca delle domande → Importa, formato Moodle XML), nella stessa banca in cui c'era.

## Cose da sapere

- Nel template niente `{{`, `{%` né `{#` fuori dalle righe Twig previste: Twig le interpreterebbe.
- Ogni controllo stampa una sola riga: `OK`, oppure il problema. L'output atteso di ogni test è `OK`.
- **Il peso di un test non è mai 0**: CodeRunner divide per il peso quando disegna la tabella dei risultati e la pagina va in errore («Division by zero»). Per un controllo che deve solo dare il messaggio si usa 0.001. `da_dashboard.py` rifiuta i pesi a zero.
- Il template usa `node --check` per gli errori di sintassi JavaScript; se Node non parte su Jobe, ripiega su un controllo di parentesi e virgolette. `diagnosi_node()` dice se Node funziona.
- Il prototipo usa l'interfaccia «Html» di CodeRunner con il solo promemoria (campo «Prototype extra»): niente casella di risposta, serve un allegato. Il campo «Risposta» resta testo semplice (`enable_in_editor: false`).
