# Regole per dati di prova buoni

## Coerenza

I dati devono essere credibili per uno studente che li legge: un errore di coerenza distrae dall'esercizio e toglie fiducia nei risultati.

- **Persone**: nomi e cognomi italiani combinati a caso (anche cognomi di famiglie di origine straniera, come nelle classi vere); nazionalità coerente con il nome (`persona_estera`); email ricavate dal nome; età coerente con il ruolo (studenti di terza 16-17 anni, docenti 28-65).
- **Tempo**: le date seguono il mondo (restituzione dopo il prestito, consegna dopo l'ordine, nascita prima dell'assunzione); gli anni scolastici vanno da settembre a giugno; niente date future rispetto all'anno scolastico in corso, salvo scadenze.
- **Quantità**: i totali derivati, se esistono come colonne, coincidono con il calcolo (meglio non salvarli: si calcolano con le query); le giacenze non diventano negative; i prestiti aperti non superano le copie.
- **Luoghi**: comuni con la provincia e il CAP giusti (lista in `dati_it.py`), con una prevalenza della provincia di Bologna quando il contesto è locale.
- **Distribuzioni**: non uniformi come un dado; qualche cliente con molti ordini e molti con pochi, prezzi con valori tondi e no, categorie di dimensioni diverse.
- **Niente persone reali**: niente nomi di personaggi famosi, di studenti o colleghi; domini email inventati (`studenti.istituto.it`, `azienda.example.it`) o generici.

Ogni regola di coerenza importante diventa un `CONTROLLO` del modello: la costruzione si ferma se i dati la violano.

## Trappole: righe che smascherano gli errori tipici

Un database di prova serve anche a distinguere le risposte giuste da quelle sbagliate. Ogni modello semina, in tutte le taglie:

| Errore dello studente | Righe che lo smascherano |
|---|---|
| JOIN interna dove serve la LEFT JOIN | un padre senza figli (autore senza libri, cliente senza ordini) |
| condizione di JOIN dimenticata o sui campi sbagliati | più righe nelle tabelle collegate, chiavi numeriche che non coincidono per caso tra tabelle diverse |
| `= NULL` al posto di `IS NULL`, COUNT(colonna) al posto di COUNT(*) | colonne facoltative con alcuni NULL |
| `>` al posto di `>=` | valori esattamente sui confini tipici: inizio e fine mese, anno 2000, prezzi tondi (10, 50, 100), soglie che le tracce useranno |
| GROUP BY sul nome invece che sulla chiave | due omonimi (stesso nome e cognome, chiave diversa) |
| HAVING sbagliato | un gruppo con esattamente la soglia tipica (2 elementi) |
| LIKE con il `%` al posto sbagliato, `=` al posto di LIKE | un testo cercato all'inizio e uno in mezzo, con maiuscole diverse |
| WHERE dimenticata in UPDATE e DELETE | righe che la condizione deve escludere e che il test mostra |
| DISTINCT dimenticato | righe che si ripetono nel risultato di una JOIN |
| ordinamento dimenticato | ordine di inserimento diverso dall'ordine richiesto (inserisci per chiave, chiedi l'ordine per nome o per data) |
| JOIN inutile in una query su una tabella sola | righe del padre senza figli (spariscono) e con più figli (si ripetono): la JOIN dà dati sbagliati |
| data sbagliata tra due tabelle | due date con significati diversi (iscrizione del socio e data della riga nella tabella ponte, tessera del cliente e data del biglietto): filtrare l'una al posto dell'altra cambia il risultato |
| confronto tra stringhe sensibile alle maiuscole | valori scritti sempre allo stesso modo nel database (le tracce citano i valori esatti) |

**Pari merito.** CodeRunner confronta le righe nell'ordine: se due righe sono alla pari nelle chiavi dell'ordinamento richiesto, una risposta giusta può darle nell'ordine opposto ed essere segnata sbagliata. Le chiavi usate per ordinare nelle tracce (cognome, data, totale di un gruppo) devono avere valori distinti nelle righe che la domanda restituisce, salvo che la traccia dica il secondo criterio. `verifica_query.py` segnala i pari merito sull'ORDER BY della soluzione (se la soluzione aggiunge un secondo criterio che la traccia non dice, il controllo non lo vede: guardalo tu).

Le trappole generali stanno nel modello; quelle di una singola domanda (un confine scelto dalla traccia) si aggiungono al database del quiz con poche INSERT o UPDATE in fondo allo script, commentate (`-- righe aggiunte per L5 - B3`, `-- spareggio per Q3a`), oppure nel modello se serviranno ancora.

## Database paralleli per le varianti di una verifica

Nelle verifiche ripetibili ogni variante di una posizione usa un database diverso (variante a, b, c), ma le domande devono essere equivalenti. Si costruiscono modelli **paralleli**: stessa forma (per esempio una relazione 1-N più una N-N con la tabella ponte, quattro tabelle), stessi tipi di colonne nelle stesse posizioni, stesse trappole nelle stesse quantità (padri senza figli, omonimi, confini dell'anno, NULL, una data di iscrizione distinta dalla data della tabella ponte), contesti diversi (palestra, cinema, ambulatorio veterinario). La scheda di ognuno elenca le trappole con le stesse frasi, così si controlla a colpo d'occhio che una query della variante a abbia la sua gemella nella b e nella c.

## Taglie

| Taglia | Righe per tabella | Quando |
|---|---|---|
| piccolo | 5-15 | primi esercizi su un argomento, debug, verifiche in cui lo studente controlla a mano il risultato |
| medio («realistico») | 20-50 | la taglia di default: esercitazioni, verifiche, attività in phpMyAdmin |
| grande | ~100 e oltre nelle tabelle dei fatti (prestiti, ordini, voti) | casi eccezionali: far vedere che cosa vuol dire lavorare su un database grande (LIMIT, conteggi, indici, ordinamenti) |

Le taglie condividono lo schema e le trappole; i dati cambiano. In CodeRunner il risultato atteso di una SELECT su una tabella grande diventa lunghissimo: con la taglia grande chiedi conteggi, aggregati, LIMIT o filtri stretti.
