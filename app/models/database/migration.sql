CREATE TABLE rgpd (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userID VARCHAR(150),
    `check` TINYINT(1),
    date_heure DATETIME,
    ipAdress VARCHAR(255),
    FOREIGN KEY (userID) REFERENCES users(id)
);
