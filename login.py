import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from database_manager import gerenciar_conexao_bd

#caminho para rodar no PC do Caio outros usuarios favor comentar a linha abaixo
sys.path.append('C:/Users/Usuario/AppData/Roaming/Python/Python313/site-packages')
import bcrypt

from PIL import Image, ImageTk

# --- Configuração de Caminhos Relativos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CADASTRO_SCRIPT_PATH = os.path.join(BASE_DIR, 'cadastro.py')
TELA_PROFESSOR_SCRIPT_PATH = os.path.join(BASE_DIR, 'tela_professor.py')
TELA_ALUNO_SCRIPT_PATH = os.path.join(BASE_DIR, 'tela_aluno.py')
TELA_SECRETARIA_SCRIPT_PATH = os.path.join(BASE_DIR, 'tela_secretaria.py')

def verificar_login():
    id = entrada_usuario.get()
    senha = entrada_senha.get()
   
    if not id and not senha:
        messagebox.showwarning("Erro Login: ","Matrícula e senha inválidos!")
    elif not id:
        messagebox.showwarning("Erro Login: ","Matrícula não informada")
    elif not senha:
        messagebox.showwarning("Erro Login: ","Senha inválida!")
    else:
        with gerenciar_conexao_bd() as cursor:
            if not cursor:
                return
            
            cursor.execute("SELECT senha, tipo FROM usuarios WHERE id = ?", (id,))
            usuario = cursor.fetchone()

        if usuario:
            senha_hash, tipo_usuario = usuario
            if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                janela.destroy()
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

def abrir_tela_professor(professor_id):
    import subprocess
    subprocess.Popen([sys.executable, TELA_PROFESSOR_SCRIPT_PATH, str(professor_id)])

def abrir_tela_aluno(aluno_id):
    import subprocess
    subprocess.Popen([sys.executable, TELA_ALUNO_SCRIPT_PATH, str(aluno_id)])

def abrir_tela_secretaria(secretaria_id):
    import subprocess
    subprocess.Popen([sys.executable, TELA_SECRETARIA_SCRIPT_PATH, str(secretaria_id)])

# --- Interface Gráfica ---

janela = tk.Tk()
janela.title("Sistema de Gerenciamento de Notas")
janela.geometry("450x500")
janela.configure(bg="#eef2f7")
janela.resizable(False, False)

#  ÍCONE + CABEÇALHO COM FAIXA VINHO + BRASÃO 

icone_path = os.path.join(BASE_DIR, "Hogwarts.jpg")

if os.path.exists(icone_path):
    try:
        # Ícone da janela
        icon_img = ImageTk.PhotoImage(Image.open(icone_path).resize((32, 32)))
        janela.iconphoto(False, icon_img)
        janela._icon_ref = icon_img
    except Exception as e:
        print("Erro ao carregar ícone:", e)

# ------- Cabeçalho estilo Hogwarts -------
header = tk.Frame(janela, bg="#5e0f16", padx=15, pady=10)
header.pack(fill=tk.X)

if os.path.exists(icone_path):
    img_header = Image.open(icone_path).resize((60, 60))
    img_header = ImageTk.PhotoImage(img_header)
    lbl_img = tk.Label(header, image=img_header, bg="#5e0f16")
    lbl_img.image = img_header
    lbl_img.pack(side="right")

tk.Label(
    header,
    text="Sistema Acadêmico",
    font=("Segoe UI", 15, "bold"),
    bg="#5e0f16",
    fg="white"
).pack(anchor="w")

# ======================================================================

frame = ttk.Frame(janela, padding=20)
frame.place(relx=0.5, rely=0.60, anchor="center")

logo_path = os.path.join(BASE_DIR, "Hogwarts.jpg")

if os.path.exists(logo_path):
    img = Image.open(logo_path)
    img = img.resize((130, 130))
    logo = ImageTk.PhotoImage(img)

    logo_label = tk.Label(frame, image=logo, background="#eef2f7")
    logo_label.image = logo 
    logo_label.pack(pady=(0, 10))
else:
    print("Logo não encontrada:", logo_path)

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

