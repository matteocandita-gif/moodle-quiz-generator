-- Database «biblioteca» (Biblioteca scolastica), taglia piccolo, seme 2026: generato con database-didattici

CREATE TABLE Autori (
    IdAutore INT PRIMARY KEY,
    Nome VARCHAR(40) NOT NULL,
    Cognome VARCHAR(40) NOT NULL,
    Nazionalita VARCHAR(30) NOT NULL,
    AnnoNascita INT
);

CREATE TABLE Libri (
    ISBN CHAR(13) PRIMARY KEY,
    Titolo VARCHAR(100) NOT NULL,
    Genere VARCHAR(20) NOT NULL,
    AnnoPubblicazione INT NOT NULL,
    Pagine INT,
    Copie INT NOT NULL,
    IdAutore INT NOT NULL,
    FOREIGN KEY (IdAutore) REFERENCES Autori(IdAutore)
);

CREATE TABLE Studenti (
    Matricola INT PRIMARY KEY,
    Nome VARCHAR(40) NOT NULL,
    Cognome VARCHAR(40) NOT NULL,
    Classe VARCHAR(3) NOT NULL,
    Email VARCHAR(80) NOT NULL,
    UNIQUE (Email)
);

CREATE TABLE Prestiti (
    IdPrestito INT PRIMARY KEY,
    ISBN CHAR(13) NOT NULL,
    Matricola INT NOT NULL,
    DataPrestito DATE NOT NULL,
    DataRestituzione DATE,
    FOREIGN KEY (ISBN) REFERENCES Libri(ISBN),
    FOREIGN KEY (Matricola) REFERENCES Studenti(Matricola)
);

INSERT INTO Autori (IdAutore, Nome, Cognome, Nazionalita, AnnoNascita) VALUES
(1, 'Marta', 'Monari', 'Italiana', 1933),
(2, 'Bianca', 'Corazza', 'Italiana', 1982),
(3, 'Florencia', 'Gómez', 'Argentina', 1930),
(4, 'Bianca', 'Corazza', 'Italiana', 1982),
(5, 'Elena', 'Martínez', 'Spagnola', 1964),
(6, 'Viola', 'Monari', 'Italiana', 1963);

INSERT INTO Libri (ISBN, Titolo, Genere, AnnoPubblicazione, Pagine, Copie, IdAutore) VALUES
('9781327139357', 'Racconti della città', 'Fantasy', 1989, 467, 2, 3),
('9786676307749', 'La lettera senza nome', 'Storico', 2000, 209, 3, 1),
('9788698924284', 'Il ritorno', 'Giallo', 2018, NULL, 1, 4),
('9783805002643', 'Amore di mezzanotte', 'Storico', 2002, 557, 3, 4),
('9789911183700', 'Un amore lontano', 'Storico', 2013, 603, 2, 5),
('9780142203221', 'La lettera e l''ombra', 'Poesia', 2001, 559, 3, 3),
('9787269867519', 'Racconti della memoria', 'Poesia', 2002, 567, 3, 2),
('9784717480361', 'La lettera d''inverno', 'Fantasy', 2015, 617, 2, 3),
('9787080460787', 'Il segreto', 'Fantasy', 2004, 600, 1, 4),
('9783936254645', 'L''isola', 'Romanzo', 2002, 184, 2, 2);

INSERT INTO Studenti (Matricola, Nome, Cognome, Classe, Email) VALUES
(1001, 'Giulio', 'Silvestri', '3A', 'giulio.silvestri@studenti.istituto.it'),
(1002, 'Mario', 'Costantini', '3B', 'mario.costantini@studenti.istituto.it'),
(1003, 'Paolo', 'Govoni', '5B', 'paolo.govoni83@studenti.istituto.it'),
(1004, 'Leonardo', 'Pancaldi', '5A', 'leonardo.pancaldi@studenti.istituto.it'),
(1005, 'Mattia', 'Fontana', '4B', 'mattia.fontana4@studenti.istituto.it'),
(1006, 'Federico', 'Martino', '5A', 'federico.martino@studenti.istituto.it'),
(1007, 'Greta', 'D''Angelo', '5A', 'greta.dangelo@studenti.istituto.it'),
(1008, 'Giulio', 'Silvestri', '3B', 'giulio.silvestri58@studenti.istituto.it');

INSERT INTO Prestiti (IdPrestito, ISBN, Matricola, DataPrestito, DataRestituzione) VALUES
(1, '9783805002643', 1002, '2025-09-17', NULL),
(2, '9784717480361', 1006, '2025-09-25', '2025-10-31'),
(3, '9787080460787', 1004, '2025-10-02', '2025-10-16'),
(4, '9781327139357', 1006, '2025-10-09', '2025-10-24'),
(5, '9787080460787', 1002, '2025-11-10', '2025-11-30'),
(6, '9783805002643', 1008, '2025-11-24', '2025-12-08'),
(7, '9781327139357', 1003, '2025-12-04', '2026-01-12'),
(8, '9787269867519', 1003, '2025-12-19', '2026-01-07'),
(9, '9788698924284', 1002, '2026-01-01', NULL),
(10, '9780142203221', 1004, '2026-01-12', '2026-01-19'),
(11, '9780142203221', 1001, '2026-01-31', NULL),
(12, '9787080460787', 1008, '2026-02-02', NULL),
(13, '9784717480361', 1006, '2026-03-03', '2026-03-17'),
(14, '9784717480361', 1004, '2026-04-15', '2026-04-29'),
(15, '9787269867519', 1003, '2026-04-20', '2026-04-28'),
(16, '9780142203221', 1005, '2026-05-19', '2026-06-10');
