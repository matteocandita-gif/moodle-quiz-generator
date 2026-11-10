<!-- percorso-dei-quiz: inizio (blocco comune: si modifica in sviluppo/strumenti/percorso-dei-quiz.md, poi allinea_copie.py) -->
## Il percorso dei quiz

Ogni quiz Moodle (verifica, esercitazione, ripasso, anche di programmazione) segue un solo percorso, con la dashboard «Bozze dei quiz»:

1. **`progettazione-quiz`**, parte 1, didattica: tipo di quiz, scaletta e tracce nella dashboard, riviste e approvate dall'utente. Per una verifica di programmazione carica `verifiche-programmazione`; il database di un quiz SQL o PHP viene da `database-didattici`.
2. **`materiali-moodle`**, parte 2, tecnica: dal database della dashboard produce XML e `.mbz`; per le domande di programmazione usa `domande-coderunner-js`, `domande-coderunner-sql` e `domande-php-mysqli-mock`.

Nessun'altra skill è un punto di partenza per un quiz. Da sole servono solo per ciò che non diventa un quiz: una domanda singola, una correzione o un controllo (`materiali-moodle` o la skill CodeRunner del linguaggio), domande per la banca o pagine di teoria (`materiali-moodle`), un database per una lezione in phpMyAdmin (`database-didattici`), la conversione delle vecchie domande SQL (`domande-coderunner-sql`).
<!-- percorso-dei-quiz: fine -->
