/**
 * Interfaccia «html_sito» per CodeRunner — versione __VERSIONE__
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
 * dell'action con i dati ricevuti. Le pagine .php non si eseguono: le esegue il template con Controlla.
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
 *    domanda successiva dal sito di una domanda precedente dello stesso tentativo.
 * Nella risposta le immagini sono in "immagini": {"img/logo.png": "logo.png"} (immagine fornita)
 * oppure {"img/foto.jpg": "data:image/jpeg;base64,..."} (immagine caricata).
 *
 * @module     qtype_coderunner/ui_html_sito
 * @copyright  2026 Matteo Candita
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
define('qtype_coderunner/ui_html_sito', [], function() {
    'use strict';

    var VERSIONE = '__VERSIONE__';
    var NOME_VALIDO = /^[a-z0-9_-][a-z0-9._-]*$/;
    var ESTERNO = /^([a-z][a-z0-9+.-]*:|\/\/)/i;
    var ALTEZZA_MINIMA = 420;
    var ALTEZZA_PREDEFINITA = 560;
    var STILE = __STILE__;
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
            '<p class="nota">Il codice PHP gira sul server: qui l\'anteprima non lo può eseguire. Premi ' +
            '<b>Controlla</b> per eseguire le pagine PHP con i dati delle prove e vedere che cosa stampano.</p>' +
            '</body></html>';
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
        try {
            if (!window.ace) {
                throw new Error('Ace non è caricato');
            }
            this.solaLettura = this.textarea.readOnly || this.textarea.disabled;
            this.que = this.textarea.closest('.que');
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
        this.stato = el('span', 'htmlve-stato');
        barra.appendChild(this.stato);
        this.btnSchermo = bottone('Schermo intero', 'Allarga l\'editor a tutta la finestra (Esc per tornare)', function() {
            self.schermoIntero();
        });
        r.appendChild(barra);

        var corpo = el('div', 'htmlve-corpo');
        this.albero = el('div', 'htmlve-albero');
        corpo.appendChild(this.albero);

        var codice = el('div', 'htmlve-codice');
        this.titoloFile = el('div', 'htmlve-titolo', '');
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

        var vista = el('div', 'htmlve-vista');
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
            self.aggiornaAnteprima();
        });
        this.campoIndirizzo = el('span', 'htmlve-url', '');
        indirizzo.appendChild(this.btnIndietro);
        indirizzo.appendChild(ricarica);
        indirizzo.appendChild(this.campoIndirizzo);
        vista.appendChild(indirizzo);
        this.iframe = el('iframe', 'htmlve-iframe');
        // allow-forms solo perché il browser controlli i campi prima dell'invio: l'invio vero lo ferma lo script.
        this.iframe.setAttribute('sandbox', 'allow-scripts allow-forms');
        this.iframe.setAttribute('title', 'Anteprima della pagina');
        vista.appendChild(this.iframe);
        this.avviso = el('div', 'htmlve-avviso');
        vista.appendChild(this.avviso);
        corpo.appendChild(vista);
        r.appendChild(corpo);

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
                self.radice.classList.toggle('htmlve-stretto', self.radice.clientWidth < 820);
                if (self.editor) {
                    self.editor.resize();
                }
            });
            this.osservatore.observe(r);
        }
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
        this.titoloFile.textContent = percorso;
        if (eHtml(percorso) || ePhp(percorso)) {
            this.pagina = percorso;
            this.richiesta = null;
            this.storia = [];
            this.aggiornaAnteprima();
        }
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
        this.titoloFile.textContent = percorso;
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
        this.titoloFile.textContent = '';
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
                this.titoloFile.textContent = this.aperto;
            } else if (this.apertaImmagine) {
                this.titoloFile.textContent = this.apertaImmagine;
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

    SitoUi.prototype.aggiornaAnteprima = function() {
        if (!this.pagina || (this.files[this.pagina] === undefined && !this.paginaNonTrovata) || this.immagini[this.pagina] !== undefined) {
            this.pagina = this.paginaPredefinita();
        }
        var html;
        if (!this.pagina) {
            html = paginaMessaggio('Nessuna pagina da visualizzare', 'Crea una pagina HTML (per esempio index.html) per vederla qui.');
            this.campoIndirizzo.textContent = '';
        } else if (this.files[this.pagina] === undefined) {
            html = paginaNonTrovata('/' + this.pagina);
            this.campoIndirizzo.textContent = '/' + this.pagina;
        } else if (ePhp(this.pagina)) {
            html = paginaPhp(this.pagina, this.richiesta);
            this.campoIndirizzo.textContent = '/' + this.pagina + this.coda();
        } else {
            html = this.costruisciPagina(this.pagina);
            this.campoIndirizzo.textContent = '/' + this.pagina + this.coda();
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
        // L'iframe è isolato: a ogni aggiornamento l'anteprima riparte dall'inizio della pagina.
        this.iframe.srcdoc = html;
    };

    SitoUi.prototype.costruisciPagina = function(percorso) {
        var self = this;
        var sorgente = this.files[percorso];
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
            if (ePhp(p)) {
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
            this.campoIndirizzo.textContent = '/' + p;
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
        var ed = this.editor;
        setTimeout(function() {
            if (ed) {
                ed.resize();
            }
        }, 0);
    };

    return {
        Constructor: SitoUi
    };
});
