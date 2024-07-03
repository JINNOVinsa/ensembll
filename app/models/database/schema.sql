DROP TABLE IF EXISTS Bookings;
DROP TABLE IF EXISTS Plates;
DROP TABLE IF EXISTS UsersCredentials;
DROP TABLE IF EXISTS AuthTokens;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS ExceptionalOpen;
DROP TABLE IF EXISTS CriticLevel;
DROP TABLE IF EXISTS Parkings;
DROP TABLE IF EXISTS Entity;
DROP TABLE IF EXISTS Profiles;



-- Stocke les informations des structures
CREATE TABLE Entity (
    id varchar(150) primary key,
    eName varchar(200) default "Structure",
    nbPlacesAllocated int,  -- Nombre total de places allouées
    nbFreePlaces int -- Nombre de places disponibles
);

CREATE TABLE Profiles (
    id varchar(36) primary key default UUID(),
    profileName varchar(255) not null default "Aucun profil",
    entityId varchar(150) not null,
    criticity int not null default 1,
    PRIMARY KEY (id, profileName),
    FOREIGN KEY (entityId) REFERENCES Entity(id)
);

CREATE TABLE CriticityTables (
    id varchar(36) primary key default UUID(),
    profileId varchar(36),
    startTS time not null,
    endTS time not null,
    criticityLevel int not null,

    FOREIGN KEY (profileId) REFERENCES Profiles(id)
);

-- Enregistre les comptes utilisateurs
CREATE TABLE Users (
    id varchar(150) not null, -- Identifiant PARKKI

    firstName varchar(30) not null,
    lastName varchar(30) not null,
    mail varchar(50) not null,
    phoneNumber varchar(15) default null,

    usrType varchar(36) not null,       -- profile
    hierarchicalLevel int default 0,    -- 0 user, 1 admin, 2 super-admin

    entityId varchar(150) not null,

    approved tinyint(1) default 0,  -- -1 refused, 0 pending, 1 approved

    created datetime not null default now(),

    PRIMARY KEY (id, mail)
    FOREIGN KEY (entityId) REFERENCES Entity(id),
    FOREIGN KEY (usrType) REFERENCES Profiles(id)
);

-- Référence les plaques d'immatriculation des usagers enregistrés
CREATE TABLE Plates (
    id uuid NOT NULL PRIMARY KEY DEFAULT UUID(),
    usrId varchar(150) not null, -- Identifiant User
    plate varchar(10) not null,
    FOREIGN KEY (usrId) REFERENCES Users(id)
);


-- Enregistre les entrées d'usagers dans les différents parking
CREATE TABLE Parkings (
    id varchar(150) primary key, -- Identifiant PARKKI
    parkingName varchar(150) not null,
    capacity int not null,
    availableSpaces int
);

-- Enregistre les ouvertures exceptionnelles de la barrière
CREATE TABLE ExceptionalOpen (
    id varchar(36) primary key default UUID(),
    pId varchar(150) not null,
    openTS datetime not null,
    closeTS datetime,
    FOREIGN KEY (pId) REFERENCES Parkings(id)
);

CREATE TABLE Bookings (
    uuid varchar(65) primary key,
    usrId varchar(150) not null,
    plate varchar(10) not null,
    present boolean default false,
    startTS datetime not null,
    endTS datetime not null,

    repeatInterval varchar(7) not null,

    customInterval varchar(7) default null,
    customAmount int default null,

    onMonday boolean default false,
    onTuesday boolean default false,
    onWednesday boolean default false,
    onThursday boolean default false,
    onFriday boolean default false,
    onSaturday boolean default false,
    onSunday boolean default false,

    ending datetime default null,

    associedCriticity int(11) not null default 1,

    FOREIGN KEY (usrId, plate) REFERENCES Plates(usrId, plate)
);

CREATE TABLE BookingsApiPeriods (
    id varchar(26) primary key,
    bookingId varchar(65),
    FOREIGN KEY (bookingId) REFERENCES Bookings(uuid)
);

CREATE TABLE UsersCredentials (
    usrLogin varchar(150) primary key,

    id varchar(150),

    pswdhash varchar(64) not null,
    salt varchar(15) not null,

    FOREIGN KEY (id) REFERENCES Users(id)
);

CREATE TABLE AuthTokens (
    token varchar(32) primary key,
    id varchar(150),
    FOREIGN KEY (id) REFERENCES Users(id)
);

CREATE TABLE ResetPswd (
    usrToken varchar(128),
    usrId varchar(150),
    created datetime not null default now(),

    PRIMARY KEY (usrToken, usrId),
    FOREIGN KEY (usrId) REFERENCES Users(id)
);
-- ?
-- CREATE TABLE CriticLevel ()