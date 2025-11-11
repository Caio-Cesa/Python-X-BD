import tkinter as tk
from tkinter import ttk
import sqlite3
import sys

def buscar_nome_professor(professor_id):
    """Busca o nome do professor no banco de dados usando o ID."""
    try:
        conexao = sqlite3.connect("gerenciamento_notas.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (professor_id,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else "Professor"
    except sqlite3.Error as e:
        print(f"Erro ao buscar nome do professor: {e}")
        return "Professor"
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()

# Pega o ID do professor passado como argumento da linha de comando
professor_id_logado = sys.argv[1] if len(sys.argv) > 1 else None

janela = tk.Tk()
janela.title("Painel do Professor")
janela.geometry("365x300")

nome_professor = buscar_nome_professor(professor_id_logado)

ttk.Label(janela, text=f"Bem-vindo(a), {nome_professor}!", font=("Segoe UI", 16)).pack(pady=20)

janela.mainloop()
