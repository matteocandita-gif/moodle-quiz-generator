"""Costruisce il prototipo CodeRunner html_con_file dal sorgente di questa cartella.

    python3 crea_prototipo.py               scrive il prototipo nell'asset del plugin e la tabella delle
                                            funzioni in tracce-consegna.md di progettazione-quiz
    python3 crea_prototipo.py --prove DIR   in più, le quattro domande di prova in DIR/prova_html_con_file.xml

Il template sta in template.py, la descrizione in testi.py: si modificano lì, mai nell'XML dell'asset.
Prima di rigenerare, le prove: python3 prove.py (README.md)."""
import base64
import html as _html
import json
import os
import re
import sys
import xml.dom.minidom

from domande import Q1_SOLUZIONE, Q1_TEST, Q2_TEST, Q3_TEST, Q4_TEST, q2_file_corretti, q3_file_corretti, q4_file_corretti, zip_sito
from testi import DESCRIZIONE_CSS_CON_TEST, DESCRIZIONE_PROTOTIPO, PROMEMORIA, TESTO_Q1, TESTO_Q2, TESTO_Q3, TESTO_Q4

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
SKILLS = os.path.join(RADICE, "plugins", "moodle-quiz-generator", "skills")
ASSET = os.path.join(SKILLS, "materiali-moodle", "assets", "prototipo-html-con-file.xml")
ASSET_CSS = os.path.join(SKILLS, "materiali-moodle", "assets", "prototipo-css-con-test.xml")
TRACCE = os.path.join(SKILLS, "progettazione-quiz", "references", "tracce-consegna.md")
INIZIO, FINE = "<!-- funzioni-html-con-file: inizio", "<!-- funzioni-html-con-file: fine -->"


def cdata(t):
    return "<![CDATA[" + (t or "").replace("]]>", "]]]]><![CDATA[>") + "]]>"


def esc(t):
    return _html.escape(t or "", quote=False)


def testcase(codice, descrizione):
    return f"""      <testcase testtype="0" useasexample="0" hiderestiffail="0" mark="1.0000000">
        <testcode>
          <text>{cdata(codice)}</text>
        </testcode>
        <stdin>
          <text></text>
        </stdin>
        <expected>
          <text>OK
</text>
        </expected>
        <extra>
          <text>{cdata(descrizione)}</text>
        </extra>
        <display>
          <text>SHOW</text>
        </display>
      </testcase>"""


def prototipo(tipo="html_con_file"):
    """Il prototipo html_con_file (file allegato) o css_con_test (casella di risposta): stesso template."""
    casella = tipo == "css_con_test"
    template = open(os.path.join(QUI, "template.py"), encoding="utf-8").read()
    colonne = json.dumps([["Controllo", "extra"], ["Trovato?", "got"]], ensure_ascii=False)
    return f"""  <question type="coderunner">
    <name>
      <text>PROTOTYPE - {tipo}</text>
    </name>
    <questiontext format="html">
      <text>{cdata(DESCRIZIONE_CSS_CON_TEST if casella else DESCRIZIONE_PROTOTIPO)}</text>
    </questiontext>
    <generalfeedback format="html">
      <text></text>
    </generalfeedback>
    <defaultgrade>1</defaultgrade>
    <penalty>0</penalty>
    <hidden>0</hidden>
    <idnumber></idnumber>
    <coderunnertype>{tipo}</coderunnertype>
    <prototypetype>2</prototypetype>
    <allornothing>0</allornothing>
    <penaltyregime>0</penaltyregime>
    <precheck>0</precheck>
    <hidecheck>0</hidecheck>
    <showsource>0</showsource>
    <answerboxlines>12</answerboxlines>
    <answerboxcolumns>100</answerboxcolumns>
    <answerpreload></answerpreload>
    <globalextra></globalextra>
    <useace>1</useace>
    <resultcolumns>{esc(colonne)}</resultcolumns>
    <template>{cdata(template)}</template>
    <iscombinatortemplate>1</iscombinatortemplate>
    <allowmultiplestdins>0</allowmultiplestdins>
    <answer></answer>
    <validateonsave>0</validateonsave>
    <testsplitterre>{cdata("|#<ab@17943918#@>#\\n|ms")}</testsplitterre>
    <language>python3</language>
    <acelang>{"css" if casella else "html"}</acelang>
    <sandbox></sandbox>
    <grader>EqualityGrader</grader>
    <cputimelimitsecs></cputimelimitsecs>
    <memlimitmb>1000</memlimitmb>
    <sandboxparams></sandboxparams>
    <templateparams>{esc(json.dumps({"pagina": "stile.css"})) if casella else ""}</templateparams>
    <hoisttemplateparams>1</hoisttemplateparams>
    <extractcodefromjson>1</extractcodefromjson>
    <templateparamslang>None</templateparamslang>
    <templateparamsevalpertry>0</templateparamsevalpertry>
    <templateparamsevald>{{}}</templateparamsevald>
    <twigall>0</twigall>
    <uiplugin>{"ace" if casella else "html"}</uiplugin>
    <uiparameters>{"" if casella else esc(json.dumps({"html_src": "prototypeextra", "enable_in_editor": False}))}</uiparameters>
    <attachments>{0 if casella else 1}</attachments>
    <attachmentsrequired>{0 if casella else 1}</attachmentsrequired>
    <maxfilesize>102400</maxfilesize>
    <filenamesregex>{"" if casella else esc(r".*\.(html|htm|zip)")}</filenamesregex>
    <filenamesexplain></filenamesexplain>
    <displayfeedback>1</displayfeedback>
    <giveupallowed>0</giveupallowed>
    <prototypeextra>{"" if casella else cdata(PROMEMORIA)}</prototypeextra>
    <testcases>
    </testcases>
  </question>
"""


