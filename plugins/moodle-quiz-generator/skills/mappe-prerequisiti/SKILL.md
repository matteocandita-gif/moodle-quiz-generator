---
name: "mappe-prerequisiti"
description: "Mappe dei prerequisiti (gerarchie di apprendimento) per l'autovalutazione degli studenti in Moodle: scompone un traguardo in competenze minime collegate da prerequisiti, le carica nell'editor «Mappe dei prerequisiti» e crea il backup .mbz di un'attività Database pronta da ripristinare, in cui lo studente spunta ciò che sa fare e il docente vede il riepilogo della classe. Usala per «una mappa dei prerequisiti su…», «l'albero delle competenze di…», «la learning hierarchy di…», «crea il .mbz della mappa», «installa l'editor delle mappe»."
---

# Mappe dei prerequisiti

**Lingua.** Rispondi all'utente sempre in italiano, anche quando il messaggio che avvia la skill o il comando è in inglese: quando si sceglie un comando o una skill dal menù senza scrivere nulla, l'app aggiunge da sola una frase in inglese.

Una mappa dei prerequisiti (in letteratura: gerarchia di apprendimento, Gagné) scompone un traguardo nelle sue competenze minime e le collega per prerequisiti. In Moodle diventa un'attività **Database**: lo studente apre la mappa, spunta le voci che sa fare e vede quali è pronto a imparare; il docente, nella vista elenco, vede il riepilogo della classe (quanti sanno fare ogni voce, chi è pronto, chi no) e la tabella degli studenti.

Non è un quiz: non passa dalla dashboard «Bozze dei quiz» né da `progettazione-quiz`.

## Le parti

| Parte | Dove | A che cosa serve |
|---|---|---|
| Editor «Mappe dei prerequisiti» | artifact privato dell'utente, pubblicato da `assets/editor.html` | l'utente crea e corregge le mappe, prova la vista dello studente, scarica backup e preset |
| Database dell'editor | collezione `gerarchie`, un documento per mappa (id = slug del titolo) | le mappe dell'utente |
| `scripts/crea_mbz.js` | questa skill | crea il backup `.mbz` di una mappa, con il codice preso da `assets/editor.html` |
| `references/installazione.md` | questa skill | installare o aggiornare l'editor |
| `references/esempio-html.json` | questa skill | una mappa vera (HTML, quarta SIA) come esempio di formato e di granularità |

**L'editor dell'utente.** Cercalo con `Artifact` (`action: "list"`, titolo «Mappe dei prerequisiti»). Se non c'è, installalo (`installazione.md`); se ne trovi più d'uno, chiedi quale. Se la `VERSIONE_PAGINA` della pagina pubblicata è più vecchia di quella di `assets/editor.html`, proponi l'aggiornamento (`installazione.md`, «Aggiornare»).

## Formato di una mappa

```json
{
  "titolo": "Progettazione di un database: le basi",
  "descrizione": "una riga",
  "vincoli": true,
  "nodi": [
    {"id": "en", "titolo": "Entità e istanze", "sotto": "classe di oggetti, rettangolo", "tipo": "scrivere", "pre": []},
    {"id": "at", "titolo": "Attributi", "sotto": "nome e dominio", "tipo": "scrivere", "pre": ["en"]}
  ]
}
```

- `id`: codice breve e **fisso**. Le spunte degli studenti sono salvate per id: in una mappa già in uso non si rinomina né si riusa un id per un'altra voce.
- `titolo` e `sotto`: il nome della voce e una riga concreta sotto (tag, simboli, un esempio).
- `tipo`: `scrivere` (saperlo produrre) o `leggere` (saperlo leggere e capire: bordo tratteggiato). La legenda mostra i due tipi solo se la mappa li usa entrambi.
- `pre`: gli id dei prerequisiti **diretti**, senza cicli. Non ripetere quelli già impliciti in un prerequisito.
- `vincoli`: `true` (predefinito) se lo studente può spuntare una voce solo dopo i suoi prerequisiti; togliendo una spunta si tolgono anche le voci che la richiedono.

Nel database dell'editor ogni mappa ha in più tre campi di gestione, che non vanno nel backup:

- `creato`: data e ora ISO di creazione, **obbligatoria** anche quando la mappa la crei tu in chat. L'editor elenca le mappe dalla più recente alla più vecchia secondo `creato`; una mappa senza data finisce in fondo.
- `aggiornato`: data e ora ISO dell'ultima modifica.
- `archiviato`: `true` se la mappa è archiviata: esce dalle mappe attive e compare in fondo al menù, tra le archiviate.

## Costruire una mappa

