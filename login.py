import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os

#caminho para rodar no PC do Caio outros usuarios favor comentar a linha abaixo
sys.path.append('C:/Users/Usuario/AppData/Roaming/Python/Python313/site-packages')
import bcrypt

# --- Configuração de Caminhos Relativos ---
# Pega o diretório do script atual (login.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Cria os caminhos completos para os outros scripts
CADASTRO_SCRIPT_PATH = os.path.join(BASE_DIR, 'cadastro.py')
TELA_PROFESSOR_SCRIPT_PATH = os.path.join(BASE_DIR, 'tela_professor.py')
TELA_ALUNO_SCRIPT_PATH = os.path.join(BASE_DIR, 'tela_aluno.py')
TELA_SECRETARIA_SCRIPT_PATH = os.path.join(BASE_DIR, 'tela_secretaria.py')

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
                    janela.destroy() # Fecha a janela de login
                    if tipo_usuario == 'professor':
                        abrir_tela_professor(id)
                    elif tipo_usuario == 'aluno':
                        abrir_tela_aluno(id)
                    elif tipo_usuario == 'secretaria':
                        abrir_tela_secretaria(id)
                else:
                    messagebox.showerror("Erro de Login", "Matrícula ou senha incorreta.")
            else:
                messagebox.showerror("Erro de Login", "Matrícula ou senha incorreta.")

        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro: {e}")
        finally:
            if 'conexao' in locals() and conexao:
                conexao.close()

def abrir_tela_professor(professor_id):
    # Esta função será responsável por chamar a tela do professor
    # Passamos o ID do professor para que a nova tela saiba quem está logado
    import subprocess
    subprocess.Popen([sys.executable, TELA_PROFESSOR_SCRIPT_PATH, str(professor_id)])

def abrir_tela_aluno(aluno_id):
    # Esta função será responsável por chamar a tela do aluno
    # Passamos o ID do aluno para que a nova tela saiba quem está logado
    import subprocess
    subprocess.Popen([sys.executable, TELA_ALUNO_SCRIPT_PATH, str(aluno_id)])

def abrir_tela_secretaria(secretaria_id):
    # Esta função será responsável por chamar a tela da secretaria
    # Passamos o ID para que a nova tela saiba quem está logado
    import subprocess
    subprocess.Popen([sys.executable, TELA_SECRETARIA_SCRIPT_PATH, str(secretaria_id)])

# --- Interface Gráfica ---


janela = tk.Tk()
janela.title("Sistema de Gerenciamento de Notas")
janela.geometry("365x300")
janela.configure(bg="#eef2f7")
janela.resizable(False, False)

frame = ttk.Frame(janela, padding=20)
frame.place(relx=0.5, rely=0.5, anchor="center")

ttk.Label(frame, text="Acesso ao Sistema", font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))
ttk.Label(frame,text="Matrícula: ").pack(anchor="w")
entrada_usuario = ttk.Entry(frame, width=30)
entrada_usuario.pack(pady=5)

ttk.Label(frame,text="Senha: ").pack(anchor="w")
entrada_senha = ttk.Entry(frame, width=30, show="*")
entrada_senha.pack(pady=5)

tk.Button(frame,text="Entrar",command=verificar_login).pack(pady=15)

entrada_usuario.focus()

janela.mainloop()