def domanda(nome, testo, test, risposta="", allegati_risposta=None, regex=r".*\.html?",
            spiegazione="", richiesti=0, dimensione=102400, righe=12):
    file_risposta = ""
    if allegati_risposta:
        file_risposta = "    <answerfiles>\n" + "\n".join(
            f'      <file name="{n}" path="/" encoding="base64">{base64.b64encode(d).decode()}</file>'
            for n, d in allegati_risposta.items()) + "\n    </answerfiles>\n"
    return f"""  <question type="coderunner">
    <name>
      <text>{esc(nome)}</text>
    </name>
    <questiontext format="html">
      <text>{cdata(testo)}</text>
    </questiontext>
    <generalfeedback format="html">
      <text></text>
    </generalfeedback>
    <defaultgrade>1</defaultgrade>
    <penalty>0</penalty>
    <hidden>0</hidden>
    <idnumber></idnumber>
    <coderunnertype>html_con_file</coderunnertype>
    <prototypetype>0</prototypetype>
    <allornothing>0</allornothing>
    <penaltyregime>0</penaltyregime>
    <precheck>0</precheck>
    <hidecheck>0</hidecheck>
    <showsource>0</showsource>
    <answerboxlines>{righe}</answerboxlines>
    <answerboxcolumns>100</answerboxcolumns>
    <answerpreload></answerpreload>
    <globalextra></globalextra>
    <useace></useace>
    <resultcolumns></resultcolumns>
    <template></template>
    <iscombinatortemplate></iscombinatortemplate>
    <allowmultiplestdins></allowmultiplestdins>
    <answer>{cdata(risposta)}</answer>
    <validateonsave>1</validateonsave>
    <testsplitterre></testsplitterre>
    <language></language>
    <acelang></acelang>
    <sandbox></sandbox>
    <grader></grader>
    <cputimelimitsecs></cputimelimitsecs>
    <memlimitmb></memlimitmb>
    <sandboxparams></sandboxparams>
    <templateparams>{esc(json.dumps({"pagina": "index.html"}))}</templateparams>
    <hoisttemplateparams>1</hoisttemplateparams>
    <extractcodefromjson>1</extractcodefromjson>
    <templateparamslang>None</templateparamslang>
    <templateparamsevalpertry>0</templateparamsevalpertry>
    <templateparamsevald>{{}}</templateparamsevald>
    <twigall>0</twigall>
    <uiplugin></uiplugin>
    <uiparameters></uiparameters>
    <attachments>1</attachments>
    <attachmentsrequired>{richiesti}</attachmentsrequired>
    <maxfilesize>{dimensione}</maxfilesize>
    <filenamesregex>{esc(regex)}</filenamesregex>
    <filenamesexplain>{esc(spiegazione)}</filenamesexplain>
    <displayfeedback>1</displayfeedback>
    <giveupallowed>0</giveupallowed>
    <prototypeextra></prototypeextra>
    <testcases>
{chr(10).join(testcase(c, d) for c, d in test)}
    </testcases>
{file_risposta}  </question>
"""


