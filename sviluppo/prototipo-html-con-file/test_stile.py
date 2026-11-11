"""Prove dei controlli sul CSS scritto nella casella (prototipo css_con_test), sullo stile in linea
e sul <style> nella pagina."""
from prova import esegui

fallite = 0


def prova(titolo, testcodes, attese, risposta="", pagina="", allegati=None, contiene=None):
    """attese: True se il controllo deve dare OK. contiene: frammenti che devono comparire nei messaggi."""
    global fallite
    uscite = esegui(testcodes, allegati, risposta=risposta, pagina=pagina)
    print("=" * 70)
    print(titolo)
    for codice, uscita, attesa in zip(testcodes, uscite, attese):
        ok = (uscita == "OK") == attesa
        fallite += not ok
        print("%s %-40s %s" % ("  " if ok else "!!", codice[:40], uscita.replace("\n", " | ")))
    if len(uscite) != len(testcodes):
        fallite += 1
        print("!! uscite:", uscite)
    for frammento in contiene or []:
        if not any(frammento in u for u in uscite):
            fallite += 1
            print("!! nei messaggi manca:", frammento)


T, F = True, False

# ---------------------------------------------------------------- foglio di stile nella casella
CSS_TEST = ['css_senza_errori()', 'css_regola("p", "color", "blue")', 'css_regola("h1", "font-size")']
prova("CSS nella casella: giusto", CSS_TEST, [T, T, T], pagina="stile.css",
      risposta="p {\n  color: blue;\n}\nh1 {\n  font-size: 30px;\n}\n")
prova("CSS nella casella: ultimo ; facoltativo, maiuscole nel valore", CSS_TEST, [T, T, T], pagina="stile.css",
      risposta="p { color: Blue }\nh1 { font-size: 30px }")
prova("CSS nella casella: manca il ; tra due dichiarazioni", CSS_TEST, [F, F, T], pagina="stile.css",
      risposta="p {\n  color: blue\n  background-color: yellow;\n}\nh1 { font-size: 30px; }",
      contiene=["stile.css, regola «p» (riga 1): manca il ; dopo «color: blue»"])
prova("CSS nella casella: = al posto di :", CSS_TEST, [F, F, T], pagina="stile.css",
      risposta="p { color = blue; }\nh1 { font-size: 30px; }",
      contiene=["non è nella forma proprietà: valore"])
# come nel browser, la regola dopo la } mancante si perde
prova("CSS nella casella: manca la } di p", CSS_TEST, [F, T, F], pagina="stile.css",
      risposta="p {\n  color: blue;\n\nh1 {\n  font-size: 30px;\n}",
      contiene=["manca la } prima della regola successiva"])
prova("CSS nella casella: valore diverso", CSS_TEST, [T, F, T], pagina="stile.css",
      risposta="p { color: red; }\nh1 { font-size: 30px; }", contiene=['color vale "red": qui serve "blue"'])
prova("CSS nella casella: regola mancante", CSS_TEST, [T, T, F], pagina="stile.css",
      risposta="p { color: blue; }", contiene=["Nel CSS non c'è una regola per h1."])
prova("CSS nella casella: vuota", CSS_TEST, [F, F, F], pagina="stile.css", risposta="   ",
      contiene=["La risposta è vuota"])
prova("CSS nella casella: graffe mancanti", ['css_senza_errori()'], [F], pagina="stile.css",
      risposta="p color: blue;", contiene=["sta fuori da una regola"])

# ---------------------------------------------------------------- stile in linea (HTML nella casella)
LINEA_TEST = ['in_linea_senza_errori()', 'in_linea("p", "color", "green")', 'in_linea("h1", "font-size")']
GIUSTO = ('<h1 style="font-size: 40px;">Benvenuti</h1>\n'
          '<p style="color: green; background-color: yellow;">Orari</p>')
prova("In linea: giusto", LINEA_TEST, [T, T, T], pagina="index.html", risposta=GIUSTO)
prova("In linea: senza ; finale", LINEA_TEST, [T, T, T], pagina="index.html",
      risposta='<h1 style="font-size: 40px">Benvenuti</h1>\n<p style="color: green">Orari</p>')
prova("In linea: manca il ; tra due dichiarazioni", LINEA_TEST, [F, F, T], pagina="index.html",
      risposta=GIUSTO.replace("color: green;", "color: green"),
      contiene=["Riga 2, attributo style di <p>: manca il ; dopo «color: green»", "è scritta male"])
