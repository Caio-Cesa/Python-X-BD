import tkinter as tk
from tkinter import ttk
import sys
from database_manager import gerenciar_conexao_bd

def buscar_dados_aluno(aluno_id):
    """Busca os dados completos do aluno (nome, curso) e suas notas."""
    aluno_info = {}
    notas_info = []
    with gerenciar_conexao_bd() as cursor:
        if not cursor:
            return {"nome": "Aluno", "curso": "Não definido"}, []
        
        # 1. Busca o nome do aluno e o curso
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (aluno_id,))
        aluno_info['nome'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT curso FROM alunos WHERE id = ?", (aluno_id,))
        resultado_curso = cursor.fetchone()
        aluno_info['curso'] = resultado_curso[0] if resultado_curso else "Não definido"
        
        # 2. Busca as notas, nome da disciplina e nome do professor
        query_notas = """
        SELECT d.nome, prof.nome, n.nota_trabalho, n.nota_prova
        FROM notas n
        JOIN disciplinas d ON n.disciplina_id = d.id
        JOIN usuarios prof ON d.professor_id = prof.id
        WHERE n.aluno_id = ?
        """
        cursor.execute(query_notas, (aluno_id,))
        notas_info = cursor.fetchall()
        
    return aluno_info, notas_info

# --- Interface Gráfica ---

# Pega o ID do aluno passado como argumento
aluno_id_logado = sys.argv[1] if len(sys.argv) > 1 else None

janela = tk.Tk()
janela.title("Painel do Aluno")
janela.geometry("700x400")

aluno_info, notas_aluno = buscar_dados_aluno(aluno_id_logado)

frame_info = ttk.Frame(janela, padding=10)
frame_info.pack(fill=tk.X)
ttk.Label(frame_info, text=f"Bem-vindo(a), {aluno_info.get('nome', 'Aluno')}!", font=("Segoe UI", 16)).pack(anchor='w')
ttk.Label(frame_info, text=f"Curso: {aluno_info.get('curso', 'Não definido')}", font=("Segoe UI", 10)).pack(anchor='w', pady=(0, 10))

# Criar a tabela (Treeview) para exibir as notas
colunas = ('disciplina', 'professor', 'nota_trabalho', 'nota_prova', 'media_final')
tabela_notas = ttk.Treeview(janela, columns=colunas, show='headings')

tabela_notas.heading('disciplina', text='Disciplina')
tabela_notas.heading('professor', text='Professor(a)')
tabela_notas.heading('nota_trabalho', text='Nota Trabalho')
tabela_notas.heading('nota_prova', text='Nota Prova')
tabela_notas.heading('media_final', text='Média Final')

tabela_notas.column('disciplina', width=250)
tabela_notas.column('professor', width=200)
tabela_notas.column('nota_trabalho', width=100, anchor='center')
tabela_notas.column('nota_prova', width=100, anchor='center')
tabela_notas.column('media_final', width=100, anchor='center')

for disciplina, professor, nota_trabalho, nota_prova in notas_aluno:
    media = (nota_trabalho + nota_prova)
    tabela_notas.insert('', tk.END, values=(disciplina, professor, nota_trabalho, nota_prova, f"{media:.2f}"))

tabela_notas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

janela.mainloop()
