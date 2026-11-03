# Controllo delle somiglianze

Un passaggio automatico della correzione: aiuta l'utente a trovare gli studenti che potrebbero aver copiato. Si fa sempre, senza che l'utente lo chieda, con i punteggi già caricati. Il risultato sta nella vista **Somiglianze** della dashboard e in una riga del messaggio di consegna.

Sono **indizi da controllare, non prove**. Il controllo non dice chi ha copiato da chi, non distingue la copia da una fonte comune (un sito, un'IA) e non vede le copie di codice corretto e breve. **Non cambia punteggi e commenti**, e nei commenti agli studenti non se ne parla mai.

**Solo segnalazioni solide.** L'utente vuole poche segnalazioni fondate, non un elenco di sospetti: i casi deboli non si scrivono né nella pagina né in «da valutare». Se non c'è nulla di solido, si dice che il controllo è stato fatto e non ha trovato nulla: è un esito normale.

## Come si fa

1. **Esporta la verifica** con `ArtifactData list` di `domande`, `valutazioni` e `somiglianze`, con `out_dir`.
2. **Cerca i candidati**: `python3 scripts/controlla_somiglianze.py CARTELLA --uscita=candidati.json --dashboard=CARTELLA_QUIZ --quiz=ID`. Con `--dashboard` il codice delle soluzioni dell'autore non conta. Con `--salta=D03,D04` si tolgono le domande chiuse (risposta multipla, vero/falso, Cloze), dove una risposta uguale non dimostra nulla.
3. **Leggi ogni candidato**: le risposte per intero, con le regole qui sotto. Lo script trova anche molti falsi allarmi: è normale, e la decisione è tua.
4. **Scrivi le voci confermate** in `esito.json` (formato in fondo), anche `[]` se non resta nulla. Poi `python3 scripts/controlla_somiglianze.py CARTELLA --esito=esito.json --uscita=documento.json`.
5. **Carica** con un `set` di `verifiche/<id>/somiglianze/segnalazioni`, con `file_path` e, se il documento esiste già, `if_version`. Lo script conserva le decisioni già prese dall'utente («Da approfondire», «Scartata»): non si riscrivono, e una voce scartata non torna tra quelle da guardare.

## Risposte simili

Il codice corretto si assomiglia per forza, quindi non si cerca codice simile: si cercano **gli stessi errori rari e le stesse stranezze**. Lo script trova anche risposte intere quasi uguali.

**Contano**, e bastano da soli se sono chiari:
- lo stesso errore in un punto dove la classe sbaglia in modi diversi, presente solo in quei due o tre;
- le stesse righe inutili o senza senso, nello stesso ordine;
- lo stesso refuso poco comune, in almeno due punti;
- nomi o valori di una variante che lo studente non aveva, se non si spiegano altrimenti;
- risposte aperte quasi uguali, con le stesse frasi non prese dalla traccia.

**Non bastano da soli**, valgono solo insieme a un indizio forte: stessi testi nei `prompt`, stessi nomi di variabili non suggeriti dalla traccia, stessa struttura generale.

**Non contano:**
- codice corretto e breve;
- nomi, testi e numeri dettati dalla traccia;
- forme viste a lezione o nel materiale (`Number(prompt("Inserisci…"))`, `let conta = 0`);
- errori diffusi tra più studenti, anche se la spiegazione sbagliata è la stessa: è un'idea sbagliata comune, non una copia;
- risposte che si assomigliano in una parte e divergono nel resto, con due modi di scrivere diversi.

Prima di confermare guarda **come scrivono** i due studenti (spazi, punti e virgola, maiuscole, stile dei nomi): se è diverso, una parte in comune va spiegata meglio. Tre o più studenti con lo stesso indizio sono un'unica voce con tutte le sigle.

Se due studenti erano vicini in aula la coppia diventa più credibile, ma non si chiede l'informazione: lo valuta l'utente quando legge la segnalazione.

## Risposte fuori linea

Lo studente fa tutta la verifica sbagliando sempre le stesse cose, ma in una risposta è stranamente corretto. L'utente può poi aprire il log delle risposte del tentativo in Moodle.

Una risposta si segnala solo se valgono **insieme** queste due condizioni:

1. **Scarto alto**: è a punteggio pieno o quasi, molto sopra ciò che ci si aspetta da quello studente su quella domanda. Lo calcola lo script, tenendo conto della difficoltà della domanda.
2. **La stessa competenza sbagliata altrove**: la risposta usa correttamente proprio ciò che lo studente sbaglia in **almeno altre due** risposte. Per esempio sbaglia l'accumulatore in due esercizi e qui lo scrive perfetto. Lo decidi tu, leggendo la risposta e i commenti delle altre.

Lo scarto da solo non basta. Uno studente può essere bravo sulle funzioni e debole sugli array: una funzione perfetta non è incoerente con un array sbagliato, se quella funzione non usa gli array. Una domanda lasciata vuota non conta come errore.

**Rafforza la segnalazione**, ma non è obbligatorio: il modo di scrivere cambia di colpo (`stile_qui` e `stile_altrove`) oppure compaiono costrutti che non usa mai altrove (`nuovi_rispetto_al_resto`). Se lo studente ha scritto la risposta nel suo modo solito, con i suoi refusi, di solito è una cosa che sa fare.

## Come si scrive

Il `motivo` è una riga che dice **che cosa si vede**, con il codice tra apici inversi. Lo script rifiuta i motivi che parlano di copiature.

- Sì: «Stesso errore raro in D08 e D10: `dati.push[gg]`, con le quadre e con la variabile dei giorni.»
- Sì: «In D06 e D10 sbaglia l'accumulatore (`somma = gol + 1`), qui lo scrive corretto e con un altro stile.»
- No: «Hanno copiato», «Ha sicuramente preso la soluzione da un compagno».

Solo sigle, niente aggettivi che attribuiscano un genere allo studente.

## Formato di `esito.json`

```json
[
  {"tipo": "simili", "studenti": ["AL-IU", "BI-AN"], "domande": ["D08", "D10"],
   "motivo": "Stesso errore raro: …",
   "frammenti": {"D08": {"AL-IU": ["dati.push[gg]"], "BI-AN": ["dati.push[gg]"]}}},
  {"tipo": "fuori-linea", "studenti": ["CE-DA"], "domande": ["D10"], "confronto": ["D06", "D08"],
   "motivo": "In D06 e D08 sbaglia …, qui …"}
]
```

- `studenti` sono le chiavi delle righe, che restano uguali anche se la sigla viene rinominata.
- `domande`: per «simili» quelle in cui si vede l'indizio, per «fuori-linea» la risposta da controllare, una sola.
- `confronto`: le risposte in cui lo studente sbaglia la stessa cosa.
- `frammenti` (facoltativo): i pezzi da evidenziare nella pagina, di norma quelli che dà lo script.

## Nel messaggio di consegna

Una riga sola: «Controllo delle somiglianze: nessuna segnalazione» oppure «Controllo delle somiglianze: 2 segnalazioni, le trovi nella vista Somiglianze». Niente dettagli sugli studenti in chat, a meno che l'utente li chieda.
