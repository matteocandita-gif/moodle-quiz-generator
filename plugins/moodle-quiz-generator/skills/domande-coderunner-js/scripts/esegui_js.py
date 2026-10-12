"""Esegue in Node il programma che i prototipi JavaScript dell'utente costruiscono
su Jobe, per calcolare gli output attesi.

- prompt: "Javascript (con prompt)", versione 2 (parametri random e test_prima)
- gapfiller: "Javascript (con gapfiller)", con il random che riparte a ogni test
  dalla posizione scritta in Extra

Il programma è lo stesso del template; in più, su stderr, alcuni marcatori che
non cambiano l'output e servono solo ai controlli: input esauriti, sequenza
random ricominciata dall'inizio.
"""
import json
import pathlib
import re
import subprocess
import tempfile

RANDOM_PREDEFINITA = [0.15, 0.23, 0.52, 0.34, 0.75, 0.38, 0.62, 0.01, 0.29, 0.40,
                      0.92, 0.54, 0.42, 0.09, 0.10, 0.07, 0.88, 0.46, 0.01, 0.21,
                      0.17, 0.64, 0.06, 0.57, 0.25, 0.29, 0.81, 0.57, 0.02, 0.62,
                      0.03, 0.38, 0.64, 0.75, 0.22, 0.49, 0.89, 0.92, 0.13, 0.72]
SEPARATORE = "#<ab@17943918#@>#"
GAP_RE = re.compile(r"\{\[.*?\]\}")
M_PROMPT = "##PROMPT_OLTRE##"
M_RANDOM = "##RANDOM_RICOMINCIA##"

_SUPPORTO = """
global.prompt = () => {
    if (inputIndex >= inputs.length) process.stderr.write("%s\\n");
    return inputs[inputIndex++];
};
Math.random = () => {
    if (randomIndex >= randomValues.length) process.stderr.write("%s\\n");
    return randomValues[randomIndex++ %% randomValues.length];
};
""" % (M_PROMPT, M_RANDOM)


def programma_prompt(risposta, testcode, stdin, extra, random=None, test_prima=False):
    valori = random or RANDOM_PREDEFINITA
    inizio = int(extra) % len(valori) if str(extra).strip() else 0
    corpo = ([testcode, "", risposta] if test_prima else [risposta, "", testcode])
    return "\n".join([
        "const inputs = %s.split('\\n');" % json.dumps(stdin),
        "let inputIndex = 0;",
        "const randomValues = %s;" % json.dumps(valori),
        "let randomIndex = %d;" % inizio,
        _SUPPORTO,
        'var SEPARATOR = "%s";' % SEPARATORE,
        "",
    ] + corpo) + "\n"


def programma_gapfiller(codice, risposte, test, random=None):
    """Un solo test, come lo esegue il template (eval di test + codice completato)."""
    valori = random or RANDOM_PREDEFINITA
    return "\n".join([
        "let inputs = [''];",
        "let inputIndex = 0;",
        "const randomValues = %s;" % json.dumps(valori),
        "let randomIndex = 0;",
        _SUPPORTO,
        'let SEPARATOR = "%s";' % SEPARATORE,
        "let code = %s;" % json.dumps(codice),
        "let field_values = %s;" % json.dumps(risposte),
        r"const regex = /\{\[.*?\]\}/;",
        "for (let field of field_values) { code = code.replace(regex, field); }",
        "let tests = %s;" % json.dumps([test]),
        "for (let i = 0; i < tests.length; i++) {",
        "    let test = tests[i];",
        "    let finalcode = test['testcode'] + \"\\n\" + code;",
        "    inputs = test['stdin'].split('\\n');",
        "    inputIndex = 0;",
        "    randomIndex = (parseInt(test['extra']) || 0) % randomValues.length;",
        "    eval(finalcode);",
        "}",
    ]) + "\n"


def esegui(programma, timeout=5):
    """Restituisce dict: output, errore (prima riga utile o None), timeout,
    prompt_oltre, random_ricomincia."""
    with tempfile.TemporaryDirectory() as tmp:
        f = pathlib.Path(tmp) / "programma.js"
        f.write_text(programma, encoding="utf-8")
        try:
            p = subprocess.run(["node", str(f)], capture_output=True, text=True,
                               timeout=timeout, cwd=tmp)
        except subprocess.TimeoutExpired as e:
            out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
            return {"output": out, "errore": None, "timeout": True,
                    "prompt_oltre": True, "random_ricomincia": False}
    err_righe = [r for r in p.stderr.splitlines() if r not in (M_PROMPT, M_RANDOM)]
    errore = None
    if p.returncode != 0 or err_righe:
        m = [r for r in err_righe if re.match(r"^\w*Error\b|^\w+: ", r)]
        errore = (m[0] if m else (err_righe[-1] if err_righe else "uscita con codice %d" % p.returncode)).strip()
    return {"output": p.stdout, "errore": errore, "timeout": False,
            "prompt_oltre": M_PROMPT in p.stderr, "random_ricomincia": M_RANDOM in p.stderr}


def conta_gap(codice):
    return len(GAP_RE.findall(codice))
