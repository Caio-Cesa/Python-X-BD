import tkinter as tk
from tkinter import ttk
import sys
import os
from PIL import Image, ImageTk

from database_manager import gerenciar_conexao_bd

def buscar_dados_aluno(aluno_id):
    """Busca os dados completos do aluno (nome, curso) e suas notas."""
    aluno_info = {}
    notas_info = []

    # Se não veio ID, já evita erro
    if not aluno_id:
        return {"nome": "Aluno não identificado", "curso": "Não definido"}, []

    with gerenciar_conexao_bd() as cursor:
        if not cursor:
            return {"nome": "Aluno", "curso": "Não definido"}, []
        
        # 1. Busca o nome do aluno
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (aluno_id,))
        resultado_nome = cursor.fetchone()
        if not resultado_nome:
            # Não achou aluno com esse ID
            return {"nome": "Aluno não identificado", "curso": "Não definido"}, []

        aluno_info['nome'] = resultado_nome[0]
        
        # 2. Busca o curso
        cursor.execute("SELECT curso FROM alunos WHERE id = ?", (aluno_id,))
        resultado_curso = cursor.fetchone()
        aluno_info['curso'] = resultado_curso[0] if resultado_curso else "Não definido"
        
        # 3. Busca as notas, nome da disciplina e nome do professor
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
janela.geometry("800x500")  # um pouco maior, só estética

# Busca dados do aluno
aluno_info, notas_aluno = buscar_dados_aluno(aluno_id_logado)

# ===== CABEÇALHO ESTILIZADO =====
frame_info = tk.Frame(janela, bg="#5e0f16", padx=20, pady=10)
frame_info.pack(fill=tk.X)

# ---- IMAGEM DO BRASÃO (Hogwarts.png na mesma pasta do arquivo) ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(BASE_DIR, "Hogwarts.png")

try:
    img_original = Image.open(img_path)
    img_redimensionada = img_original.resize((70, 70))
    img_tk = ImageTk.PhotoImage(img_redimensionada)

    label_img = tk.Label(frame_info, image=img_tk, bg="#5e0f16")
    label_img.image = img_tk  # mantém referência
    label_img.pack(side="right", padx=10)

    # ícone da janela (substitui a pena)
    img_icon = ImageTk.PhotoImage(img_original.resize((32, 32)))
    janela.iconphoto(False, img_icon)
    janela._icon_reference = img_icon  # impede de sumir da memória

except Exception as e:
    print("Erro ao definir ícone da janela:", e)


except Exception as e:
    print("ERRO AO CARREGAR IMAGEM:")
    print("Caminho usado:", img_path)
    print("Erro:", e)

# Texto de boas-vindas
tk.Label(
    frame_info,
    text=f"Bem-vindo(a), {aluno_info.get('nome', 'Aluno')}!",
    font=("Segoe UI", 16, "bold"),
    bg="#5e0f16",
    fg="white"
).pack(anchor='w')

tk.Label(
    frame_info,
    text=f"Curso: {aluno_info.get('curso', 'Não definido')}",
    font=("Segoe UI", 10),
    bg="#5e0f16",
    fg="#e0e0e0"
).pack(anchor='w', pady=(0, 10))

# ===== ESTILO DA TABELA (somente visual) =====
style = ttk.Style()
style.configure("Treeview", font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))


colunas = ('disciplina', 'professor', 'nota_trabalho', 'nota_prova', 'nota_final', 'status')
tabela_notas = ttk.Treeview(janela, columns=colunas, show='headings')

tabela_notas.heading('disciplina', text='Disciplina')
tabela_notas.heading('professor', text='Professor(a)')
tabela_notas.heading('nota_trabalho', text='Nota Trabalho')
tabela_notas.heading('nota_prova', text='Nota Prova')
tabela_notas.heading('nota_final', text='Nota Final')
tabela_notas.heading('status', text='Status')

tabela_notas.column('disciplina', width=220, anchor='w')
tabela_notas.column('professor', width=180, anchor='w')
tabela_notas.column('nota_trabalho', width=100, anchor='center')
tabela_notas.column('nota_prova', width=100, anchor='center')
tabela_notas.column('nota_final', width=80, anchor='center')
tabela_notas.column('status', width=80, anchor='center')


tabela_notas.tag_configure('oddrow', background='#f0f0f0')
tabela_notas.tag_configure('evenrow', background='white')


for i, (disciplina, professor, nota_trabalho, nota_prova) in enumerate(notas_aluno):
    nota_final = nota_trabalho + nota_prova
    status = "Aprovado" if nota_final >= 6.0 else "Reprovado"
    tag = 'evenrow' if i % 2 == 0 else 'oddrow'

    tabela_notas.insert(
        '',
        tk.END,
        values=(disciplina, professor, nota_trabalho, nota_prova, f"{nota_final:.2f}", status),
        tags=(tag,)
    )

tabela_notas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

janela.mainloop()
