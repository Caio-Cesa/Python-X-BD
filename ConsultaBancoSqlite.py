import sqlite3
conexao = sqlite3.connect("gerenciamento_notas.db")
cursor = conexao.cursor()

cursor.execute("""
select * from usuarios
""")

for linha in cursor.fetchall():
    print(linha)

conexao.close()