prova("In linea: graffe nell'attributo", LINEA_TEST, [F, T, T], pagina="index.html",
      risposta=GIUSTO.replace('style="color: green;', 'style="{color: green;').replace('yellow;"', 'yellow;}"'),
      contiene=["non ci vanno le graffe"])
prova("In linea: = al posto di :", LINEA_TEST, [F, F, T], pagina="index.html",
      risposta=GIUSTO.replace("color: green", "color=green"), contiene=["non è nella forma proprietà: valore"])
prova("In linea: style sul tag sbagliato", LINEA_TEST, [T, F, F], pagina="index.html",
      risposta='<h1>Benvenuti</h1>\n<p>Orari</p>\n<div style="color: green;">x</div>',
      contiene=["Nessun <p> ha l'attributo style.", "Nessun <h1> ha l'attributo style."])
prova("In linea: nessuno style", ['in_linea_senza_errori()'], [F], pagina="index.html",
      risposta="<p>Orari</p>", contiene=["nessun tag ha l'attributo style"])
prova("In linea: valore diverso", LINEA_TEST, [T, F, T], pagina="index.html",
      risposta=GIUSTO.replace("color: green;", "color: red;"), contiene=['color vale "red": qui serve "green"'])
prova("In linea: tag che manca", ['in_linea("table")'], [F], pagina="index.html", risposta=GIUSTO,
      contiene=["Nella pagina non c'è nessun <table>."])

# ---------------------------------------------------------------- <style> nella pagina
PAGINA = """<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Orari</title>
    <style>
        h1 {
            color: navy;
        }
        p {
            font-size: 18px;
            background-color: #eeeeee;
        }
    </style>
</head>
<body>
    <h1>Orari</h1>
    <p>Lunedì</p>
</body>
</html>
"""
STYLE_TEST = ['stile_interno()', 'stile_interno_senza_errori()', 'stile_interno_regola("h1", "color", "navy")',
              'stile_interno_regola("p", "font-size")', 'nessuno_stile_interno()']
prova("<style>: giusto", STYLE_TEST, [T, T, T, T, F], allegati={"orari.html": PAGINA.encode()},
      pagina="orari.html")
prova("<style>: giusto, nella casella", STYLE_TEST[:4], [T, T, T, T], risposta=PAGINA, pagina="orari.html")
prova("<style>: manca il ; (riga della pagina)", STYLE_TEST[:4], [T, F, T, F],
      allegati={"orari.html": PAGINA.replace("font-size: 18px;", "font-size: 18px").encode()},
      pagina="orari.html", contiene=["<style>, regola «p» (riga 10): manca il ; dopo «font-size: 18px»"])
prova("<style>: manca la } di h1", STYLE_TEST[:3], [T, F, T],
      allegati={"orari.html": PAGINA.replace("navy;\n        }", "navy;\n").encode()}, pagina="orari.html")
NEL_BODY = """<html>
<head>
    <title>Orari</title>
</head>
<body>
    <style>
        h1 { color: navy; }
    </style>
    <h1>Orari</h1>
</body>
</html>
"""
prova("<style> nel body", STYLE_TEST[:3], [F, T, T], allegati={"orari.html": NEL_BODY.encode()},
      pagina="orari.html", contiene=["deve stare dentro <head>"])
prova("<style>: vuoto", ['stile_interno()'], [F],
      allegati={"orari.html": b"<html><head><title>x</title><style>\n</style></head><body><p>x</p></body></html>"},
      pagina="orari.html", contiene=["il <style> è vuoto"])
prova("<style> mancante, c'è il link", STYLE_TEST[:3], [F, F, F],
      allegati={"orari.html": b'<html><head><title>x</title><link rel="stylesheet" href="s.css"></head>'
                              b'<body><h1>x</h1></body></html>'},
      pagina="orari.html", contiene=["lo stile è in un file CSS collegato"])
prova("<style> mancante, c'è style in linea", ['stile_interno()'], [F],
      allegati={"orari.html": b'<html><head><title>x</title></head><body><h1 style="color: navy">x</h1></body></html>'},
      pagina="orari.html", contiene=["con l'attributo style dentro i tag"])
prova("<style>: valore diverso", ['stile_interno_regola("h1", "color", "red")'], [F],
      allegati={"orari.html": PAGINA.encode()}, pagina="orari.html", contiene=['color vale "navy": qui serve "red"'])

print("FALLITE: %d" % fallite)
