# ------- Insertions -------

INSERT_USER = """INSERT INTO Users (id, firstName, lastName, mail, phoneNumber, usrType, entityId)
                VALUES (\"{id}\", \"{firstname}\", \"{lastname}\", \"{mail}\", "{phone}", \"{usrType}\", \"{entityId}\")"""

INSERT_CONFIRMED_USER = """INSERT INTO Users (id, firstName, lastName, mail, phoneNumber, usrType, entityId, approved)
                VALUES (\"{id}\", \"{firstname}\", \"{lastname}\", \"{mail}\", "{phone}", \"{usrType}\", \"{entityId}\", 1)"""

INSERT_ADMIN_USER = """INSERT INTO Users (id, firstName, lastName, mail, phoneNumber, usrType, hierarchicalLevel, entityId, approved)
                VALUES (\"{id}\", \"{firstname}\", \"{lastname}\", \"{mail}\", "{phone}", \"{usrType}\", 1, \"{entityId}\", 1)"""

INSERT_SUPER_ADMIN_USER = """INSERT INTO Users (id, firstName, lastName, mail, phoneNumber, usrType, hierarchicalLevel, entityId, approved)
                VALUES (\"{id}\", \"{firstname}\", \"{lastname}\", \"{mail}\", "{phone}", \"{usrType}\", 2, \"{entityId}\", 1)"""

INSERT_USER_CREDENTIALS = """INSERT INTO UsersCredentials VALUES (\"{id}\", \"{login}\", \"{pswdHash}\", \"{salt}\")"""

INSERT_USER_TOKEN = """INSERT INTO AuthTokens VALUES (\"{token}\", \"{usrId}\")"""

INSERT_USER_PLATE = """INSERT INTO Plates VALUES (\"{usrId}\", \"{plate}\")"""

INSERT_BOOKING = """INSERT INTO Bookings (uuid, usrId, plate, startTS, endTS, repeatInterval, ending, associedCriticity) VALUES ("{uuid}", \"{usrId}\", \"{plate}\", \"{startTS}\", \"{endTS}\", \"{interval}\", \"{ending}\", "{criticity}")"""

INSERT_CUSTOM_BOOKING = """INSERT INTO Bookings (uuid, usrId, plate, startTS, endTS, repeatInterval, customInterval, customAmount, onMonday, onTuesday, onWednesday, onThursday, onFriday, onSaturday, onSunday, ending, associedCriticity) VALUES ("{uuid}", \"{usrId}\", \"{plate}\", \"{startTS}\", \"{endTS}\", \"custom\", \"{customInterval}\", {customAmount}, \"{onMonday}\", \"{onTuesday}\", \"{onWednesday}\", \"{onThursday}\", \"{onFriday}\", \"{onSaturday}\", \"{onSunday}\", \"{ending}\", "{criticity}")"""

INSERT_API_PERIOD = """INSERT INTO BookingsApiPeriods (id, bookingId) VALUES ("{id}", "{bookingId}")"""

INSERT_ENTITY = """INSERT INTO Entity (id, eName, nbPlacesAllocated, nbFreePlaces) VALUES ("{id}", "{eName}", "{nbPlacesAllocated}", "{nbFreePlaces}")"""

#INSERT_PROFILE = """INSERT INTO Profiles (profileName, criticity) VALUES ("{pName}", "{pCriticity}")"""

INSERT_PROFILE = """INSERT INTO Profiles (profileName, criticity, entityId) VALUES ("{pName}", "{pCriticity}", "{entityId}")"""

INSERT_RESET_PSWD = """INSERT INTO ResetPswd (usrToken, usrId) VALUES ("{usrToken}", "{usrId}")"""

INSERT_READING_PLATE = """INSERT INTO FalseReading (theoricalPlate, readingPlate, trueLetter, falseLetter) VALUES ("{theoricalPlate}", "{readingPlate}", "{trueLetter}", "{falseLetter}")"""

# ------- Deletions -------

DELETE_USER_TOKEN_BY_TOKEN = """DELETE FROM AuthTokens WHERE token=\"{token}\""""

DELETE_USER_TOKEN_BY_ID = """DELETE FROM AuthTokens WHERE id=\"{id}\""""

DELETE_USER_CREDENTIALS_BY_ID = """DELETE FROM UsersCredentials WHERE id="{id}" """
DELETE_USER_BY_ID = """DELETE FROM Users WHERE id="{id}" """

