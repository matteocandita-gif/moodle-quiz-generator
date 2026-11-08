/* Griglie di valutazione: il modulo comune alle pagine del plugin («Tracce di progettazione»; in seguito
   «Bozze dei quiz» e «Correzione verifiche») e agli script in Node.

   Una griglia è un elenco di righe, ognuna {macro, area, max, descrittori, tipo}:
     macro        la macroarea (prima colonna); righe consecutive con la stessa macro si uniscono
     area         l'area di valutazione (seconda colonna); vuota: la riga occupa le due colonne
     max          i punti della riga; null per una riga di sola descrizione (es. «Query SQL – Descrizione»)
     descrittori  i cinque descrittori dei livelli, o null (le righe delle singole query hanno solo le fasce)
     tipo         una chiave libera, che dice da dove viene la riga (entita, query, aperta, teoria…)
   Le fasce dei livelli non si salvano: si calcolano dai punti con fasce(max).
   Il voto è il punteggio diviso il totale, per 10, arrotondato al mezzo voto.

   Nel browser il modulo è window.Griglia; in Node require("./griglia.js"). Nessuna libreria esterna. */
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.Griglia = api;
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var LIVELLI = ["Insufficiente", "Base (2)", "Sufficiente (3)", "Buono (4)", "Ottimo (5)"];

  /* Descrittori predefiniti. Cambiandoli qui cambiano per tutte le griglie che non li hanno personalizzati
     (quelle con le righe salvate nella verifica restano come sono). */
  var DESCRITTORI = {
    /* progettazione di database (E/R) */
    entita: [
      "Il modello presenta gravi mancanze: entità essenziali assenti o scorrette, attributi incompleti o collocati in modo errato, chiavi mancanti o sbagliate e notazione grafica molto imprecisa o incoerente.",
      "Il modello individua solo parte delle entità necessarie; gli attributi sono parzialmente corretti ma non sempre ben posizionati; le chiavi sono individuate in modo incerto; la notazione è irregolare ma ancora interpretabile.",
      "Il modello contiene la maggior parte delle entità corrette e gli attributi principali sono ben collocati; le chiavi sono individuate con solo lievi imprecisioni; la notazione è nel complesso corretta con minimi errori formali.",
      "Tutte le entità e gli attributi richiesti sono presenti e correttamente collocati; le chiavi sono individuate correttamente; la notazione è chiara, coerente e senza errori sostanziali. Qualche imprecisione o scelta non ottimale.",
      "Entità e attributi scelti sono corretti, chiari ed efficaci, senza ridondanze; i dati multipli e quelli derivati sono trattati correttamente. Struttura ordinata e leggibile; eventuali imprecisioni sono marginali."
    ],
    associazioni: [
      "Le associazioni tra le entità sono in gran parte assenti, errate o incoerenti; notazione confusa o scorretta.",
      "Alcune associazioni sono corrette, ma ne mancano di importanti o ne compaiono di non pertinenti; notazione incompleta ma ancora comprensibile.",
      "La maggior parte delle associazioni è modellata in modo corretto; i loro attributi sono generalmente ben collocati; la notazione è chiara salvo imprecisioni minori.",
      "Tutte le associazioni richieste sono presenti, corrette e coerenti con il testo; eventuali attributi sono ben collocati; la notazione è chiara e priva di errori. Qualche imprecisione o scelta non ottimale.",
      "Le associazioni sono corrette e modellate in modo chiaro, efficace e senza ridondanze; i loro attributi sono corretti e ben identificati. Eventuali inesattezze grafiche o formali sono marginali."
    ],
    vincoliIsa: [
      "Le cardinalità sono spesso errate o mancanti e le eventuali gerarchie ISA sono assenti o totalmente scorrette; la notazione dei vincoli è confusa.",
      "Alcune cardinalità sono corrette ma altre presentano errori significativi; le ISA sono incomplete o solo parzialmente corrette; la notazione è imprecisa.",
      "Le cardinalità sono nel complesso corrette con pochi errori; le ISA sono adeguate salvo dettagli minori; la notazione dei vincoli è generalmente corretta.",
      "Cardinalità e ISA sono tutte corrette e coerenti con la realtà descritta; la notazione è chiara, omogenea e senza errori sostanziali. Qualche imprecisione o scelta non ottimale.",
      "Cardinalità e partecipazioni sono corrette e motivate; le ISA sono modellate in modo corretto sia nel significato sia nel disegno; la notazione dei vincoli è completa, rigorosa e coerente."
    ],
    vincoli: [
      "Le cardinalità sono spesso errate o mancanti; la notazione dei vincoli è confusa.",
      "Alcune cardinalità sono corrette ma altre presentano errori significativi; la notazione è imprecisa.",
      "Le cardinalità sono nel complesso corrette con pochi errori; la notazione dei vincoli è generalmente corretta.",
      "Le cardinalità sono tutte corrette e coerenti con la realtà descritta; la notazione è chiara, omogenea e senza errori sostanziali. Qualche imprecisione o scelta non ottimale.",
      "Cardinalità e partecipazioni sono corrette e motivate; la notazione dei vincoli è completa, rigorosa e coerente."
    ],
    documentazione: [
      "Assente, gravemente incompleta o strutturalmente errata.",
      "Incompleta, con errori strutturali rilevanti o informazioni poco pertinenti.",
      "Documentazione parzialmente completa: alcuni tipi di dato o vincoli sono corretti, altri imprecisi o mancanti; struttura comunque corretta.",
      "Documentazione completa negli elementi essenziali, con scelte di tipo di dato e vincoli generalmente corrette; ipotesi aggiuntive indicate; nessun errore sostanziale.",
      "Documentazione completa e chiara, con scelte di tipo di dato e vincoli appropriate e coerenti; ipotesi aggiuntive indicate e motivate; eventuali imprecisioni sono marginali."
    ],
    relazionale: [
      "Modello assente o ampiamente errato: mancano relazioni, campi, chiavi primarie ed esterne.",
      "Modello incompleto o con errori strutturali rilevanti: relazioni mancanti o mal derivate, campi non presenti, chiavi primarie mancanti o scorrette.",
      "Modello nel complesso corretto ma con alcune imprecisioni: tutte le relazioni sono presenti con i loro campi; le chiavi primarie sono indicate; la traduzione delle associazioni è talvolta imprecisa.",
      "Modello corretto con poche imprecisioni: tutte le relazioni sono presenti; le chiavi primarie sono indicate correttamente; quasi tutte le associazioni e le gerarchie sono tradotte correttamente.",
      "Modello corretto e coerente con il diagramma E/R: tutte le relazioni sono presenti; chiavi primarie ed esterne, associazioni e gerarchie sono ricavate e indicate correttamente."
    ],
    query: [
      "Query assente, non eseguibile o completamente errata; sintassi non valida o logica incoerente rispetto al modello.",
      "Query parzialmente eseguibile ma con errori logici rilevanti (JOIN errati, condizioni scorrette, tabelle o attributi sbagliati); risultato non utilizzabile.",
      "Query strutturalmente corretta e quasi del tutto eseguibile; logica generalmente corretta ma con imprecisioni (condizioni o JOIN incompleti, ambiguità minori); risultato solo parzialmente corretto.",
      "Query eseguibile e quasi corretta nel risultato; uso adeguato di JOIN, condizioni e attributi; qualche errore nelle condizioni o nelle formule.",
      "Query corretta, chiara e ben strutturata, con scelta efficace delle condizioni e dei JOIN; eventuali imprecisioni sono marginali e non cambiano il risultato."
    ],
    php: [
      "Pagina assente o non funzionante: connessione, query o visualizzazione mancanti o completamente errate.",
      "Pagina incompleta: alcune parti sono presenti (connessione, form o query) ma con errori che impediscono di ottenere il risultato richiesto.",
      "Pagina nel complesso funzionante: connessione e query corrette, con imprecisioni nella lettura dei dati del form o nella visualizzazione dei risultati.",
      "Pagina funzionante e coerente con il proprio database: form, query e visualizzazione corretti; qualche imprecisione o controllo mancante.",
      "Pagina corretta, chiara e ordinata: form, connessione, query e visualizzazione dei risultati completi; gestisce anche il caso senza risultati o l'errore della query."
    ],
    /* domanda aperta di teoria, dentro una verifica di progettazione */
    aperta: [
      "Risposta assente o con concetti errati; terminologia non corretta.",
      "Risposta molto incompleta: pochi elementi corretti, esposti in modo frammentario.",
      "Gli elementi principali sono corretti ma poco sviluppati; terminologia nel complesso corretta.",
      "Risposta completa e corretta, con qualche imprecisione o un esempio poco pertinente.",
      "Risposta completa, precisa e ben organizzata, con terminologia rigorosa ed esempi pertinenti."
    ],
    /* competenze delle verifiche di programmazione (JavaScript, SQL, PHP, HTML) */
    teoria: [
      "Risposte assenti o con concetti errati; terminologia non corretta.",
      "Conosce solo alcuni concetti, in modo frammentario; terminologia spesso imprecisa.",
      "Conosce i concetti principali e li applica a casi semplici; terminologia nel complesso corretta.",
      "Conosce i concetti in modo completo e li applica ai casi proposti; qualche imprecisione nei termini.",
      "Conoscenze complete e sicure, applicate con precisione anche ai casi meno immediati; terminologia rigorosa."
    ],
    lettura: [
      "Non ricostruisce che cosa fa il codice né ne prevede il risultato.",
      "Interpreta solo le istruzioni più semplici; il risultato previsto è in gran parte errato.",
      "Segue il codice nei casi semplici; errori su condizioni, cicli o casi particolari.",
      "Prevede il risultato e riconosce il codice che lo produce; qualche errore sui dettagli.",
      "Legge il codice con sicurezza anche nei casi particolari e distingue con precisione codici quasi uguali."
    ],
    debug: [
      "Non individua gli errori, o le correzioni non risolvono il problema.",
      "Individua solo alcuni errori, soprattutto di sintassi; correzioni incomplete.",
      "Individua e corregge gli errori principali; quelli di logica solo in parte.",
      "Individua e corregge errori di sintassi e di logica; qualche correzione imprecisa.",
      "Individua tutti gli errori, ne spiega la causa e li corregge senza introdurne di nuovi."
    ],
    scrittura: [
      "Codice assente, non funzionante o lontano dalla richiesta.",
      "Codice parziale, con errori di sintassi o di logica che impediscono di ottenere il risultato richiesto.",
      "Codice funzionante che soddisfa i requisiti principali; errori nei casi particolari o qualche requisito mancante.",
      "Codice corretto che soddisfa quasi tutti i requisiti; qualche imprecisione o scelta poco efficace.",
      "Codice corretto, completo e leggibile (nomi, indentazione, a capo), che gestisce anche i casi particolari e risolve anche i problemi più complessi della prova."
    ]
  };

  /* parti intere quasi uguali che fanno esattamente il totale (30 su 4: 8, 8, 7, 7) */
  function distribuisci(totale, n) {
    if (n <= 0) return [];
    var base = Math.floor(totale / n), resto = totale - base * n, out = [];
    for (var i = 0; i < n; i++) out.push(base + (i < resto ? 1 : 0));
    return out;
  }

  /* fasce dei cinque livelli in proporzione al massimo: 15 → 0-3, 4-6, 7-9, 10-12, 13-15.
     Sotto i 5 punti i livelli non stanno in punti interi: mezzi punti (4 → 0-1, 1,5, 2-2,5, 3, 3,5-4). */
  function fasce(max) {
    if (max == null || !(max > 0)) return null;
    var passo = max < 5 ? 0.5 : 1, arr = function (v) { return Math.round(v / passo) * passo; };
    var num = function (v) { return String(v).replace(".", ","); };
    var su = [1, 2, 3, 4, 5].map(function (k) { return arr(max * k / 5); }), out = [], giu = 0;
    for (var k = 0; k < 5; k++) { var a = giu, b = Math.min(Math.max(su[k], a), max); out.push(a === b ? num(b) : num(a) + "-" + num(b)); giu = b + passo; }
    return out;
  }

  /* il livello (0-4) di un punteggio in una riga da max punti, secondo le fasce */
  function livello(punti, max) {
    if (!(max > 0) || punti == null || isNaN(punti)) return null;
    var passo = max < 5 ? 0.5 : 1, arr = function (v) { return Math.round(v / passo) * passo; };
    for (var k = 0; k < 5; k++) if (punti <= arr(max * (k + 1) / 5)) return k;
    return 4;
  }

  var copia = function (o) { return JSON.parse(JSON.stringify(o)); };

  /* righe pulite (senza fasce) da salvare in una verifica: si tengono solo i campi del formato */
  function daSalvare(righe) {
    return (righe || []).map(function (r) {
      var d = Array.isArray(r.descrittori) && r.descrittori.some(function (x) { return String(x || "").trim(); })
        ? [0, 1, 2, 3, 4].map(function (k) { return String(r.descrittori[k] || ""); }) : null;
      return { macro: String(r.macro || ""), area: String(r.area || ""), max: r.max == null || r.max === "" ? null : Number(r.max) || 0, descrittori: d, tipo: String(r.tipo || "") };
    });
  }

  /* la griglia completa: righe con le fasce, totale */
  function completa(righe) {
    var out = (righe || []).map(function (r) { var x = copia(r); x.fasce = fasce(x.max); return x; });
    var totale = out.reduce(function (s, r) { return s + (Number(r.max) || 0); }, 0);
    return { righe: out, totale: totale };
  }

  /* il voto da un punteggio: punti / totale × 10, al mezzo voto più vicino */
  function voto(punti, totale) {
    if (!(totale > 0)) return null;
    return Math.round(punti / totale * 10 * 2) / 2;
  }

  /* problemi di una griglia, per gli avvisi delle pagine e degli script */
  function controlla(g, atteso) {
    var avv = [];
    if (atteso != null && g.totale !== atteso) avv.push("la griglia fa " + g.totale + " punti invece di " + atteso + ": controlla i punti delle righe");
    g.righe.forEach(function (r, i) {
      if (!String(r.macro || "").trim() && !String(r.area || "").trim()) avv.push("la riga " + (i + 1) + " non ha un nome");
      if (r.max != null && !(r.max >= 0)) avv.push("la riga " + (i + 1) + " ha punti non validi");
    });
    return avv;
  }

  /* ------------------------------------------------------------------ verifiche di programmazione: competenze */
  /* Le righe della griglia sono le competenze, non gli esercizi; ogni riga raccoglie gli esercizi che la
     verificano (per tipologia, qualunque sia la parte della verifica). La parte avanzata non è una riga. */
  var COMPETENZE = [
    { tipo: "teoria", area: "Conoscenze teoriche" },
    { tipo: "lettura", area: "Lettura e comprensione del codice" },
    { tipo: "debug", area: "Individuazione e correzione degli errori" },
    { tipo: "scrittura", area: "Scrittura di codice" }
  ];
  /* tipologia della dashboard «Bozze dei quiz» → competenza; null = non valutata (pagine, campo di prova) */
  var COMPETENZA_TIPOLOGIA = {
    istruzioni: null, comelavoriamo: null, paginablocco: null, campo_prova: null,
    /* tipologie generiche: decide la lettera della posizione (L lettura, D errori, altrimenti teoria) */
    vf: "pos", multipla: "pos", crocette: "pos", breve: "pos", corrispondenza: "pos", cloze_testo: "pos", ordine: "pos",
    teoria_aperta: "teoria",
    esempio_svolto: "lettura", tracciamento: "lettura", lettura_output: "lettura",
    trova_errore: "debug", debug_msg: "debug", debug_silenzioso: "debug", debug_motivazione: "debug",
    compl_campi: "scrittura", guidato: "scrittura", compl_eseguito: "scrittura", scrittura_scheletro: "scrittura",
    prog_completo: "scrittura", funzione: "scrittura", prog_dati: "scrittura", prog_random: "scrittura", query: "scrittura",
    create_tabelle: "scrittura", query_due_passi: "scrittura", vincoli: "scrittura", pagina_php: "scrittura",
    esercizio_libero: "scrittura", consegna_file: "scrittura", libero_html: "scrittura", libero_css: "scrittura"
  };
  var POS_COMPETENZA = { T: "teoria", L: "lettura", D: "debug" };
  var basePos = function (p) { return String(p || "").trim().replace(/[a-z]$/, ""); };
  function competenzaDi(riga) {
    var t = riga.tipologia;
    var lettera = basePos(riga.pos).charAt(0);
    if (Object.prototype.hasOwnProperty.call(COMPETENZA_TIPOLOGIA, t)) {
      var c = COMPETENZA_TIPOLOGIA[t];
      return c === "pos" ? (POS_COMPETENZA[lettera] || "teoria") : c;
    }
    return POS_COMPETENZA[lettera] || "scrittura";
  }
  /* le posizioni valutate di una verifica: una per posizione anche con più varianti (E1a, E1b → E1) */
  function posizioni(righe) {
    var out = [], per = {};
    (righe || []).slice().sort(function (a, b) { return (Number(a.ordine) || 0) - (Number(b.ordine) || 0); }).forEach(function (r) {
      var c = competenzaDi(r), p = basePos(r.pos), pt = Number(r.punti) || 0;
      if (!c || !p || !(pt > 0)) return;
      if (!per[p]) { per[p] = { pos: p, punti: pt, pdp: !!r.pdp, competenza: c, titolo: r.titolo || "" }; out.push(per[p]); }
      else { per[p].punti = Math.max(per[p].punti, pt); per[p].pdp = per[p].pdp || !!r.pdp; }
    });
    return out;
  }
  /* la griglia di una verifica dalle sue righe (domande della dashboard) e dalla personalizzazione salvata nel
     quiz (quiz.griglia.righe: [{area, descrittori, tipo, pos: ["T1", "E2"…]}]). Ogni riga:
     {area, tipo, descrittori, pos, max, maxPdp, tolte}. In più: senzaRiga (posizioni non assegnate). */
  function daDomande(righe, personalizzazione) {
    var P = posizioni(righe), di = {}, out = [], assegnate = {};
    P.forEach(function (x) { di[x.pos] = x; });
    var base = personalizzazione && Array.isArray(personalizzazione.righe) && personalizzazione.righe.length
      ? personalizzazione.righe.map(function (r) { return { area: r.area, tipo: r.tipo || "personale", descrittori: r.descrittori, pos: (r.pos || []).filter(function (p) { return di[p]; }) }; })
      : COMPETENZE.map(function (c) { return { area: c.area, tipo: c.tipo, descrittori: null, pos: P.filter(function (x) { return x.competenza === c.tipo; }).map(function (x) { return x.pos; }) }; })
        .filter(function (r) { return r.pos.length; });
    base.forEach(function (r) {
      r.pos.forEach(function (p) { assegnate[p] = true; });
      r.descrittori = Array.isArray(r.descrittori) && r.descrittori.some(function (x) { return String(x || "").trim(); }) ? r.descrittori
        : (DESCRITTORI[r.tipo] || ["", "", "", "", ""]).slice();
      r.max = r.pos.reduce(function (s, p) { return s + di[p].punti; }, 0);
      r.tolte = r.pos.filter(function (p) { return di[p].pdp; });
      r.maxPdp = r.pos.reduce(function (s, p) { return s + (di[p].pdp ? 0 : di[p].punti); }, 0);
      out.push(r);
    });
    var g = completa(out);
    g.totalePdp = out.reduce(function (s, r) { return s + r.maxPdp; }, 0);
    g.tolte = P.filter(function (x) { return x.pdp; }).map(function (x) { return x.pos; });
    g.senzaRiga = P.filter(function (x) { return !assegnate[x.pos]; }).map(function (x) { return x.pos; });
    g.posizioni = P;
    g.personalizzata = !!(personalizzazione && Array.isArray(personalizzazione.righe) && personalizzazione.righe.length);
    return g;
  }
  /* la personalizzazione da salvare nel quiz, a partire dalla griglia attuale */
  function personalizzazioneDi(g) {
    return { righe: g.righe.map(function (r) { return { area: r.area, tipo: r.tipo, descrittori: r.descrittori.slice(), pos: r.pos.slice() }; }) };
  }

  /* ------------------------------------------------------------------ tabella HTML (commento di Moodle) */
  /* Stili negli attributi: l'editor di Moodle toglie i <style>. opz.pdp: copia PDP (colonne Classe e PDP,
     esercizi tolti barrati); opz.punti: {indice riga → punti dello studente}, per la griglia compilata. */
  function escH(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
  var num = function (v) { return String(Math.round(v * 100) / 100).replace(".", ","); };
  function htmlTabella(g, opz) {
    opz = opz || {};
    var pdp = !!opz.pdp, punti = opz.punti || null, B = "border:1px solid #888;padding:4px 6px;vertical-align:top;";
    var th = function (t, x) { return '<th style="' + B + 'background:#e7e6e6;text-align:center;' + (x || "") + '">' + t + "</th>"; };
    var h = "";
    if (pdp) h += '<p style="margin:0 0 6px 0;"><strong>Riduzione dei contenuti per PDP</strong>: ' + (g.tolte.length ? "tolti " + escH(g.tolte.join(", ")) + " (" + num(g.totale - g.totalePdp) + " punti su " + num(g.totale) + "). Punteggio massimo " + num(g.totalePdp) + "." : "nessun esercizio tolto.") + "</p>";
    h += '<table style="border-collapse:collapse;font-size:12px;width:100%;"><thead><tr>' + th("Competenza", "width:16%;") +
      LIVELLI.map(function (l) { return th(escH(l)); }).join("") + th(pdp ? "Punti (classe → PDP)" : "Punti", "width:9%;") + "</tr></thead><tbody>";
    var totS = 0, totM = 0;
    g.righe.forEach(function (r, i) {
      if (!r.pos || !r.pos.length) return;   // competenza senza esercizi: non è nella griglia
      var max = pdp ? r.maxPdp : r.max, f = fasce(max), p = punti ? punti[i] : null, lv = p != null && max > 0 ? livello(p, max) : null;
      totM += max; if (p != null) totS += p;
      var es = r.pos.map(function (x) { return r.tolte.indexOf(x) >= 0 && pdp ? "<s>" + escH(x) + "</s>" : escH(x); }).join(", ");
      h += '<tr><td style="' + B + '"><strong>' + escH(r.area) + '</strong><br><span style="font-size:11px;">Esercizi: ' + es + "</span></td>";
      if (!(max > 0)) {
        h += '<td colspan="5" style="' + B + 'color:#666;font-style:italic;">Non valutata: esercizi tolti per riduzione PDP</td>';
      } else {
        for (var k = 0; k < 5; k++) {
          var su = lv === k;
          h += '<td style="' + B + (su ? "background:#cfe2ff;border:2px solid #1a56db;" : "") + '">' + escH(r.descrittori[k]) +
            '<div style="text-align:right;font-weight:bold;">' + (f ? f[k] : "") + "</div></td>";
        }
      }
      var cellaP = (p != null ? "<strong>" + num(p) + "</strong> / " : "") + (pdp && r.max !== r.maxPdp ? '<span style="text-decoration:line-through;">' + num(r.max) + "</span> " + num(r.maxPdp) : num(max));
      h += '<td style="' + B + 'text-align:center;vertical-align:middle;">' + cellaP + "</td></tr>";
    });
    var votoS = punti ? voto(totS, totM) : null;
    h += '</tbody><tfoot><tr><td colspan="6" style="' + B + 'text-align:right;"><strong>Totale</strong>' + (votoS != null ? " — voto <strong>" + num(votoS) + "</strong>" : "") +
      '</td><td style="' + B + 'text-align:center;"><strong>' + (punti ? num(totS) + " / " : "") + num(totM) + "</strong></td></tr></tfoot></table>";
    return h;
  }

  return { LIVELLI: LIVELLI, DESCRITTORI: DESCRITTORI, distribuisci: distribuisci, fasce: fasce, livello: livello,
    daSalvare: daSalvare, completa: completa, voto: voto, controlla: controlla,
    COMPETENZE: COMPETENZE, COMPETENZA_TIPOLOGIA: COMPETENZA_TIPOLOGIA, competenzaDi: competenzaDi, posizioni: posizioni,
    daDomande: daDomande, personalizzazioneDi: personalizzazioneDi, htmlTabella: htmlTabella };
});
