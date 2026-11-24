# L'interfaccia «html_sito» di CodeRunner

Da leggere quando il quiz ha un «Sito con l'editor» (`sito_html`) o un «Sito PHP con l'editor» (`sito_php`), o quando l'utente chiede di installare o aggiornare l'interfaccia sul server Moodle. Fa parte di `materiali-moodle`; il formato della riga è in `tracce-html.md` di `progettazione-quiz`, la generazione in `righe-coderunner.md`.

## Che cos'è

Un'interfaccia di CodeRunner, come Ace, Html o Table, che si sceglie in una domanda con **Personalizza → Input UI: html_sito**. Lo studente crea cartelle e file del sito («+ File», «+ Cartella», «+ Immagine», «Rinomina», «Sposta» o trascinamento, «Elimina»), li scrive con l'editor Ace di CodeRunner e vede l'anteprima della pagina aperta, con i link che portano da una pagina all'altra, «Not Found» come un server vero quando il file non c'è e le immagini solo con il percorso giusto. Il codice dello studente gira in un riquadro isolato e non può toccare la pagina di Moodle.

**L'anteprima come un browser** (dalla 0.12.0): non segue il file aperto nell'editor. All'apertura mostra la pagina principale; un'altra pagina si apre con **«▶ Apri nel browser»** nella barra sopra il codice (o Ctrl+Invio), seguendo i link e i moduli della pagina, oppure scrivendo l'indirizzo nella barra (`pagine/libri.php?genere=Giallo` e Invio). Così modificare una pagina PHP non la esegue. Una pagina HTML nell'anteprima si aggiorna da sola mentre si scrive; una pagina PHP no: l'avviso dice di premere ⟳.

**Tre blocchi** (dalla 0.11.0): **Traccia** (una copia del testo della domanda), **Editor** (la barra dei file, l'elenco e il codice) e **Anteprima del browser**, ognuno con la sua intestazione. Traccia e anteprima si chiudono a scomparsa (il pulsante nell'intestazione, o «Traccia» e «Anteprima» nell'intestazione dell'editor) e si allargano trascinando il bordo; la scelta resta nel browser per tutte le domande. Quando la domanda è stretta, editor e anteprima stanno uno sopra l'altro, con la traccia a sinistra.

**Moduli e pagine PHP nell'anteprima**: inviando un modulo, il browser controlla i campi (`required`, `min`, `type="email"`…) e l'anteprima va alla pagina dell'`action`: con GET i dati compaiono nella barra degli indirizzi (`cerca.html?q=giallo`), con POST in un avviso. Le pagine `.php` (con i colori di PHP nell'editor) non si eseguono, salvo con `anteprima_php`: l'anteprima mostra il nome della pagina e la tabella dei dati che riceverebbe, con il metodo e i `name`, e ricorda che le esegue Controlla. Anche un link con `?id=3` porta i suoi dati GET. «Copia sito» e «Incolla sito» portano il sito da una domanda all'altra dello stesso tentativo.

La risposta è il sito in JSON, che il template di `html_con_file` ricrea in una cartella e controlla come uno zip:

```json
{"htmlve":1,"versione":"0.6.1","salvato":"2026-11-19T10:57:28.000Z",
 "cartelle":["css","img","pagine"],
 "files":{"css/stile.css":"…","index.html":"…","pagine/menu.html":"…"},
 "immagini":{"img/logo.png":"logo.png","img/foto.jpg":"data:image/jpeg;base64,…"}}
```

Nelle immagini, un nome è un'immagine fornita dalla domanda; un `data:` è un'immagine caricata dallo studente (solo con `file_pc`).

**Salvataggio**: l'interfaccia scrive il sito nella risposta 0,8 secondi dopo ogni modifica e CodeRunner lo ricopia ogni 2 secondi e all'invio della pagina, poi lo salva il quiz di Moodle. Durante un tentativo c'è anche una copia nel browser, usata solo se è più recente della risposta salvata (PC spento prima del salvataggio automatico). In revisione, in Valutazione manuale e nella soluzione dell'autore il sito è in sola lettura. Ctrl-Alt-M (di CodeRunner) mostra la risposta grezza.

**Sito di partenza** (dalla 0.12.1): il preload della domanda (`answerpreload`) può contenere un sito nello stesso formato della risposta; `da_dashboard.py` lo scrive dalle sezioni `=== partenza …` della riga (`tracce-html.md` di `progettazione-quiz`). Al primo accesso CodeRunner lo mette nella risposta e l'editor lo apre. Il pulsante di ripristino di CodeRunner ferma l'editor, rimette il preload nella risposta e lo fa ripartire: quando riparte nella stessa pagina (ripristino o ritorno da Ctrl-Alt-M) l'editor legge solo la risposta, senza la copia nel browser, e la salva subito, così il ripristino arriva anche a Moodle.

## I parametri dell'interfaccia

Tutti facoltativi; `da_dashboard.py` li scrive dalle opzioni della riga.