DELETE_PLATE = """DELETE FROM Plates WHERE plate=\"{plate}\" AND usrId="{usrId}" """

DELETE_USER_PLATES = """DELETE FROM Plates WHERE usrId="{id}" """

DELETE_PROFILE = """DELETE FROM Profiles WHERE id="{profileId}" AND profileName!="Aucun profil" """

DELETE_BOOKING = """DELETE FROM Bookings WHERE uuid=\"{bookingId}\" and usrId=\"{usrId}\"""" # Probleme de sécurité si usrId pas inclus

DELETE_BOOKING_API = """DELETE FROM BookingsApiPeriods WHERE bookingId="{bookingId}" """

DELETE_BOOKING_PERIODS = """DELETE FROM BookingsApiPeriods WHERE bookingId="{bId}" """

DELETE_USER_PASSWORD_RESET_REQUEST = """DELETE FROM ResetPswd WHERE usrId="{usrId}" """

DELETE_ENTITY = """DELETE FROM Entity WHERE id="{id}" """

# ------- Fetchs -------

# Fetch entity
GET_ALL_ENTITIES = """SELECT id, eName, nbPlacesAllocated, nbFreePlaces FROM Entity"""

GET_ALL_ENTITIES_IDS_AND_NAMES = """SELECT id, eName FROM Entity"""

GET_ALL_ENTITIES_IDS = """SELECT id FROM Entity""" 

# Fetch profiles
GET_PROFILES = """SELECT * FROM Profiles"""

GET_PROFILES_NAMES = """SELECT profileName FROM Profiles"""

GET_PROFILES_BY_ENTITY = """SELECT id, profileName, criticity FROM Profiles WHERE entityId="{entityId}" """

GET_PROFILES_NAMES_BY_ENTITY = """SELECT profileName FROM Profiles WHERE entityId="{entityId}" """

GET_PROFILE_NAME_BY_ID = """SELECT profileName from Profiles WHERE id=\"{id}\""""

GET_PROFILE_ID_BY_NAME = """SELECT id from Profiles WHERE profileName=\"{name}\""""

# Update profiles
UPDATE_PROFILE_BY_ID = """UPDATE Profiles SET profileName="{newName}", criticity="{newCriticity}" WHERE id="{pId}" """

# Update errors
UPDATE_ERRORS = """UPDATE Errors SET value = value + 1 WHERE id="{id}" """

# Fetch Users
GET_ALL_USERS_INFOS = """SELECT * FROM Users"""

GET_USERS_AND_ADMIN = """SELECT U.id, U.firstName, U.lastName, U.mail, U.phoneNumber, U.usrType, U.approved, U.hierarchicalLevel, E.id, E.eName FROM Users U, Entity E WHERE U.hierarchicalLevel < 2 AND E.id=U.entityId"""

GET_USERS_AND_ADMIN_COUNT = """SELECT COUNT(*) FROM Users WHERE hierarchicalLevel < 2"""

GET_USER_INFO_BY_ID = """SELECT firstname, lastname, mail, phoneNumber, usrType, approved, hierarchicalLevel, entityId FROM Users WHERE id=\"{id}\""""

GET_USER_INFO_BY_MAIL = """SELECT id, firstname, lastname, mail, usrType, entityId FROM Users WHERE mail=\"{mail}\""""

GET_USER_CREDENTIALS = """SELECT pswdHash, salt FROM UsersCredentials WHERE usrLogin=\"{login}\""""

GET_USER_ID_BY_LOGIN = """SELECT id FROM UsersCredentials WHERE usrLogin=\"{login}\""""

GET_USER_ID_FROM_TOKEN = """SELECT id FROM AuthTokens WHERE token=\"{token}\""""

GET_USER_HIERARCHICAL_LEVEL = """SELECT hierarchicalLevel FROM Users WHERE id="{usrId}" """

GET_USER_MAIL_BY_ID = """SELECT mail FROM Users WHERE id="{usrId}" """

GET_USER_APPROBATION = """SELECT approved FROM Users WHERE id="{usrId}" """

GET_USERS_COUNT = """SELECT COUNT(*) FROM Users"""

GET_USER_PLATES = """SELECT plate FROM Plates WHERE usrId=\"{usrId}\""""

GET_USER_PLATES_COUNT = """SELECT COUNT(*) FROM Plates WHERE usrId="{usrId}" """

GET_USER_PROFILE = """SELECT usrType FROM Users WHERE id="{id}" """

