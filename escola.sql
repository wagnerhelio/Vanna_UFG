-- habilita validação de chaves estrangeiras nesta sessão
PRAGMA foreign_keys = ON;

-- ======================
-- TABELAS BÁSICAS
-- ======================

-- Tabela de turmas (usa o número como chave primária "natural")
CREATE TABLE turma (
  numero INTEGER PRIMARY KEY CHECK (numero > 0)
);

-- Tabela de professores
CREATE TABLE professor (
  id    INTEGER PRIMARY KEY,           -- alias de ROWID
  nome  TEXT NOT NULL UNIQUE
);

-- Tabela de especializações
CREATE TABLE especializacao (
  id    INTEGER PRIMARY KEY,
  nome  TEXT NOT NULL UNIQUE
);

-- ======================
-- TABELAS DE RELAÇÃO (M:N)
-- ======================

-- Professor <-> Turma (um prof pode dar aula em várias turmas e vice-versa)
CREATE TABLE professor_turma (
  professor_id  INTEGER NOT NULL,
  turma_numero  INTEGER NOT NULL,
  PRIMARY KEY (professor_id, turma_numero),
  FOREIGN KEY (professor_id) REFERENCES professor(id) ON DELETE CASCADE,
  FOREIGN KEY (turma_numero) REFERENCES turma(numero)    ON DELETE CASCADE
);

-- Especialização <-> Turma (uma esp. pode existir em várias turmas e vice-versa)
CREATE TABLE especializacao_turma (
  especializacao_id INTEGER NOT NULL,
  turma_numero      INTEGER NOT NULL,
  PRIMARY KEY (especializacao_id, turma_numero),
  FOREIGN KEY (especializacao_id) REFERENCES especializacao(id) ON DELETE CASCADE,
  FOREIGN KEY (turma_numero)      REFERENCES turma(numero)      ON DELETE CASCADE
);

-- ======================
-- DADOS INICIAIS
-- ======================

-- Turmas
INSERT INTO turma (numero) VALUES (1), (2);

-- Professores
INSERT INTO professor (nome) VALUES ('Ronaldo'), ('Sandeco'), ('Otavio');

-- Vínculos Professor x Turma
-- (exemplos: ajuste como preferir)
-- Ronaldo -> Turma 1
INSERT INTO professor_turma VALUES (
  (SELECT id FROM professor WHERE nome='Ronaldo'), 1
);
-- Sandeco -> Turma 2
INSERT INTO professor_turma VALUES (
  (SELECT id FROM professor WHERE nome='Sandeco'), 2
);
-- Otavio -> Turmas 1 e 2
INSERT INTO professor_turma VALUES
  ((SELECT id FROM professor WHERE nome='Otavio'), 1),
  ((SELECT id FROM professor WHERE nome='Otavio'), 2);

-- Especialização
INSERT INTO especializacao (nome) VALUES ('Agentes Inteligentes');

-- Vínculos Especialização x Turma (Agentes Inteligentes -> turmas 1 e 2)
INSERT INTO especializacao_turma VALUES
  ((SELECT id FROM especializacao WHERE nome='Agentes Inteligentes'), 1),
  ((SELECT id FROM especializacao WHERE nome='Agentes Inteligentes'), 2);

-- ======================
-- CONSULTAS ÚTEIS (testes)
-- ======================

-- Professores por turma
-- SELECT t.numero, p.nome
-- FROM turma t
-- JOIN professor_turma pt ON pt.turma_numero = t.numero
-- JOIN professor p        ON p.id = pt.professor_id
-- ORDER BY t.numero, p.nome;

-- Turmas por professor
-- SELECT p.nome, t.numero
-- FROM professor p
-- JOIN professor_turma pt ON pt.professor_id = p.id
-- JOIN turma t            ON t.numero = pt.turma_numero
-- ORDER BY p.nome, t.numero;

-- Especializações por turma
-- SELECT t.numero, e.nome
-- FROM turma t
-- JOIN especializacao_turma et ON et.turma_numero = t.numero
-- JOIN especializacao e        ON e.id = et.especializacao_id
-- ORDER BY t.numero, e.nome;
