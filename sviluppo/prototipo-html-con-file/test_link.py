"""Prove delle funzioni ancore_valide, link_esterno, uno_tra."""
from prova import esegui
fallite = 0
BASE = """<!DOCTYPE html>
<html><head><title>Sito</title></head>
<body>
<h1>La nostra scuola</h1>
<p><a href="#dove">dove siamo</a>, <a href="#contatti">contatti</a></p>
<h2 id="dove">Dove siamo</h2>
<p>Bologna.</p>
<h2 id="contatti">Contatti</h2>
<p>Sul <a href="https://www.salvemini.bo.it" target="_blank">sito</a>.</p>
</body></html>
"""
def una(codice, pagina, attesa, titolo):
    global fallite
    u = esegui([codice], {"index.html": pagina.encode()}, pagina="index.html")[0]
    ok = (u == "OK") == attesa
    fallite += not ok
    print("%s %-45s %s" % ("  " if ok else "!!", titolo, u.replace("\n", " | ")))

una("ancore_valide(2)", BASE, True, "due ancore giuste")
una("ancore_valide(2)", BASE.replace('id="contatti"', 'id="dove"'), False, "id ripetuto")
una("ancore_valide(2)", BASE.replace('href="#contatti"', 'href="contatti"'), False, "href senza #")
una("ancore_valide(2)", BASE.replace('href="#contatti"', 'href="#Contatti"'), False, "maiuscola nell'href")
una("ancore_valide(3)", BASE, False, "ne servono tre")
una("link_esterno(nuova_scheda=True)", BASE, True, "link esterno con nuova scheda")
una("link_esterno(nuova_scheda=True)", BASE.replace(' target="_blank"', ''), False, "senza target")
una("link_esterno()", BASE.replace(' target="_blank"', ''), True, "senza target ma non richiesto")
una("link_esterno(nuova_scheda=True)", BASE.replace('https://www.', 'www.'), False, "www senza https")
una('uno_tra("p", "ul", "ol")', BASE, True, "c'è un paragrafo")
una('uno_tra("p", "ul", "ol")', "<html><body><h1>Orari</h1><ul><li>8-13</li></ul></body></html>", True, "c'è una lista")
una('uno_tra("p", "ul", "ol")', "<html><body><h1>Orari</h1></body></html>", False, "solo il titolo")
print("PROVE LINK FALLITE:", fallite)