GET_USERS_FROM_ENTITY = """SELECT U.id, U.firstName, U.lastName, U.mail, U.phoneNumber, U.usrType, U.approved, U.hierarchicalLevel, E.id, E.eName FROM Users U, Entity E WHERE U.entityId="{entityId}" AND U.hierarchicalLevel=0 AND E.id=U.entityId"""

GET_PLATES_FROM_ENTITY = """SELECT P.plate FROM Plates P, Users U WHERE U.entityId="{entityId}" AND P.usrId=U.id"""

GET_ENTITY_ID_FROM_USER = """SELECT entityId FROM Users WHERE id="{usrId}" """

GET_USERS_COUNT_BY_ENTITY = """SELECT COUNT(*) FROM Users WHERE entityId="{entityId}" AND hierarchicalLevel=0 """

GET_USERS_TO_CONFIRM_COUNT_BY_ENTITY_COUNT = """SELECT COUNT(*) FROM Users WHERE entityId="{entityId}" AND hierarchicalLevel=0 AND approved=0"""

GET_USERS_TO_CONFIRM_COUNT = """SELECT COUNT(*) FROM Users WHERE approved=0"""

CHECK_LOGIN_EXISTS = """SELECT EXISTS(SELECT * FROM UsersCredentials WHERE usrLogin="{login}")"""

GET_USERNAME_BY_ID = """SELECT usrLogin FROM UsersCredentials WHERE id="{id}" """

# RGPD
GET_USER_RGPD = """SELECT * FROM rgpd WHERE userID="{usrId}" """

INSERT_USER_RGPD_TRUE_CONSENT = """INSERT INTO rgpd (userID, `check`, date_heure) VALUES ("{userID}", "{check}", "{date}")"""

DELETE_USER_RGPD_BY_ID = """DELETE FROM rgpd WHERE userID="{usrId}" """

# Update User
UPDATE_USER_WITH_TEL_BY_ID = """UPDATE Users SET lastname="{lname}", firstname="{fname}", mail="{mail}", phoneNumber="{tel}", entityId="{entityId}", usrType="{pId}" WHERE id="{usrId}" """

UPDATE_USER_WITHOUT_TEL_BY_ID = """UPDATE Users SET lastname="{lname}", firstname="{fname}", mail="{mail}", entityId="{entityId}", usrType="{pId}" WHERE id="{usrId}" """

UPDATE_USERS_PROFILE = """UPDATE Users SET usrType="{newProfileId}" WHERE usrType="{oldProfileId}" """

UPDATE_USER_APPROBATION = """UPDATE Users SET approved={approbation} WHERE id="{usrId}" """

# Update entity
UPDATE_ENTITY_SPOTS = """UPDATE Entity SET nbPlacesAllocated={spots} WHERE id="{id}" """

GET_ENTITY_SPOTS = """SELECT nbPlacesAllocated FROM Entity WHERE id="{entityId}" """

GET_ENTITY_FREE_SPOTS = """SELECT COUNT(*) FROM Bookings B WHERE B.usrId IN (SELECT id FROM Users WHERE entityId="{entityId}" AND hierarchicalLevel < 2)"""

# Fetch Bookings
GET_BOOKING_FROM_ID = """SELECT * FROM Bookings WHERE uuid="{uuid}" AND usrId="{usrId}" """

GET_BOOKING_PERIOD = """SELECT id FROM BookingsApiPeriods WHERE bookingId="{bId}" """

GET_USER_BOOKINGS = """SELECT * FROM Bookings WHERE usrId=\"{usrId}\""""

GET_BOOKINGS_COUNT = """SELECT COUNT(*) FROM Bookings"""

GET_CURRENT_BOOKINGS_COUNT = """SELECT COUNT(*) FROM Bookings WHERE startTS <= NOW() AND ending >= NOW()"""

GET_BOOKING_FROM_ENTITY_ID = """SELECT B.*, U.id, U.firstName, U.lastname, U.mail, U.phoneNumber, U.usrType FROM Bookings B, Users U WHERE U.hierarchicalLevel<2 AND B.usrId IN (SELECT id FROM Users WHERE entityId="{entityId}") AND U.id=B.usrId ORDER BY B.startTS, B.plate"""

