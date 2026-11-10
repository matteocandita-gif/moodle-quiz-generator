# Richieste fuori dalla dashboard: domande sciolte, pagine, controllo di materiale esistente

Da leggere quando la richiesta non passa dalla dashboard «Bozze dei quiz»: una domanda o un gruppo di domande per la banca, una pagina, il controllo o la correzione di un export. Fa parte di `materiali-moodle`: il percorso, i passi della generazione e le regole generali stanno in `SKILL.md`.

## Distribuzione su pagine

Con la dashboard pagine e sezioni sono già nelle righe e finiscono nel `.mbz`. Per una proposta fuori dalla dashboard, ogni quiz dice come le domande si dividono in pagine.

- **Su una pagina da sole**: le domande complesse, in particolare quelle di programmazione (CodeRunner, debug, esercizi liberi) e le domande aperte con un codice proprio.
- **Sulla stessa pagina**: le domande che hanno bisogno di un contesto che sta in un'altra domanda (un codice, una tabella, una pagina di teoria a cui rispondono, l'esercizio a cui si riferisce una domanda di teoria), sempre; le domande brevi e veloci (vero/falso, risposta multipla rapida) quando condividono lo stesso contesto.
- **Sezioni**: quando il quiz ha parti distinte che lo studente deve vedere (istruzioni, blocchi di una lezione), proponi le intestazioni di sezione di Moodle e la posizione da cui parte ciascuna; compaiono nel blocco di navigazione. Nelle verifiche niente sezioni che rivelino la parte avanzata.

Forma della proposta: nella tabella del tracciato una colonna **Pag.** (le domande sulla stessa pagina hanno lo stesso numero) e una riga di separazione in grassetto all'inizio di ogni sezione:

| Pag. | Pos. | Domanda | Tipo |
|---|---|---|---|
| **— Sezione: Blocco A —** | | | |
| 2 | A1 | Variabili e assegnamento | Teoria |
| 3 | A2 | Il ciclo stampa 5 righe | Vero/falso |
| 3 | A3 | i vale 5 all'uscita | Vero/falso |
| 4 | A4 | Input e calcoli | CodeRunner |

Quando consegni solo l'XML ricorda come applicarla: Ripagina (una domanda per pagina, se è il caso) e poi le intestazioni di sezione nelle posizioni indicate.

## Produrre le domande

1. Scrivi la specifica (`references/formato-specifica.md`) nella cartella di lavoro, con il codice grezzo nei blocchi `[[codice LINGUAGGIO]]`. Con la dashboard la specifica la scrive `da_dashboard.py`.
2. Lancia `python3 scripts/crea_xml.py specifica.txt NOME.xml` (lo script sta nella cartella della skill, i file nella cartella di lavoro). Se si ferma, correggi la specifica e rilancia. Gli avvisi non bloccano, ma valuta se hanno ragione.
3. Se ci sono domande CodeRunner, producile con la skill indicata in `references/sequenza.md`, poi unisci: `python3 scripts/unisci_xml.py NOME.xml prima.xml seconda.xml …`, nell'ordine della sequenza. Lancia `controlla_xml.py` anche sull'XML delle altre skill.
4. Consegna all'utente l'XML (o l'`.mbz`) come file. Nel messaggio: categoria, numero di domande per tipo, distribuzione su pagine e sezioni da impostare (solo per l'XML), note per il docente, eventuali avvisi rimasti, e per le verifiche quando aprire la revisione. Ricorda che l'import crea sempre domande nuove.

**Domanda singola**: se l'utente vuole il testo da incollare, dagli l'HTML già espanso (passalo da `crea_xml.py` o da `espandi_html.py` per avere il `<pre>` pronto), più risposte e feedback.

## Produrre le pagine

- **Dentro un quiz**: domanda `description` nella specifica, insieme agli esercizi.
- **Attività Pagina o Area di testo e media**: scrivi l'HTML con i blocchi `[[codice]]` e lancia `python3 scripts/espandi_html.py sorgente.html NOME.html`; consegna il file, che l'utente incolla nell'editor in modalità sorgente.

## Controllare materiale esistente

`python3 scripts/controlla_xml.py FILE.xml --avvisi` controlla un export con le stesse regole. Riporta all'utente ogni problema con il nome della domanda e che cosa vede lo studente (es. «nel feedback compare \/»). Le pagine fatte prima di questa skill possono avere emoji o lo stile vecchio: segnalalo una volta, senza elencarlo per ogni pagina.

Per correggere: estrai le domande da modificare nella specifica, correggi, rigenera. Se le domande sono già usate in un quiz, l'utente preferisce modificarle in Moodle invece di reimportarle (l'import crea domande nuove, e i quiz resterebbero collegati alle vecchie): dagli i testi corretti da incollare, come in «Aggiornare un quiz già in Moodle»; l'XML da reimportare solo per le domande non ancora usate o se lo chiede lui.
