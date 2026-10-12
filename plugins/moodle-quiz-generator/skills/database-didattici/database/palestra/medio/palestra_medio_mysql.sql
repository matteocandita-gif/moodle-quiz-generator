-- Da importare in phpMyAdmin (scheda Importa) o con: mysql -u root < questo_file.sql
-- Crea il database «palestra» e ricrea le tabelle: si può reimportare per ripartire dai dati originali.
CREATE DATABASE IF NOT EXISTS palestra CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE palestra;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Iscrizioni;
DROP TABLE IF EXISTS Soci;
DROP TABLE IF EXISTS Corsi;
DROP TABLE IF EXISTS Istruttori;
SET FOREIGN_KEY_CHECKS = 1;

-- Database «palestra» (Palestra), taglia medio, seme 5101: generato con database-didattici

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
(5, 'Giada', 'Hu', 'Personal trainer certificato', '2017-06-05'),
(6, 'Beatrice', 'Vitale', 'Laurea in Scienze motorie', '2022-05-30'),
(7, 'Luigi', 'Accorsi', 'Diploma ISEF', '2015-03-05'),
(8, 'Erica', 'Costantini', 'Istruttore federale', '2017-05-14'),
(9, 'Bianca', 'Bernardi', 'Laurea in Scienze motorie', '2026-09-01');

INSERT INTO Corsi (IdCorso, Nome, Livello, Giorno, Orario, CostoMensile, PostiMax, IdIstruttore) VALUES
(1, 'Yoga', 'Base', 'Mercoledì', '17:30', 40.00, 20, 1),
(2, 'Yoga', 'Avanzato', 'Sabato', '20:30', 30.00, 15, 1),
(3, 'Pilates', 'Base', 'Giovedì', '18:30', 50.00, 20, 1),
(4, 'Kickboxing', 'Base', 'Giovedì', '19:30', 42.50, 10, 3),
(5, 'Ginnastica posturale', 'Base', 'Martedì', '19:30', 50.00, 15, 3),
(6, 'Pilates', 'Intermedio', 'Venerdì', '17:30', 55.00, 10, 2),
(7, 'Danza moderna', 'Intermedio', 'Sabato', '19:30', 45.00, 20, 4),
(8, 'Stretching', 'Base', 'Venerdì', '10:30', 38.50, 20, 4),
(9, 'Circuit training', 'Base', 'Venerdì', '12:30', 60.00, 20, 5),
(10, 'Hip hop', 'Avanzato', 'Mercoledì', '12:30', 48.00, 25, 8),
(11, 'Difesa personale', 'Base', 'Sabato', '20:30', 40.00, 12, 6),
(12, 'Yoga', 'Intermedio', 'Giovedì', '18:30', 30.00, 15, 5),
(13, 'Pilates', 'Avanzato', 'Sabato', '19:30', 50.00, 20, 6),
(14, 'Zumba', 'Base', 'Lunedì', '18:30', 42.50, 10, 6),
(15, 'Spinning', 'Intermedio', 'Mercoledì', '17:30', 35.00, 20, 7),
(16, 'Functional training', 'Intermedio', 'Martedì', '10:30', 55.00, 25, 6),
(17, 'Pugilato', 'Intermedio', 'Giovedì', '12:30', 45.00, 20, 7),
(18, 'Kickboxing', 'Intermedio', 'Sabato', '19:30', 38.50, 12, 1);

