# La specifica e gli script

L'XML non si scrive a mano. Si scrive una **specifica** in testo semplice, con l'HTML leggibile e il codice grezzo nei blocchi `[[codice]]`, e `scripts/crea_xml.py` la trasforma in Moodle XML dopo aver controllato tutte le regole. È lo stesso metodo della skill `domande-php-mysqli-mock`.

## Formato

Le righe che iniziano con `=== ` aprono una sezione; il resto è contenuto, copiato così com'è. Le righe vuote all'inizio e alla fine di una sezione vengono tolte.

```text
=== category
Lezione 6 - JavaScript: i cicli
=== question description
=== name
L6 - 00 - Come lavoriamo oggi
=== questiontext
<div style="...">...</div>
=== question cloze
=== name
L6 - B1 - Tracciamento: il ciclo for
=== note
Appunti per il docente: restano nella specifica, non vanno nell'XML.
=== questiontext
<p>...</p>
[[codice js]]
...
[[/codice]]
<p>... {1:NUMERICAL:=3:0#Corretto.} ...</p>
```

| Sezione | Per | Contenuto |
|---|---|---|
| `category` | tutte | categoria delle domande che seguono; si può ripetere per cambiarla. `Lezione 6 - …` diventa `$module$/top/Lezione 6 - …`; un percorso che inizia con `$` resta com'è |
| `question TIPO` | tutte | apre una domanda: `cloze`, `multichoice`, `truefalse`, `shortanswer`, `essay`, `description` |
| `name` | tutte | nome della domanda |
| `options` | tutte | righe `chiave: valore` (tabella sotto) |
| `note` | tutte | note per il docente, non esportate |
| `questiontext` | tutte | testo HTML |
| `generalfeedback` | tutte | feedback generale, facoltativo |
| `answer FRAZIONE` | multichoice, shortanswer | una risposta; `100` giusta, `0` sbagliata, valori intermedi per i punteggi parziali |
| `feedback` | multichoice, shortanswer | feedback della risposta appena sopra |
| `feedback true` / `feedback false` | truefalse | feedback delle due risposte |
| `graderinfo` | essay | indicazioni per chi corregge |
| `responsetemplate` | essay | testo iniziale nella casella di risposta |

## Opzioni

| Opzione | Tipi | Predefinito |
|---|---|---|
| `defaultgrade` | tutti tranne cloze e description | `1` |
| `penalty` | tutti tranne description | `0.3333333`; `1` per truefalse; `0` per essay |
| `single` | multichoice | `true` (`false` = più risposte giuste) |
| `shuffleanswers` | multichoice | `true` |
| `answernumbering` | multichoice | `abc` (`none`, `123`, `ABCD`) |
| `showstandardinstruction` | multichoice | `0` |
| `correct` | truefalse | obbligatoria: `true` o `false` |
| `usecase` | shortanswer | `0` |
| `responseformat` | essay | `plain` (`editor` per testo formattato) |
| `responsefieldlines` | essay | `25` |
| `responserequired`, `attachments`, `attachmentsrequired` | essay | `1`, `0`, `0` |

## Gli script

Tutti si lanciano dalla cartella della skill con `python3 scripts/NOME.py`.

| Script | Che cosa fa |
|---|---|
| `crea_xml.py SPEC.txt USCITA.xml` | specifica → Moodle XML; espande i blocchi `[[codice]]`; si ferma con l'elenco degli errori se una regola non è rispettata, e segnala gli avvisi |
| `espandi_html.py SORGENTE.html USCITA.html` | prepara una pagina per l'attività Pagina: espande `[[codice]]` e controlla lo stile |
| `controlla_xml.py FILE.xml [--avvisi]` | controlla un XML esistente (un export dell'utente, o l'XML di un'altra skill) con le stesse regole |
| `unisci_xml.py USCITA.xml A.xml B.xml … [--categoria "Nome"]` | unisce più XML in un file solo, nell'ordine dato |
| `leggi_mbz.py BACKUP.mbz [opzioni]` | legge un backup di corso: vedi `backup-mbz.md` |

Errori bloccanti di `crea_xml.py`: campi Cloze malformati o senza risposta giusta, escaping di `/` o `"`, entità o tag nelle risposte, menù con opzioni condivise in `MULTICHOICE_S` o in ordini diversi o nell'ordine delle risposte giuste, campi dentro `<pre><code>`, emoji, tag `<html>`/`<head>`/`<body>`/`<style>`/`<script>`, risposta singola senza esattamente una risposta a 100, risposta multipla a più risposte con le frazioni positive che non sommano 100 o le frazioni negative che non sommano -100, vero/falso senza `correct`, nomi ripetuti.

Avvisi (non bloccanti): menù singolo con `MULTICHOICE`, titoli grandi nel testo di una domanda, risposta multipla senza feedback sulle sbagliate, risposta aperta senza `graderinfo`.

## Consegna

1. Scrivi la specifica in `/home/claude/` e lancia `crea_xml.py`; correggi finché non passa.
2. Copia l'XML in `/mnt/user-data/outputs/` e presentalo. Presenta anche la specifica se l'utente vuole rivederla.
3. Nel messaggio: la categoria, il numero di domande per tipo, le note per il docente (che nell'XML non ci sono) e gli avvisi rimasti con il motivo.
4. Per una **domanda singola** l'utente può chiedere il testo da incollare invece dell'XML: dagli l'HTML del testo già espanso (con il `<pre>` pronto), più le risposte e i feedback se il tipo li ha.

Per importare: Banca delle domande → Importa → formato *Moodle XML*. L'import crea sempre domande nuove: non aggiorna quelle esistenti.
