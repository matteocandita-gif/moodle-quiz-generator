# La descrizione di un diagramma (file .er)

Un file di testo, una riga per elemento. Le righe vuote e quelle che cominciano con `#` non contano. Le righe **rientrate** (spazi o tab) appartengono all'entità o all'associazione della riga sopra.

```
titolo: Calciatori e squadre
griglia: 250 170

entita Calciatore @ 0 0
    sinistra: *IDCalciatore, Nome, Cognome
entita Squadra @ 2 0
    sopra: *Nome, Citta, PosizioneCampionato
entita Ruolo @ 0 1.4
    sotto: *CodRuolo, Nome

associazione gioca in: Calciatore (1,1) -- Squadra (1,N)
associazione ricopre: Calciatore (1,N) -- Ruolo (1,N)
    sotto: Anni
```

## Intestazione (facoltativa)

| Riga | Significato |
|---|---|
| `titolo: …` | nome della pagina nel file draw.io |
| `colori: entita=… associazioni=…` | da non scrivere nei diagrammi nuovi: valgono i colori predefiniti, entità `azzurro` e associazioni `bianco`. Solo per ridisegnare com'è una figura esistente del libro: `rosa`, `verde`, `giallo`, `arancio`, `bianco`, `azzurro` |
| `griglia: L A` | larghezza di una colonna e altezza di una riga, in pixel (predefinite 250 e 170) |

## Entità

`entita NOME @ COLONNA RIGA` mette il centro del rettangolo nella cella della griglia (colonne e righe dallo 0, anche con decimali: `@ 1.5 0`, `@ 0 1.4`). Il nome può avere spazi. Righe rientrate:

| Riga | Significato |
|---|---|
| `sopra: A, B, C` | attributi sopra il rettangolo, da sinistra a destra |
| `sotto: …` | sotto, da sinistra a destra |
| `sinistra: …` / `destra: …` | ai lati, dall'alto in basso |
| `*` davanti a un attributo | fa parte della chiave primaria |
| `identificata da: ASSOC1, ASSOC2` | entità debole: la linea della chiave taglia anche le linee di queste associazioni |

- Un solo `*`: chiave semplice, pallino pieno.
- Più `*`: chiave composta; gli attributi della chiave stanno **sullo stesso lato**, e la linea con il pallino nero taglia i loro gambetti (come Comuni con Nome e Provincia).
- Entità debole: gli attributi della chiave stanno **sopra o sotto**, e le associazioni di `identificata da` arrivano **ai fianchi** dell'entità (stessa riga). La linea passa sotto (o sopra) l'entità, taglia i gambetti e risale a tagliare le linee delle associazioni, con il pallino nero sull'ultima (come Compito con Alunno e Materia).
- Ogni entità deve avere la chiave: senza `*` lo script avvisa.
- Il rettangolo si allarga da solo per il nome e per gli attributi sopra e sotto; si allunga in altezza per gli attributi ai lati.

## Associazioni

`associazione NOME: ENTITA1 (min,max) -- ENTITA2 (min,max)`

- Il nome è tutto quello che sta prima dei due punti (anche con spazi: `gioca in`).
- Ogni cardinalità si scrive **accanto all'entità a cui si riferisce**, come nel diagramma: `Studente (1,1) -- Classe (1,N)` mette (1,1) vicino a Studente.
- Senza posizione il rombo va a metà tra le due entità, che devono stare **sulla stessa riga o sulla stessa colonna**. Altrimenti si indica dove va con `@ COLONNA RIGA` alla fine della riga; le linee partono dal lato dell'entità rivolto verso il rombo, e se le due cose non sono allineate la linea è obliqua: meglio allineare.
- Attributi dell'associazione: righe rientrate `sotto: …` o `sopra: …` (come «tariffa» o «ruolo» nel libro).

**Associazione ricorsiva**: la stessa entità ai due lati, `associazione Capo di: Dipendente (1,1) -- Dipendente (1,N)`. Il rombo va a destra dell'entità (`@ sinistra` alla fine della riga per metterlo a sinistra); la **prima** cardinalità va sulla linea a gomito, che parte dall'alto dell'entità, la **seconda** sulla linea diritta. Gli attributi sopra l'entità si spostano dalla parte opposta al gomito.

## Regole per un diagramma leggibile

- Due entità collegate distano almeno una colonna (o una riga): il rombo e le due cardinalità devono starci. Se lo script avvisa «molto vicina», allarga `griglia:` o allontana le entità.
- Gli attributi vanno sui lati da cui **non** arrivano linee: un'entità collegata a destra e a sinistra ha gli attributi sopra e sotto; una collegata in basso li ha a sinistra, a destra o sopra.
- Tra due righe di entità con attributi sotto e sopra servono più di 170 px: usa righe a 1.4 o 1.5 o una `griglia:` più alta.
- Molti attributi su un lato allargano molto il rettangolo: dividili tra due lati (per esempio la chiave a sinistra, gli altri sotto).
- Nomi delle entità al **singolare** (Cliente, non Clienti) e verbo delle associazioni al singolare («effettua», non «effettuano»), anche se la traccia parla al plurale: lo script avvisa quando un nome sembra plurale. Attributi senza spazi, come nel libro (`DataNascita`, `Ore_settimanali`).

## Ritocchi in draw.io

Ogni entità è un **gruppo** con i suoi attributi e la linea della chiave: si sposta con un trascinamento e le linee delle associazioni la seguono. Le cardinalità sono attaccate alle linee e si spostano con loro. Si possono cambiare testi, cardinalità, colori, posizioni; si può aggiungere un attributo copiando uno esistente del gruppo (pallino, gambetto, etichetta). Il PNG si rifà con `drawio_png.py`, che si ferma se trova forme che non conosce.
