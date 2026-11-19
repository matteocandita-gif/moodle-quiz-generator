"""Prove del sito scritto con l'editor (interfaccia html_sito): JSON nella risposta, anche dentro la
serializzazione dell'interfaccia Html, immagini fornite (file di supporto o segnaposto) e caricate."""
import base64
import json

from prova import esegui
fallite = 0
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
INDEX = """<!DOCTYPE html>
<html><head><title>Da Mario</title><link rel="stylesheet" href="css/stile.css"></head>
<body><img src="img/logo.png" alt="logo"><h1>Pizzeria</h1><a href="pagine/menu.html">Menu</a></body></html>
"""
MENU = """<!DOCTYPE html>
<html><head><title>Menu</title><link rel="stylesheet" href="../css/stile.css"></head>
<body><h1>Menu</h1><img src="../img/foto.jpg" alt="foto"><a href="../index.html">Home</a></body></html>
"""


def sito(**cambia):
    s = {"htmlve": 1, "versione": "0.6.0", "salvato": "2026-11-19T10:00:00.000Z",
         "cartelle": ["css", "img", "pagine"],
         "files": {"index.html": INDEX, "pagine/menu.html": MENU, "css/stile.css": "h1 { color: red; }"},
         "immagini": {"img/logo.png": "logo.png",
                      "img/foto.jpg": "data:image/png;base64," + base64.b64encode(PNG).decode()}}
    s.update(cambia)
    return json.dumps(s)


def una(codice, risposta, attesa, titolo, supporto=None, soluzione=""):
    global fallite
    u = esegui([codice], risposta=risposta, soluzione=soluzione, pagina="index.html", supporto=supporto)[0]
    ok = (u == "OK") == attesa
    fallite += not ok
    print("%s %-55s %s" % ("  " if ok else "!!", titolo, u.replace("\n", " | ")))


una("struttura_base()", sito(), True, "JSON dell'editor nella risposta")
una("struttura_base()", json.dumps({"crui_sito": [sito()]}), True, "JSON dentro la serializzazione Html")
una('cartella_ben_formata(pagine="pagine")', sito(), True, "cartelle del sito ricreate")
una('css_collegato("css/stile.css")', sito(), True, "CSS collegato")
una('link_validi("index.html", "pagine/menu.html")', sito(), True, "link e immagini validi")
una('immagine("img/logo.png")', sito(), True, "immagine fornita senza file di supporto (segnaposto)")
una('immagine("img/logo.png")', sito(), True, "immagine fornita dal file di supporto", supporto={"logo.png": PNG})
una('file_presente("img/foto.jpg")', sito(), True, "immagine caricata dallo studente")
una('link_validi()', sito(immagini={"logo.png": "logo.png"}), False, "logo fuori dalla cartella img")
una('cartella_ben_formata()', sito(immagini={"logo.png": "logo.png"}), False, "immagine nella cartella sbagliata")
una('file_presente("x.html")', sito(files={"index.html": INDEX, "../x.html": "fuori"}), False, "percorso che esce dalla cartella")
una("struttura_base()", sito(files={}), False, "sito senza pagine")
una("struttura_base()", "<!DOCTYPE html><html><head><title>t</title></head><body></body></html>", True,
    "risposta HTML normale (non dall'editor)")
una("struttura_come_soluzione()", sito(), True, "soluzione dell'autore scritta con l'editor", soluzione=sito())
print("PROVE EDITOR FALLITE:", fallite)
