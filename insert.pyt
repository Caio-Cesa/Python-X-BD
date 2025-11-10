import sqlite3

conexao = sqlite3.connect("gerenciamento_notas.db")
cursor = conexao.cursor()

try:
    cursor.execute("""
    INSERT INTO usuarios (id, cpf, nome, email, senha, tipo)
    VALUES (1, '11111111111', 'Otaviano Martins Monteiro', 
    'otaviano.monteiro@professores.newtonpaiva.br', 
    '$2b$12$YsUoita1vUcrI7qjEWkrm.8gFvGBKRIcs.31F597NCEWAGmbrzYR.', 
    'professor');
    """)
    
    cursor.execute("""
    INSERT INTO usuarios (id, cpf, nome, email, senha, tipo)
    VALUES (2, '22222222222', 'Ana Souza Lemos',
     'ana.lemos@alunos.newtonpaiva.br',
     '$2b$12$YsUoita1vUcrI7qjEWkrm.8gFvGBK31F597NCEWAGmbrzYRRIcs..', 
     'aluno');
    """)
    
    cursor.execute("""
    INSERT INTO usuarios (id, cpf, nome, email, senha, tipo)
    VALUES (3, '33333333333', 'Pedro Augusto Santos', 
    'pedro.santos@alunos.newtonpaiva.br', 
    '$2b$12$YsUoita1vUcrI7qjEWkrm.8gFvGBK31F597NCEWAGmbrzYRRIcs..', 
    'aluno');
    """)
    
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
