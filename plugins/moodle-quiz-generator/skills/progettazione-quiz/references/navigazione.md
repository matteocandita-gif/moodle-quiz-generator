# Collegare le pagine del plugin (barra di navigazione)

Le pagine del plugin hanno in cima una barra discreta, «Quiz generator», con i link alle altre pagine dello stesso utente. Ogni link si apre in una nuova scheda; la pagina corrente è evidenziata e non è un link. Le pagine sono:

| Chiave | Pagina (titolo) | Skill che la installa |
|---|---|---|
| `bozze` | Bozze dei quiz | `progettazione-quiz` (`references/installazione.md`) |
| `tracce` | Tracce di progettazione | (in preparazione) |
| `correzioni` | Correzione verifiche | `correzione-verifiche` (`references/dashboard-correzioni.md`) |
| `mappe` | Mappe dei prerequisiti | `mappe-prerequisiti` (`references/installazione.md`) |

Ogni pagina ha un indirizzo diverso per ogni utente, e una pagina non può elencare gli artifact dell'utente: gli indirizzi li scrive Claude, nel database di ciascuna pagina, nel documento `impostazioni/navigazione`:

```json
{"pagine": {"bozze": "https://claude.ai/artifact/…", "correzioni": "https://claude.ai/artifact/…", "mappe": "https://claude.ai/artifact/…"},
 "altri": [],
 "aggiornato": "2026-10-30T09:40:00Z"}
```

La barra compare solo se c'è almeno un'altra pagina da raggiungere; senza il documento, o con la sola pagina corrente, la pagina resta com'era. La pagina corrente si riconosce dal titolo (il `<title>` della pagina comincia con il nome della tabella), quindi il link a se stessa nel documento non dà fastidio.

## Quando

Dopo ogni installazione o aggiornamento di una qualsiasi delle pagine, e quando l'utente chiede la barra o dice che un link non va. Una pagina nuova va aggiunta anche nelle altre: per questo si riscrive il documento in **tutte** le pagine installate, non solo in quella appena pubblicata.

## Come

1. **Trova le pagine.** `Artifact` con `action: "list"` (`limit: 50`): per ogni riga della tabella cerca l'artifact dell'utente il cui titolo comincia con il nome della pagina. Se ce n'è più d'uno, prendi quello fissato nella barra laterale, altrimenti il più recente, e dillo all'utente in una riga. Le pagine non trovate restano fuori.
2. **Scrivi il documento in ciascuna pagina trovata.** Con `ArtifactData`, sull'`url` della pagina: `get` di `impostazioni/navigazione`; se esiste, `update` con `if_version` di `pagine` e `aggiornato` (così restano gli `altri`); se non esiste, `set` con `pagine`, `altri: []` e `aggiornato`. Le chiavi di `pagine` sono quelle della tabella; ci vanno solo indirizzi `https://claude.ai/artifact/…`.
3. **Verifica**: un `get` del documento in una delle pagine.
4. **Di' all'utente** in una riga quali pagine sono collegate. Le pagine pubblicate prima della barra la mostrano solo dopo l'aggiornamento della pagina (lo propone la skill che la installa).

`altri` è per i link personali che l'utente chiede di aggiungere (per esempio una sua pagina di menù): una lista di `{"titolo": "…", "url": "https://…"}`, la stessa in tutte le pagine, mostrata in fondo alla barra dopo una linea. Non aggiungerne di tua iniziativa.

## Per chi modifica il plugin

Il codice della barra è uno solo, `sviluppo/strumenti/barra-navigazione.html`, e sta nelle pagine tra i commenti `<!-- barra-navigazione: inizio` e `<!-- barra-navigazione: fine -->`. Non si modifica dentro le pagine: si cambia l'originale e si lancia `python3 sviluppo/strumenti/allinea_copie.py` dalla radice del repository (poi, per l'editor delle mappe, `node sviluppo/mappe-prerequisiti/costruisci_editor.js`). Una pagina nuova del plugin: i due commenti subito sotto l'apertura del contenuto, la sua riga in `BLOCCHI` dello script, la sua chiave in `PAGINE` della barra e nella tabella qui sopra.
