"""Dati italiani per i database didattici: nomi, cognomi, comuni, vie, prodotti, materie…
Nessuna persona reale: nomi e cognomi si combinano a caso.

Uso nei modelli:  g.nome("F"), g.cognome(), g.persona(), g.comune(), g.via(), g.email(nome, cognome),
                  g.telefono(), g.data_tra("2024-09-01", "2025-06-10"), g.importo(5, 40), g.scegli(lista) …
(vedi la classe Generatore in costruisci.py)."""

NOMI_M = """Alessandro Andrea Antonio Alberto Angelo Bruno Carlo Claudio Cristian Daniele Davide Diego Domenico
Edoardo Emanuele Enrico Fabio Federico Filippo Francesco Gabriele Giacomo Gianluca Giorgio Giovanni Giulio
Giuseppe Jacopo Leonardo Lorenzo Luca Luigi Manuel Marco Mario Massimo Matteo Mattia Michele Nicola Paolo
Pietro Raffaele Riccardo Roberto Samuele Simone Stefano Tommaso Umberto Valerio Vincenzo Elia Christian
Gabriel Ivan Kevin Thomas Youssef Omar Ahmed Mohamed Alexandru Andrei""".split()
NOMI_F = """Alessia Alice Anna Arianna Aurora Beatrice Benedetta Camilla Carlotta Caterina Chiara Cristina
Elena Eleonora Elisa Emma Erica Federica Francesca Gaia Giada Ginevra Giorgia Giulia Greta Ilaria Irene
Laura Letizia Linda Lucia Ludovica Marta Martina Matilde Michela Nicole Noemi Paola Rebecca Roberta
Sara Serena Silvia Sofia Valentina Veronica Viola Vittoria Asia Bianca Emily Rachele Ambra Agnese Mia
Fatima Amira Maria Ioana Andreea Yasmine""".split()
COGNOMI = """Rossi Russo Ferrari Esposito Bianchi Romano Colombo Ricci Marino Greco Bruno Gallo Conti De_Luca
Mancini Costa Giordano Rizzo Lombardi Moretti Barbieri Fontana Santoro Mariani Rinaldi Caruso Ferrara
Galli Martini Leone Longo Gentile Martinelli Vitale Lombardo Serra Coppola De_Santis D'Angelo Marchetti
Parisi Villa Conte Ferraro Ferri Fabbri Bianco Marini Grasso Valentini Messina Sala De_Angelis Gatti
Pellegrini Palumbo Sanna Farina Rizzi Monti Cattaneo Morelli Amato Silvestri Mazza Testa Grassi
Pellegrino Carbone Giuliani Benedetti Barone Rossetti Caputo Montanari Guerra Palmieri Bernardi
Martino Fiore De_Rosa Ferretti Bellini Basile Riva Donati Piras Vitali Battaglia Sartori Neri Costantini
Milani Pagano Ruggiero Sorrentino D'Amico Orlando Damico Negri Zanetti Bertolini Guidi Poli Bassi
Malaguti Zanardi Bonfiglioli Tassinari Cavazza Zucchini Gamberini Righi Bergonzoni Sabattini Fini
Tinti Lodi Draghetti Venturi Mattioli Pancaldi Bolognesi Masetti Nanni Govoni Brunelli Scagliarini
Lambertini Zecchi Accorsi Monari Cremonini Grandi Selmi Musiani Biagi Lenzi Hu Chen Popescu Rahman
Kaur Ahmeti Bianchini Esposti Corazza""".split()
COGNOMI = [c.replace("_", " ") for c in COGNOMI]

