# Gli altri tipi di domanda

Per ogni tipo: quando usarlo, come scriverlo, le impostazioni che lo script mette da solo (modificabili con `=== options`, vedi `formato-specifica.md`).

## Risposta multipla (`multichoice`)

Per i concetti brevi e per il **Trova l'errore**. Due varianti:

- **una sola giusta** quando l'affermazione vera è una: quattro opzioni, una corretta;
- **più giuste** quando le affermazioni vere sono più d'una (per esempio un trova l'errore con più errori): un'opzione per affermazione, 2 giuste e 2 sbagliate oppure 3 giuste e 3 sbagliate; mai una risposta singola con opzioni che ne mettono insieme diverse.

Per tutte e due:

- Le sbagliate sono **errori di ragionamento plausibili**, non riempitivi. Un'alternativa ugualmente corretta in programmazione (la concatenazione dove noi interpoliamo, un costrutto equivalente) non è mai un'opzione sbagliata.
- **Ogni opzione ha il suo feedback**: «Esatto: …» sulle giuste, «No: …» più il motivo sulle altre. È il feedback a insegnare.
- Opzioni di lunghezza simile: la più lunga e dettagliata non deve essere sempre quella giusta.
- Niente «tutte le precedenti» o «nessuna delle precedenti».

Con più giuste: `single: false` in `=== options`; le giuste si dividono il 100% (ad esempio nel caso di tre `=== answer 33.33333`), le sbagliate una penalità che sommata fa −100% (ad esempio nel caso di tre `=== answer -33.33333`), altrimenti chi spunta tutto prende il punteggio pieno. Il testo dice «Seleziona tutte le risposte corrette», perché l'istruzione standard è nascosta, e il feedback generale riporta la soluzione completa.

Impostazioni: risposta singola, opzioni mescolate, numerazione `abc`, istruzione standard nascosta, penalità `0.3333333`, punteggio 1.

```text
=== question multichoice
=== name
L1 - B4 - Trova l'errore: UPDATE senza WHERE
=== questiontext
<p>Il gestore vuole abbassare a 12 euro il prezzo del solo libro <em>Il nome del vento</em>, e scrive:</p>
[[codice sql]]
UPDATE Libri SET Prezzo = 12.00;
[[/codice]]
<p>Che cosa succede?</p>
=== answer 100
Tutti i libri passano a 12.00 euro, perché manca la clausola WHERE
=== feedback
Esatto: senza WHERE l'UPDATE vale per tutti i record.
=== answer 0
MySQL segnala un errore di sintassi, perché UPDATE richiede sempre WHERE
=== feedback
No: la query è sintatticamente corretta, ed è proprio questo il pericolo.
...
```

## Vero o falso (`truefalse`)

Per un'affermazione netta su un concetto. Feedback su entrambe le risposte, che spieghi il concetto in sé, non solo «giusto/sbagliato».

Impostazioni: penalità `1` (con due sole opzioni un secondo tentativo non vale nulla), punteggio 1. Si indica la risposta giusta con `correct: true` o `correct: false` in `=== options`.

```text
=== question truefalse
=== name
L2 - C3 - WHERE e HAVING
=== options
correct: true
=== questiontext
<p>WHERE filtra i singoli record prima del raggruppamento, mentre HAVING filtra i gruppi dopo il raggruppamento.</p>
=== feedback true
Esatto: per questo le condizioni sulle funzioni di aggregazione vanno in HAVING.
=== feedback false
No: è proprio questa la differenza tra WHERE e HAVING.
```

## Risposta breve (`shortanswer`)

Una sola parola o un nome (un comando, un tag, una funzione). Per più buchi nella stessa situazione usa una Cloze. Ogni variante accettata è una `=== answer 100`; maiuscole e minuscole ignorate salvo `usecase: 1`.

## Risposta aperta (`essay`)

Per l'**esercizio libero**: lo studente scrive i file (in XAMPP o nell'editor), li prova e incolla il codice. Correzione a mano.

- Nella consegna: i file da scrivere con il loro nome, che cosa deve fare ognuno, i dati da usare, come incollare (un blocco per file, con il nome del file sopra).
- `=== graderinfo`: le cose da controllare, una per riga, nell'ordine in cui le si guarda. Lo studente non le vede.
- Impostazioni: testo semplice (`plain`, adatto al codice), risposta obbligatoria, 25 righe, nessun allegato, punteggio 1 (alzalo con `defaultgrade` per gli esercizi lunghi).

## Descrizione (`description`)

Le pagine dentro il quiz: vedi `pagine.md`. Punteggio 0, nessuna risposta.

## Formato GIFT

Solo se l'utente lo chiede esplicitamente: nel corso per i colleghi è il formato «di livello 1» per chi inserisce domande semplici. Per il lavoro dell'utente il formato è sempre Moodle XML, che conserva HTML, feedback e categorie senza perdite.
