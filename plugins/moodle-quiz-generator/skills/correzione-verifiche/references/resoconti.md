# Resoconti per il docente

A correzione finita, su richiesta («prepara i resoconti della verifica …»), un resoconto per ogni studente e uno della classe. Sono **per il docente**: diretti, anche con ipotesi («quasi certamente il tempo», «ha usato quelle caselle per provare»). Più avanti potranno essere adattati per gli studenti, ma non ora.

## Da dove si parte

Rileggi il database della verifica (`ArtifactData list` di `domande` e `valutazioni` con `out_dir`): punteggi e commenti sono quelli decisi dall'utente, che contano più delle proposte. Per ogni studente guarda tutte le domande insieme, con i titoli e il tipo (teoria, programma, debug…), e calcola il voto con le somme dello script, non a mano. Se l'utente ha già finito in Moodle e ha cambiato punteggi o pesi lì (il caso tipico: la revisione fatta direttamente in Valutazione manuale), i voti veri sono quelli dell'export «Valutazioni» di Moodle: chiedilo, leggilo usando solo le iniziali (cognome e nome ridotti alle prime due lettere, mai stampati per intero) e abbinalo alle sigle; i commenti della dashboard servono comunque per gli errori. Dillo nel resoconto della classe («con i punteggi inseriti in Moodle»). Se la prova ha parti distinte (prima e seconda metà, base e avanzata, teoria e pratica), calcola anche il voto di ogni parte: è spesso il dato che spiega il resto.

## Lo studente

Righe brevi, ognuna con un'etichetta seguita dai due punti (la pagina la mette in grassetto). Si usano solo le righe che servono, in quest'ordine:

- **Andamento**: voto, giudizio in una frase, dove sta il punto forte (con le domande, D2, D6…).
- **Punti di forza**, se non sono già nell'andamento.
- **Difficoltà**: dove perde i punti, per argomento o per tipo di domanda, con esempi concreti dalle risposte.
- **Errori ricorrenti**: lo stesso errore in più domande (un pattern), la cosa più utile del resoconto. Per esempio: `let` ridichiarato dentro i blocchi, stampare invece di restituire, condizioni limite sbagliate, nella teoria riscrivere il codice invece di spiegare, rispondere solo alla prima richiesta.
- **Teoria**: se c'è una parte teorica con un andamento diverso dal resto.
- **Gestione della prova**: domande lasciate vuote (e dove), codice incollato da un'altra domanda, ordine insolito.
- **Da riprendere**: due o tre cose concrete.

Quattro-sei righe in tutto. Il codice tra apici inversi, come nei commenti. Solo sigle; niente aggettivi o participi che attribuiscano un genere allo studente («arrivato», «fermata»): si parla della prova («la prova si interrompe a metà»).

## La classe

Stesse regole, con le etichette **Andamento** (media, sufficienti, distribuzione o differenza tra le parti), **Lettura** (che cosa dicono i numeri: lunghezza, domande saltate, argomenti), **Punti di forza**, **Errori diffusi** (con la percentuale media delle domande) e **Da valutare** (decisioni per il docente: pesi, recupero, cosa riprendere in classe). I nomi degli studenti citati come esempio sono sigle.

## Dove si salvano

Nella collezione `verifiche/<id>/resoconti`: il documento `studenti` con `righe` (chiave dello studente → `testo`, `aggiornato` AAAA-MM-GG, `modificato: false`) e il documento `classe` con `testo`, `aggiornato`, `modificato`. La prima volta `set`, poi `update` con `if_version`; se `modificato` è `true` l'utente ha cambiato il testo dalla pagina: non riscriverlo senza chiedere. Se i punteggi cambiano dopo (domande tolte dal conteggio, revisioni), i resoconti si rifanno, perché citano i voti.
