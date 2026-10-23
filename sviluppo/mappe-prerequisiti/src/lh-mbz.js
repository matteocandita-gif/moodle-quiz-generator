/* Gerarchie di apprendimento - backup .mbz di un'attività Database pronta (modello: backup Moodle 5.2). */
(function (root) {
  'use strict';

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  var XML = '<?xml version="1.0" encoding="UTF-8"?>\n';

  /*
   * files: oggetto restituito da LH_PRESET.build (preset.xml, modelli, jstemplate.js)
   * opts: { nome, intro, now (secondi), sezione }
   * Restituisce { 'percorso': 'contenuto' } con i file del backup.
   */
  function files(presetFiles, opts) {
    opts = opts || {};
    var now = opts.now || Math.floor(Date.now() / 1000);
    var nome = opts.nome || 'Mappa dei prerequisiti';
    var sezione = opts.sezione != null ? opts.sezione : 0;
    var MID = 900001, DID = 900001, CTX = 900001, FID = 900001;
    var dir = 'activities/data_' + MID;
    var filename = (opts.filename || 'backup-mappa') + '.mbz';
    var t = function (k) { return esc(presetFiles[k] || ''); };

    var data = XML +
      '<activity id="' + DID + '" moduleid="' + MID + '" modulename="data" contextid="' + CTX + '">\n' +
      '  <data id="' + DID + '">\n' +
      '    <name>' + esc(nome) + '</name>\n' +
      '    <intro>' + esc(opts.intro || '') + '</intro>\n' +
      '    <introformat>1</introformat>\n' +
      '    <comments>0</comments>\n' +
      '    <timeavailablefrom>0</timeavailablefrom>\n' +
      '    <timeavailableto>0</timeavailableto>\n' +
      '    <timeviewfrom>0</timeviewfrom>\n' +
      '    <timeviewto>0</timeviewto>\n' +
      '    <requiredentries>0</requiredentries>\n' +
      '    <requiredentriestoview>0</requiredentriestoview>\n' +
      '    <maxentries>1</maxentries>\n' +
      '    <rssarticles>0</rssarticles>\n' +
      '    <singletemplate>' + t('singletemplate.html') + '</singletemplate>\n' +
      '    <listtemplate>' + t('listtemplate.html') + '</listtemplate>\n' +
      '    <listtemplateheader>' + t('listtemplateheader.html') + '</listtemplateheader>\n' +
      '    <listtemplatefooter>' + t('listtemplatefooter.html') + '</listtemplatefooter>\n' +
      '    <addtemplate>' + t('addtemplate.html') + '</addtemplate>\n' +
      '    <rsstemplate>' + t('rsstemplate.html') + '</rsstemplate>\n' +
      '    <rsstitletemplate>' + t('rsstitletemplate.html') + '</rsstitletemplate>\n' +
      '    <csstemplate>' + t('csstemplate.css') + '</csstemplate>\n' +
      '    <jstemplate>' + t('jstemplate.js') + '</jstemplate>\n' +
      '    <asearchtemplate>' + t('asearchtemplate.html') + '</asearchtemplate>\n' +
      '    <approval>1</approval>\n' +
      '    <manageapproved>1</manageapproved>\n' +
      '    <scale>10</scale>\n' +
      '    <assessed>0</assessed>\n' +
      '    <assesstimestart>0</assesstimestart>\n' +
      '    <assesstimefinish>0</assesstimefinish>\n' +
      '    <defaultsort>0</defaultsort>\n' +
      '    <defaultsortdir>0</defaultsortdir>\n' +
      '    <editany>0</editany>\n' +
      '    <notification>0</notification>\n' +
      '    <timemodified>' + now + '</timemodified>\n' +
      '    <config>$@NULL@$</config>\n' +
      '    <completionentries>0</completionentries>\n' +
      '    <fields>\n' +
      '      <field id="' + FID + '">\n' +
      '        <type>text</type>\n' +
      '        <name>voci</name>\n' +
      '        <description>Voci spuntate dallo studente (le gestisce la mappa, non modificare a mano)</description>\n' +
      '        <required>0</required>\n' +
      '        <param1>0</param1>\n' +
      [2, 3, 4, 5, 6, 7, 8, 9, 10].map(function (i) { return '        <param' + i + '>$@NULL@$</param' + i + '>\n'; }).join('') +
      '      </field>\n' +
      '    </fields>\n' +
      '    <records>\n    </records>\n' +
      '    <recordstags>\n    </recordstags>\n' +
      '  </data>\n' +
      '</activity>';

    var module = XML +
      '<module id="' + MID + '" version="2026042000">\n' +
      '  <modulename>data</modulename>\n' +
      '  <sectionid>' + (900000 + sezione) + '</sectionid>\n' +
      '  <sectionnumber>' + sezione + '</sectionnumber>\n' +
      '  <idnumber></idnumber>\n' +
      '  <added>' + now + '</added>\n' +
      '  <score>0</score>\n' +
      '  <indent>0</indent>\n' +
      '  <visible>1</visible>\n' +
      '  <visibleoncoursepage>1</visibleoncoursepage>\n' +
      '  <visibleold>1</visibleold>\n' +
      '  <groupmode>0</groupmode>\n' +
      '  <groupingid>0</groupingid>\n' +
      '  <completion>0</completion>\n' +
      '  <completiongradeitemnumber>$@NULL@$</completiongradeitemnumber>\n' +
      '  <completionpassgrade>0</completionpassgrade>\n' +
      '  <completionview>0</completionview>\n' +
      '  <completionexpected>0</completionexpected>\n' +
      '  <availability>$@NULL@$</availability>\n' +
      '  <showdescription>0</showdescription>\n' +
      '  <downloadcontent>1</downloadcontent>\n' +
      '  <lang></lang>\n' +
      '  <enableaitools>$@NULL@$</enableaitools>\n' +
      '  <enabledaiactions>$@NULL@$</enabledaiactions>\n' +
      '  <tags>\n  </tags>\n' +
      '</module>';

    var settings = [
      ['filename', filename], ['users', 0], ['anonymize', 0], ['role_assignments', 0], ['activities', 1],
      ['blocks', 0], ['files', 1], ['filters', 0], ['comments', 0], ['badges', 0], ['calendarevents', 0],
      ['userscompletion', 0], ['logs', 0], ['grade_histories', 0], ['groups', 0], ['competencies', 0],
      ['customfield', 0], ['contentbankcontent', 0], ['xapistate', 0], ['legacyfiles', 0]
    ].map(function (s) {
      return '      <setting>\n        <level>root</level>\n        <name>' + s[0] + '</name>\n        <value>' + esc(s[1]) + '</value>\n      </setting>\n';
    }).join('') +
      '      <setting>\n        <level>activity</level>\n        <activity>data_' + MID + '</activity>\n        <name>data_' + MID + '_included</name>\n        <value>1</value>\n      </setting>\n' +
      '      <setting>\n        <level>activity</level>\n        <activity>data_' + MID + '</activity>\n        <name>data_' + MID + '_userinfo</name>\n        <value>0</value>\n      </setting>\n';

    var backupId = Array.prototype.map.call(String(now) + nome, function (c) { return c.charCodeAt(0); })
      .reduce(function (h, c) { return (h * 31 + c) >>> 0; }, 7).toString(16);
    while (backupId.length < 32) { backupId += backupId; }
    backupId = backupId.slice(0, 32);

    var mb = XML +
      '<moodle_backup>\n' +
      '  <information>\n' +
      '    <name>' + esc(filename) + '</name>\n' +
      '    <moodle_version>2026042002.02</moodle_version>\n' +
      '    <moodle_release>5.2.2+ (Build: 20260903)</moodle_release>\n' +
      '    <backup_version>2026042000</backup_version>\n' +
      '    <backup_release>5.2</backup_release>\n' +
      '    <backup_date>' + now + '</backup_date>\n' +
      '    <mnet_remoteusers>0</mnet_remoteusers>\n' +
      '    <include_files>1</include_files>\n' +
      '    <include_file_references_to_external_content>0</include_file_references_to_external_content>\n' +
      '    <original_wwwroot>https://salvemini.synology.me/moodle</original_wwwroot>\n' +
      '    <original_site_identifier_hash>8568b3483d0e2ab302ef2738533ac213</original_site_identifier_hash>\n' +
      '    <original_course_id>900000</original_course_id>\n' +
      '    <original_course_format>topics</original_course_format>\n' +
      '    <original_course_fullname>Mappe dei prerequisiti</original_course_fullname>\n' +
      '    <original_course_shortname>mappe-prerequisiti</original_course_shortname>\n' +
      '    <original_course_startdate>' + now + '</original_course_startdate>\n' +
      '    <original_course_enddate>0</original_course_enddate>\n' +
      '    <original_course_contextid>900000</original_course_contextid>\n' +
      '    <original_system_contextid>1</original_system_contextid>\n' +
      '    <details>\n' +
      '      <detail backup_id="' + backupId + '">\n' +
      '        <type>activity</type>\n        <format>moodle2</format>\n        <interactive>1</interactive>\n' +
      '        <mode>70</mode>\n        <execution>2</execution>\n        <executiontime>0</executiontime>\n' +
      '      </detail>\n' +
      '    </details>\n' +
      '    <contents>\n      <activities>\n        <activity>\n' +
      '          <moduleid>' + MID + '</moduleid>\n' +
      '          <sectionid>' + (900000 + sezione) + '</sectionid>\n' +
      '          <modulename>data</modulename>\n' +
      '          <title>' + esc(nome) + '</title>\n' +
      '          <directory>' + dir + '</directory>\n' +
      '          <insubsection></insubsection>\n' +
      '        </activity>\n      </activities>\n    </contents>\n' +
      '    <settings>\n' + settings + '    </settings>\n' +
      '  </information>\n' +
      '</moodle_backup>';

    var out = {};
    out['moodle_backup.xml'] = mb;
    out[dir + '/data.xml'] = data;
    out[dir + '/module.xml'] = module;
    out[dir + '/inforef.xml'] = XML + '<inforef>\n</inforef>';
    out[dir + '/roles.xml'] = XML + '<roles>\n  <role_overrides>\n  </role_overrides>\n  <role_assignments>\n  </role_assignments>\n</roles>';
    out[dir + '/grades.xml'] = XML + '<activity_gradebook>\n  <grade_items>\n  </grade_items>\n  <grade_letters>\n  </grade_letters>\n</activity_gradebook>';
    out[dir + '/grade_history.xml'] = XML + '<grade_history>\n  <grade_grades>\n  </grade_grades>\n</grade_history>';
    out['completion.xml'] = XML + '<course_completion>\n</course_completion>';
    out['files.xml'] = XML + '<files>\n</files>';
    out['groups.xml'] = XML + '<groups>\n  <groupcustomfields>\n  </groupcustomfields>\n  <groupings>\n    <groupingcustomfields>\n    </groupingcustomfields>\n  </groupings>\n</groups>';
    out['outcomes.xml'] = XML + '<outcomes_definition>\n</outcomes_definition>';
    out['questions.xml'] = XML + '<question_categories>\n</question_categories>';
    out['roles.xml'] = XML + '<roles_definition>\n</roles_definition>';
    out['scales.xml'] = XML + '<scales_definition>\n</scales_definition>';
    out['moodle_backup.log'] = '';
    return { files: out, dirs: ['activities/', dir + '/'], now: now, filename: filename };
  }

  /* ---------- archivio tar (ustar) come quello di Moodle, con .ARCHIVE_INDEX in testa ---------- */
  function utf8(s) {
    if (typeof TextEncoder !== 'undefined') { return new TextEncoder().encode(s); }
    return Uint8Array.from(Buffer.from(s, 'utf8'));
  }
  function octal(n, len) {
    var s = n.toString(8);
    while (s.length < len - 1) { s = '0' + s; }
    return s + '\0';
  }
  function header(name, size, mtime, isDir) {
    var h = new Uint8Array(512);
    var put = function (str, off, max) { var b = utf8(str); h.set(b.subarray(0, max), off); };
    put(name, 0, 100);
    put(isDir ? '0000755\0' : '0000644\0', 100, 8);
    put('0000000\0', 108, 8);
    put('0000000\0', 116, 8);
    put(octal(size, 12), 124, 12);
    put(octal(mtime, 12), 136, 12);
    put('        ', 148, 8);
    h[156] = isDir ? 53 : 48; // '5' cartella, '0' file
    put('ustar\0', 257, 6);
    put('00', 263, 2);
    var sum = 0;
    for (var i = 0; i < 512; i++) { sum += h[i]; }
    put(octal(sum, 7) + ' ', 148, 8);
    return h;
  }
  function tar(pack) {
    var names = Object.keys(pack.files);
    var lines = [];
    pack.dirs.forEach(function (d) { lines.push(d + '\td\t0\t?'); });
    names.forEach(function (n) { lines.push(n + '\tf\t' + utf8(pack.files[n]).length + '\t' + pack.now); });
    var index = 'Moodle archive file index. Count: ' + lines.length + '\n' + lines.join('\n') + '\n';
    var entries = [['.ARCHIVE_INDEX', index, false]];
    pack.dirs.forEach(function (d) { entries.push([d, null, true]); });
    names.forEach(function (n) { entries.push([n, pack.files[n], false]); });
    var chunks = [], total = 0;
    entries.forEach(function (e) {
      var body = e[2] ? new Uint8Array(0) : utf8(e[1]);
      chunks.push(header(e[0], body.length, pack.now, e[2]));
      chunks.push(body);
      var pad = (512 - body.length % 512) % 512;
      chunks.push(new Uint8Array(pad));
      total += 512 + body.length + pad;
    });
    chunks.push(new Uint8Array(1024));
    total += 1024;
    var out = new Uint8Array(total), off = 0;
    chunks.forEach(function (c) { out.set(c, off); off += c.length; });
    return out;
  }

  root.LH_MBZ = { files: files, tar: tar };
  if (typeof module !== 'undefined' && module.exports) { module.exports = root.LH_MBZ; }
})(typeof window !== 'undefined' ? window : this);
