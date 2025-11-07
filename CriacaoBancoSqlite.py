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

cpf = "111111111111"
nome = "Otaviano Martins Monteiro"
email = "otaviano.monteiro@professores.newtonpaiva.edu.br"
senha = "12345678"
tipo = "professor"

# Criptografar a senha
senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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

conexao.commit()
conexao.close()