import subprocess, os, shutil, re

# Prototipo sql_salvemini: SQLite con chiavi esterne attive, controllo di sola
# sintassi (precheck) ed errori SQL mostrati come output leggibile.
student_answer = """{{ STUDENT_ANSWER | e('py') }}""".rstrip()
column_widths = []
{% for width in QUESTION.parameters.columnwidths %}
column_widths.append({{width}})
{% endfor %}
foreign_keys = True
{% if QUESTION.parameters.foreign_keys is defined and QUESTION.parameters.foreign_keys == false %}
foreign_keys = False
{% endif %}

if not student_answer.endswith(';'):
    student_answer = student_answer + ';'
db_files = [fname for fname in os.listdir() if fname.endswith('.db')]
if len(db_files) == 0:
    raise Exception("No DB files found!")
elif len(db_files) == 1:
    db_working = db_files[0][:-3]  # Strip .db extension
else:
    raise Exception("Multiple DB files not implemented yet, sorry!")

SEPARATOR = "#<ab@17943918#@>#"
controls = [".mode column", ".headers on"]
if foreign_keys:
    controls.append("PRAGMA foreign_keys = ON;")
if column_widths:
    controls.append(".width " + ' '.join(str(width) for width in column_widths))
prelude = '\n'.join(controls) + '\n'


def errori_leggibili(stderr):
    """Una riga 'ERRORE: messaggio' per ogni errore, senza numeri di riga."""
    righe = []
    for riga in stderr.splitlines():
        m = re.match(r'^(?:Parse error|Runtime error|Error)(?: near line \d+)?: (.*?)(?: \(\d+\))?$', riga)
        if m:
            righe.append("ERRORE: " + m.group(1))
    return righe


def esegui(codice):
    with open('commands', 'w') as f:
        f.write(codice)
    with open('commands') as f:
        p = subprocess.run(['sqlite3', db_working], stdin=f, capture_output=True,
                           universal_newlines=True)
    uscita = '\n'.join(r.rstrip() for r in p.stdout.rstrip().splitlines())
    return uscita, errori_leggibili(p.stderr)


{% for TEST in TESTCASES %}
shutil.copyfile(db_files[0], db_working)  # Copy clean writeable db file
testcode = """{{ TEST.testcode | e('py') }}"""
extra = """{{ TEST.extra | e('py') }}"""
{% if TEST.testtype == 1 %}
# Precheck: esegue solo la risposta e mostra soltanto gli eventuali errori
uscita, errori = esegui(prelude + student_answer)
if errori:
    print('\n'.join(errori))
{% else %}
uscita, errori = esegui('\n'.join([prelude, extra, student_answer, testcode]))
righe = ([uscita] if uscita else []) + errori
print('\n'.join(righe))
{% endif %}
{% if not loop.last %}
print(SEPARATOR)
{% endif %}
{% endfor %}
