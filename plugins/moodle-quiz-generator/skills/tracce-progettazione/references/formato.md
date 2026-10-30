# Il formato della traccia

Una traccia è un documento JSON: lo stesso che sta nella dashboard (collezione `tracce`, vedi `dashboard.md`) e che `scripts/uscite_traccia.js` trasforma in Word e HTML. Il testo è diviso in **blocchi**; ogni uscita li monta sempre nello stesso ordine.

```json
{
  "titolo": "Piattaforma di streaming",
  "breve": "streaming serie TV",
  "classe": "5R",
  "uso": "verifica",
  "data": "2026-11-12",
  "preset": "intermedio",
  "opzioni": {"entita": "5-6", "nn": "1-2", "uno_uno": "no", "ricorsiva": "no", "debole": "no", "isa": "no",
              "opzionali": "sì", "ristrutturare": 1, "chiavi": "in parte", "testo": "intermedio", "ipotesi": 2,
              "documentazione": "sì", "sql_tabelle": "no", "query": 3, "gradino": 2, "requisiti_query": 0, "php": "no"},
  "testo": {
    "premessa": "",
    "realta": "Si vuole gestire il database di una piattaforma di streaming…\n\nDi ogni regista interessano…",
    "presentare": {"documentazione": true, "sql_tabelle": false},
    "requisiti_query": false,
    "query": [
      {"testo": "Elenco di tutti gli attori che hanno partecipato a una serie TV diretta dal regista 'Martin Scorsese'",
       "gradino": 1, "requisito": "partecipazione degli attori agli episodi (N a N) e regista della serie"}
    ],
    "php": null
  },
  "pdp": {"riduzioni": {"presentare.documentazione": "Riduzione contenuti per PDP: fornire solo la prima riga delle tabelle di documentazione"}},
  "griglia": {"pesi": null},
  "verifica": {"intestazione": "5 SIA Verifica Modello E/R", "griglia": true},
  "docente": {
    "costrutti": ["N a N con attributo (ruolo da protagonista)", "1 a N", "attributi opzionali", "dato derivato (costo della serie)"],
    "ipotesi_attese": ["un attore può avere più ruoli nello stesso episodio? (la traccia non lo dice)", "…"],
    "punti_delicati": ["il regista dell'episodio può essere diverso da quello della serie: due associazioni distinte"],
    "durata": "70 minuti",
    "er": "titolo: Piattaforma di streaming\n…"
  }
}
```

| Campo | Significato |
|---|---|
| `titolo` | titolo del contesto, in testa alla traccia |
| `breve` | due o tre parole per il nome dei file (`5R-NOV-2026-streamingSerieTV.docx`) |
| `classe`, `data` | per l'intestazione e il nome dei file (mese e anno dalla data) |
| `uso` | `verifica` (Word con griglia), `compito` (HTML per la descrizione del Compito), `esercizio` (HTML, in classe), `esame` (simulazione: premessa e «Il candidato… sviluppi:») |
| `testo.premessa` | solo per `esame`: la premessa sul settore, prima del caso |
| `testo.realta` | la realtà; un paragrafo per riga vuota; `**grassetto**` e `*corsivo*` ammessi ma da usare poco |
| `testo.presentare` | che cosa consegnare oltre a E/R e schema relazionale (sempre presenti): `documentazione` (predefinito sì), `sql_tabelle` |
| `testo.requisiti_query` | `true` quando una query aggiunge un requisito: la consegna dice «tenendo conto anche delle informazioni richieste dalle query» |
| `testo.query` | le query: `testo` come lo leggono gli studenti, `gradino` (1-3), `requisito` che verificano (solo per il docente) |
| `testo.php` | `null` oppure `{"testo": "…", "connessione": "…"}`: la richiesta e i dati di connessione (o «Dati per la connessione a scelta del candidato.») |
| `pdp.riduzioni` | per la copia PDP: una frase in grassetto sotto il punto ridotto. Chiavi: `presentare.er`, `presentare.documentazione`, `presentare.relazionale`, `presentare.sql_tabelle`, `query.N` (dalla 1), `php` |
| `griglia.pesi` | `null` per i pesi predefiniti, oppure i pesi della verifica (`griglia.md`) |
| `verifica` | `intestazione` (predefinita «5 SIA Verifica Modello E/R», dalla prima cifra della classe); `griglia: false` per un Word senza griglia |
| `docente` | note per il docente, mai nelle uscite per gli studenti: costrutti, ipotesi attese (le ipotesi intere di SKILL.md; minime, vincoli e chiavi da scegliere vanno nei punti delicati), punti delicati, durata, il `.er` del modello bersaglio |

## Le uscite

`node scripts/uscite_traccia.js TRACCIA.json --word --pdp --html` (con un nome di file dopo l'opzione, oppure il nome standard). Prima di scrivere controlla il JSON: gli **errori** (titolo, realtà o query mancanti) fermano lo script, gli **avvisi** (query senza requisito, griglia che non fa 100, riduzione con una chiave sconosciuta) vanno letti e risolti o riferiti.

- **Word della verifica**: intestazione, riga di Nome, Data e Classe, titolo, realtà, «Presentare:» con l'elenco, le query, «Scrivere le query SQL che rispondono a queste domande.», la pagina PHP se c'è, la nota sull'ordine (corsivo) e quella sulle scelte dello studente (grassetto). Poi, su una pagina orizzontale, la griglia e la regola del voto.
- **Word PDP**: come sopra, più le riduzioni in grassetto sotto i punti indicati, il promemoria delle colonne della documentazione (solo nella copia PDP) e la frase «…tenendo conto dei criteri di valutazione personalizzata previsti dal PDP» sopra la griglia.
- **HTML per Moodle** (descrizione di un Compito): **eccezione allo stile delle pagine Moodle**, per scelta dell'utente. La traccia deve avere lo stesso aspetto del Word della verifica, perché gli studenti la ritrovino uguale: niente colori, riquadri o stili, solo paragrafi, elenchi numerati, grassetto per le istruzioni e il titolo del contesto, nello stesso ordine del Word, senza intestazione e griglia. In fondo la riga **Consegna** (le foto dei fogli se si lavora su carta, altrimenti un unico file Word completo).
- Prima di consegnare un Word, convertilo in PDF e guarda le pagine (`soffice --headless --convert-to pdf`, poi `pdftoppm`): righe che vanno a capo male, la griglia che esce dalla pagina.

- **Soluzione** (Word e HTML): `--soluzione-word [FILE] --soluzione-html [FILE] --png DIAGRAMMA.png`, dal campo `soluzione` (`dashboard.md`). Il Word: traccia e ipotesi su pagina verticale, diagramma e documentazione su pagina orizzontale, poi schema relazionale e query (in Consolas). L'HTML è una pagina sola con il diagramma dentro.

La dashboard usa lo stesso file: `UsciteTraccia.docx(traccia, {pdp})` restituisce i byte del `.docx`, `UsciteTraccia.html(traccia)` il frammento HTML, `docxSoluzione(traccia, png)` e `htmlSoluzione(traccia, png)` la soluzione (png = byte del diagramma o `null`), `UsciteTraccia.nomeFile(traccia, {pdp})` il nome.
