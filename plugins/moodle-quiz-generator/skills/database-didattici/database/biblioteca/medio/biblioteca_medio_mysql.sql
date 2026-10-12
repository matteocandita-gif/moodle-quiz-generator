-- Da importare in phpMyAdmin (scheda Importa) o con: mysql -u root < questo_file.sql
-- Crea il database «biblioteca» e ricrea le tabelle: si può reimportare per ripartire dai dati originali.
CREATE DATABASE IF NOT EXISTS biblioteca CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE biblioteca;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Prestiti;
DROP TABLE IF EXISTS Studenti;
DROP TABLE IF EXISTS Libri;
DROP TABLE IF EXISTS Autori;
SET FOREIGN_KEY_CHECKS = 1;

-- Database «biblioteca» (Biblioteca scolastica), taglia medio, seme 2026: generato con database-didattici

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
(4, 'Rachele', 'Caruso', 'Italiana', 1982),
(5, 'Elena', 'Martínez', 'Spagnola', 1964),
(6, 'Viola', 'Monari', 'Italiana', 1963),
(7, 'Francesca', 'Lodi', 'Italiana', 1959),
(8, 'Giulia', 'Draghetti', 'Italiana', 1971),
(9, 'Karen', 'Miller', 'Statunitense', 1982),
(10, 'Agnese', 'Bonfiglioli', 'Italiana', 1981),
(11, 'James', 'Wilson', 'Inglese', 1926),
(12, 'Anna', 'Becker', 'Tedesca', 1981),
(13, 'Bianca', 'Corazza', 'Italiana', 1989),
(14, 'Serena', 'Martino', 'Italiana', 1984),
(15, 'Lena', 'Becker', 'Tedesca', 1957);

INSERT INTO Libri (ISBN, Titolo, Genere, AnnoPubblicazione, Pagine, Copie, IdAutore) VALUES
('9788421018738', 'Il silenzio perduto', 'Fantasy', 1998, 591, 1, 3),
('9787843355507', 'Il silenzio', 'Saggio', 2000, 534, 3, 1),
('9784717480361', 'Racconti della notte', 'Saggio', 2015, NULL, 2, 6),
('9784037861054', 'Amore di mezzanotte', 'Storico', 2004, 362, 2, 14),
('9784923573028', 'Un amore lontano', 'Romanzo', 2017, 104, 1, 14),
('9782667495386', 'La casa dimenticata', 'Poesia', 2005, 364, 3, 4),
('9789936160875', 'Racconti del ritorno', 'Poesia', 1960, 593, 3, 3),
('9782525159540', 'Il sogno e il porto', 'Fantasy', 2017, 606, 1, 4),
('9786475530314', 'La lettera e il viaggio', 'Giallo', 2018, 489, 3, 13),
('9780315393763', 'L''isola', 'Fantasy', 1966, 445, 1, 1),
('9785599227394', 'Il mare', 'Romanzo', 2022, 423, 2, 6),
('9785183963894', 'La casa e il viaggio', 'Storico', 2017, 434, 3, 10),
('9780744592332', 'Il fiume senza nome', 'Storico', 1972, 139, 3, 1),
('9780591510462', 'Lo specchio lontano', 'Storico', 2017, 280, 2, 11),
('9785940735819', 'La lettera', 'Fantasy', 2006, 281, 1, 14),
('9785055014497', 'La memoria', 'Storico', 1998, 583, 1, 5),
('9783641573690', 'Racconti del vento', 'Romanzo', 2007, 326, 1, 14),
('9782879341616', 'Racconti della casa', 'Fantasy', 2018, 117, 1, 7),
('9789510926117', 'L''estate e il giardino', 'Saggio', 2001, 391, 2, 10),
('9781872832839', 'Il confine e il giardino', 'Romanzo', 2017, 198, 2, 13),
('9786470912414', 'Il sogno e la stazione', 'Saggio', 2004, 373, 1, 11),
('9781100044556', 'Racconti dell''ombra', 'Storico', 1976, 104, 2, 3),
('9784393655803', 'La lettera perduta', 'Romanzo', 2009, 215, 3, 2),
('9786030952492', 'Racconti del porto', 'Saggio', 2025, 310, 2, 6),
('9785965912761', 'La lettera di vetro', 'Romanzo', 2004, 454, 3, 14),
('9787281260760', 'Lo specchio', 'Romanzo', 2010, 386, 2, 1),
('9783878185755', 'Il ritorno', 'Giallo', 2019, 440, 3, 6),
('9780508021414', 'La notte lontana', 'Saggio', 2001, 218, 2, 10),
('9782483037223', 'Racconti del bosco', 'Storico', 2014, 454, 2, 1),
('9783328203515', 'La strada e la casa', 'Saggio', 2008, 277, 1, 11),
('9780980351187', 'Il confine', 'Fantasy', 1988, 106, 3, 5),
('9782549709526', 'Racconti del silenzio', 'Saggio', 2021, 273, 1, 3),
('9787486523758', 'Racconti della stazione', 'Romanzo', 2021, 147, 3, 6),
('9783702721917', 'Il fiume', 'Fantasy', 1974, 498, 1, 1),
('9787030910422', 'L''inverno e la strada', 'Saggio', 2015, 575, 2, 6),
('9788751022855', 'L''isola e il confine', 'Romanzo', 2005, 266, 2, 7),
('9788668757732', 'Racconti dell''estate', 'Saggio', 1966, 312, 2, 3),
('9782185113890', 'La torre senza nome', 'Giallo', 2018, 177, 3, 7),
('9781333242809', 'Racconti della strada', 'Giallo', 2010, 284, 2, 9),
('9787077170640', 'L''estate e la lettera', 'Fantasy', 2002, 522, 3, 4);

