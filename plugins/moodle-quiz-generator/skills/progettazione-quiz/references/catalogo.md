# Catalogo delle tipologie

È lo stesso catalogo della dashboard (`CAT_RAW` nel sorgente): se cambia qui, va cambiato anche lì, e nel dizionario `CATALOGO` di `da_dashboard.py`.

Colonne: **id** è il valore del campo `tipologia` della riga; **Tipo Moodle** decide come la riga diventa domanda; **Tipi di quiz** dice in quali preset è prevista (sigle in `preset.md`), e fuori da quelli la dashboard dà un avviso; **Prefisso** entra nel nome Moodle (`L<lezione> - <pos> - <prefisso>: <titolo>`; nelle verifiche, che hanno un codice al posto del numero di lezione, `V5R - <pos> - <prefisso>: <titolo>`).

| id | Tipologia | Famiglia | Tipo Moodle / strumento | Tipi di quiz | Note | Prefisso del nome |
|---|---|---|---|---|---|---|
| `istruzioni` | Istruzioni | Pagine | Descrizione | V VT | pagina |  |
| `comelavoriamo` | Come lavoriamo oggi | Pagine | Descrizione | ED EDT EP ER | pagina |  |
| `paginablocco` | Pagina del blocco | Pagine | Descrizione | ED EDT ER | pagina | Spiegazione (Ripasso in RT ed ER) |
| `vf` | Vero/falso | Concetti | Vero/falso | VT RT ED EDT ER |  |  |
| `multipla` | Risposta multipla (una giusta) | Concetti | Risposta multipla | VT RT ED EDT ER |  |  |
| `crocette` | Risposta multipla (più giuste) | Concetti | Risposta multipla | VT RT ED EDT ER |  |  |
| `breve` | Risposta breve | Concetti | Risposta breve | VT RT ED EDT | solo con una risposta giusta senza varianti |  |
| `corrispondenza` | Corrispondenza | Concetti | Corrispondenza | VT RT ED EDT ER |  |  |
| `cloze_testo` | Completamento di testo | Concetti | Cloze | VT RT ED EDT ER |  |  |
| `ordine` | Metti in ordine | Concetti | Cloze | VT RT ED EDT |  |  |
| `teoria_aperta` | Teoria a risposta aperta | Concetti | Aperta | V VT RT | su una pagina da sola, correzione manuale |  |
| `esempio_svolto` | Esempio svolto da leggere | Lettura del codice | Cloze | ED ER |  | Esempio svolto |
| `tracciamento` | Tracciamento | Lettura del codice | Cloze | V RT ED EP ER |  | Tracciamento |
| `lettura_output` | Lettura dell'output | Lettura del codice | Cloze | V RT ED EP ER |  | Tracciamento |
| `trova_errore` | Trova l'errore | Lettura del codice | Risposta multipla | V RT ED EP ER |  | Trova l'errore |
| `compl_campi` | Completamento a campi | Completamento | Cloze | ED EP ER |  | Completamento |
| `guidato` | Esempio guidato | Completamento | Cloze | ED ER |  | Esempio guidato |
| `compl_eseguito` | Completamento eseguito | Completamento | CodeRunner JS (gapfiller) | ED EP ER | su una pagina da sola | Completamento |
| `scrittura_scheletro` | Codice parziale | Completamento | CodeRunner JS, PHP | ED EP ER | su una pagina da sola | Scrivere |
| `debug_msg` | Debug con messaggi | Debugging | CodeRunner JS, SQL, PHP | ED EP ER | su una pagina da sola | Debug |
| `debug_silenzioso` | Debug silenzioso | Debugging | CodeRunner JS, SQL, PHP | ED EP ER | su una pagina da sola | Debug |
| `debug_motivazione` | Debug con motivazione | Debugging | Aperta | V | su una pagina da sola, correzione manuale | Debug |
| `prog_completo` | Programma completo | Scrittura con correzione automatica | CodeRunner JS | V ED EP ER | su una pagina da sola | Scrivere |
| `funzione` | Funzione | Scrittura con correzione automatica | CodeRunner JS | V ED EP ER | su una pagina da sola | Scrivere |
| `prog_dati` | Programma su dati dati | Scrittura con correzione automatica | CodeRunner JS | ED EP ER | su una pagina da sola | Scrivere |
| `prog_random` | Programma con valori casuali | Scrittura con correzione automatica | CodeRunner JS | ED EP | su una pagina da sola | Scrivere |
| `query` | Query | Scrittura con correzione automatica | CodeRunner SQL | V ED EP ER | su una pagina da sola | Scrivere |
| `create_tabelle` | Creazione di tabelle | Scrittura con correzione automatica | CodeRunner SQL | V ED EP | su una pagina da sola | Scrivere |
| `query_due_passi` | Query in due passi | Scrittura con correzione automatica | CodeRunner SQL | ED EP | su una pagina da sola | Scrivere |
| `vincoli` | Vincoli di integrità | Scrittura con correzione automatica | CodeRunner SQL | ED | su una pagina da sola | Esercizio |
| `pagina_php` | Pagina PHP con database | Scrittura con correzione automatica | CodeRunner PHP | V ED EP ER | su una pagina da sola | Scrivere |
| `esercizio_libero` | Esercizio libero | Altro | Aperta | V ED EP ER | su una pagina da sola, correzione manuale | Esercizio libero |
| `libero_html` | Esercizio HTML | Altro | CodeRunner php_con_test (scratchpad) o html (senza anteprima), senza test | V ED EP ER | su una pagina da sola, correzione manuale | Esercizio libero |
| `libero_css` | Esercizio CSS | Altro | CodeRunner CSS (senza test) | V ED EP ER | su una pagina da sola, correzione manuale | Esercizio libero |
| `campo_prova` | Campo di prova | Altro | CodeRunner SQL | V EP | su una pagina da sola | Campo di prova |

