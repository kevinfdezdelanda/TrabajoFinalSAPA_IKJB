DROP TABLE IF EXISTS user;

CREATE TABLE user (
 idUser INTEGER PRIMARY KEY,
 name VARCHAR(75) NOT NULL,
 photo LONGBLOB
);