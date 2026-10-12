#!/usr/bin/env python3
"""Parte 2 in un comando: dal database esportato della dashboard al Moodle XML e al backup .mbz.

Uso:
    python3 genera_quiz.py EXPORT QUIZ_ID USCITA [--js=CARTELLA] [--sql=CARTELLA] [--php=CARTELLA] [--nome=BASE]
                           [--salta-coderunner] [--varianti=a[,b...]]

EXPORT, QUIZ_ID, USCITA  come per da_dashboard.py
--js=CARTELLA   cartella scripts/ della skill domande-coderunner-js (serve se il quiz ha righe
                CodeRunner JavaScript); se manca la cerca accanto a materiali-moodle
--sql=CARTELLA  cartella scripts/ della skill domande-coderunner-sql (righe CodeRunner SQL);
                se manca la cerca accanto a materiali-moodle
--php=CARTELLA  cartella scripts/ della skill domande-php-mysqli-mock (righe CodeRunner PHP)
--nome=BASE     nome dei file prodotti (predefinito: quiz)
--varianti=a    verifiche ripetibili: genera solo le varianti indicate (lettera finale della posizione);
                le righe senza tag restano tutte (vedi da_dashboard.py)

Esegue, nella cartella dove sta (insieme agli script di materiali-moodle):
  1. da_dashboard.py            -> specifica.txt, specifica-js.txt, specifica-sql.txt, impaginazione.json
  2. crea_xml.py                -> parti/domande.xml
  3. crea_xml.py della skill JS -> parti/coderunner-js.xml (gli output attesi li calcola Node);
     esercizi liberi HTML/CSS e corrispondenze li scrive già da_dashboard.py in domande-dirette.xml
  3c. php_attesi.py (output attesi eseguendo la soluzione con PHP e il template del prototipo) e
      crea_xml.py --verifica della skill PHP -> parti/coderunner-php.xml
  3b. crea_xml.py della skill SQL -> parti/coderunner-sql.xml (costruisce i database, calcola gli output
     con l'emulatore di sqlite3 e allega il database a ogni domanda)
  4. unisci_xml.py              -> BASE.xml (poi i tag delle varianti, se ci sono)
  5. controlla_xml.py
  6. crea_mbz.py                -> BASE.mbz (solo se non mancano righe: con --salta-coderunner no)
Si ferma al primo passo che fallisce e ne mostra l'output.
"""
import glob
import html
import json
import re
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))


def esegui(args, passo):
    print("== %s" % passo)
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        print(out)
    if r.returncode != 0:
        raise SystemExit("FERMO al passo «%s»" % passo)


def metti_tag(percorso, tag_nomi):
    """Aggiunge <tags> alle domande dell'XML finale (le varianti delle verifiche ripetibili)."""
    testo = open(percorso, encoding="utf-8").read()
    fatti = []

    def sost(m):
        blocco = m.group(0)
        n = re.search(r"<name>\s*<text>(.*?)</text>", blocco, re.S)
        nome = html.unescape(n.group(1)) if n else None
        if nome in tag_nomi and "<tags>" not in blocco:
            fatti.append(nome)
            t = html.escape(tag_nomi[nome], quote=False)
            return blocco.replace("</question>", "    <tags>\n      <tag><text>%s</text></tag>\n    </tags>\n  </question>" % t)
        return blocco
    testo = re.sub(r'<question type="(?!category)[^"]*">.*?</question>', sost, testo, flags=re.S)
    mancano = sorted(set(tag_nomi) - set(fatti))
    if mancano:
        raise SystemExit("FERMO: domande con tag non trovate nell'XML: %s" % mancano)
    open(percorso, "w", encoding="utf-8").write(testo)
    return "OK: %d domande con tag" % len(fatti)


