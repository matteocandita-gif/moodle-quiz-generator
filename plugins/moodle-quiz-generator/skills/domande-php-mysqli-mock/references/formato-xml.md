# Dalla specifica all'XML di Moodle

Le domande non si scrivono direttamente in XML: si scrive un **file di specifica** in testo semplice e lo script `scripts/crea_xml.py` lo trasforma nell'XML da importare in Moodle (Banca delle domande → Importa → formato *Moodle XML*). Così il codice PHP resta leggibile, senza escaping, e la struttura dell'XML è sempre quella giusta.

## Il file di specifica

Le righe che iniziano con `=== ` aprono una sezione; tutto il resto è contenuto grezzo, copiato così com'è (niente CDATA, niente virgolette da proteggere). Un file può contenere più domande e più database.

```text
=== category
Ripasso quarta in quinta/Lezione 5 - PHP e database
=== database dblibreria
CREATE TABLE Presentazioni (Id INTEGER PRIMARY KEY AUTOINCREMENT, ...);
INSERT INTO Presentazioni (...) VALUES (...), (...);
=== question
=== name
L5 - C8 - Scrivere: le presentazioni
=== options
answerboxlines: 30
=== note
Appunti per il docente: non finiscono nell'XML.
=== questiontext
<p>Testo HTML della domanda...</p>
[[codice html]]
<form action="presentazioni.php" method="GET">...</form>
[[/codice]]
...disclaimer...
=== answer
<?php
...
=== test
$_GET = ['sala' => 'Auditorium', 'posti' => '10'];
FakeDB::configure(['user' => 'root', 'password' => '', 'database' => 'dblibreria']);
=== descrizione
Auditorium, almeno 10 posti liberi
=== expected
<table>
...
=== test HIDE
...
```

| Sezione | Obbligatoria | Contenuto |
|---|---|---|
| `category` | no | categoria di destinazione, prima della prima domanda: `Nome` diventa `$module$/top/Nome`, un percorso che inizia con `$` resta com'è. Senza, la domanda va nella categoria scelta all'importazione |
| `database NOME` | no | SQL (accettato da SQLite) che crea e popola il database; lo script costruisce `NOME.db` e lo allega alle domande sqlite che lo usano |
| `question` | sì | apre una domanda (nessun contenuto) |
| `name` | sì | nome della domanda |
| `options` | no | righe `chiave: valore` (tabella sotto) |
| `note` | no | note per il docente, non esportate |
| `questiontext` | sì | testo HTML con il disclaimer; i blocchi `[[codice LINGUA]] … [[/codice]]` diventano il `<pre>` colorato dello stile di materiali-moodle |
| `preload` | no | codice precaricato; vuoto per la scrittura completa |
| `answer` | sì | soluzione, inizia con `<?php` |
| `test` | sì, almeno uno | codice del campo Test; `=== test HIDE` lo nasconde allo studente |
| `descrizione` | no, ma consigliata | dopo un test: la frase che lo studente vede nella colonna della prova (campo Extra) |
| `expected` | sì, dopo ogni test | output atteso |

Le righe vuote all'inizio e alla fine di ogni sezione vengono tolte; all'output atteso lo script aggiunge un solo a capo finale, come fa Moodle all'esportazione.

## Impostazioni della domanda

Lo script riproduce l'XML che Moodle esporta per una domanda CodeRunner con questi prototipi: tutti i campi che il prototipo gestisce (template, linguaggio, grader, sandbox…) restano vuoti, così la domanda li eredita dal prototipo installato. Valori predefiniti modificabili con `=== options`:

