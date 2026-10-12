# Changelog

Le novità di ogni versione di «Moodle: quiz generator». Le righe segnate **Dashboard** cambiano la pagina «Bozze dei quiz»: Claude propone di aggiornarla, e i quiz salvati restano.

## 0.3.4 — 12/10/2026

- Snippet HTML con l'anteprima accanto: un blocco ```` ```html anteprima ```` mostra il codice e, a fianco, come lo mostra il browser (nella dashboard e in Moodle). Regola didattica in `progettazione-quiz`: nella pagina di teoria la prima volta che compaiono tag con un effetto da capire (liste, tabelle), mai nell'esempio svolto.
- **Dashboard** 0.3.4: anteprima degli snippet nel Dettaglio.

## 0.3.3 — 12/10/2026

- **Dashboard** 0.3.3: nel Dettaglio l'elenco delle domande non torna più in cima a ogni clic e la domanda scelta resta visibile; l'elenco resta fermo mentre la domanda scorre e occupa tutta l'altezza visibile della finestra (ha una sua barra solo se è più lungo); scegliendo una domanda, la pagina risale all'inizio della domanda.

## 0.3.2 — 12/10/2026

- **Dashboard** 0.3.2: una pagina di spiegazione può stare sulla stessa pagina del quiz di una domanda complessa (per esempio i passi da seguire e la consegna del file): l'avviso «le domande di programmazione stanno su una pagina da sole» conta solo le domande.

## 0.3.1 — 12/10/2026

- Nuova tipologia **Consegna di un file** (`consegna_file`): domanda aperta senza testo, con un file da caricare (.html, .htm, .css). Serve a verificare che gli studenti abbiano creato davvero il file, per esempio la pagina dell'esempio svolto.
- **Dashboard** 0.3.1: la tipologia nel catalogo e nel dettaglio.
- L'importazione da un backup riconosce le domande aperte con solo il file da caricare.

## 0.3.0 — 12/10/2026

- **Dashboard** 0.3.0: scelta «Esercizi HTML» nei dati del quiz e nel modulo «Nuovo quiz» (con linguaggio HTML e CSS): **con anteprima** (prototipo `php_con_test`, con l'area di prova) o **senza anteprima** (prototipo `html`: il campo serve solo a incollare il codice scritto nell'editor e provato nel browser). Il dettaglio mostra il prototipo scelto.
- La generazione del quiz usa il prototipo scelto (campo `prototipoHtml`); senza scelta resta `php_con_test`.
- L'importazione da un backup riconosce gli esercizi HTML con il prototipo `html` e imposta il quiz «senza anteprima».

## 0.2.0 — 12/10/2026

- **Dashboard** 0.2.0: nel modulo «Nuovo quiz» il primo tipo è «Libero (senza preset)», senza regole su tipi, quantità, punti e tempi, con la scelta del comportamento in Moodle (esercitazione o verifica).
- **Dashboard**: riquadro «Come scegliere il tipo di quiz» con la descrizione di ogni tipo.
- **Dashboard**: lezione o codice facoltativi; se mancano, il quiz riceve un codice di tre caratteri che comincia con la classe (per esempio 4K7).
- Un codice che comincia con una cifra non è più preso per un numero di lezione: «Lezione N» solo per i numeri.

## 0.1.1 — 12/10/2026

- Claude risponde sempre in italiano, anche quando un comando o una skill si avvia dal menù (l'app aggiunge da sola una frase in inglese).

## 0.1.0 — 12/10/2026

Prima versione del plugin, nata dalle skill usate finora a scuola.

- Sette skill: `progettazione-quiz`, `materiali-moodle`, `verifiche-programmazione`, `domande-coderunner-js`, `domande-coderunner-sql`, `domande-php-mysqli-mock`, `database-didattici`.
- Comando `installa-dashboard`: pubblica la dashboard dell'utente, crea l'attività programmata che avvia i quiz, salva le impostazioni; aggiorna una dashboard esistente senza toccare i quiz.
- **Dashboard** 0.1.0: l'avvio dei quiz legge l'attività dalle impostazioni della pagina (riquadro «Impostazioni» nella vista iniziale); benvenuto al primo avvio; tipo «Importato da Moodle» per i quiz portati da un backup.
- Importazione di un quiz da un backup `.mbz` e confronto tra un backup e la dashboard, per riportare le correzioni fatte in Moodle.
- Catalogo dei database didattici dentro il plugin (biblioteca, palestra, cinema, veterinario, in tre taglie); ogni utente ha la sua pagina «Database didattici» per quelli che crea.
