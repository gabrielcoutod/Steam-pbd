DROP TABLE IF EXISTS Dlc;
DROP TABLE IF EXISTS Idioma ;
DROP TABLE IF EXISTS Categorizacao ;
DROP TABLE IF EXISTS Classificacao ;
DROP TABLE IF EXISTS Desenvolvedora ;
DROP TABLE IF EXISTS Distribuidora ;
DROP TABLE IF EXISTS Tags ;
DROP TABLE IF EXISTS Empresa ;
DROP TABLE IF EXISTS Tag ;
DROP TABLE IF EXISTS Genero ;
DROP TABLE IF EXISTS Categoria ;
DROP TABLE IF EXISTS Lingua ;
DROP TABLE IF EXISTS Jogo;
DROP TABLE IF EXISTS App;

CREATE TABLE App (
    id SERIAL NOT NULL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    preco DECIMAL(6,2) NOT NULL,
    data_lancamento DATE NOT NULL,
    analises_positivas INTEGER NOT NULL,
    analises_negativas INTEGER NOT NULL,
    windows_support BOOLEAN NOT NULL, 
    linux_support BOOLEAN NOT NULL, 
    mac_support BOOLEAN NOT NULL
);

CREATE TABLE Categoria (
    id SERIAL NOT NULL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE Categorizacao (
    fk_Categoria_id INTEGER NOT NULL,
    fk_App_id INTEGER NOT NULL,
    PRIMARY KEY(fk_Categoria_id, fk_App_id),
    FOREIGN KEY (fk_Categoria_id) REFERENCES Categoria (id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (fk_App_id) REFERENCES App (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Genero (
    id SERIAL NOT NULL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE Classificacao (
    fk_Genero_id INTEGER NOT NULL,
    fk_App_id INTEGER NOT NULL,
    PRIMARY KEY (fk_Genero_id, fk_App_id),
    FOREIGN KEY (fk_Genero_id) REFERENCES Genero (id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (fk_App_id) REFERENCES App (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Empresa (
    id SERIAL NOT NULL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL
);

CREATE TABLE Desenvolvedora (
    fk_Empresa_id INTEGER NOT NULL,
    fk_App_id INTEGER NOT NULL,
    PRIMARY KEY (fk_Empresa_id, fk_App_id),
    FOREIGN KEY (fk_Empresa_id) REFERENCES Empresa (id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (fk_App_id) REFERENCES App (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Distribuidora (
    fk_Empresa_id INTEGER NOT NULL,
    fk_App_id INTEGER NOT NULL,
    PRIMARY KEY (fk_Empresa_id, fk_App_id),
    FOREIGN KEY (fk_Empresa_id) REFERENCES Empresa (id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (fk_App_id) REFERENCES App (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Tag (
    id SERIAL NOT NULL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL
);

CREATE TABLE Tags (
    fk_Tag_id INTEGER NOT NULL,
    fk_App_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    PRIMARY KEY (fk_App_id, fk_Tag_id),
    FOREIGN KEY (fk_App_id) REFERENCES App (id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (fk_Tag_id) REFERENCES Tag (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Lingua (
    id SERIAL NOT NULL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL
);

CREATE TABLE Idioma (
    fk_Lingua_id INTEGER NOT NULL,
    fk_App_id INTEGER NOT NULL,
    PRIMARY KEY (fk_App_id, fk_Lingua_id),
    FOREIGN KEY (fk_App_id) REFERENCES App (id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (fk_Lingua_id) REFERENCES Lingua (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Jogo (
    id INTEGER PRIMARY KEY NOT NULL,
    FOREIGN KEY (id) REFERENCES App(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Dlc (
    id INTEGER NOT NULL PRIMARY KEY,
    fk_Jogo_id INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES App(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (fk_Jogo_id) REFERENCES Jogo(id) ON UPDATE CASCADE ON DELETE CASCADE
);