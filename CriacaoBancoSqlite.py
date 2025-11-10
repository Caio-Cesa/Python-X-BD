import sqlite3
import sys
sys.path.append('C:/Users/Usuario/AppData/Roaming/Python/Python313/site-packages')
import bcrypt

# Criando um banco de dados (se ainda não existir) e conecta ao banco
conexao = sqlite3.connect("gerenciamento_notas.db")

#Obtendo um cursor, para enviar comandos ao banco de dados
cursor = conexao.cursor()

# Criando a tabela de pessoas
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpf TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('secretaria', 'professor', 'aluno'))
);
""")
#A tabela alunos vai se relacionar com usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS alunos (
    id INT PRIMARY KEY,
    curso VARCHAR(40),
    FOREIGN KEY (id) REFERENCES usuarios(id) ON DELETE CASCADE
);
""")

#-- A tabela professores vai se relacionar com usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS professores (
    id INT PRIMARY KEY,
    titulacao VARCHAR(20),
    area_atuacao VARCHAR(20),
    FOREIGN KEY (id) REFERENCES usuarios(id) ON DELETE CASCADE
);
""")

#tabela disciplinas
cursor.execute("""
CREATE TABLE IF NOT EXISTS disciplinas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    professor_id INT NOT NULL,
    FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE RESTRICT
);
""")

#tabela matriculas
cursor.execute("""
CREATE TABLE IF NOT EXISTS matriculas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id INT NOT NULL,
    disciplina_id INT NOT NULL,
    UNIQUE (aluno_id, disciplina_id),
    FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
    FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE
);
""")

#Tabela de notas
cursor.execute("""
CREATE TABLE IF NOT EXISTS notas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    disciplina_id INT NOT NULL,
    aluno_id INT NOT NULL,
    professor_id INT NOT NULL,
    nota_trabalho DECIMAL(4,2) NOT NULL CHECK (nota_trabalho >= 0 AND nota_trabalho <= 5),
    nota_prova DECIMAL(4,2) NOT NULL CHECK (nota_prova >= 0 AND nota_prova <= 5),
	matricula_id INT NOT NULL,
    
    FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
    FOREIGN KEY (matricula_id) REFERENCES matriculas(id) ON DELETE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE CASCADE,
    FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE
);
""")

# Criptografar a senha
#senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
'''
# Verificar se o usuário já existe antes de inserir
cursor.execute("SELECT id FROM usuarios WHERE cpf = ? OR email = ?", (cpf, email))
if cursor.fetchone() is None:
    # Inserir no banco se não existir
    cursor.execute("""
    INSERT INTO usuarios (cpf, nome, email, senha, tipo)
    VALUES (?, ?, ?, ?, ?)
    """, (cpf, nome, email, senha_hash, tipo))
    print("Usuário professor padrão inserido com sucesso.")
else:
    print("Usuário professor padrão já existe no banco de dados.")
'''
conexao.commit()
conexao.close()