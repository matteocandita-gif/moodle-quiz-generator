# La sequenza di un'esercitazione

## Esercitazioni senza codice

Concetti, architetture, teoria (il web, i tre livelli, la normativa): pagina del blocco, poi domande brevi (risposta multipla, vero/falso), poi esercizi di ragionamento (Cloze di tracciamento o «metti in ordine»).

## Esercitazioni con codice

Valgono per HTML, CSS, JavaScript, SQL, PHP. Le parti sono sempre queste, in quest'ordine:

| # | Parte | Forma |
|---|---|---|
| 1 | introduzione senza codice | pagina: che problema risolviamo, a che cosa serve |
| 2 | spiegazione tecnica | pagina: istruzioni, sintassi, regole |
| 3 | esempio svolto | riquadro giallo nella pagina, oppure Cloze di lettura «Esempio svolto: leggere X» |
| 4 | completamento | Cloze con i campi dentro il codice |
| 5 | debugging | CodeRunner dove si può (sotto), altrimenti «Trova l'errore» |
| 6 | esercizio guidato | Cloze «Esempio guidato» o scrittura con scheletro |
| 7 | esercizio finale | scrittura completa: CodeRunner, oppure risposta aperta |

Le parti 1 e 2 possono stare nella stessa pagina. Il debugging viene **dopo** il completamento: lo studente deve aver già scritto il codice giusto prima di cercare quello sbagliato.

## Il debugging

Due tipologie, in quest'ordine:

1. **Con messaggi**: il codice si ferma con un errore; lo studente legge il messaggio, capisce dove si è fermato, corregge, riprova. Gli errori emergono uno alla volta.
2. **Silenzioso**: il codice gira ma il risultato è sbagliato; lo studente confronta l'output con quello atteso. È l'errore più frequente quando lavorano da soli.

Ogni errore deve essere legato a un concetto della lezione (un nome di tabella, `$_GET` al posto di `$_POST`, `>` al posto di `>=`, una JOIN mancante), mai un refuso fine a se stesso. In una sequenza di domande il sostegno cala: prima si dice quanti errori ci sono e dove, poi solo quanti, poi nulla.

## Chi fa che cosa

| Linguaggio | Debugging e scrittura con correzione automatica | Skill |
|---|---|---|
| JavaScript | CodeRunner con il prototipo JavaScript dell'utente (`prompt()` legge l'input del test, `Math.random()` restituisce valori prefissati) | `domande-coderunner-js` |
| SQL | CodeRunner SQL su SQLite, con il database allegato | `domande-coderunner-sql` |
| PHP con database | CodeRunner `php_mysqli_mock` | `domande-php-mysqli-mock` |
| HTML, CSS | niente da eseguire: Cloze o «Trova l'errore» a risposta multipla | questa |

Quando la sequenza richiede domande CodeRunner, leggi lo `SKILL.md` della skill indicata e seguilo per quelle domande; poi unisci gli XML con `scripts/unisci_xml.py`, così l'utente importa un file solo. Se la skill indicata non è installata, dillo all'utente e proponi l'alternativa senza CodeRunner (Trova l'errore, Cloze di correzione).

## Scrivere a memoria o saper leggere

Con l'IA che scrive codice, molte parti si valutano sulla **lettura**: tracciare, prevedere l'output, trovare l'errore. Ma l'Esame di Stato scritto chiede ancora di scrivere a mano SQL, la pagina HTML con il form, il PHP che legge dal database: queste parti restano anche come **scrittura**. Quando prepari una sequenza, chiediti per ogni argomento se è da saper scrivere o da saper leggere, e se non è chiaro chiedilo all'utente nella proposta.

## Come si lavora

Per una sequenza o un gruppo di domande, **prima la proposta, poi i file**:

1. un elenco delle domande e delle pagine, ognuna con nome, tipo, che cosa allena e difficoltà;
2. il nome della categoria in cui andranno (proponilo tu: per esempio `Lezione 6 - JavaScript: i cicli`);
3. le domande che passeranno a una skill CodeRunner.

Si produce dopo la conferma dell'utente. Una richiesta puntuale (una domanda sola, una correzione) si esegue subito.