INSERT INTO Soci (IdSocio, Nome, Cognome, DataNascita, Citta, Telefono, DataIscrizione) VALUES
(1, 'Chiara', 'Vitali', '1998-08-08', 'Bologna', '396 0200040', '2026-06-25'),
(2, 'Chiara', 'Orlando', '1971-09-23', 'Bologna', '331 7317074', '2025-01-01'),
(3, 'Maria', 'Monari', '1994-09-20', 'Bologna', '357 8092488', '2025-12-31'),
(4, 'Noemi', 'Galli', '1973-08-11', 'Bologna', '345 1464208', '2024-12-31'),
(5, 'Ivan', 'Biagi', '2003-11-15', 'Bologna', '382 8817525', '2026-01-01'),
(6, 'Marta', 'Ricci', '1999-08-22', 'Bologna', '385 4194936', '2025-11-24'),
(7, 'Carlo', 'De Luca', '1961-02-19', 'Bologna', '339 3428034', '2023-10-10'),
(8, 'Paolo', 'Barone', '1960-01-01', 'Bologna', NULL, '2023-01-10'),
(9, 'Ginevra', 'Bassi', '1968-12-22', 'Sasso Marconi', '344 0571789', '2024-02-06'),
(10, 'Emily', 'Venturi', '1975-05-13', 'Calderara di Reno', '351 1384730', '2026-05-04'),
(11, 'Cristian', 'Parisi', '1996-03-22', 'Bologna', '372 5913596', '2023-09-05'),
(12, 'Noemi', 'Brunelli', '1973-09-08', 'Bologna', NULL, '2025-04-25'),
(13, 'Federico', 'Draghetti', '1966-05-20', 'Casalecchio di Reno', '369 6110803', '2026-01-27'),
(14, 'Alessia', 'Russo', '1998-01-07', 'Imola', '367 7116167', '2026-04-07'),
(15, 'Caterina', 'Brunelli', '1961-11-04', 'Bologna', NULL, '2026-04-05'),
(16, 'Emma', 'Sorrentino', '1967-04-01', 'Imola', NULL, '2023-12-18'),
(17, 'Giulio', 'Cattaneo', '1980-10-22', 'San Lazzaro di Savena', '352 8261303', '2023-12-21'),
(18, 'Chiara', 'Malaguti', '1970-08-10', 'Bologna', '321 2674838', '2025-03-30'),
(19, 'Thomas', 'Govoni', '1973-01-10', 'Calderara di Reno', '384 6115831', '2023-02-05'),
(20, 'Carlo', 'Chen', '1970-01-28', 'Zola Predosa', NULL, '2023-07-03'),
(21, 'Ilaria', 'Piras', '1979-02-27', 'Zola Predosa', '345 1797537', '2023-02-28'),
(22, 'Lorenzo', 'Valentini', '2004-06-05', 'Anzola dell''Emilia', '351 3754911', '2025-02-15'),
(23, 'Federico', 'Gamberini', '1972-10-02', 'Bologna', '348 5297191', '2024-12-02'),
(24, 'Caterina', 'Fontana', '1973-02-03', 'Pianoro', NULL, '2025-12-13'),
(25, 'Carlo', 'Zucchini', '1964-12-04', 'Monte San Pietro', NULL, '2025-03-29'),
(26, 'Alessandro', 'Venturi', '1975-12-24', 'Calderara di Reno', '343 4761717', '2023-09-23'),
(27, 'Serena', 'Santoro', '1989-02-25', 'Bologna', '362 4021662', '2023-01-14'),
(28, 'Chiara', 'Vitali', '1993-07-30', 'Casalecchio di Reno', NULL, '2026-03-26'),
(29, 'Greta', 'Bianchi', '1997-07-15', 'San Lazzaro di Savena', '358 5550216', '2025-05-31'),
(30, 'Benedetta', 'Rinaldi', '1994-11-11', 'Bologna', '370 0292875', '2025-06-14');

INSERT INTO Iscrizioni (IdIscrizione, IdSocio, IdCorso, DataInizio, DataFine) VALUES
(1, 8, 7, '2023-05-07', NULL),
(2, 21, 8, '2023-10-06', NULL),
(3, 21, 13, '2023-11-12', NULL),
(4, 20, 11, '2023-11-17', NULL),
(5, 7, 3, '2023-11-18', NULL),
(6, 7, 1, '2024-02-05', '2024-03-27'),
(7, 11, 5, '2024-03-12', NULL),
(8, 7, 16, '2024-03-25', '2024-08-24'),
(9, 16, 1, '2024-04-07', NULL),
(10, 26, 14, '2024-04-12', '2024-10-02'),
(11, 16, 15, '2024-05-20', NULL),
(12, 17, 12, '2024-07-19', NULL),
(13, 9, 13, '2024-12-01', NULL),
(14, 2, 10, '2025-01-01', NULL),
(15, 4, 3, '2025-01-21', NULL),
(16, 2, 3, '2025-01-25', '2025-03-22'),
(17, 2, 1, '2025-02-22', NULL),
(18, 22, 13, '2025-03-04', '2025-09-07'),
(19, 22, 12, '2025-03-13', NULL),
(20, 25, 11, '2025-05-22', '2025-10-16'),
(21, 25, 9, '2025-06-10', NULL),
(22, 2, 7, '2025-07-13', '2026-01-18'),
(23, 4, 9, '2025-09-19', '2026-05-11'),
(24, 22, 4, '2025-10-30', NULL),
(25, 12, 2, '2025-11-05', NULL),
(26, 24, 8, '2025-12-15', NULL),
(27, 25, 5, '2025-12-18', NULL),
(28, 3, 2, '2026-01-01', NULL),
(29, 6, 14, '2026-01-02', '2026-06-29'),
(30, 18, 7, '2026-01-02', '2026-02-25'),
(31, 24, 3, '2026-01-02', NULL),
(32, 25, 3, '2026-01-02', NULL),
(33, 3, 7, '2026-01-15', NULL),
(34, 3, 10, '2026-02-03', NULL),
(35, 13, 11, '2026-02-06', '2026-08-15'),
(36, 3, 11, '2026-03-23', NULL),
(37, 28, 4, '2026-03-27', NULL),
(38, 15, 7, '2026-05-12', '2026-07-30'),
(39, 6, 15, '2026-05-25', '2026-07-05'),
(40, 10, 1, '2026-06-19', NULL),
(41, 1, 1, '2026-06-28', NULL),
(42, 1, 6, '2026-07-01', NULL),
(43, 24, 11, '2026-07-24', NULL),
(44, 14, 7, '2026-07-29', NULL),
(45, 1, 4, '2026-08-24', NULL),
(46, 28, 15, '2026-09-12', NULL),
(47, 3, 9, '2026-09-24', NULL),
(48, 1, 14, '2026-09-30', NULL),
(49, 10, 13, '2026-09-30', NULL),
(50, 15, 9, '2026-09-30', NULL);