| Parametro | Opzione della riga | Che cosa fa |
|---|---|---|
| `chiusura_automatica` | `aiuti: chiusura` | Ace chiude da solo tag, virgolette e parentesi |
| `completamento` | `aiuti: completamento` | Ace propone tag, attributi e proprietà CSS mentre si scrive |
| `segnala_errori` | `aiuti: errori` | Ace segna nel margine gli errori di sintassi che riconosce |
| `immagini` | `immagini: logo.png, pizza.jpg` | le immagini del testo della domanda che lo studente mette nel sito con «+ Immagine» |
| `file_pc` | `file_pc: sì` | file del computer: «Scarica .zip» (il sito in uno .zip), «Importa» (file sciolti o uno .zip, nella cartella selezionata; anche le pagine `.php` dalla 0.9.1), immagini caricate con «+ Immagine» (massimo 500 KB l'una); mai nelle verifiche |
| `carica_immagini` | (nome vecchio) | come `file_pc`: vale ancora per le domande già fatte |
| `copia_incolla` | (sempre acceso) | pulsanti «Copia sito» e «Incolla sito»: il sito di una domanda si porta in un'altra dello stesso tentativo, per gli esercizi a passi. Gli appunti stanno nel browser e valgono solo nello stesso tentativo |
| `traccia` | (acceso; `traccia: no` per toglierlo) | pannello «Traccia» a sinistra dell'editor, con una copia del testo della domanda (immagini comprese) letta dalla pagina del quiz: lo studente legge la consegna mentre scrive. Nel modulo di modifica della domanda il testo non c'è e il pannello non compare |
| `anteprima_php` | `anteprima_php: sì` (solo `sito_php`) | l'anteprima esegue davvero le pagine `.php` su Jobe, con gli errori di PHP come XAMPP: l'editor manda il sito e la richiesta (GET o POST) con il servizio web di CodeRunner, che va attivato (sotto). Cambiare pagina o dati esegue di nuovo la pagina; cambiare solo il codice no (l'avviso dice di premere ⟳), per non mandare una richiesta a ogni tasto. Senza il servizio, o oltre il limite di richieste, l'anteprima lo dice e mostra i dati ricevuti come prima |
| `anteprima_php_db` | (lo scrive `da_dashboard.py` con `database`) | il database delle pagine per l'anteprima: `{"nome", "nomedb", "sql"}` (lo script SQL, perché il file `.db` allegato non è visibile allo studente; `nomedb` `"*"` con il controllo tollerante). Lo stato del database resta nell'editor tra una richiesta e l'altra; 🗄 riparte dai dati iniziali |

Le immagini fornite l'interfaccia le cerca tra le immagini della domanda per nome del file. Nel modulo di modifica della domanda il testo non c'è e compaiono come riquadri grigi con il nome: i percorsi e i controlli funzionano lo stesso.

## Installare o aggiornare l'interfaccia (una volta, l'amministratore di Moodle)

I file stanno in `assets/interfaccia-html-sito/` di questa skill:

| File | A che cosa serve |
|---|---|
| `ui_html_sito.js` | l'interfaccia (modulo AMD `qtype_coderunner/ui_html_sito`) |
| `ui_html_sito.json` | i parametri dell'interfaccia, che CodeRunner mostra nel modulo della domanda |
| `stringhe.php` | le descrizioni dei parametri, che lo script aggiunge alle stringhe di CodeRunner |
| `installa.sh` | copia tutto al posto giusto e svuota le cache |

1. Dai all'utente i quattro file (`SendUserFile`, oppure nella sua cartella collegata) e digli di copiarli in una cartella del server Moodle.
2. Sul server, da quella cartella: `sudo bash installa.sh /percorso/di/moodle` (la cartella con `config.php`). Lo script trova CodeRunner (anche nella cartella `public` di Moodle 5.1 e successivi), copia `ui_html_sito.js` e `ui_html_sito.json` in `question/type/coderunner/amd/src/` e `ui_html_sito.js` come `amd/build/ui_html_sito.min.js`, aggiunge (o sostituisce) le descrizioni dei parametri in fondo a `lang/en/qtype_coderunner.php` controllando che il file resti corretto, e prova a svuotare le cache con l'utente `www-data` (un altro utente: `sudo UTENTE_WEB=nome bash installa.sh …`).
3. **Svuotare le cache** di Moodle (Amministrazione del sito → Sviluppo → Svuota le cache), se lo script dice di non esserci riuscito: senza, la domanda mostra la casella di testo vuota al posto dell'editor.
4. Controllo: in una domanda CodeRunner, **Personalizza → Input UI** elenca `html_sito`; nell'anteprima di una domanda che lo usa compare l'editor (dopo Ctrl+F5).

**Per `anteprima_php`** (una volta): Amministrazione del sito → Plugin → Tipi di domanda → CodeRunner, sezione del servizio web, spunta **«Enable sandbox web service»** (`qtype_coderunner/wsenabled`) e lascia attivo il registro delle richieste (`wsloggingenabled`), che serve al limite. Il limite di richieste per studente all'ora è `wsmaxhourlyrate` (predefinito 200; 0 = nessun limite) e il tempo massimo di ogni esecuzione `wsmaxcputime` (predefinito 5 secondi). Gli studenti hanno già il permesso `qtype/coderunner:sandboxwsaccess`. Ogni pagina PHP aperta nell'anteprima è una richiesta a Jobe.

**Dopo ogni aggiornamento di CodeRunner** l'interfaccia sparisce, perché sta nella cartella del plugin: si rilancia `installa.sh` e si svuotano le cache. Lo stesso quando cambia `ui_html_sito.js` nel plugin (lo dice il changelog).

Il sorgente sta nel repository, in `sviluppo/interfaccia-html-sito/` (`modulo.js` e `stile.css`, costruiti con `build.py`), con una pagina di prova che simula CodeRunner: `ui_html_sito.js` non si modifica a mano. Il programma che l'anteprima manda a Jobe è `anteprima_php.py`: `build.py` ci mette l'avvio di PHP del template di `php_sito` e la facciata di mysqli di `domande-php-mysqli-mock`, così l'anteprima esegue le pagine come il controllo. Per provarla in locale: `python3 prova/server_prova.py` e la pagina di prova con `?php=1` (o `?php=db`).
