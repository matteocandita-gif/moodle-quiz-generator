-- Database «palestra» (Palestra), taglia piccolo, seme 5101: generato con database-didattici

CREATE TABLE Istruttori (
    IdIstruttore INT PRIMARY KEY,
    Nome VARCHAR(40) NOT NULL,
    Cognome VARCHAR(40) NOT NULL,
    Qualifica VARCHAR(40) NOT NULL,
    DataAssunzione DATE NOT NULL
);

CREATE TABLE Corsi (
    IdCorso INT PRIMARY KEY,
    Nome VARCHAR(40) NOT NULL,
    Livello VARCHAR(15) NOT NULL,
    Giorno VARCHAR(10) NOT NULL,
    Orario CHAR(5) NOT NULL,
    CostoMensile DECIMAL(5,2) NOT NULL,
    PostiMax INT NOT NULL,
    IdIstruttore INT NOT NULL,
    FOREIGN KEY (IdIstruttore) REFERENCES Istruttori(IdIstruttore)
);

CREATE TABLE Soci (
    IdSocio INT PRIMARY KEY,
    Nome VARCHAR(40) NOT NULL,
    Cognome VARCHAR(40) NOT NULL,
    DataNascita DATE NOT NULL,
    Citta VARCHAR(40) NOT NULL,
    Telefono VARCHAR(15),
    DataIscrizione DATE NOT NULL
);

CREATE TABLE Iscrizioni (
    IdIscrizione INT PRIMARY KEY,
    IdSocio INT NOT NULL,
    IdCorso INT NOT NULL,
    DataInizio DATE NOT NULL,
    DataFine DATE,
    FOREIGN KEY (IdSocio) REFERENCES Soci(IdSocio),
    FOREIGN KEY (IdCorso) REFERENCES Corsi(IdCorso)
);

INSERT INTO Istruttori (IdIstruttore, Nome, Cognome, Qualifica, DataAssunzione) VALUES
(1, 'Giulia', 'De Santis', 'Laurea in Scienze motorie', '2021-07-25'),
(2, 'Erica', 'Costantini', 'Diploma ISEF', '2022-11-10'),
(3, 'Tommaso', 'Villa', 'Istruttore federale', '2022-05-16'),
(4, 'Giulia', 'Grasso', 'Laurea in Scienze motorie', '2014-12-17'),
(5, 'Erica', 'Costantini', 'Personal trainer certificato', '2017-06-05'),
(6, 'Beatrice', 'Vitale', 'Laurea in Scienze motorie', '2026-09-01');

INSERT INTO Corsi (IdCorso, Nome, Livello, Giorno, Orario, CostoMensile, PostiMax, IdIstruttore) VALUES
(1, 'Yoga', 'Base', 'Sabato', '19:30', 40.00, 10, 1),
(2, 'Yoga', 'Avanzato', 'Martedì', '18:30', 30.00, 12, 1),
(3, 'Pilates', 'Base', 'Venerdì', '17:30', 50.00, 10, 1),
(4, 'Kickboxing', 'Base', 'Giovedì', '17:30', 42.50, 15, 3),
(5, 'Ginnastica posturale', 'Intermedio', 'Giovedì', '17:30', 50.00, 15, 3),
(6, 'Pilates', 'Intermedio', 'Giovedì', '18:30', 55.00, 20, 2),
(7, 'Danza moderna', 'Base', 'Giovedì', '19:30', 45.00, 10, 4),
(8, 'Stretching', 'Base', 'Martedì', '19:30', 38.50, 15, 4),
(9, 'Circuit training', 'Avanzato', 'Giovedì', '20:30', 60.00, 10, 5),
(10, 'Hip hop', 'Intermedio', 'Sabato', '19:30', 48.00, 20, 5);

INSERT INTO Soci (IdSocio, Nome, Cognome, DataNascita, Citta, Telefono, DataIscrizione) VALUES
(1, 'Fabio', 'D''Amico', '1991-03-17', 'Bologna', NULL, '2024-10-31'),
(2, 'Samuele', 'De Santis', '1984-04-06', 'Bologna', '364 8740894', '2025-01-01'),
(3, 'Camilla', 'Donati', '1998-08-11', 'Bologna', '395 7103905', '2025-12-31'),
(4, 'Chiara', 'Villa', '1974-04-20', 'Bologna', '395 1096099', '2024-12-31'),
(5, 'Riccardo', 'Esposito', '1998-08-08', 'Bologna', '396 0200040', '2026-01-01'),
(6, 'Chiara', 'Orlando', '1971-09-23', 'Zola Predosa', '331 7317074', '2026-03-27'),
(7, 'Maria', 'Monari', '1994-09-20', 'Anzola dell''Emilia', '357 8092488', '2023-10-01'),
(8, 'Noemi', 'Galli', '1973-08-11', 'Bologna', '345 1464208', '2023-12-26'),
(9, 'Ivan', 'Biagi', '2003-11-15', 'Modena', '382 8817525', '2024-09-25'),
(10, 'Fabio', 'D''Amico', '1999-08-22', 'Casalecchio di Reno', '385 4194936', '2025-11-24'),
(11, 'Carlo', 'De Luca', '1961-02-19', 'Bologna', '339 3428034', '2023-10-10'),
(12, 'Paolo', 'Barone', '1960-01-01', 'Bologna', NULL, '2025-06-14');

INSERT INTO Iscrizioni (IdIscrizione, IdSocio, IdCorso, DataInizio, DataFine) VALUES
(1, 7, 4, '2023-11-29', NULL),
(2, 7, 7, '2023-12-14', NULL),
(3, 7, 3, '2024-03-26', NULL),
(4, 1, 6, '2024-11-21', NULL),
(5, 1, 4, '2024-11-28', NULL),
(6, 1, 1, '2024-12-17', NULL),
(7, 2, 9, '2025-01-04', NULL),
(8, 4, 5, '2025-01-13', '2025-08-13'),
(9, 2, 1, '2025-01-27', NULL),
(10, 2, 3, '2025-02-03', NULL),
(11, 4, 1, '2025-02-11', NULL),
(12, 4, 3, '2025-02-19', NULL),
(13, 2, 7, '2025-03-23', NULL),
(14, 9, 1, '2025-06-04', '2026-01-08'),
(15, 4, 4, '2025-07-20', '2025-12-15'),
(16, 10, 4, '2025-11-24', NULL),
(17, 3, 2, '2026-01-14', NULL),
(18, 3, 3, '2026-01-17', '2026-06-08'),
(19, 3, 7, '2026-01-18', NULL),
(20, 3, 9, '2026-01-23', NULL);
