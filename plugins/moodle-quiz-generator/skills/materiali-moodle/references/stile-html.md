# Stile HTML

Tutto l'HTML è un **frammento** da incollare nell'editor di Moodle in modalità sorgente: niente `<html>`, `<head>`, `<body>`, `<style>`, `<script>` (Moodle blocca gli script). Gli stili sono tutti inline. Niente emoji.

Ci sono due livelli:

- **pagine** (pagine di teoria, esempi svolti, la pagina «Come lavoriamo oggi», attività Pagina, descrizioni nei quiz): struttura completa con titoli, sezioni spaziate e riquadri;
- **testo delle domande**: compatto, senza titoli grandi. In un quiz i titoli occupano spazio senza aiutare.

## Pagine

### Contenitore e titoli

```html
<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 900px; margin: 0 auto; color: #333333; line-height: 1.6;">
<h1 style="color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;">Blocco B - Leggere dal database</h1>
<h2 style="color: #c0392b; margin-top: 30px;">Le cinque fasi</h2>
<p>...</p>
<h3 style="color: #2c3e50; margin-top: 24px;">La fase 5: elaborare i risultati</h3>
...
</div>
```

- `h1`: uno per pagina, il titolo della pagina.
- `h2`: le sezioni. Il `margin-top: 30px` dà il respiro verticale tra le sezioni: non toglierlo.
- `h3`: sottosezioni, solo se servono.
- Titoli in minuscolo normale (solo l'iniziale maiuscola), senza emoji né simboli decorativi.

### Riquadro degli obiettivi

Subito dopo l'`h1` delle pagine che aprono un'esercitazione:

```html
<h2 style="color: #c0392b; margin-top: 30px;">Obiettivi dell'esercitazione</h2>
<ul style="background-color: #fdf2e9; padding: 16px 40px; border-radius: 8px; border-left: 5px solid #e74c3c;">
<li>...</li>
</ul>
```

### Riquadri

Sfondo chiaro, bordo sinistro più scuro dello stesso colore, titolo in grassetto nel tono più scuro. I colori sono quelli del libro dell'utente: lo stesso significato ovunque.

```html
<div style="background-color: SFONDO; border-left: 5px solid BORDO; padding: 12px 16px; border-radius: 4px; margin: 0 0 16px;">
<p style="margin: 0 0 6px; color: TITOLO;"><strong>Titolo del riquadro</strong></p>
<p style="margin: 0;">Contenuto.</p>
</div>
```

| Uso | SFONDO | BORDO | TITOLO |
|---|---|---|---|
| concetti, definizioni («Che cos'è…») | `#c9daf8` | `#6d9eeb` | `#1c4587` |
| esempi: «Esempio svolto», «Guardalo in azione» | `#fff2cc` | `#f1c232` | `#7f6000` |
| «Da rileggere sul manuale», approfondimenti | `#d9ead3` | `#93c47d` | `#274e13` |
| «N.B.», «Come si svolge», «Prima di andare avanti» | `#f9cb9c` | `#e69138` | `#783f04` |
| «Che cosa può andare storto», errori tipici | `#f4cccc` | `#e06666` | `#660000` |

L'ultimo paragrafo di un riquadro ha `margin: 0` (o `margin-bottom: 0`), così il riquadro non ha spazio vuoto in fondo. Un elenco dentro un riquadro: `<ol style="margin: 0;">` o `<ul style="margin: 0;">`.

## Elementi comuni a pagine e domande

### Codice

Non scrivere il `<pre>` a mano: scrivi il codice grezzo in un blocco

```text
[[codice php]]
$prezzo = 12.50;
echo "<p>Totale: " . $prezzo . "</p>";
[[/codice]]
```

Lo script (`crea_xml.py` per le domande, `espandi_html.py` per le pagine) lo trasforma nel `<pre>` scuro con le entità HTML al posto di `<`, `>`, `&` e la colorazione della sintassi. Linguaggi: `php`, `js`, `sql`, `html`, `css`; senza linguaggio, o con `[[codice php semplice]]`, il codice resta senza colori.

**Codice da leggere**: `[[codice js leggere]]` (anche `php` e `sql`) colora il codice come gli altri e poi lo rende non eseguibile (`rendi_non_eseguibile` in `moodle_lib.py`): alcune lettere delle parole chiave diventano lettere cirilliche identiche (`lеt`, `іf`, `SЕLECT`) e dopo alcuni operatori compare uno spazio a larghezza zero, scritti come entità numeriche (`&#1077;`, `&#8203;`) perché non si perdano. Circa una sostituzione per riga (almeno 3, al massimo 10), su righe diverse; ognuna si tiene solo se da sola fa fallire il codice copiato (`node --check`, `php -l`, SQLite), quindi correggerne una non basta. Le scelte dipendono dal codice: rigenerando, le stesse. Mai nelle stringhe e nei commenti. Dalla dashboard il marcatore lo mette `da_dashboard.py` nelle domande di lettura (`formato-consegna.md` di `progettazione-quiz`); a mano si usa solo nel testo delle domande, mai nelle pagine, negli esempi da usare come riferimento, nella correzione e nei feedback. Gli avvisi (interprete mancante, codice troppo corto) li stampa `crea_xml.py`.

Se il blocco contiene **campi Cloze**, lo script non colora e lascia intatti i campi: gli `<span>` della colorazione potrebbero spezzarli. In quel caso il blocco diventa un `<pre>` senza `<code>`, come vuole la regola dell'utente.

Il `<pre>` risultante:

```html
<pre style="background-color: #333333; color: #eceff1; padding: 12px; border-radius: 4px; overflow-x: auto; margin: 8px 0; line-height: 1.5;">...</pre>
```

Colori della sintassi: parole chiave `#ebcb8b`, stringhe e valori `#a3be8c`, variabili, attributi e proprietà `#8fbcbb`, commenti `#9aa0a6`, numeri `#d08770`, tag e selettori `#81a1c1`.

### Codice nel testo

Nomi di file, campi, funzioni, tag in monospace:

```html
<span style="font-family: monospace;">catalogo.php</span>
```

Si usa lo `span` e non `<code>`, anche nelle pagine: è sicuro anche dentro le Cloze e non fa intervenire l'evidenziatore.

### Tabella di dati

```html
<table style="border-collapse: collapse; margin: 8px 0;">
<thead>
<tr><th style="border: 1px solid #999999; padding: 4px 8px; background-color: #eeeeee; text-align: left;">ISBN</th><th style="border: 1px solid #999999; padding: 4px 8px; background-color: #eeeeee; text-align: left;">Titolo</th></tr>
</thead>
<tbody>
<tr><td style="border: 1px solid #999999; padding: 4px 8px; background-color: #ffffff;">9788804</td><td style="border: 1px solid #999999; padding: 4px 8px; background-color: #ffffff;">Il fu Mattia Pascal</td></tr>
</tbody>
</table>
```

La chiave primaria si può sottolineare con `<u>` nelle descrizioni dello schema: `Libri (<u>ISBN</u>, Titolo, Autore, Prezzo)`.

### Link

Ai siti dimostrativi dell'utente, sempre in una nuova scheda:

```html
<a href="https://salvemini.synology.me/webdemo/7-mysqli.html" target="_blank" rel="noopener">Il web dietro le quinte</a>
```

## Testo delle domande

- Uno o due paragrafi di situazione e consegna; parole chiave della consegna in grassetto.
- Poi, se servono, la tabella di dati e il codice.
- Niente `h1`/`h2`: se serve separare parti, un paragrafo in grassetto.
- Un riquadro (stessa forma delle pagine) solo per indicazioni lunghe o un N.B. che non deve sfuggire.
- Lo scenario ricorrente è la **Libreria Pagina 42** (database `dblibreria`, tabella `Libri (ISBN, Titolo, Autore, Prezzo)`): usalo quando l'utente non indica altro, così domande, pagine e siti dimostrativi parlano dello stesso caso.

## Registro

Tecnico e semplice, frasi brevi, seconda persona plurale nelle pagine («guardate», «rileggiamo»), seconda singolare nelle consegne («completa», «scegli»). Ogni termine nuovo si definisce prima di usarlo. Niente aggettivi enfatici e niente formule tipiche dei testi generati («davvero», «fondamentale», «non solo… ma anche»).
