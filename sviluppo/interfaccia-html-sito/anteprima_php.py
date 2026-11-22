"""Anteprima delle pagine PHP nell'editor html_sito: questo programma lo manda l'interfaccia a Jobe con il
servizio web di CodeRunner (qtype_coderunner_run_in_sandbox), insieme al file richiesta.json con il sito
e la richiesta. Esegue la pagina come il controllo del prototipo php_sito (stesso avvio di PHP, stessa
facciata di mysqli) e stampa un JSON: {"html": quello che stampa la pagina, "stato": il database dopo
la richiesta, in base64}. Lo stato torna all'interfaccia, che lo rimanda alla richiesta successiva:
così l'INSERT di un modulo si vede poi nella pagina dell'elenco, come con XAMPP.

Non si modifica il file costruito: build.py ci mette AVVIO_PHP (da template.py del prototipo) e la
facciata di mysqli (da domande-php-mysqli-mock), negli stessi segnaposto qui sotto."""
import base64
import json
import os
import re
import subprocess

AVVIO_PHP = __AVVIO_PHP__
FAKEDB_PHP = __FAKEDB_PHP__
TROPPO_LENTO = "La pagina non finisce entro 5 secondi: c'è un ciclo che non si ferma?"


def esci(**dati):
    print(json.dumps(dati, ensure_ascii=False))
    raise SystemExit(0)


def dati_php(coppie):
    """Le coppie [name, valore] del modulo come le riceve PHP: name[] diventa un array."""
    out = {}
    for nome, valore in coppie:
        if nome.endswith("[]"):
            out.setdefault(nome[:-2], []).append(valore)
        else:
            out[nome] = valore
    return out


r = json.load(open("richiesta.json", encoding="utf-8"))
radice = os.path.abspath("sito")
for percorso, contenuto in r["files"].items():
    parti = [p for p in str(percorso).split("/") if p not in ("", ".", "..")]
    if not parti:
        continue
    destinazione = os.path.join(radice, *parti)
    os.makedirs(os.path.dirname(destinazione), exist_ok=True)
    with open(destinazione, "w", encoding="utf-8") as f:
        f.write(contenuto)
pagina = "/".join(p for p in r["pagina"].split("/") if p not in ("", ".", ".."))
completo = os.path.join(radice, *pagina.split("/"))
if not os.path.isfile(completo):
    esci(errore="Non trovo la pagina %s." % pagina)

db = ""
if r.get("db"):
    db = os.path.abspath("lavoro.sqlite")
    if r.get("stato"):
        with open(db, "wb") as f:
            f.write(base64.b64decode(r["stato"]))
    else:
        try:   # il database si costruisce con la libreria SQLite di Python, se c'è; altrimenti con il client sqlite3
            import sqlite3
            con = sqlite3.connect(db)
            try:
                con.executescript(r["db"]["sql"])
                con.commit()
            except sqlite3.Error as e:
                esci(errore="Errore nel database della domanda (avvisa l'insegnante): %s" % e)
            finally:
                con.close()
        except ImportError:
            p = subprocess.run(["sqlite3", db], input=r["db"]["sql"] + "\n;\n", capture_output=True, text=True,
                               timeout=20)
            if p.stderr.strip():
                esci(errore="Errore nel database della domanda (avvisa l'insegnante): " + p.stderr.strip()[:300])
    with open("fakedb_php_sito.php", "w", encoding="utf-8") as f:
        f.write(FAKEDB_PHP)

with open("avvio_php_sito.php", "w", encoding="utf-8") as f:
    f.write(AVVIO_PHP)
metodo = "POST" if r.get("metodo") == "post" else "GET"
coppie = r.get("dati") or []
dati = {"get": dati_php(coppie) if metodo == "GET" else {}, "post": dati_php(coppie) if metodo == "POST" else {},
        "metodo": metodo, "pagina": pagina, "cartella": os.path.dirname(completo), "radice": radice,
        "file": os.path.basename(completo), "db": db, "fakedb": os.path.abspath("fakedb_php_sito.php"),
        "nomedb": r["db"].get("nomedb", "") if db else ""}
with open("dati_richiesta.json", "w", encoding="utf-8") as f:
    json.dump(dati, f)
try:
    p = subprocess.run(["php", "-d", "display_errors=stdout", "-d", "html_errors=0", "-d", "log_errors=0",
                        "-d", "error_reporting=E_ALL", "-d", "max_execution_time=3",
                        os.path.abspath("avvio_php_sito.php"), os.path.abspath("dati_richiesta.json")],
                       capture_output=True, text=True, timeout=6, cwd=radice)
    uscita = p.stdout + p.stderr
except subprocess.TimeoutExpired:
    uscita = TROPPO_LENTO
uscita = uscita.replace(radice + os.sep, "").replace(radice, "").replace(os.getcwd() + os.sep, "")
uscita = re.sub(r"(PHP )?Fatal error: +Maximum execution time of \d+ seconds? exceeded.*", TROPPO_LENTO, uscita)
uscita = re.sub(r" on line (\d+)", r" alla riga \1", uscita)
stato = ""
if db:
    with open(db, "rb") as f:
        stato = base64.b64encode(f.read()).decode("ascii")
esci(html=uscita, stato=stato)
