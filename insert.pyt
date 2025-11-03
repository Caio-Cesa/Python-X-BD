
import sqlite3

conexao = sqlite3.connect("comercio.db")
cursor = conexao.cursor()

cursor.execute("INSERT INTO clientes (nome,cpf) VALUES (?,?)",
               ("Caio","11111111111"))

cliente_id = cursor.lastrowid
cursor.execute("INSERT INTO compras (cliente_id,produto) VALUES(?,?)",
               (cliente_id,"Impresora"))

cursor.execute("INSERT INTO clientes (nome,cpf) VALUES(?,?)",
               ("Warley","22222222222"))

cliente_id = cursor.lastrowid
cursor.execute("INSERT INTO compras(cliente_id,produto) VALUES(?,?)",
               (cliente_id,"Tinta"))

conexao.commit()
print("Todos os clientes: ")
cursor.execute("""SELECT * FROM clientes""")
for linha in cursor.fetchall():
    print(linha)

print("Todas as compras: ")
cursor.execute("""SELECT * FROM compras""")
for linha in cursor.fetchall():
    print(linha)
