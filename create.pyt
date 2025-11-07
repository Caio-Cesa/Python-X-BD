import sqlite3

conexao =sqlite3.connect("comercio.db")

cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE compras(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        produto TEXT NOT NULL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
)
""")

conexao.close()