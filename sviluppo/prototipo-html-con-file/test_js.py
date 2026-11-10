"""Prove dei controlli JavaScript (domanda 4), con node e senza node (ripiego)."""
from domande import *
from prova import esegui

q4 = [c for c, _ in Q4_TEST]
fallite = 0
T, F = True, False


def prova(titolo, file, attese, senza_node=False):
    global fallite
    uscite = esegui(q4, {"libreria.zip": zip_sito(file)}, pagina="index.html", senza_node=senza_node)
    print("=" * 70)
    print(titolo + ("  [SENZA NODE]" if senza_node else ""))
    for codice, uscita, attesa in zip(q4, uscite, attese):
        ok = (uscita == "OK") == attesa
        fallite += not ok
        print("%s %-32s %s" % ("  " if ok else "!!", codice[:32], uscita.replace("\n", " | ")))
    if len(uscite) != len(q4):
        fallite += 1
        print("!! uscite:", uscite)


for sn in (False, True):
    prova("Q4 corretta", q4_file_corretti(), [T] * 8, sn)

    f = q4_file_corretti()
    f["js/script.js"] = Q4_JS.replace('paragrafo.textContent = "Dal', 'paragrafo.textContent = Dal')
    prova("stringa senza virgolette di apertura", f, [T, T, T, F, T, T, T, T], sn)

    f = q4_file_corretti()
    f["js/script.js"] = Q4_JS.replace("19.30\";\n}", "19.30\";\n")
    prova("manca la } della funzione", f, [T, T, T, F, T, T, T, T], sn)

    f = q4_file_corretti()
    f["js/script.js"] = Q4_JS.replace('addEventListener("click", mostraOrari);', 'addEventListener("click", mostraOrari;')
    prova("manca una )", f, [T, T, T, F, T, T, T, T], sn)

f = q4_file_corretti()
f["js/script.js"] = Q4_JS.replace('getElementById("orari")', 'getElementById("Orari")').replace(
    "function mostraOrari()", "function mostraorari()")
prova("id e funzione con maiuscole sbagliate", f, [T, T, T, T, F, T, F, T])

f = q4_file_corretti()
f["index.html"] = Q4_INDEX.replace('<script src="js/script.js"></script>\n', '').replace(
    "</head>", '<script src="js/script.js"></script>\n</head>')
prova("script nel head senza defer", f, [T, T, F, T, T, T, T, T])

f = q4_file_corretti()
f["index.html"] = Q4_INDEX.replace('<script src="js/script.js"></script>\n', '').replace(
    "</head>", '<script src="js/script.js" defer></script>\n</head>')
prova("script nel head con defer", f, [T] * 8)

f = q4_file_corretti()
f["script.js"] = f.pop("js/script.js")
f["index.html"] = Q4_INDEX.replace('src="js/script.js"', 'src="script.js"')
prova("script nella cartella principale", f, [F, F, T, T, T, T, T, T])

f = q4_file_corretti()
del f["js/script.js"]
f["index.html"] = Q4_INDEX.replace('<button id="pulsante-orari">', '<button id="pulsante-orari" onclick="mostraOrari()">').replace(
    '<script src="js/script.js"></script>', "<script>\nfunction mostraOrari() {\n  document.getElementById('orari').textContent = 'ciao';\n}\n</script>")
prova("tutto dentro la pagina, con onclick", f, [T, F, T, T, T, F, T, F])

f = q4_file_corretti()
f["js/script.js"] = Q4_JS.replace("function mostraOrari() {", "const mostraOrari = () => {").replace(
    'document.getElementById("pulsante-orari")', 'document.querySelector("#pulsante-orari")')
prova("funzione a freccia e querySelector", f, [T] * 8)

f = q4_file_corretti()
f["js/script.js"] = "// document.getElementById(\"nonce\").addEventListener(...)\n" + Q4_JS.replace(
    'document.getElementById("pulsante-orari").addEventListener("click", mostraOrari);',
    '// addEventListener lo aggiungo dopo')
prova("addEventListener solo nei commenti", f, [T, T, T, T, T, F, T, T])

# errore in uno script dentro la pagina: il numero di riga deve essere quello della pagina
pagina = Q4_INDEX.replace('<script src="js/script.js"></script>', "<script>\nlet x = (1 + 2;\n</script>")
uscita = esegui(["js_senza_errori()"], {"libreria.zip": zip_sito({"index.html": pagina})}, pagina="index.html")
print("=" * 70, "\nscript nella pagina con errore (riga attesa 12):", uscita)
fallite += "riga 12" not in uscita[0]
uscita = esegui(["js_senza_errori()"], {"libreria.zip": zip_sito({"index.html": pagina})}, pagina="index.html",
                senza_node=True)
print("stesso, senza node:", uscita)
fallite += "riga 12" not in uscita[0]
print("diagnosi:", esegui(["diagnosi_node()"], {"index.html": Q4_INDEX.encode()}, pagina="index.html"))
print("diagnosi senza node:", esegui(["diagnosi_node()"], {"index.html": Q4_INDEX.encode()}, pagina="index.html", senza_node=True))
print("\nPROVE JS FALLITE:", fallite)