1. **Parti dal materiale dell'utente**: capitoli del libro, programmi, appunti. Se manca, chiedilo. Chiedi anche la classe e il modulo o periodo dell'anno.
2. **Scomponi in competenze minime**, una per voce: ciò che si può verificare da solo. Il traguardo finale è una voce in fondo che richiede le voci principali. Una mappa può avere più traguardi (per esempio uno di scrittura e uno di lettura).
3. **Collega per prerequisiti diretti.** Le frecce che attraversano argomenti diversi (una regola di traduzione che richiede un concetto dello schema E/R) sono le più utili: tienile.
4. **Non assegnare livelli**: la pagina li calcola dalla catena di prerequisiti. Conta la progressione, non il numero di livelli né la corrispondenza con le lezioni.
5. **Dimensione.** Titoli brevi (circa 22 caratteri al massimo), così la mappa resta leggibile intorno agli 800 px dello spazio di Moodle. Tieni una mappa intorno alle 25 voci: oltre, le frecce si intrecciano. Per un argomento più grande dividi **per modulo o periodo dell'anno**, non per fase o capitolo, perché la divisione taglierebbe le frecce tra le parti; nella seconda mappa metti una voce di partenza che riassume la prima (per esempio «Le basi della progettazione»).
6. **Proponi la mappa all'utente** prima di produrre il backup: le voci e i collegamenti si discutono, e l'utente li corregge anche direttamente nell'editor.

## Caricare la mappa nell'editor

`ArtifactData` `set` con l'URL dell'editor, `collection: "gerarchie"`, `doc_id` = slug del titolo (minuscole, lettere e cifre separate da trattini, senza accenti), dati = la mappa con in più `"creato"` e `"aggiornato"` uguali alla data e ora attuali (ISO) e `"archiviato": false`. Per riscrivere una mappa esistente leggila prima, passa il suo `version` come `if_version` e conserva `creato` e `archiviato`. L'editor aperto mostra da solo una mappa nuova che quel browser non ha ancora visto: non serve dire all'utente di cercarla nel menù. Digli che lì può correggerla e provarla con «Prova come studente».

**Archiviare ed eliminare.** In fondo all'editor, il riquadro «Archivia o elimina la mappa» (chiuso) archivia o riattiva la mappa (campo `archiviato`) oppure la elimina definitivamente, con un secondo clic di conferma. Le attività già create in Moodle non cambiano. Se l'utente ti chiede di eliminare una mappa, prima salvane una copia (`ArtifactData` `get` con `out_dir`, consegnata all'utente come file JSON), poi `delete`. Non archiviare né eliminare una mappa di tua iniziativa.

## Creare il backup .mbz

1. **Leggi la mappa attuale dall'editor**, perché l'utente può averla corretta: `ArtifactData` `get` (`collection: "gerarchie"`, `doc_id`) oppure `list`, con `out_dir` nella cartella di lavoro. Se la mappa esiste solo in chat, scrivila in un file JSON.
2. **Lancia lo script** (serve Node):
   ```
   node <cartella della skill>/scripts/crea_mbz.js <mappa.json> <cartella-uscita> "Nome dell'attività"
   ```
   Il nome è facoltativo (predefinito: il titolo della mappa). Lo script controlla la mappa (id ripetuti, prerequisiti inesistenti, cicli) e si ferma se non va; scrive `<slug>.mbz` e stampa il numero di voci e la larghezza della mappa. Se la larghezza supera di molto i 1000 px, proponi di accorciare i titoli o di dividere la mappa.
3. **Consegna il file** `.mbz` con SendUserFile.

Il backup contiene un'attività Database già impostata: approvazione richiesta (ogni studente vede solo la propria scheda; il docente non approva nulla e vede tutto), una scheda per studente, modalità gruppo «Nessun gruppo», sezione 0 (Generale), senza dati utente. Il campo si chiama `voci` e contiene gli id spuntati.

L'editor ha lo stesso codice: il pulsante «Scarica il backup per Moodle» dà uno `.zip` con dentro il `.mbz` (il browser non può salvare file `.mbz`), «Preset» dà il preset dell'attività.

## Che cosa dire all'utente

- **Attività nuova:** nel corso, Altro → Ripristino, carica il `.mbz` e ripristinalo nel corso attuale. Nome e sezione si cambiano dopo.
- **Attività già in uso:** non ripristinare un nuovo backup, che creerebbe un'attività vuota. Scarica il «Preset» dall'editor e importalo nella stessa attività (scheda Preset), confermando il campo `voci`: le spunte restano. I browser possono mostrare la mappa precedente fino a 10 minuti.
- **Gli studenti non vedono «Aggiungi scheda»:** quasi sempre è la modalità gruppo. Con i gruppi separati chi non è in un gruppo non può aggiungere schede; se il corso forza la modalità gruppo, va cambiata nelle impostazioni del corso. Altre cause: un periodo di sola lettura nelle impostazioni dell'attività, o una scheda già presente (massimo una).
- **Riepilogo incompleto:** il riepilogo conta le schede della pagina della vista elenco; con più di 10 studenti la pagina mostra il link «Mostra tutte le schede in una pagina».
