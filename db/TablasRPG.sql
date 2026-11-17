CREATE DATABASE rpg_manager CHARACTER SET utf8mb4;
USE rpg_manager;

SHOW TABLES;

CREATE TABLE Clase (
    id_clase INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
);

CREATE TABLE personaje (
    id_personaje INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    id_clase INT,
    nivel INT CHECK (nivel BETWEEN 1 AND 100),
    vida INT CHECK (vida >= 0),
    foreign key (id_clase) REFERENCES clase(id_clase)
);

insert into clase (nombre, descripcion) values ("Mago", "El erudito de las artes arcanas. Controla hechizos devastadores, pero su vida es frágil.");
insert into clase (nombre, descripcion) values ("Guerrero", "El tanque de primera línea. Su rol es aguantar los golpes más duros y repartir espadazos cuerpo a cuerpo.");
insert into clase (nombre, descripcion) values ("Arquero", "El cazador a distancia. Ágil, letal y con gran precisión para abatir enemigos antes de que se acerquen.");

insert into personaje (nombre, id_clase, nivel, vida) values ("Gaspar", 3, 1, 100);

Select * from clase;
Select * from personaje;
