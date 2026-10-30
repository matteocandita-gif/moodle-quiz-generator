# Installare e aggiornare l'editor «Mappe dei prerequisiti»

Ogni utente ha il suo editor: una pagina pubblicata come artifact privato, con il database delle sue mappe. La pagina sta in `assets/editor.html` di questa skill; le mappe stanno nel database della pagina (collezione `gerarchie`) e restano quando la pagina si ripubblica.

## Installare

Si fa quando l'utente lo chiede («installa l'editor delle mappe», comando `installa-mappe`) o quando serve l'editor e non c'è.

1. **Controlla che non ci sia già.** `Artifact` con `action: "list"`: cerca un artifact il cui titolo contiene «Mappe dei prerequisiti». Se c'è, non crearne un altro: passa ad «Aggiornare».
2. **Pubblica la pagina.** Copia `assets/editor.html` nella cartella di lavoro e pubblicala con `Artifact`, con `icon: "map"`, la `description` «Editor delle mappe dei prerequisiti: voci, collegamenti e backup per l'attività Database di Moodle.» e queste capacità:
   ```json
   {"db": {}, "downloads": true}
   ```
   L'URL del risultato è l'editor dell'utente.
3. **Facoltativo: una mappa di esempio.** Se l'utente vuole vedere com'è fatta una mappa, carica `references/esempio-html.json` con `ArtifactData` `set` (`collection: "gerarchie"`, `doc_id: "html"`, con in più `"creato"` e `"aggiornato"` uguali alla data e ora attuali e `"archiviato": false`). Altrimenti l'editor parte vuoto e propone «Crea la prima mappa».
4. **Verifica**: `ArtifactData` `list` di `gerarchie`.
4b. **Collega le pagine del plugin** seguendo `references/navigazione.md`: scrive in ogni pagina installata gli indirizzi delle altre, per la barra di navigazione in cima.
5. **Di' all'utente**, in poche righe: l'editor è pronto ed è visibile solo a lui; le mappe si salvano da sole; «Prova come studente» mostra la mappa come la vedrà la classe; «Scarica il backup per Moodle» dà lo `.zip` con il `.mbz` da ripristinare nel corso; in fondo alla pagina c'è la guida «Come portarla in Moodle».

## Aggiornare

Quando una nuova versione del plugin porta una pagina nuova (la costante `VERSIONE_PAGINA` in `assets/editor.html` è diversa da quella della pagina pubblicata), o quando l'utente lo chiede.

1. Leggi la pagina pubblicata (`Artifact`, `action: "read"`) e confronta `VERSIONE_PAGINA`. Se è uguale, non serve niente. Una pagina senza `VERSIONE_PAGINA` è precedente al plugin: va aggiornata.
2. Ripubblica `assets/editor.html` sullo **stesso URL**, senza `capabilities` (restano quelle salvate); se la pagina pubblicata non ha `db` e `downloads`, passale entrambe. Le mappe restano: stanno nel database, non nella pagina.
2b. **Collega le pagine del plugin** seguendo `references/navigazione.md`: scrive in ogni pagina installata gli indirizzi delle altre, per la barra di navigazione in cima.
3. Di' all'utente che cosa cambia nella pagina, in una riga. Le attività già create in Moodle non cambiano: per portare il nuovo codice in un'attività in uso si reimporta il preset (vedi SKILL.md).

Non modificare la pagina pubblicata a mano: le modifiche si fanno in `assets/editor.html` del plugin e arrivano a tutti con l'aggiornamento.