GET_CURRENT_BOOKING_FROM_ENTITY_ID = """SELECT B.*, U.id, U.firstName, U.lastname, U.mail, U.phoneNumber, U.usrType FROM Bookings B, Users U WHERE U.hierarchicalLevel<2 AND B.usrId IN (SELECT id FROM Users WHERE entityId="{entityId}") AND U.id=B.usrId AND B.startTS <= NOW() AND B.ending >= NOW() ORDER BY B.startTS, B.plate"""

GET_BOOKING_FROM_ENTITY_ID_OVERLAPPING_DATETIME = """SELECT B.*, U.id, U.firstName, U.lastname, U.mail, U.phoneNumber, U.usrType FROM Bookings B, Users U WHERE ((B.startTS<"{bookingStart}" AND "{bookingStart}"<B.endTS) OR (B.startTS<"{bookingEnd}" AND "{bookingEnd}"<B.endTS) OR ("{bookingStart}"<B.startTS AND "{bookingEnd}">B.endTS)) AND B.usrId IN (SELECT id FROM Users WHERE entityId="{entityId}") AND U.id=B.usrId ORDER BY B.startTS, B.plate"""

GET_BOOKING_COUNT_FROM_ENTITY_OVERLAPPING_DATETIME = """SELECT COUNT(*) FROM Bookings B WHERE ((B.startTS<="{bookingStart}" AND "{bookingStart}"<=B.endTS) OR (B.startTS<="{bookingEnd}" AND "{bookingEnd}"<=B.endTS) OR ("{bookingStart}"<=B.startTS AND "{bookingEnd}">=B.endTS)) AND B.usrId IN (SELECT id FROM Users WHERE entityId="{entityId}")"""

GET_BOOKINGS_COUNT_FROM_ENTITY_ID = """SELECT COUNT(*) FROM Bookings WHERE usrId IN (SELECT id FROM Users WHERE entityId="{entityId}")"""

GET_BOOKINGS_STARTS_IN_INTERVAL = """SELECT * FROM Bookings WHERE startTS >= "{startInterval}" AND startTS <= "{endInterval}" AND plate="{plate}" """

GET_BOOKINGS_ENDS_IN_INTERVAL = """SELECT * FROM Bookings WHERE endTS >= "{startInterval}" AND endTS <= "{endInterval}" AND plate="{plate}" """

GET_BOOKINGS_ENDS_IN_INTERVAL_WITHOUT_PLATE = """SELECT * FROM Bookings WHERE endTS >= "{startInterval}" AND endTS <= "{endInterval}" """

GET_USERS_BOOKINGS_COUNT_FROM_ENTITY_ID = """SELECT COUNT(*) FROM Bookings WHERE usrId IN (SELECT id FROM Users WHERE entityId="{entityId}" AND hierarchicalLevel < 2)"""

GET_CURRENT_USERS_BOOKINGS_COUNT_FROM_ENTITY_ID = """SELECT COUNT(*) FROM Bookings WHERE usrId IN (SELECT id FROM Users WHERE entityId="{entityId}" AND hierarchicalLevel < 2) AND startTS <= NOW() AND ending >= NOW()"""

GET_BOOKING_FOR_DATETIME_AND_PLATE = """SELECT * FROM Bookings WHERE plate="{plate}" AND startTS<="{datetime}" AND endTS>="{datetime}" """

GET_ALL_BOOKINGS = """SELECT B.*, U.id, U.firstName, U.lastname, U.mail, U.phoneNumber, U.usrType FROM Bookings B, Users U WHERE U.id=B.usrId ORDER BY B.startTS, B.plate"""

GET_ALL_CURRENT_BOOKINGS = """SELECT B.*, U.id, U.firstName, U.lastname, U.mail, U.phoneNumber, U.usrType FROM Bookings B, Users U WHERE U.id=B.usrId AND B.startTS <= NOW() AND B.ending >= NOW() ORDER BY B.startTS, B.plate"""

# Fetch Parkings
GET_ALL_PARKINGS = """SELECT * FROM Parkings"""

GET_PARKING = """SELECT * FROM Parkings WHERE id=\"{id}\""""

GET_USER_PARKING_ENTRY = """SELECT * FROM Parking WHERE usrId=\"{usrId}\""""

# Fetch Exceptional opens
GET_EXCEPTIONAL_OPEN = """SELECT * FROM ExceptionalOpen WHERE uuid=\"{uuid}\""""

GET_PARKING_EXCEPTIONAL_OPEN = """SELECT * FROM ExceptionalOpen WHERE pId=\"{pId}\""""

