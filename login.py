import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import sys
sys.path.append('C:/Users/Usuario/AppData/Roaming/Python/Python313/site-packages')
import bcrypt

def verificar_login ():
    id = entrada_usuario.get()
    senha = entrada_senha.get()
   
    if not id and not senha:
        messagebox.showwarning("Erro Login: ","Matrícula e senha inválidos!")
    elif not id:
        messagebox.showwarning("Erro Login: ","Matrícula não informada")
    elif not senha:
        messagebox.showwarning("Erro Login: ","Senha inválida!")
    else:
        try:
            # Conectar ao banco de dados
            conexao = sqlite3.connect("gerenciamento_notas.db")
            cursor = conexao.cursor()

            # Buscar usuário pelo ID (matrícula)
            cursor.execute("SELECT senha, tipo FROM usuarios WHERE id = ?", (id,))
            usuario = cursor.fetchone()

            if usuario:
                senha_hash = usuario[0]
                tipo_usuario = usuario[1]
                
                # Verificar se a senha fornecida corresponde à senha armazenada (hash)
                if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                    messagebox.showinfo("Login bem-sucedido", f"Bem-vindo! Login como {tipo_usuario} realizado com sucesso.")
                    # Aqui você pode adicionar a lógica para abrir a próxima janela da aplicação
                else:
                    messagebox.showerror("Erro de Login", "Matrícula ou senha incorreta.")
            else:
                messagebox.showerror("Erro de Login", "Matrícula ou senha incorreta.")

        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro: {e}")
        finally:
            if 'conexao' in locals() and conexao:
                conexao.close()


janela = tk.Tk()
janela.title("Sistema de Gerenciamento de Notas")
janela.geometry("400x300")

tk.Label(janela,text="Matrícula: ").pack(pady=5)
entrada_usuario = tk.Entry(janela)
entrada_usuario.pack(pady=5)

tk.Label(janela,text="Senha: ").pack(pady=5)
entrada_senha = tk.Entry(janela,show="*")
entrada_senha.pack(pady=5)


tk.Button(janela,text="Entrar",command=verificar_login).pack(pady=10)



janela.mainloop()
