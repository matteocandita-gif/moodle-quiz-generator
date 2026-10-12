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

-- Database «cinema» (Cinema), taglia piccolo, seme 5102: generato con database-didattici

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
(5, 'Hannah', 'Müller', 'Tedesca', 1962),
(6, 'Emma', 'Sorrentino', 'Italiana', 1952);

INSERT INTO Film (IdFilm, Titolo, Genere, Durata, AnnoUscita, IdRegista) VALUES
(1, 'Il ritorno', 'Drammatico', 126, 2026, 1),
(2, 'La casa sul lago', 'Commedia', 104, 2026, 1),
(3, 'Ultima fermata', 'Avventura', 100, 2026, 1),
(4, 'Notte di luglio', 'Fantascienza', 120, 2025, 3),
(5, 'Le stelle di Marte', 'Thriller', 104, 2025, 3),
(6, 'Un''estate al mare', 'Animazione', 104, 2026, 2),
(7, 'Il ritorno', 'Drammatico', 120, 1998, 4),
(8, 'Fuga da Neo Tokyo', 'Commedia', 100, 2025, 4),
(9, 'La festa di nozze', 'Avventura', 110, 2025, 5),
(10, 'Il volo del gabbiano', 'Fantascienza', 95, 2025, 5);

INSERT INTO Clienti (IdCliente, Nome, Cognome, DataNascita, Citta, Email, DataTessera) VALUES
(1, 'Veronica', 'Venturi', '1962-07-07', 'Bologna', NULL, '2023-03-14'),
(2, 'Francesca', 'Tinti', '1986-07-15', 'Bologna', 'francesca.tinti20@outlook.it', '2025-01-01'),
(3, 'Veronica', 'Corazza', '1967-04-01', 'Bologna', 'veronica.corazza41@virgilio.it', '2025-12-31'),
(4, 'Andrea', 'Bianchini', '1993-02-14', 'Bologna', NULL, '2024-12-31'),
(5, 'Kevin', 'Piras', '1976-10-14', 'Bologna', 'kevin.piras82@gmail.com', '2026-01-01'),
(6, 'Gianluca', 'Cattaneo', '1981-05-07', 'Bergamo', 'gianluca.cattaneo@hotmail.it', '2023-06-02'),
(7, 'Omar', 'Martini', '1969-07-27', 'Bologna', NULL, '2023-03-13'),
(8, 'Simone', 'Grassi', '1994-05-12', 'Bologna', 'simone.grassi@hotmail.it', '2023-02-18'),
(9, 'Ambra', 'Battaglia', '1953-07-01', 'Bologna', 'ambra.battaglia@yahoo.it', '2026-05-20'),
(10, 'Veronica', 'Venturi', '2008-02-21', 'San Lazzaro di Savena', 'veronica.venturi80@hotmail.it', '2025-02-24'),
(11, 'Alessandro', 'Villa', '1999-01-13', 'Casalecchio di Reno', NULL, '2023-10-17'),
(12, 'Irene', 'Esposti', '1986-01-17', 'Bologna', 'irene.esposti@virgilio.it', '2025-06-14');

INSERT INTO Biglietti (IdBiglietto, IdFilm, IdCliente, DataProiezione, Ora, Sala, Prezzo) VALUES
(1, 7, 1, '2025-01-17', '18:30', 'Sala 3', 7.50),
(2, 4, 1, '2025-01-18', '21:00', 'Sala 2', 9.00),
(3, 5, 8, '2025-02-07', '21:00', 'Sala 3', 9.00),
(4, 5, 10, '2025-02-25', '16:00', 'Sala 3', 6.50),
(5, 9, 2, '2025-03-11', '16:00', 'Sala 3', 6.50),
(6, 4, 10, '2025-08-23', '18:30', 'Sala 3', 7.50),
(7, 6, 1, '2026-01-15', '18:30', 'Sala 3', 7.50),
(8, 2, 7, '2026-01-21', '21:00', 'Sala 2', 9.00),
(9, 9, 3, '2026-01-24', '16:00', 'Sala 1', 6.50),
(10, 1, 7, '2026-01-25', '16:00', 'Sala 3', 6.50),
(11, 2, 3, '2026-01-29', '18:30', 'Sala 2', 7.50),
(12, 1, 1, '2026-01-30', '16:00', 'Sala 2', 6.50),
(13, 1, 2, '2026-01-31', '16:00', 'Sala 2', 6.50),
(14, 3, 8, '2026-02-02', '16:00', 'Sala 2', 6.50),
(15, 1, 2, '2026-02-23', '16:00', 'Sala 2', 6.50),
(16, 5, 3, '2026-03-05', '16:00', 'Sala 2', 6.50),
(17, 3, 2, '2026-03-11', '16:00', 'Sala 3', 6.50),
(18, 7, 3, '2026-03-12', '21:00', 'Sala 3', 9.00),
(19, 3, 4, '2026-07-13', '18:30', 'Sala 3', 7.50),
(20, 1, 9, '2026-08-30', '18:30', 'Sala 2', 7.50);
