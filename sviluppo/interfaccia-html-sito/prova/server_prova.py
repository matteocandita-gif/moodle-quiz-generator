"""Server per provare in locale l'anteprima PHP dell'interfaccia: serve i file del repository e risponde a
POST /esegui come il servizio web di CodeRunner con Jobe (esegue il programma dell'anteprima con python3,
php e sqlite3; dove sqlite3 manca usa sqlite3_cli.py, e php parte senza estensioni come su Jobe).

    python3 server_prova.py      poi http://localhost:8765/sviluppo/interfaccia-html-sito/prova/prova-coderunner.html?php=1"""
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", "..", ".."))
sys.path.insert(0, os.path.join(RADICE, "plugins", "moodle-quiz-generator", "skills", "materiali-moodle", "scripts"))
import da_dashboard  # noqa: E402


class Gestore(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=RADICE, **k)

    def log_message(self, *a):
        pass

    def do_POST(self):
        if self.path != "/esegui":
            self.send_error(404)
            return
        args = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with tempfile.TemporaryDirectory() as d:
            for nome, testo in json.loads(args.get("files") or "{}").items():
                with open(os.path.join(d, nome), "w", encoding="utf-8") as f:
                    f.write(testo)
            with open(os.path.join(d, "__tester__.python3"), "w", encoding="utf-8") as f:
                f.write(args["sourcecode"])
            r = subprocess.run([sys.executable, "__tester__.python3"], cwd=d, capture_output=True, text=True,
                               timeout=20, env=da_dashboard.ambiente_php(d))
        # come qtype_coderunner_run_in_sandbox: il risultato della sandbox di CodeRunner, non quello grezzo di Jobe
        risposta = json.dumps({"error": 0, "result": 15 if r.returncode == 0 else 12, "cmpinfo": "",
                               "output": r.stdout, "stderr": r.stderr}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(risposta.decode()).encode())   # come il servizio: una stringa JSON


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("localhost", 8765), Gestore).serve_forever()
