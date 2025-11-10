import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import bcrypt

def conectar():
    
    # Altera a conexão para um banco de dados sqlite3
    return sqlite3.connect('gerenciamento_notas.db')

def criar_tabela():
    # Cria a tabela de usuários se ela não existir
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                tipo TEXT NOT NULL
            )
        ''')
        conexao.commit()
        conexao.close()
    except sqlite3.Error as erro:
        messagebox.showerror("Erro ao criar tabela!", erro)

def limpar_campos():
    entrada_nome.delete(0,tk.END)
    
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'),bcrypt.gensalt())

    conexao = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        # Altera o estilo do parâmetro SQL de %s para ?
        sql = "INSERT INTO usuarios(nome, cpf, email, senha, tipo) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(sql,(nome,cpf,email,senha_hash,tipo))
        conexao.commit()

        messagebox.showinfo("Confirmado!","Cadastro feito com sucesso!")
        limpar_campos()
    # Trata exceção de integridade (CPF/email duplicado) de forma específica
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro!", "CPF ou E-mail já cadastrado.")
    except sqlite3.Error as erro:
        messagebox.showerror("Erro!",erro)
    finally:
        if conexao:
            conexao.close()

#Janela
janela = tk.Tk()
botao_cadastrar = tk.Button(janela,text="Cadastrar", command=cadastrar_usuario)
botao_cadastrar.pack(pady=20)

# Cria a tabela antes de iniciar a aplicação
#criar_tabela()

janela.mainloop()