## Note sulle tipologie

- **Pagine** (`istruzioni`, `comelavoriamo`, `paginablocco`): domande `description` dentro il quiz, mai l'attività Pagina del corso. Senza punti. Si scrivono già nella forma finale, in seconda persona plurale, con i riquadri.
- **Risposta breve**: solo quando la risposta giusta è una e non ha sinonimi, sigle o forme estese da accettare; gli errori prevedibili si scrivono come opzioni sbagliate con il loro feedback. Se le risposte accettabili sono più d'una, meglio una risposta multipla.
- **Metti in ordine**: solo se l'ordine non si ricava dal buon senso senza aver letto la pagina.
- **Risposta multipla**: due varianti, una sola giusta (`multipla`, `( )`) o più giuste (`crocette`, `[x]` / `[ ]`). La seconda si usa quando le affermazioni vere sono più d'una, con un'opzione per affermazione: mai una risposta singola con opzioni che ne mettono insieme diverse. «Trova l'errore» è una risposta multipla: con un errore solo `( )`, con più errori `[x]` / `[ ]` (la tipologia resta `trova_errore`). Con più risposte giuste: 2 giuste e 2 sbagliate oppure 3 giuste e 3 sbagliate; le sbagliate senza percentuale prendono da sole una penalità che sommata fa −100%, così chi spunta tutto prende 0 (penalità diverse si scrivono a mano, `[ -50%]`, e le altre sbagliate si dividono quello che manca: la somma resta −100%); la traccia dice «Seleziona tutte le risposte corrette», perché l'istruzione standard di Moodle è nascosta; la `correzione` (feedback generale) riporta la soluzione completa. Un'alternativa ugualmente corretta in programmazione (per esempio la concatenazione dove noi interpoliamo) non è mai un'opzione sbagliata.
- **Completamento a campi** (`compl_campi`) e **esempio guidato** (`guidato`): Cloze con i campi dentro il codice. In HTML un campo non può contenere un tag: il campo contiene il nome del tag, parentesi angolari e barra sono già scritte nel codice. Nei completamenti ogni campo vale di norma 1 punto, quindi i punti della riga e il numero dei campi vanno insieme: cambiare i punti vuol dire cambiare i campi.
- **Esempio svolto da leggere** (`esempio_svolto`), **tracciamento**, **lettura dell'output**: Cloze di lettura, con risposte brevi, numeri e menù a tendina.
- **Esercizio libero** (`esercizio_libero`): risposta aperta a correzione manuale, con criteri e punti per criterio nella «Correzione», per le risposte senza codice.
- **Esercizio HTML** (`libero_html`) ed **Esercizio CSS** (`libero_css`): esercizi liberi a correzione manuale con l'editor di CodeRunner, senza test (prototipi `php_con_test` per l'HTML con anteprima, che ha lo scratchpad per vedere la pagina interpretata, oppure `html` per l'HTML senza anteprima, scelto nei dati del quiz, e `css`). Sono gli esercizi finali delle esercitazioni e delle verifiche di HTML e CSS, dove non c'è correzione automatica. Nell'`html` si può chiedere anche CSS nel documento o in linea; nel `css` la risposta è solo il foglio di stile. Convenzioni in `formato-consegna.md`.
- **Codice parziale** (`scrittura_scheletro`): esercizio di scrittura con il prototipo «con prompt» in cui lo studente trova già una parte del codice nella casella (per esempio la definizione di una funzione da usare, uno scheletro da riempire, dati già preparati), nella sezione `=== preload` di «Soluzione e test». Si distingue dal completamento eseguito (gapfiller, spazi da riempire) perché la casella è libera e si può scrivere qualsiasi codice.
- **Corrispondenza**: righe `elemento <-> corrispondenza`, con le risposte in più come righe `<-> …` (convenzione in `formato-consegna.md`). La scrive direttamente `da_dashboard.py` (`crea_xml.py` non la gestisce) e va nell'XML e nell'.mbz. Come le altre domande di comprensione, non deve risolversi perché due parole stanno vicine nella pagina di spiegazione.
- **CodeRunner** (righe con «CodeRunner» nel tipo): la traccia si scrive come le altre, senza campi né opzioni; soluzione e test vanno nel campo `coderunner` («Soluzione e test», vedi `formato-consegna.md`). Le **JavaScript**, le **SQL** e le **PHP** (prototipo `php_mysqli_sqlite`) le converte `genera_quiz.py` con `domande-coderunner-js`, `domande-coderunner-sql` e `domande-php-mysqli-mock`; gli **esercizi HTML e CSS** li scrive direttamente `da_dashboard.py`. Finiscono tutti nell'XML e nell'.mbz, con il database del quiz allegato alle SQL e alle PHP.
