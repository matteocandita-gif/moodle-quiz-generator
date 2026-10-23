/* Gerarchie di apprendimento - file del preset per l'attività Database di Moodle. */
(function (root) {
  'use strict';

  function xmlEsc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  var PRESET_XML =
    '<preset>\n\n' +
    '<settings>\n' +
    '<intro></intro>\n' +
    '<comments>0</comments>\n' +
    '<requiredentries>0</requiredentries>\n' +
    '<requiredentriestoview>0</requiredentriestoview>\n' +
    '<maxentries>1</maxentries>\n' +
    '<rssarticles>0</rssarticles>\n' +
    '<approval>1</approval>\n' +
    '<manageapproved>1</manageapproved>\n' +
    '<defaultsortdir>0</defaultsortdir>\n' +
    '<defaultsort>0</defaultsort>\n' +
    '</settings>\n\n' +
    '<field>\n' +
    '<type>text</type>\n' +
    '<name>voci</name>\n' +
    '<description>Voci spuntate dallo studente (le gestisce la mappa, non modificare a mano)</description>\n' +
    '<required>0</required>\n' +
    '<param1>0</param1>\n' +
    '</field>\n\n' +
    '</preset>\n';

  var ADD =
    '<div class="lh-app" data-lh="edit" data-field="[[voci#id]]">\n' +
    '  <p class="lh-hint">Clicca le voci che ti senti in grado di fare: diventano verdi. ' +
    'Le voci con il bordo blu sono quelle che sei pronto a imparare, perché sai già tutto quello che richiedono. ' +
    'Quando hai finito premi «Salva».</p>\n' +
    '  <div class="lh-native">[[voci]]</div>\n' +
    '</div>\n';

  var SINGLE =
    '<div class="lh-app" data-lh="view">\n' +
    '  <span class="lh-data" hidden>[[voci]]</span>\n' +
    '  <span class="lh-user" hidden>##user##</span>\n' +
    '  <span class="lh-edit" hidden>##edit##</span>\n' +
    '</div>\n';

  var LIST_HEADER = '<div class="lh-app" data-lh="list"></div>\n<div class="lh-entries">\n';
  var LIST =
    '<div class="lh-entry">\n' +
    '  <span class="lh-user">##user##</span>\n' +
    '  <span class="lh-data">[[voci]]</span>\n' +
    '  <span class="lh-edit">##edit##</span>\n' +
    '  <span class="lh-approve" hidden>##approve##</span>\n' +
    '  <span class="lh-more" hidden>##moreurl##</span>\n' +
    '</div>\n';
  var LIST_FOOTER = '</div>\n';

  var ASEARCH =
    '<div class="container">\n' +
    '  <div class="mb-3"><div class="fw-bold mb-2">Nome</div>##firstname##</div>\n' +
    '  <div class="mb-3"><div class="fw-bold mb-2">Cognome</div>##lastname##</div>\n' +
    '</div>\n';

  var CSS =
    '.lh-app{margin:.5rem 0 1rem}\n' +
    '.lh-app .lh-btn{margin:.25rem 0 .75rem}\n' +
    '.lh-app .lh-who{font-size:1.25rem;margin:.25rem 0}\n';

  function build(graph, runtimeSrc, moodleSrc) {
    var js =
      '/* Gerarchia di apprendimento: ' + String(graph.titolo || '').replace(/\*\//g, '') + ' */\n' +
      'window.LH_GRAFO = ' + JSON.stringify(graph, null, 1).replace(/</g, '\\u003c') + ';\n' +
      runtimeSrc + '\n' + moodleSrc + '\n';
    return {
      'preset.xml': PRESET_XML,
      'addtemplate.html': ADD,
      'singletemplate.html': SINGLE,
      'listtemplate.html': LIST,
      'listtemplateheader.html': LIST_HEADER,
      'listtemplatefooter.html': LIST_FOOTER,
      'asearchtemplate.html': ASEARCH,
      'rsstemplate.html': '<div>##user## - [[voci]]</div>\n',
      'rsstitletemplate.html': '##user##\n',
      'csstemplate.css': CSS,
      'jstemplate.js': js
    };
  }

  function slug(s) {
    return String(s || 'gerarchia').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'gerarchia';
  }

  root.LH_PRESET = { build: build, slug: slug, xmlEsc: xmlEsc };
  if (typeof module !== 'undefined' && module.exports) { module.exports = root.LH_PRESET; }
})(typeof window !== 'undefined' ? window : this);
