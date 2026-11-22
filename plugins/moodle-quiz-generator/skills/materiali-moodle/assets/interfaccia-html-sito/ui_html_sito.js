/**
 * Interfaccia «html_sito» per CodeRunner — versione 0.12.0
 *
 * Lo studente crea le cartelle e i file del sito (HTML, CSS, JS), li scrive con l'editor Ace
 * di CodeRunner e vede l'anteprima delle pagine. La risposta è un JSON:
 *   {"htmlve": 1, "versione": "...", "salvato": "...", "cartelle": [...], "files": {"index.html": "...", ...}}
 * che il template di html_con_file ricrea in una cartella e controlla come uno zip.
 *
 * Installazione: questo file va in question/type/coderunner/amd/src/ui_html_sito.js
 * e, identico, in question/type/coderunner/amd/build/ui_html_sito.min.js; poi si svuotano le cache.
 * CodeRunner carica Ace da sé perché il nome dell'interfaccia contiene «html».
 *
 * Il codice degli studenti gira in un iframe isolato (sandbox senza allow-same-origin):
 * non può leggere né modificare la pagina di Moodle. I moduli si possono «inviare» (allow-forms, così il
 * browser controlla i campi), ma l'invio lo ferma lo script dell'anteprima: l'editor mostra la pagina
 * dell'action con i dati ricevuti. Le pagine .php le esegue il template con Verifica; con anteprima_php
 * le esegue anche l'anteprima, con il servizio web di CodeRunner che manda il sito a Jobe.
 * L'anteprima è un browser: non segue il file aperto; le pagine si aprono con «▶ Apri nel browser» (Ctrl+Invio),
 * con i link e i moduli, o scrivendo l'indirizzo. Editor e anteprima stanno nei blocchi Traccia | Editor | Anteprima.
 *
 * Parametri dell'interfaccia (tutti falsi se non indicati), es. {"chiusura_automatica": true}:
 *  - chiusura_automatica: Ace chiude da solo tag, virgolette e parentesi;
 *  - completamento: Ace propone tag, attributi e proprietà mentre si scrive;
 *  - segnala_errori: Ace segna nel margine gli errori di sintassi che riconosce;
 *  - immagini: nomi delle immagini messe dal docente nel testo della domanda, es. "logo.png, pizza.jpg":
 *    lo studente le mette nel sito con «+ Immagine», nella cartella che sceglie;
 *  - file_pc: lavoro anche con i file del computer (mai nelle verifiche con SEB): «Scarica .zip» scarica il sito,
 *    «Importa» aggiunge file sciolti o il contenuto di uno .zip, «+ Immagine» carica anche immagini dal computer;
 *  - carica_immagini: nome vecchio di file_pc, vale ancora per le domande già fatte;
 *  - copia_incolla (vero se non indicato): pulsanti «Copia sito» e «Incolla sito», per ripartire nella
 *    domanda successiva dal sito di una domanda precedente dello stesso tentativo;
 *  - traccia (vero se non indicato): pannello «Traccia» a sinistra, con una copia del testo della domanda;
 *  - anteprima_php: l'anteprima esegue davvero le pagine .php su Jobe, con il servizio web di CodeRunner
 *    (qtype_coderunner_run_in_sandbox, da attivare nelle impostazioni di CodeRunner): errori di PHP compresi;
 *  - anteprima_php_db: con anteprima_php, il database delle pagine, JSON {"nome": ..., "nomedb": ..., "sql": ...}
 *    (script SQL per SQLite; nomedb "*" accetta qualsiasi nome in mysqli_connect). Lo stato del database
 *    resta nell'editor tra una richiesta e l'altra, finché non si ricarica la pagina o si riparte con 🗄.
 * Nella risposta le immagini sono in "immagini": {"img/logo.png": "logo.png"} (immagine fornita)
 * oppure {"img/foto.jpg": "data:image/jpeg;base64,..."} (immagine caricata).
 *
 * @module     qtype_coderunner/ui_html_sito
 * @copyright  2026 Matteo Candita
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
define('qtype_coderunner/ui_html_sito', [], function() {
    'use strict';

    var VERSIONE = '0.12.0';
    var NOME_VALIDO = /^[a-z0-9_-][a-z0-9._-]*$/;
    var ESTERNO = /^([a-z][a-z0-9+.-]*:|\/\/)/i;
    var ALTEZZA_MINIMA = 420;
    var ALTEZZA_PREDEFINITA = 560;
    var STILE = "html.htmlve-blocca-scorrimento, html.htmlve-blocca-scorrimento body { overflow: hidden !important; }\n\n.htmlve {\n  --htmlve-bordo: #c9ced6;\n  --htmlve-sfondo: #f4f5f7;\n  --htmlve-accento: #0f6cbf;\n  position: relative;\n  display: flex;\n  flex-direction: column;\n  font-family: system-ui, -apple-system, \"Segoe UI\", Roboto, sans-serif;\n  font-size: 14px;\n  line-height: 1.35;\n  color: #1d2125;\n  margin: 0;\n  text-align: left;\n}\n\n.htmlve * { box-sizing: border-box; }\n\n/* tre blocchi: Traccia | Editor | Anteprima del browser */\n.htmlve-blocchi { flex: 1; min-height: 0; display: grid; }\n.htmlve-blocco {\n  display: flex;\n  flex-direction: column;\n  min-width: 0;\n  min-height: 0;\n  border: 1px solid var(--htmlve-bordo);\n  border-radius: 6px;\n  overflow: hidden;\n  background: #fff;\n}\n.htmlve-testata {\n  flex: none;\n  display: flex;\n  align-items: center;\n  gap: 6px;\n  height: 24px;\n  padding: 0 4px 0 10px;\n  background: #e4e8ee;\n  border-bottom: 1px solid var(--htmlve-bordo);\n  font-size: 12px;\n  font-weight: 600;\n  color: #3f4750;\n}\n.htmlve-testata-titolo { flex: none; white-space: nowrap; }\n.htmlve-testata .htmlve-btn { flex: none; white-space: nowrap; padding: 0 7px; font-size: 12px; font-weight: 400; line-height: 16px; }\n.htmlve-testata .htmlve-spinta { margin-left: auto; }\n.htmlve-testata .htmlve-stato { font-weight: 400; font-size: 11px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; min-width: 0; }\n.htmlve-traccia { flex: 1; min-height: 0; overflow: auto; padding: 10px 12px; font-size: 13px; line-height: 1.45; }\n.htmlve-traccia img { max-width: 100%; height: auto; }\n.htmlve-traccia pre { white-space: pre-wrap; font-size: 12px; }\n.htmlve-traccia > :first-child > :first-child, .htmlve-traccia > :first-child { margin-top: 0; }\n.htmlve-striscia {\n  font: inherit;\n  font-size: 12px;\n  font-weight: 600;\n  color: var(--htmlve-accento);\n  background: #eef3fa;\n  border: 1px solid var(--htmlve-bordo);\n  border-radius: 6px;\n  writing-mode: vertical-rl;\n  padding: 10px 0;\n  cursor: pointer;\n  display: flex;\n  align-items: center;\n  justify-content: flex-start;\n  min-width: 0;\n}\n.htmlve-striscia:hover { background: #dfeaf7; }\n.htmlve-striscia.htmlve-orizzontale { writing-mode: horizontal-tb; padding: 4px 10px; }\n.htmlve-maniglia { position: relative; cursor: col-resize; touch-action: none; }\n.htmlve-maniglia::after { content: \"\"; position: absolute; top: 30%; bottom: 30%; left: 3px; width: 2px; border-radius: 1px; background: transparent; }\n.htmlve-maniglia:hover::after, .htmlve-trascina .htmlve-maniglia::after { background: #9fb3c8; }\n.htmlve-maniglia.htmlve-ferma { cursor: default; }\n.htmlve-maniglia.htmlve-ferma::after { background: transparent !important; }\n.htmlve-trascina, .htmlve-trascina * { cursor: col-resize !important; user-select: none !important; }\n.htmlve-trascina iframe { pointer-events: none; }\n.htmlve-btn.htmlve-premuto { background: #dfeaf7; border-color: #9fb3c8; }\n\n/* barra dei comandi */\n.htmlve-barra {\n  display: flex;\n  align-items: center;\n  flex-wrap: wrap;\n  gap: 6px;\n  padding: 6px 8px;\n  background: var(--htmlve-sfondo);\n  border-bottom: 1px solid var(--htmlve-bordo);\n}\n.htmlve-btn {\n  font: inherit;\n  font-size: 13px;\n  padding: 4px 10px;\n  border: 1px solid var(--htmlve-bordo);\n  border-radius: 4px;\n  background: #fff;\n  color: #1d2125;\n  cursor: pointer;\n  line-height: 1.3;\n}\n.htmlve-btn:hover:not(:disabled) { border-color: var(--htmlve-accento); color: var(--htmlve-accento); }\n.htmlve-btn:disabled { opacity: .45; cursor: default; }\n.htmlve-btn.htmlve-primario { background: var(--htmlve-accento); border-color: var(--htmlve-accento); color: #fff; }\n.htmlve-btn.htmlve-primario:hover { color: #fff; filter: brightness(1.1); }\n.htmlve-btn.htmlve-mini { padding: 1px 7px; font-size: 13px; }\n.htmlve-stato { margin-left: auto; font-size: 12px; color: #5c6670; }\n\n/* l'editor: albero | codice */\n.htmlve-corpo {\n  flex: 1;\n  display: grid;\n  grid-template-columns: 160px minmax(0, 1fr);\n  min-height: 0;\n}\n.htmlve-stretto .htmlve-corpo { grid-template-columns: 130px minmax(0, 1fr); }\n\n.htmlve-albero {\n  overflow: auto;\n  border-right: 1px solid var(--htmlve-bordo);\n  background: #fafbfc;\n  padding: 4px 0;\n  user-select: none;\n}\n.htmlve-voce {\n  display: flex;\n  align-items: center;\n  gap: 5px;\n  padding: 3px 6px;\n  cursor: pointer;\n  white-space: nowrap;\n  font-size: 13px;\n}\n.htmlve-voce:hover { background: #e9eef5; }\n.htmlve-voce.selezionata, .htmlve-voce.aperta { background: #d6e4f5; }\n.htmlve-voce.aperta .htmlve-nome { font-weight: 600; }\n.htmlve-icona { font-size: 13px; width: 16px; text-align: center; }\n.htmlve-nome { overflow: hidden; text-overflow: ellipsis; }\n.htmlve-suggerimento { padding: 8px 10px; font-size: 12px; color: #5c6670; white-space: normal; }\n\n.htmlve-codice { position: relative; display: flex; flex-direction: column; min-width: 0; min-height: 0; }\n.htmlve-titolo {\n  display: flex;\n  align-items: center;\n  gap: 8px;\n  font-size: 12px;\n  font-family: Consolas, \"Courier New\", monospace;\n  padding: 2px 4px 2px 8px;\n  border-bottom: 1px solid var(--htmlve-bordo);\n  background: var(--htmlve-sfondo);\n  min-height: 26px;\n}\n.htmlve-nome-file { flex: 1; min-width: 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }\n.htmlve-btn.htmlve-apri { flex: none; font-family: system-ui, -apple-system, \"Segoe UI\", Roboto, sans-serif; font-size: 12px;\n  padding: 0 8px; line-height: 18px; color: var(--htmlve-accento); border-color: #9fb3c8; background: #fff; }\n.htmlve-btn.htmlve-apri:disabled { color: #6a737d; border-color: var(--htmlve-bordo); }\n.htmlve-cm { flex: 1; min-height: 0; position: relative; }\n.htmlve-ace { position: absolute; inset: 0; }\n.htmlve-vuoto {\n  display: none;\n  position: absolute;\n  top: 60px;\n  left: 50px;\n  right: 20px;\n  color: #6a737d;\n  font-size: 13px;\n}\n\n.htmlve-vista { display: flex; flex-direction: column; min-width: 0; min-height: 0; }\n.htmlve-schede {\n  display: flex;\n  align-items: flex-end;\n  padding: 4px 8px 0;\n  background: #dadce0;\n  min-height: 26px;\n}\n.htmlve-scheda {\n  display: flex;\n  align-items: center;\n  gap: 6px;\n  max-width: 260px;\n  min-width: 90px;\n  padding: 4px 12px;\n  background: #e8eaed;\n  border-radius: 8px 8px 0 0;\n  font-size: 12px;\n  color: #202124;\n  overflow: hidden;\n  white-space: nowrap;\n}\n.htmlve-scheda::before {\n  content: \"\";\n  flex: none;\n  width: 10px;\n  height: 10px;\n  border-radius: 50%;\n  background: #9aa0a6;\n}\n.htmlve-scheda span { overflow: hidden; text-overflow: ellipsis; }\n.htmlve-scheda.senza-titolo span { color: #80868b; font-style: italic; }\n.htmlve-indirizzo {\n  display: flex;\n  align-items: center;\n  gap: 4px;\n  padding: 3px 6px;\n  background: #e8eaed;\n  border-bottom: 1px solid var(--htmlve-bordo);\n  min-height: 25px;\n}\n.htmlve-url {\n  flex: 1;\n  min-width: 0;\n  background: #fff;\n  border: 1px solid transparent;\n  border-radius: 10px;\n  padding: 1px 10px;\n  font-size: 12px;\n  line-height: 18px;\n  color: #3c4043;\n  font-family: Consolas, \"Courier New\", monospace;\n  overflow: hidden;\n  white-space: nowrap;\n  text-overflow: ellipsis;\n  margin: 0;\n}\n.htmlve-url:focus { outline: none; border-color: var(--htmlve-accento); color: #1d2125; }\n.htmlve-iframe { flex: 1; width: 100%; border: 0; background: #fff; min-height: 0; }\n.htmlve-avviso { display: none; font-size: 12px; padding: 4px 8px; background: #fff8e1; border-top: 1px solid #f0d78c; color: #6b5300; }\n\n/* finestrella per nomi e conferme */\n.htmlve-finestra { display: none; position: absolute; inset: 0; background: rgba(0, 0, 0, .25); z-index: 5; border-radius: 6px; }\n.htmlve-finestra.aperta { display: flex; align-items: flex-start; justify-content: center; padding-top: 70px; }\n.htmlve-dialogo { background: #fff; border-radius: 6px; padding: 14px 16px; width: min(440px, 92%); box-shadow: 0 6px 24px rgba(0, 0, 0, .2); }\n.htmlve-msg { margin-bottom: 8px; }\n.htmlve-input { width: 100%; font: inherit; font-family: Consolas, \"Courier New\", monospace; padding: 5px 8px; border: 1px solid var(--htmlve-bordo); border-radius: 4px; }\n.htmlve-errore { color: #b3261e; font-size: 12px; min-height: 16px; margin-top: 4px; }\n.htmlve-bottoni { display: flex; justify-content: flex-end; gap: 6px; margin-top: 6px; }\n\n/* sola lettura */\n.htmlve-lettura .htmlve-barra { background: #eef3ea; }\n.htmlve-grezza { border-top: 1px solid var(--htmlve-bordo); padding: 4px 8px; font-size: 12px; }\n.htmlve-grezza summary { cursor: pointer; color: #5c6670; }\n.htmlve-grezza pre { max-height: 240px; overflow: auto; font-size: 12px; white-space: pre-wrap; word-break: break-all; }\n\n/* schermo intero */\n.htmlve.htmlve-pieno { position: fixed; inset: 0; z-index: 100000; margin: 0; height: auto !important; padding: 6px; background: #f4f5f7; }\n.htmlve.htmlve-pieno .htmlve-corpo { grid-template-columns: 190px minmax(0, 1fr); }\n\n/* immagini */\n.htmlve-immagine { display: none; position: absolute; top: 27px; left: 0; right: 0; bottom: 0; background: #fafbfc;\n  flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 12px; z-index: 4; }\n.htmlve-immagine img { max-width: 100%; max-height: 80%; object-fit: contain; border: 1px solid var(--htmlve-bordo);\n  background: repeating-conic-gradient(#eee 0% 25%, #fff 0% 50%) 50% / 16px 16px; }\n.htmlve-didascalia { font-size: 12px; color: #5c6670; }\n.htmlve-griglia { display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 8px; max-height: 260px; overflow: auto; }\n.htmlve-scelta { display: flex; flex-direction: column; align-items: center; gap: 4px; width: 112px; padding: 6px;\n  border: 1px solid var(--htmlve-bordo); border-radius: 4px; background: #fff; cursor: pointer; font: inherit; font-size: 12px; }\n.htmlve-scelta:hover { border-color: var(--htmlve-accento); }\n.htmlve-scelta img { width: 96px; height: 64px; object-fit: contain; }\n.htmlve-scelta span { max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }\n\n/* spostamento */\n.htmlve-voce.htmlve-sopra { background: #cfe2f7; outline: 2px dashed var(--htmlve-accento); outline-offset: -2px; }\n.htmlve-destinazioni { display: flex; flex-direction: column; max-height: 260px; overflow: auto; margin: 4px 0 8px;\n  border: 1px solid var(--htmlve-bordo); border-radius: 4px; }\n.htmlve-destinazione { display: flex; align-items: center; gap: 6px; padding: 5px 8px; border: 0; background: #fff;\n  text-align: left; font: inherit; font-size: 13px; cursor: pointer; }\n.htmlve-destinazione:hover:not(:disabled) { background: #e9eef5; }\n.htmlve-destinazione:disabled { color: #9aa1a8; cursor: default; }\n";
    var ANTEPRIMA_PHP = "\"\"\"Anteprima delle pagine PHP nell'editor html_sito: questo programma lo manda l'interfaccia a Jobe con il\nservizio web di CodeRunner (qtype_coderunner_run_in_sandbox), insieme al file richiesta.json con il sito\ne la richiesta. Esegue la pagina come il controllo del prototipo php_sito (stesso avvio di PHP, stessa\nfacciata di mysqli) e stampa un JSON: {\"html\": quello che stampa la pagina, \"stato\": il database dopo\nla richiesta, in base64}. Lo stato torna all'interfaccia, che lo rimanda alla richiesta successiva:\ncosì l'INSERT di un modulo si vede poi nella pagina dell'elenco, come con XAMPP.\n\nNon si modifica il file costruito: build.py ci mette AVVIO_PHP (da template.py del prototipo) e la\nfacciata di mysqli (da domande-php-mysqli-mock), negli stessi segnaposto qui sotto.\"\"\"\nimport base64\nimport json\nimport os\nimport re\nimport subprocess\n\nAVVIO_PHP = \"<?php\\n$__r = json_decode(file_get_contents($argv[1]), true);\\n$_GET = $__r[\\\"get\\\"];\\n$_POST = $__r[\\\"post\\\"];\\n$_REQUEST = array_merge($_GET, $_POST);\\n$_COOKIE = [];\\n$_FILES = [];\\n$_SERVER[\\\"REQUEST_METHOD\\\"] = $__r[\\\"metodo\\\"];\\n$_SERVER[\\\"QUERY_STRING\\\"] = http_build_query($_GET);\\n$_SERVER[\\\"SCRIPT_NAME\\\"] = $_SERVER[\\\"PHP_SELF\\\"] = \\\"/\\\" . $__r[\\\"pagina\\\"];\\n$_SERVER[\\\"REQUEST_URI\\\"] = \\\"/\\\" . $__r[\\\"pagina\\\"] . ($_GET ? \\\"?\\\" . http_build_query($_GET) : \\\"\\\");\\n$_SERVER[\\\"HTTP_HOST\\\"] = $_SERVER[\\\"SERVER_NAME\\\"] = \\\"localhost\\\";\\nif ($__r[\\\"db\\\"] !== \\\"\\\") {\\n    // pagine con il database: la facciata di mysqli del prototipo php_mysqli_sqlite, sul database di lavoro\\n    require $__r[\\\"fakedb\\\"];\\n    FakeDB::$file = $__r[\\\"db\\\"];\\n    FakeDB::$database = $__r[\\\"nomedb\\\"];\\n}\\nchdir($__r[\\\"cartella\\\"]);\\nini_set(\\\"open_basedir\\\", $__r[\\\"radice\\\"]);\\n$GLOBALS[\\\"__file_php_sito\\\"] = $__r[\\\"file\\\"];\\nunset($__r, $argv, $argc);\\ninclude $GLOBALS[\\\"__file_php_sito\\\"];\\n\"\nFAKEDB_PHP = \"<?php\\n/* =====================================================================\\n * Prototipo php_mysqli_sqlite per CodeRunner (PHP)\\n * La facciata di mysqli (funzioni, classi, controllo delle credenziali) è\\n * simulata; le query vengono ESEGUITE DAVVERO su un database SQLite creato\\n * dal campo Test, con il client sqlite3 di Jobe (lo stesso delle domande SQL).\\n * Gli errori delle query sono quelli di SQLite, così come escono.\\n *\\n * REQUISITI su Jobe: client sqlite3 nel PATH; proc_open consentito in PHP;\\n * estensione PHP mysqli NON caricata (altrimenti \\\"Cannot redeclare\\\").\\n *\\n * Nota Twig: in questo codice non usare mai due graffe aperte di seguito,\\n * né una graffa seguita da cancelletto o percento.\\n * ===================================================================== */\\n\\ndefine('MYSQLI_ASSOC', 1);\\ndefine('MYSQLI_NUM', 2);\\ndefine('MYSQLI_BOTH', 3);\\ndefine('MYSQLI_REPORT_OFF', 0);\\ndefine('MYSQLI_REPORT_ERROR', 1);\\ndefine('MYSQLI_REPORT_STRICT', 2);\\ndefine('MYSQLI_REPORT_ALL', 255);\\n\\nclass mysqli_sql_exception extends RuntimeException {}\\n\\nfinal class FakeDB\\n{\\n    const SEP = '#@FAKEDB-SEPARATORE@#';\\n\\n    // ---- configurazione (impostata dal campo Test con FakeDB::configure) ----\\n    public static $hosts = ['localhost', '127.0.0.1'];\\n    public static $port = null;          // null = accetta qualsiasi porta\\n    public static $user = 'root';\\n    public static $password = '';\\n    public static $database = '';       // '*' = qualsiasi nome (controllo tollerante del prototipo php_sito)\\n    public static $schema = '';          // SQL che crea e popola il database\\n    public static $dbfile = '';          // file .db allegato; se vuoto, l'unico .db allegato alla domanda\\n    public static $foreignKeys = true;   // PRAGMA foreign_keys = ON a ogni query\\n    public static $queries = [];         // facoltativo: query (o /regex/) => risultato forzato\\n    public static $exceptions = false;   // true = comportamento predefinito di PHP 8.1+\\n    public static $sqlite = 'sqlite3';   // comando del client\\n\\n    // ---- stato interno ----\\n    public static $file = null;\\n    public static $log = [];\\n    public static $connectErrno = 0;\\n    public static $connectError = null;\\n\\n    public static function configure(array $config)\\n    {\\n        foreach ($config as $key => $value) {\\n            if (!property_exists(self::class, $key) || in_array($key, ['file', 'log'], true)) {\\n                throw new InvalidArgumentException(\\\"FakeDB: opzione sconosciuta '$key'\\\");\\n            }\\n            self::${$key} = $value;\\n        }\\n        self::prepareDatabase();\\n    }\\n\\n    // Crea il database di lavoro: copia del file allegato e/o esecuzione dello schema\\n    private static function prepareDatabase()\\n    {\\n        self::$file = getcwd() . '/fakedb_lavoro.sqlite';\\n        if (file_exists(self::$file)) {\\n            unlink(self::$file);\\n        }\\n        $sorgente = self::$dbfile;\\n        if ($sorgente === '') {                       // nessun file indicato: l'unico .db allegato, se c'è\\n            $allegati = glob('*.db');\\n            if (count($allegati) > 1) {\\n                throw new RuntimeException(\\\"FakeDB: la domanda ha più file .db allegati, indica quale con 'dbfile'\\\");\\n            }\\n            $sorgente = $allegati ? $allegati[0] : '';\\n        }\\n        if ($sorgente !== '') {\\n            if (!copy($sorgente, self::$file)) {\\n                throw new RuntimeException(\\\"FakeDB: file del database non trovato: \\\" . $sorgente);\\n            }\\n        }\\n        if (trim(self::$schema) !== '') {\\n            $prefisso = self::$foreignKeys ? \\\"PRAGMA foreign_keys = ON;\\\\n\\\" : '';\\n            $esito = self::cli($prefisso . self::$schema . \\\"\\\\n;\\\\n\\\");\\n            $errori = self::parseErrors($esito[1]);\\n            if ($errori) {\\n                throw new RuntimeException(\\\"FakeDB: errore nello schema del test: \\\" . $errori[0][0]);\\n            }\\n        } elseif ($sorgente === '') {\\n            touch(self::$file);\\n        }\\n    }\\n\\n    // Esegue uno script con il client sqlite3 sul database di lavoro: [stdout, stderr]\\n    public static function cli($script)\\n    {\\n        $descrittori = [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']];\\n        $processo = proc_open([self::$sqlite, self::$file], $descrittori, $pipes);\\n        if (!is_resource($processo)) {\\n            throw new RuntimeException('FakeDB: impossibile avviare ' . self::$sqlite);\\n        }\\n        fwrite($pipes[0], $script);\\n        fclose($pipes[0]);\\n        $uscita = stream_get_contents($pipes[1]);\\n        fclose($pipes[1]);\\n        $errori = stream_get_contents($pipes[2]);\\n        fclose($pipes[2]);\\n        proc_close($processo);\\n        return [$uscita, $errori];\\n    }\\n\\n    // Righe \\\"Parse error near line N: messaggio\\\" -> [[messaggio, codice], ...]\\n    public static function parseErrors($stderr)\\n    {\\n        $errori = [];\\n        foreach (preg_split('/\\\\R/', (string)$stderr) as $riga) {\\n            if (preg_match('/^(?:Parse error|Runtime error|Error)(?: near line \\\\d+)?: (.*?)(?: \\\\((\\\\d+)\\\\))?$/', $riga, $m)) {\\n                $errori[] = [$m[1], isset($m[2]) && $m[2] !== '' ? (int)$m[2] : 1];\\n            }\\n        }\\n        return $errori;\\n    }\\n\\n    // true se apici, virgolette e commenti sono tutti chiusi\\n    private static function balanced($sql)\\n    {\\n        $n = strlen($sql);\\n        $i = 0;\\n        while ($i < $n) {\\n            $c = $sql[$i];\\n            if ($c === '-' && substr($sql, $i, 2) === '--') {\\n                $j = strpos($sql, \\\"\\\\n\\\", $i);\\n                if ($j === false) {\\n                    return true;\\n                }\\n                $i = $j + 1;\\n                continue;\\n            }\\n            if ($c === '/' && substr($sql, $i, 2) === '/*') {\\n                $j = strpos($sql, '*/', $i + 2);\\n                if ($j === false) {\\n                    return false;\\n                }\\n                $i = $j + 2;\\n                continue;\\n            }\\n            if ($c === \\\"'\\\" || $c === '\\\"' || $c === '`') {\\n                $j = strpos($sql, $c, $i + 1);\\n                if ($j === false) {\\n                    return false;\\n                }\\n                $i = $j + 1;\\n                continue;\\n            }\\n            $i++;\\n        }\\n        return true;\\n    }\\n\\n    // Prima parola della query (select, insert, ...), saltando spazi e commenti\\n    public static function verb($sql)\\n    {\\n        $s = preg_replace('#^(\\\\s+|--[^\\\\n]*\\\\n?|/\\\\*.*?\\\\*/)*#s', '', (string)$sql);\\n        return preg_match('/^([a-z]+)/i', $s, $m) ? strtolower($m[1]) : '';\\n    }\\n\\n    private static function decodeRows($testo)\\n    {\\n        $testo = trim($testo);\\n        if ($testo === '') {\\n            return [];\\n        }\\n        $dati = json_decode($testo, true);\\n        if (!is_array($dati)) {                       // più risultati: si tiene il primo\\n            $pezzi = preg_split('/\\\\]\\\\s*\\\\R\\\\[/', $testo, 2);\\n            $dati = json_decode($pezzi[0] . ']', true);\\n        }\\n        return is_array($dati) ? $dati : [];\\n    }\\n\\n    /* Esegue una query dello studente.\\n     * Restituisce ['error' => [messaggio, codice] o null, 'rows' => [...],\\n     *              'changes' => n, 'id' => n] */\\n    public static function execute($sql)\\n    {\\n        $script = \\\".mode json\\\\n\\\" . (self::$foreignKeys ? \\\"PRAGMA foreign_keys = ON;\\\\n\\\" : '');\\n        $chiusa = self::balanced($sql);\\n        if ($chiusa) {\\n            $script .= $sql . \\\"\\\\n;\\\\n.print \\\" . self::SEP . \\\"\\\\nSELECT changes() AS c, last_insert_rowid() AS i;\\\\n\\\";\\n        } else {\\n            $script .= $sql . \\\"\\\\n\\\";                   // l'errore lo segnala sqlite3\\n        }\\n        list($uscita, $stderr) = self::cli($script);\\n        $errori = self::parseErrors($stderr);\\n        $parti = preg_split('/^' . preg_quote(self::SEP, '/') . '\\\\s*$/m', $uscita, 2);\\n        $meta = isset($parti[1]) ? self::decodeRows($parti[1]) : [];\\n        return [\\n            'error' => $errori ? $errori[0] : null,\\n            'rows' => self::decodeRows($parti[0]),\\n            'changes' => isset($meta[0]['c']) ? (int)$meta[0]['c'] : 0,\\n            'id' => isset($meta[0]['i']) ? (int)$meta[0]['i'] : 0,\\n        ];\\n    }\\n\\n    // ---- funzioni di supporto per i test ----\\n\\n    // Righe di una SELECT sul database di lavoro (valori come stringhe)\\n    public static function rows($sql)\\n    {\\n        $esito = self::execute($sql);\\n        if ($esito['error']) {\\n            throw new RuntimeException('FakeDB::rows: ' . $esito['error'][0]);\\n        }\\n        return array_map(function ($riga) {\\n            return array_map(function ($v) {\\n                return $v === null ? null : (string)$v;\\n            }, $riga);\\n        }, $esito['rows']);\\n    }\\n\\n    public static function count($tabella)\\n    {\\n        $righe = self::rows(\\\"SELECT COUNT(*) AS n FROM $tabella\\\");\\n        return (int)$righe[0]['n'];\\n    }\\n\\n    public static function normalize($sql)\\n    {\\n        $sql = str_replace('`', '', strtolower(trim((string)$sql)));\\n        $sql = rtrim($sql, \\\"; \\\\t\\\\r\\\\n\\\");\\n        $sql = preg_replace('/\\\\s+/', ' ', $sql);\\n        return preg_replace('/\\\\s*([,=()<>])\\\\s*/', '$1', $sql);\\n    }\\n\\n    // Risultato forzato dalla mappa 'queries', se la query vi compare\\n    public static function lookup($sql)\\n    {\\n        $normalized = self::normalize($sql);\\n        foreach (self::$queries as $pattern => $result) {\\n            $pattern = (string)$pattern;\\n            $isRegex = strlen($pattern) > 1 && $pattern[0] === '/';\\n            $match = $isRegex\\n                ? preg_match($pattern, $normalized) === 1\\n                : self::normalize($pattern) === $normalized;\\n            if ($match) {\\n                return [true, $result];\\n            }\\n        }\\n        return [false, null];\\n    }\\n\\n    public static function checkConnection($host, $user, $password, $database, $port)\\n    {\\n        $host = $host ?? 'localhost';\\n        $user = (string)$user;\\n        $password = (string)$password;\\n        $database = (string)$database;\\n\\n        if (!in_array($host, self::$hosts, true)) {\\n            return [2002, \\\"php_network_getaddresses: getaddrinfo for $host failed: Name or service not known\\\"];\\n        }\\n        if (self::$port !== null && $port !== null && (int)$port !== (int)self::$port) {\\n            return [2002, 'Connection refused'];\\n        }\\n        if ($user !== self::$user || $password !== self::$password) {\\n            $usingPassword = $password === '' ? 'NO' : 'YES';\\n            return [1045, \\\"Access denied for user '$user'@'localhost' (using password: $usingPassword)\\\"];\\n        }\\n        if ($database !== '' && self::$database !== '*' && $database !== self::$database) {\\n            return [1049, \\\"Unknown database '$database'\\\"];\\n        }\\n        return null;\\n    }\\n\\n    public static function executedQueries()\\n    {\\n        $out = [];\\n        foreach (self::$log as $entry) {\\n            if ($entry[0] === 'query') {\\n                $out[] = $entry[1];\\n            }\\n        }\\n        return $out;\\n    }\\n\\n    public static function connectionClosed()\\n    {\\n        foreach (self::$log as $entry) {\\n            if ($entry[0] === 'close') {\\n                return true;\\n            }\\n        }\\n        return false;\\n    }\\n}\\n\\nclass mysqli\\n{\\n    public $connect_errno = 0;\\n    public $connect_error = null;\\n    public $errno = 0;\\n    public $error = '';\\n    public $affected_rows = 0;\\n    public $insert_id = 0;\\n    private $db = '';\\n    private $connected = false;\\n    private $closed = false;\\n\\n    public function __construct($hostname = null, $username = null, $password = null,\\n                                $database = '', $port = null, $socket = null)\\n    {\\n        FakeDB::$log[] = ['connect', $hostname, $username, $password, $database];\\n        $error = FakeDB::checkConnection($hostname, $username, $password, $database, $port);\\n        if ($error !== null) {\\n            $this->connect_errno = $error[0];\\n            $this->connect_error = $error[1];\\n            FakeDB::$connectErrno = $error[0];\\n            FakeDB::$connectError = $error[1];\\n            if (FakeDB::$exceptions) {\\n                throw new mysqli_sql_exception($error[1], $error[0]);\\n            }\\n            return;\\n        }\\n        FakeDB::$connectErrno = 0;\\n        FakeDB::$connectError = null;\\n        $this->connected = true;\\n        $this->db = (string)$database;\\n    }\\n\\n    private function ensureUsable()\\n    {\\n        if ($this->closed) {\\n            throw new Error('mysqli object is already closed');\\n        }\\n        if (!$this->connected) {\\n            throw new Error('mysqli object is not fully initialized');\\n        }\\n    }\\n\\n    private function fail($errno, $message)\\n    {\\n        $this->errno = $errno;\\n        $this->error = $message;\\n        if (FakeDB::$exceptions) {\\n            throw new mysqli_sql_exception($message, $errno);\\n        }\\n        return false;\\n    }\\n\\n    public function query($query)\\n    {\\n        $this->ensureUsable();\\n        FakeDB::$log[] = ['query', $query];\\n        $this->errno = 0;\\n        $this->error = '';\\n\\n        if ($this->db === '') {\\n            return $this->fail(1046, 'No database selected');\\n        }\\n\\n        // 1. risultato forzato dal test, se previsto\\n        list($found, $result) = FakeDB::lookup($query);\\n        if ($found) {\\n            if ($result === true) {\\n                $this->affected_rows = 0;\\n                return true;\\n            }\\n            if (is_int($result)) {\\n                $this->affected_rows = $result;\\n                return true;\\n            }\\n            if (is_array($result) && isset($result['error'])) {\\n                return $this->fail($result['error'][0], $result['error'][1]);\\n            }\\n            if (is_array($result) && (isset($result['affected']) || isset($result['insert_id']))) {\\n                $this->affected_rows = $result['affected'] ?? 0;\\n                $this->insert_id = $result['insert_id'] ?? 0;\\n                return true;\\n            }\\n            $res = new mysqli_result($result);\\n            $this->affected_rows = $res->num_rows;\\n            return $res;\\n        }\\n\\n        // 2. esecuzione vera su SQLite\\n        $esito = FakeDB::execute($query);\\n        if ($esito['error'] !== null) {\\n            return $this->fail($esito['error'][1], $esito['error'][0]);\\n        }\\n        $verbo = FakeDB::verb($query);\\n        if (in_array($verbo, ['select', 'with', 'values', 'pragma', 'explain'], true)) {\\n            $res = new mysqli_result($esito['rows']);\\n            $this->affected_rows = $res->num_rows;\\n            return $res;\\n        }\\n        $this->affected_rows = $esito['changes'];\\n        if (in_array($verbo, ['insert', 'replace'], true)) {\\n            $this->insert_id = $esito['id'];\\n        }\\n        return true;\\n    }\\n\\n    public function select_db($database)\\n    {\\n        $this->ensureUsable();\\n        if (FakeDB::$database !== '*' && $database !== FakeDB::$database) {\\n            return $this->fail(1049, \\\"Unknown database '$database'\\\");\\n        }\\n        $this->db = $database;\\n        return true;\\n    }\\n\\n    public function set_charset($charset)\\n    {\\n        $this->ensureUsable();\\n        return true;\\n    }\\n\\n    public function real_escape_string($string)\\n    {\\n        $this->ensureUsable();\\n        return str_replace(\\\"'\\\", \\\"''\\\", (string)$string);   // '' vale sia in SQLite sia in MySQL\\n    }\\n\\n    public function close()\\n    {\\n        $this->ensureUsable();\\n        $this->closed = true;\\n        FakeDB::$log[] = ['close'];\\n        return true;\\n    }\\n}\\n\\nclass mysqli_result implements IteratorAggregate\\n{\\n    public $num_rows = 0;\\n    public $field_count = 0;\\n    private $rows = [];\\n    private $position = 0;\\n\\n    public function __construct(array $rows)\\n    {\\n        // Come il vero mysqli (query non preparate): tutti i valori arrivano come stringhe\\n        foreach ($rows as $row) {\\n            $this->rows[] = array_map(function ($v) {\\n                return $v === null ? null : (string)$v;\\n            }, $row);\\n        }\\n        $this->num_rows = count($this->rows);\\n        $this->field_count = $this->num_rows ? count($this->rows[0]) : 0;\\n    }\\n\\n    public function fetch_assoc()\\n    {\\n        return $this->position < $this->num_rows ? $this->rows[$this->position++] : null;\\n    }\\n\\n    public function fetch_row()\\n    {\\n        $r = $this->fetch_assoc();\\n        return $r === null ? null : array_values($r);\\n    }\\n\\n    public function fetch_object()\\n    {\\n        $r = $this->fetch_assoc();\\n        return $r === null ? null : (object)$r;\\n    }\\n\\n    public function fetch_array($mode = MYSQLI_BOTH)\\n    {\\n        $r = $this->fetch_assoc();\\n        if ($r === null || $mode === MYSQLI_ASSOC) {\\n            return $r;\\n        }\\n        if ($mode === MYSQLI_NUM) {\\n            return array_values($r);\\n        }\\n        $both = [];\\n        $i = 0;\\n        foreach ($r as $k => $v) {\\n            $both[$i++] = $v;\\n            $both[$k] = $v;\\n        }\\n        return $both;\\n    }\\n\\n    public function fetch_all($mode = MYSQLI_NUM)\\n    {\\n        $all = [];\\n        while (($r = $this->fetch_array($mode)) !== null) {\\n            $all[] = $r;\\n        }\\n        return $all;\\n    }\\n\\n    public function data_seek($offset)\\n    {\\n        if ($offset < 0 || $offset >= $this->num_rows) {\\n            return false;\\n        }\\n        $this->position = $offset;\\n        return true;\\n    }\\n\\n    public function free() {}\\n\\n    public function getIterator(): Iterator\\n    {\\n        $rest = array_slice($this->rows, $this->position);\\n        $this->position = $this->num_rows;\\n        return new ArrayIterator($rest);\\n    }\\n}\\n\\n// ---- Stile procedurale (i type hint producono gli stessi TypeError del vero mysqli) ----\\nfunction mysqli_connect($hostname = null, $username = null, $password = null,\\n                        $database = '', $port = null, $socket = null)\\n{\\n    $conn = new mysqli($hostname, $username, $password, $database, $port, $socket);\\n    return $conn->connect_errno ? false : $conn;\\n}\\nfunction mysqli_connect_errno() { return FakeDB::$connectErrno; }\\nfunction mysqli_connect_error() { return FakeDB::$connectError; }\\nfunction mysqli_query(mysqli $mysql, $query) { return $mysql->query($query); }\\nfunction mysqli_error(mysqli $mysql) { return $mysql->error; }\\nfunction mysqli_errno(mysqli $mysql) { return $mysql->errno; }\\nfunction mysqli_select_db(mysqli $mysql, $database) { return $mysql->select_db($database); }\\nfunction mysqli_set_charset(mysqli $mysql, $charset) { return $mysql->set_charset($charset); }\\nfunction mysqli_real_escape_string(mysqli $mysql, $string) { return $mysql->real_escape_string($string); }\\nfunction mysqli_affected_rows(mysqli $mysql) { return $mysql->affected_rows; }\\nfunction mysqli_insert_id(mysqli $mysql) { return $mysql->insert_id; }\\nfunction mysqli_close(mysqli $mysql) { return $mysql->close(); }\\nfunction mysqli_fetch_assoc(mysqli_result $result) { return $result->fetch_assoc(); }\\nfunction mysqli_fetch_row(mysqli_result $result) { return $result->fetch_row(); }\\nfunction mysqli_fetch_object(mysqli_result $result) { return $result->fetch_object(); }\\nfunction mysqli_fetch_array(mysqli_result $result, $mode = MYSQLI_BOTH) { return $result->fetch_array($mode); }\\nfunction mysqli_fetch_all(mysqli_result $result, $mode = MYSQLI_NUM) { return $result->fetch_all($mode); }\\nfunction mysqli_num_rows(mysqli_result $result) { return $result->num_rows; }\\nfunction mysqli_num_fields(mysqli_result $result) { return $result->field_count; }\\nfunction mysqli_data_seek(mysqli_result $result, $offset) { return $result->data_seek($offset); }\\nfunction mysqli_free_result(mysqli_result $result) { $result->free(); }\\nfunction mysqli_report($flags)\\n{\\n    FakeDB::$exceptions = (bool)($flags & MYSQLI_REPORT_STRICT);\\n    return true;\\n}\\n\\n/* ======================= fine del mock ======================= */\\n\"\nTROPPO_LENTO = \"La pagina non finisce entro 5 secondi: c'è un ciclo che non si ferma?\"\n\n\ndef esci(**dati):\n    print(json.dumps(dati, ensure_ascii=False))\n    raise SystemExit(0)\n\n\ndef dati_php(coppie):\n    \"\"\"Le coppie [name, valore] del modulo come le riceve PHP: name[] diventa un array.\"\"\"\n    out = {}\n    for nome, valore in coppie:\n        if nome.endswith(\"[]\"):\n            out.setdefault(nome[:-2], []).append(valore)\n        else:\n            out[nome] = valore\n    return out\n\n\nr = json.load(open(\"richiesta.json\", encoding=\"utf-8\"))\nradice = os.path.abspath(\"sito\")\nfor percorso, contenuto in r[\"files\"].items():\n    parti = [p for p in str(percorso).split(\"/\") if p not in (\"\", \".\", \"..\")]\n    if not parti:\n        continue\n    destinazione = os.path.join(radice, *parti)\n    os.makedirs(os.path.dirname(destinazione), exist_ok=True)\n    with open(destinazione, \"w\", encoding=\"utf-8\") as f:\n        f.write(contenuto)\npagina = \"/\".join(p for p in r[\"pagina\"].split(\"/\") if p not in (\"\", \".\", \"..\"))\ncompleto = os.path.join(radice, *pagina.split(\"/\"))\nif not os.path.isfile(completo):\n    esci(errore=\"Non trovo la pagina %s.\" % pagina)\n\ndb = \"\"\nif r.get(\"db\"):\n    db = os.path.abspath(\"lavoro.sqlite\")\n    if r.get(\"stato\"):\n        with open(db, \"wb\") as f:\n            f.write(base64.b64decode(r[\"stato\"]))\n    else:\n        try:   # il database si costruisce con la libreria SQLite di Python, se c'è; altrimenti con il client sqlite3\n            import sqlite3\n            con = sqlite3.connect(db)\n            try:\n                con.executescript(r[\"db\"][\"sql\"])\n                con.commit()\n            except sqlite3.Error as e:\n                esci(errore=\"Errore nel database della domanda (avvisa l'insegnante): %s\" % e)\n            finally:\n                con.close()\n        except ImportError:\n            p = subprocess.run([\"sqlite3\", db], input=r[\"db\"][\"sql\"] + \"\\n;\\n\", capture_output=True, text=True,\n                               timeout=20)\n            if p.stderr.strip():\n                esci(errore=\"Errore nel database della domanda (avvisa l'insegnante): \" + p.stderr.strip()[:300])\n    with open(\"fakedb_php_sito.php\", \"w\", encoding=\"utf-8\") as f:\n        f.write(FAKEDB_PHP)\n\nwith open(\"avvio_php_sito.php\", \"w\", encoding=\"utf-8\") as f:\n    f.write(AVVIO_PHP)\nmetodo = \"POST\" if r.get(\"metodo\") == \"post\" else \"GET\"\ncoppie = r.get(\"dati\") or []\ndati = {\"get\": dati_php(coppie) if metodo == \"GET\" else {}, \"post\": dati_php(coppie) if metodo == \"POST\" else {},\n        \"metodo\": metodo, \"pagina\": pagina, \"cartella\": os.path.dirname(completo), \"radice\": radice,\n        \"file\": os.path.basename(completo), \"db\": db, \"fakedb\": os.path.abspath(\"fakedb_php_sito.php\"),\n        \"nomedb\": r[\"db\"].get(\"nomedb\", \"\") if db else \"\"}\nwith open(\"dati_richiesta.json\", \"w\", encoding=\"utf-8\") as f:\n    json.dump(dati, f)\ntry:\n    p = subprocess.run([\"php\", \"-d\", \"display_errors=stdout\", \"-d\", \"html_errors=0\", \"-d\", \"log_errors=0\",\n                        \"-d\", \"error_reporting=E_ALL\", \"-d\", \"max_execution_time=3\",\n                        os.path.abspath(\"avvio_php_sito.php\"), os.path.abspath(\"dati_richiesta.json\")],\n                       capture_output=True, text=True, timeout=6, cwd=radice)\n    uscita = p.stdout + p.stderr\nexcept subprocess.TimeoutExpired:\n    uscita = TROPPO_LENTO\nuscita = uscita.replace(radice + os.sep, \"\").replace(radice, \"\").replace(os.getcwd() + os.sep, \"\")\nuscita = re.sub(r\"(PHP )?Fatal error: +Maximum execution time of \\d+ seconds? exceeded.*\", TROPPO_LENTO, uscita)\nuscita = re.sub(r\" on line (\\d+)\", r\" alla riga \\1\", uscita)\nstato = \"\"\nif db:\n    with open(db, \"rb\") as f:\n        stato = base64.b64encode(f.read()).decode(\"ascii\")\nesci(html=uscita, stato=stato)\n"; // Programma Python che esegue una pagina PHP su Jobe (anteprima_php.py).
    var MAX_IMMAGINE = 500 * 1024; // Dimensione massima di un'immagine caricata dallo studente.
    var ESTENSIONI_IMMAGINE = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'ico', 'bmp'];

    /* ---------- percorsi ---------- */

    function cartellaDi(p) {
        var i = p.lastIndexOf('/');
        return i < 0 ? '' : p.slice(0, i);
    }
    function nomeDi(p) {
        return p.slice(p.lastIndexOf('/') + 1);
    }
    function unisci(d, n) {
        return d ? d + '/' + n : n;
    }
    function estensione(p) {
        var n = nomeDi(p);
        var i = n.lastIndexOf('.');
        return i < 0 ? '' : n.slice(i + 1).toLowerCase();
    }
    function eHtml(p) {
        var e = estensione(p);
        return e === 'html' || e === 'htm';
    }
    function ePhp(p) {
        return estensione(p) === 'php';
    }
    function esc(t) {
        return String(t).replace(/[<>&"]/g, function(c) {
            return {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;'}[c];
        });
    }

    /* Risolve un href relativo alla cartella della pagina. Restituisce null se il percorso
       esce dalla cartella del sito o è vuoto. Come su un server, maiuscole e minuscole contano. */
    function risolvi(cartella, href) {
        var p = href.split('#')[0].split('?')[0];
        if (p === '') {
            return null;
        }
        try {
            p = decodeURIComponent(p);
        } catch (e) {
            // Lascia il percorso com'è.
        }
        var parti = p.charAt(0) === '/' ? [] : (cartella ? cartella.split('/') : []);
        var pezzi = p.split('/');
        for (var i = 0; i < pezzi.length; i++) {
            var s = pezzi[i];
            if (s === '' || s === '.') {
                continue;
            }
            if (s === '..') {
                if (!parti.length) {
                    return null;
                }
                parti.pop();
            } else {
                parti.push(s);
            }
        }
        var r = parti.join('/');
        if (/\/$/.test(p) || r === '') {
            r = unisci(r, 'index.html');
        }
        return r;
    }

    function eImmagine(p) {
        return ESTENSIONI_IMMAGINE.indexOf(estensione(p)) >= 0;
    }

    /* Nome di file accettabile ricavato da quello di un file del computer: minuscole, senza accenti e spazi. */
    function nomePulito(n) {
        var s = (n || '').toLowerCase();
        if (s.normalize) {
            s = s.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        }
        s = s.replace(/\s+/g, '-').replace(/[^a-z0-9._-]/g, '');
        return s.replace(/^[.]+/, '');
    }

    /* Segnaposto per un'immagine fornita che non si trova nel testo della domanda. */
    function segnaposto(nome) {
        var t = nome.replace(/[<>&"]/g, '');
        var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="160" height="100">' +
            '<rect width="160" height="100" fill="#e9ecef" stroke="#adb5bd"/>' +
            '<text x="80" y="55" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#495057">' + t + '</text></svg>';
        return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    }

    function modoAce(p) {
        var e = estensione(p);
        if (e === 'html' || e === 'htm') {
            return 'ace/mode/html';
        }
        if (e === 'css') {
            return 'ace/mode/css';
        }
        if (e === 'js') {
            return 'ace/mode/javascript';
        }
        if (e === 'php') {
            return 'ace/mode/php';
        }
        return 'ace/mode/text';
    }

    function el(tag, cls, testo) {
        var e = document.createElement(tag);
        if (cls) {
            e.className = cls;
        }
        if (testo !== undefined && testo !== null) {
            e.textContent = testo;
        }
        return e;
    }

    function ora(d) {
        var due = function(n) {
            return (n < 10 ? '0' : '') + n;
        };
        return due(d.getHours()) + ':' + due(d.getMinutes()) + ':' + due(d.getSeconds());
    }

    function dataOra(iso) {
        var d = new Date(iso);
        return isNaN(d) ? '' : d.toLocaleDateString('it-IT') + ' ' + ora(d);
    }

    function aggiungiStile() {
        if (document.getElementById('html-sito-stile')) {
            return;
        }
        var s = document.createElement('style');
        s.id = 'html-sito-stile';
        s.textContent = STILE;
        document.head.appendChild(s);
    }

    /* ---------- formato della risposta ---------- */

    /* Estrae l'oggetto che comincia con {"htmlve" anche se nel testo c'è altro intorno. */
    function estraiOggetto(testo) {
        var a = testo.indexOf('{"htmlve"');
        if (a < 0) {
            return null;
        }
        var livello = 0, inStringa = false;
        for (var i = a; i < testo.length; i++) {
            var c = testo.charAt(i);
            if (inStringa) {
                if (c === '\\') {
                    i++;
                } else if (c === '"') {
                    inStringa = false;
                }
            } else if (c === '"') {
                inStringa = true;
            } else if (c === '{') {
                livello++;
            } else if (c === '}') {
                livello--;
                if (livello === 0) {
                    return testo.slice(a, i + 1);
                }
            }
        }
        return null;
    }

    function leggiSito(testo) {
        var json = testo ? estraiOggetto(testo) : null;
        if (!json) {
            return null;
        }
        try {
            var o = JSON.parse(json);
            if (!o || o.htmlve !== 1 || typeof o.files !== 'object') {
                return null;
            }
            var files = {}, immagini = {};
            Object.keys(o.files).forEach(function(k) {
                if (typeof o.files[k] === 'string') {
                    files[k] = o.files[k];
                }
            });
            if (o.immagini && typeof o.immagini === 'object') {
                Object.keys(o.immagini).forEach(function(k) {
                    if (typeof o.immagini[k] === 'string') {
                        immagini[k] = o.immagini[k];
                    }
                });
            }
            return {
                immagini: immagini,
                salvato: o.salvato || '',
                cartelle: Array.isArray(o.cartelle) ? o.cartelle.filter(function(c) {
                    return typeof c === 'string';
                }) : [],
                files: files
            };
        } catch (e) {
            return null;
        }
    }

    /* ---------- anteprima ---------- */

    // Inserito in ogni pagina dell'anteprima: i link passano dall'editor invece di navigare davvero.
    var SCRIPT_ANTEPRIMA = '(' + function() {
        document.addEventListener('click', function(e) {
            var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
            if (!a) {
                return;
            }
            var h = a.getAttribute('href');
            e.preventDefault();
            if (h.charAt(0) === '#') {
                var id = decodeURIComponent(h.slice(1));
                var t = id ? (document.getElementById(id) || document.getElementsByName(id)[0]) : null;
                if (t) {
                    t.scrollIntoView();
                } else if (!id) {
                    window.scrollTo(0, 0);
                }
                return;
            }
            parent.postMessage({htmlve: 'vai', href: h}, '*');
        }, true);
        // Invio di un modulo: il browser ha già controllato i campi (required, min, type=email...).
        // Se lo script della pagina non l'ha fermato, i dati passano all'editor, che mostra dove vanno.
        window.addEventListener('submit', function(e) {
            if (e.defaultPrevented) {
                return;
            }
            e.preventDefault();
            var f = e.target, s = e.submitter;
            var dati = [];
            var fd;
            try {
                fd = new FormData(f, s || undefined);
            } catch (x) {
                fd = new FormData(f);
            }
            fd.forEach(function(v, k) {
                dati.push([k, typeof v === 'string' ? v : (v && v.name) || '']);
            });
            var metodo = (s && s.getAttribute('formmethod')) || f.getAttribute('method') || 'get';
            var azione = (s && s.getAttribute('formaction')) || f.getAttribute('action') || '';
            parent.postMessage({htmlve: 'invio', metodo: metodo.toLowerCase(), azione: azione, dati: dati}, '*');
        }, false);
    }.toString() + ')();';

    function paginaMessaggio(titolo, testo) {
        return '<!DOCTYPE html><html><head><meta charset="utf-8">' +
            '<style>body{font-family:system-ui,sans-serif;color:#555;padding:24px}h1{font-size:18px}</style></head>' +
            '<body><h1>' + titolo + '</h1><p>' + testo + '</p></body></html>';
    }

    /* Tabella dei dati ricevuti da una pagina (dopo un modulo o un link con ?...). */
    function tabellaDati(richiesta) {
        if (!richiesta || !richiesta.dati.length) {
            return '<p>La pagina non ha ricevuto dati.</p>';
        }
        var nome = richiesta.metodo === 'post' ? '$_POST' : '$_GET';
        return '<p>Dati ricevuti con il metodo <b>' + richiesta.metodo.toUpperCase() + '</b> (in PHP si leggono in <code>' +
            nome + '</code>):</p><table><tr><th>name</th><th>valore</th></tr>' +
            richiesta.dati.map(function(d) {
                return '<tr><td><code>' + esc(d[0]) + '</code></td><td>' + (d[1] === '' ? '<i>(vuoto)</i>' : esc(d[1])) +
                    '</td></tr>';
            }).join('') + '</table>';
    }

    function paginaPhp(percorso, richiesta) {
        return '<!DOCTYPE html><html><head><meta charset="utf-8"><style>body{font-family:system-ui,sans-serif;' +
            'color:#444;padding:20px}h1{font-size:18px}table{border-collapse:collapse;margin-top:6px}' +
            'td,th{border:1px solid #bbb;padding:4px 10px;text-align:left}th{background:#eee}' +
            '.nota{background:#fff8e1;border-left:4px solid #f0ad4e;padding:8px 12px}</style></head><body>' +
            '<h1>Pagina PHP: ' + esc(percorso) + '</h1>' + tabellaDati(richiesta) +
            '<p class="nota">In questa domanda l\'anteprima non esegue il PHP: mostra solo i dati che arrivano alla ' +
            'pagina. Le pagine PHP le esegue il pulsante <b>Verifica</b> sotto l\'editor, con i dati delle prove: ' +
            'i risultati compaiono sotto la domanda.</p>' +
            '</body></html>';
    }

    /* Quando l'anteprima non riesce a far eseguire la pagina PHP: il motivo e i dati che la pagina riceverebbe. */
    function paginaErrorePhp(percorso, richiesta, testo) {
        return paginaPhp(percorso, richiesta).replace(/<p class="nota">[\s\S]*?<\/p>/,
            '<p class="nota">' + esc(testo) + '</p>');
    }

    function paginaNonTrovata(url) {
        var u = esc(url);
        return '<!DOCTYPE html><html><head><meta charset="utf-8"><title>404 Not Found</title></head><body>' +
            '<h1>Not Found</h1><p>The requested URL ' + u + ' was not found on this server.</p><hr>' +
            '<address>Apache Server</address></body></html>';
    }

    /* ---------- interfaccia ---------- */

    /**
     * Costruttore richiesto da CodeRunner: solo lavoro sincrono e leggero.
     * Ace si crea in postInsert(), quando l'elemento è già nella pagina.
     *
     * @param {string} textareaId id della textarea della risposta
     * @param {number} w larghezza disponibile
     * @param {number} h altezza disponibile
     * @param {object} params parametri dell'interfaccia (aiuti dell'editor, vedi in alto)
     */
    function SitoUi(textareaId, w, h, params) {
        this.textarea = document.getElementById(textareaId);
        this.params = params || {};
        this.fail = false;
        this.files = {};
        this.immagini = {};       // percorso nel sito -> nome dell'immagine fornita oppure data URL
        this.datiImmagini = {};   // nome dell'immagine fornita -> data URL (letta dal testo della domanda)
        this.cartelle = [];
        this.sessioni = {};
        this.aperto = null;
        this.selezione = '';
        this.selezioneCartella = true;
        this.pagina = null;
        this.storia = [];
        this.daSalvare = false;
        this.salvatoIl = '';
        this.altezza = ALTEZZA_PREDEFINITA;
        var vero = function(v) {
            return v === true || v === 1 || v === '1' || v === 'true';
        };
        this.aiuti = {
            chiusura: vero(this.params.chiusura_automatica),
            completamento: vero(this.params.completamento),
            errori: vero(this.params.segnala_errori)
        };
        var elenco = this.params.immagini;
        if (typeof elenco === 'string') {
            elenco = elenco.split(',');
        }
        this.fornite = (Array.isArray(elenco) ? elenco : []).map(function(n) {
            return String(n).trim();
        }).filter(function(n) {
            return n !== '';
        });
        this.filePc = vero(this.params.file_pc) || vero(this.params.carica_immagini);
        this.caricaConsentito = this.filePc;
        this.copiaConsentita = this.params.copia_incolla === undefined || vero(this.params.copia_incolla);
        this.anteprimaPhp = vero(this.params.anteprima_php);
        this.dbPhp = null;
        if (this.anteprimaPhp && this.params.anteprima_php_db) {
            try {
                this.dbPhp = typeof this.params.anteprima_php_db === 'string' ?
                    JSON.parse(this.params.anteprima_php_db) : this.params.anteprima_php_db;
            } catch (e) {
                window.console.error('anteprima_php_db non è un JSON valido', e);
            }
        }
        this.statoDb = '';        // Il database dopo l'ultima richiesta (base64), rimandato a quella successiva.
        this.uscitaPhp = null;    // Ultima pagina PHP eseguita: {chiave, firma, html}.
        this.numeroPhp = 0;       // Le risposte arrivate tardi (di una richiesta precedente) si scartano.
        this.forzaPhp = false;
        try {
            if (!window.ace) {
                throw new Error('Ace non è caricato');
            }
            this.solaLettura = this.textarea.readOnly || this.textarea.disabled;
            this.que = this.textarea.closest('.que');
            this.disposizione = leggiDisposizione();
            this.preparaTraccia();
            aggiungiStile();
            this.carica();
            this.costruisci();
            this.leggiImmaginiFornite();
        } catch (e) {
            window.console.error(e);
            this.fail = true;
        }
    }

    SitoUi.prototype.failed = function() {
        return this.fail;
    };

    SitoUi.prototype.failMessage = function() {
        return 'ace_ui_notready';
    };

    SitoUi.prototype.getElement = function() {
        var self = this;
        // Se CodeRunner non chiama postInsert(), Ace si crea appena l'elemento è nella pagina.
        setTimeout(function() {
            self.postInsert();
        }, 0);
        return this.radice;
    };

    SitoUi.prototype.postInsert = function() {
        if (this.fail || this.editor || !this.radice.isConnected) {
            return;
        }
        this.disponi();
        this.creaEditor();
        this.disegnaAlbero();
        var prima = this.files['index.html'] !== undefined ? 'index.html' : Object.keys(this.files).sort()[0];
        if (prima) {
            this.apri(prima, true);
        } else {
            this.mostraVuoto();
        }
        this.aggiornaAnteprima();
        this.aggiornaStato();
        if (this.recuperato) {
            // Il lavoro recuperato dal browser va subito nella risposta.
            this.daSalvare = true;
            this.salvaSubito();
            this.recuperato = true;
            this.aggiornaStato();
        }
    };

    SitoUi.prototype.sync = function() {
        if (!this.fail) {
            this.salvaSubito();
        }
    };

    SitoUi.prototype.syncIntervalSecs = function() {
        return 2;
    };

    SitoUi.prototype.destroy = function() {
        if (this.fail) {
            return;
        }
        this.salvaSubito();
        clearTimeout(this.timerSalva);
        clearTimeout(this.timerAnteprima);
        window.removeEventListener('message', this.suMessaggio);
        document.removeEventListener('keydown', this.suTasto);
        document.documentElement.classList.remove('htmlve-blocca-scorrimento');
        if (this.osservatore) {
            this.osservatore.disconnect();
        }
        if (this.editor) {
            this.editor.destroy();
        }
        if (this.radice.parentNode) {
            this.radice.parentNode.removeChild(this.radice);
        }
    };

    SitoUi.prototype.resize = function(w, h) {
        // Si segue solo un ridimensionamento voluto (trascinando il bordo): così non si entra
        // in un ciclo con l'altezza del contenitore, che a sua volta dipende dall'editor.
        if (h >= ALTEZZA_MINIMA && Math.abs(h - this.altezza) > 30) {
            this.altezza = h;
            this.radice.style.height = h + 'px';
        }
        if (this.editor) {
            this.editor.resize();
        }
    };

    SitoUi.prototype.hasFocus = function() {
        return !!(this.editor && this.editor.isFocused());
    };

    // Lo schermo intero lo gestisce l'editor (pulsante nella barra), non CodeRunner.
    SitoUi.prototype.allowFullScreen = function() {
        return false;
    };

    SitoUi.prototype.setAllowFullScreen = function() {
        // Niente da fare: vedi allowFullScreen().
    };

    /* ---------- dati ---------- */

    SitoUi.prototype.chiaveCopia = function() {
        var m = /[?&]attempt=(\d+)/.exec(location.search);
        return m ? 'html_sito:' + location.host + ':' + m[1] + ':' + this.textarea.name : null;
    };

    SitoUi.prototype.carica = function() {
        var dati = leggiSito(this.textarea.value);
        this.testoRisposta = this.textarea.value;
        // Copia di sicurezza nel browser, solo durante un tentativo: si usa se è più recente della risposta.
        var chiave = this.solaLettura ? null : this.chiaveCopia();
        if (chiave) {
            try {
                var copia = leggiSito(window.localStorage.getItem(chiave));
                if (copia && (!dati || copia.salvato > dati.salvato)) {
                    dati = copia;
                    this.recuperato = true;
                }
            } catch (e) {
                // Il localStorage può non essere disponibile.
            }
        }
        if (dati) {
            this.files = dati.files;
            this.immagini = dati.immagini;
            this.cartelle = dati.cartelle;
            this.salvatoIl = dati.salvato;
        }
    };

    /* Tutte le cartelle: quelle create e quelle che contengono file. */
    SitoUi.prototype.tutteLeCartelle = function() {
        var set = {};
        var aggiungi = function(p) {
            while (p) {
                set[p] = true;
                p = cartellaDi(p);
            }
        };
        this.cartelle.forEach(aggiungi);
        Object.keys(this.files).concat(Object.keys(this.immagini)).forEach(function(f) {
            aggiungi(cartellaDi(f));
        });
        return Object.keys(set).sort();
    };

    SitoUi.prototype.esiste = function(p) {
        return this.files[p] !== undefined || this.immagini[p] !== undefined || this.tutteLeCartelle().indexOf(p) >= 0;
    };

    /* ---------- costruzione ---------- */

    SitoUi.prototype.costruisci = function() {
        var self = this;
        var r = this.radice = el('div', 'htmlve' + (this.solaLettura ? ' htmlve-lettura' : ''));
        r.style.height = this.altezza + 'px';
        // Tre blocchi: Traccia | Editor | Anteprima del browser; i due ai lati si chiudono e si allargano trascinando.
        var blocchi = this.blocchi = el('div', 'htmlve-blocchi');
        r.appendChild(blocchi);

        var barra = el('div', 'htmlve-barra');
        var bottone = function(testo, titolo, fn) {
            var b = el('button', 'htmlve-btn', testo);
            b.type = 'button';
            b.title = titolo;
            b.addEventListener('click', fn);
            barra.appendChild(b);
            return b;
        };
        if (!this.solaLettura) {
            bottone('+ File', 'Crea un nuovo file nella cartella selezionata', function() {
                self.nuovoFile();
            });
            bottone('+ Cartella', 'Crea una nuova cartella nella cartella selezionata', function() {
                self.nuovaCartella();
            });
            if (this.fornite.length || this.caricaConsentito) {
                bottone('+ Immagine', 'Mette un\'immagine nella cartella selezionata', function() {
                    self.nuovaImmagine();
                });
            }
            this.btnRinomina = bottone('Rinomina', 'Rinomina il file o la cartella selezionata', function() {
                self.rinomina();
            });
            this.btnSposta = bottone('Sposta', 'Sposta il file o la cartella selezionata in un\'altra cartella ' +
                    '(si può anche trascinare nell\'elenco)', function() {
                self.sposta();
            });
            this.btnElimina = bottone('Elimina', 'Elimina il file o la cartella selezionata', function() {
                self.elimina();
            });
        }
        if (this.filePc) {
            bottone('Scarica .zip', 'Scarica tutto il sito in un file .zip, da aprire sul computer', function() {
                self.scaricaZip();
            });
            if (!this.solaLettura) {
                bottone('Importa', 'Aggiunge alla cartella selezionata file del computer (.html, .css, .js, immagini) ' +
                        'o il contenuto di uno .zip', function() {
                    self.scegliFileDaImportare();
                });
            }
        }
        if (this.copiaConsentita) {
            bottone('Copia sito', 'Copia tutto il sito (file, cartelle e immagini), per incollarlo in un\'altra ' +
                    'domanda di questo quiz', function() {
                self.copiaSito();
            });
            if (!this.solaLettura) {
                bottone('Incolla sito', 'Mette qui il sito copiato con «Copia sito» al posto di quello che c\'è',
                        function() {
                    self.incollaSito();
                });
            }
        }
        // Nell'intestazione dell'editor: lo stato del salvataggio e i pulsanti dei blocchi (la barra resta ai file).
        var testataEditor = testata('Editor');
        this.stato = el('span', 'htmlve-stato htmlve-spinta');
        testataEditor.appendChild(this.stato);
        var mini = function(testo, titolo, fn) {
            var b = el('button', 'htmlve-btn htmlve-mini', testo);
            b.type = 'button';
            b.title = titolo;
            b.addEventListener('click', fn);
            testataEditor.appendChild(b);
            return b;
        };
        if (this.tracciaDisponibile) {
            this.btnTraccia = mini('Traccia', 'Mostra o nasconde la traccia (il testo della domanda)', function() {
                self.mostraPannello('traccia', !self.disposizione.traccia);
            });
        }
        this.btnVista = mini('Anteprima', 'Mostra o nasconde l\'anteprima del browser', function() {
            self.mostraPannello('vista', !self.disposizione.vista);
        });
        this.btnSchermo = mini('Schermo intero', 'Allarga l\'editor a tutta la finestra (Esc per tornare)', function() {
            self.schermoIntero();
        });

        if (this.tracciaDisponibile) {
            this.bTraccia = el('div', 'htmlve-blocco htmlve-b-traccia');
            this.bTraccia.appendChild(testata('Traccia', '‹', 'Chiudi la traccia', function() {
                self.mostraPannello('traccia', false);
            }));
            this.contenutoTraccia = el('div', 'htmlve-traccia');
            this.contenutoTraccia.appendChild(this.copiaTraccia);
            this.bTraccia.appendChild(this.contenutoTraccia);
            blocchi.appendChild(this.bTraccia);
            this.sTraccia = striscia('Traccia ›', 'Apri la traccia', function() {
                self.mostraPannello('traccia', true);
            });
            blocchi.appendChild(this.sTraccia);
            this.m1 = el('div', 'htmlve-maniglia');
            this.m1.title = 'Trascina per allargare o stringere la traccia';
            blocchi.appendChild(this.m1);
        }
        var bEditor = this.bEditor = el('div', 'htmlve-blocco htmlve-b-editor');
        bEditor.appendChild(testataEditor);
        bEditor.appendChild(barra);
        blocchi.appendChild(bEditor);

        var corpo = el('div', 'htmlve-corpo');
        this.albero = el('div', 'htmlve-albero');
        corpo.appendChild(this.albero);

        var codice = el('div', 'htmlve-codice');
        this.titoloFile = el('div', 'htmlve-titolo');
        this.nomeFile = el('span', 'htmlve-nome-file', '');
        this.titoloFile.appendChild(this.nomeFile);
        // L'anteprima non segue il file aperto: la pagina si apre nel browser con questo pulsante (o Ctrl+Invio).
        this.btnApri = el('button', 'htmlve-btn htmlve-mini htmlve-apri', '▶ Apri nel browser');
        this.btnApri.type = 'button';
        this.btnApri.title = 'Apre questa pagina nell\'anteprima del browser (Ctrl+Invio); una pagina PHP viene eseguita';
        this.btnApri.addEventListener('click', function() {
            self.apriNelBrowser();
        });
        this.titoloFile.appendChild(this.btnApri);
        codice.appendChild(this.titoloFile);
        var contenitore = el('div', 'htmlve-cm');
        this.ospiteAce = el('div', 'htmlve-ace');
        contenitore.appendChild(this.ospiteAce);
        codice.appendChild(contenitore);
        this.vuoto = el('div', 'htmlve-vuoto');
        codice.appendChild(this.vuoto);
        this.vistaImmagine = el('div', 'htmlve-immagine');
        codice.appendChild(this.vistaImmagine);
        corpo.appendChild(codice);
        bEditor.appendChild(corpo);

        this.m2 = el('div', 'htmlve-maniglia');
        this.m2.title = 'Trascina per allargare o stringere l\'anteprima';
        blocchi.appendChild(this.m2);
        var vista = this.bVista = el('div', 'htmlve-blocco htmlve-vista');
        vista.appendChild(testata('Anteprima del browser', '›', 'Chiudi l\'anteprima', function() {
            self.mostraPannello('vista', false);
        }));
        // La scheda del browser: il <title> della pagina, come lo vede chi visita il sito.
        var schede = el('div', 'htmlve-schede');
        this.scheda = el('div', 'htmlve-scheda');
        this.titoloScheda = el('span', '', '');
        this.scheda.appendChild(this.titoloScheda);
        schede.appendChild(this.scheda);
        vista.appendChild(schede);
        var indirizzo = el('div', 'htmlve-indirizzo');
        this.btnIndietro = el('button', 'htmlve-btn htmlve-mini', '←');
        this.btnIndietro.type = 'button';
        this.btnIndietro.title = 'Torna alla pagina precedente';
        this.btnIndietro.addEventListener('click', function() {
            self.indietro();
        });
        var ricarica = el('button', 'htmlve-btn htmlve-mini', '⟳');
        ricarica.type = 'button';
        ricarica.title = 'Ricarica l\'anteprima';
        ricarica.addEventListener('click', function() {
            self.forzaPhp = true;
            self.aggiornaAnteprima();
        });
        // La barra dell'indirizzo si può scrivere, come nel browser: pagine/libri.php?genere=Giallo e Invio.
        this.campoIndirizzo = el('input', 'htmlve-url');
        this.campoIndirizzo.type = 'text';
        this.campoIndirizzo.spellcheck = false;
        this.campoIndirizzo.setAttribute('aria-label', 'Indirizzo della pagina nell\'anteprima');
        this.campoIndirizzo.title = 'Scrivi l\'indirizzo di una pagina del sito (anche con ?nome=valore) e premi Invio';
        this.campoIndirizzo.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                self.vaiIndirizzo(self.campoIndirizzo.value);
            } else if (e.key === 'Escape') {
                e.stopPropagation();
                self.campoIndirizzo.value = self.indirizzoMostrato || '';
                self.campoIndirizzo.blur();
            }
        });
        this.campoIndirizzo.addEventListener('blur', function() {
            self.campoIndirizzo.value = self.indirizzoMostrato || '';
        });
        indirizzo.appendChild(this.btnIndietro);
        indirizzo.appendChild(ricarica);
        if (this.dbPhp) {
            var riparti = el('button', 'htmlve-btn htmlve-mini', '🗄');
            riparti.type = 'button';
            riparti.title = 'Database: riparti dai dati iniziali (annulla gli inserimenti e le modifiche fatti nell\'anteprima)';
            riparti.addEventListener('click', function() {
                self.statoDb = '';
                self.forzaPhp = true;
                self.aggiornaAnteprima();
            });
            indirizzo.appendChild(riparti);
        }
        indirizzo.appendChild(this.campoIndirizzo);
        vista.appendChild(indirizzo);
        this.iframe = el('iframe', 'htmlve-iframe');
        // allow-forms solo perché il browser controlli i campi prima dell'invio: l'invio vero lo ferma lo script.
        this.iframe.setAttribute('sandbox', 'allow-scripts allow-forms');
        this.iframe.setAttribute('title', 'Anteprima della pagina');
        vista.appendChild(this.iframe);
        this.avviso = el('div', 'htmlve-avviso');
        vista.appendChild(this.avviso);
        blocchi.appendChild(vista);
        this.sVista = striscia('‹ Anteprima', 'Apri l\'anteprima del browser', function() {
            self.mostraPannello('vista', true);
        });
        blocchi.appendChild(this.sVista);
        this.preparaManiglie();

        this.finestra = el('div', 'htmlve-finestra');
        r.appendChild(this.finestra);

        this.suMessaggio = function(e) {
            if (e.source !== self.iframe.contentWindow || !e.data) {
                return;
            }
            if (e.data.htmlve === 'vai') {
                self.vai(String(e.data.href));
            } else if (e.data.htmlve === 'invio' && Array.isArray(e.data.dati)) {
                self.invio(String(e.data.metodo || 'get'), String(e.data.azione || ''), e.data.dati.map(function(d) {
                    return [String(d[0]), String(d[1])];
                }));
            }
        };
        window.addEventListener('message', this.suMessaggio);

        this.suTasto = function(e) {
            if (e.key === 'Escape' && self.radice.classList.contains('htmlve-pieno') &&
                    !self.finestra.classList.contains('aperta')) {
                self.schermoIntero();
            }
        };
        document.addEventListener('keydown', this.suTasto);

        if (window.ResizeObserver) {
            this.osservatore = new ResizeObserver(function() {
                self.disponi();
            });
            this.osservatore.observe(r);
        }
    };

    /* ---------- i tre blocchi: Traccia | Editor | Anteprima del browser ---------- */

    function testata(titolo, simbolo, etichetta, fn) {
        var t = el('div', 'htmlve-testata');
        t.appendChild(el('span', 'htmlve-testata-titolo', titolo));
        if (fn) {
            var b = el('button', 'htmlve-btn htmlve-mini htmlve-spinta', simbolo);
            b.type = 'button';
            b.title = etichetta;
            b.setAttribute('aria-label', etichetta);
            b.addEventListener('click', fn);
            t.appendChild(b);
        }
        return t;
    }

    function striscia(testo, etichetta, fn) {
        var b = el('button', 'htmlve-striscia', testo);
        b.type = 'button';
        b.title = etichetta;
        b.setAttribute('aria-label', etichetta);
        b.addEventListener('click', fn);
        return b;
    }

    var CHIAVE_DISPOSIZIONE = 'html_sito:disposizione';

    /* Quali blocchi sono aperti e quanto sono larghi: si ricorda nel browser, per tutte le domande. */
    function leggiDisposizione() {
        var d = {traccia: true, vista: true, lt: 0, lv: 0};
        try {
            var salvata = JSON.parse(window.localStorage.getItem(CHIAVE_DISPOSIZIONE) || 'null');
            if (salvata && typeof salvata === 'object') {
                ['traccia', 'vista'].forEach(function(k) {
                    if (typeof salvata[k] === 'boolean') {
                        d[k] = salvata[k];
                    }
                });
                ['lt', 'lv'].forEach(function(k) {
                    if (typeof salvata[k] === 'number' && salvata[k] > 0) {
                        d[k] = salvata[k];
                    }
                });
            }
        } catch (e) {
            // Senza la memoria del browser si riparte ogni volta dalla disposizione predefinita.
        }
        return d;
    }

    SitoUi.prototype.salvaDisposizione = function() {
        try {
            window.localStorage.setItem(CHIAVE_DISPOSIZIONE, JSON.stringify(this.disposizione));
        } catch (e) {
            // Memoria del browser piena o non disponibile: pazienza.
        }
    };

    /* La traccia è una copia del testo della domanda, che sta nella stessa pagina sopra l'editor. */
    SitoUi.prototype.preparaTraccia = function() {
        this.tracciaDisponibile = false;
        if (this.params.traccia !== undefined && !(this.params.traccia === true || this.params.traccia === 1 ||
                this.params.traccia === '1' || this.params.traccia === 'true')) {
            return;
        }
        var fonte = this.que ? this.que.querySelector('.qtext') : null;
        var copia;
        if (fonte) {
            copia = fonte.cloneNode(true);
        } else {
            var formulazione = this.que ? this.que.querySelector('.formulation') : null;
            if (!formulazione) {
                return;
            }
            copia = formulazione.cloneNode(true);
            Array.prototype.forEach.call(copia.querySelectorAll('.ablock, .htmlve, .im-controls, .outcome, ' +
                    '.validationerror, textarea, input, select, button'), function(x) {
                x.remove();
            });
        }
        Array.prototype.forEach.call(copia.querySelectorAll('script'), function(x) {
            x.remove();
        });
        Array.prototype.forEach.call(copia.querySelectorAll('[id]'), function(x) {
            x.removeAttribute('id'); // Gli id restano unici nella pagina del quiz.
        });
        copia.removeAttribute('id');
        if (!copia.textContent.trim() && !copia.querySelector('img')) {
            return;
        }
        this.copiaTraccia = copia;
        this.tracciaDisponibile = true;
    };

    SitoUi.prototype.mostraPannello = function(nome, aperto) {
        this.disposizione[nome] = aperto;
        this.salvaDisposizione();
        this.disponi();
    };

    function limita(x, min, max) {
        return Math.max(min, Math.min(max, x));
    }

    /* Larghezze e posizione dei blocchi. Largo: i tre affiancati. Stretto (dentro una pagina del quiz piccola):
       la traccia a sinistra, editor e anteprima uno sopra l'altro. */
    SitoUi.prototype.disponi = function() {
        if (!this.blocchi) {
            return;
        }
        var d = this.disposizione;
        var W = this.blocchi.clientWidth || 1000;
        var stretto = W < 820;
        this.radice.classList.toggle('htmlve-stretto', stretto);
        var t = this.tracciaDisponibile && d.traccia;
        var v = d.vista;
        var lv = v && !stretto ? limita(d.lv || Math.round(W * 0.34), 220, Math.max(220, W - 360)) : 0;
        var lt = t ? limita(d.lt || Math.round(W * (stretto ? 0.3 : 0.24)), 160,
            Math.max(160, W - (stretto ? 380 : 360 + (v ? lv : 30)))) : 0;
        this.larghezze = {lt: lt, lv: lv, W: W};
        var mostra = function(x, si) {
            if (x) {
                x.style.display = si ? '' : 'none';
            }
        };
        mostra(this.bTraccia, t);
        mostra(this.sTraccia, this.tracciaDisponibile && !t);
        mostra(this.bVista, v);
        mostra(this.sVista, !v);
        if (this.m1) {
            this.m1.classList.toggle('htmlve-ferma', !t);
        }
        this.m2.classList.toggle('htmlve-ferma', !v || stretto);
        this.sVista.classList.toggle('htmlve-orizzontale', stretto);
        var colonne = this.tracciaDisponibile ? [t ? lt + 'px' : '30px', '8px'] : [];
        var c0 = colonne.length; // Numero di colonne della traccia (0 o 2).
        var posto = function(x, colonna, riga) {
            if (x) {
                x.style.gridColumn = colonna;
                x.style.gridRow = riga;
            }
        };
        if (stretto) {
            colonne.push('minmax(0, 1fr)');
            this.blocchi.style.gridTemplateColumns = colonne.join(' ');
            this.blocchi.style.gridTemplateRows = 'minmax(0, 1fr) 8px ' + (v ? 'minmax(0, 1fr)' : 'auto');
            posto(this.bTraccia, '1', '1 / span 3');
            posto(this.sTraccia, '1', '1 / span 3');
            posto(this.m1, '2', '1 / span 3');
            posto(this.bEditor, String(c0 + 1), '1');
            posto(this.m2, String(c0 + 1), '2');
            posto(this.bVista, String(c0 + 1), '3');
            posto(this.sVista, String(c0 + 1), '3');
        } else {
            colonne.push('minmax(0, 1fr)', '8px', v ? lv + 'px' : '30px');
            this.blocchi.style.gridTemplateColumns = colonne.join(' ');
            this.blocchi.style.gridTemplateRows = 'minmax(0, 1fr)';
            [this.bTraccia, this.sTraccia, this.m1, this.bEditor, this.m2, this.bVista, this.sVista].forEach(function(x) {
                posto(x, '', '');
            });
        }
        if (this.btnTraccia) {
            this.btnTraccia.classList.toggle('htmlve-premuto', t);
            this.btnTraccia.setAttribute('aria-pressed', t ? 'true' : 'false');
        }
        this.btnVista.classList.toggle('htmlve-premuto', v);
        this.btnVista.setAttribute('aria-pressed', v ? 'true' : 'false');
        if (this.editor) {
            this.editor.resize();
        }
    };

    /* Le maniglie tra i blocchi: trascinandole cambia la larghezza della traccia o dell'anteprima. */
    SitoUi.prototype.preparaManiglie = function() {
        var self = this;
        var trascina = function(maniglia, chiave, verso) {
            if (!maniglia) {
                return;
            }
            maniglia.addEventListener('pointerdown', function(e) {
                if (maniglia.classList.contains('htmlve-ferma') || e.button !== 0) {
                    return;
                }
                e.preventDefault();
                var x0 = e.clientX;
                var w0 = self.larghezze[chiave];
                self.radice.classList.add('htmlve-trascina');
                var muovi = function(ev) {
                    self.disposizione[chiave] = Math.max(120, w0 + verso * (ev.clientX - x0));
                    self.disponi();
                };
                var lascia = function() {
                    document.removeEventListener('pointermove', muovi);
                    document.removeEventListener('pointerup', lascia);
                    self.radice.classList.remove('htmlve-trascina');
                    self.disposizione[chiave] = self.larghezze[chiave]; // Quella davvero usata, dentro i limiti.
                    self.salvaDisposizione();
                };
                document.addEventListener('pointermove', muovi);
                document.addEventListener('pointerup', lascia);
            });
        };
        trascina(this.m1, 'lt', 1);
        trascina(this.m2, 'lv', -1);
    };

    SitoUi.prototype.creaEditor = function() {
        var self = this;
        var completamento = this.aiuti.completamento;
        if (completamento) {
            try {
                window.ace.require('ace/ext/language_tools'); // Lo carica CodeRunner insieme ad Ace.
            } catch (e) {
                completamento = false;
            }
        }
        var ed = this.editor = window.ace.edit(this.ospiteAce);
        ed.setOptions({
            fontSize: '14px',
            showPrintMargin: false,
            tabSize: 2,
            useSoftTabs: true,
            behavioursEnabled: this.aiuti.chiusura, // Chiusura automatica di tag, virgolette e parentesi.
            enableBasicAutocompletion: completamento,
            enableLiveAutocompletion: completamento,
            readOnly: this.solaLettura
        });
        ed.$blockScrolling = Infinity;
        ed.commands.addCommand({
            name: 'apriNelBrowser',
            bindKey: {win: 'Ctrl-Enter', mac: 'Command-Enter'},
            exec: function() {
                self.apriNelBrowser();
            }
        });
        ed.on('change', function() {
            if (!self.aperto || self.solaLettura || self.cambioSessione) {
                return;
            }
            self.files[self.aperto] = ed.getValue();
            self.programmaSalvataggio();
            self.programmaAnteprima();
        });
        ed.on('blur', function() {
            self.salvaSubito();
        });
    };

    SitoUi.prototype.sessione = function(percorso) {
        if (!this.sessioni[percorso]) {
            var s = window.ace.createEditSession(this.files[percorso] || '');
            s.setUseWorker(this.aiuti.errori); // Segnalazione degli errori nel margine.
            s.setMode(modoAce(percorso));
            s.setTabSize(2);
            s.setUseSoftTabs(true);
            this.sessioni[percorso] = s;
        }
        return this.sessioni[percorso];
    };

    /* ---------- albero dei file ---------- */

    SitoUi.prototype.disegnaAlbero = function() {
        var self = this;
        var cartelle = this.tutteLeCartelle();
        var files = Object.keys(this.files).concat(Object.keys(this.immagini));
        this.albero.textContent = '';

        var voce = function(percorso, cartella, livello) {
            var v = el('div', 'htmlve-voce' + (cartella ? ' htmlve-dir' : ' htmlve-file'));
            v.style.paddingLeft = (6 + livello * 14) + 'px';
            var icona = cartella ? '📁' : self.immagini[percorso] !== undefined ? '🖼️' :
                (eHtml(percorso) ? '📄' : estensione(percorso) === 'css' ? '🎨' : '📃');
            v.appendChild(el('span', 'htmlve-icona', icona));
            v.appendChild(el('span', 'htmlve-nome', percorso === '' ? 'sito' : nomeDi(percorso)));
            if (percorso === self.selezione && cartella === self.selezioneCartella) {
                v.classList.add('selezionata');
            }
            if (!cartella && (percorso === self.aperto || (!self.aperto && percorso === self.selezione))) {
                v.classList.add('aperta');
            }
            if (!self.solaLettura && percorso !== '') {
                v.draggable = true;
                v.addEventListener('dragstart', function(e) {
                    self.trascinato = {percorso: percorso, cartella: cartella};
                    e.dataTransfer.effectAllowed = 'move';
                    e.dataTransfer.setData('text/plain', percorso);
                });
                v.addEventListener('dragend', function() {
                    self.trascinato = null;
                });
            }
            if (!self.solaLettura && cartella) {
                v.addEventListener('dragover', function(e) {
                    if (self.trascinato) {
                        e.preventDefault();
                        e.dataTransfer.dropEffect = 'move';
                        v.classList.add('htmlve-sopra');
                    }
                });
                v.addEventListener('dragleave', function() {
                    v.classList.remove('htmlve-sopra');
                });
                v.addEventListener('drop', function(e) {
                    v.classList.remove('htmlve-sopra');
                    if (!self.trascinato) {
                        return;
                    }
                    e.preventDefault();
                    var t = self.trascinato;
                    self.trascinato = null;
                    self.spostaIn(t.percorso, t.cartella, percorso);
                });
            }
            v.addEventListener('click', function() {
                if (cartella) {
                    self.selezione = percorso;
                    self.selezioneCartella = true;
                    self.disegnaAlbero();
                } else {
                    self.apri(percorso);
                }
            });
            self.albero.appendChild(v);
        };

        var livello = function(dir, n) {
            cartelle.filter(function(c) {
                return cartellaDi(c) === dir;
            }).forEach(function(c) {
                voce(c, true, n);
                livello(c, n + 1);
            });
            files.filter(function(f) {
                return cartellaDi(f) === dir;
            }).sort().forEach(function(f) {
                voce(f, false, n);
            });
        };

        voce('', true, 0);
        livello('', 1);
        if (!files.length && !cartelle.length) {
            this.albero.appendChild(el('div', 'htmlve-suggerimento', this.solaLettura ? 'Nessun file.' :
                'La cartella del sito è vuota. Crea i file e le cartelle con «+ File» e «+ Cartella».'));
        }
        if (this.btnRinomina) {
            var radice = this.selezioneCartella && this.selezione === '';
            this.btnRinomina.disabled = radice;
            this.btnSposta.disabled = radice;
            this.btnElimina.disabled = radice;
        }
    };

    SitoUi.prototype.cartellaDestinazione = function() {
        return this.selezioneCartella ? this.selezione : cartellaDi(this.selezione);
    };

    SitoUi.prototype.apri = function(percorso, senzaFuoco) {
        if (this.immagini[percorso] !== undefined) {
            this.apriImmagine(percorso);
            return;
        }
        this.vistaImmagine.style.display = 'none';
        this.apertaImmagine = null;
        this.aperto = percorso;
        this.selezione = percorso;
        this.selezioneCartella = false;
        this.cambioSessione = true;
        this.editor.setSession(this.sessione(percorso));
        this.cambioSessione = false;
        this.editor.setReadOnly(this.solaLettura);
        this.vuoto.style.display = 'none';
        this.mostraNomeFile(percorso);
        this.disegnaAlbero();
        if (!this.solaLettura && !senzaFuoco) {
            this.editor.focus();
        }
    };

    /* Un'immagine non si modifica: al posto dell'editor si vede l'immagine. */
    SitoUi.prototype.apriImmagine = function(percorso) {
        this.aperto = null;
        this.selezione = percorso;
        this.selezioneCartella = false;
        this.cambioSessione = true;
        this.editor.setSession(window.ace.createEditSession(''));
        this.cambioSessione = false;
        this.editor.setReadOnly(true);
        this.vuoto.style.display = 'none';
        this.mostraNomeFile(percorso);
        var origine = this.immagini[percorso];
        this.vistaImmagine.textContent = '';
        var img = el('img');
        img.src = this.urlImmagine(percorso);
        img.alt = percorso;
        this.vistaImmagine.appendChild(img);
        this.vistaImmagine.appendChild(el('div', 'htmlve-didascalia', origine.indexOf('data:') === 0 ?
            'Immagine caricata dal computer.' : 'Immagine fornita dalla domanda: ' + origine + '.'));
        this.vistaImmagine.style.display = 'flex';
        this.apertaImmagine = percorso;
        this.disegnaAlbero();
    };

    SitoUi.prototype.mostraVuoto = function() {
        this.vistaImmagine.style.display = 'none';
        this.apertaImmagine = null;
        this.aperto = null;
        this.cambioSessione = true;
        this.editor.setSession(window.ace.createEditSession(''));
        this.cambioSessione = false;
        this.editor.setReadOnly(true);
        this.mostraNomeFile('');
        this.vuoto.textContent = this.solaLettura ? 'Nessun file aperto.' :
            'Seleziona un file nell\'elenco a sinistra, oppure creane uno con «+ File».';
        this.vuoto.style.display = 'block';
    };

    /* ---------- finestrella per nomi e conferme (niente prompt/confirm del browser) ---------- */

    SitoUi.prototype.chiedi = function(messaggio, valore, conInput) {
        var self = this;
        return new Promise(function(fine) {
            var f = self.finestra;
            f.textContent = '';
            var box = el('div', 'htmlve-dialogo');
            box.appendChild(el('div', 'htmlve-msg', messaggio));
            var input = null;
            var errore = el('div', 'htmlve-errore');
            if (conInput) {
                input = el('input', 'htmlve-input');
                input.type = 'text';
                input.value = valore || '';
                input.setAttribute('autocomplete', 'off');
                input.setAttribute('spellcheck', 'false');
                box.appendChild(input);
            }
            box.appendChild(errore);
            var bottoni = el('div', 'htmlve-bottoni');
            var ok = el('button', 'htmlve-btn htmlve-primario', 'OK');
            var no = el('button', 'htmlve-btn', 'Annulla');
            ok.type = 'button';
            no.type = 'button';
            bottoni.appendChild(no);
            bottoni.appendChild(ok);
            box.appendChild(bottoni);
            f.appendChild(box);
            f.classList.add('aperta');
            var chiudi = function(r) {
                f.classList.remove('aperta');
                f.textContent = '';
                fine(r);
            };
            ok.addEventListener('click', function() {
                if (!input) {
                    chiudi(true);
                    return;
                }
                var v = input.value.trim();
                var msg = self.validaNome ? self.validaNome(v) : '';
                if (msg) {
                    errore.textContent = msg;
                    input.focus();
                    return;
                }
                chiudi(v);
            });
            no.addEventListener('click', function() {
                chiudi(null);
            });
            box.addEventListener('keydown', function(e) {
                // Invio non deve inviare il modulo del quiz.
                if (e.key === 'Enter') {
                    e.preventDefault();
                    ok.click();
                }
                if (e.key === 'Escape') {
                    e.preventDefault();
                    e.stopPropagation();
                    chiudi(null);
                }
            });
            setTimeout(function() {
                if (input) {
                    input.focus();
                    var punto = input.value.lastIndexOf('.');
                    input.setSelectionRange(0, punto > 0 ? punto : input.value.length);
                } else {
                    ok.focus();
                }
            }, 0);
        });
    };

    SitoUi.prototype.chiediNome = function(messaggio, valore, cartella, attuale) {
        var self = this;
        this.validaNome = function(v) {
            if (!v) {
                return 'Scrivi un nome.';
            }
            if (!NOME_VALIDO.test(v) || v === '.' || v === '..') {
                return 'Usa solo lettere minuscole, numeri e i segni - _ . (niente spazi, accenti o barre).';
            }
            var p = unisci(cartella, v);
            if (p !== attuale && self.esiste(p)) {
                return 'In questa cartella c\'è già un file o una cartella con questo nome.';
            }
            return '';
        };
        return this.chiedi(messaggio, valore, true).then(function(r) {
            self.validaNome = null;
            return r;
        });
    };

    SitoUi.prototype.nuovoFile = function() {
        var self = this;
        var dir = this.cartellaDestinazione();
        var proposta = this.files[unisci(dir, 'index.html')] === undefined ? 'index.html' : '';
        this.chiediNome('Nome del nuovo file in «' + (dir || 'sito') + '» (con l\'estensione, es. index.html, stile.css):',
                proposta, dir).then(function(nome) {
            if (!nome) {
                return;
            }
            var p = unisci(dir, nome);
            self.files[p] = '';
            self.apri(p);
            self.programmaSalvataggio();
        });
    };

    SitoUi.prototype.nuovaCartella = function() {
        var self = this;
        var dir = this.cartellaDestinazione();
        this.chiediNome('Nome della nuova cartella in «' + (dir || 'sito') + '»:', '', dir).then(function(nome) {
            if (!nome) {
                return;
            }
            var p = unisci(dir, nome);
            self.cartelle.push(p);
            self.selezione = p;
            self.selezioneCartella = true;
            self.disegnaAlbero();
            self.programmaSalvataggio();
        });
    };

    SitoUi.prototype.rinomina = function() {
        var self = this;
        var vecchio = this.selezione;
        var cartella = this.selezioneCartella;
        if (vecchio === '' && cartella) {
            return;
        }
        var dir = cartellaDi(vecchio);
        this.chiediNome('Nuovo nome per «' + nomeDi(vecchio) + '»:', nomeDi(vecchio), dir, vecchio).then(function(nome) {
            if (!nome || nome === nomeDi(vecchio)) {
                return;
            }
            self.cambiaPercorso(vecchio, unisci(dir, nome), cartella);
        });
    };

    /* Cambia il percorso di un file o di una cartella (con tutto quello che contiene): serve a Rinomina e a Sposta.
       I link nelle pagine non cambiano, come quando si spostano i file sul computer. */
    SitoUi.prototype.cambiaPercorso = function(vecchio, nuovo, cartella) {
        var self = this;
        var sposta = function(p) {
            if (p === vecchio) {
                return nuovo;
            }
            if (cartella && p.indexOf(vecchio + '/') === 0) {
                return nuovo + p.slice(vecchio.length);
            }
            return p;
        };
        var files = {}, sessioni = {}, immagini = {};
        Object.keys(this.files).forEach(function(p) {
            files[sposta(p)] = self.files[p];
        });
        Object.keys(this.immagini).forEach(function(p) {
            immagini[sposta(p)] = self.immagini[p];
        });
        Object.keys(this.sessioni).forEach(function(p) {
            var q = sposta(p);
            sessioni[q] = self.sessioni[p];
            if (q !== p) {
                sessioni[q].setMode(modoAce(q)); // L'estensione può essere cambiata.
            }
        });
        this.files = files;
        this.immagini = immagini;
        this.sessioni = sessioni;
        this.cartelle = this.cartelle.map(sposta);
        if (this.aperto) {
            this.aperto = sposta(this.aperto);
        }
        if (this.apertaImmagine) {
            this.apertaImmagine = sposta(this.apertaImmagine);
        }
        if (this.pagina) {
            this.pagina = sposta(this.pagina);
        }
        this.selezione = nuovo;
        this.selezioneCartella = cartella;
        if (!cartella && this.immagini[nuovo] !== undefined) {
            this.apriImmagine(nuovo);
        } else if (!cartella && this.aperto === nuovo) {
            this.apri(nuovo);
        } else {
            if (this.aperto) {
                this.mostraNomeFile(this.aperto);
            } else if (this.apertaImmagine) {
                this.mostraNomeFile(this.apertaImmagine);
            }
            this.disegnaAlbero();
        }
        this.aggiornaAnteprima();
        this.programmaSalvataggio();
    };

    /* Perché non si può spostare qui (stringa vuota se si può). */
    SitoUi.prototype.motivoNoSposta = function(vecchio, cartella, dest) {
        if (dest === cartellaDi(vecchio)) {
            return 'È già in questa cartella.';
        }
        if (cartella && (dest === vecchio || dest.indexOf(vecchio + '/') === 0)) {
            return 'Una cartella non si può spostare dentro sé stessa.';
        }
        if (this.esiste(unisci(dest, nomeDi(vecchio)))) {
            return 'In «' + (dest || 'sito') + '» c\'è già un file o una cartella che si chiama «' + nomeDi(vecchio) + '».';
        }
        return '';
    };

    SitoUi.prototype.spostaIn = function(vecchio, cartella, dest) {
        var motivo = this.motivoNoSposta(vecchio, cartella, dest);
        if (motivo) {
            if (dest !== cartellaDi(vecchio)) {
                this.avvisa(motivo);
            }
            return;
        }
        this.cambiaPercorso(vecchio, unisci(dest, nomeDi(vecchio)), cartella);
    };

    /* Finestrella con un solo messaggio e il pulsante OK. */
    SitoUi.prototype.avvisa = function(messaggio) {
        var f = this.finestra;
        f.textContent = '';
        var box = el('div', 'htmlve-dialogo');
        box.appendChild(el('div', 'htmlve-msg', messaggio));
        var bottoni = el('div', 'htmlve-bottoni');
        var ok = el('button', 'htmlve-btn htmlve-primario', 'OK');
        ok.type = 'button';
        var chiudi = function() {
            f.classList.remove('aperta');
            f.textContent = '';
        };
        ok.addEventListener('click', chiudi);
        box.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === 'Escape') {
                e.preventDefault();
                e.stopPropagation();
                chiudi();
            }
        });
        bottoni.appendChild(ok);
        box.appendChild(bottoni);
        f.appendChild(box);
        f.classList.add('aperta');
        setTimeout(function() {
            ok.focus();
        }, 0);
    };

    /* Pulsante «Sposta»: si sceglie la cartella di destinazione da un elenco. */
    SitoUi.prototype.sposta = function() {
        var self = this;
        var vecchio = this.selezione;
        var cartella = this.selezioneCartella;
        if (vecchio === '' && cartella) {
            return;
        }
        var f = this.finestra;
        f.textContent = '';
        var box = el('div', 'htmlve-dialogo');
        box.appendChild(el('div', 'htmlve-msg', 'In quale cartella vuoi spostare «' + nomeDi(vecchio) + '»?'));
        var elenco = el('div', 'htmlve-destinazioni');
        var chiudi = function() {
            f.classList.remove('aperta');
            f.textContent = '';
        };
        [''].concat(this.tutteLeCartelle()).forEach(function(dest) {
            var livello = dest === '' ? 0 : dest.split('/').length;
            var b = el('button', 'htmlve-destinazione');
            b.type = 'button';
            b.style.paddingLeft = (8 + livello * 16) + 'px';
            b.appendChild(el('span', 'htmlve-icona', '📁'));
            b.appendChild(el('span', '', dest === '' ? 'sito' : nomeDi(dest)));
            var motivo = self.motivoNoSposta(vecchio, cartella, dest);
            if (motivo) {
                b.disabled = true;
                b.title = motivo;
            }
            b.addEventListener('click', function() {
                chiudi();
                self.spostaIn(vecchio, cartella, dest);
            });
            elenco.appendChild(b);
        });
        box.appendChild(elenco);
        var bottoni = el('div', 'htmlve-bottoni');
        var no = el('button', 'htmlve-btn', 'Annulla');
        no.type = 'button';
        no.addEventListener('click', chiudi);
        bottoni.appendChild(no);
        box.appendChild(bottoni);
        box.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                e.preventDefault();
                e.stopPropagation();
                chiudi();
            }
        });
        f.appendChild(box);
        f.classList.add('aperta');
        setTimeout(function() {
            no.focus();
        }, 0);
    };

    SitoUi.prototype.elimina = function() {
        var self = this;
        var p = this.selezione;
        var cartella = this.selezioneCartella;
        if (p === '' && cartella) {
            return;
        }
        var contenuti = cartella ? Object.keys(this.files).concat(Object.keys(this.immagini)).filter(function(f) {
            return f.indexOf(p + '/') === 0;
        }).length : 0;
        var msg = cartella ?
            'Eliminare la cartella «' + p + '»' + (contenuti ? ' e i ' + contenuti + ' file che contiene' : '') +
                '? L\'operazione non si può annullare.' :
            'Eliminare il file «' + p + '»? L\'operazione non si può annullare.';
        this.chiedi(msg, '', false).then(function(ok) {
            if (!ok) {
                return;
            }
            var dentro = function(x) {
                return x === p || (cartella && x.indexOf(p + '/') === 0);
            };
            Object.keys(self.files).forEach(function(f) {
                if (dentro(f)) {
                    delete self.files[f];
                    delete self.sessioni[f];
                }
            });
            Object.keys(self.immagini).forEach(function(f) {
                if (dentro(f)) {
                    delete self.immagini[f];
                }
            });
            self.cartelle = self.cartelle.filter(function(c) {
                return !dentro(c);
            });
            self.selezione = cartellaDi(p);
            self.selezioneCartella = true;
            if ((self.aperto && dentro(self.aperto)) || (!self.aperto && dentro(p))) {
                self.mostraVuoto();
            }
            if (self.pagina && dentro(self.pagina)) {
                self.pagina = null;
            }
            self.disegnaAlbero();
            self.aggiornaAnteprima();
            self.programmaSalvataggio();
        });
    };

    /* ---------- copia e incolla del sito tra le domande ---------- */

    /* Gli appunti stanno nel browser e valgono solo nello stesso tentativo: il sito di uno studente
       non si incolla nel tentativo di un altro, anche sullo stesso computer. */
    var CHIAVE_APPUNTI = 'html_sito:appunti:' + location.host;

    SitoUi.prototype.tentativo = function() {
        var m = /[?&]attempt=(\d+)/.exec(location.search);
        return m ? m[1] : 'senza-tentativo';
    };

    SitoUi.prototype.copiaSito = function() {
        var self = this;
        var n = Object.keys(this.files).length + Object.keys(this.immagini).length;
        if (!n) {
            this.avvisa('Il sito è vuoto: non c\'è niente da copiare.');
            return;
        }
        var files = {}, immagini = {};
        Object.keys(this.files).forEach(function(k) {
            files[k] = self.sessioni[k] ? self.sessioni[k].getValue() : self.files[k];
        });
        Object.keys(this.immagini).forEach(function(k) {
            immagini[k] = self.immagini[k];
        });
        try {
            window.localStorage.setItem(CHIAVE_APPUNTI, JSON.stringify({
                tentativo: this.tentativo(),
                quando: new Date().toISOString(),
                cartelle: this.tutteLeCartelle(),
                files: files,
                immagini: immagini
            }));
        } catch (e) {
            this.avvisa('Non riesco a copiare il sito: il browser non lascia salvare gli appunti.');
            return;
        }
        var nf = Object.keys(this.files).length, ni = Object.keys(this.immagini).length;
        this.avvisa('Sito copiato: ' + nf + ' file' + (ni ? ' e ' + ni + (ni === 1 ? ' immagine' : ' immagini') : '') +
            '. Nella domanda in cui volete ripartire da qui premete «Incolla sito».');
    };

    SitoUi.prototype.incollaSito = function() {
        var self = this;
        var appunti = null;
        try {
            appunti = JSON.parse(window.localStorage.getItem(CHIAVE_APPUNTI) || 'null');
        } catch (e) {
            appunti = null;
        }
        if (!appunti || appunti.tentativo !== this.tentativo() || typeof appunti.files !== 'object') {
            this.avvisa('Non c\'è nessun sito da incollare: prima, nella domanda da cui volete ripartire, ' +
                'premete «Copia sito».');
            return;
        }
        var n = Object.keys(appunti.files).length;
        var pieno = Object.keys(this.files).length + Object.keys(this.immagini).length > 0;
        var conferma = pieno ? this.chiedi('Incollare il sito copiato (' + n + ' file)? Prende il posto di tutto ' +
            'quello che c\'è ora in questo editor, e non si può annullare.', '', false) : Promise.resolve(true);
        conferma.then(function(ok) {
            if (!ok) {
                return;
            }
            self.files = {};
            Object.keys(appunti.files).forEach(function(k) {
                if (typeof appunti.files[k] === 'string') {
                    self.files[k] = appunti.files[k];
                }
            });
            self.immagini = {};
            Object.keys(appunti.immagini || {}).forEach(function(k) {
                if (typeof appunti.immagini[k] === 'string') {
                    self.immagini[k] = appunti.immagini[k];
                }
            });
            self.cartelle = Array.isArray(appunti.cartelle) ? appunti.cartelle.filter(function(c) {
                return typeof c === 'string';
            }) : [];
            self.sessioni = {};
            self.selezione = '';
            self.selezioneCartella = true;
            self.pagina = null;
            self.storia = [];
            self.disegnaAlbero();
            var prima = self.files['index.html'] !== undefined ? 'index.html' : Object.keys(self.files).sort()[0];
            if (prima) {
                self.apri(prima, true);
            } else {
                self.mostraVuoto();
            }
            self.aggiornaAnteprima();
            self.programmaSalvataggio();
        });
    };

    /* ---------- file del computer: scaricare il sito in .zip, importare file e .zip ---------- */

    var TABELLA_CRC = (function() {
        var t = [];
        for (var n = 0; n < 256; n++) {
            var c = n;
            for (var k = 0; k < 8; k++) {
                c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
            }
            t[n] = c >>> 0;
        }
        return t;
    })();

    function crc32(b) {
        var c = 0xFFFFFFFF;
        for (var i = 0; i < b.length; i++) {
            c = TABELLA_CRC[(c ^ b[i]) & 0xFF] ^ (c >>> 8);
        }
        return (c ^ 0xFFFFFFFF) >>> 0;
    }

    /* Uno .zip senza compressione (metodo «store»): voci = [{nome, dati: Uint8Array o null per una cartella}]. */
    function creaZip(voci) {
        var enc = new TextEncoder();
        var d = new Date();
        var ora = (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1);
        var giorno = ((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
        var parti = [], centrale = [], pos = 0;
        var intestazione = function(firma, lunghezza) {
            var b = new DataView(new ArrayBuffer(lunghezza));
            b.setUint32(0, firma, true);
            return b;
        };
        voci.forEach(function(v) {
            var nome = enc.encode(v.nome);
            var dati = v.dati || new Uint8Array(0);
            var crc = crc32(dati);
            var l = intestazione(0x04034b50, 30);
            l.setUint16(4, 20, true);
            l.setUint16(6, 0x0800, true); // nomi in UTF-8
            l.setUint16(8, 0, true);
            l.setUint16(10, ora, true);
            l.setUint16(12, giorno, true);
            l.setUint32(14, crc, true);
            l.setUint32(18, dati.length, true);
            l.setUint32(22, dati.length, true);
            l.setUint16(26, nome.length, true);
            l.setUint16(28, 0, true);
            var c = intestazione(0x02014b50, 46);
            c.setUint16(4, 20, true);
            c.setUint16(6, 20, true);
            c.setUint16(8, 0x0800, true);
            c.setUint16(10, 0, true);
            c.setUint16(12, ora, true);
            c.setUint16(14, giorno, true);
            c.setUint32(16, crc, true);
            c.setUint32(20, dati.length, true);
            c.setUint32(24, dati.length, true);
            c.setUint16(28, nome.length, true);
            c.setUint32(38, v.dati ? 0 : 0x10, true); // attributo «cartella»
            c.setUint32(42, pos, true);
            parti.push(l.buffer, nome, dati);
            centrale.push(c.buffer, nome);
            pos += 30 + nome.length + dati.length;
        });
        var dim = centrale.reduce(function(a, x) {
            return a + x.byteLength;
        }, 0);
        var fine = intestazione(0x06054b50, 22);
        fine.setUint16(8, voci.length, true);
        fine.setUint16(10, voci.length, true);
        fine.setUint32(12, dim, true);
        fine.setUint32(16, pos, true);
        return new Blob(parti.concat(centrale, [fine.buffer]), {type: 'application/zip'});
    }

    /* Le voci di uno .zip: [{nome, dati: Uint8Array}] (solo i file). Metodi «store» e «deflate». */
    function leggiZip(buffer) {
        var v = new DataView(buffer);
        var u8 = new Uint8Array(buffer);
        var fine = -1;
        for (var i = buffer.byteLength - 22; i >= Math.max(0, buffer.byteLength - 65557); i--) {
            if (v.getUint32(i, true) === 0x06054b50) {
                fine = i;
                break;
            }
        }
        if (fine < 0) {
            return Promise.reject(new Error('non è un file .zip valido'));
        }
        var n = v.getUint16(fine + 10, true);
        var p = v.getUint32(fine + 16, true);
        var dec = new TextDecoder('utf-8');
        var lavori = [];
        for (var k = 0; k < n; k++) {
            if (v.getUint32(p, true) !== 0x02014b50) {
                return Promise.reject(new Error('il file .zip è rovinato'));
            }
            var metodo = v.getUint16(p + 10, true);
            var compresso = v.getUint32(p + 20, true);
            var lnome = v.getUint16(p + 28, true), lextra = v.getUint16(p + 30, true), lcomm = v.getUint16(p + 32, true);
            var locale = v.getUint32(p + 42, true);
            var nome = dec.decode(u8.subarray(p + 46, p + 46 + lnome));
            p += 46 + lnome + lextra + lcomm;
            if (/\/$/.test(nome)) {
                continue;
            }
            var inizio = locale + 30 + v.getUint16(locale + 26, true) + v.getUint16(locale + 28, true);
            var dati = u8.slice(inizio, inizio + compresso);
            lavori.push((function(nome, metodo, dati) {
                if (metodo === 0) {
                    return Promise.resolve({nome: nome, dati: dati});
                }
                if (metodo !== 8 || !window.DecompressionStream) {
                    return Promise.resolve({nome: nome, dati: null});
                }
                var flusso = new Blob([dati]).stream().pipeThrough(new window.DecompressionStream('deflate-raw'));
                return new Response(flusso).arrayBuffer().then(function(b) {
                    return {nome: nome, dati: new Uint8Array(b)};
                });
            })(nome, metodo, dati));
        }
        return Promise.all(lavori);
    }

    var ESTENSIONI_TESTO = ['html', 'htm', 'css', 'js', 'php', 'txt', 'json', 'md', 'xml', 'csv'];

    function tipoMime(p) {
        var e = estensione(p);
        return {png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', svg: 'image/svg+xml',
            webp: 'image/webp', ico: 'image/x-icon', bmp: 'image/bmp'}[e] || 'application/octet-stream';
    }

    function inDataUrl(byte, mime) {
        var s = '';
        for (var i = 0; i < byte.length; i += 0x8000) {
            s += String.fromCharCode.apply(null, byte.subarray(i, i + 0x8000));
        }
        return 'data:' + mime + ';base64,' + window.btoa(s);
    }

    SitoUi.prototype.scaricaZip = function() {
        var self = this;
        var enc = new TextEncoder();
        var voci = this.tutteLeCartelle().map(function(c) {
            return {nome: 'sito/' + c + '/', dati: null};
        });
        Object.keys(this.files).sort().forEach(function(p) {
            var testo = self.sessioni[p] ? self.sessioni[p].getValue() : self.files[p];
            voci.push({nome: 'sito/' + p, dati: enc.encode(testo)});
        });
        var immagini = Object.keys(this.immagini).sort();
        Promise.all(immagini.map(function(p) {
            var url = self.urlImmagine(p);
            return fetch(url).then(function(r) {
                return r.arrayBuffer();
            }).then(function(b) {
                return {nome: 'sito/' + p, dati: new Uint8Array(b)};
            }).catch(function() {
                return null;
            });
        })).then(function(img) {
            img.forEach(function(x) {
                if (x) {
                    voci.push(x);
                }
            });
            if (voci.length === 0) {
                self.avvisa('Il sito è vuoto: non c\'è niente da scaricare.');
                return;
            }
            var a = document.createElement('a');
            a.href = URL.createObjectURL(creaZip(voci));
            a.download = 'sito.zip';
            document.body.appendChild(a);
            a.click();
            setTimeout(function() {
                URL.revokeObjectURL(a.href);
                a.remove();
            }, 1000);
        });
    };

    SitoUi.prototype.scegliFileDaImportare = function() {
        var self = this;
        var input = el('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = '.zip,.html,.htm,.css,.js,.php,.txt,image/*';
        input.style.display = 'none';
        input.addEventListener('change', function() {
            var scelti = Array.prototype.slice.call(input.files || []);
            input.remove();
            if (scelti.length) {
                self.importa(scelti);
            }
        });
        this.radice.appendChild(input);
        input.click();
    };

    /* Aggiunge al sito, nella cartella selezionata, i file scelti sul computer (anche dentro uno .zip). */
    SitoUi.prototype.importa = function(scelti) {
        var self = this;
        var dir = this.cartellaDestinazione();
        var saltati = [];
        Promise.all(scelti.map(function(file) {
            return file.arrayBuffer().then(function(b) {
                if (estensione(file.name) !== 'zip') {
                    return [{nome: file.name, dati: new Uint8Array(b)}];
                }
                return leggiZip(b).then(function(voci) {
                    voci = voci.filter(function(x) {
                        var parti = x.nome.split('/');
                        return parti[0] !== '__MACOSX' && !parti.some(function(s) {
                            return s.charAt(0) === '.';
                        }) && !/(^|\/)(thumbs\.db|desktop\.ini)$/i.test(x.nome);
                    });
                    // Se tutto sta in una sola cartella (la cartella compressa), si toglie quella.
                    var prima = voci.length && voci[0].nome.indexOf('/') > 0 ? voci[0].nome.split('/')[0] + '/' : '';
                    if (prima && voci.every(function(x) {
                        return x.nome.indexOf(prima) === 0;
                    })) {
                        voci.forEach(function(x) {
                            x.nome = x.nome.slice(prima.length);
                        });
                    }
                    return voci;
                }).catch(function(e) {
                    saltati.push(file.name + ' (' + e.message + ')');
                    return [];
                });
            });
        })).then(function(gruppi) {
            var nuovi = [], rinominati = [];
            [].concat.apply([], gruppi).forEach(function(x) {
                var pulito = x.nome.split('/').map(nomePulito).filter(function(s) {
                    return s !== '' && s !== '.' && s !== '..';
                }).join('/');
                var p = unisci(dir, pulito);
                var e = estensione(p);
                if (!pulito || !x.dati) {
                    saltati.push(x.nome);
                } else if (ESTENSIONI_TESTO.indexOf(e) >= 0) {
                    nuovi.push({p: p, testo: new TextDecoder('utf-8').decode(x.dati)});
                } else if (eImmagine(p)) {
                    if (x.dati.length > MAX_IMMAGINE) {
                        saltati.push(x.nome + ' (immagine oltre ' + Math.round(MAX_IMMAGINE / 1024) + ' KB)');
                        return;
                    }
                    nuovi.push({p: p, immagine: inDataUrl(x.dati, tipoMime(p))});
                } else {
                    saltati.push(x.nome);
                    return;
                }
                if (pulito !== x.nome) {
                    rinominati.push(x.nome + ' → ' + pulito);
                }
            });
            var doppi = nuovi.filter(function(x) {
                return self.files[x.p] !== undefined || self.immagini[x.p] !== undefined;
            });
            var conferma = doppi.length ? self.chiedi('Questi file ci sono già: ' + doppi.map(function(x) {
                return x.p;
            }).join(', ') + '. Sostituirli con quelli importati? (Annulla: si importano solo i file nuovi.)', '', false) :
                Promise.resolve(true);
            return conferma.then(function(sostituisci) {
                var fatti = 0;
                nuovi.forEach(function(x) {
                    var c = self.files[x.p] !== undefined || self.immagini[x.p] !== undefined;
                    if (c && !sostituisci) {
                        return;
                    }
                    delete self.files[x.p];
                    delete self.immagini[x.p];
                    delete self.sessioni[x.p];
                    if (x.immagine) {
                        self.immagini[x.p] = x.immagine;
                    } else {
                        self.files[x.p] = x.testo;
                    }
                    fatti++;
                });
                if (fatti) {
                    if (self.aperto && self.files[self.aperto] !== undefined) {
                        self.apri(self.aperto, true);
                    }
                    self.disegnaAlbero();
                    self.aggiornaAnteprima();
                    self.programmaSalvataggio();
                }
                var msg = 'Importati ' + fatti + ' file in «' + (dir || 'sito') + '».';
                if (rinominati.length) {
                    msg += ' Nomi sistemati (minuscole, senza spazi né accenti): ' + rinominati.join(', ') +
                        '. Se le pagine usavano i nomi vecchi, correggete i link.';
                }
                if (saltati.length) {
                    msg += ' Non importati: ' + saltati.join(', ') + '.';
                }
                self.avvisa(msg);
            });
        });
    };

    /* ---------- salvataggio ---------- */

    SitoUi.prototype.serializza = function() {
        var self = this;
        var files = {}, immagini = {};
        Object.keys(this.files).sort().forEach(function(k) {
            files[k] = self.files[k];
        });
        Object.keys(this.immagini).sort().forEach(function(k) {
            immagini[k] = self.immagini[k];
        });
        this.salvatoIl = new Date().toISOString();
        return JSON.stringify({
            htmlve: 1,
            versione: VERSIONE,
            salvato: this.salvatoIl,
            cartelle: this.tutteLeCartelle(),
            files: files,
            immagini: immagini
        });
    };

    SitoUi.prototype.programmaSalvataggio = function() {
        var self = this;
        if (this.solaLettura) {
            return;
        }
        clearTimeout(this.timerSalva);
        this.daSalvare = true;
        this.timerSalva = setTimeout(function() {
            self.salvaSubito();
        }, 800);
    };

    /* Scrive il sito nella risposta. La chiamano CodeRunner (sync, ogni 2 secondi e all'invio
       della pagina) e l'editor stesso, poco dopo ogni modifica. */
    SitoUi.prototype.salvaSubito = function() {
        if (this.solaLettura || !this.daSalvare) {
            return;
        }
        clearTimeout(this.timerSalva);
        this.daSalvare = false;
        var json = this.serializza();
        this.textarea.value = json;
        this.avvisaMoodle();
        var chiave = this.chiaveCopia();
        if (chiave) {
            try {
                window.localStorage.setItem(chiave, json);
            } catch (e) {
                // Pieno o non disponibile: la risposta resta comunque nella textarea.
            }
        }
        this.recuperato = false;
        this.aggiornaStato();
    };

    /* Il salvataggio automatico del quiz parte quando nel modulo cambia un campo: si avvisa
       con un evento "change" sulla textarea e sul campo nascosto «sequencecheck» della domanda. */
    SitoUi.prototype.avvisaMoodle = function() {
        var ta = this.textarea;
        ['input', 'change'].forEach(function(t) {
            ta.dispatchEvent(new Event(t, {bubbles: true}));
        });
        var input = this.que && this.que.querySelector('input[name$=":sequencecheck"]');
        if (input) {
            input.dispatchEvent(new Event('change', {bubbles: true}));
        }
    };

    SitoUi.prototype.aggiornaStato = function() {
        var t;
        if (this.solaLettura) {
            t = this.salvatoIl ? 'Sola lettura · ultima modifica ' + dataOra(this.salvatoIl) : 'Sola lettura';
        } else if (this.recuperato) {
            t = 'Lavoro recuperato dalla copia nel browser';
        } else if (this.salvatoIl) {
            t = 'Registrato nella risposta alle ' + ora(new Date(this.salvatoIl));
        } else {
            t = 'Nessuna modifica';
        }
        this.stato.textContent = t;
    };

    /* ---------- anteprima ---------- */

    SitoUi.prototype.programmaAnteprima = function() {
        var self = this;
        clearTimeout(this.timerAnteprima);
        this.timerAnteprima = setTimeout(function() {
            self.aggiornaAnteprima();
        }, 500);
    };

    SitoUi.prototype.paginaPredefinita = function() {
        this.richiesta = null;
        if (this.files['index.html'] !== undefined) {
            return 'index.html';
        }
        if (this.files['index.php'] !== undefined) {
            return 'index.php';
        }
        return Object.keys(this.files).filter(eHtml).sort()[0] || Object.keys(this.files).filter(ePhp).sort()[0] || null;
    };

    SitoUi.prototype.mostraNomeFile = function(testo) {
        this.nomeFile.textContent = testo;
        var pagina = !!this.aperto && (eHtml(this.aperto) || ePhp(this.aperto));
        this.btnApri.disabled = !pagina;
        this.btnApri.title = pagina ? 'Apre questa pagina nell\'anteprima del browser (Ctrl+Invio)' +
            (ePhp(this.aperto) ? ': la pagina PHP viene eseguita' : '') :
            'Si apre nel browser una pagina .html o .php: apri la pagina che usa questo file';
    };

    SitoUi.prototype.mostraIndirizzo = function(testo) {
        this.indirizzoMostrato = testo;
        if (document.activeElement !== this.campoIndirizzo) {
            this.campoIndirizzo.value = testo;
        }
    };

    /* «Apri nel browser»: la pagina aperta nell'editor va nell'anteprima (una pagina PHP si esegue). */
    SitoUi.prototype.apriNelBrowser = function() {
        if (!this.aperto || !(eHtml(this.aperto) || ePhp(this.aperto))) {
            return;
        }
        if (this.disposizione && !this.disposizione.vista) {
            this.mostraPannello('vista', true);
        }
        if (this.pagina) {
            this.storia.push(this.pagina);
        }
        this.pagina = this.aperto;
        this.richiesta = null;
        this.forzaPhp = true;
        this.aggiornaAnteprima();
    };

    /* L'indirizzo scritto nella barra: dalla cartella del sito, con o senza / all'inizio, anche con ?dati. */
    SitoUi.prototype.vaiIndirizzo = function(testo) {
        var t = String(testo || '').trim().replace(/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?/i, '');
        this.campoIndirizzo.blur();
        if (!t) {
            this.mostraIndirizzo(this.indirizzoMostrato || '');
            return;
        }
        this.forzaPhp = true;
        this.vai(ESTERNO.test(t) ? t : (t.charAt(0) === '/' ? t : '/' + t));
    };

    SitoUi.prototype.aggiornaAnteprima = function() {
        if (!this.pagina || (this.files[this.pagina] === undefined && !this.paginaNonTrovata) || this.immagini[this.pagina] !== undefined) {
            this.pagina = this.paginaPredefinita();
        }
        var html;
        if (!this.pagina) {
            html = paginaMessaggio('Nessuna pagina da visualizzare', 'Crea una pagina HTML (per esempio index.html) per vederla qui.');
            this.mostraIndirizzo('');
        } else if (this.files[this.pagina] === undefined) {
            html = paginaNonTrovata('/' + this.pagina);
            this.mostraIndirizzo('/' + this.pagina);
        } else if (ePhp(this.pagina) && this.anteprimaPhp) {
            this.mostraIndirizzo('/' + this.pagina + this.coda());
            html = this.anteprimaDiPhp();
        } else if (ePhp(this.pagina)) {
            html = paginaPhp(this.pagina, this.richiesta);
            this.mostraIndirizzo('/' + this.pagina + this.coda());
        } else {
            html = this.costruisciPagina(this.pagina);
            this.mostraIndirizzo('/' + this.pagina + this.coda());
        }
        this.btnIndietro.disabled = !this.storia.length;
        this.aggiornaScheda();
        this.avviso.style.display = 'none';
        if (this.richiesta && this.richiesta.metodo === 'post' && !ePhp(this.pagina || '')) {
            this.avviso.textContent = 'La pagina ha ricevuto con POST: ' + this.richiesta.dati.map(function(d) {
                return d[0] + '=' + d[1];
            }).join(', ') + ' (una pagina HTML non li legge: servirebbe una pagina PHP).';
            this.avviso.style.display = 'block';
        }
        if (this.avvisoPhp) {
            this.avviso.textContent = this.avvisoPhp;
            this.avviso.style.display = 'block';
            this.avvisoPhp = '';
        }
        this.forzaPhp = false;
        // L'iframe è isolato: a ogni aggiornamento l'anteprima riparte dall'inizio della pagina.
        this.iframe.srcdoc = html;
    };

    /* ---------- anteprima delle pagine PHP (anteprima_php) ---------- */

    /* Una firma del sito: se cambia, la pagina PHP mostrata non corrisponde più al codice. */
    function firma(oggetto) {
        var t = JSON.stringify(oggetto), h = 0;
        for (var i = 0; i < t.length; i++) {
            h = (h * 31 + t.charCodeAt(i)) | 0;
        }
        return t.length + ':' + h;
    }

    /* L'HTML da mostrare per la pagina PHP aperta: l'ultima esecuzione se vale ancora, altrimenti la richiesta a
       Jobe (intanto un messaggio). Cambiare pagina o dati esegue di nuovo; cambiare solo il codice no, per non
       mandare una richiesta a ogni tasto: lo dice l'avviso, e ⟳ riesegue. */
    SitoUi.prototype.anteprimaDiPhp = function() {
        var chiave = this.pagina + ' ' + JSON.stringify(this.richiesta || null);
        var f = firma(this.files);
        var u = this.uscitaPhp;
        if (u && u.chiave === chiave && !this.forzaPhp) {
            if (u.firma !== f) {
                this.avvisoPhp = 'Hai modificato il sito: premi ⟳ per eseguire di nuovo la pagina PHP.';
            }
            return u.html;
        }
        this.eseguiPhp(chiave, f);
        return paginaMessaggio('Esecuzione di ' + esc(this.pagina) + '…', 'Il server sta eseguendo la pagina PHP.');
    };

    SitoUi.prototype.eseguiPhp = function(chiave, f) {
        var self = this;
        var numero = ++this.numeroPhp;
        var pagina = this.pagina, richiesta = this.richiesta;
        var testi = {};
        Object.keys(this.files).forEach(function(k) {
            testi[k] = self.files[k];
        });
        var dati = {files: testi, pagina: pagina, metodo: richiesta ? richiesta.metodo : 'get',
            dati: richiesta ? richiesta.dati : [], db: this.dbPhp, stato: this.statoDb};
        var mostra = function(html, titolo) {
            if (numero !== self.numeroPhp || self.pagina !== pagina) {
                return; // Nel frattempo lo studente è andato su un'altra pagina.
            }
            self.uscitaPhp = {chiave: chiave, firma: f, html: html, titolo: titolo};
            self.aggiornaScheda();
            self.iframe.srcdoc = html;
        };
        var errore = function(testo) {
            mostra(paginaErrorePhp(pagina, richiesta, testo), '');
            self.uscitaPhp = null; // Al prossimo aggiornamento si riprova.
        };
        chiamaJobe(dati, function(risultato) {
            if (risultato.errore) {
                errore(risultato.errore);
                return;
            }
            if (self.dbPhp) {
                self.statoDb = risultato.stato || '';
            }
            var uscita = risultato.html || '';
            var titolo = /<title[^>]*>([\s\S]*?)<\/title>/i.exec(uscita);
            mostra(self.costruisciPagina(pagina, uscita), titolo ? titolo[1] : '');
        }, errore);
    };

    /* Manda il programma dell'anteprima a Jobe con il servizio web di CodeRunner (come l'interfaccia scratchpad). */
    function chiamaJobe(dati, fatto, errore) {
        var req = window.require;
        if (typeof req !== 'function' || !window.M || !window.M.cfg) {
            errore('Qui non c\'è il servizio web di CodeRunner. Premi Verifica per eseguire le pagine PHP con i dati delle prove.');
            return;
        }
        req(['core/ajax'], function(ajax) {
            ajax.call([{
                methodname: 'qtype_coderunner_run_in_sandbox',
                args: {
                    contextid: window.M.cfg.contextid,
                    sourcecode: ANTEPRIMA_PHP,
                    language: 'python3',
                    stdin: '',
                    files: JSON.stringify({'richiesta.json': JSON.stringify(dati)}),
                    params: ''
                },
                done: function(testo) {
                    var r;
                    try {
                        r = JSON.parse(testo);
                    } catch (e) {
                        errore('Risposta del server non leggibile.');
                        return;
                    }
                    // Il servizio risponde come la sandbox di CodeRunner: {error, result, output, stderr, cmpinfo}
                    // (error 0 e result 15 = eseguito); per sicurezza si accetta anche la forma di Jobe (outcome, stdout).
                    var esito = r.result !== undefined ? r.result : r.outcome;
                    var uscita = r.output !== undefined ? r.output : r.stdout;
                    if (r.error) {
                        errore('Il server delle prove non risponde (errore ' + r.error + '): riprova tra poco o premi Verifica.');
                        return;
                    }
                    if (esito !== 15) {
                        errore('Il server non ha eseguito la pagina (esito ' + esito + '). ' +
                            String(r.cmpinfo || r.stderr || '').slice(0, 300));
                        return;
                    }
                    try {
                        fatto(JSON.parse(uscita));
                    } catch (e) {
                        errore('Risposta del server non leggibile: ' + String(uscita || r.stderr || '').slice(0, 300));
                    }
                },
                fail: function(e) {
                    var m = (e && (e.message || e.errorcode)) || String(e);
                    if (/disabled|disattivato/i.test(m)) {
                        m = 'Il servizio che esegue il PHP nell\'anteprima non è attivo: lo attiva l\'amministratore ' +
                            'nelle impostazioni di CodeRunner (servizio web della sandbox). Intanto premi Verifica.';
                    } else if (/rate|exceeded|superato/i.test(m)) {
                        m = 'Hai eseguito troppe pagine PHP nell\'ultima ora: aspetta un po\' oppure premi Verifica.';
                    }
                    errore(m);
                }
            }]);
        }, function() {
            errore('Il servizio web di CodeRunner non si è caricato. Premi Verifica per eseguire le pagine PHP con i dati delle prove.');
        });
    }

    SitoUi.prototype.costruisciPagina = function(percorso, sorgenteDato) {
        var self = this;
        var sorgente = sorgenteDato !== undefined ? sorgenteDato : this.files[percorso];
        var conDoctype = /^\s*(<!--[\s\S]*?-->\s*)*<!doctype/i.test(sorgente);
        var doc = new DOMParser().parseFromString(sorgente, 'text/html');
        var dir = cartellaDi(percorso);
        var ogni = function(selettore, fn) {
            Array.prototype.forEach.call(doc.querySelectorAll(selettore), fn);
        };

        ogni('base', function(b) {
            b.remove();
        });
        // Fogli di stile collegati: il contenuto del file .css entra nella pagina.
        ogni('link[href]', function(l) {
            var rel = (l.getAttribute('rel') || '').toLowerCase().split(/\s+/);
            if (rel.indexOf('stylesheet') < 0) {
                return;
            }
            var href = l.getAttribute('href');
            var p = ESTERNO.test(href) ? null : risolvi(dir, href);
            if (p !== null && self.files[p] !== undefined) {
                var st = doc.createElement('style');
                st.textContent = self.files[p];
                st.htmlveCartella = cartellaDi(p); // Gli url() del CSS sono relativi al file .css.
                l.replaceWith(st);
            } else {
                l.remove();
            }
        });
        ogni('script[src]', function(s) {
            var href = s.getAttribute('src');
            var p = ESTERNO.test(href) ? null : risolvi(dir, href);
            var n = doc.createElement('script');
            if (p !== null && self.files[p] !== undefined) {
                n.textContent = self.files[p];
            }
            s.replaceWith(n);
        });
        // Immagini: quelle del sito diventano data URL, le altre restano rotte come nel browser.
        ogni('img[src], input[type=image][src]', function(x) {
            x.setAttribute('src', self.urlRisorsa(dir, x.getAttribute('src')) || 'data:,');
        });
        ogni('source[src], video[src], audio[src], iframe[src], embed[src]', function(x) {
            x.setAttribute('src', 'data:,');
        });
        ogni('style', function(st) {
            st.textContent = self.riscriviUrl(st.textContent, st.htmlveCartella !== undefined ? st.htmlveCartella : dir);
        });
        ogni('[style]', function(x) {
            x.setAttribute('style', self.riscriviUrl(x.getAttribute('style'), dir));
        });
        ogni('[srcset]', function(x) {
            x.removeAttribute('srcset');
        });

        // I percorsi relativi rimasti (es. url() nel CSS) puntano a un indirizzo inesistente, non al server di Moodle.
        var base = doc.createElement('base');
        base.setAttribute('href', 'https://anteprima.invalid/');
        var sc = doc.createElement('script');
        sc.textContent = SCRIPT_ANTEPRIMA;
        var head = doc.head || doc.documentElement.insertBefore(doc.createElement('head'), doc.body);
        head.insertBefore(sc, head.firstChild);
        head.insertBefore(base, head.firstChild);
        return (conDoctype ? '<!DOCTYPE html>\n' : '') + doc.documentElement.outerHTML;
    };

    /* Il titolo nella scheda: il <title> della pagina; senza, il nome del file, come fa il browser. */
    SitoUi.prototype.aggiornaScheda = function() {
        var p = this.pagina;
        var titolo = '';
        var sorgente = p && this.files[p];
        if (typeof sorgente === 'string') {
            if (ePhp(p) && this.uscitaPhp && this.uscitaPhp.chiave.split(' ')[0] === p && this.uscitaPhp.titolo) {
                // Pagina PHP eseguita nell'anteprima: il <title> di quello che ha stampato.
                titolo = new DOMParser().parseFromString(this.uscitaPhp.titolo, 'text/html').documentElement.textContent;
            } else if (ePhp(p)) {
                // Di una pagina PHP si legge il <title> scritto nel codice, se c'è (senza eseguire il PHP).
                var m = /<title[^>]*>([\s\S]*?)<\/title>/i.exec(sorgente);
                titolo = m && !/<\?/.test(m[1]) ? new DOMParser().parseFromString(m[1], 'text/html').documentElement.textContent : '';
            } else {
                titolo = new DOMParser().parseFromString(sorgente, 'text/html').title;
            }
        }
        if (p && sorgente === undefined) {
            titolo = this.immagini[p] !== undefined ? nomeDi(p) : '404 Not Found';
        }
        titolo = (titolo || '').replace(/\s+/g, ' ').trim();
        var senza = !titolo;
        this.scheda.classList.toggle('senza-titolo', senza && !!p);
        this.titoloScheda.textContent = senza ? (p ? nomeDi(p) + this.coda() : 'Nuova scheda') : titolo;
        this.scheda.title = senza && p ? 'La pagina non ha un <title> (o è vuoto): il browser mostra il nome del file.' : titolo;
    };

    /* Quello che segue il nome della pagina nella barra degli indirizzi: ?nome=valore per i dati GET. */
    SitoUi.prototype.coda = function() {
        var r = this.richiesta;
        if (!r || r.metodo !== 'get' || !r.dati.length) {
            return '';
        }
        return '?' + r.dati.map(function(d) {
            return encodeURIComponent(d[0]) + '=' + encodeURIComponent(d[1]).replace(/%20/g, '+');
        }).join('&');
    };

    /* Invio di un modulo nell'anteprima: si va alla pagina dell'action con i dati, come farebbe il browser. */
    SitoUi.prototype.invio = function(metodo, azione, dati) {
        if (ESTERNO.test(azione)) {
            this.avviso.textContent = 'Il modulo invia i dati a un altro sito (' + azione + '): nell\'anteprima non si apre.';
            this.avviso.style.display = 'block';
            return;
        }
        metodo = metodo === 'post' ? 'post' : 'get';
        var p = azione.split('#')[0].split('?')[0] === '' ? this.pagina : risolvi(cartellaDi(this.pagina || ''), azione);
        this.vai(p === null ? azione : '/' + p, {metodo: metodo, dati: dati});
    };

    SitoUi.prototype.vai = function(href, richiesta) {
        if (ESTERNO.test(href)) {
            this.avviso.textContent = 'Link a un sito esterno (' + href + '): nell\'anteprima non si apre.';
            this.avviso.style.display = 'block';
            return;
        }
        var p = risolvi(cartellaDi(this.pagina || ''), href);
        if (p !== null && this.files[p] === undefined && this.tutteLeCartelle().indexOf(p) >= 0) {
            p = unisci(p, 'index.html');
        }
        if (p !== null && this.immagini[p] !== undefined) {
            this.richiesta = null;
            this.storia.push(this.pagina);
            this.pagina = p;
            this.mostraIndirizzo('/' + p);
            this.btnIndietro.disabled = false;
            this.aggiornaScheda();
            this.iframe.srcdoc = '<!DOCTYPE html><html><body style="margin:0;background:#0e0e0e;display:flex;' +
                'align-items:center;justify-content:center;height:100vh"><img src="' + this.urlImmagine(p) + '"></body></html>';
            return;
        }
        if (!richiesta) {
            // Un link con ?nome=valore porta i dati con GET, come un modulo.
            var q = href.split('#')[0].split('?')[1];
            richiesta = q ? {metodo: 'get', dati: q.split('&').filter(Boolean).map(function(c) {
                var kv = c.split('=');
                var dec = function(x) {
                    try {
                        return decodeURIComponent((x || '').replace(/\+/g, ' '));
                    } catch (e) {
                        return x || '';
                    }
                };
                return [dec(kv[0]), dec(kv.slice(1).join('='))];
            })} : null;
        }
        this.storia.push(this.pagina);
        this.pagina = p === null ? href : p;
        this.richiesta = richiesta;
        this.paginaNonTrovata = this.files[this.pagina] === undefined;
        this.aggiornaAnteprima();
        this.paginaNonTrovata = false;
    };

    SitoUi.prototype.indietro = function() {
        if (this.storia.length) {
            this.richiesta = null;
            this.pagina = this.storia.pop();
            this.aggiornaAnteprima();
        }
    };

    /* ---------- immagini ---------- */

    /* Le immagini fornite stanno nel testo della domanda: si leggono e si trasformano in data URL,
       perché l'anteprima isolata non può caricarle da Moodle. */
    SitoUi.prototype.leggiImmaginiFornite = function() {
        var self = this;
        if (!this.fornite.length) {
            return;
        }
        // Tutte le immagini della domanda tranne quelle dell'editor: il testo non ha sempre la classe qtext.
        var immaginiTesto = this.que ? Array.prototype.filter.call(this.que.querySelectorAll('img'), function(img) {
            return !img.closest('.htmlve');
        }) : [];
        if (this.que && !immaginiTesto.length) {
            window.console.warn('html_sito: nessuna immagine trovata nel testo della domanda');
        }
        this.fornite.forEach(function(nome) {
            var trovata = immaginiTesto.filter(function(img) {
                var src = (img.getAttribute('src') || '').split('?')[0].split('#')[0];
                var ultimo = src.slice(src.lastIndexOf('/') + 1);
                try {
                    ultimo = decodeURIComponent(ultimo);
                } catch (e) {
                    // Lascia il nome com'è.
                }
                return ultimo === nome;
            })[0];
            if (!trovata) {
                window.console.warn('html_sito: l\'immagine ' + nome + ' non è nel testo della domanda. Immagini trovate: ' +
                    immaginiTesto.map(function(img) {
                        return img.getAttribute('src');
                    }).join(', '));
                self.datiImmagini[nome] = segnaposto(nome);
                return;
            }
            self.datiImmagini[nome] = trovata.src; // Intanto l'indirizzo; il data URL arriva tra poco.
            fetch(trovata.src, {credentials: 'same-origin'}).then(function(r) {
                if (!r.ok) {
                    throw new Error(r.status);
                }
                return r.blob();
            }).then(function(blob) {
                return new Promise(function(fatto) {
                    var fr = new FileReader();
                    fr.onload = function() {
                        fatto(fr.result);
                    };
                    fr.readAsDataURL(blob);
                });
            }).then(function(url) {
                self.datiImmagini[nome] = url;
                self.aggiornaAnteprima();
                if (self.apertaImmagine && self.immagini[self.apertaImmagine] === nome) {
                    self.apriImmagine(self.apertaImmagine);
                }
            }).catch(function() {
                // Senza fetch (es. pagina aperta dal disco) si prova a ridisegnare l'immagine già caricata.
                try {
                    var c = document.createElement('canvas');
                    c.width = trovata.naturalWidth;
                    c.height = trovata.naturalHeight;
                    c.getContext('2d').drawImage(trovata, 0, 0);
                    self.datiImmagini[nome] = c.toDataURL('image/png');
                } catch (e) {
                    self.datiImmagini[nome] = trovata.src;
                }
                self.aggiornaAnteprima();
            });
        });
    };

    SitoUi.prototype.urlImmagine = function(percorso) {
        var origine = this.immagini[percorso];
        if (origine === undefined) {
            return null;
        }
        if (origine.indexOf('data:') === 0) {
            return origine;
        }
        return this.datiImmagini[origine] || segnaposto(origine);
    };

    /* Indirizzo da usare nell'anteprima per un percorso scritto nella pagina: l'immagine del sito, se c'è. */
    SitoUi.prototype.urlRisorsa = function(cartella, href) {
        if (!href || ESTERNO.test(href)) {
            return /^data:/i.test(href || '') ? href : null;
        }
        var p = risolvi(cartella, href);
        return p === null ? null : this.urlImmagine(p);
    };

    SitoUi.prototype.riscriviUrl = function(css, cartella) {
        var self = this;
        return (css || '').replace(/url\(\s*(['"]?)([^'")]*)\1\s*\)/gi, function(tutto, virgolette, href) {
            var u = self.urlRisorsa(cartella, href.trim());
            return u ? 'url("' + u + '")' : tutto;
        });
    };

    /* Finestrella con le immagini fornite (e, se consentito, il caricamento dal computer). */
    SitoUi.prototype.scegliImmagine = function() {
        var self = this;
        return new Promise(function(fine) {
            var f = self.finestra;
            f.textContent = '';
            var box = el('div', 'htmlve-dialogo');
            var dir = self.cartellaDestinazione();
            box.appendChild(el('div', 'htmlve-msg', 'Quale immagine vuoi mettere in «' + (dir || 'sito') + '»?'));
            var griglia = el('div', 'htmlve-griglia');
            var chiudi = function(r) {
                f.classList.remove('aperta');
                f.textContent = '';
                fine(r);
            };
            self.fornite.forEach(function(nome) {
                var b = el('button', 'htmlve-scelta');
                b.type = 'button';
                var img = el('img');
                img.src = self.datiImmagini[nome] || segnaposto(nome);
                img.alt = nome;
                b.appendChild(img);
                b.appendChild(el('span', '', nome));
                b.addEventListener('click', function() {
                    chiudi({nome: nome, origine: nome});
                });
                griglia.appendChild(b);
            });
            box.appendChild(griglia);
            var errore = el('div', 'htmlve-errore');
            var bottoni = el('div', 'htmlve-bottoni');
            if (self.caricaConsentito) {
                var input = el('input');
                input.type = 'file';
                input.accept = 'image/*';
                input.style.display = 'none';
                input.addEventListener('change', function() {
                    var file = input.files && input.files[0];
                    if (!file) {
                        return;
                    }
                    if (!/^image\//.test(file.type)) {
                        errore.textContent = 'Il file scelto non è un\'immagine.';
                        return;
                    }
                    if (file.size > MAX_IMMAGINE) {
                        errore.textContent = 'L\'immagine è troppo grande (massimo ' + Math.round(MAX_IMMAGINE / 1024) +
                            ' KB): riducila prima di caricarla.';
                        return;
                    }
                    var fr = new FileReader();
                    fr.onload = function() {
                        chiudi({nome: nomePulito(file.name), origine: fr.result});
                    };
                    fr.readAsDataURL(file);
                });
                box.appendChild(input);
                var carica = el('button', 'htmlve-btn', 'Carica dal computer…');
                carica.type = 'button';
                carica.addEventListener('click', function() {
                    input.click();
                });
                bottoni.appendChild(carica);
            }
            box.appendChild(errore);
            var no = el('button', 'htmlve-btn', 'Annulla');
            no.type = 'button';
            no.addEventListener('click', function() {
                chiudi(null);
            });
            bottoni.appendChild(no);
            box.appendChild(bottoni);
            box.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    e.preventDefault();
                    e.stopPropagation();
                    chiudi(null);
                }
            });
            f.appendChild(box);
            f.classList.add('aperta');
            setTimeout(function() {
                no.focus();
            }, 0);
        });
    };

    SitoUi.prototype.nuovaImmagine = function() {
        var self = this;
        var dir = this.cartellaDestinazione();
        this.scegliImmagine().then(function(scelta) {
            if (!scelta) {
                return null;
            }
            return self.chiediNome('Nome dell\'immagine in «' + (dir || 'sito') + '»:', scelta.nome, dir).then(function(nome) {
                if (!nome) {
                    return;
                }
                var p = unisci(dir, nome);
                self.immagini[p] = scelta.origine;
                self.apriImmagine(p);
                self.aggiornaAnteprima();
                self.programmaSalvataggio();
            });
        });
    };

    /* ---------- schermo intero ---------- */

    SitoUi.prototype.schermoIntero = function() {
        var pieno = this.radice.classList.toggle('htmlve-pieno');
        document.documentElement.classList.toggle('htmlve-blocca-scorrimento', pieno);
        this.btnSchermo.textContent = pieno ? 'Riduci' : 'Schermo intero';
        var self = this;
        setTimeout(function() {
            self.disponi();
        }, 0);
    };

    return {
        Constructor: SitoUi
    };
});