# Fetch admin data
GET_UNAPPROVED_USERS_BY_ENTITY = """SELECT U.id, U.firstname, U.lastname, P.profileName FROM Users U, Profiles P WHERE hierarchicalLevel=0 AND approved=0 AND entityId="{entityId}" AND P.id=U.usrType"""

# Update entries
CONFIRM_USER = """UPDATE Users SET approved=1 WHERE id="{usrId}" """

GET_PASSWORD_RESET_REQUEST = """SELECT * FROM ResetPswd WHERE usrToken="{token}" """

UPDATE_PASSWORD_CREDENTIALS = """UPDATE UsersCredentials SET pswdhash="{pswdHash}", salt="{salt}" WHERE id="{usrId}" """

EXISTS_PROFILE_BY_ID_AND_ENTITY = """SELECT EXISTS(SELECT * FROM Profiles WHERE id="{profileId}" AND entityId="{entityId}") """

GET_PROFILE_BY_ID = """SELECT * FROM Profiles WHERE id="{id}" """

GET_PROFILE_CRITICITY = """SELECT criticity FROM Profiles WHERE id="{profileId}" """

GET_ENTITY_FROM_PROFILE = """SELECT entityId FROM Profiles WHERE id="{id}" """

GET_PROFILE_TIME_SLOTS = """SELECT * FROM CriticityTables WHERE profileId="{profileId}" """

GET_TIME_SLOT_BY_ID = """SELECT * FROM CriticityTables WHERE id="{id}" """

INSERT_PROFILE_TIME_SLOTS = """INSERT INTO CriticityTables (profileId, startTS, endTS, criticityLevel) VALUES ("{profileId}", "{start}", "{end}", {level}) """

DELETE_TIME_SLOT = """DELETE FROM CriticityTables WHERE id="{id}" """

GET_TIME_SLOTS_LEVELS_FOR_DATETIME = """SELECT criticityLevel FROM CriticityTables WHERE profileId="{profileId}" AND ((startTS<="{start}" AND "{start}"<=endTS) OR (startTS<="{end}" AND "{end}"<=endTS) OR ("{start}"<=startTS AND "{end}">=endTS))"""

IS_MAIL_EXISTS = """SELECT EXISTS(SELECT mail FROM Users WHERE mail="{mail}")"""

UPDATE_USER_MAIL = """UPDATE Users SET mail="{mail}", approved=0 WHERE id="{usrId}" """

""" FLOW ALERTS QUERIES """
GET_RAW_ALERTS = """SELECT * FROM FlowAlerts"""

GET_ALERTS_BY_PLATE = """SELECT * FROM Alerts WHERE plate="{plate}" """

GET_FULL_INFO_ALERTS = """SELECT A.id, A.earlier, A.later, U.firstName, U.lastName, B.plate, B.startTS, B.endTS FROM FlowAlerts A, Bookings B, Users U WHERE A.bookingId=B.uuid AND U.id=B.usrId"""

GET_ALERT_INFO = """SELECT U.firstName, U.lastName, B.plate, B.startTS, B.endTS FROM FlowAlerts A, Bookings B, Users U WHERE B.uuid="{bookingId}" AND U.id=B.usrId"""

INSERT_ALERT_WITHOUT_BOOKING = """INSERT INTO FlowAlerts (id, earlier, later, plate) VALUES ("{id}", "{earlier}", "{later}", "{plate}")"""

INSERT_ALERT_WITH_BOOKING = """INSERT INTO FlowAlerts (id, earlier, later, plate, firstname, lastname, start, end) VALUES ("{id}", "{earlier}", "{later}", "{plate}", "{firstName}", "{lastName}", "{start}", "{end}")"""

DELETE_ALERTS_BY_PLATE = """DELETE FROM FlowAlerts WHERE plate="{plate}" """

""" REFRESH BOOKINGS QUERIES """
GET_USER_START_END_BOOKING = """SELECT usrId, startTS, endTS FROM Bookings WHERE uuid="{bid}" """

GET_BOOKING_IDS_DAILY_REFRESH = """SELECT uuid FROM Bookings WHERE repeatInterval="daily" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""

REFRESH_DAILY_BOOKINGS_START = """UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 24 hour) WHERE repeatInterval="daily" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""
REFRESH_DAILY_BOOKINGS_END = """UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 24 hour) WHERE repeatInterval="daily" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""

GET_BOOKING_IDS_WEEKLY_REFRESH = """SELECT uuid FROM Bookings WHERE repeatInterval="weekly" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""

