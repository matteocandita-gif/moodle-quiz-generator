-- Da importare in phpMyAdmin (scheda Importa) o con: mysql -u root < questo_file.sql
-- Crea il database «cinema» e ricrea le tabelle: si può reimportare per ripartire dai dati originali.
CREATE DATABASE IF NOT EXISTS cinema CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cinema;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Biglietti;
DROP TABLE IF EXISTS Clienti;
DROP TABLE IF EXISTS Film;
DROP TABLE IF EXISTS Registi;
SET FOREIGN_KEY_CHECKS = 1;

-- Database «cinema» (Cinema), taglia medio, seme 5102: generato con database-didattici

CREATE TABLE Registi (
    IdRegista INT PRIMARY KEY,
    Nome VARCHAR(40) NOT NULL,
    Cognome VARCHAR(40) NOT NULL,
    Nazionalita VARCHAR(30) NOT NULL,
    AnnoNascita INT NOT NULL
);

CREATE TABLE Film (
    IdFilm INT PRIMARY KEY,
    Titolo VARCHAR(60) NOT NULL,
    Genere VARCHAR(20) NOT NULL,
    Durata INT NOT NULL,
    AnnoUscita INT NOT NULL,
    IdRegista INT NOT NULL,
    FOREIGN KEY (IdRegista) REFERENCES Registi(IdRegista)
);

CREATE TABLE Clienti (
    IdCliente INT PRIMARY KEY,
    Nome VARCHAR(40) NOT NULL,
    Cognome VARCHAR(40) NOT NULL,
    DataNascita DATE NOT NULL,
    Citta VARCHAR(40) NOT NULL,
    Email VARCHAR(80),
    DataTessera DATE NOT NULL
);

CREATE TABLE Biglietti (
    IdBiglietto INT PRIMARY KEY,
    IdFilm INT NOT NULL,
    IdCliente INT NOT NULL,
    DataProiezione DATE NOT NULL,
    Ora CHAR(5) NOT NULL,
    Sala VARCHAR(10) NOT NULL,
    Prezzo DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (IdFilm) REFERENCES Film(IdFilm),
    FOREIGN KEY (IdCliente) REFERENCES Clienti(IdCliente)
);

INSERT INTO Registi (IdRegista, Nome, Cognome, Nazionalita, AnnoNascita) VALUES
(1, 'Mario', 'Rinaldi', 'Italiana', 1966),
(2, 'Hannah', 'Müller', 'Tedesca', 1954),
(3, 'Martina', 'Guerra', 'Italiana', 1954),
(4, 'James', 'Evans', 'Inglese', 1958),
(5, 'Isabel', 'Fernández', 'Spagnola', 1962),
(6, 'Emma', 'Sorrentino', 'Italiana', 1952),
(7, 'Irene', 'Messina', 'Italiana', 1963),
(8, 'Hannah', 'Müller', 'Tedesca', 1962),
(9, 'Jean', 'Girard', 'Francese', 1952);

INSERT INTO Film (IdFilm, Titolo, Genere, Durata, AnnoUscita, IdRegista) VALUES
(1, 'Il ritorno', 'Drammatico', 104, 2026, 1),
(2, 'La casa sul lago', 'Commedia', 126, 2025, 1),
(3, 'Ultima fermata', 'Avventura', 126, 2025, 1),
(4, 'Notte di luglio', 'Fantascienza', 126, 2025, 3),
(5, 'Le stelle di Marte', 'Thriller', 126, 2025, 3),
(6, 'Un''estate al mare', 'Animazione', 120, 2026, 2),
(7, 'Il ritorno', 'Drammatico', 120, 1998, 4),
(8, 'Fuga da Neo Tokyo', 'Commedia', 126, 2026, 4),
(9, 'La festa di nozze', 'Avventura', 120, 2025, 5),
(10, 'Il volo del gabbiano', 'Fantascienza', 88, 2026, 8),
(11, 'Cuori in trasferta', 'Thriller', 118, 2026, 1),
(12, 'L''isola dei robot', 'Animazione', 88, 2025, 1),
(13, 'Ombre sul fiume', 'Drammatico', 100, 2025, 1),
(14, 'Il caso Moretti', 'Commedia', 100, 2026, 5),
(15, 'Pane e cioccolato fondente', 'Avventura', 104, 2026, 5),
(16, 'La grande corsa', 'Fantascienza', 104, 2025, 7),
(17, 'Il pianeta verde', 'Thriller', 118, 2025, 7),
(18, 'Il viaggio di Leo', 'Animazione', 104, 2025, 5);

