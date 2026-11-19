/**
 * Interfaccia «html_sito» per CodeRunner — versione 0.6.1
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
 * non può leggere né modificare la pagina di Moodle.
 *
 * Parametri dell'interfaccia (tutti falsi se non indicati), es. {"chiusura_automatica": true}:
 *  - chiusura_automatica: Ace chiude da solo tag, virgolette e parentesi;
 *  - completamento: Ace propone tag, attributi e proprietà mentre si scrive;
 *  - segnala_errori: Ace segna nel margine gli errori di sintassi che riconosce;
 *  - immagini: nomi delle immagini messe dal docente nel testo della domanda, es. "logo.png, pizza.jpg":
 *    lo studente le mette nel sito con «+ Immagine», nella cartella che sceglie;
 *  - carica_immagini: lo studente può caricare immagini dal suo computer (non nelle verifiche con SEB).
 * Nella risposta le immagini sono in "immagini": {"img/logo.png": "logo.png"} (immagine fornita)
 * oppure {"img/foto.jpg": "data:image/jpeg;base64,..."} (immagine caricata).
 *
 * @module     qtype_coderunner/ui_html_sito
 * @copyright  2026 Matteo Candita
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
define('qtype_coderunner/ui_html_sito', [], function() {
    'use strict';

    var VERSIONE = '0.6.1';
    var NOME_VALIDO = /^[a-z0-9_-][a-z0-9._-]*$/;
    var ESTERNO = /^([a-z][a-z0-9+.-]*:|\/\/)/i;
    var ALTEZZA_MINIMA = 420;
    var ALTEZZA_PREDEFINITA = 560;
    var STILE = "html.htmlve-blocca-scorrimento, html.htmlve-blocca-scorrimento body { overflow: hidden !important; }\n\n.htmlve {\n  --htmlve-bordo: #c9ced6;\n  --htmlve-sfondo: #f4f5f7;\n  --htmlve-accento: #0f6cbf;\n  position: relative;\n  display: flex;\n  flex-direction: column;\n  border: 1px solid var(--htmlve-bordo);\n  border-radius: 6px;\n  background: #fff;\n  font-family: system-ui, -apple-system, \"Segoe UI\", Roboto, sans-serif;\n  font-size: 14px;\n  line-height: 1.35;\n  color: #1d2125;\n  margin: 0;\n  text-align: left;\n}\n\n.htmlve * { box-sizing: border-box; }\n\n/* barra dei comandi */\n.htmlve-barra {\n  display: flex;\n  align-items: center;\n  flex-wrap: wrap;\n  gap: 6px;\n  padding: 6px 8px;\n  background: var(--htmlve-sfondo);\n  border-bottom: 1px solid var(--htmlve-bordo);\n  border-radius: 6px 6px 0 0;\n}\n.htmlve-btn {\n  font: inherit;\n  font-size: 13px;\n  padding: 4px 10px;\n  border: 1px solid var(--htmlve-bordo);\n  border-radius: 4px;\n  background: #fff;\n  color: #1d2125;\n  cursor: pointer;\n  line-height: 1.3;\n}\n.htmlve-btn:hover:not(:disabled) { border-color: var(--htmlve-accento); color: var(--htmlve-accento); }\n.htmlve-btn:disabled { opacity: .45; cursor: default; }\n.htmlve-btn.htmlve-primario { background: var(--htmlve-accento); border-color: var(--htmlve-accento); color: #fff; }\n.htmlve-btn.htmlve-primario:hover { color: #fff; filter: brightness(1.1); }\n.htmlve-btn.htmlve-mini { padding: 1px 7px; font-size: 13px; }\n.htmlve-stato { margin-left: auto; font-size: 12px; color: #5c6670; }\n\n/* corpo: albero | codice | anteprima */\n.htmlve-corpo {\n  flex: 1;\n  display: grid;\n  grid-template-columns: 170px minmax(0, 1fr) minmax(0, 1fr);\n  min-height: 0;\n}\n.htmlve-stretto .htmlve-corpo {\n  grid-template-columns: 160px minmax(0, 1fr);\n  grid-template-rows: minmax(0, 1fr) minmax(0, 1fr);\n}\n.htmlve-stretto .htmlve-albero { grid-row: 1 / span 2; }\n.htmlve-stretto .htmlve-vista { grid-column: 2; border-top: 1px solid var(--htmlve-bordo); }\n\n.htmlve-albero {\n  overflow: auto;\n  border-right: 1px solid var(--htmlve-bordo);\n  background: #fafbfc;\n  padding: 4px 0;\n  user-select: none;\n}\n.htmlve-voce {\n  display: flex;\n  align-items: center;\n  gap: 5px;\n  padding: 3px 6px;\n  cursor: pointer;\n  white-space: nowrap;\n  font-size: 13px;\n}\n.htmlve-voce:hover { background: #e9eef5; }\n.htmlve-voce.selezionata, .htmlve-voce.aperta { background: #d6e4f5; }\n.htmlve-voce.aperta .htmlve-nome { font-weight: 600; }\n.htmlve-icona { font-size: 13px; width: 16px; text-align: center; }\n.htmlve-nome { overflow: hidden; text-overflow: ellipsis; }\n.htmlve-suggerimento { padding: 8px 10px; font-size: 12px; color: #5c6670; white-space: normal; }\n\n.htmlve-codice { position: relative; display: flex; flex-direction: column; min-width: 0; min-height: 0; border-right: 1px solid var(--htmlve-bordo); }\n.htmlve-stretto .htmlve-codice { border-right: 0; }\n.htmlve-titolo {\n  font-size: 12px;\n  font-family: Consolas, \"Courier New\", monospace;\n  padding: 4px 8px;\n  border-bottom: 1px solid var(--htmlve-bordo);\n  background: var(--htmlve-sfondo);\n  min-height: 25px;\n}\n.htmlve-cm { flex: 1; min-height: 0; position: relative; }\n.htmlve-ace { position: absolute; inset: 0; }\n.htmlve-vuoto {\n  display: none;\n  position: absolute;\n  top: 60px;\n  left: 50px;\n  right: 20px;\n  color: #6a737d;\n  font-size: 13px;\n}\n\n.htmlve-vista { display: flex; flex-direction: column; min-width: 0; min-height: 0; }\n.htmlve-indirizzo {\n  display: flex;\n  align-items: center;\n  gap: 4px;\n  padding: 3px 6px;\n  background: #e8eaed;\n  border-bottom: 1px solid var(--htmlve-bordo);\n  min-height: 25px;\n}\n.htmlve-url {\n  flex: 1;\n  background: #fff;\n  border-radius: 10px;\n  padding: 1px 10px;\n  font-size: 12px;\n  color: #3c4043;\n  font-family: Consolas, \"Courier New\", monospace;\n  overflow: hidden;\n  white-space: nowrap;\n  text-overflow: ellipsis;\n}\n.htmlve-iframe { flex: 1; width: 100%; border: 0; background: #fff; min-height: 0; }\n.htmlve-avviso { display: none; font-size: 12px; padding: 4px 8px; background: #fff8e1; border-top: 1px solid #f0d78c; color: #6b5300; }\n\n/* finestrella per nomi e conferme */\n.htmlve-finestra { display: none; position: absolute; inset: 0; background: rgba(0, 0, 0, .25); z-index: 5; border-radius: 6px; }\n.htmlve-finestra.aperta { display: flex; align-items: flex-start; justify-content: center; padding-top: 70px; }\n.htmlve-dialogo { background: #fff; border-radius: 6px; padding: 14px 16px; width: min(440px, 92%); box-shadow: 0 6px 24px rgba(0, 0, 0, .2); }\n.htmlve-msg { margin-bottom: 8px; }\n.htmlve-input { width: 100%; font: inherit; font-family: Consolas, \"Courier New\", monospace; padding: 5px 8px; border: 1px solid var(--htmlve-bordo); border-radius: 4px; }\n.htmlve-errore { color: #b3261e; font-size: 12px; min-height: 16px; margin-top: 4px; }\n.htmlve-bottoni { display: flex; justify-content: flex-end; gap: 6px; margin-top: 6px; }\n\n/* sola lettura */\n.htmlve-lettura .htmlve-barra { background: #eef3ea; }\n.htmlve-grezza { border-top: 1px solid var(--htmlve-bordo); padding: 4px 8px; font-size: 12px; }\n.htmlve-grezza summary { cursor: pointer; color: #5c6670; }\n.htmlve-grezza pre { max-height: 240px; overflow: auto; font-size: 12px; white-space: pre-wrap; word-break: break-all; }\n\n/* schermo intero */\n.htmlve.htmlve-pieno { position: fixed; inset: 0; z-index: 100000; margin: 0; border-radius: 0; height: auto !important; }\n.htmlve.htmlve-pieno .htmlve-corpo { grid-template-columns: 200px minmax(0, 1fr) minmax(0, 1fr); grid-template-rows: none; }\n.htmlve.htmlve-pieno .htmlve-albero { grid-row: auto; }\n.htmlve.htmlve-pieno .htmlve-vista { grid-column: auto; border-top: 0; }\n.htmlve.htmlve-pieno .htmlve-codice { border-right: 1px solid var(--htmlve-bordo); }\n\n/* immagini */\n.htmlve-immagine { display: none; position: absolute; top: 26px; left: 0; right: 0; bottom: 0; background: #fafbfc;\n  flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 12px; z-index: 4; }\n.htmlve-immagine img { max-width: 100%; max-height: 80%; object-fit: contain; border: 1px solid var(--htmlve-bordo);\n  background: repeating-conic-gradient(#eee 0% 25%, #fff 0% 50%) 50% / 16px 16px; }\n.htmlve-didascalia { font-size: 12px; color: #5c6670; }\n.htmlve-griglia { display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 8px; max-height: 260px; overflow: auto; }\n.htmlve-scelta { display: flex; flex-direction: column; align-items: center; gap: 4px; width: 112px; padding: 6px;\n  border: 1px solid var(--htmlve-bordo); border-radius: 4px; background: #fff; cursor: pointer; font: inherit; font-size: 12px; }\n.htmlve-scelta:hover { border-color: var(--htmlve-accento); }\n.htmlve-scelta img { width: 96px; height: 64px; object-fit: contain; }\n.htmlve-scelta span { max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }\n\n/* spostamento */\n.htmlve-voce.htmlve-sopra { background: #cfe2f7; outline: 2px dashed var(--htmlve-accento); outline-offset: -2px; }\n.htmlve-destinazioni { display: flex; flex-direction: column; max-height: 260px; overflow: auto; margin: 4px 0 8px;\n  border: 1px solid var(--htmlve-bordo); border-radius: 4px; }\n.htmlve-destinazione { display: flex; align-items: center; gap: 6px; padding: 5px 8px; border: 0; background: #fff;\n  text-align: left; font: inherit; font-size: 13px; cursor: pointer; }\n.htmlve-destinazione:hover:not(:disabled) { background: #e9eef5; }\n.htmlve-destinazione:disabled { color: #9aa1a8; cursor: default; }\n";
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
    }.toString() + ')();';

    function paginaMessaggio(titolo, testo) {
        return '<!DOCTYPE html><html><head><meta charset="utf-8">' +
            '<style>body{font-family:system-ui,sans-serif;color:#555;padding:24px}h1{font-size:18px}</style></head>' +
            '<body><h1>' + titolo + '</h1><p>' + testo + '</p></body></html>';
    }

    function paginaNonTrovata(url) {
        var u = url.replace(/[<>&"]/g, function(c) {
            return {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;'}[c];
        });
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
        this.caricaConsentito = vero(this.params.carica_immagini);
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
        this.iframe.setAttribute('sandbox', 'allow-scripts');
        this.iframe.setAttribute('title', 'Anteprima della pagina');
        vista.appendChild(this.iframe);
        this.avviso = el('div', 'htmlve-avviso');
        vista.appendChild(this.avviso);
        corpo.appendChild(vista);
        r.appendChild(corpo);

        this.finestra = el('div', 'htmlve-finestra');
        r.appendChild(this.finestra);

        this.suMessaggio = function(e) {
            if (e.source !== self.iframe.contentWindow || !e.data || e.data.htmlve !== 'vai') {
                return;
            }
            self.vai(String(e.data.href));
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
        if (eHtml(percorso)) {
            this.pagina = percorso;
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
        if (this.files['index.html'] !== undefined) {
            return 'index.html';
        }
        return Object.keys(this.files).filter(eHtml).sort()[0] || null;
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
        } else {
            html = this.costruisciPagina(this.pagina);
            this.campoIndirizzo.textContent = '/' + this.pagina;
        }
        this.btnIndietro.disabled = !this.storia.length;
        this.avviso.style.display = 'none';
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

    SitoUi.prototype.vai = function(href) {
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
            this.storia.push(this.pagina);
            this.pagina = p;
            this.campoIndirizzo.textContent = '/' + p;
            this.btnIndietro.disabled = false;
            this.iframe.srcdoc = '<!DOCTYPE html><html><body style="margin:0;background:#0e0e0e;display:flex;' +
                'align-items:center;justify-content:center;height:100vh"><img src="' + this.urlImmagine(p) + '"></body></html>';
            return;
        }
        this.storia.push(this.pagina);
        this.pagina = p === null ? href : p;
        this.paginaNonTrovata = this.files[this.pagina] === undefined;
        this.aggiornaAnteprima();
        this.paginaNonTrovata = false;
    };

    SitoUi.prototype.indietro = function() {
        if (this.storia.length) {
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