# comune, sigla provincia, regione, CAP (CAP generico del comune)
COMUNI = [
 ("Bologna","BO","Emilia-Romagna","40121"),("Casalecchio di Reno","BO","Emilia-Romagna","40033"),
 ("Zola Predosa","BO","Emilia-Romagna","40069"),("Sasso Marconi","BO","Emilia-Romagna","40037"),
 ("San Lazzaro di Savena","BO","Emilia-Romagna","40068"),("Imola","BO","Emilia-Romagna","40026"),
 ("Castel Maggiore","BO","Emilia-Romagna","40013"),("Valsamoggia","BO","Emilia-Romagna","40053"),
 ("Monte San Pietro","BO","Emilia-Romagna","40050"),("Pianoro","BO","Emilia-Romagna","40065"),
 ("Calderara di Reno","BO","Emilia-Romagna","40012"),("Anzola dell'Emilia","BO","Emilia-Romagna","40011"),
 ("Modena","MO","Emilia-Romagna","41121"),("Vignola","MO","Emilia-Romagna","41058"),
 ("Reggio Emilia","RE","Emilia-Romagna","42121"),("Parma","PR","Emilia-Romagna","43121"),
 ("Ferrara","FE","Emilia-Romagna","44121"),("Ravenna","RA","Emilia-Romagna","48121"),
 ("Rimini","RN","Emilia-Romagna","47921"),("Forlì","FC","Emilia-Romagna","47121"),
 ("Cesena","FC","Emilia-Romagna","47521"),("Piacenza","PC","Emilia-Romagna","29121"),
 ("Milano","MI","Lombardia","20121"),("Bergamo","BG","Lombardia","24121"),("Brescia","BS","Lombardia","25121"),
 ("Torino","TO","Piemonte","10121"),("Genova","GE","Liguria","16121"),("Venezia","VE","Veneto","30121"),
 ("Verona","VR","Veneto","37121"),("Padova","PD","Veneto","35121"),("Trento","TN","Trentino-Alto Adige","38121"),
 ("Firenze","FI","Toscana","50121"),("Pisa","PI","Toscana","56121"),("Siena","SI","Toscana","53100"),
 ("Perugia","PG","Umbria","06121"),("Ancona","AN","Marche","60121"),("Roma","RM","Lazio","00118"),
 ("Napoli","NA","Campania","80121"),("Salerno","SA","Campania","84121"),("Bari","BA","Puglia","70121"),
 ("Lecce","LE","Puglia","73100"),("Taranto","TA","Puglia","74121"),("Potenza","PZ","Basilicata","85100"),
 ("Cosenza","CS","Calabria","87100"),("Reggio Calabria","RC","Calabria","89121"),
 ("Palermo","PA","Sicilia","90121"),("Catania","CT","Sicilia","95121"),("Cagliari","CA","Sardegna","09121"),
 ("Sassari","SS","Sardegna","07100"),("Trieste","TS","Friuli-Venezia Giulia","34121"),
 ("Udine","UD","Friuli-Venezia Giulia","33100"),("Aosta","AO","Valle d'Aosta","11100"),
 ("L'Aquila","AQ","Abruzzo","67100"),("Pescara","PE","Abruzzo","65121"),("Campobasso","CB","Molise","86100"),
]
VIE = """Via Roma|Via Garibaldi|Via Mazzini|Via Dante|Via Verdi|Via Marconi|Via Matteotti|Via Cavour|
Via XX Settembre|Via della Repubblica|Via Indipendenza|Via San Vitale|Via Saragozza|Via Emilia|
Via Porrettana|Via Andrea Costa|Via dei Mille|Via Galilei|Via Leopardi|Via Manzoni|Via Carducci|
Viale Europa|Viale della Libertà|Via Fermi|Via Pascoli|Via Petrarca|Via Gramsci|Via Togliatti|
Via Battisti|Via Oberdan|Via Kennedy|Via Moro|Piazza Maggiore|Piazza Garibaldi|Via del Lavoro|
Via dell'Artigianato|Via Bazzanese|Via Marzabotto|Via Ronzani|Via Calzavecchio""".replace("\n", "").split("|")

MATERIE = ["Italiano", "Storia", "Matematica", "Inglese", "Francese", "Spagnolo", "Informatica",
           "Economia aziendale", "Diritto", "Economia politica", "Scienze motorie", "Religione",
           "Scienze integrate", "Geografia", "Fisica", "Chimica"]
INDIRIZZI_SCOLASTICI = ["SIA", "AFM", "RIM", "Turismo"]

CATEGORIE_PRODOTTI = {
 "Cancelleria": ["Quaderno a righe", "Quaderno a quadretti", "Penna a sfera blu", "Penna gel nera",
                 "Matita HB", "Gomma bianca", "Evidenziatore giallo", "Righello 30 cm", "Compasso",
                 "Raccoglitore ad anelli", "Astuccio", "Zaino scolastico", "Calcolatrice scientifica"],
 "Informatica": ["Mouse wireless", "Tastiera USB", "Chiavetta USB 32 GB", "Cuffie con microfono",
                 "Webcam HD", "Hub USB-C", "Monitor 24 pollici", "Hard disk esterno 1 TB",
                 "Cavo HDMI 2 m", "Tappetino mouse", "Router Wi-Fi", "Stampante laser"],
 "Alimentari": ["Pasta di semola 500 g", "Riso Carnaroli 1 kg", "Olio extravergine 1 l",
                "Passata di pomodoro", "Parmigiano Reggiano 300 g", "Mortadella Bologna 200 g",
                "Caffè macinato 250 g", "Biscotti integrali", "Latte intero 1 l", "Farina 00 1 kg",
                "Tortellini 250 g", "Aceto balsamico di Modena"],
 "Abbigliamento": ["Felpa con cappuccio", "Maglietta di cotone", "Jeans", "Giacca impermeabile",
                   "Scarpe da ginnastica", "Sciarpa di lana", "Cappello", "Calzini sportivi",
                   "Pantaloni della tuta", "Camicia bianca"],
 "Casa": ["Lampada da scrivania", "Tazza in ceramica", "Set di bicchieri", "Asciugamano",
          "Cuscino", "Orologio da parete", "Vaso di vetro", "Portafoto", "Tovaglia", "Candela profumata"],
 "Sport": ["Pallone da calcio", "Pallone da pallavolo", "Racchetta da tennis", "Borraccia",
           "Tappetino yoga", "Corda per saltare", "Manubri 2 kg", "Casco da bici", "Zaino da trekking"],
}
GENERI_LIBRI = ["Romanzo", "Giallo", "Fantascienza", "Fantasy", "Storico", "Saggio", "Poesia",
                "Biografia", "Avventura", "Fumetto"]
