import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import sys
sys.path.append('C:/Users/Usuario/AppData/Roaming/Python/Python313/site-packages')
import bcrypt

def limpar_campos():
    entrada_nome.delete(0,tk.END)
    entrada_cpf.delete(0, tk.END)
    entrada_email.delete(0, tk.END)
    entrada_senha.delete(0, tk.END)
    combo_tipo.set('') # Limpa a seleção do combobox

def cadastrar_usuario():
    nome = entrada_nome.get()
    cpf = entrada_cpf.get()
    email = entrada_email.get()
    senha = entrada_senha.get()
    tipo = combo_tipo.get()

    # Validação simples dos campos
    if not all([nome, cpf, email, senha, tipo]):
        messagebox.showwarning("Campos Incompletos", "Por favor, preencha todos os campos.")
        return

    # Criptografa a senha
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conexao = sqlite3.connect('gerenciamento_notas.db')
    cursor = conexao.cursor()

    try:
        # Insere na tabela usuarios
        sql_usuario = "INSERT INTO usuarios(nome, cpf, email, senha, tipo) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(sql_usuario, (nome, cpf, email, senha_hash, tipo))
        
        # Pega o ID do último usuário inserido
        user_id = cursor.lastrowid

        # Insere na tabela específica (aluno ou professor)
        if tipo == 'aluno':
            # Você pode adicionar campos para curso aqui se desejar
            cursor.execute("INSERT INTO alunos(id, curso) VALUES (?, ?)", (user_id, 'Não definido'))
        elif tipo == 'professor':
            # Você pode adicionar campos para titulação/área aqui
            cursor.execute("INSERT INTO professores(id, titulacao, area_atuacao) VALUES (?, ?, ?)", (user_id, 'Não definido', 'Não definida'))

        conexao.commit()

        messagebox.showinfo("Confirmado!", f"Usuário '{nome}' cadastrado com sucesso com o ID: {user_id}")
        limpar_campos()

    except sqlite3.IntegrityError:
        messagebox.showerror("Erro!", "CPF ou E-mail já cadastrado.")
    except sqlite3.Error as erro:
        messagebox.showerror("Erro de Banco de Dados!", erro)
    finally:
        if conexao:
            conexao.close()

#Janela
janela = tk.Tk()
janela.title("Cadastro de Novo Usuário")
janela.geometry("350x350")

ttk.Label(janela, text="Nome Completo:").pack(pady=5)
entrada_nome = ttk.Entry(janela, width=40)
entrada_nome.pack()

ttk.Label(janela, text="CPF:").pack(pady=5)
entrada_cpf = ttk.Entry(janela, width=40)
entrada_cpf.pack()

ttk.Label(janela, text="E-mail:").pack(pady=5)
entrada_email = ttk.Entry(janela, width=40)
entrada_email.pack()

ttk.Label(janela, text="Senha:").pack(pady=5)
entrada_senha = ttk.Entry(janela, width=40, show="*")
entrada_senha.pack()

ttk.Label(janela, text="Tipo de Usuário:").pack(pady=5)
combo_tipo = ttk.Combobox(janela, values=['aluno', 'professor', 'secretaria'], state="readonly")
combo_tipo.pack()

botao_cadastrar = tk.Button(janela,text="Cadastrar", command=cadastrar_usuario)
botao_cadastrar.pack(pady=20)

janela.mainloop()
