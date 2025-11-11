import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
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


janela = tk.Tk()
janela.title("Sistema de Gerenciamento de Notas")
janela.geometry("365x260")
janela.configure(bg="#eef2f7")
janela.resizable(False, False)

frame = ttk.Frame(janela, padding=20)
frame.place(relx=0.5, rely=0.5, anchor="center")

ttk.Label(frame, text="Acesso ao Sistema", font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))
ttk.Label(janela,text="Matrícula: ").pack(anchor="w")
entrada_usuario = ttk.Entry(frame, width=30)
entrada_usuario.pack(pady=5)

ttk.Label(frame,text="Senha: ").pack(anchor="w")
entrada_senha = ttk.Entry(frame, width=30, show="*")
entrada_senha.pack(pady=5)

tk.Button(janela,text="Entrar",command=verificar_login).pack(pady=15)

entrada_usuario.focus()
janela.mainloop()
