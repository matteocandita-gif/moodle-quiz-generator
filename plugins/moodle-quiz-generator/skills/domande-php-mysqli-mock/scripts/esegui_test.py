#!/usr/bin/env python3
"""Esegue un test di una domanda php_mysqli_mock in locale, come farebbe Jobe.

Uso:
    python3 esegui_test.py CAMPO_TEST.php CODICE_STUDENTE.php [OUTPUT_ATTESO.txt]

CAMPO_TEST.php contiene il codice del campo Test (senza tag <?php);
CODICE_STUDENTE.php contiene la risposta (soluzione o preload), che inizia con <?php.
Se si passa anche il file con l'output atteso, lo script dice se coincide.

PHP viene lanciato con -n (nessun php.ini): così l'estensione mysqli non viene
caricata, come richiesto dal mock, e gli avvisi finiscono nell'output.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

PLACEHOLDER_TEST = "{{ TEST.testcode }}"
PLACEHOLDER_RISPOSTA = "{{ STUDENT_ANSWER }}"


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    if not shutil.which("php"):
        sys.exit("PHP non è disponibile in questo ambiente: verifica gli output a mano.")

    radice = pathlib.Path(__file__).resolve().parent.parent
    template = (radice / "assets" / "prototipo-mock-template.php").read_text(encoding="utf-8")
    campo_test = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    risposta = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")

    if PLACEHOLDER_TEST not in template or PLACEHOLDER_RISPOSTA not in template:
        sys.exit("Il template non contiene i segnaposto Twig attesi.")
    programma = template.replace(PLACEHOLDER_TEST, campo_test).replace(PLACEHOLDER_RISPOSTA, risposta)

    with tempfile.NamedTemporaryFile("w", suffix=".php", delete=False, encoding="utf-8") as f:
        f.write(programma)
        percorso = f.name

    esito = subprocess.run(
        ["php", "-n", "-d", "display_errors=stdout", percorso],
        capture_output=True, text=True,
    )
    output = esito.stdout
    print(output, end="" if output.endswith("\n") else "\n")
    if esito.stderr:
        print("--- stderr ---\n" + esito.stderr, file=sys.stderr)

    if len(sys.argv) == 4:
        atteso = pathlib.Path(sys.argv[3]).read_text(encoding="utf-8")
        if output.rstrip() == atteso.rstrip():
            print("=== OK: l'output coincide con quello atteso ===")
        else:
            print("=== DIVERSO dall'output atteso ===")
            sys.exit(1)


if __name__ == "__main__":
    main()
