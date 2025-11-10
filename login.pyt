import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
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
janela.geometry("400x300")

tk.Label(janela,text="Matrícula: ").pack(pady=5)
entrada_usuario = tk.Entry(janela)
entrada_usuario.pack(pady=5)

tk.Label(janela,text="Senha: ").pack(pady=5)
entrada_senha = tk.Entry(janela,show="*")
entrada_senha.pack(pady=5)


tk.Button(janela,text="Entrar",command=verificar_login).pack(pady=10)



janela.mainloop()