EDITORI = [("Einaudi", "Torino"), ("Mondadori", "Milano"), ("Feltrinelli", "Milano"), ("Zanichelli", "Bologna"),
           ("Il Mulino", "Bologna"), ("Laterza", "Bari"), ("Adelphi", "Milano"), ("Sellerio", "Palermo"),
           ("Bompiani", "Milano"), ("Giunti", "Firenze"), ("Rizzoli", "Milano"), ("Garzanti", "Milano")]
REPARTI = ["Amministrazione", "Vendite", "Acquisti", "Magazzino", "Marketing", "Produzione",
           "Risorse umane", "Assistenza clienti", "Sistemi informativi", "Logistica"]
RUOLI = ["Impiegato", "Responsabile", "Tecnico", "Addetto", "Consulente", "Stagista", "Direttore"]
METODI_PAGAMENTO = ["Carta di credito", "Bancomat", "Contanti", "Bonifico", "PayPal"]
STATI_ORDINE = ["In lavorazione", "Spedito", "Consegnato", "Annullato"]
SPORT = ["Calcio", "Pallavolo", "Basket", "Nuoto", "Tennis", "Atletica", "Ciclismo", "Rugby"]
COLORI = ["Rosso", "Blu", "Verde", "Giallo", "Nero", "Bianco", "Grigio", "Arancione", "Viola"]
MARCHE_AUTO = [("Fiat", ["Panda", "500", "Tipo"]), ("Volkswagen", ["Golf", "Polo"]), ("Renault", ["Clio", "Captur"]),
               ("Dacia", ["Sandero", "Duster"]), ("Toyota", ["Yaris", "Aygo"]), ("Ford", ["Fiesta", "Puma"]),
               ("Peugeot", ["208", "2008"]), ("Lancia", ["Ypsilon"]), ("Jeep", ["Renegade"])]
DOMINI_EMAIL = ["gmail.com", "libero.it", "outlook.it", "yahoo.it", "hotmail.it", "virgilio.it"]

# nomi e cognomi coerenti con la nazionalità (per autori, clienti esteri, fornitori…)
NOMI_ESTERI = {
 "Francese": (["Jean", "Pierre", "Marie", "Claire", "Louis", "Camille", "Julien", "Sophie"],
              ["Dubois", "Martin", "Bernard", "Lefèvre", "Moreau", "Laurent", "Girard", "Roux"]),
 "Inglese": (["James", "Emily", "Oliver", "Charlotte", "George", "Alice", "Henry", "Grace"],
             ["Smith", "Taylor", "Brown", "Wilson", "Evans", "Clarke", "Hughes", "Walker"]),
 "Statunitense": (["John", "Mary", "Robert", "Linda", "Michael", "Susan", "David", "Karen"],
                  ["Johnson", "Miller", "Davis", "Anderson", "Thompson", "Moore", "Jackson", "White"]),
 "Spagnola": (["Carlos", "Lucía", "Javier", "Carmen", "Miguel", "Elena", "Pablo", "Isabel"],
              ["García", "Fernández", "López", "Martínez", "Sánchez", "Romero", "Navarro", "Torres"]),
 "Tedesca": (["Hans", "Anna", "Klaus", "Greta", "Lukas", "Hannah", "Felix", "Lena"],
             ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Wagner", "Becker", "Hoffmann"]),
 "Argentina": (["Diego", "Sofía", "Martín", "Valentina", "Lucas", "Camila", "Mateo", "Florencia"],
               ["González", "Rodríguez", "Pérez", "Gómez", "Díaz", "Álvarez", "Ruiz", "Castro"]),
}
