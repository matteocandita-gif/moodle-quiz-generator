// Ricostruisce la pagina dell'editor «Mappe dei prerequisiti» dai sorgenti.
// Uso (dalla radice del repository): node sviluppo/mappe-prerequisiti/costruisci_editor.js
// Scrive plugins/moodle-quiz-generator/skills/mappe-prerequisiti/assets/editor.html.
// Non modificare editor.html a mano: modifica i sorgenti, rilancia e alza VERSIONE_PAGINA in editor.src.html.
const fs = require('fs');
const path = require('path');
const qui = __dirname;
const read = (f) => fs.readFileSync(path.join(qui, f), 'utf8');
const parti = {
  RUNTIME: read('src/lh-runtime.js'),
  MOODLE: read('src/lh-moodle.js'),
  PRESET: read('src/lh-preset.js'),
  MBZ: read('src/lh-mbz.js'),
};
for (const [n, s] of Object.entries(parti)) {
  if (/<\/script/i.test(s)) throw new Error(n + ' contiene </script');
}
let html = read('editor.src.html');
for (const [n, s] of Object.entries(parti)) html = html.split('/*@@' + n + '@@*/').join(s);
const out = path.join(qui, '..', '..', 'plugins', 'moodle-quiz-generator', 'skills', 'mappe-prerequisiti', 'assets', 'editor.html');
fs.writeFileSync(out, html);
console.log(path.relative(process.cwd(), out) + ' (' + html.length + ' caratteri)');
