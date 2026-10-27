# La dashboard «Correzione verifiche»

Una sola pagina privata per tutte le verifiche dell'utente, come la dashboard «Bozze dei quiz». Il codice sta in `assets/dashboard-correzioni.html`; i dati di ogni verifica stanno nel suo database, quindi la pagina si può aggiornare senza perdere le correzioni.

## Che cosa vede l'utente

- **Nuova correzione**, in cima all'elenco: l'utente trascina l'Excel «Risposte» di Moodle, anche con i nomi. La pagina apre il file nel browser (un `.xlsx` è uno zip di XML: `DecompressionStream`, nessuna libreria esterna; anche CSV), crea le sigle dalle colonne Cognome e Nome (prime due lettere, maiuscole, con un numero se due coincidono), scarta le altre colonne con dati personali, cancella il nome dello studente anche dentro le sue risposte. Facoltativo: la tabella Risposte incollata dal browser, abbinata per nome completo, che rimette i tag con `fondi()`. Dopo l'anteprima salva il documento della verifica (`origine: "dashboard"`, `stato: "da correggere"`), le domande (con `testi`, le tracce dell'export, una per variante; `max` e `tipo` li scrive poi Claude) e le valutazioni (`esito: "in attesa"`, punteggi vuoti, `variante` per le domande casuali), e apre la verifica.
- **Elenco delle verifiche**, dalla più recente: titolo, classe, numero di studenti, data e avanzamento della revisione. Le verifiche archiviate stanno in fondo, chiuse.
- Dentro una verifica, tre viste:
  - **Per domanda**: una scheda per domanda e gli studenti in ordine di cognome, come nell'export e in Valutazione manuale. In cima i criteri e che cosa fare in Moodle.
  - **Per studente**: una scheda per studente con tutte le sue domande, il totale e il voto. Serve per controllare il voto complessivo o per inserire dalla revisione del tentativo.
  - **Riepilogo voti**: punti di ogni domanda, totale, voto in decimi, media. Un clic su una riga apre lo studente. In fondo c'è il riquadro «Archivia o elimina la verifica»: l'archiviazione è reversibile, l'eliminazione chiede conferma nella pagina e cancella la verifica con tutte le sue domande e valutazioni.
- Ogni riga ha la risposta, l'esito dei test, il punteggio automatico stimato e la proposta («porta a 4,5»), il punteggio e il commento modificabili, «Copia punteggio», «Copia commento per Moodle» (frase sull'IA in corsivo e commento, come HTML: ogni riga del commento diventa un paragrafo, il codice tra apici inversi `<code>`, i blocchi ```js `<pre><code>`, il testo tra `**` grassetto; sotto il commento c'è l'anteprima), la spunta «Inserito in Moodle» dove serve. Una riga è a posto quando ha il punteggio e, se va riportata in Moodle, è segnata «Inserito»: le schede e l'elenco mostrano quante restano da inserire o senza punteggio.
- **Importa da Moodle**: si incolla la tabella «Risposte» copiata dal browser (con i tag HTML che l'export in Excel toglie). La pagina legge la tabella senza inserirla nel documento, trova i nomi (il link al profilo con il testo, non quello della foto), li converte nelle sigle provando tutte le divisioni del nome completo, cancella il nome anche dentro le risposte, e fa abbinare a mano quelli che non trova. La tabella copiata dal browser comprime spazi e a capo (il codice arriva su una riga, e in PHP un commento `//` nasconderebbe il resto): `fondi()` rimette i tag della tabella dentro a capo e rientri dell'export, e se il risultato perdesse anche un carattere tiene la versione copiata. Salva con un `update` per domanda solo `risposta` e `importata: true` delle righe scelte. Avvisa se qualche sigla resta senza tentativo (riga non copiata) o se ci sono tentativi non abbinati, che non si salvano. Propone le domande in cui il codice con i tag è diverso da quello dell'export (confronto senza spazi e a capo).
- **Aggiungi studenti da un altro export (versione PDP)**, nella stessa vista: l'utente trascina l'Excel «Risposte» della copia PDP del quiz, anche con i nomi (se li ha tolti, la pagina propone «PDP 1», «PDP 2»… e le sigle le scrive lui). La copia ha domande in più (la dichiarazione iniziale sulle mappe concettuali; le descrizioni «non svolgere» nell'export non compaiono) e tracce riscritte, quindi le colonne si abbinano alle domande della verifica **per somiglianza del testo** (parole e codice, Jaccard; sotto il 15% la colonna è ignorata), con un menù per correggere l'abbinamento. Le domande escluse non si ricavano dall'export (non ha i punti massimi): la pagina propone quelle vuote per tutti gli studenti PDP e quelle che nella copia non ci sono, e l'utente conferma. Salva le righe nuove con `update` (mai `set`) con `pdp: true`, `esclusa` e `variante` (la traccia della copia si aggiunge in fondo a `testi` della domanda), in coda nell'ordine, e aggiorna `studenti` nel documento della verifica.
- **Versione PDP nelle viste**: le righe escluse sono schede tratteggiate («esclusa dal PDP»), senza punteggio, mai da inserire in Moodle; la spunta «Esclusa dal PDP» nelle schede degli studenti PDP le cambia. Il voto di uno studente PDP è sul suo massimo ridotto (la somma dei massimi delle domande non escluse), come in Moodle se la copia ha gli stessi punti della verifica: dopo aver cambiato i punti in un quiz, vanno cambiati anche nell'altro. Nel riepilogo la cella esclusa è «×», il totale mostra il massimo ridotto e la sigla ha l'etichetta PDP; media e istogramma lasciano fuori chi non ha ancora nessun punteggio.
- I filtri «Solo le righe ancora da inserire in Moodle» e «Nascondi le risposte», e l'ordine degli studenti per cognome, crescente o decrescente («A → Z» / «Z → A»), come si può scegliere in Valutazione manuale. L'ordine vale in tutte e tre le viste e resta salvato nel browser.

Una riga è «da inserire» in Moodle se la domanda è a correzione manuale, oppure se la proposta è diversa dal punteggio automatico.

- Nel **riepilogo voti**, sotto la tabella, l'istogramma dei voti a fasce di mezzo voto (come quello di Moodle) con la linea della sufficienza, media, mediana e sufficienti; poi il resoconto della classe.

## Il database

| Collezione | Documento | Contenuto |
|---|---|---|
| `verifiche` | `<id>` (es. `v5r-5q`) | `titolo`, `sottotitolo`, `quiz` (id nella dashboard dei quiz), `studenti`, `disclaimer`, `creato` (AAAA-MM-GG), `archiviata`, `avanzamento` (lo aggiorna la pagina) |
| `verifiche/<id>/domande` | `D01`, `D02`… | `n`, `breve` (posizione nella dashboard), `titolo`, `max`, `tipo` (`manuale` o `auto`), `criteri` |
| `verifiche/<id>/valutazioni` | `D01`, `D02`… | `righe`: una mappa chiave dello studente → `s` (sigla), `ord`, `risposta`, `esito`, `auto`, `punti`, `commento`, `inserito`; per la versione PDP `pdp: true` ed `esclusa: true` sulle domande tolte (le verifiche più vecchie hanno anche `ok`, non più usato) |
| `verifiche/<id>/resoconti` | `studenti`, `classe` | `studenti`: `righe` (chiave → `testo`, `aggiornato`, `modificato`); `classe`: `testo`, `aggiornato`, `modificato`. Vedi `resoconti.md` |

Una domanda è un solo documento, con le righe degli studenti in una mappa: così il database si riempie con un batch e la pagina salva una riga con un `update` che tocca solo quella (`{righe: {"AL-IU": {punti: 4.5}}}`). L'`id` della verifica unisce il quiz e la classe, perché la stessa verifica si può correggere in più classi.

## Pubblicare la dashboard, la prima volta

1. `Artifact list`: se c'è già una pagina «Correzione verifiche», usa quella.
2. Altrimenti pubblica `assets/dashboard-correzioni.html` con `capabilities: {"db": {"rules": [{"path": "", "read": "admin", "write": "admin"}]}, "user": {}}`, cioè lettura e scrittura solo per chi può modificare la pagina, e icona `grade`.
3. Controllo: un `get` di un documento di `verifiche/<id>/valutazioni` con `as_level: "interact"` deve risultare inesistente.
4. Per aggiornare la pagina di una versione nuova del plugin: leggila con `Artifact read`, poi ripubblica l'asset sullo stesso `url`. I dati restano.

## Caricare una verifica

`ArtifactData batch` di `set` con le voci stampate da `prepara_revisione.py`: il documento della verifica, poi domande e valutazioni. Nella risposta all'utente: una frase sulla verifica caricata, le scelte da controllare, che cosa resta in attesa.

## Aggiornare una domanda dopo il caricamento

Per una domanda rimasta in attesa (l'HTML recuperato dopo): scrivi `voti/DNN.json` e lancia `prepara_revisione.py … --solo=DNN`. Se l'utente non l'ha ancora toccata, fai un `set` del documento con `if_version` (la versione la dà un `get`). Se l'ha già toccata, aggiorna con `update` solo le righe e i campi che cambiano: un `set` cancellerebbe le sue modifiche.

## Eliminare su richiesta

Se l'utente chiede a te di eliminare una verifica, prima rileggila e consegnagli la tabella dei voti (`riepilogo.py --csv`), poi cancella con un `batch` di `delete` i documenti di `verifiche/<id>/valutazioni`, `verifiche/<id>/domande` e infine `verifiche/<id>`: i documenti annidati non si cancellano da soli.

## Rileggere

`ArtifactData list` di `verifiche/<id>/domande` e `verifiche/<id>/valutazioni` con `out_dir`, poi `riepilogo.py` su quella cartella. Il punteggio che trovi è quello deciso dall'utente, che può averlo cambiato: non riscriverlo.
