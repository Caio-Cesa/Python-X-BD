import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from database_manager import gerenciar_conexao_bd
import subprocess

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

def verificar_login(event=None):
    """Verifica as credenciais do usuário e o direciona para a tela correspondente."""
    user_id_str = entrada_usuario.get()
    senha = entrada_senha.get()
   
    if not user_id_str or not senha:
        messagebox.showwarning("Campos Vazios", "Por favor, informe a matrícula e a senha.")
        return
    
    try:
        # O ID no banco é um inteiro
        user_id = int(user_id_str)
    except ValueError:
        messagebox.showerror("Erro de Login", "A matrícula deve ser um número.")
        return

    with gerenciar_conexao_bd() as cursor:
        if not cursor:
            return # A mensagem de erro já foi exibida pelo gerenciador de conexão
        cursor.execute("SELECT senha, tipo FROM usuarios WHERE id = ?", (user_id,))
        usuario = cursor.fetchone()

    if not usuario:
        messagebox.showerror("Erro de Login", "Matrícula ou senha incorreta.")
        return

    senha_hash, tipo_usuario = usuario
    
    if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
        janela.destroy() # Fecha a janela de login
        if tipo_usuario == 'professor':
            abrir_tela_professor(user_id)
        elif tipo_usuario == 'aluno':
            abrir_tela_aluno(user_id)
        elif tipo_usuario == 'secretaria':
            abrir_tela_secretaria(user_id)
    else:
        messagebox.showerror("Erro de Login", "Matrícula ou senha incorreta.")

def abrir_tela_professor(professor_id):
    subprocess.Popen([sys.executable, TELA_PROFESSOR_SCRIPT_PATH, str(professor_id)])

def abrir_tela_aluno(aluno_id):
    subprocess.Popen([sys.executable, TELA_ALUNO_SCRIPT_PATH, str(aluno_id)])

def abrir_tela_secretaria(secretaria_id):
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

btn_entrar = ttk.Button(frame, text="Entrar", command=verificar_login)
btn_entrar.pack(pady=15, ipady=4, ipadx=10)

# Foco inicial no campo de usuário
entrada_usuario.focus()

# Permite que o usuário pressione "Enter" para fazer login
janela.bind('<Return>', verificar_login)

janela.mainloop()