INSERT INTO Clienti (IdCliente, Nome, Cognome, DataNascita, Citta, Email, DataTessera) VALUES
(1, 'Fabio', 'Montanari', '1971-11-29', 'Bologna', NULL, '2025-01-20'),
(2, 'Ivan', 'Caruso', '1957-01-10', 'Bologna', NULL, '2025-01-01'),
(3, 'Omar', 'Martini', '1969-07-27', 'Bologna', NULL, '2025-12-31'),
(4, 'Simone', 'Grassi', '1994-05-12', 'Bologna', 'simone.grassi@libero.it', '2024-12-31'),
(5, 'Ambra', 'Battaglia', '1953-07-01', 'Bologna', 'ambra.battaglia@gmail.com', '2026-01-01'),
(6, 'Mattia', 'Serra', '2008-02-21', 'Bologna', 'mattia.serra@outlook.it', '2025-02-24'),
(7, 'Alessandro', 'Villa', '1999-01-13', 'Casalecchio di Reno', NULL, '2023-10-17'),
(8, 'Irene', 'Esposti', '1986-01-17', 'Bologna', 'irene.esposti23@outlook.it', '2026-07-13'),
(9, 'Massimo', 'De Rosa', '1977-09-14', 'Monte San Pietro', 'massimo.derosa@gmail.com', '2023-09-09'),
(10, 'Tommaso', 'Righi', '1995-05-21', 'Pianoro', 'tommaso.righi74@outlook.it', '2023-08-12'),
(11, 'Giorgio', 'Longo', '1984-03-27', 'Monte San Pietro', NULL, '2023-08-12'),
(12, 'Amira', 'Serra', '1993-07-12', 'Bologna', 'amira.serra31@yahoo.it', '2025-04-01'),
(13, 'Tommaso', 'Gatti', '2008-12-30', 'Bologna', 'tommaso.gatti73@yahoo.it', '2026-06-25'),
(14, 'Alexandru', 'Riva', '2008-04-07', 'Bologna', NULL, '2025-02-05'),
(15, 'Silvia', 'Esposti', '1980-11-27', 'Bologna', 'silvia.esposti@yahoo.it', '2025-03-09'),
(16, 'Beatrice', 'Guidi', '2003-09-07', 'Bergamo', 'beatrice.guidi5@virgilio.it', '2023-03-21'),
(17, 'Giuseppe', 'Lenzi', '1979-10-20', 'Bologna', 'giuseppe.lenzi@yahoo.it', '2023-03-05'),
(18, 'Daniele', 'Caruso', '1975-03-15', 'Bologna', 'daniele.caruso@virgilio.it', '2025-01-06'),
(19, 'Ludovica', 'Montanari', '1973-01-15', 'Monte San Pietro', 'ludovica.montanari@libero.it', '2024-09-01'),
(20, 'Antonio', 'Bianchini', '1970-09-18', 'Napoli', 'antonio.bianchini59@yahoo.it', '2025-12-02'),
(21, 'Antonio', 'Zecchi', '2010-04-03', 'Anzola dell''Emilia', 'antonio.zecchi60@outlook.it', '2023-05-10'),
(22, 'Federico', 'Bruno', '1976-10-14', 'Bologna', 'federico.bruno6@gmail.com', '2024-05-07'),
(23, 'Emanuele', 'Grassi', '1961-04-05', 'Calderara di Reno', NULL, '2023-02-08'),
(24, 'Laura', 'Bianchi', '1979-02-25', 'Imola', 'laura.bianchi@hotmail.it', '2025-03-28'),
(25, 'Emanuele', 'Chen', '2004-05-23', 'Pianoro', 'emanuele.chen@libero.it', '2026-06-19'),
(26, 'Andrea', 'Gamberini', '2000-11-14', 'Firenze', 'andrea.gamberini86@virgilio.it', '2025-06-23'),
(27, 'Michela', 'De Luca', '1966-09-21', 'Bologna', 'michela.deluca@hotmail.it', '2023-06-26'),
(28, 'Fabio', 'Montanari', '1968-02-01', 'San Lazzaro di Savena', 'fabio.montanari75@yahoo.it', '2024-12-21'),
(29, 'Ambra', 'Mazza', '1993-09-27', 'Bologna', 'ambra.mazza38@yahoo.it', '2023-07-20'),
(30, 'Rebecca', 'De Rosa', '1993-01-03', 'Bologna', NULL, '2025-06-14');

