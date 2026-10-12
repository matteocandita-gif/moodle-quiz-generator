# Changelog

Le novità di ogni versione di «Moodle: quiz generator». Le righe segnate **Dashboard** cambiano la pagina «Bozze dei quiz»: Claude propone di aggiornarla, e i quiz salvati restano.

## 0.1.1 — 12/10/2026

- Claude risponde sempre in italiano, anche quando un comando o una skill si avvia dal menù (l'app aggiunge da sola una frase in inglese).

## 0.1.0 — 12/10/2026

Prima versione del plugin, nata dalle skill usate finora a scuola.

- Sette skill: `progettazione-quiz`, `materiali-moodle`, `verifiche-programmazione`, `domande-coderunner-js`, `domande-coderunner-sql`, `domande-php-mysqli-mock`, `database-didattici`.
- Comando `installa-dashboard`: pubblica la dashboard dell'utente, crea l'attività programmata che avvia i quiz, salva le impostazioni; aggiorna una dashboard esistente senza toccare i quiz.
- **Dashboard** 0.1.0: l'avvio dei quiz legge l'attività dalle impostazioni della pagina (riquadro «Impostazioni» nella vista iniziale); benvenuto al primo avvio; tipo «Importato da Moodle» per i quiz portati da un backup.
- Importazione di un quiz da un backup `.mbz` e confronto tra un backup e la dashboard, per riportare le correzioni fatte in Moodle.
- Catalogo dei database didattici dentro il plugin (biblioteca, palestra, cinema, veterinario, in tre taglie); ogni utente ha la sua pagina «Database didattici» per quelli che crea.
