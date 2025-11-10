import sqlite3
conexao = sqlite3.connect("gerenciamento_notas.db")
cursor = conexao.cursor()

print("\n--- Verificando todos os dados inseridos ---")

tabelas = ['usuarios', 'professores', 'alunos', 'disciplinas', 'matriculas', 'notas']

for tabela in tabelas:
    print(f"\n--- Dados da tabela: {tabela} ---")
    cursor.execute(f"SELECT * FROM {tabela}")
    nomes_colunas = [description[0] for description in cursor.description]
    print(nomes_colunas)
    for linha in cursor.fetchall():
        print(linha)

conexao.close()
