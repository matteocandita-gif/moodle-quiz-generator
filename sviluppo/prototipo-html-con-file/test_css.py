"""Prove dei controlli su cartella, nomi e CSS (domanda 3)."""
from domande import *
from prova import esegui
import test_prove  # noqa: F401  (riesegue anche le prove delle domande 1 e 2)

q3 = [c for c, _ in Q3_TEST]
fallite = 0


def prova(titolo, file, attese, cartella="libreria/"):
    global fallite
    uscite = esegui(q3, {"libreria.zip": zip_sito(file, cartella)}, pagina="index.html")
    print("=" * 70)
    print(titolo)
    for codice, uscita, attesa in zip(q3, uscite, attese):
        ok = (uscita == "OK") == attesa
        fallite += not ok
        print("%s %-34s %s" % ("  " if ok else "!!", codice[:34], uscita.replace("\n", " | ")))
    if len(uscite) != len(q3):
        fallite += 1
        print("!! uscite:", uscite)


T = True
F = False
prova("Q3 corretta", q3_file_corretti(), [T] * 9)

f = q3_file_corretti(); f["Thumbs.db"] = b"x"; f["img/desktop.ini"] = b"x"
prova("Q3 corretta con Thumbs.db e desktop.ini (ignorati)", f, [T] * 9)

f = q3_file_corretti(); f["stile.css"] = f.pop("css/stile.css")
f["index.html"] = Q3_INDEX.replace('href="css/stile.css"', 'href="stile.css"')
prova("CSS nella cartella principale", f, [F, T, F, T, T, T, T, T, T])

f = q3_file_corretti(); f["css/Stile.css"] = f.pop("css/stile.css")
prova("Stile.css con la maiuscola, link a stile.css", f, [T, F, F, F, F, F, F, T, F])

f = q3_file_corretti(); f["img/foto libreria.jpg"] = PNG; f["Nuovo documento di testo.txt"] = b"ciao"
f["Immagini/logo.png"] = PNG
prova("file con spazio, .txt estraneo, cartella Immagini", f, [F, F, T, T, T, T, T, T, T])

f = q3_file_corretti()
f["css/stile.css"] = Q3_CSS.replace("color: #8b0000;\n}", "color: #8b0000\n  font-size: 2em;\n}").replace(
    "font-weight: bold;", "font-weight bold;")
prova("CSS: manca un ; e manca un :", f, [T, T, T, F, T, F, T, T, T])

f = q3_file_corretti()
f["css/stile.css"] = Q3_CSS.replace("h1 {\n  color: #8b0000;\n}", "h1 {\n  color: #8b0000;\n")
prova("CSS: manca la } di h1", f, [T, T, T, F, T, T, F, T, T])

f = q3_file_corretti()
f["index.html"] = Q3_INDEX.replace('class="evidenza"', 'class="Evidenza"').replace(
    "<h1>", '<h1 style="color: red;">')
prova("classe con la maiuscola e attributo style", f, [T, T, T, T, T, T, F, F, T])

f = q3_file_corretti()
f["index.html"] = Q3_INDEX.replace('<link rel="stylesheet" href="css/stile.css">', '<link href="css/stile.css">')
prova("link senza rel=stylesheet", f, [T, T, F, F, F, F, F, T, T])

f = q3_file_corretti()
f["index.html"] = Q3_INDEX.replace('<link rel="stylesheet" href="css/stile.css">\n', '').replace(
    "</head>", "<style>\nh1 { color: red; }\n</style>\n</head>")
prova("stile in <style> invece del file", f, [T, T, F, F, F, F, F, F, T])

f = q3_file_corretti()
f["css/stile.css"] = "@charset \"UTF-8\";\n" + Q3_CSS + "\n@media (max-width: 600px) {\n  h1 { font-size: 1.5em; }\n}\n"
prova("CSS con @charset e @media", f, [T] * 9)

prova("zip senza cartella esterna", q3_file_corretti(), [T] * 9, cartella="")

# strutture diverse chieste dalla domanda
def una(codice, file, attesa, titolo):
    global fallite
    uscita = esegui([codice], {"libreria.zip": zip_sito(file)}, pagina="index.html")[0]
    ok = (uscita == "OK") == attesa
    fallite += not ok
    print("%s %-60s %s" % ("  " if ok else "!!", titolo, uscita.replace("\n", " | ")))

print("=" * 70)
f = q3_file_corretti(); f["pagine/contatti.html"] = Q2_CONTATTI
una('cartella_ben_formata(pagine="pagine")', f, True, "pagine in pagine/")
f = q3_file_corretti(); f["contatti.html"] = Q2_CONTATTI
una('cartella_ben_formata(pagine="pagine")', f, False, "contatti.html nella cartella principale")
una('cartella_ben_formata()', f, True, "senza pagine=: va bene ovunque")
f = q3_file_corretti(); f["risorse/css/stile.css"] = f.pop("css/stile.css")
una('cartella_ben_formata(css="risorse/css")', f, True, "css annidato in risorse/css")
una('cartella_ben_formata()', f, False, "css annidato ma la domanda vuole css/")
f = q3_file_corretti(); f["immagini/logo.png"] = f.pop("img/logo.png")
una('cartella_ben_formata(img="immagini")', f, True, "immagini/ al posto di img/")

# classi_coerenti su un caso a parte
uscita = esegui(["classi_coerenti()"], {"libreria.zip": zip_sito(
    {"index.html": Q3_INDEX.replace('class="evidenza"', 'class="evidenzia"'), "css/stile.css": Q3_CSS,
     "img/logo.png": PNG})}, pagina="index.html")
print("=" * 70, "\nclassi_coerenti con errore di battitura:", uscita)
fallite += uscita[0] == "OK"

print("\nPROVE CSS FALLITE:", fallite)
