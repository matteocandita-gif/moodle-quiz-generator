"""La facciata di mysqli del prototipo php_sito è una copia di quella del prototipo php_mysqli_sqlite
(domande-php-mysqli-mock/assets/prototipo-sqlite-template.php, fino a «fine del mock»), dentro template.py
tra le righe «# fakedb: inizio» e «# fakedb: fine». Si modifica solo l'originale: crea_prototipo.py
la ricopia con allinea(), e test_php.py controlla che le due siano uguali."""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
ORIGINALE = os.path.join(QUI, "..", "..", "plugins", "moodle-quiz-generator", "skills", "domande-php-mysqli-mock",
                         "assets", "prototipo-sqlite-template.php")
TEMPLATE = os.path.join(QUI, "template.py")
FINE_MOCK = "/* ======================= fine del mock ======================= */"
BLOCCO = re.compile(r"(FAKEDB_PHP = r''')(.*?)(''')", re.S)


def originale():
    testo = open(ORIGINALE, encoding="utf-8").read()
    return testo[:testo.index(FINE_MOCK) + len(FINE_MOCK)] + "\n"


def nel_template():
    return BLOCCO.search(open(TEMPLATE, encoding="utf-8").read()).group(2)


def allinea():
    """Ricopia la facciata nel template; restituisce True se è cambiata."""
    nuova = originale()
    for vietato in ("'''", "{{", "{%", "{#"):
        if vietato in nuova:
            raise SystemExit("la facciata di mysqli contiene %s: non si può copiare nel template" % vietato)
    testo = open(TEMPLATE, encoding="utf-8").read()
    if BLOCCO.search(testo).group(2) == nuova:
        return False
    testo = BLOCCO.sub(lambda m: m.group(1) + nuova + m.group(3), testo, count=1)
    open(TEMPLATE, "w", encoding="utf-8").write(testo)
    return True