REFRESH_WEEKLY_BOOKINGS_START = """UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 7 day) WHERE repeatInterval="weekly" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""
REFRESH_WEEKLY_BOOKINGS_END = """UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 7 day) WHERE repeatInterval="weekly" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""

GET_BOOKING_IDS_MONTHLY_REFRESH = """SELECT uuid FROM Bookings WHERE repeatInterval="monthly" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""

REFRESH_MONTHLY_BOOKINGS_START = """UPDATE Bookings SET startTS=date_add(startTS, INTERVAL 1 month) WHERE repeatInterval="monthly" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""
REFRESH_MONTHLY_BOOKINGS_END = """UPDATE Bookings SET endTS=date_add(endTS, INTERVAL 1 month) WHERE repeatInterval="monthly" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""

GET_BOOKING_IDS_CUSTOM_DAILY_REFRESH = """SELECT uuid FROM Bookings WHERE repeatInterval="custom" AND customInterval="day" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""

REFRESH_CUSTOM_DAILY_BOOKINGS_START = """UPDATE Bookings SET startTS=date_add(startTS, INTERVAL customAmount day) WHERE repeatInterval="custom" AND customInterval="day" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""
REFRESH_CUSTOM_DAILY_BOOKINGS_END = """UPDATE Bookings SET endTS=date_add(endTS, INTERVAL customAmount day) WHERE repeatInterval="custom" AND customInterval="day" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""

GET_BOOKING_IDS_CUSTOM_MONTHLY_REFRESH = """SELECT uuid FROM Bookings WHERE repeatInterval="custom" AND customInterval="month" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""

REFRESH_CUSTOM_MONTHLY_BOOKINGS_START = """UPDATE Bookings SET startTS=date_add(startTS, INTERVAL customAmount month) WHERE repeatInterval="custom" AND customInterval="month" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""
REFRESH_CUSTOM_MONTHLY_BOOKINGS_END = """UPDATE Bookings SET endTS=date_add(endTS, INTERVAL customAmount month) WHERE repeatInterval="custom" AND customInterval="month" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""

GET_BOOKING_IDS_CUSTOM_WEEKLY_REFRESH = """SELECT uuid, customAmount, onMonday, onTuesday, onWednesday, onThursday, onFriday, onSaturday, onSunday FROM Bookings WHERE repeatInterval="custom" AND customInterval="week" AND endTS <= CURRENT_TIMESTAMP AND ending > CURRENT_TIMESTAMP"""

REFRESH_CUSTOM_WEEKLY_BOOKINGS_START = """UPDATE Bookings SET startTS=date_add(startTS, INTERVAL {dayInterval} DAY) WHERE repeatInterval="custom" AND customInterval="week" AND uuid="{bid}" """
REFRESH_CUSTOM_WEEKLY_BOOKINGS_END = """UPDATE Bookings SET endTS=date_add(endTS, INTERVAL {dayInterval} DAY) WHERE repeatInterval="custom" AND customInterval="week" AND uuid="{bid}" """

""" QUERIES FOR FLOW DATABASE """
GET_FLOW_IN_IN_INTERVAL = """SELECT plate, record FROM FlowIn WHERE record>="{startTS}" AND record<="{endTS}" """

GET_FLOW_OUT_IN_INTERVAL = """SELECT plate, record FROM FlowOut WHERE record>="{startTS}" AND record<="{endTS}" """

GET_PLATE_FLOW_IN_IN_INTERVAL = """SELECT plate, record FROM FlowIn WHERE record>="{startTS}" AND record<="{endTS}" AND plate="{plate}" """

GET_PLATE_FLOW_OUT_IN_INTERVAL = """SELECT plate, record FROM FlowOut WHERE record>="{startTS}" AND record<="{endTS}" AND plate="{plate}" """

GET_PLATE_IN_DATETIMES_RECORDS = """SELECT plate, record FROM FlowIn WHERE plate="{plate}" """

GET_PLATE_OUT_DATETIMES_RECORDS = """SELECT plate, record FROM FlowOut WHERE plate="{plate}" """

GET_PLATE_IN_RECORDS = """SELECT plate FROM FlowIn WHERE record>="{startTS}" AND record<="{endTS}" """

GET_PLATE_IN_RECORDS_ERRORS = """SELECT plate FROM FailedPlate WHERE record>="{startTS}" AND record<="{endTS}" """