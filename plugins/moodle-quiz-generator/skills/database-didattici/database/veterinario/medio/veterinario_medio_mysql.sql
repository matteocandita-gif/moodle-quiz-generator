-- Da importare in phpMyAdmin (scheda Importa) o con: mysql -u root < questo_file.sql
-- Crea il database «veterinario» e ricrea le tabelle: si può reimportare per ripartire dai dati originali.
CREATE DATABASE IF NOT EXISTS veterinario CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE veterinario;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Visite;
DROP TABLE IF EXISTS Veterinari;
DROP TABLE IF EXISTS Animali;
DROP TABLE IF EXISTS Proprietari;
SET FOREIGN_KEY_CHECKS = 1;

-- Database «veterinario» (Ambulatorio veterinario), taglia medio, seme 5103: generato con database-didattici

CREATE TABLE Proprietari (
    IdProprietario INT PRIMARY KEY,
    Nome VARCHAR(40) NOT NULL,
    Cognome VARCHAR(40) NOT NULL,
    Citta VARCHAR(40) NOT NULL,
    Telefono VARCHAR(15) NOT NULL
);

CREATE TABLE Animali (
    IdAnimale INT PRIMARY KEY,
    Nome VARCHAR(30) NOT NULL,
    Specie VARCHAR(20) NOT NULL,
    Razza VARCHAR(40),
    DataNascita DATE NOT NULL,
    DataRegistrazione DATE NOT NULL,
    IdProprietario INT NOT NULL,
    FOREIGN KEY (IdProprietario) REFERENCES Proprietari(IdProprietario)
);

CREATE TABLE Veterinari (
    IdVeterinario INT PRIMARY KEY,
    Nome VARCHAR(40) NOT NULL,
    Cognome VARCHAR(40) NOT NULL,
    Specializzazione VARCHAR(40) NOT NULL
);

CREATE TABLE Visite (
    IdVisita INT PRIMARY KEY,
    IdAnimale INT NOT NULL,
    IdVeterinario INT NOT NULL,
    Data DATE NOT NULL,
    Motivo VARCHAR(30) NOT NULL,
    Costo DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (IdAnimale) REFERENCES Animali(IdAnimale),
    FOREIGN KEY (IdVeterinario) REFERENCES Veterinari(IdVeterinario)
);

INSERT INTO Proprietari (IdProprietario, Nome, Cognome, Citta, Telefono) VALUES
(1, 'Elena', 'Orlando', 'Imola', '382 1201130'),
(2, 'Camilla', 'Coppola', 'Bologna', '384 4019446'),
(3, 'Gabriel', 'Sorrentino', 'Bologna', '392 4430723'),
(4, 'Michele', 'Greco', 'Taranto', '326 1773437'),
(5, 'Benedetta', 'Bertolini', 'Pianoro', '370 3869411'),
(6, 'Jacopo', 'Grasso', 'Castel Maggiore', '382 1131489'),
(7, 'Umberto', 'Lombardi', 'Valsamoggia', '382 4174250'),
(8, 'Giacomo', 'Conte', 'Sasso Marconi', '370 6952110'),
(9, 'Alexandru', 'Ferrara', 'Bologna', '323 3935567'),
(10, 'Omar', 'Barbieri', 'San Lazzaro di Savena', '363 7860949'),
(11, 'Andrea', 'Marino', 'Sasso Marconi', '346 2438503'),
(12, 'Filippo', 'Monti', 'Bologna', '336 6913266'),
(13, 'Camilla', 'Coppola', 'Zola Predosa', '380 8478397'),
(14, 'Rachele', 'Villa', 'Sasso Marconi', '391 1359722');

INSERT INTO Animali (IdAnimale, Nome, Specie, Razza, DataNascita, DataRegistrazione, IdProprietario) VALUES
(1, 'Luna', 'Gatto', 'Europeo', '2012-03-08', '2021-08-19', 1),
(2, 'Tigre', 'Gatto', 'Europeo', '2016-11-05', '2025-01-01', 1),
(3, 'Milo', 'Gatto', 'Siamese', '2010-04-20', '2025-12-31', 1),
(4, 'Kira', 'Gatto', 'Siamese', '2019-09-23', '2024-12-31', 3),
(5, 'Briciola', 'Gatto', NULL, '2021-05-17', '2026-01-01', 3),
(6, 'Pallino', 'Cane', 'Labrador', '2015-08-25', '2025-07-15', 2),
(7, 'Nina', 'Gatto', 'Maine coon', '2017-12-29', '2025-02-06', 4),
(8, 'Luna', 'Gatto', NULL, '2016-02-19', '2025-11-24', 4),
(9, 'Zeus', 'Pappagallo', 'Cocorita', '2018-12-18', '2019-08-08', 5),
(10, 'Bianca', 'Cane', 'Jack Russell', '2017-09-09', '2022-09-28', 13),
(11, 'Teo', 'Gatto', NULL, '2016-06-23', '2023-08-28', 14),
(12, 'Lilly', 'Cane', 'Labrador', '2014-02-10', '2023-02-03', 6),
(13, 'Oliver', 'Cane', 'Labrador', '2016-03-21', '2026-06-13', 9),
(14, 'Cleo', 'Cane', 'Jack Russell', '2015-04-09', '2022-12-16', 5),
(15, 'Birba', 'Pappagallo', 'Cocorita', '2022-02-28', '2025-12-29', 5),
(16, 'Leo', 'Coniglio', NULL, '2010-10-23', '2024-07-04', 5),
(17, 'Maya', 'Cane', 'Beagle', '2015-05-03', '2024-01-17', 12),
(18, 'Toby', 'Gatto', NULL, '2024-12-03', '2025-02-03', 5),
(19, 'Pepe', 'Cane', 'Jack Russell', '2013-05-05', '2025-06-13', 12),
(20, 'Neve', 'Gatto', 'Siamese', '2013-10-12', '2023-04-20', 11),
(21, 'Romeo', 'Gatto', 'Europeo', '2023-03-02', '2026-04-29', 12),
(22, 'Molly', 'Tartaruga', NULL, '2018-06-21', '2022-08-28', 10),
(23, 'Ciuffo', 'Gatto', 'Europeo', '2020-04-10', '2022-08-05', 11),
(24, 'Arturo', 'Tartaruga', NULL, '2015-07-17', '2020-12-02', 8),
(25, 'Mia', 'Gatto', 'Persiano', '2014-12-13', '2025-06-14', 11);

