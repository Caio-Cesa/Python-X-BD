import sqlite3
import sys
sys.path.append('C:/Users/Usuario/AppData/Roaming/Python/Python313/site-packages')
import bcrypt

conexao = sqlite3.connect("gerenciamento_notas.db")
cursor = conexao.cursor()

try:
    # Criptografar as senhas antes de inserir
    senha0_hash = bcrypt.hashpw('000'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    senha1_hash = bcrypt.hashpw('111'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    senha2_hash = bcrypt.hashpw('222'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    senha3_hash = bcrypt.hashpw('333'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute("""
    INSERT INTO usuarios (id, cpf, nome, email, senha, tipo)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (0, '0000', 'Administrador',
          'administrador@secretaria.newtonpaiva.br',
          senha0_hash,
          'secretaria'))
    cursor.execute("""
    INSERT INTO usuarios (id, cpf, nome, email, senha, tipo)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (1, '11111111111', 'Otaviano Martins Monteiro',
          'otaviano.monteiro@professores.newtonpaiva.br',
          senha1_hash,
          'professor'))
    
    cursor.execute("""
    INSERT INTO usuarios (id, cpf, nome, email, senha, tipo)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (2, '22222222222', 'Ana Souza Lemos',
          'ana.lemos@alunos.newtonpaiva.br',
          senha2_hash,
          'aluno'))
    
    cursor.execute("""
    INSERT INTO usuarios (id, cpf, nome, email, senha, tipo)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (3, '33333333333', 'Pedro Augusto Santos',
          'pedro.santos@alunos.newtonpaiva.br',
          senha3_hash,
          'aluno'))
    
    cursor.execute("""
    INSERT INTO professores (id, titulacao, area_atuacao)
    VALUES (1, 'Doutorado', 'Computação');
    """)
    
    cursor.execute("""
    INSERT INTO alunos (id, curso)
    VALUES (2, 'Sistemas de Informação'), (3, 'Ciência da Computação');
    """)
           
    cursor.execute("""
    INSERT INTO disciplinas (id, nome, professor_id)
    VALUES (1, 'Desenvolvimento Rápido de Aplicações em Python', 1);
    """)
    
    cursor.execute("""
    INSERT INTO matriculas (id, aluno_id, disciplina_id)
    VALUES (1, 2, 1), (2, 3, 1);
    """)
    
    cursor.execute("""
    INSERT INTO notas (disciplina_id, aluno_id, professor_id, nota_trabalho, nota_prova, matricula_id)
    VALUES (1, 2, 1, 4.5, 3.8, 1),  (1, 3, 1, 3.9, 4.7, 2);
    """)
    print("Dados inseridos com sucesso!")
except sqlite3.IntegrityError:
    print("Os dados de exemplo já existem no banco de dados.")

conexao.commit()
conexao.close()