| Opzione | Predefinito | Significato |
|---|---|---|
| `prototipo` | `sqlite` | `sqlite` (php_mysqli_sqlite, query eseguite davvero) o `mock` (php_mysqli_mock, mappa delle query) |
| `database` | l'unico definito | quale `=== database` allegare (solo prototipo sqlite) |
| `defaultgrade` | `1` | punteggio della domanda |
| `penalty` | `0` | penalità per tentativo |
| `allornothing` | `1` | `1` = punteggio solo se passano tutti i test; `0` = punteggio parziale per test (utile nella scrittura completa) |
| `penaltyregime` | `0` | penalità progressive di CodeRunner |
| `precheck` | `0` | pulsante di controllo preliminare |
| `hidecheck` | `0` | `1` nasconde il pulsante Controlla (per le verifiche) |
| `showsource` | `0` | mostra il programma completo eseguito (solo per il docente in fase di prova) |
| `answerboxlines` | calcolato | righe della casella di risposta: il massimo tra 18 e le righe del preload più 3 |
| `answerboxcolumns` | `100` | colonne della casella |
| `validateonsave` | `1` | CodeRunner controlla la soluzione al salvataggio della domanda |
| `displayfeedback` | `1` | mostra la tabella dei risultati dei test |
| `giveupallowed` | `0` | pulsante per arrendersi e vedere la soluzione |

Ogni test viene esportato con `testtype="0"`, `useasexample="0"`, `mark="1.0000000"`, `display` SHOW (o HIDE) e la descrizione nel campo Extra. Il database allegato è un elemento `<file name="NOME.db" path="/" encoding="base64">` dentro `<testcases>`, come nella skill SQL. Non usare "use as example": mostrerebbe nel testo il codice del campo Test, cioè la configurazione del database simulato.

## Uso degli script

```bash
python3 scripts/crea_xml.py specifica.txt /mnt/user-data/outputs/NOME.xml [--verifica] [--cartella-db DIR]
python3 scripts/prova_query.py specifica.txt NOME_DB "SELECT ..." [--prima "SQL dello schema del test"]
```

`crea_xml.py` si ferma con un elenco di problemi se manca una sezione obbligatoria, se il testo non contiene il disclaimer, se la soluzione o il preload non iniziano con `<?php`, se un test non ha l'output atteso o non chiama `FakeDB::configure`, se un database ha errori SQL, se un nome è ripetuto, o se l'HTML non rispetta lo stile (emoji, tag vietati, blocchi di codice non chiusi). Alla fine controlla che l'XML sia ben formato. `--cartella-db` salva anche i file `.db`, da aprire con DB Browser.

Con `--verifica`, se PHP (e per il prototipo sqlite il client `sqlite3`) sono installati, esegue la soluzione su ogni test e confronta l'output; per ogni test mostra anche la prima riga di output del preload. Nella chat di Claude.ai non ci sono: lo script lo dice e gli output vanno controllati con `prova_query.py` e a mano.

`prova_query.py` costruisce il database dalla specifica ed esegue una query, mostrando i valori come li vedrà lo studente: serve a calcolare le righe e il loro formato negli output attesi.

Dopo l'importazione, aprire la domanda e salvarla con *Validate on save* attivo fa verificare a CodeRunner la soluzione su Jobe: è il controllo definitivo.

## Struttura dell'XML generato (riferimento)

Ricavata dall'esportazione di una domanda reale. Per ogni domanda:

```xml
<question type="coderunner">
  <name><text>…</text></name>
  <questiontext format="html"><text><![CDATA[…HTML…]]></text></questiontext>
  <generalfeedback format="html"><text></text></generalfeedback>
  <defaultgrade>1</defaultgrade> <penalty>0</penalty> <hidden>0</hidden> <idnumber></idnumber>
  <coderunnertype>php_mysqli_mock</coderunnertype> <prototypetype>0</prototypetype>
  <allornothing>1</allornothing> … <answerboxlines>18</answerboxlines> <answerboxcolumns>100</answerboxcolumns>
  <answerpreload><![CDATA[…]]></answerpreload>
  … campi vuoti ereditati dal prototipo (template, grader, language, sandbox…) …
  <answer><![CDATA[…]]></answer>
  <validateonsave>1</validateonsave>
  … <twigall>0</twigall> … <displayfeedback>1</displayfeedback> <giveupallowed>0</giveupallowed>
  <testcases>
    <testcase testtype="0" useasexample="0" hiderestiffail="0" mark="1.0000000">
      <testcode><text><![CDATA[…]]></text></testcode>
      <stdin><text></text></stdin>
      <expected><text><![CDATA[…\n]]></text></expected>
      <extra><text></text></extra>
      <display><text>SHOW</text></display>
    </testcase>
  </testcases>
</question>
```

Se un contenuto contenesse la sequenza `]]>`, lo script la spezza su due sezioni CDATA, come richiede l'XML.
