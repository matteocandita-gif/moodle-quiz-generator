"""Prove del template su consegne giuste e sbagliate."""
from domande import *
from prova import esegui

q1 = [c for c, _ in Q1_TEST]
q2 = [c for c, _ in Q2_TEST]
fallite = 0


def mostra(titolo, uscite, attese):
    global fallite
    print("=" * 70)
    print(titolo)
    for (codice, uscita, attesa) in zip(attese[0], uscite, attese[1]):
        ok = (uscita == "OK") == attesa
        if not ok:
            fallite += 1
        segno = "  " if ok else "!!"
        print("%s %-45s %s" % (segno, codice.replace("\n", " / ")[:45], uscita.replace("\n", " | ")))
    if len(uscite) != len(attese[0]):
        fallite += 1
        print("!! numero di uscite diverso:", len(uscite), uscite)


def html(s):
    return s.encode("utf-8")


# --- domanda 1
mostra("Q1 corretta, allegato index.html",
       esegui(q1, {"index.html": html(Q1_SOLUZIONE)}, pagina="index.html"), (q1, [True] * 7))

mostra("Q1 corretta, incollata nella casella",
       esegui(q1, risposta=Q1_SOLUZIONE, pagina="index.html"), (q1, [True] * 7))

mostra("Q1 salvata in ANSI (cp1252) con accenti",
       esegui(q1, {"index.html": Q1_SOLUZIONE.replace("indipendente", "più indipendente").encode("cp1252")},
              pagina="index.html"), (q1, [True] * 7))

sbagliata = (Q1_SOLUZIONE.replace("<title>Libreria Pagina 42</title>\n</head>\n<body>",
                                  "</head>\n<body>\n<title>Libreria Pagina 42</title>")
             .replace("<li>Carta regalo</li>", "<li>Carta regalo")
             .replace("<ul>", "<ol>").replace("</ul>", "</ol>")
             .replace("<h1>Libreria Pagina 42</h1>", "<h1>Libreria</h1>"))
mostra("Q1 sbagliata: title nel body, li non chiuso, ol al posto di ul, h1 diverso",
       esegui(q1, {"index.html": html(sbagliata)}, pagina="index.html"),
       (q1, [False, False, False, True, True, False, True]))

mostra("Q1 file chiamato Index.html",
       esegui(q1, {"Index.html": html(Q1_SOLUZIONE)}, pagina="index.html"), (q1, [False] * 7))

mostra("Q1 senza parametro pagina, unico file con un altro nome",
       esegui(q1, {"pagina.html": html(Q1_SOLUZIONE)}), (q1, [True] * 7))

mostra("Q1 consegna di un .docx",
       esegui(q1, {"pagina.docx": b"PK..."}), (q1, [False] * 7))

# --- domanda 2
mostra("Q2 corretta, zip con cartella libreria/",
       esegui(q2, {"libreria.zip": zip_sito(q2_file_corretti())}, pagina="index.html"), (q2, [True] * 7))

mostra("Q2 corretta, zip senza cartella esterna",
       esegui(q2, {"sito.zip": zip_sito(q2_file_corretti(), "")}, pagina="index.html"), (q2, [True] * 7))

f = q2_file_corretti()
f["index.html"] = (Q2_INDEX.replace('src="img/logo.png"', 'src="img/Logo.png"')
                   .replace('href="pagine/contatti.html"', 'href="contatti.html"'))
f["pagine/contatti.html"] = Q2_CONTATTI.replace('href="../index.html"', 'href="C:\\Users\\Mario\\sito\\index.html"')
mostra("Q2 sbagliata: Logo con maiuscola, link senza cartella, percorso assoluto del PC",
       esegui(q2, {"libreria.zip": zip_sito(f)}, pagina="index.html"),
       (q2, [True, True, False, True, False, False, False]))

f = q2_file_corretti()
del f["img/logo.png"]
f["index.html"] = Q2_INDEX.replace(' alt="Logo della Libreria Pagina 42"', "")
mostra("Q2 sbagliata: manca il logo, img senza alt",
       esegui(q2, {"libreria.zip": zip_sito(f)}, pagina="index.html"),
       (q2, [False, True, False, False, True, True, False]))

f = q2_file_corretti()
f["img\\logo.png"] = f.pop("img/logo.png")
f["index.html"] = Q2_INDEX.replace('src="img/logo.png"', 'src="img\\logo.png"')
mostra("Q2 zip con separatore \\ e src con \\",
       esegui(q2, {"libreria.zip": zip_sito(f)}, pagina="index.html"),
       (q2, [True, True, False, True, True, True, False]))

mostra("Q2 zip rovinato",
       esegui(q2, {"libreria.zip": b"non sono uno zip"}, pagina="index.html"), (q2, [False] * 7))

# --- confronto con la soluzione (funzione ripresa dal prototipo del collega)
conf = ["struttura_come_soluzione()"]
mostra("confronto: uguale con testo diverso",
       esegui(conf, risposta=Q1_SOLUZIONE.replace("Carta regalo", "Spedizioni"), soluzione=Q1_SOLUZIONE),
       (conf, [True]))
mostra("confronto: manca l'ultimo paragrafo",
       esegui(conf, risposta=Q1_SOLUZIONE.replace("<p>Via dei Libri 42, Bologna.</p>\n", ""),
              soluzione=Q1_SOLUZIONE), (conf, [False]))
mostra("confronto: h3 al posto di h2",
       esegui(conf, risposta=Q1_SOLUZIONE.replace("h2>Dove", "h3>Dove").replace("siamo</h2>", "siamo</h3>"),
              soluzione=Q1_SOLUZIONE), (conf, [False]))

print("\nPROVE FALLITE:", fallite)
