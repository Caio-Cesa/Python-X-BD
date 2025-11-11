import tkinter as tk
from tkinter import ttk
import sqlite3
import sys

def buscar_dados_aluno(aluno_id):
    """Busca o nome do aluno e suas notas no banco de dados."""
    try:
        conexao = sqlite3.connect("gerenciamento_notas.db")
        cursor = conexao.cursor()

        # Busca o nome do aluno
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (aluno_id,))
        nome_aluno = cursor.fetchone()[0]

        # Busca as notas do aluno, juntando com o nome da disciplina
        query_notas = """
        SELECT d.nome, n.nota_trabalho, n.nota_prova
        FROM notas n
        JOIN disciplinas d ON n.disciplina_id = d.id
        WHERE n.aluno_id = ?
        """
        cursor.execute(query_notas, (aluno_id,))
        notas = cursor.fetchall()

        return nome_aluno, notas

    except sqlite3.Error as e:
        print(f"Erro de banco de dados: {e}")
        return "Aluno", []
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()

# --- Interface Gráfica ---

# Pega o ID do aluno passado como argumento
aluno_id_logado = sys.argv[1] if len(sys.argv) > 1 else None

janela = tk.Tk()
janela.title("Painel do Aluno")
janela.geometry("365x300")

nome_aluno, notas_aluno = buscar_dados_aluno(aluno_id_logado)

ttk.Label(janela, text=f"Bem-vindo(a), {nome_aluno}!", font=("Segoe UI", 16)).pack(pady=20)
ttk.Label(janela, text="Suas Notas:", font=("Segoe UI", 12)).pack(pady=(0, 10))

# Criar a tabela (Treeview) para exibir as notas
colunas = ('disciplina', 'nota_trabalho', 'nota_prova', 'media_final')
tabela_notas = ttk.Treeview(janela, columns=colunas, show='headings')

tabela_notas.heading('disciplina', text='Disciplina')
tabela_notas.heading('nota_trabalho', text='Nota Trabalho')
tabela_notas.heading('nota_prova', text='Nota Prova')
tabela_notas.heading('media_final', text='Média Final')

for disciplina, nota_trabalho, nota_prova in notas_aluno:
    media = (nota_trabalho + nota_prova)
    tabela_notas.insert('', tk.END, values=(disciplina, nota_trabalho, nota_prova, f"{media:.2f}"))

tabela_notas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

janela.mainloop()