def scrivi(percorso, domande):
    testo = '<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n' + "\n".join(domande) + "\n</quiz>\n"
    xml.dom.minidom.parseString(testo.encode("utf-8"))   # controlla che l'XML sia ben formato
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, "w", encoding="utf-8") as f:
        f.write(testo)
    print("scritto", os.path.relpath(percorso, RADICE), len(testo), "caratteri")


def tabella_funzioni():
    """La tabella delle funzioni in Markdown, per tracce-consegna.md (stesso elenco della descrizione)."""
    from testi import FUNZIONI_HTML, FUNZIONI_CARTELLA, FUNZIONI_CSS, FUNZIONI_STILE, FUNZIONI_JS
    def md(testo):
        # il codice in linea si mette da parte prima di togliere i tag, così <link> e <style> restano
        codici = []
        def tieni(m):
            codici.append("`%s`" % _html.unescape(m.group(1)))
            return "\x00%d\x00" % (len(codici) - 1)
        testo = re.sub(r'<span style="font-family: monospace;">(.*?)</span>', tieni, testo)
        testo = _html.unescape(re.sub(r"<[^>]+>", "", testo))
        testo = re.sub(r"\x00(\d+)\x00", lambda m: codici[int(m.group(1))], testo)
        return testo.replace("|", "\\|")
    parti = []
    for titolo, righe in (("La pagina HTML", FUNZIONI_HTML), ("La cartella del sito e i collegamenti", FUNZIONI_CARTELLA),
                          ("Il CSS", FUNZIONI_CSS), ("Il CSS nella pagina: `<style>` e attributo style", FUNZIONI_STILE),
                          ("Il JavaScript", FUNZIONI_JS)):
        parti.append("**%s**\n\n| Test | Che cosa controlla |\n|---|---|\n" % titolo
                     + "\n".join("| `%s` | %s |" % (f, md(d)) for f, d in righe))
    return "\n\n".join(parti)


def aggiorna_tracce():
    testo = open(TRACCE, encoding="utf-8").read()
    i, j = testo.index(INIZIO), testo.index(FINE)
    i = testo.index("-->", i) + 3
    nuovo = testo[:i] + "\n" + tabella_funzioni() + "\n" + testo[j:]
    if nuovo != testo:
        open(TRACCE, "w", encoding="utf-8").write(nuovo)
        print("aggiornata la tabella delle funzioni in", os.path.relpath(TRACCE, RADICE))


def main():
    scrivi(ASSET, [prototipo()])
    scrivi(ASSET_CSS, [prototipo("css_con_test")])
    aggiorna_tracce()
    if "--prove" in sys.argv:
        cartella = sys.argv[sys.argv.index("--prove") + 1]
        scrivi(os.path.join(cartella, "prova_html_con_file.xml"), [
            domanda("HTML prova - Pagina della libreria (file .html)", TESTO_Q1, Q1_TEST, risposta=Q1_SOLUZIONE,
                    regex=r"index\.html",
                    spiegazione="<p><strong>Il file deve chiamarsi index.html, tutto minuscolo.</strong></p>", richiesti=1, righe=10),
            domanda("HTML prova - Sito della libreria (cartella .zip)", TESTO_Q2, Q2_TEST,
                    allegati_risposta={"libreria.zip": zip_sito(q2_file_corretti())}, regex=r"libreria\.zip",
                    spiegazione="<p><strong>Il file deve chiamarsi libreria.zip, tutto minuscolo e senza spazi.</strong></p>", richiesti=1,
                    dimensione=10485760, righe=3),
            domanda("HTML prova - Sito della libreria con CSS (cartella .zip)", TESTO_Q3, Q3_TEST,
                    allegati_risposta={"libreria.zip": zip_sito(q3_file_corretti())}, regex=r"libreria\.zip",
                    spiegazione="<p><strong>Il file deve chiamarsi libreria.zip, tutto minuscolo e senza spazi.</strong></p>", richiesti=1,
                    dimensione=10485760, righe=3),
            domanda("HTML prova - Sito della libreria con JavaScript (cartella .zip)", TESTO_Q4, Q4_TEST,
                    allegati_risposta={"libreria.zip": zip_sito(q4_file_corretti())}, regex=r"libreria\.zip",
                    spiegazione="<p><strong>Il file deve chiamarsi libreria.zip, tutto minuscolo e senza spazi.</strong></p>", richiesti=1,
                    dimensione=10485760, righe=3),
        ])


if __name__ == "__main__":
    main()
