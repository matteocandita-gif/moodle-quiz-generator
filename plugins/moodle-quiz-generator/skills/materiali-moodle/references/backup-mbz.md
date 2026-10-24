# I backup di corso (.mbz)

L'utente carica spesso un backup per far analizzare un corso (confronti tra il corso «deposito» e il corso dell'anno, recupero di domande, ricostruzione di come era fatta un'esercitazione).

## Struttura

Un `.mbz` è un archivio tar.gz (zip nelle versioni vecchie):

- `moodle_backup.xml`: nome del corso, versione di Moodle, elenco delle sezioni e delle attività con la sezione di appartenenza;
- `sections/section_N/section.xml`: titolo e descrizione di ogni sezione;
- `activities/<tipo>_<id>/<tipo>.xml`: ogni attività (per un quiz, `quiz.xml` con le impostazioni e le domande usate);
- `questions.xml` alla **radice**: le domande di tutte le banche incluse nel backup, con categorie, versioni, testo e risposte. Il testo delle domande non sta nelle cartelle dei quiz.

Da Moodle 4 le domande hanno versioni: conta l'ultima. I quiz puntano alle domande con un riferimento alla voce della banca (`questionbankentryid`), oppure a una categoria per le domande casuali. Nei backup di Moodle 5.2 le domande che il quiz prende da una banca condivisa (un'attività «Banca delle domande», per esempio quella di un corso deposito) sono incluse in `questions.xml`, con il contesto e gli stamp originali della banca, anche se il quiz sta in un altro corso. `leggi_mbz.py --banche` elenca queste banche con i valori per l'impaginazione `banca` di `crea_mbz.py` (vedi «Depositi» in `SKILL.md`).

## Lo script

```bash
python3 scripts/leggi_mbz.py BACKUP.mbz                # sezioni, attività, banche con il numero di domande per tipo
python3 scripts/leggi_mbz.py BACKUP.mbz --quiz         # per ogni quiz: tempo, punti, sezioni, slot con pagina e punti, versioni, domande casuali per tag
python3 scripts/leggi_mbz.py BACKUP.mbz --domande SQL  # testo delle domande delle categorie che contengono "SQL"
python3 scripts/leggi_mbz.py BACKUP.mbz --estrai /home/claude/corso   # per analisi più fini
```

Per confronti tra due corsi, estrai entrambi e confronta con Python le attività (per nome e tipo) e le domande (per nome e testo): identiche, modificate, presenti in uno solo.

Se lo script fallisce su un backup (formati cambiano tra versioni di Moodle), estrai con `--estrai` e leggi direttamente `moodle_backup.xml` e `questions.xml`: la struttura sopra resta valida.

## Riservatezza

I backup possono contenere dati degli studenti (iscrizioni, tentativi, valutazioni) se sono stati inclusi. Nelle analisi e nei file prodotti **non riportare mai nomi completi degli studenti**: usa le iniziali.

## Esportare domande dal backup

Per riusare domande di un backup in un altro corso, la via più semplice per l'utente resta l'export dalla banca delle domande in Moodle XML. Se serve farlo dal backup, ricostruisci le domande nella specifica di `crea_xml.py` (per i tipi che gestisce) partendo da testo e risposte in `questions.xml`.