INSERT INTO Studenti (Matricola, Nome, Cognome, Classe, Email) VALUES
(1001, 'Alberto', 'Fabbri', '4A', 'alberto.fabbri@studenti.istituto.it'),
(1002, 'Gabriele', 'Ricci', '3A', 'gabriele.ricci@studenti.istituto.it'),
(1003, 'Stefano', 'Giordano', '4A', 'stefano.giordano@studenti.istituto.it'),
(1004, 'Eleonora', 'Biagi', '3B', 'eleonora.biagi@studenti.istituto.it'),
(1005, 'Fabio', 'Galli', '4A', 'fabio.galli35@studenti.istituto.it'),
(1006, 'Benedetta', 'Lombardi', '4B', 'benedetta.lombardi@studenti.istituto.it'),
(1007, 'Rebecca', 'Bernardi', '5B', 'rebecca.bernardi59@studenti.istituto.it'),
(1008, 'Roberto', 'Pancaldi', '4B', 'roberto.pancaldi@studenti.istituto.it'),
(1009, 'Luigi', 'Costantini', '5B', 'luigi.costantini48@studenti.istituto.it'),
(1010, 'Maria', 'Battaglia', '3A', 'maria.battaglia@studenti.istituto.it'),
(1011, 'Diego', 'Brunelli', '4A', 'diego.brunelli69@studenti.istituto.it'),
(1012, 'Vittoria', 'Farina', '3B', 'vittoria.farina13@studenti.istituto.it'),
(1013, 'Laura', 'Zecchi', '5A', 'laura.zecchi@studenti.istituto.it'),
(1014, 'Giada', 'Brunelli', '4B', 'giada.brunelli60@studenti.istituto.it'),
(1015, 'Cristina', 'Messina', '4B', 'cristina.messina@studenti.istituto.it'),
(1016, 'Roberto', 'Sartori', '4B', 'roberto.sartori91@studenti.istituto.it'),
(1017, 'Eleonora', 'Marchetti', '4B', 'eleonora.marchetti@studenti.istituto.it'),
(1018, 'Ivan', 'Carbone', '4A', 'ivan.carbone@studenti.istituto.it'),
(1019, 'Paolo', 'Carbone', '4B', 'paolo.carbone88@studenti.istituto.it'),
(1020, 'Caterina', 'Chen', '5B', 'caterina.chen@studenti.istituto.it'),
(1021, 'Elisa', 'Riva', '3B', 'elisa.riva@studenti.istituto.it'),
(1022, 'Mario', 'Guerra', '5A', 'mario.guerra@studenti.istituto.it'),
(1023, 'Roberta', 'Guidi', '4B', 'roberta.guidi6@studenti.istituto.it'),
(1024, 'Raffaele', 'Bassi', '4A', 'raffaele.bassi@studenti.istituto.it'),
(1025, 'Andrei', 'Chen', '5A', 'andrei.chen30@studenti.istituto.it'),
(1026, 'Gabriel', 'Neri', '5B', 'gabriel.neri61@studenti.istituto.it'),
(1027, 'Arianna', 'Guidi', '5B', 'arianna.guidi44@studenti.istituto.it'),
(1028, 'Andrea', 'Carbone', '5A', 'andrea.carbone@studenti.istituto.it'),
(1029, 'Carlotta', 'Donati', '5A', 'carlotta.donati@studenti.istituto.it'),
(1030, 'Alberto', 'Fabbri', '3A', 'alberto.fabbri18@studenti.istituto.it');

