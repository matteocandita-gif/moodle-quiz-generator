# La dashboard «Correzione verifiche»

Una sola pagina privata per tutte le verifiche dell'utente, come la dashboard «Bozze dei quiz». Il codice sta in `assets/dashboard-correzioni.html`; i dati di ogni verifica stanno nel suo database, quindi la pagina si può aggiornare senza perdere le correzioni.

## Che cosa vede l'utente

- **Nuova correzione**, in cima all'elenco: l'utente trascina l'Excel «Risposte» di Moodle, anche con i nomi. La pagina apre il file nel browser (un `.xlsx` è uno zip di XML: `DecompressionStream`, nessuna libreria esterna; anche CSV), crea le sigle dalle colonne Cognome e Nome (prime due lettere, maiuscole, con un numero se due coincidono), scarta le altre colonne con dati personali, cancella il nome dello studente anche dentro le sue risposte. Facoltativo: la tabella Risposte incollata dal browser, abbinata per nome completo, che rimette i tag con `fondi()`. Dopo l'anteprima salva il documento della verifica (`origine: "dashboard"`, `stato: "da correggere"`), le domande (con `testi`, le tracce dell'export, una per variante; `max` e `tipo` li scrive poi Claude) e le valutazioni (`esito: "in attesa"`, punteggi vuoti, `variante` per le domande casuali), e apre la verifica.
- **Elenco delle verifiche**, dalla più recente: titolo, classe, numero di studenti, data e avanzamento della revisione. Le verifiche archiviate stanno in fondo, chiuse.
- Dentro una verifica, tre viste:
  - **Per domanda**: una scheda per domanda e gli studenti in ordine di cognome, come nell'export e in Valutazione manuale. In cima i criteri e che cosa fare in Moodle.
  - **Per studente**: una scheda per studente con tutte le sue domande, il totale e il voto. Serve per controllare il voto complessivo o per inserire dalla revisione del tentativo.
  - **Riepilogo voti**: punti di ogni domanda, totale, voto in decimi, media. Un clic su una riga apre lo studente. In fondo c'è il riquadro «Archivia o elimina la verifica»: l'archiviazione è reversibile, l'eliminazione chiede conferma nella pagina e cancella la verifica con tutte le sue domande e valutazioni.
- Ogni riga ha la risposta, l'esito dei test, il punteggio automatico stimato e la proposta («porta a 4,5»), il punteggio e il commento modificabili, «Copia punteggio», «Copia commento per Moodle» (frase sull'IA in corsivo e commento, come HTML: ogni riga del commento diventa un paragrafo), la spunta «Inserito in Moodle» dove serve. Una riga è a posto quando ha il punteggio e, se va riportata in Moodle, è segnata «Inserito»: le schede e l'elenco mostrano quante restano da inserire o senza punteggio.
- **Importa da Moodle**: si incolla la tabella «Risposte» copiata dal browser (con i tag HTML che l'export in Excel toglie). La pagina legge la tabella senza inserirla nel documento, trova i nomi (il link al profilo con il testo, non quello della foto), li converte nelle sigle provando tutte le divisioni del nome completo, cancella il nome anche dentro le risposte, e fa abbinare a mano quelli che non trova. La tabella copiata dal browser comprime spazi e a capo (il codice arriva su una riga, e in PHP un commento `//` nasconderebbe il resto): `fondi()` rimette i tag della tabella dentro a capo e rientri dell'export, e se il risultato perdesse anche un carattere tiene la versione copiata. Salva con un `update` per domanda solo `risposta` e `importata: true` delle righe scelte. Avvisa se qualche sigla resta senza tentativo (riga non copiata) o se ci sono tentativi non abbinati, che non si salvano. Propone le domande in cui il codice con i tag è diverso da quello dell'export (confronto senza spazi e a capo).
- I filtri «Solo le righe ancora da inserire in Moodle» e «Nascondi le risposte», e l'ordine degli studenti per cognome, crescente o decrescente («A → Z» / «Z → A»), come si può scegliere in Valutazione manuale. L'ordine vale in tutte e tre le viste e resta salvato nel browser.

Una riga è «da inserire» in Moodle se la domanda è a correzione manuale, oppure se la proposta è diversa dal punteggio automatico.

## Il database

| Collezione | Documento | Contenuto |
|---|---|---|
| `verifiche` | `<id>` (es. `v5r-5q`) | `titolo`, `sottotitolo`, `quiz` (id nella dashboard dei quiz), `studenti`, `disclaimer`, `creato` (AAAA-MM-GG), `archiviata`, `avanzamento` (lo aggiorna la pagina) |
| `verifiche/<id>/domande` | `D01`, `D02`… | `n`, `breve` (posizione nella dashboard), `titolo`, `max`, `tipo` (`manuale` o `auto`), `criteri` |
| `verifiche/<id>/valutazioni` | `D01`, `D02`… | `righe`: una mappa chiave dello studente → `s` (sigla), `ord`, `risposta`, `esito`, `auto`, `punti`, `commento`, `inserito` (le verifiche più vecchie hanno anche `ok`, non più usato) |
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
