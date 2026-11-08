# Feedback per lo studente e griglia compilata

A correzione finita, su richiesta («prepara i feedback della verifica …»), un feedback complessivo per ogni studente. Va nel commento della **«Domanda per note e correzioni»** (la domanda da 0 punti che `materiali-moodle` mette all'inizio di ogni verifica), insieme alla griglia di valutazione compilata con i suoi punteggi: resta agli atti e lo studente lo vede nella revisione del tentativo. L'utente lo copia dalla vista «Feedback» della dashboard («Copia per Moodle»), in Valutazione manuale di quella domanda, per tutti gli studenti in una volta.

È diverso dal resoconto (`resoconti.md`), che è **per il docente**: diretto, con ipotesi sul perché. Il feedback è **per lo studente**: lo legge lui, e in caso di contestazione lo leggono la famiglia o il dirigente.

## Da dove si parte

Come per i resoconti: rileggi il database della verifica (`domande`, `valutazioni` con `out_dir`), perché punteggi e commenti sono quelli decisi dall'utente. Se ci sono già i resoconti, partono da lì le osservazioni, riscritte per lo studente. Il voto non si ripete nel testo: lo dice la griglia, sotto.

## Il testo

- Seconda persona, tono sereno e concreto: «Nella lettura del codice prevedi bene il risultato dei cicli; nel programma E1 manca il controllo del caso vuoto».
- Tre-cinque frasi, una per riga (ogni riga diventa un paragrafo in Moodle). Nell'ordine: che cosa è andato bene, con gli esercizi (T1, E2…); che cosa ha fatto perdere punti, per competenza (le stesse della griglia: conoscenze teoriche, lettura del codice, individuazione degli errori, scrittura del codice); una o due cose da riprendere, concrete.
- Gli errori ricorrenti valgono più dei singoli: «in due esercizi stampi il risultato invece di restituirlo con `return`».
- Il codice tra apici inversi, come nei commenti delle domande; niente blocchi lunghi.
- Niente ipotesi sulle cause («forse non hai studiato», «probabilmente il tempo»), niente confronti con la classe o con altri studenti, niente riferimenti alle somiglianze tra le risposte (sono decisioni del docente, non del feedback). Niente aggettivi o participi che attribuiscano un genere: si parla della prova o delle azioni («la prova si ferma a metà dell'E2», «hai lasciato vuoto il D1»).
- Per gli studenti PDP non si nomina il PDP: la riduzione la mostra la griglia («Riduzione dei contenuti per PDP: tolti …»). Il feedback parla solo degli esercizi che ha svolto.
- Domande lasciate vuote: si dicono, senza giudizio, e diventano una delle cose da riprendere.

La frase sull'IA («Il seguente feedback è stato scritto con l'aiuto di una IA generativa…») la aggiunge la pagina in testa, come nei commenti: non scriverla nel testo.

## La griglia

Non si scrive: la calcola la pagina, per ogni studente, con il modulo `griglia.js` (righe per competenza, livello evidenziato in base ai punti, totale e voto al mezzo voto). Le righe vengono da:

1. la griglia salvata nella verifica (campo `griglia` del documento `verifiche/<id>`): quella della dashboard «Bozze dei quiz», copiata al caricamento con `prepara_revisione.py --griglia=CARTELLA/quiz/ID.json` (con `--unisci` si applica `revisione/griglia.json` con un `update` del documento della verifica);
2. altrimenti la proposta della pagina, dalle tipologie e dalle posizioni delle domande (la parte avanzata non è una competenza).

Le verifiche precedenti alla griglia nella dashboard dei quiz non hanno né `griglia` né `tipologia`: la pagina lascia senza competenza le domande con la sola posizione generica («D6») e lo segnala nel riquadro «Griglia della verifica», dove l'utente assegna ogni domanda a una competenza (vale solo per quella verifica). Se l'utente ti chiede la griglia di una verifica vecchia, proponi tu l'assegnazione leggendo le tracce e scrivila nel campo `griglia` (`{righe: [{area, tipo, descrittori: null, pos: ["T1", …]}], origine: "pagina"}`), con le quattro competenze di `griglia.js` (`COMPETENZE`).

Per gli studenti PDP la griglia è quella della copia: esercizi tolti barrati, massimo della riga e totale ridotti, «Non valutata» per una competenza con tutti gli esercizi tolti. Il voto è punti / massimo ridotto × 10.

## Dove si salva

Nella collezione `verifiche/<id>/resoconti`, documento `feedback`: `righe`, una mappa chiave dello studente → `testo`, `aggiornato` (AAAA-MM-GG), `modificato: false`, `inserito: false`. La prima volta `set`; poi `update` con `ifVersion` e solo le righe che cambiano. Se una riga ha `modificato: true` l'utente l'ha corretta dalla pagina: non riscriverla senza chiedere. `inserito` lo segna l'utente: non toccarlo. Se i punteggi cambiano dopo, la griglia si aggiorna da sola; il testo va rivisto solo se cita qualcosa che non è più vero.