def cerca_js(skill="domande-coderunner-js"):
    """Cartella scripts/ di una skill sorella: prima accanto a questa skill (stesso plugin),
    poi nelle cartelle dove Claude installa le skill."""
    for pat in [os.path.join(QUI, "..", "..", skill, "scripts"),
                os.path.join(QUI, "..", skill, "scripts"),
                "/mnt/skills/*/%s/scripts" % skill,
                "/mnt/skills/*/*/%s/scripts" % skill,
                "/root/.claude/skills/*/%s/scripts" % skill,
                "/root/.claude/skills/*/*/%s/scripts" % skill,
                os.path.expanduser("~/.claude/skills/*/*/%s/scripts" % skill)]:
        for d in glob.glob(pat):
            if os.path.exists(os.path.join(d, "crea_xml.py")):
                return os.path.abspath(d)
    return None


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) != 3:
        raise SystemExit(__doc__)
    export, qid, usc = a
    opz = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
    salta = "--salta-coderunner" in sys.argv
    base = opz.get("nome", "quiz")
    parti = os.path.join(usc, "parti")
    os.makedirs(parti, exist_ok=True)

    esegui([os.path.join(QUI, "da_dashboard.py"), export, qid, usc] + (["--salta-coderunner"] if salta else [])
           + (["--varianti=" + opz["varianti"]] if opz.get("varianti") else []), "conversione dal database")
    xmls = []
    if "=== question" in open(os.path.join(usc, "specifica.txt"), encoding="utf-8").read():
        xmls.append(os.path.join(parti, "domande.xml"))
        esegui([os.path.join(QUI, "crea_xml.py"), os.path.join(usc, "specifica.txt"), xmls[0]], "XML delle domande")
    spec_js = os.path.join(usc, "specifica-js.txt")
    if os.path.exists(spec_js):
        js = opz.get("js") or cerca_js()
        if not js:
            raise SystemExit("Servono gli script di domande-coderunner-js: indica la cartella con --js=")
        xmls.append(os.path.join(parti, "coderunner-js.xml"))
        esegui([os.path.join(js, "crea_xml.py"), spec_js, xmls[-1]], "XML CodeRunner JavaScript")
    spec_sql = os.path.join(usc, "specifica-sql.txt")
    if os.path.exists(spec_sql):
        sq = opz.get("sql") or cerca_js("domande-coderunner-sql")
        if not sq:
            raise SystemExit("Servono gli script di domande-coderunner-sql: indica la cartella con --sql=")
        xmls.append(os.path.join(parti, "coderunner-sql.xml"))
        esegui([os.path.join(sq, "crea_xml.py"), spec_sql, xmls[-1], "--cartella-db", os.path.join(usc, "database")],
               "XML CodeRunner SQL")
    spec_php = os.path.join(usc, "specifica-php.txt")
    if os.path.exists(spec_php):
        ph = opz.get("php") or cerca_js("domande-php-mysqli-mock")
        if not ph:
            raise SystemExit("Servono gli script di domande-php-mysqli-mock: indica la cartella con --php=")
        sys.path.insert(0, QUI)
        from php_attesi import prepara_sqlite3
        print("== client sqlite3 per PHP: " + prepara_sqlite3())   # anche per i sottoprocessi
        esegui([os.path.join(QUI, "php_attesi.py"), spec_php, "--php=" + ph], "output attesi PHP")
        xmls.append(os.path.join(parti, "coderunner-php.xml"))
        esegui([os.path.join(ph, "crea_xml.py"), spec_php, xmls[-1], "--verifica"], "XML CodeRunner PHP")
    web = os.path.join(usc, "domande-dirette.xml")
    if os.path.exists(web):
        xmls.append(web)
    if not xmls:
        raise SystemExit("Nessuna domanda da convertire")
    finale = os.path.join(usc, base + ".xml")
    if len(xmls) > 1:
        esegui([os.path.join(QUI, "unisci_xml.py"), finale] + xmls, "unione")
    else:
        open(finale, "w", encoding="utf-8").write(open(xmls[0], encoding="utf-8").read())
    ptag = os.path.join(usc, "tag.json")
    if os.path.exists(ptag):
        print("== tag delle varianti")
        print(metti_tag(finale, json.load(open(ptag, encoding="utf-8"))))
    esegui([os.path.join(QUI, "controlla_xml.py"), finale], "controllo")
    if salta:
        print("== .mbz non creato: mancano le righe CodeRunner lasciate fuori. Uniscile all'XML e lancia crea_mbz.py.")
        return
    esegui([os.path.join(QUI, "crea_mbz.py"), finale, os.path.join(usc, "impaginazione.json"),
            os.path.join(usc, base + ".mbz")], "backup .mbz")
    print("FATTO: %s e %s" % (finale, os.path.join(usc, base + ".mbz")))


if __name__ == "__main__":
    main()
