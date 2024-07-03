TRUNCATE TABLE Entity;
TRUNCATE TABLE Users;
TRUNCATE TABLE Plates;
TRUNCATE TABLE Parkings;
TRUNCATE TABLE ExceptionalOpen;
TRUNCATE TABLE Bookings;

INSERT INTO Entity VALUES ("id1", 150, 150);
INSERT INTO Entity VALUES ("id2", 75, 30);
INSERT INTO Entity VALUES ("id3", 90, 90);
INSERT INTO Entity VALUES ("id4", 210, 175);

INSERT INTO Profiles (profileName) VALUES ('Liberal externe (médecin, kiné,...)');
INSERT INTO Profiles (profileName) VALUES ('Salarié, enseignant, vacataire');
INSERT INTO Profiles (profileName) VALUES ('Intervenant extérieur');
INSERT INTO Profiles (profileName) VALUES ('Client, visiteur');
INSERT INTO Profiles (profileName) VALUES ('Habitant, étudiant');

INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId1", "1", "2", "mail", "2cfdeb8b-8eac-11ed-88e1-c6d5d9bd2b9b", "id1");
INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId2", "1", "2", "mail", 0, "id1");
INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId3", "1", "2", "mail", 0, "id1");
INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId4", "1", "2", "mail", 0, "id2");
INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId5", "1", "2", "mail", 0, "id2");
INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId6", "1", "2", "mail", 0, "id2");
INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId7", "1", "2", "mail", 0, "id3");
INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId8", "1", "2", "mail", 0, "id3");
INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId9", "1", "2", "mail", 0, "id3");
INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId10", "1", "2", "mail", 0, "id4");
INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId11", "1", "2", "mail", 0, "id4");
INSERT INTO Users (id, firstname, lastname, mail, usrType, entityId) VALUES ("uId12", "1", "2", "mail", 0, "id4");

INSERT INTO Plates(usrId, plate) VALUES ("uId1", "AA-123-AA");
INSERT INTO Plates(usrId, plate) VALUES ("uId1", "1234 AA 00");
INSERT INTO Plates(usrId, plate) VALUES ("uId2", "EF-615-ZK");
INSERT INTO Plates(usrId, plate) VALUES ("uId3", "DZ-345-SC");
INSERT INTO Plates(usrId, plate) VALUES ("uId4", "OK-864-VF");
INSERT INTO Plates(usrId, plate) VALUES ("uId5", "DS-354-CS");
INSERT INTO Plates(usrId, plate) VALUES ("uId6", "VR-864-MF");
INSERT INTO Plates(usrId, plate) VALUES ("uId7", "PA-681-IC");
INSERT INTO Plates(usrId, plate) VALUES ("uId8", "FD-513-JG");
INSERT INTO Plates(usrId, plate) VALUES ("uId9", "PO-684-DV");
INSERT INTO Plates(usrId, plate) VALUES ("uId10", "DV-035-EF");
INSERT INTO Plates(usrId, plate) VALUES ("uId11", "MO-953-VF");
INSERT INTO Plates(usrId, plate) VALUES ("uId12", "DS-843-DZ");

INSERT INTO Parkings(id, parkingName, capacity, availableSpaces) VALUES ("pId1", "parking", 200, 200);
INSERT INTO Parkings(id, parkingName, capacity, availableSpaces) VALUES ("pId2", "parking", 200, 150);
INSERT INTO Parkings(id, parkingName, capacity, availableSpaces) VALUES ("pId3", "parking", 150, 75);

INSERT INTO ExceptionalOpen(pId, openTS, endTS) VALUES ("pId1", "1000-01-01 00:00:00", "1000-01-01 00:00:00");
INSERT INTO ExceptionalOpen(pId, openTS, endTS) VALUES ("pId1", "1000-01-01 00:00:00", "1000-01-01 00:00:00");
INSERT INTO ExceptionalOpen(pId, openTS, endTS) VALUES ("pId2", "1000-01-01 00:00:00", "1000-01-01 00:00:00");
INSERT INTO ExceptionalOpen(pId, openTS, endTS) VALUES ("pId3", "1000-01-01 00:00:00", "1000-01-01 00:00:00");

INSERT INTO Bookings(usrId, plate, present, startTS, endTS) VALUES ("4ed7c5a3a00cb6ab81fb205519ee91d0222dc6f4a3cd0d8a192c5c5901a4ed3a", "AA-123-AA", false, "2022-01-05 10:20:00", "2022-01-05 11:30:00");
INSERT INTO Bookings(usrId, plate, present, startTS, endTS) VALUES ("4ed7c5a3a00cb6ab81fb205519ee91d0222dc6f4a3cd0d8a192c5c5901a4ed3a", "AA-123-AA", false, "2022-01-08 17:30:00", "2022-01-09 20:00:00");
INSERT INTO Bookings(usrId, plate, present, startTS, endTS) VALUES ("4ed7c5a3a00cb6ab81fb205519ee91d0222dc6f4a3cd0d8a192c5c5901a4ed3a", "AA-123-AA", false, "2022-01-15 08:00:00", "2022-01-15 17:00:00");
INSERT INTO Bookings(usrId, plate, present, startTS, endTS) VALUES ("4ed7c5a3a00cb6ab81fb205519ee91d0222dc6f4a3cd0d8a192c5c5901a4ed3a", "1234 AA 00", false, "2022-04-06 10:00:00", "2022-04-06 18:00:00");
INSERT INTO Bookings(usrId, plate, present, startTS, endTS) VALUES ("4ed7c5a3a00cb6ab81fb205519ee91d0222dc6f4a3cd0d8a192c5c5901a4ed3a", "1234 AA 00", false, "2022-08-23 10:00:00", "2022-08-23 12:08:00");
INSERT INTO Bookings(usrId, plate, present, startTS, endTS) VALUES ("4ed7c5a3a00cb6ab81fb205519ee91d0222dc6f4a3cd0d8a192c5c5901a4ed3a", "1234 AA 00", false, "2022-09-12 10:35:00", "2022-09-12 11:00:00");
INSERT INTO Bookings(usrId, plate, present, startTS, endTS) VALUES ("4ed7c5a3a00cb6ab81fb205519ee91d0222dc6f4a3cd0d8a192c5c5901a4ed3a", "AA-123-AA", false, "2022-10-18 12:00:00", "2022-10-18 19:40:00");
INSERT INTO Bookings(usrId, plate, present, startTS, endTS) VALUES ("4ed7c5a3a00cb6ab81fb205519ee91d0222dc6f4a3cd0d8a192c5c5901a4ed3a", "AA-123-AA", false, "2022-12-10 20:05:00", "2022-12-10 23:40:00");
INSERT INTO Bookings(usrId, plate, present, startTS, endTS) VALUES ("4ed7c5a3a00cb6ab81fb205519ee91d0222dc6f4a3cd0d8a192c5c5901a4ed3a", "AA-123-AA", false, "2022-12-25 19:00:00", "2022-12-25 22:10:00");
INSERT INTO Bookings(usrId, plate, present, startTS, endTS) VALUES ("4ed7c5a3a00cb6ab81fb205519ee91d0222dc6f4a3cd0d8a192c5c5901a4ed3a", "1234 AA 00", false, "2022-01-02 08:20:00", "2022-01-05 12:10:00");
