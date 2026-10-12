# Domande Cloze

## Sintassi dei campi

```text
{PESO:TIPO:=giusta#feedback~sbagliata#feedback~sbagliata#feedback}
```

- `PESO`: di solito `1`.
- `=` segna la risposta corretta; in alternativa `%100%`, `%50%` per i punteggi parziali.
- `#` apre il feedback dell'opzione, `~` separa le opzioni.

| Tipo | Uso |
|---|---|
| `SHORTANSWER` | risposta breve, maiuscole e minuscole indifferenti; più risposte accettate con `~=` (`{1:SHORTANSWER:=css/stile.css~=./css/stile.css}`) |
| `SHORTANSWER_C` | come sopra ma distingue maiuscole e minuscole: per nomi di variabili o chiavi quando il caso conta |
| `NUMERICAL` | numero con tolleranza: `{1:NUMERICAL:=37.5:0#Corretto: 12.50 × 3.}` |
| `MULTICHOICE_S` | menù a tendina con opzioni mescolate da Moodle: **la scelta normale** |
| `MULTICHOICE` | menù con ordine fisso: **solo** per il caso dei menù che condividono le opzioni (sotto) |

## Le regole dell'utente

Lo script `crea_xml.py` le controlla tutte; `controlla_xml.py` le controlla su file già esistenti.

1. **Escaping solo di `}` `#` `~`** dentro i campi (`\}`, `\#`, `\~`). Mai `\/` né `\"`: nel Moodle dell'utente la barra rovesciata compare allo studente, sia nei menù sia nei feedback.
2. **Menù singoli: `MULTICHOICE_S`.** Con l'ordine fisso la risposta giusta si indovina dalla posizione.
3. **Menù che condividono le stesse opzioni** (metti in ordine, classifica ogni riga): `MULTICHOICE`, con le opzioni nello **stesso ordine in tutti i campi**, mescolato una volta in fase di scrittura e **diverso dall'ordine delle risposte corrette**. `MULTICHOICE_S` le rimescolerebbe in modo diverso in ogni campo, e lo studente si perderebbe.
4. **Campi dentro un blocco di codice: solo `<pre>`, mai `<pre><code>`.** Il `<code>` fa intervenire l'evidenziatore di sintassi, che toglie i campi. Se i campi stanno fuori dal codice, il blocco può avere `<code>`; il blocco `[[codice]]` della skill gestisce tutto da solo.
5. **Niente entità HTML nelle risposte dei campi a risposta breve e numerici.** Moodle confronta il testo del campo con quello digitato: `&lt;=` non coinciderà mai con `<=`. Nei feedback le entità vanno bene.
6. **Nessun tag nelle risposte.** Una risposta come `<form>` verrebbe letta come HTML. Metti il campo sul solo nome: `&lt;{1:SHORTANSWER:=form} action="…"&gt;`.
7. **Nei menù, l'apostrofo si scrive `'`** così com'è: `&#39;` o `&amp;#39;` arrivano allo studente come codice. Se un'opzione deve mostrare `<`, lì sì si scrive `&lt;`.

## Le famiglie

### Tracciamento

Una tabella di dati e una query (o un frammento di codice); lo studente prevede il risultato. **I campi stanno fuori dal codice**, nel testo sotto.

```text
<p>Data la tabella <strong>Libri</strong>:</p>
...tabella...
[[codice sql]]
SELECT Titolo FROM Libri WHERE Prezzo < 10 ORDER BY Titolo;
[[/codice]]
<p>La query restituisce {1:NUMERICAL:=2:0#Corretto: solo due libri costano meno di 10 euro.} righe.
La prima riga è {1:MULTICHOICE_S:=Il barone rampante#Corretto: è il primo in ordine alfabetico.~Il fu Mattia Pascal#No: costa 9.50 ma in ordine alfabetico viene dopo.~Il nome del vento#No: costa 12 euro, non passa la condizione.}.</p>
```

Le opzioni sbagliate dei menù sono gli **errori tipici**, e il feedback spiega perché sono sbagliate.

### Lettura dell'output

«Che cosa stampa questo codice?», «che cosa mostra il browser?». Campi numerici per contare (paragrafi, righe, richieste), menù per scegliere tra uscite plausibili. Come nel tracciamento, i campi stanno sotto il codice.

### Completamento e scrittura

Il codice con dei buchi: **i campi stanno dentro il blocco di codice**. Quasi sempre `SHORTANSWER`, oppure `MULTICHOICE_S` quando le alternative sbagliate insegnano qualcosa (`INTO`/`IN`/`TO`).

```text
[[codice php]]
<?php
{1:SHORTANSWER:=$}libri = 4;
{1:SHORTANSWER:=if} ($libri {1:SHORTANSWER:=>=} 3) {
    {1:SHORTANSWER:=echo} "<p>Omaggio!</p>";
}
?>
[[/codice]]
```

- Ogni buco è una parte che lo studente deve saper scrivere, non un dettaglio di battitura.
- Prevedi le varianti corrette con `~=`: percorsi equivalenti (`css/stile.css` e `./css/stile.css`), apici singoli o doppi, spazi facoltativi. Maiuscole e minuscole non servono: `SHORTANSWER` già le ignora.
- I caratteri `>` e `<=` nelle risposte si scrivono così come sono; un tag no (regola 6).

### Metti in ordine

Un elenco numerato, un menù per posizione, tutti con le stesse opzioni (regola 3):

```text
<ol>
<li>{1:MULTICHOICE:il browser legge l'HTML~=il browser invia la richiesta#Corretto.~il browser mostra la pagina~il server invia index.html}</li>
<li>{1:MULTICHOICE:il browser legge l'HTML~il browser invia la richiesta~il browser mostra la pagina~=il server invia index.html#Corretto.}</li>
<li>{1:MULTICHOICE:=il browser legge l'HTML#Corretto.~il browser invia la richiesta~il browser mostra la pagina~il server invia index.html}</li>
<li>{1:MULTICHOICE:il browser legge l'HTML~il browser invia la richiesta~=il browser mostra la pagina#Corretto.~il server invia index.html}</li>
</ol>
```

Le opzioni sono nello stesso ordine in ogni campo, e quell'ordine non è la sequenza giusta.

## Convenzioni

- Feedback della risposta giusta: «Corretto.» oppure «Corretto: » più il motivo, quando il motivo insegna qualcosa.
- Feedback delle sbagliate: «No: » più il perché.
- Penalità `0.3333333` per tentativo (predefinita nello script).
- Una Cloze tiene insieme campi sulla **stessa situazione**: se le domande sono indipendenti, meglio domande separate.
- Nel testo, dopo il codice, frasi complete in cui i campi si leggono come parte della frase.