INSERT INTO Biglietti (IdBiglietto, IdFilm, IdCliente, DataProiezione, Ora, Sala, Prezzo) VALUES
(1, 3, 17, '2025-01-20', '21:00', 'Sala 3', 9.00),
(2, 4, 1, '2025-01-23', '16:00', 'Sala 1', 6.50),
(3, 4, 1, '2025-01-23', '18:30', 'Sala 2', 7.50),
(4, 2, 16, '2025-01-27', '18:30', 'Sala 1', 7.50),
(5, 4, 1, '2025-01-29', '16:00', 'Sala 1', 6.50),
(6, 13, 14, '2025-02-11', '18:30', 'Sala 1', 7.50),
(7, 4, 10, '2025-02-12', '18:30', 'Sala 3', 7.50),
(8, 3, 27, '2025-02-18', '16:00', 'Sala 3', 6.50),
(9, 3, 2, '2025-02-20', '16:00', 'Sala 1', 6.50),
(10, 3, 2, '2025-02-24', '21:00', 'Sala 3', 9.00),
(11, 4, 23, '2025-03-02', '18:30', 'Sala 1', 7.50),
(12, 4, 28, '2025-03-13', '18:30', 'Sala 3', 7.50),
(13, 3, 4, '2025-03-29', '16:00', 'Sala 1', 6.50),
(14, 3, 9, '2025-04-03', '18:30', 'Sala 3', 7.50),
(15, 4, 12, '2025-04-06', '18:30', 'Sala 3', 7.50),
(16, 16, 6, '2025-04-08', '16:00', 'Sala 1', 6.50),
(17, 7, 24, '2025-04-11', '16:00', 'Sala 2', 6.50),
(18, 13, 16, '2025-04-15', '18:30', 'Sala 1', 7.50),
(19, 3, 4, '2025-04-16', '18:30', 'Sala 2', 7.50),
(20, 9, 28, '2025-04-19', '18:30', 'Sala 3', 7.50),
(21, 5, 27, '2025-04-23', '21:00', 'Sala 2', 9.00),
(22, 9, 2, '2025-05-12', '18:30', 'Sala 3', 7.50),
(23, 5, 21, '2025-05-12', '18:30', 'Sala 1', 7.50),
(24, 7, 3, '2025-12-31', '21:00', 'Sala 1', 9.00),
(25, 1, 2, '2026-01-18', '18:30', 'Sala 1', 7.50),
(26, 14, 7, '2026-01-19', '16:00', 'Sala 1', 6.50),
(27, 15, 19, '2026-01-20', '21:00', 'Sala 1', 9.00),
(28, 11, 19, '2026-01-21', '18:30', 'Sala 3', 7.50),
(29, 15, 11, '2026-01-25', '16:00', 'Sala 1', 6.50),
(30, 15, 9, '2026-01-29', '16:00', 'Sala 1', 6.50),
(31, 1, 16, '2026-01-29', '16:00', 'Sala 1', 6.50),
(32, 11, 19, '2026-01-30', '21:00', 'Sala 3', 9.00),
(33, 2, 3, '2026-02-02', '18:30', 'Sala 2', 7.50),
(34, 14, 16, '2026-02-04', '16:00', 'Sala 3', 6.50),
(35, 1, 17, '2026-02-04', '16:00', 'Sala 2', 6.50),
(36, 6, 1, '2026-02-07', '21:00', 'Sala 3', 9.00),
(37, 11, 6, '2026-02-15', '16:00', 'Sala 1', 6.50),
(38, 15, 15, '2026-02-21', '18:30', 'Sala 3', 7.50),
(39, 1, 1, '2026-02-22', '18:30', 'Sala 1', 7.50),
(40, 15, 7, '2026-02-23', '21:00', 'Sala 1', 9.00),
(41, 13, 3, '2026-02-24', '18:30', 'Sala 1', 7.50),
(42, 10, 3, '2026-02-28', '16:00', 'Sala 2', 6.50),
(43, 15, 16, '2026-03-15', '21:00', 'Sala 3', 9.00),
(44, 8, 3, '2026-03-24', '18:30', 'Sala 2', 7.50),
(45, 15, 4, '2026-04-08', '21:00', 'Sala 1', 9.00),
(46, 14, 2, '2026-06-02', '16:00', 'Sala 2', 6.50),
(47, 10, 2, '2026-06-15', '18:30', 'Sala 3', 7.50),
(48, 7, 25, '2026-06-26', '21:00', 'Sala 1', 9.00),
(49, 12, 8, '2026-07-13', '16:00', 'Sala 1', 6.50),
(50, 15, 13, '2026-07-15', '21:00', 'Sala 3', 9.00);
