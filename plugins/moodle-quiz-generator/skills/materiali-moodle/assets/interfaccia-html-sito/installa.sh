#!/bin/bash
# Installa (o reinstalla dopo un aggiornamento di CodeRunner) l'interfaccia html_sito.
# Uso, dalla cartella che contiene questo script:
#   sudo ./installa.sh /percorso/di/moodle
# Il percorso è la cartella principale di Moodle (quella con config.php).
set -e

MOODLE="${1:?Indica la cartella di Moodle, es. sudo ./installa.sh /var/www/moodle}"
QUI="$(cd "$(dirname "$0")" && pwd)"

# Da Moodle 5.1 il codice sta nella sottocartella public.
if [ -d "$MOODLE/public/question/type/coderunner" ]; then
    RADICE="$MOODLE/public"
else
    RADICE="$MOODLE"
fi
CR="$RADICE/question/type/coderunner"
if [ ! -d "$CR/amd/src" ] || [ ! -d "$CR/amd/build" ]; then
    echo "Non trovo CodeRunner in $CR" >&2
    exit 1
fi

# Stesso file in src (lì CodeRunner cerca le interfacce) e in build (lì Moodle lo carica).
# Il .json elenca i parametri dell'interfaccia (gli aiuti dell'editor).
install -m 644 "$QUI/ui_html_sito.js" "$CR/amd/src/ui_html_sito.js"
install -m 644 "$QUI/ui_html_sito.js" "$CR/amd/build/ui_html_sito.min.js"
install -m 644 "$QUI/ui_html_sito.json" "$CR/amd/src/ui_html_sito.json"
echo "Copiato in $CR/amd/src e $CR/amd/build"

# Descrizioni dei parametri, mostrate nel modulo di modifica della domanda.
# Se ci sono già (installazione precedente) si sostituiscono con quelle nuove.
LINGUA="$CR/lang/en/qtype_coderunner.php"
cp "$LINGUA" "$LINGUA.bak-html_sito"
sed -i '/html_sito: inizio/,/html_sito: fine/d' "$LINGUA"
cat "$QUI/stringhe.php" >> "$LINGUA"
if php -l "$LINGUA" > /dev/null; then
    rm "$LINGUA.bak-html_sito"
    echo "Descrizioni dei parametri aggiornate in $LINGUA"
else
    mv "$LINGUA.bak-html_sito" "$LINGUA"
    echo "Attenzione: non sono riuscito ad aggiornare le descrizioni dei parametri (file ripristinato)." >&2
fi

# Svuota le cache con l'utente del server web (www-data, oppure UTENTE_WEB=... prima del comando),
# così i file della cache restano suoi.
PURGE=""
for f in "$RADICE/admin/cli/purge_caches.php" "$MOODLE/admin/cli/purge_caches.php"; do
    [ -f "$f" ] && PURGE="$f" && break
done
if [ -n "$PURGE" ] && sudo -u "${UTENTE_WEB:-www-data}" php "$PURGE"; then
    echo "Cache svuotate. Fatto."
else
    echo "Non sono riuscito a svuotare le cache da qui: fallo da Moodle," >&2
    echo "Amministrazione del sito > Sviluppo > Svuota le cache > Svuota tutte le cache." >&2
fi