INSERT INTO Veterinari (IdVeterinario, Nome, Cognome, Specializzazione) VALUES
(1, 'Lucia', 'Negri', 'Medicina generale'),
(2, 'Luigi', 'Lodi', 'Chirurgia'),
(3, 'Asia', 'Pancaldi', 'Dermatologia'),
(4, 'Mattia', 'Grasso', 'Cardiologia'),
(5, 'Umberto', 'Colombo', 'Medicina generale'),
(6, 'Emma', 'Greco', 'Odontoiatria'),
(7, 'Federico', 'Pellegrino', 'Medicina generale');

INSERT INTO Visite (IdVisita, IdAnimale, IdVeterinario, Data, Motivo, Costo) VALUES
(1, 9, 4, '2019-10-14', 'Controllo', 40.00),
(2, 1, 1, '2021-08-22', 'Visita urgente', 80.00),
(3, 1, 1, '2021-09-05', 'Controllo', 40.00),
(4, 1, 1, '2021-11-30', 'Visita urgente', 80.00),
(5, 1, 1, '2022-02-14', 'Controllo', 40.00),
(6, 1, 3, '2022-04-20', 'Visita dermatologica', 70.00),
(7, 23, 5, '2022-09-20', 'Visita urgente', 80.00),
(8, 10, 1, '2022-10-30', 'Visita urgente', 80.00),
(9, 23, 2, '2022-11-04', 'Sterilizzazione', 180.00),
(10, 22, 5, '2022-11-14', 'Visita urgente', 80.00),
(11, 10, 2, '2022-12-20', 'Sterilizzazione', 180.00),
(12, 22, 3, '2023-01-17', 'Visita dermatologica', 70.00),
(13, 14, 5, '2023-01-28', 'Controllo', 40.00),
(14, 23, 4, '2023-02-21', 'Ecocardiogramma', 120.00),
(15, 12, 5, '2023-03-25', 'Controllo', 40.00),
(16, 20, 6, '2023-05-02', 'Pulizia dei denti', 90.00),
(17, 20, 5, '2023-05-14', 'Vaccinazione', 45.00),
(18, 20, 2, '2023-09-17', 'Sterilizzazione', 180.00),
(19, 12, 1, '2023-10-05', 'Controllo', 40.00),
(20, 11, 5, '2023-10-28', 'Vaccinazione', 45.00),
(21, 11, 1, '2024-01-13', 'Vaccinazione', 45.00),
(22, 20, 4, '2024-05-21', 'Ecocardiogramma', 120.00),
(23, 16, 1, '2024-08-29', 'Visita urgente', 80.00),
(24, 2, 2, '2025-01-10', 'Sterilizzazione', 180.00),
(25, 2, 5, '2025-01-21', 'Controllo', 40.00),
(26, 2, 1, '2025-01-29', 'Controllo', 40.00),
(27, 4, 1, '2025-02-09', 'Vaccinazione', 45.00),
(28, 7, 1, '2025-02-13', 'Vaccinazione', 45.00),
(29, 18, 5, '2025-03-07', 'Visita urgente', 80.00),
(30, 18, 4, '2025-05-02', 'Controllo', 40.00),
(31, 2, 1, '2025-05-11', 'Visita urgente', 80.00),
(32, 19, 2, '2025-06-29', 'Controllo', 40.00),
(33, 16, 5, '2025-07-26', 'Visita urgente', 80.00),
(34, 18, 1, '2025-10-29', 'Visita urgente', 80.00),
(35, 8, 6, '2025-12-11', 'Estrazione', 150.00),
(36, 19, 4, '2026-01-07', 'Controllo', 40.00),
(37, 8, 5, '2026-01-11', 'Controllo', 40.00),
(38, 3, 5, '2026-01-23', 'Visita urgente', 80.00),
(39, 3, 3, '2026-02-01', 'Visita dermatologica', 70.00),
(40, 3, 2, '2026-02-09', 'Sterilizzazione', 180.00),
(41, 3, 1, '2026-02-12', 'Controllo', 40.00),
(42, 19, 1, '2026-02-23', 'Vaccinazione', 45.00),
(43, 3, 2, '2026-03-19', 'Controllo', 40.00),
(44, 15, 1, '2026-06-14', 'Vaccinazione', 45.00),
(45, 21, 5, '2026-07-23', 'Controllo', 40.00),
(46, 13, 5, '2026-08-13', 'Visita urgente', 80.00),
(47, 13, 1, '2026-08-14', 'Vaccinazione', 45.00),
(48, 6, 1, '2026-08-21', 'Controllo', 40.00),
(49, 3, 5, '2026-09-22', 'Visita urgente', 80.00),
(50, 8, 5, '2026-09-23', 'Vaccinazione', 45.00);
