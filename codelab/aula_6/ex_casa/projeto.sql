CREATE TABLE Receita (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL
);

CREATE TABLE Tag (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE link_receita_tag (
    receita_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (receita_id, tag_id),
    FOREIGN KEY (receita_id) REFERENCES Receita(id),
    FOREIGN KEY (tag_id) REFERENCES Tag(id)
);
