// Crea il backup .mbz di un'attività Database di Moodle con una mappa dei prerequisiti.
// Uso: node crea_mbz.js <mappa.json> <cartella-uscita> ["Nome dell'attività"]
// Il codice della mappa (disegno, collegamento con Moodle, modelli, backup) è preso da ../assets/editor.html,
// la stessa pagina che l'utente pubblica come editor: così il backup ha sempre la versione del plugin.
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const vm = require('vm');

const [mapPath, outDir, nomeAttivita] = process.argv.slice(2);
if (!mapPath || !outDir) {
  console.error('Uso: node crea_mbz.js <mappa.json> <cartella-uscita> ["Nome dell\'attività"]');
  process.exit(1);
}
const editorPath = path.join(__dirname, '..', 'assets', 'editor.html');
const html = fs.readFileSync(editorPath, 'utf8');
const scripts = [...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)];
const byId = (id) => {
  const m = scripts.find((s) => s[1].includes('id="' + id + '"'));
  if (!m) throw new Error('script ' + id + ' non trovato in editor.html');
  return m[2];
};
const byStart = (start) => {
  const m = scripts.find((s) => !s[1].includes('src=') && s[2].startsWith(start));
  if (!m) throw new Error('script "' + start + '" non trovato in editor.html');
  return m[2];
};
const ctx = { window: {}, TextEncoder };
vm.createContext(ctx);
vm.runInContext(byStart('/* Gerarchie di apprendimento - file del preset'), ctx);
vm.runInContext(byStart('/* Gerarchie di apprendimento - backup .mbz'), ctx);
vm.runInContext(byId('src-runtime'), ctx);
const { LH_PRESET, LH_MBZ, LH } = ctx.window;

let g = JSON.parse(fs.readFileSync(mapPath, 'utf8'));
if (g.data && g.data.nodi) g = g.data; // documento letto con ArtifactData
delete g.aggiornato;
if (!g.titolo || !Array.isArray(g.nodi) || !g.nodi.length) throw new Error('la mappa non ha titolo o voci');

// controlli sulla mappa
const ids = new Set();
const errori = [];
g.nodi.forEach((n) => {
  if (!n.id) errori.push('voce senza id: ' + JSON.stringify(n.titolo));
  else if (ids.has(n.id)) errori.push('id ripetuto: ' + n.id);
  ids.add(n.id);
});
g.nodi.forEach((n) => (n.pre || []).forEach((p) => { if (!ids.has(p)) errori.push(n.id + ' richiede ' + p + ', che non esiste'); }));
const cicli = LH.layout(g, (t) => t.length * 7).cyclic;
if (cicli.length) errori.push('prerequisiti in ciclo intorno a: ' + cicli.join(', '));
if (errori.length) { console.error('Mappa non valida:\n- ' + errori.join('\n- ')); process.exit(2); }

const slug = LH_PRESET.slug(g.titolo);
const runtime = byId('src-runtime');
const moodle = byId('src-moodle');
const pack = LH_MBZ.files(LH_PRESET.build(g, runtime, moodle), { nome: nomeAttivita || g.titolo, filename: slug });
if (!pack.files[pack.dirs[1] + 'data.xml'].includes('window.LH_GRAFO')) throw new Error('modello JavaScript senza mappa');
fs.mkdirSync(outDir, { recursive: true });
const out = path.resolve(outDir, slug + '.mbz');
fs.writeFileSync(out, zlib.gzipSync(Buffer.from(LH_MBZ.tar(pack))));
const lay = LH.layout(g, (t, size, w) => t.length * size * (w >= 600 ? 0.6 : 0.55));
console.log(out);
console.log(g.nodi.length + ' voci, attività «' + (nomeAttivita || g.titolo) + '», larghezza della mappa circa ' + lay.width + ' px');
