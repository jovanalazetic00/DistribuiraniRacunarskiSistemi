DROP DATABASE IF EXISTS DRS_PROJEKAT;

CREATE DATABASE DRS_PROJEKAT;

use DRS_PROJEKAT;

CREATE TABLE Kartica(
   BrojKartice BIGINT,
   ImeKorisnika VARCHAR(50) NOT NULL,
   DatumIsteka date,
   NovcanoStanje FLOAT NOT NULL,
   SigurnosniKod INTEGER NOT NULL,
   CONSTRAINT kartica_PK PRIMARY KEY (BrojKartice)
);

INSERT INTO Kartica(BrojKartice,ImeKorisnika,DatumIsteka,NovcanoStanje,SigurnosniKod) 
VALUES(4242424242424242,"Pera",'2026-02-01',2000,123);
INSERT INTO Kartica(BrojKartice,ImeKorisnika,DatumIsteka,NovcanoStanje,SigurnosniKod) 
VALUES(4343434343434343,"Nemanja",'2030-10-05',30000,456);

CREATE TABLE Korisnik(
    Ime VARCHAR(50) NOT NULL,
    Prezime VARCHAR(50) NOT NULL,
    Adresa VARCHAR(50) NOT NULL,
    Grad VARCHAR(50) NOT NULL,
    Drzava VARCHAR(50) NOT NULL,
    BrojTelefona BIGINT NOT NULL,
    Email VARCHAR(50) NOT NULL, 
    Lozinka VARCHAR(50) NOT NULL,
    BrojKartice BIGINT,
    NovcanoStanje FLOAT NOT NULL,
    Verifikovan TINYINT NOT NULL,
    Valuta VARCHAR(3) NOT NULL,
    CONSTRAINT korisnik_PK PRIMARY KEY (Email)
);

INSERT INTO Korisnik(Ime,Prezime,Adresa,Grad,Drzava,BrojTelefona,Email,Lozinka,BrojKartice,NovcanoStanje,Verifikovan,Valuta)
VALUES("Pera","Peric","Bulevar Evrope 98","Novi Sad","Srbija",0601112223,"pera@gmail.com","lozinka1",0,0,0,"RSD");


CREATE TABLE Transakcija(
       IdTransakcije INTEGER NOT NULL AUTO_INCREMENT,
       Posiljalac VARCHAR(50) NOT NULL,
       Primalac VARCHAR(50),
       BrojKarticeKorisnika BIGINT,
       KolicinaNovca FLOAT NOT NULL,
       StatusTransakcije VARCHAR(20) NOT NULL,
       Valuta VARCHAR(3) NOT NULL,
       CONSTRAINT transakcija_PK PRIMARY KEY (IdTransakcije)
       
);