-- Database «veterinario» (Ambulatorio veterinario), taglia piccolo, seme 5103: generato con database-didattici

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
(5, 'Camilla', 'Coppola', 'Zola Predosa', '370 3869411'),
(6, 'Jacopo', 'Grasso', 'Castel Maggiore', '382 1131489');

INSERT INTO Animali (IdAnimale, Nome, Specie, Razza, DataNascita, DataRegistrazione, IdProprietario) VALUES
(1, 'Luna', 'Gatto', 'Europeo', '2018-11-22', '2019-11-18', 1),
(2, 'Tigre', 'Gatto', 'Siamese', '2018-09-05', '2025-01-01', 1),
(3, 'Milo', 'Gatto', 'Siamese', '2024-01-15', '2025-12-31', 1),
(4, 'Kira', 'Gatto', 'Persiano', '2014-09-13', '2024-12-31', 3),
(5, 'Briciola', 'Gatto', 'Maine coon', '2022-06-04', '2026-01-01', 3),
(6, 'Pallino', 'Gatto', 'Maine coon', '2024-04-13', '2024-06-26', 2),
(7, 'Nina', 'Cane', 'Pastore tedesco', '2021-03-09', '2021-12-05', 4),
(8, 'Luna', 'Pappagallo', 'Cocorita', '2010-05-25', '2019-05-08', 4),
(9, 'Zeus', 'Gatto', 'Maine coon', '2015-06-04', '2021-08-28', 5),
(10, 'Bianca', 'Gatto', 'Europeo', '2022-10-26', '2025-06-14', 5);

INSERT INTO Veterinari (IdVeterinario, Nome, Cognome, Specializzazione) VALUES
(1, 'Angelo', 'Grandi', 'Medicina generale'),
(2, 'Thomas', 'Chen', 'Chirurgia'),
(3, 'Vincenzo', 'De Santis', 'Dermatologia'),
(4, 'Filippo', 'Monti', 'Cardiologia'),
(5, 'Rebecca', 'Ferraro', 'Medicina generale');

INSERT INTO Visite (IdVisita, IdAnimale, IdVeterinario, Data, Motivo, Costo) VALUES
(1, 1, 3, '2019-11-19', 'Controllo', 40.00),
(2, 1, 1, '2019-11-27', 'Controllo', 40.00),
(3, 1, 1, '2019-12-23', 'Controllo', 40.00),
(4, 8, 1, '2020-06-24', 'Visita urgente', 80.00),
(5, 1, 1, '2021-03-09', 'Controllo', 40.00),
(6, 9, 2, '2022-03-16', 'Intervento', 250.00),
(7, 9, 1, '2022-05-31', 'Controllo', 40.00),
(8, 6, 1, '2024-09-02', 'Controllo', 40.00),
(9, 2, 2, '2025-01-04', 'Sterilizzazione', 180.00),
(10, 2, 4, '2025-01-11', 'Ecocardiogramma', 120.00),
(11, 2, 2, '2025-01-12', 'Intervento', 250.00),
(12, 4, 1, '2025-03-30', 'Visita urgente', 80.00),
(13, 2, 1, '2025-05-02', 'Visita urgente', 80.00),
(14, 4, 1, '2025-05-19', 'Controllo', 40.00),
(15, 4, 1, '2025-07-04', 'Vaccinazione', 45.00),
(16, 2, 1, '2025-12-05', 'Vaccinazione', 45.00),
(17, 3, 3, '2026-01-07', 'Visita dermatologica', 70.00),
(18, 3, 1, '2026-01-21', 'Controllo', 40.00),
(19, 3, 1, '2026-05-24', 'Controllo', 40.00),
(20, 3, 1, '2026-06-25', 'Visita urgente', 80.00);
