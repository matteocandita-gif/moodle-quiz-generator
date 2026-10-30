/* Uscite di una traccia di progettazione: Word della verifica (anche la copia PDP, con la griglia di
   valutazione) e HTML per la descrizione di un Compito Moodle.
   Un solo modulo per la dashboard «Tracce di progettazione» (nel browser) e per Claude in chat (Node):
     node scripts/uscite_traccia.js TRACCIA.json [--word FILE.docx] [--pdp FILE.docx] [--html FILE.html] [--griglia]
   La traccia è il documento JSON descritto in references/formato.md. Nessuna libreria esterna: il .docx
   è uno zip (non compresso) di XML scritto qui. */
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.UsciteTraccia = api;
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  /* ------------------------------------------------------------------ testo */
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  };
  /* **grassetto**, *corsivo* (solo tra spazi: l'asterisco delle chiavi esterne non è corsivo), <u>sottolineato</u> e `codice` in pezzi {t, b, i, u, c} */
  function pezzi(testo) {
    var out = [], re = /(\*\*[^*]+\*\*|<u>.*?<\/u>|`[^`]+`|(?<![^\s(«"])\*[^*\s](?:[^*]*[^*\s])?\*(?![\w*]))/g, s = String(testo || ""), last = 0, m;
    while ((m = re.exec(s))) {
      if (m.index > last) out.push({ t: s.slice(last, m.index) });
      if (m[0].slice(0, 2) === "**") pezzi(m[0].slice(2, -2)).forEach(function (q) { q.b = true; out.push(q); });
      else if (m[0].slice(0, 3) === "<u>") out.push({ t: m[0].slice(3, -4), u: true });
      else if (m[0].charAt(0) === "`") out.push({ t: m[0].slice(1, -1), c: true });
      else out.push({ t: m[0].slice(1, -1), i: true });
      last = m.index + m[0].length;
    }
    if (last < s.length) out.push({ t: s.slice(last) });
    return out;
  }
  var paragrafi = function (s) { return String(s || "").split(/\n\s*\n|\n/).map(function (x) { return x.trim(); }).filter(Boolean); };

  /* ------------------------------------------------------------------ contenuto comune */
  var PRESENTARE = [
    ["er", "Modello E/R completo in tutte le sue componenti."],
    ["documentazione", "Documentazione del progetto."],
    ["relazionale", "Equivalente modello relazionale."],
    ["sql_tabelle", "Definizione in linguaggio SQL di alcune tabelle, con i vincoli di integrità referenziale e di dominio."]
  ];
  function vociPresentare(t) {
    var p = (t.testo && t.testo.presentare) || {};
    return PRESENTARE.filter(function (v) {
      if (v[0] === "documentazione") return p.documentazione !== false;
      if (v[0] === "sql_tabelle") return !!p.sql_tabelle;
      return true;
    }).map(function (v, i) { return { chiave: v[0], testo: v[1], n: i + 1 }; });
  }
  var conPhp = function (t) { return !!(t.testo && t.testo.php && t.testo.php.testo); };
  var conIsa = function (t) {
    var o = t.opzioni || {};
    return o.isa === true || o.isa === "sì" || /\bgerarchia\b/.test((t.docente && t.docente.er) || "");
  };
  var esame = function (t) { return t.uso === "esame"; };
  function riduzione(t, chiave, pdp) {
    if (!pdp) return "";
    var r = (t.pdp && t.pdp.riduzioni) || {};
    return r[chiave] || "";
  }
  var FRASE_IPOTESI = "Tutti gli elementi non esplicitati rimangono a scelta dello studente. Motivare eventualmente le scelte fatte.";
  var FRASE_ORDINE = "Oltre alla correttezza del codice, costituiranno elementi di valutazione anche la struttura e l'ordine dell'esercizio consegnato.";
  var FRASE_QUERY = "Il database così ottenuto dovrà consentire di ricavare le seguenti informazioni:";
  var FRASE_REQUISITI = "tenendo conto anche delle informazioni richieste dalle query";

  /* ------------------------------------------------------------------ griglia */
  var PESI = {
    senzaPhp: { entita: 15, associazioni: 15, vincoli: 15, documentazione: 10, relazionale: 15, query: 30, php: 0 },
    conPhp: { entita: 15, associazioni: 15, vincoli: 10, documentazione: 10, relazionale: 15, query: 20, php: 15 }
  };
  var LIVELLI = ["Insufficiente", "Base (2)", "Sufficiente (3)", "Buono (4)", "Ottimo (5)"];
  var DESCRITTORI = {
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
    ]
  };
  /* parti intere quasi uguali che fanno esattamente il totale (30 su 4 query: 8, 8, 7, 7) */
  function distribuisci(totale, n) {
    if (n <= 0) return [];
    var base = Math.floor(totale / n), resto = totale - base * n, out = [];
    for (var i = 0; i < n; i++) out.push(base + (i < resto ? 1 : 0));
    return out;
  }
  /* fasce dei cinque livelli in proporzione al massimo: 15 → 0-3, 4-6, 7-9, 10-12, 13-15 */
  function fasce(max) {
    /* sotto i 5 punti i livelli non stanno in punti interi: si usano i mezzi punti (4 → 0-1, 1,5, 2-2,5, 3, 3,5-4) */
    var passo = max < 5 ? 0.5 : 1, arr = function (v) { return Math.round(v / passo) * passo; };
    var num = function (v) { return String(v).replace(".", ","); };
    var su = [1, 2, 3, 4, 5].map(function (k) { return arr(max * k / 5); }), out = [], giu = 0;
    for (var k = 0; k < 5; k++) { var a = giu, b = Math.min(Math.max(su[k], a), max); out.push(a === b ? num(b) : num(a) + "-" + num(b)); giu = b + passo; }
    return out;
  }
  function pesi(t) {
    var p = conPhp(t) ? PESI.conPhp : PESI.senzaPhp, pers = (t.griglia && t.griglia.pesi) || null, out = {};
    Object.keys(p).forEach(function (k) { out[k] = pers && pers[k] != null ? Number(pers[k]) : p[k]; });
    if (!conPhp(t)) out.php = 0;
    return out;
  }
  /* righe della griglia: {macro, area, max, descrittori, fasce, tipo} */
  function griglia(t) {
    var w = pesi(t), q = (t.testo && t.testo.query) || [], isa = conIsa(t), righe = [];
    var riga = function (macro, area, chiave, max) { righe.push({ macro: macro, area: area, max: max, descrittori: DESCRITTORI[chiave], fasce: fasce(max), tipo: chiave }); };
    riga("Modello concettuale (E/R)", "Entità e attributi", "entita", w.entita);
    riga("Modello concettuale (E/R)", "Associazioni", "associazioni", w.associazioni);
    riga("Modello concettuale (E/R)", isa ? "Vincoli (cardinalità, ISA)" : "Vincoli (cardinalità)", isa ? "vincoliIsa" : "vincoli", w.vincoli);
    riga("Documentazione tecnica (entità e associazioni)", "", "documentazione", w.documentazione);
    riga("Modello relazionale (coerenza con il proprio E/R)", "", "relazionale", w.relazionale);
    righe.push({ macro: "Query SQL", area: "Descrizione (valutate sul proprio modello)", max: null, descrittori: DESCRITTORI.query, fasce: null, tipo: "query-descrizione" });
    distribuisci(w.query, q.length).forEach(function (m, i) {
      righe.push({ macro: "Query SQL", area: "Query " + (i + 1), max: m, descrittori: null, fasce: fasce(m), tipo: "query" });
    });
    if (conPhp(t)) riga("Pagina PHP", "", "php", w.php);
    var totale = righe.reduce(function (s, r) { return s + (r.max || 0); }, 0);
    return { righe: righe, totale: totale, pesi: w };
  }

  /* ------------------------------------------------------------------ nome dei file */
  var MESI = ["GEN", "FEB", "MAR", "APR", "MAG", "GIU", "LUG", "AGO", "SET", "OTT", "NOV", "DIC"];
  function nomeFile(t, opz) {
    opz = opz || {};
    var d = String(t.data || new Date().toISOString().slice(0, 10)), mese = MESI[Number(d.slice(5, 7)) - 1] || "", anno = d.slice(0, 4);
    var contesto = String(t.breve || t.titolo || "traccia").normalize("NFD").replace(/[̀-ͯ]/g, "")
      .replace(/[^A-Za-z0-9]+(.)?/g, function (_, c) { return c ? c.toUpperCase() : ""; }).replace(/^./, function (c) { return c.toLowerCase(); });
    var parti = [t.classe || "", mese, anno, contesto].filter(Boolean).join("-");
    return parti + (opz.variante ? "-" + opz.variante : "") + (opz.pdp ? "-PDP" : "") + (opz.estensione || ".docx");
  }

  /* ------------------------------------------------------------------ HTML per Moodle
     Eccezione allo stile delle pagine Moodle: la traccia deve avere lo stesso aspetto del Word della verifica,
     così gli studenti la ritrovano uguale. Niente colori, riquadri o stili: paragrafi, elenchi numerati e
     grassetto per le istruzioni, nello stesso ordine del Word (senza intestazione e griglia). */
  function htmlInline(s) {
    return pezzi(s).map(function (p) { var x = esc(p.t); if (p.c) x = "<code>" + x + "</code>"; if (p.u) x = "<u>" + x + "</u>"; return p.b ? "<strong>" + x + "</strong>" : p.i ? "<em>" + x + "</em>" : x; }).join("");
  }
  function html(t) {
    var x = t.testo || {}, v = vociPresentare(t), q = x.query || [], out = [];
    if (x.premessa) { out.push("<p><strong>Premessa</strong></p>"); paragrafi(x.premessa).forEach(function (p) { out.push("<p>" + htmlInline(p) + "</p>"); }); }
    out.push("<p><strong>" + esc(t.titolo) + "</strong></p>");
    paragrafi(x.realta).forEach(function (p) { out.push("<p>" + htmlInline(p) + "</p>"); });
    var testaPres = esame(t) ? "Il candidato, fatte le opportune ipotesi aggiuntive" + (x.requisiti_query ? " e " + FRASE_REQUISITI : "") + ", sviluppi:"
      : "Presentare" + (x.requisiti_query ? ", " + FRASE_REQUISITI : "") + ":";
    out.push("<p><strong>" + esc(testaPres) + "</strong></p>");
    out.push("<ol>" + v.map(function (it) { return "<li>" + esc(it.testo) + "</li>"; }).join("") + "</ol>");
    out.push("<p><strong>" + esc(FRASE_QUERY) + "</strong></p>");
    out.push("<ol>" + q.map(function (r) { return "<li>" + htmlInline(r.testo) + "</li>"; }).join("") + "</ol>");
    out.push("<p><strong>Scrivere le query SQL</strong> che rispondono a queste domande.</p>");
    if (conPhp(t)) {
      out.push("<p><strong>Pagina PHP</strong></p>");
      paragrafi(x.php.testo).forEach(function (p) { out.push("<p>" + htmlInline(p) + "</p>"); });
      if (x.php.connessione) out.push("<p>" + htmlInline(x.php.connessione) + "</p>");
    }
    out.push("<p><em>" + esc(FRASE_ORDINE) + "</em></p>");
    out.push("<p><strong>" + esc(FRASE_IPOTESI) + "</strong></p>");
    var cosa = "diagramma E/R, documentazione, modello relazionale e query" + (conPhp(t) ? ", più il codice della pagina PHP" : "");
    out.push("<p><strong>Consegna:</strong> se lavorate su carta, le foto dei fogli, dritte e leggibili, una per pagina; altrimenti un unico file Word completo, con " + esc(cosa) + ".</p>");
    return out.join("\n");
  }

  /* ------------------------------------------------------------------ Word (WordprocessingML) */
  var W = {
    run: function (p, opz) {
      opz = opz || {};
      var rpr = (p.c || opz.mono ? '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>' : "") + (p.b || opz.b ? "<w:b/>" : "") + (p.i || opz.i ? "<w:i/>" : "") +
        (p.u ? '<w:u w:val="single"/>' : "") + (opz.size ? '<w:sz w:val="' + opz.size + '"/><w:szCs w:val="' + opz.size + '"/>' : "");
      return "<w:r>" + (rpr ? "<w:rPr>" + rpr + "</w:rPr>" : "") + '<w:t xml:space="preserve">' + esc(p.t) + "</w:t></w:r>";
    },
    par: function (testo, opz) {
      opz = opz || {};
      var ppr = "";
      if (opz.stile) ppr += '<w:pStyle w:val="' + opz.stile + '"/>';
      if (opz.num) ppr += '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="' + opz.num + '"/></w:numPr>';
      if (opz.dopo != null || opz.prima != null || opz.interlinea) ppr += '<w:spacing w:before="' + (opz.prima || 0) + '" w:after="' + (opz.dopo != null ? opz.dopo : 120) + '"' + (opz.interlinea ? ' w:line="' + opz.interlinea + '" w:lineRule="auto"' : '') + '/>';
      if (opz.rientro) ppr += '<w:ind w:left="' + opz.rientro + '"/>';
      if (opz.centro) ppr += '<w:jc w:val="center"/>';
      if (opz.destra) ppr += '<w:jc w:val="right"/>';
      if (opz.giustifica) ppr += '<w:jc w:val="both"/>';
      if (opz.sez) ppr += opz.sez;
      var runs = (Array.isArray(testo) ? testo : pezzi(testo)).map(function (p) { return W.run(p, opz); }).join("");
      return "<w:p>" + (ppr ? "<w:pPr>" + ppr + "</w:pPr>" : "") + runs + "</w:p>";
    }
  };
  var SEZ_VERTICALE = '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="567" w:footer="567" w:gutter="0"/></w:sectPr>';
  var SEZ_ORIZZONTALE = '<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="360" w:footer="360" w:gutter="0"/></w:sectPr>';

  function tabellaGriglia(g) {
    var larg = [1300, 1500, 2400, 2400, 2400, 2400, 2400, 1000], tot = larg.reduce(function (a, b) { return a + b; }, 0);
    var bordo = '<w:tblBorders>' + ["top", "left", "bottom", "right", "insideH", "insideV"].map(function (b) { return "<w:" + b + ' w:val="single" w:sz="4" w:space="0" w:color="000000"/>'; }).join("") + "</w:tblBorders>";
    var cella = function (contenuto, opz) {
      opz = opz || {};
      var tcpr = '<w:tcW w:w="' + opz.w + '" w:type="dxa"/>' + (opz.span ? '<w:gridSpan w:val="' + opz.span + '"/>' : "") +
        (opz.vm === "inizio" ? '<w:vMerge w:val="restart"/>' : opz.vm === "segue" ? "<w:vMerge/>" : "") +
        (opz.sfondo ? '<w:shd w:val="clear" w:color="auto" w:fill="' + opz.sfondo + '"/>' : "") + '<w:vAlign w:val="' + (opz.va || "top") + '"/>';
      return "<w:tc><w:tcPr>" + tcpr + "</w:tcPr>" + (contenuto || W.par("", { dopo: 0, size: 16 })) + "</w:tc>";
    };
    var piccolo = function (s, o) { o = o || {}; return W.par(s, { dopo: 0, size: o.size || 14, b: o.b, centro: o.centro, destra: o.destra, interlinea: 220 }); };
    var righe = [];
    righe.push("<w:tr><w:trPr><w:tblHeader/></w:trPr>" +
      cella(piccolo("Macroarea", { b: true, centro: true }), { w: larg[0], vm: "inizio", sfondo: "E7E6E6", va: "center" }) +
      cella(piccolo("Area di valutazione", { b: true, centro: true }), { w: larg[1], vm: "inizio", sfondo: "E7E6E6", va: "center" }) +
      cella(piccolo("Livello (descrizione e punteggio)", { b: true, centro: true }), { w: larg[2] * 5, span: 5, sfondo: "E7E6E6" }) +
      cella(piccolo("Punteggio assegnato", { b: true, centro: true }), { w: larg[7], vm: "inizio", sfondo: "E7E6E6", va: "center" }) + "</w:tr>");
    righe.push("<w:tr><w:trPr><w:tblHeader/></w:trPr>" + cella("", { w: larg[0], vm: "segue", sfondo: "E7E6E6" }) + cella("", { w: larg[1], vm: "segue", sfondo: "E7E6E6" }) +
      LIVELLI.map(function (l, i) { return cella(piccolo(l, { b: true, centro: true }), { w: larg[2 + i], sfondo: "E7E6E6" }); }).join("") +
      cella("", { w: larg[7], vm: "segue", sfondo: "E7E6E6" }) + "</w:tr>");
    var prima = {};
    g.righe.forEach(function (r) {
      var nuova = !prima[r.macro]; prima[r.macro] = true;
      var gruppo = g.righe.filter(function (x) { return x.macro === r.macro; }).length;
      var celleNome;
      if (!r.area) celleNome = cella(piccolo(r.macro, { b: true, centro: true, size: 18 }), { w: larg[0] + larg[1], span: 2, va: "center" });
      else celleNome = cella(nuova ? piccolo(r.macro, { b: true, centro: true, size: 18 }) : "", { w: larg[0], vm: gruppo > 1 ? (nuova ? "inizio" : "segue") : null, va: "center" }) +
        cella(piccolo(r.area + (r.max ? " (" + r.max + ")" : ""), { b: true }), { w: larg[1], va: "center" });
      var livelli = [0, 1, 2, 3, 4].map(function (k) {
        var c = "";
        if (r.descrittori) c += piccolo(r.descrittori[k]);
        if (r.fasce) c += piccolo(r.fasce[k], { b: true, destra: true });
        return cella(c, { w: larg[2 + k], va: r.descrittori ? "top" : "center" });
      }).join("");
      var punteggio = cella(r.max ? piccolo("/ " + r.max, { destra: true }) : "", { w: larg[7], va: "bottom" });
      righe.push("<w:tr><w:trPr><w:cantSplit/></w:trPr>" + celleNome + livelli + punteggio + "</w:tr>");
    });
    righe.push("<w:tr>" + cella(piccolo("Totale", { b: true, size: 18 }), { w: tot - larg[7], span: 7, va: "center" }) +
      cella(piccolo("/ " + g.totale, { b: true, destra: true, size: 18 }), { w: larg[7] }) + "</w:tr>");
    return '<w:tbl><w:tblPr><w:tblW w:w="' + tot + '" w:type="dxa"/>' + bordo +
      '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="57" w:type="dxa"/><w:right w:w="57" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>' +
      larg.map(function (x) { return '<w:gridCol w:w="' + x + '"/>'; }).join("") + "</w:tblGrid>" + righe.join("") + "</w:tbl>";
  }

  function corpoWord(t, pdp) {
    var x = t.testo || {}, v = vociPresentare(t), q = x.query || [], b = [], numeri = 0;
    var nuovaLista = function () { numeri += 1; return numeri; };
    var intest = (t.verifica && t.verifica.intestazione) || (String(t.classe || "").charAt(0) + " SIA Verifica Modello E/R").trim();
    b.push(W.par(intest, { centro: true, dopo: 120 }));
    b.push(W.par("Nome ____________________________   Data ______________   Classe ____", { centro: true, dopo: 240 }));
    if (x.premessa) { b.push(W.par("**Premessa**", { dopo: 60 })); paragrafi(x.premessa).forEach(function (p) { b.push(W.par(p, { giustifica: true })); }); }
    b.push(W.par([{ t: t.titolo || "", b: true }], { prima: 120, dopo: 120 }));
    paragrafi(x.realta).forEach(function (p) { b.push(W.par(p, { giustifica: true })); });
    var testaPres = esame(t) ? "Il candidato, fatte le opportune ipotesi aggiuntive" + (x.requisiti_query ? " e " + FRASE_REQUISITI : "") + ", sviluppi:"
      : "Presentare" + (x.requisiti_query ? ", " + FRASE_REQUISITI : "") + ":";
    b.push(W.par([{ t: testaPres, b: true }], { prima: 120, dopo: 60 }));
    var n1 = nuovaLista();
    v.forEach(function (it) {
      b.push(W.par(it.testo, { num: n1, dopo: 40 }));
      var rid = riduzione(t, "presentare." + it.chiave, pdp);
      if (rid) b.push(W.par([{ t: rid, b: true }], { rientro: 720, dopo: 40 }));
    });
    b.push(W.par([{ t: FRASE_QUERY, b: true }], { prima: 160, dopo: 60 }));
    var n2 = nuovaLista();
    q.forEach(function (r, i) {
      b.push(W.par(r.testo, { num: n2, dopo: 40 }));
      var rid = riduzione(t, "query." + (i + 1), pdp);
      if (rid) b.push(W.par([{ t: rid, b: true }], { rientro: 720, dopo: 40 }));
    });
    b.push(W.par([{ t: "Scrivere le query SQL", b: true }, { t: " che rispondono a queste domande." }], { prima: 120 }));
    if (conPhp(t)) {
      b.push(W.par([{ t: "Pagina PHP", b: true }], { prima: 160, dopo: 60 }));
      paragrafi(x.php.testo).forEach(function (p) { b.push(W.par(p, { giustifica: true })); });
      if (x.php.connessione) b.push(W.par(x.php.connessione));
      var rid = riduzione(t, "php", pdp);
      if (rid) b.push(W.par([{ t: rid, b: true }], { dopo: 60 }));
    }
    b.push(W.par([{ t: FRASE_ORDINE, i: true }], { prima: 160 }));
    b.push(W.par([{ t: FRASE_IPOTESI, b: true }], { giustifica: true }));
    if (pdp) {
      b.push(W.par([{ t: "Per la verifica si ricordano le colonne delle tabelle di ", i: true }, { t: "documentazione", i: true, b: true }, { t: ".", i: true }], { prima: 160, dopo: 40 }));
      b.push(W.par([{ t: "Entità", i: true, b: true }, { t: ": nome, sinonimi, descrizione, attributo, tipo di dato, vincoli", i: true }], { dopo: 40 }));
      b.push(W.par([{ t: "Associazioni", i: true, b: true }, { t: ": nome, descrizione, tipo di associazione, entità collegate, attributo, tipo di dato, vincoli", i: true }]));
    }
    var conGriglia = !(t.verifica && t.verifica.griglia === false);
    if (conGriglia) {
      b.push(W.par("", { dopo: 0, sez: SEZ_VERTICALE }));
      b.push(W.par("La correzione della prova verrà effettuata con la seguente griglia di valutazione" +
        (pdp ? " e tenendo conto dei criteri di valutazione personalizzata previsti dal PDP." : "."), { dopo: 120 }));
      b.push(tabellaGriglia(griglia(t)));
      b.push(W.par("Per ottenere il voto si divide il punteggio per 10 e si arrotonda al mezzo voto più vicino.", { prima: 120 }));
      return { corpo: b.join(""), sezFinale: SEZ_ORIZZONTALE, liste: numeri };
    }
    return { corpo: b.join(""), sezFinale: SEZ_VERTICALE, liste: numeri };
  }

  var XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n';
  var NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"';
  function fileDocx(t, opz) {
    opz = opz || {};
    var c = corpoWord(t, !!opz.pdp);
    return pacchetto(c.corpo, c.sezFinale, c.liste, t.titolo, null);
  }
  function pacchetto(corpo, sezFinale, liste, titolo, png) {
    var c = { corpo: corpo, sezFinale: sezFinale, liste: liste };
    var nums = "";
    for (var i = 1; i <= c.liste; i++) nums += '<w:num w:numId="' + i + '"><w:abstractNumId w:val="0"/><w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>';
    var out = {
      "[Content_Types].xml": XML + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>' + (png ? '<Default Extension="png" ContentType="image/png"/>' : "") +
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>' +
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>' +
        '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>' +
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>',
      "_rels/.rels": XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>' +
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>',
      "docProps/core.xml": XML + '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>' + esc(titolo) + "</dc:title><dc:creator>Moodle: quiz generator</dc:creator></cp:coreProperties>",
      "word/_rels/document.xml.rels": XML + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' +
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>' +
        (png ? '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/diagramma.png"/>' : "") + "</Relationships>",
      "word/styles.xml": XML + "<w:styles " + NS + '><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial" w:cs="Arial"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="it-IT"/></w:rPr></w:rPrDefault>' +
        '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>' +
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>' +
        '<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/><w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style></w:styles>',
      "word/numbering.xml": XML + "<w:numbering " + NS + '><w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>' + nums + "</w:numbering>",
      "word/document.xml": XML + "<w:document " + NS + "><w:body>" + c.corpo + c.sezFinale + "</w:body></w:document>"
    };
    if (png) out["word/media/diagramma.png"] = png.byte;
    return out;
  }

  /* ------------------------------------------------------------------ soluzione (Word e HTML)
     Dalla soluzione salvata nella traccia (formato.md: diagramma PNG, documentazione e schema in Markdown,
     query): traccia, ipotesi, diagramma, documentazione, schema relazionale, query, come la soluzione
     completa di diagrammi-er. */
  function mdBlocchi(testo) {
    var righe = String(testo || "").split("\n"), out = [], i = 0;
    var celle = function (x) { return x.trim().replace(/^\||\|$/g, "").split("|").map(function (c) { return c.trim(); }); };
    while (i < righe.length) {
      var r = righe[i];
      if (/^\s*\|/.test(r)) {
        var tab = []; while (i < righe.length && /^\s*\|/.test(righe[i])) { tab.push(righe[i]); i++; }
        out.push({ tipo: "tabella", testa: celle(tab[0]), righe: tab.slice(2).map(celle) }); continue;
      }
      var h = /^#{1,4}\s+(.*)$/.exec(r) || /^\*\*([^*]+)\*\*\s*$/.exec(r);
      if (h && !/\(/.test(h[1])) { out.push({ tipo: "titolo", testo: h[1] }); i++; continue; }
      if (/^\s*[-*]\s/.test(r)) {
        var v = []; while (i < righe.length && /^\s*[-*]\s/.test(righe[i])) { v.push(righe[i].replace(/^\s*[-*]\s/, "")); i++; }
        out.push({ tipo: "elenco", voci: v }); continue;
      }
      if (r.trim()) out.push({ tipo: "p", testo: r.trim() });
      i++;
    }
    return out;
  }
  /* la documentazione di diagrammi-er comincia con le ipotesi: si separano, perché nella soluzione vengono prima */
  function dividiIpotesi(blocchi) {
    var ip = [], resto = [], dentro = false;
    blocchi.forEach(function (b) {
      if (b.tipo === "titolo") dentro = /^ipotesi/i.test(b.testo);
      if (dentro) { if (b.tipo === "elenco") ip = ip.concat(b.voci); else if (b.tipo === "p") ip.push(b.testo); }
      else resto.push(b);
    });
    return { ipotesi: ip, resto: resto };
  }
  function datiSoluzione(t) {
    var s = t.soluzione || {}, d = dividiIpotesi(mdBlocchi(s.documentazione));
    var ipotesi = (s.ipotesi || []).concat(d.ipotesi.filter(function (x) { return (s.ipotesi || []).indexOf(x) < 0; }));
    return { ipotesi: ipotesi, documentazione: d.resto, schema: mdBlocchi(s.schema), query: s.query || [] };
  }
  function dimPng(b) {
    if (!b || b.length < 24) return null;
    var u = function (o) { return ((b[o] << 24) >>> 0) + (b[o + 1] << 16) + (b[o + 2] << 8) + b[o + 3]; };
    return { w: u(16), h: u(20) };
  }
  function immagineWord(png, maxW, maxH) {
    var d = dimPng(png) || { w: 800, h: 400 }, emu = 914400 / 96;
    var sc = Math.min(1, maxW / (d.w * emu), maxH / (d.h * emu)), cx = Math.round(d.w * emu * sc), cy = Math.round(d.h * emu * sc);
    return '<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="' + cx + '" cy="' + cy + '"/><wp:docPr id="1" name="Diagramma E/R"/>' +
      '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">' +
      '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="1" name="diagramma.png"/><pic:cNvPicPr/></pic:nvPicPr>' +
      '<pic:blipFill><a:blip r:embed="rId3"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="' + cx + '" cy="' + cy + '"/></a:xfrm>' +
      '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>';
  }
  function tabellaWord(testa, righe, larghezza) {
    var n = testa.length, w = Math.floor(larghezza / n);
    var bordo = '<w:tblBorders>' + ["top", "left", "bottom", "right", "insideH", "insideV"].map(function (b) { return "<w:" + b + ' w:val="single" w:sz="4" w:space="0" w:color="808080"/>'; }).join("") + "</w:tblBorders>";
    var cella = function (x, intest) {
      return '<w:tc><w:tcPr><w:tcW w:w="' + w + '" w:type="dxa"/>' + (intest ? '<w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>' : "") + "</w:tcPr>" + W.par(x, { dopo: 0, size: 16, b: intest }) + "</w:tc>";
    };
    return '<w:tbl><w:tblPr><w:tblW w:w="' + w * n + '" w:type="dxa"/>' + bordo + '<w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>' +
      testa.map(function () { return '<w:gridCol w:w="' + w + '"/>'; }).join("") + "</w:tblGrid>" +
      '<w:tr><w:trPr><w:tblHeader/></w:trPr>' + testa.map(function (x) { return cella(x, true); }).join("") + "</w:tr>" +
      righe.map(function (r) { return "<w:tr><w:trPr><w:cantSplit/></w:trPr>" + testa.map(function (_, k) { return cella(r[k] || "", false); }).join("") + "</w:tr>"; }).join("") + "</w:tbl>";
  }
  function blocchiWord(bl, larghezza) {
    return bl.map(function (b) {
      if (b.tipo === "tabella") return tabellaWord(b.testa, b.righe, larghezza) + W.par("", { dopo: 60 });
      if (b.tipo === "titolo") return W.par([{ t: b.testo.replace(/\*\*/g, ""), b: true }], { prima: 120, dopo: 60 });
      if (b.tipo === "elenco") return b.voci.map(function (v) { return W.par([{ t: "• " }].concat(pezzi(v)), { rientro: 360, dopo: 40 }); }).join("");
      return W.par(b.testo, { dopo: 80 });
    }).join("");
  }
  var titoloSez = function (s) { return W.par([{ t: s, b: true }], { prima: 240, dopo: 120, size: 28 }); };
  function fileDocxSoluzione(t, png) {
    var ds = datiSoluzione(t), x = t.testo || {}, b = [];
    b.push(W.par([{ t: "Soluzione: " + (t.titolo || ""), b: true }], { size: 32, dopo: 200 }));
    b.push(titoloSez("Traccia"));
    paragrafi(x.realta).forEach(function (p) { b.push(W.par(p, { giustifica: true })); });
    if (ds.ipotesi.length) { b.push(titoloSez("Ipotesi aggiuntive")); ds.ipotesi.forEach(function (v) { b.push(W.par([{ t: "• " }].concat(pezzi(v)), { rientro: 360, dopo: 40 })); }); }
    /* diagramma e documentazione su pagine orizzontali: sono larghi */
    b.push(W.par("", { dopo: 0, sez: SEZ_VERTICALE }));
    b.push(titoloSez("Diagramma E/R"));
    if (png) b.push(immagineWord(png, 15398 * 635, 8600 * 635));
    else b.push(W.par([{ t: "(diagramma non disponibile)", i: true }]));
    if (ds.documentazione.length) { b.push(titoloSez("Documentazione")); b.push(blocchiWord(ds.documentazione, 15398)); }
    b.push(W.par("", { dopo: 0, sez: SEZ_ORIZZONTALE }));
    b.push(titoloSez("Schema relazionale"));
    b.push(blocchiWord(ds.schema, 9638));
    if (ds.query.length) {
      b.push(titoloSez("Query SQL"));
      ds.query.forEach(function (q, i) {
        b.push(W.par([{ t: (i + 1) + ". ", b: true }].concat(pezzi(q.richiesta)), { prima: 120, dopo: 60 }));
        String(q.sql || "").split("\n").forEach(function (r) { b.push(W.par([{ t: r.replace(/\t/g, "    ") || " " }], { mono: true, size: 18, dopo: 0, rientro: 360 })); });
      });
    }
    return pacchetto(b.join(""), SEZ_VERTICALE, 0, "Soluzione: " + (t.titolo || ""), png ? { byte: png } : null);
  }
  function docxSoluzione(t, png) { return zip(fileDocxSoluzione(t, png)); }
  function base64(b) {
    var s = "", tab = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    for (var i = 0; i < b.length; i += 3) {
      var n = (b[i] << 16) | ((b[i + 1] || 0) << 8) | (b[i + 2] || 0);
      s += tab[(n >> 18) & 63] + tab[(n >> 12) & 63] + (i + 1 < b.length ? tab[(n >> 6) & 63] : "=") + (i + 2 < b.length ? tab[n & 63] : "=");
    }
    return s;
  }
  /* Moodle toglie i <style>: nel frammento per Moodle gli stili delle tabelle stanno negli attributi */
  var ST_MOODLE = { tab: ' style="overflow-x:auto"', table: ' style="border-collapse:collapse;width:100%"', cella: ' style="border:1px solid #999;padding:4px 7px;text-align:left;vertical-align:top"' };
  function htmlBlocchi(bl, mo, h) {
    var st = mo ? ST_MOODLE : { tab: ' class="tab"', table: "", cella: "" };
    return bl.map(function (b) {
      if (b.tipo === "tabella") return "<div" + st.tab + "><table" + st.table + "><thead><tr>" + b.testa.map(function (c) { return "<th" + st.cella + ">" + htmlInline(c) + "</th>"; }).join("") + "</tr></thead><tbody>" +
        b.righe.map(function (r) { return "<tr>" + b.testa.map(function (_, k) { return "<td" + st.cella + ">" + htmlInline(r[k] || "") + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>";
      if (b.tipo === "titolo") return "<" + h + ">" + htmlInline(b.testo.replace(/\*\*/g, "")) + "</" + h + ">";
      if (b.tipo === "elenco") return "<ul>" + b.voci.map(function (v) { return "<li>" + htmlInline(v) + "</li>"; }).join("") + "</ul>";
      return "<p>" + htmlInline(b.testo) + "</p>";
    }).join("\n");
  }
  /* il corpo della soluzione; mo = frammento per Moodle (titoli h3/h4, stili negli attributi) */
  function corpoSoluzione(t, png, mo) {
    var ds = datiSoluzione(t), x = t.testo || {}, o = [], h2 = mo ? "h3" : "h2", h3 = mo ? "h4" : "h3";
    var tit = function (s) { return "<" + h2 + ">" + s + "</" + h2 + ">"; };
    o.push(tit("Traccia") + paragrafi(x.realta).map(function (p) { return "<p>" + htmlInline(p) + "</p>"; }).join(""));
    if (ds.ipotesi.length) o.push(tit("Ipotesi aggiuntive") + "<ul>" + ds.ipotesi.map(function (v) { return "<li>" + htmlInline(v) + "</li>"; }).join("") + "</ul>");
    o.push(tit("Diagramma E/R") + (png ? '<p><img alt="Diagramma E/R" src="data:image/png;base64,' + base64(png) + '"' + (mo ? ' style="max-width:100%;height:auto"' : "") + "></p>" : "<p><em>(diagramma non disponibile)</em></p>"));
    if (ds.documentazione.length) o.push(tit("Documentazione") + htmlBlocchi(ds.documentazione, mo, h3));
    o.push(tit("Schema relazionale") + htmlBlocchi(ds.schema, mo, h3));
    if (ds.query.length) o.push(tit("Query SQL") + ds.query.map(function (q, i) { return "<p><strong>" + (i + 1) + ".</strong> " + htmlInline(q.richiesta) + "</p><pre>" + esc(q.sql) + "</pre>"; }).join(""));
    return o.join("\n");
  }
  function htmlSoluzione(t, png) {
    var o = [];
    o.push('<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Soluzione: ' + esc(t.titolo) + "</title>");
    o.push("<style>body{font:15px/1.5 Arial,Helvetica,sans-serif;color:#222;max-width:1100px;margin:24px auto;padding:0 16px}h1{font-size:1.5rem}h2{font-size:1.15rem;margin-top:28px;border-bottom:1px solid #ccc;padding-bottom:4px}h3{font-size:1rem;margin:18px 0 6px}" +
      ".tab{overflow-x:auto}table{border-collapse:collapse;font-size:.85rem;width:100%}th,td{border:1px solid #999;padding:4px 7px;text-align:left;vertical-align:top}th{background:#eee}" +
      "img{max-width:100%;height:auto}pre{background:#f4f4f4;border:1px solid #ddd;padding:10px;overflow-x:auto;font:13px/1.45 Consolas,monospace}@media print{h2{break-after:avoid}pre,tr{break-inside:avoid}}</style></head><body>");
    o.push("<h1>Soluzione: " + esc(t.titolo) + "</h1>");
    o.push(corpoSoluzione(t, png, false));
    o.push("</body></html>");
    return o.join("\n");
  }
  /* frammento da incollare in Moodle (codice sorgente dell'editor): niente <style>, diagramma come data URI */
  function htmlSoluzioneMoodle(t, png) { return corpoSoluzione(t, png, true); }

  /* ------------------------------------------------------------------ zip senza compressione */
  var CRC = (function () { var t = []; for (var n = 0; n < 256; n++) { var c = n; for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t.push(c >>> 0); } return t; })();
  function crc32(b) { var c = 0xFFFFFFFF; for (var i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 0xFF] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; }
  function zip(files) {
    var enc = new TextEncoder(), parti = [], centrale = [], off = 0;
    var u16 = function (v) { return [v & 255, (v >>> 8) & 255]; }, u32 = function (v) { return [v & 255, (v >>> 8) & 255, (v >>> 16) & 255, (v >>> 24) & 255]; };
    Object.keys(files).forEach(function (nome) {
      var dati = typeof files[nome] === "string" ? enc.encode(files[nome]) : files[nome], n = enc.encode(nome), c = crc32(dati);
      var comune = [].concat(u16(20), u16(0x0800), u16(0), u16(0), u16(0x21), u32(c), u32(dati.length), u32(dati.length), u16(n.length), u16(0));
      var loc = new Uint8Array([].concat(u32(0x04034b50), comune));
      parti.push(loc, n, dati);
      centrale.push(new Uint8Array([].concat(u32(0x02014b50), u16(20), comune, u16(0), u16(0), u16(0), u32(0), u32(off))), n);
      off += loc.length + n.length + dati.length;
    });
    var dimC = centrale.reduce(function (s, a) { return s + a.length; }, 0), nf = Object.keys(files).length;
    var fine = new Uint8Array([].concat(u32(0x06054b50), u16(0), u16(0), u16(nf), u16(nf), u32(dimC), u32(off), u16(0)));
    var tutte = parti.concat(centrale, [fine]), tot = tutte.reduce(function (s, a) { return s + a.length; }, 0), out = new Uint8Array(tot), p = 0;
    tutte.forEach(function (a) { out.set(a, p); p += a.length; });
    return out;
  }
  function docx(t, opz) { return zip(fileDocx(t, opz)); }

  /* ------------------------------------------------------------------ controlli */
  function controlla(t) {
    var err = [], avv = [], x = t.testo || {};
    if (!t.titolo) err.push("manca il titolo del contesto");
    if (!paragrafi(x.realta).length) err.push("manca il testo della realtà");
    if (!(x.query || []).length) err.push("mancano le query (ci sono sempre)");
    (x.query || []).forEach(function (r, i) { if (!r.requisito) avv.push("query " + (i + 1) + ": manca il requisito che verifica (note per il docente)"); });
    var g = griglia(t);
    if (g.totale !== 100) avv.push("la griglia fa " + g.totale + " punti invece di 100: controlla i pesi");
    if (t.pdp && t.pdp.riduzioni) Object.keys(t.pdp.riduzioni).forEach(function (k) {
      if (!/^(presentare\.(er|documentazione|relazionale|sql_tabelle)|query\.\d+|php)$/.test(k)) avv.push("riduzione PDP con una chiave sconosciuta: " + k);
    });
    return { errori: err, avvisi: avv };
  }

  return { html: html, docx: docx, docxSoluzione: docxSoluzione, htmlSoluzione: htmlSoluzione, htmlSoluzioneMoodle: htmlSoluzioneMoodle, fileDocx: fileDocx, griglia: griglia, fasce: fasce, distribuisci: distribuisci, nomeFile: nomeFile, controlla: controlla, pezzi: pezzi };
});

/* ------------------------------------------------------------------ uso da riga di comando */
if (typeof require !== "undefined" && typeof module !== "undefined" && require.main === module) {
  var fs = require("fs"), U = module.exports, a = process.argv.slice(2);
  if (!a.length) { console.error("uso: node uscite_traccia.js TRACCIA.json [--word F.docx] [--pdp F.docx] [--html F.html] [--griglia] [--soluzione-word F.docx] [--soluzione-html F.html] [--png DIAGRAMMA.png]"); process.exit(2); }
  var t = JSON.parse(fs.readFileSync(a[0], "utf8")), opt = function (k) { var i = a.indexOf(k); return i >= 0 ? (a[i + 1] && !/^--/.test(a[i + 1]) ? a[i + 1] : true) : null; };
  var c = U.controlla(t);
  c.errori.forEach(function (e) { console.log("ERRORE  " + e); });
  c.avvisi.forEach(function (e) { console.log("AVVISO  " + e); });
  if (c.errori.length) process.exit(1);
  var w = opt("--word"), p = opt("--pdp"), h = opt("--html");
  if (w) { var fw = w === true ? U.nomeFile(t) : w; fs.writeFileSync(fw, U.docx(t)); console.log("Word:     " + fw); }
  if (p) { var fp = p === true ? U.nomeFile(t, { pdp: true }) : p; fs.writeFileSync(fp, U.docx(t, { pdp: true })); console.log("Word PDP: " + fp); }
  if (h) { var fh = h === true ? U.nomeFile(t, { estensione: ".html" }) : h; fs.writeFileSync(fh, U.html(t)); console.log("HTML:     " + fh); }
  var sw = opt("--soluzione-word"), sh = opt("--soluzione-html"), png = opt("--png"), pb = png && png !== true ? fs.readFileSync(png) : null;
  if ((sw || sh) && !t.soluzione) { console.log("ERRORE  la traccia non ha ancora la soluzione"); process.exit(1); }
  if (sw) { var fs1 = sw === true ? "Soluzione - " + U.nomeFile(t) : sw; fs.writeFileSync(fs1, U.docxSoluzione(t, pb && new Uint8Array(pb))); console.log("Soluzione Word: " + fs1); }
  if (sh) { var fs2 = sh === true ? "Soluzione - " + U.nomeFile(t, { estensione: ".html" }) : sh; fs.writeFileSync(fs2, U.htmlSoluzione(t, pb && new Uint8Array(pb))); console.log("Soluzione HTML: " + fs2); }
  if (opt("--griglia")) {
    var g = U.griglia(t);
    g.righe.forEach(function (r) { if (r.max) console.log((r.area || r.macro).padEnd(32) + String(r.max).padStart(4) + "   " + r.fasce.join(" | ")); });
    console.log("Totale".padEnd(32) + String(g.totale).padStart(4));
  }
}
