# Prove del plugin

Un controllo da lanciare **prima di ogni rilascio**, dalla radice del repository:

```
python3 sviluppo/prove/prova_tutto.py
```

Dura circa un minuto. Stampa «TUTTO A POSTO» oppure i problemi, ognuno con **che cosa fare**.

## Che cosa controlla

1. Node e PHP ci sono (servono per calcolare gli output delle domande CodeRunner).
2. Le copie dei file condivisi tra le skill sono uguali all'originale (`sviluppo/strumenti/allinea_copie.py`).
3. I file citati nelle skill (`references/…`, `scripts/…`, `assets/…`) esistono.
4. Ogni tipologia di domanda ha una riga nel quiz di prova.
5. I due quiz di prova si generano fino al `.mbz`.
6. Le domande generate (testi, risposte, punti, pagine, sezioni) sono quelle di `atteso/*.struttura.txt`.
7. Gli output dei test CodeRunner sono quelli di `atteso/*.output.txt`. Questi dipendono anche dal computer (versioni di Node, PHP, SQLite): per questo stanno in un controllo a parte.

## Che cosa NON controlla

La qualità didattica dei quiz, le quattro pagine nel browser, il ripristino in Moodle.

## I quiz di prova

Stanno in `export/`, nella stessa forma dell'esportazione della dashboard «Bozze dei quiz»: `export/quiz/<id>.json` è il quiz, `export/quiz/<id>/domande/rNN.json` le righe.

- `prova`: un'esercitazione con una riga per ogni tipologia di domanda.
- `verprova`: una verifica con due varianti per posizione (domande casuali per tag).

**Una tipologia nuova**: aggiungi una riga in `export/quiz/prova/domande/` (copia il file di una tipologia simile, cambia `pos`, `pag`, `titolo`, `tipologia`, `traccia`, `coderunner`; l'`ordine` più alto di tutti), poi aggiorna il risultato atteso.

## Aggiornare il risultato atteso

Solo quando una modifica cambia **apposta** le domande generate (una regola nuova di stile, una tipologia nuova):

1. `cd sviluppo/prove && python3 aggiorna_atteso.py` mostra le differenze, senza scrivere niente.
2. Mostra le differenze all'utente e aspetta il suo ok.
3. `python3 aggiorna_atteso.py --ok-dell-utente` scrive i file nuovi.
4. Nel CHANGELOG scrivi che cosa è cambiato nelle domande generate.

Mai per far passare una prova che fallisce senza un motivo noto all'utente, e mai modificando `prova_tutto.py`.
