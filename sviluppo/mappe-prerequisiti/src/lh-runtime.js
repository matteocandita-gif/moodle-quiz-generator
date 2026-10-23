/* Gerarchie di apprendimento - motore di impaginazione e disegno (nessuna dipendenza esterna). */
(function (root) {
  'use strict';
  if (root.LH && root.LH.version) { return; }

  var SVGNS = 'http://www.w3.org/2000/svg';
  var NODE_H = 46, RANK_SEP = 46, NODE_SEP = 14, DUMMY_W = 6, MARGIN = 8, PAD_X = 24;

  var COLORS = {
    fill: '#ffffff', stroke: '#a9a79e', text: '#1f1e1b', sub: '#5f5e5a',
    lockFill: '#f5f4f0', lockStroke: '#cfcdc4', lockText: '#8a887f',
    ready: '#2f6fd0',
    doneFill: '#e3f0d6', doneStroke: '#5c9a2a', doneText: '#2d5410',
    edge: '#c2c0b6', edgeOpen: '#2f6fd0', edgeDone: '#86b85a', hover: '#d4861a',
    selected: '#7a4fd0'
  };

  function tipoLeggere(n) { return n.tipo === 'leggere'; }

  /* ---------- misura del testo ---------- */
  var measureCtx = null;
  function makeMeasure(fontFamily) {
    try {
      if (!measureCtx) { measureCtx = document.createElement('canvas').getContext('2d'); }
    } catch (e) { measureCtx = null; }
    return function (text, size, weight) {
      if (measureCtx) {
        measureCtx.font = (weight || 400) + ' ' + size + 'px ' + (fontFamily || 'sans-serif');
        return measureCtx.measureText(text).width;
      }
      return text.length * size * (weight >= 600 ? 0.6 : 0.55);
    };
  }

  /* ---------- pulizia del grafo ---------- */
  function normalize(graph) {
    var nodes = (graph && graph.nodi) || [];
    var byId = {}, list = [];
    nodes.forEach(function (n) {
      if (!n || !n.id || byId[n.id]) { return; }
      var c = { id: String(n.id), titolo: n.titolo || n.id, sotto: n.sotto || '', tipo: n.tipo === 'leggere' ? 'leggere' : 'scrivere', pre: [] };
      byId[c.id] = c; list.push(c);
    });
    nodes.forEach(function (n) {
      if (!n || !byId[n.id]) { return; }
      var seen = {};
      byId[n.id].pre = (n.pre || []).map(String).filter(function (p) {
        if (!byId[p] || p === String(n.id) || seen[p]) { return false; }
        seen[p] = true; return true;
      });
    });
    return { list: list, byId: byId };
  }

  /* Rileva i cicli: restituisce l'ordine topologico e gli archi da ignorare. */
  function topo(list, byId) {
    var indeg = {}, suc = {}, order = [], queue = [];
    list.forEach(function (n) { indeg[n.id] = n.pre.length; suc[n.id] = []; });
    list.forEach(function (n) { n.pre.forEach(function (p) { suc[p].push(n.id); }); });
    list.forEach(function (n) { if (!indeg[n.id]) { queue.push(n.id); } });
    while (queue.length) {
      var v = queue.shift(); order.push(v);
      suc[v].forEach(function (w) { if (--indeg[w] === 0) { queue.push(w); } });
    }
    var placed = {}; order.forEach(function (v) { placed[v] = true; });
    var cyclic = [];
    list.forEach(function (n) {
      if (!placed[n.id]) {
        cyclic.push(n.id);
        n.pre = n.pre.filter(function (p) { return placed[p]; });
        order.push(n.id); placed[n.id] = true;
      }
    });
    return { order: order, cyclic: cyclic };
  }

  /* Vero se aggiungere l'arco p -> v creerebbe un ciclo. */
  function createsCycle(graph, p, v) {
    if (p === v) { return true; }
    var g = normalize(graph), stack = [p], seen = {};
    while (stack.length) {
      var x = stack.pop();
      if (x === v) { return true; }
      if (seen[x] || !g.byId[x]) { continue; }
      seen[x] = true;
      g.byId[x].pre.forEach(function (q) { stack.push(q); });
    }
    return false;
  }

  /* ---------- impaginazione a strati ---------- */
  function layout(graph, measure, opts) {
    var g = normalize(graph), list = g.list, byId = g.byId;
    var tp = topo(list, byId), order = tp.order;
    var suc = {};
    list.forEach(function (n) { suc[n.id] = []; });
    list.forEach(function (n) { n.pre.forEach(function (p) { suc[p].push(n.id); }); });

    // 1. livelli: catena più lunga, poi ogni voce si avvicina al lato con più collegamenti
    var rank = {};
    order.forEach(function (v) {
      var pre = byId[v].pre;
      rank[v] = pre.length ? 1 + Math.max.apply(null, pre.map(function (p) { return rank[p]; })) : 0;
    });
    for (var it = 0; it < 6; it++) {
      for (var i = order.length - 1; i >= 0; i--) {
        var v = order[i], pre = byId[v].pre, sc = suc[v];
        var lo = pre.length ? 1 + Math.max.apply(null, pre.map(function (p) { return rank[p]; })) : 0;
        var hi = sc.length ? Math.min.apply(null, sc.map(function (s) { return rank[s]; })) - 1 : Infinity;
        if (sc.length > pre.length && hi !== Infinity) { rank[v] = hi; }
        else if (pre.length > sc.length || hi === Infinity) { rank[v] = lo; }
        else { rank[v] = Math.max(lo, Math.min(rank[v], hi)); }
      }
    }
    var minR = Infinity, maxR = 0;
    order.forEach(function (v) { minR = Math.min(minR, rank[v]); });
    order.forEach(function (v) { rank[v] -= minR; maxR = Math.max(maxR, rank[v]); });
    if (!order.length) { maxR = -1; }

    // 1b. livelli troppo larghi: sposto le voci che hanno margine verso livelli più liberi
    var widthOf = {};
    order.forEach(function (v) {
      var n = byId[v];
      widthOf[v] = Math.ceil(Math.max(Math.max(measure(n.titolo, 13, 600), measure(n.sotto, 11, 400)) + PAD_X, 70));
    });
    function rankWidths() {
      var w = [];
      for (var r = 0; r <= maxR; r++) { w.push(0); }
      var cnt = w.map(function () { return 0; });
      order.forEach(function (v) { w[rank[v]] += widthOf[v]; cnt[rank[v]]++; });
      order.forEach(function (v) {
        byId[v].pre.forEach(function (p) {
          for (var r = rank[p] + 1; r < rank[v]; r++) { w[r] += DUMMY_W; cnt[r]++; }
        });
      });
      return w.map(function (x, r) { return x + Math.max(0, cnt[r] - 1) * NODE_SEP; });
    }
    function edgeLen() {
      var s = 0;
      order.forEach(function (v) { byId[v].pre.forEach(function (p) { s += rank[v] - rank[p]; }); });
      return s;
    }
    var target = (opts && opts.maxWidth) || 760;
    function score() {
      var ws = rankWidths(), sc = 0;
      ws.forEach(function (w) { if (w > target) { sc += (w - target) * (w - target); } });
      return sc + edgeLen() * 50;
    }
    var cur = score();
    for (var guard = 0; guard < 200; guard++) {
      var bestMove = null, bestScore = cur;
      order.forEach(function (v) {
        var pre = byId[v].pre, sc = suc[v];
        var lo = pre.length ? 1 + Math.max.apply(null, pre.map(function (p) { return rank[p]; })) : 0;
        var hi = sc.length ? Math.min.apply(null, sc.map(function (s) { return rank[s]; })) - 1 : maxR;
        for (var r = lo; r <= hi; r++) {
          if (r === rank[v]) { continue; }
          var old = rank[v]; rank[v] = r;
          var m = score();
          rank[v] = old;
          if (m < bestScore - 1e-6) { bestScore = m; bestMove = [v, r]; }
        }
      });
      if (!bestMove) { break; }
      rank[bestMove[0]] = bestMove[1]; cur = bestScore;
    }

    // 2. nodi fittizi per gli archi lunghi
    var L = {}; // chiave -> info
    var layers = [];
    for (var r = 0; r <= maxR; r++) { layers.push([]); }
    order.forEach(function (v) {
      L[v] = { key: v, real: true, rank: rank[v], w: widthOf[v], up: [], down: [] };
      layers[rank[v]].push(v);
    });
    var edges = [], dcount = 0;
    order.forEach(function (v) {
      byId[v].pre.forEach(function (p) {
        var chain = [p], prev = p;
        for (var rr = rank[p] + 1; rr < rank[v]; rr++) {
          var key = '\u0000d' + (dcount++);
          L[key] = { key: key, real: false, rank: rr, w: DUMMY_W, up: [], down: [] };
          layers[rr].push(key);
          L[prev].down.push(key); L[key].up.push(prev);
          chain.push(key); prev = key;
        }
        L[prev].down.push(v); L[v].up.push(prev);
        chain.push(v);
        edges.push({ from: p, to: v, chain: chain });
      });
    });

    // 3. ordine dentro i livelli: baricentri con passate alterne, si tiene il migliore
    function idx(layer) { var m = {}; layer.forEach(function (k, i) { m[k] = i; }); return m; }
    function crossings(ls) {
      var total = 0;
      for (var r = 0; r < ls.length - 1; r++) {
        var pos = idx(ls[r + 1]), segs = [];
        ls[r].forEach(function (k, i) { L[k].down.forEach(function (d) { segs.push([i, pos[d]]); }); });
        for (var a = 0; a < segs.length; a++) {
          for (var b = a + 1; b < segs.length; b++) {
            if ((segs[a][0] - segs[b][0]) * (segs[a][1] - segs[b][1]) < 0) { total++; }
          }
        }
      }
      return total;
    }
    function sweep(ls, down) {
      var start = down ? 1 : ls.length - 2, end = down ? ls.length : -1, step = down ? 1 : -1;
      for (var r = start; r !== end; r += step) {
        var ref = idx(ls[r - step]);
        var cur = idx(ls[r]);
        var bc = {};
        ls[r].forEach(function (k) {
          var nb = down ? L[k].up : L[k].down;
          if (nb.length) {
            var s = 0; nb.forEach(function (x) { s += ref[x]; });
            bc[k] = s / nb.length;
          } else { bc[k] = cur[k]; }
        });
        ls[r] = ls[r].slice().sort(function (a, b) { return (bc[a] - bc[b]) || (cur[a] - cur[b]); });
      }
    }
    var best = layers.map(function (l) { return l.slice(); }), bestC = crossings(best);
    var work = layers.map(function (l) { return l.slice(); });
    for (var s = 0; s < 24 && bestC > 0; s++) {
      sweep(work, s % 2 === 0);
      var c = crossings(work);
      if (c < bestC) { bestC = c; best = work.map(function (l) { return l.slice(); }); }
    }
    layers = best;

    // 4. coordinate orizzontali: allineamento ai vicini rispettando ordine e distanze (regressione isotonica)
    var X = {};
    function gap(a, b) { return (L[a].w + L[b].w) / 2 + (L[a].real || L[b].real ? NODE_SEP : 4); }
    var FRAME = 0;
    layers.forEach(function (layer) {
      var x = 0;
      layer.forEach(function (k, i) {
        if (i > 0) { x += gap(layer[i - 1], k); }
        X[k] = x;
      });
      if (layer.length) { FRAME = Math.max(FRAME, x + (L[layer[0]].w + L[layer[layer.length - 1]].w) / 2); }
      var off = x / 2; layer.forEach(function (k) { X[k] -= off; });
    });
    FRAME = FRAME * 1.06 + 20;
    function place(layer, desired, weight) {
      // y_i = x_i - c_i deve essere non decrescente; minimizza la distanza pesata da desired
      var n = layer.length, c = [], target = [];
      for (var i = 0; i < n; i++) {
        c[i] = i === 0 ? 0 : c[i - 1] + gap(layer[i - 1], layer[i]);
        target[i] = desired[i] - c[i];
      }
      var blocks = [];
      for (i = 0; i < n; i++) {
        blocks.push({ v: target[i], w: weight[i], n: 1 });
        while (blocks.length > 1 && blocks[blocks.length - 2].v > blocks[blocks.length - 1].v) {
          var b2 = blocks.pop(), b1 = blocks.pop();
          var w = b1.w + b2.w;
          blocks.push({ v: (b1.v * b1.w + b2.v * b2.w) / w, w: w, n: b1.n + b2.n });
        }
      }
      // limiti della cornice: la prima voce non esce a sinistra, l'ultima non esce a destra
      var lowB = -FRAME / 2 + L[layer[0]].w / 2;
      var highB = FRAME / 2 - L[layer[n - 1]].w / 2 - c[n - 1];
      var k = 0;
      blocks.forEach(function (b) {
        var v = Math.min(Math.max(b.v, lowB), Math.max(lowB, highB));
        for (var j = 0; j < b.n; j++) { X[layer[k]] = v + c[k]; k++; }
      });
    }
    function pass(mode) {
      var rs = [];
      for (var r = 0; r < layers.length; r++) { rs.push(r); }
      if (mode === 'up') { rs.reverse(); }
      rs.forEach(function (r) {
        var layer = layers[r];
        var desired = [], weight = [];
        layer.forEach(function (k) {
          var nb = mode === 'down' ? L[k].up : mode === 'up' ? L[k].down : L[k].up.concat(L[k].down);
          if (nb.length) {
            var s = 0; nb.forEach(function (x) { s += X[x]; });
            desired.push(s / nb.length);
          } else { desired.push(X[k]); }
          weight.push(L[k].real ? (nb.length ? 1 : 0.2) : 3);
        });
        place(layer, desired, weight);
      });
    }
    for (var q = 0; q < 6; q++) { pass('down'); pass('up'); }
    for (q = 0; q < 4; q++) { pass('both'); }

    // 5. coordinate finali
    var minX = Infinity, maxX = -Infinity;
    Object.keys(L).forEach(function (k) {
      minX = Math.min(minX, X[k] - L[k].w / 2); maxX = Math.max(maxX, X[k] + L[k].w / 2);
    });
    if (minX === Infinity) { minX = 0; maxX = 0; }
    var out = { nodes: {}, edges: [], cyclic: tp.cyclic };
    Object.keys(L).forEach(function (k) {
      L[k].x = X[k] - minX + MARGIN;
      L[k].y = MARGIN + L[k].rank * (NODE_H + RANK_SEP) + NODE_H / 2;
    });
    order.forEach(function (v) {
      var n = byId[v];
      out.nodes[v] = { id: v, x: L[v].x, y: L[v].y, w: L[v].w, h: NODE_H, titolo: n.titolo, sotto: n.sotto, tipo: n.tipo, pre: n.pre.slice(), suc: suc[v].slice() };
    });
    edges.forEach(function (e) {
      var pts = e.chain.map(function (k) { return { x: L[k].x, y: L[k].y }; });
      pts[0].y += NODE_H / 2;
      pts[pts.length - 1].y -= NODE_H / 2 + 2;
      var d = 'M' + r1(pts[0].x) + ' ' + r1(pts[0].y);
      for (var i = 1; i < pts.length; i++) {
        var a = pts[i - 1], b = pts[i], dy = (b.y - a.y) / 2;
        d += ' C' + r1(a.x) + ' ' + r1(a.y + dy) + ' ' + r1(b.x) + ' ' + r1(b.y - dy) + ' ' + r1(b.x) + ' ' + r1(b.y);
      }
      out.edges.push({ from: e.from, to: e.to, d: d });
    });
    out.width = Math.ceil(maxX - minX + 2 * MARGIN);
    out.height = Math.ceil(order.length ? MARGIN * 2 + (maxR + 1) * NODE_H + maxR * RANK_SEP : 2 * MARGIN);
    out.order = order;
    return out;
  }
  function r1(v) { return Math.round(v * 10) / 10; }

  /* ---------- disegno ---------- */
  function el(tag, attrs, parent) {
    var e = document.createElementNS(SVGNS, tag);
    for (var k in attrs) { if (attrs.hasOwnProperty(k)) { e.setAttribute(k, attrs[k]); } }
    if (parent) { parent.appendChild(e); }
    return e;
  }

  /*
   * opts:
   *   mode: 'edit' (lo studente spunta), 'view' (sola lettura), 'summary' (riepilogo classe), 'author' (editor)
   *   done: array di id spuntati
   *   onChange(doneArray)
   *   counts: {id: numero}, total: numero studenti (per 'summary')
   *   onSelect(id) per 'summary' e 'author'; selected: id evidenziato
   */
  function render(container, graph, opts) {
    opts = opts || {};
    var mode = opts.mode || 'view';
    var done = {};
    (opts.done || []).forEach(function (id) { done[id] = true; });
    var font = '';
    try { font = window.getComputedStyle(container).fontFamily; } catch (e) { font = ''; }
    var avail = container.clientWidth || (container.parentNode && container.parentNode.clientWidth) || 760;
    var lay = layout(graph, makeMeasure(font), { maxWidth: Math.max(480, avail - 4) });
    container.innerHTML = '';
    // vincoli: si spunta una voce solo se sono spuntati i suoi prerequisiti (default sì)
    var strict = mode === 'edit' && opts.vincoli !== false && graph.vincoli !== false;
    var notice = null;
    if (mode === 'edit') {
      notice = document.createElement('div');
      notice.className = 'lh-notice';
      notice.setAttribute('aria-live', 'polite');
      container.appendChild(notice);
    }
    var flash = {}, flashTimer = null;
    function say(msg) { if (notice) { notice.textContent = msg || ''; } }
    var top = mode === 'summary' ? 16 : 6;
    var svg = el('svg', { viewBox: '0 ' + (-top) + ' ' + Math.max(lay.width, 10) + ' ' + Math.max(lay.height + top, 10), role: 'img', 'class': 'lh-svg' }, container);
    svg.style.width = lay.width + 'px';
    svg.style.maxWidth = '100%';
    svg.style.minWidth = Math.round(lay.width * 0.72) + 'px';
    svg.style.height = 'auto';
    svg.style.display = 'block';
    svg.style.margin = '0 auto';
    svg.style.fontFamily = font || 'inherit';
    var uid = 'lh' + Math.random().toString(36).slice(2, 8);
    var defs = el('defs', {}, svg);
    ['edge', 'edgeOpen', 'edgeDone', 'hover'].forEach(function (c) {
      var m = el('marker', { id: uid + c, viewBox: '0 0 10 10', refX: '8', refY: '5', markerWidth: '7', markerHeight: '7', orient: 'auto-start-reverse' }, defs);
      el('path', { d: 'M2 1L8 5L2 9', fill: 'none', stroke: COLORS[c], 'stroke-width': '1.6', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, m);
    });
    var gE = el('g', {}, svg), gN = el('g', {}, svg);
    var edgeEls = lay.edges.map(function (e) {
      var p = el('path', { d: e.d, fill: 'none', 'stroke-width': '1.2' }, gE);
      return { e: e, p: p };
    });
    var nodeEls = {};
    var hovered = null, selected = opts.selected || null;
    lay.order.forEach(function (id) {
      var n = lay.nodes[id];
      var g = el('g', { 'class': 'lh-node', 'data-id': id, tabindex: mode === 'edit' || mode === 'author' || mode === 'summary' ? '0' : '-1' }, gN);
      g.style.cursor = mode === 'view' ? 'default' : 'pointer';
      var rect = el('rect', { x: r1(n.x - n.w / 2), y: r1(n.y - n.h / 2), width: n.w, height: n.h, rx: 9 }, g);
      if (n.tipo === 'leggere') { rect.setAttribute('stroke-dasharray', '5 3'); }
      var mark = el('g', { transform: 'translate(' + r1(n.x - n.w / 2 + 3) + ',' + r1(n.y - n.h / 2 + 3) + ')' }, g);
      el('circle', { r: '7.5', fill: COLORS.doneStroke, stroke: '#ffffff', 'stroke-width': '1.5' }, mark);
      el('path', { d: 'M-3.2 0.2 L-0.9 2.5 L3.4 -2.4', fill: 'none', stroke: '#ffffff', 'stroke-width': '1.8', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, mark);
      var t1 = el('text', { x: r1(n.x), y: r1(n.y - 7), 'text-anchor': 'middle', 'dominant-baseline': 'central', 'font-size': '13', 'font-weight': '600' }, g);
      t1.textContent = n.titolo;
      var t2 = el('text', { x: r1(n.x), y: r1(n.y + 10), 'text-anchor': 'middle', 'dominant-baseline': 'central', 'font-size': '11' }, g);
      t2.textContent = n.sotto;
      var badge = null;
      if (mode === 'summary') {
        badge = el('text', { x: r1(n.x + n.w / 2 - 6), y: r1(n.y - n.h / 2 - 5), 'text-anchor': 'end', 'font-size': '11', 'font-weight': '600' }, g);
      }
      var title = el('title', {}, g);
      title.textContent = n.titolo + (n.pre.length ? ' - richiede: ' + n.pre.map(function (p) { return lay.nodes[p].titolo; }).join(', ') : '');
      nodeEls[id] = { g: g, rect: rect, mark: mark, t1: t1, t2: t2, badge: badge };
      g.addEventListener('mouseenter', function () { hovered = id; paint(); });
      g.addEventListener('mouseleave', function () { hovered = null; paint(); });
      function act() {
        if (mode === 'edit') {
          if (done[id]) {
            delete done[id];
            var removed = strict ? dependentsDone(id) : [];
            removed.forEach(function (r) { delete done[r]; });
            say(removed.length ? 'Tolta la spunta anche da ' + names(removed) + (removed.length === 1 ? ', che richiede ' : ', che richiedono ') + '«' + n.titolo + '».' : '');
          } else if (strict && !isReady(id)) {
            var missing = n.pre.filter(function (p) { return !done[p]; });
            say('Per spuntare «' + n.titolo + '» devi prima saper fare ' + names(missing) + '.');
            flash = {};
            missing.forEach(function (p) { flash[p] = true; });
            clearTimeout(flashTimer);
            flashTimer = setTimeout(function () { flash = {}; paint(); }, 2500);
            paint();
            return;
          } else {
            done[id] = true;
            say('');
          }
          paint();
          if (opts.onChange) { opts.onChange(getDone()); }
        } else if (mode === 'summary' || mode === 'author') {
          selected = selected === id && mode === 'summary' ? null : id;
          paint();
          if (opts.onSelect) { opts.onSelect(selected); }
        }
      }
      g.addEventListener('click', act);
      g.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); act(); }
      });
    });

    function names(ids) {
      var t = ids.map(function (x) { return '«' + lay.nodes[x].titolo + '»'; });
      return t.length > 1 ? t.slice(0, -1).join(', ') + ' e ' + t[t.length - 1] : t[0];
    }
    function dependentsDone(id) {
      var out = [], seen = {}, stack = lay.nodes[id].suc.slice();
      while (stack.length) {
        var x = stack.pop();
        if (seen[x]) { continue; }
        seen[x] = true;
        if (done[x]) { out.push(x); }
        lay.nodes[x].suc.forEach(function (s) { stack.push(s); });
      }
      return lay.order.filter(function (x) { return out.indexOf(x) >= 0; });
    }
    function getDone() { return lay.order.filter(function (id) { return done[id]; }); }
    function isReady(id) { return lay.nodes[id].pre.every(function (p) { return done[p]; }); }
    function mix(a, b, t) {
      var pa = [1, 3, 5].map(function (i) { return parseInt(a.substr(i, 2), 16); });
      var pb = [1, 3, 5].map(function (i) { return parseInt(b.substr(i, 2), 16); });
      return '#' + pa.map(function (v, i) { var c = Math.round(v + (pb[i] - v) * t).toString(16); return c.length < 2 ? '0' + c : c; }).join('');
    }

    function paint() {
      var counts = opts.counts || {}, total = opts.total || 0;
      lay.order.forEach(function (id) {
        var ne = nodeEls[id], fill, stroke, sw = 0.9, tc, sc, mk = '';
        if (mode === 'summary') {
          var frac = total ? (counts[id] || 0) / total : 0;
          fill = mix('#f7f6f2', '#9ccc6e', frac);
          stroke = frac >= 0.999 && total ? COLORS.doneStroke : COLORS.stroke;
          tc = COLORS.text; sc = COLORS.sub;
          ne.badge.textContent = total ? (counts[id] || 0) + '/' + total : '';
          ne.badge.setAttribute('fill', COLORS.sub);
        } else if (mode === 'author') {
          fill = COLORS.fill; stroke = COLORS.stroke; tc = COLORS.text; sc = COLORS.sub;
        } else {
          var d = !!done[id], ok = isReady(id);
          if (d) { fill = COLORS.doneFill; stroke = COLORS.doneStroke; tc = COLORS.doneText; sc = COLORS.doneText; mk = '✓'; }
          else if (ok) { fill = COLORS.fill; stroke = COLORS.ready; sw = 2; tc = COLORS.text; sc = COLORS.sub; }
          else { fill = COLORS.lockFill; stroke = COLORS.lockStroke; tc = COLORS.lockText; sc = COLORS.lockText; }
        }
        if (mode === 'edit') { ne.g.style.cursor = strict && !done[id] && !isReady(id) ? 'not-allowed' : 'pointer'; }
        if (flash[id]) { stroke = COLORS.hover; sw = 2.6; }
        else if (selected === id) { stroke = COLORS.selected; sw = 2.4; }
        else if (hovered && (id === hovered || lay.nodes[hovered].pre.indexOf(id) >= 0 || lay.nodes[hovered].suc.indexOf(id) >= 0) && id !== hovered) { stroke = COLORS.hover; sw = 2; }
        ne.rect.setAttribute('fill', fill); ne.rect.setAttribute('stroke', stroke); ne.rect.setAttribute('stroke-width', sw);
        ne.t1.setAttribute('fill', tc); ne.t2.setAttribute('fill', sc);
        ne.mark.style.display = mk ? '' : 'none';
      });
      edgeEls.forEach(function (x) {
        var c = 'edge', w = 1.2;
        var focus = hovered || (mode === 'author' || mode === 'summary' ? selected : null);
        if (focus && (x.e.from === focus || x.e.to === focus)) { c = 'hover'; w = 2; }
        else if (mode === 'edit' || mode === 'view') {
          if (done[x.e.from] && done[x.e.to]) { c = 'edgeDone'; }
          else if (done[x.e.from]) { c = 'edgeOpen'; w = 1.6; }
        }
        x.p.setAttribute('stroke', COLORS[c]); x.p.setAttribute('stroke-width', w);
        x.p.setAttribute('marker-end', 'url(#' + uid + c + ')');
      });
      if (opts.onPaint) { opts.onPaint({ done: getDone().length, total: lay.order.length, ready: lay.order.filter(function (id) { return !done[id] && isReady(id); }).length }); }
    }
    paint();
    return {
      getDone: getDone,
      setDone: function (arr) { done = {}; (arr || []).forEach(function (id) { done[id] = true; }); paint(); },
      setCounts: function (counts, total) { opts.counts = counts; opts.total = total; paint(); },
      select: function (id) { selected = id; paint(); },
      layout: lay,
      svg: svg
    };
  }

  /* ---------- legenda e contatore riutilizzabili ---------- */
  function legend(graph) {
    var box = document.createElement('div');
    box.className = 'lh-legend';
    var nodes = graph ? normalize(graph).list : [];
    // i due tipi in legenda solo se la mappa li usa entrambi
    var both = !graph || (nodes.some(function (n) { return n.tipo === 'leggere'; }) && nodes.some(function (n) { return n.tipo !== 'leggere'; }));
    box.innerHTML =
      '<span><i class="lh-sw" style="border:2px solid ' + COLORS.ready + '"></i>pronta da imparare</span>' +
      '<span><i class="lh-sw" style="background:' + COLORS.doneFill + ';border:1px solid ' + COLORS.doneStroke + '"></i>la so fare</span>' +
      '<span><i class="lh-sw" style="background:' + COLORS.lockFill + ';border:1px solid ' + COLORS.lockStroke + '"></i>non ancora</span>' +
      (both ?
      '<span><i class="lh-sw" style="border:1px solid ' + COLORS.stroke + '"></i>da saper scrivere</span>' +
      '<span><i class="lh-sw" style="border:1px dashed ' + COLORS.stroke + '"></i>da saper leggere</span>' : '');
    return box;
  }

  var CSS =
    '.lh-wrap{margin:.5rem 0 1rem;max-width:100%;overflow-x:auto}' +
    '.lh-legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.85rem;color:#5f5e5a;margin:.25rem 0 .75rem}' +
    '.lh-legend span{display:inline-flex;align-items:center;gap:6px}' +
    '.lh-sw{display:inline-block;width:18px;height:11px;border-radius:3px;box-sizing:border-box}' +
    '.lh-count{font-weight:600;color:#1f1e1b;margin:.25rem 0}' +
    '.lh-node:focus{outline:none}.lh-node:focus-visible rect{stroke:#7a4fd0;stroke-width:2.4}' +
    '.lh-notice{min-height:1.4em;font-size:.9rem;color:#8a5a00;margin:0 0 .25rem}' +
    '.lh-hint{color:#5f5e5a;font-size:.9rem;margin:.25rem 0 .5rem}' +
    '.lh-table{border-collapse:collapse;width:100%;font-size:.9rem;margin:.5rem 0}' +
    '.lh-table th,.lh-table td{border-bottom:1px solid #e3e1da;padding:6px 8px;text-align:left;vertical-align:middle}' +
    '.lh-bar{display:inline-block;width:120px;height:8px;background:#ecebe5;border-radius:4px;overflow:hidden;vertical-align:middle;margin-right:8px}' +
    '.lh-bar i{display:block;height:100%;background:#86b85a}' +
    '.lh-detail{border:1px solid #e3e1da;border-radius:8px;padding:10px 14px;margin:.5rem 0;background:#fbfaf7}' +
    '.lh-detail h4{font-size:1rem;margin:0 0 .4rem}' +
    '.lh-cols{display:flex;flex-wrap:wrap;gap:24px}.lh-cols>div{min-width:200px;flex:1}' +
    '.lh-cols ul{margin:.25rem 0 0;padding-left:1.1rem}';
  function injectCss() {
    if (document.getElementById('lh-css')) { return; }
    var s = document.createElement('style'); s.id = 'lh-css'; s.textContent = CSS;
    (document.head || document.documentElement).appendChild(s);
  }

  function countText(p) {
    return 'Sai fare ' + p.done + (p.done === 1 ? ' voce' : ' voci') + ' su ' + p.total + ' \u00b7 ' +
      p.ready + (p.ready === 1 ? ' pronta' : ' pronte') + ' da imparare';
  }

  root.LH = { version: 1, countText: countText, layout: layout, render: render, normalize: normalize, createsCycle: createsCycle, legend: legend, injectCss: injectCss, COLORS: COLORS };
})(typeof window !== 'undefined' ? window : this);