INSERT INTO Prestiti (IdPrestito, ISBN, Matricola, DataPrestito, DataRestituzione) VALUES
(1, '9784717480361', 1016, '2025-09-18', '2025-10-13'),
(2, '9785965912761', 1016, '2025-09-23', '2025-10-09'),
(3, '9786470912414', 1005, '2025-09-28', '2025-10-06'),
(4, '9788668757732', 1002, '2025-10-02', '2025-10-24'),
(5, '9785965912761', 1024, '2025-10-02', '2025-10-13'),
(6, '9783328203515', 1013, '2025-10-09', NULL),
(7, '9782185113890', 1002, '2025-10-20', '2025-11-20'),
(8, '9786030952492', 1006, '2025-10-24', NULL),
(9, '9780744592332', 1004, '2025-10-25', '2025-11-07'),
(10, '9782483037223', 1007, '2025-11-12', '2025-12-22'),
(11, '9784923573028', 1025, '2025-11-15', '2025-12-09'),
(12, '9786475530314', 1004, '2025-11-27', '2025-12-22'),
(13, '9780508021414', 1001, '2025-11-28', '2025-12-18'),
(14, '9780744592332', 1005, '2025-12-02', '2025-12-13'),
(15, '9785183963894', 1022, '2025-12-02', '2026-01-05'),
(16, '9785599227394', 1017, '2025-12-21', NULL),
(17, '9782525159540', 1006, '2025-12-28', '2026-01-12'),
(18, '9786030952492', 1023, '2025-12-31', NULL),
(19, '9780744592332', 1012, '2026-01-01', NULL),
(20, '9783702721917', 1005, '2026-01-01', NULL),
(21, '9787281260760', 1010, '2026-01-04', '2026-02-02'),
(22, '9785055014497', 1013, '2026-01-15', '2026-02-07'),
(23, '9787843355507', 1015, '2026-01-16', '2026-02-20'),
(24, '9788751022855', 1011, '2026-01-23', NULL),
(25, '9785599227394', 1018, '2026-01-23', '2026-01-28'),
(26, '9785183963894', 1025, '2026-01-24', NULL),
(27, '9782185113890', 1028, '2026-01-24', '2026-01-28'),
(28, '9785183963894', 1005, '2026-01-29', NULL),
(29, '9787843355507', 1016, '2026-01-31', '2026-03-04'),
(30, '9783702721917', 1015, '2026-02-01', '2026-03-07'),
(31, '9783702721917', 1004, '2026-02-03', '2026-02-11'),
(32, '9784923573028', 1024, '2026-02-14', NULL),
(33, '9787030910422', 1001, '2026-02-15', '2026-03-13'),
(34, '9782667495386', 1028, '2026-02-28', '2026-03-24'),
(35, '9780315393763', 1030, '2026-02-28', '2026-04-04'),
(36, '9789510926117', 1024, '2026-03-20', '2026-04-22'),
(37, '9783702721917', 1017, '2026-03-30', '2026-04-15'),
(38, '9788668757732', 1004, '2026-03-31', NULL),
(39, '9786030952492', 1021, '2026-04-03', '2026-05-10'),
(40, '9787030910422', 1028, '2026-04-19', '2026-05-21'),
(41, '9782667495386', 1014, '2026-04-24', '2026-05-07'),
(42, '9784393655803', 1005, '2026-05-07', '2026-05-13'),
(43, '9787030910422', 1003, '2026-05-11', '2026-06-09'),
(44, '9782667495386', 1015, '2026-05-12', '2026-06-10'),
(45, '9780315393763', 1010, '2026-05-14', '2026-06-10'),
(46, '9788668757732', 1015, '2026-05-18', '2026-05-30'),
(47, '9782483037223', 1018, '2026-05-19', '2026-06-04'),
(48, '9782879341616', 1025, '2026-05-23', '2026-06-10'),
(49, '9783878185755', 1002, '2026-05-23', '2026-06-06'),
(50, '9785055014497', 1008, '2026-05-26', '2026-06-08');
