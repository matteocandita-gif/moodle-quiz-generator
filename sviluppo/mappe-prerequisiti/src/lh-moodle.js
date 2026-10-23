/* Gerarchie di apprendimento - collegamento con l'attività Database di Moodle. */
(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState !== 'loading') { fn(); } else { document.addEventListener('DOMContentLoaded', fn); }
  }
  function ids(text) {
    return String(text || '').split(/[\s,;]+/).map(function (x) { return x.trim(); }).filter(Boolean);
  }
  function div(cls, text) {
    var d = document.createElement('div');
    if (cls) { d.className = cls; }
    if (text) { d.textContent = text; }
    return d;
  }
  function editHref(scope) {
    var a = scope && scope.querySelector('.lh-edit a[href]');
    return a ? a.getAttribute('href') : null;
  }
  function button(href, label) {
    var a = document.createElement('a');
    a.className = 'btn btn-primary lh-btn';
    a.href = href; a.textContent = label;
    return a;
  }

  ready(function () {
    var G = window.LH_GRAFO;
    if (!G || !window.LH) { return; }
    LH.injectCss();
    var nodes = LH.normalize(G).list, known = {};
    nodes.forEach(function (n) { known[n.id] = n; });
    var N = nodes.length;

    var countText = LH.countText;

    /* --- Pagina di inserimento / modifica: lo studente spunta --- */
    Array.prototype.forEach.call(document.querySelectorAll('.lh-app[data-lh="edit"]'), function (box) {
      var input = document.getElementById('field_' + box.getAttribute('data-field')) ||
        box.querySelector('input[type="text"], textarea');
      if (!input) { return; }
      var native = box.querySelector('.lh-native');
      if (native) { native.style.display = 'none'; }
      var all = ids(input.value);
      var keep = all.filter(function (id) { return !known[id]; });  // voci tolte dalla mappa: si conservano
      var count = div('lh-count');
      var wrap = div('lh-wrap');
      box.appendChild(count);
      box.appendChild(LH.legend(G));
      box.appendChild(wrap);
      LH.render(wrap, G, {
        mode: 'edit',
        done: all.filter(function (id) { return known[id]; }),
        onChange: function (arr) { input.value = arr.concat(keep).join(','); },
        onPaint: function (p) { count.textContent = countText(p); }
      });
    });

    /* --- Scheda singola: sola lettura --- */
    Array.prototype.forEach.call(document.querySelectorAll('.lh-app[data-lh="view"]'), function (box) {
      var data = box.querySelector('.lh-data');
      var who = box.querySelector('.lh-user');
      var href = editHref(box);
      if (who && who.textContent.trim()) {
        var h = document.createElement('h3');
        h.className = 'lh-who';
        h.textContent = who.textContent.trim();
        box.appendChild(h);
      }
      var count = div('lh-count');
      box.appendChild(count);
      if (href) { box.appendChild(button(href, 'Aggiorna la mia autovalutazione')); }
      box.appendChild(LH.legend(G));
      var wrap = div('lh-wrap');
      box.appendChild(wrap);
      LH.render(wrap, G, {
        mode: 'view',
        done: ids(data && data.textContent).filter(function (id) { return known[id]; }),
        onPaint: function (p) { count.textContent = countText(p); }
      });
    });

    /* --- Elenco: lo studente vede la sua mappa, il docente il riepilogo della classe --- */
    var listBox = document.querySelector('.lh-app[data-lh="list"]');
    if (!listBox) { return; }
    var entryEls = Array.prototype.slice.call(document.querySelectorAll('.lh-entry'));
    if (!entryEls.length) { return; }
    var entries = entryEls.map(function (e) {
      var u = e.querySelector('.lh-user'), d = e.querySelector('.lh-data'), m = e.querySelector('.lh-more');
      return {
        name: u ? u.textContent.trim() : '',
        done: ids(d && d.textContent).filter(function (id) { return known[id]; }),
        more: m ? m.textContent.trim() : '',
        edit: editHref(e),
        canApprove: !!e.querySelector('.lh-approve a, .lh-approve button')
      };
    });
    var names = {};
    entries.forEach(function (x) { names[x.name] = true; });
    var teacher = entries.some(function (x) { return x.canApprove; }) || Object.keys(names).length > 1;
    var holder = document.querySelector('.lh-entries');
    if (holder) { holder.style.display = 'none'; }

    if (!teacher) {
      var own = entries[0];
      var count = div('lh-count');
      listBox.appendChild(count);
      if (own.edit) { listBox.appendChild(button(own.edit, 'Aggiorna la mia autovalutazione')); }
      listBox.appendChild(LH.legend(G));
      var w = div('lh-wrap');
      listBox.appendChild(w);
      LH.render(w, G, { mode: 'view', done: own.done, onPaint: function (p) { count.textContent = countText(p); } });
      return;
    }

    // Riepilogo per il docente
    var counts = {};
    entries.forEach(function (x) { x.done.forEach(function (id) { counts[id] = (counts[id] || 0) + 1; }); });
    var total = entries.length;
    var head = div('lh-count', 'Riepilogo della classe: ' + total + (total === 1 ? ' studente' : ' studenti'));
    listBox.appendChild(head);
    if (document.querySelector('.pagination, .paging')) {
      var more = div('lh-hint');
      var url = new URL(window.location.href);
      url.searchParams.set('perpage', '1000');
      more.innerHTML = 'Il riepilogo conta solo le schede di questa pagina. ';
      var a = document.createElement('a'); a.href = url.toString(); a.textContent = 'Mostra tutte le schede in una pagina';
      more.appendChild(a);
      listBox.appendChild(more);
    }
    listBox.appendChild(div('lh-hint', 'Il colore indica quanti studenti dichiarano di saper fare la voce. Clicca una voce per vedere i nomi.'));
    var detail = div('lh-detail');
    detail.style.display = 'none';
    var w2 = div('lh-wrap');
    listBox.appendChild(w2);
    listBox.appendChild(detail);

    function showDetail(id) {
      if (!id) { detail.style.display = 'none'; return; }
      var n = known[id];
      var yes = [], ready = [], no = [];
      entries.forEach(function (x) {
        var d = {};
        x.done.forEach(function (k) { d[k] = true; });
        if (d[id]) { yes.push(x.name); }
        else if (n.pre.every(function (p) { return d[p]; })) { ready.push(x.name); }
        else { no.push(x.name); }
      });
      detail.innerHTML = '';
      var h = document.createElement('h4'); h.textContent = n.titolo + (n.sotto ? ' (' + n.sotto + ')' : '');
      detail.appendChild(h);
      var cols = div('lh-cols');
      [['La sanno fare', yes], ['Pronti a impararla', ready], ['Mancano dei prerequisiti', no]].forEach(function (c) {
        var col = div('');
        var t = document.createElement('strong'); t.textContent = c[0] + ' (' + c[1].length + ')';
        col.appendChild(t);
        var ul = document.createElement('ul');
        c[1].sort().forEach(function (name) { var li = document.createElement('li'); li.textContent = name; ul.appendChild(li); });
        col.appendChild(ul);
        cols.appendChild(col);
      });
      detail.appendChild(cols);
      detail.style.display = '';
    }
    LH.render(w2, G, { mode: 'summary', counts: counts, total: total, onSelect: showDetail });

    // Tabella degli studenti
    var table = document.createElement('table');
    table.className = 'lh-table';
    table.innerHTML = '<thead><tr><th>Studente</th><th>Voci che sa fare</th><th>Pronte da imparare</th></tr></thead>';
    var tb = document.createElement('tbody');
    entries.slice().sort(function (a, b) { return a.name.localeCompare(b.name); }).forEach(function (x) {
      var d = {};
      x.done.forEach(function (k) { d[k] = true; });
      var ready = nodes.filter(function (n) { return !d[n.id] && n.pre.every(function (p) { return d[p]; }); }).length;
      var tr = document.createElement('tr');
      var td1 = document.createElement('td');
      if (x.more) { var a = document.createElement('a'); a.href = x.more; a.textContent = x.name; td1.appendChild(a); }
      else { td1.textContent = x.name; }
      var td2 = document.createElement('td');
      var bar = document.createElement('span'); bar.className = 'lh-bar';
      var fill = document.createElement('i'); fill.style.width = (N ? Math.round(100 * x.done.length / N) : 0) + '%';
      bar.appendChild(fill); td2.appendChild(bar);
      td2.appendChild(document.createTextNode(x.done.length + '/' + N));
      var td3 = document.createElement('td'); td3.textContent = String(ready);
      tr.appendChild(td1); tr.appendChild(td2); tr.appendChild(td3);
      tb.appendChild(tr);
    });
    table.appendChild(tb);
    listBox.appendChild(table);
  });
})();
