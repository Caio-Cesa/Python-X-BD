import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import sys
import os
import subprocess
from PIL import Image, ImageTk  # <- para o brasão

from database_manager import gerenciar_conexao_bd

def buscar_disciplinas_professor(professor_id):
    """Busca as disciplinas lecionadas pelo professor."""
    with gerenciar_conexao_bd() as cursor:
        if not cursor:
            return []
        cursor.execute("SELECT id, nome FROM disciplinas WHERE professor_id = ?", (professor_id,))
        return cursor.fetchall()
    return []


def buscar_alunos_e_notas(disciplina_id):
    """Busca alunos e suas notas para uma dada disciplina."""
    query = """
    SELECT u.id, u.nome, n.nota_trabalho, n.nota_prova
    FROM usuarios u
    JOIN notas n ON u.id = n.aluno_id
    WHERE n.disciplina_id = ?
    ORDER BY u.nome
    """
    with gerenciar_conexao_bd() as cursor:
        if not cursor:
            return []
        cursor.execute(query, (disciplina_id,))
        return cursor.fetchall()
    return []


def atualizar_notas_aluno(aluno_id, disciplina_id, nota_trabalho, nota_prova):
    """Atualiza as notas de um aluno no banco de dados."""
    with gerenciar_conexao_bd() as cursor:
        if not cursor:
            return
        cursor.execute("""
            UPDATE notas 
            SET nota_trabalho = ?, nota_prova = ? 
            WHERE aluno_id = ? AND disciplina_id = ?
        """, (nota_trabalho, nota_prova, aluno_id, disciplina_id))
    messagebox.showinfo("Sucesso", "Notas atualizadas com sucesso!")


def ao_selecionar_disciplina(event):
    """Callback para quando uma disciplina é selecionada no ComboBox."""
    label_media_trabalhos.config(text="Média Trabalhos: -")
    label_media_provas.config(text="Média Provas: -")

    for i in tabela_alunos.get_children():
        tabela_alunos.delete(i)

    entrada_nota_trabalho.delete(0, tk.END)
    entrada_nota_prova.delete(0, tk.END)

    disciplina_selecionada = combo_disciplinas.get()
    disciplina_id = disciplinas_dict[disciplina_selecionada]

    alunos = buscar_alunos_e_notas(disciplina_id)

    total_trabalho = 0
    total_prova = 0
    num_alunos = len(alunos)

    for idx, aluno in enumerate(alunos):
        aluno_id, nome, nota_trabalho, nota_prova = aluno
        media = nota_trabalho + nota_prova

        total_trabalho += nota_trabalho
        total_prova += nota_prova

        tag = "evenrow" if idx % 2 == 0 else "oddrow"

        tabela_alunos.insert(
            "",
            tk.END,
            values=(aluno_id, nome, nota_trabalho, nota_prova, f"{media:.2f}"),
            tags=(tag,)
        )

    if num_alunos > 0:
        label_media_trabalhos.config(text=f"Média Trabalhos: {total_trabalho / num_alunos:.2f}")
        label_media_provas.config(text=f"Média Provas: {total_prova / num_alunos:.2f}")


def ao_selecionar_aluno(event):
    item = tabela_alunos.focus()
    if not item:
        return

    valores = tabela_alunos.item(item, "values")
    entrada_nota_trabalho.delete(0, tk.END)
    entrada_nota_trabalho.insert(0, valores[2])
    entrada_nota_prova.delete(0, tk.END)
    entrada_nota_prova.insert(0, valores[3])


def salvar_edicao():
    item = tabela_alunos.focus()
    if not item:
        messagebox.showwarning("Nenhum Aluno Selecionado", "Selecione um aluno para editar.")
        return

    try:
        nova_trabalho = float(entrada_nota_trabalho.get())
        nova_prova = float(entrada_nota_prova.get())
    except ValueError:
        messagebox.showerror("Erro", "Digite valores numéricos.")
        return

    valores = tabela_alunos.item(item, "values")
    aluno_id = valores[0]
    disciplina_id = disciplinas_dict[combo_disciplinas.get()]

    atualizar_notas_aluno(aluno_id, disciplina_id, nova_trabalho, nova_prova)
    ao_selecionar_disciplina(None)


def exportar_para_csv():
    disciplina = combo_disciplinas.get()
    if not disciplina:
        messagebox.showwarning("Aviso", "Selecione uma disciplina.")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv")],
        initialfile=f"Relatorio_{disciplina.replace(' ', '_')}.csv"
    )

    if not path:
        return

    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Nome", "Trabalho", "Prova", "Média"])
            for item in tabela_alunos.get_children():
                writer.writerow(tabela_alunos.item(item, "values"))
        messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{path}")
    except Exception as e:
        messagebox.showerror("Erro", str(e))


# ================= INTERFACE ======================

professor_id_logado = sys.argv[1] if len(sys.argv) > 1 else None

janela = tk.Tk()
janela.title("Painel do Professor")
janela.geometry("800x600")

# ======= (ALTERAÇÃO MÍNIMA) BRASÃO + ÍCONE =========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
icone_path = os.path.join(BASE_DIR, "Hogwarts.png")

try:
    # Ícone da janela
    img_icon = ImageTk.PhotoImage(Image.open(icone_path).resize((32, 32)))
    janela.iconphoto(False, img_icon)
    janela._icon_ref = img_icon

    # Cabeçalho discreto
    frame_header = tk.Frame(janela, bg="#5e0f16", padx=15, pady=10)
    frame_header.pack(fill=tk.X)

    img_header = ImageTk.PhotoImage(Image.open(icone_path).resize((60, 60)))
    lbl_header = tk.Label(frame_header, image=img_header, bg="#5e0f16")
    lbl_header.image = img_header
    lbl_header.pack(side="right")

    tk.Label(
        frame_header,
        text="Painel do Professor",
        font=("Segoe UI", 15, "bold"),
        bg="#5e0f16",
        fg="white"
    ).pack(anchor="w")

except Exception as e:
    print("Erro ao carregar brasão:", e)
# ====================================================


# ===== Seleção da disciplina =====
frame_disciplina = ttk.Frame(janela, padding=10)
frame_disciplina.pack(fill=tk.X)

frame_esquerda_disciplina = ttk.Frame(frame_disciplina)
frame_esquerda_disciplina.pack(side=tk.LEFT, fill=tk.X, expand=True)

ttk.Label(frame_esquerda_disciplina, text="Selecione a Disciplina:").pack(side=tk.LEFT, padx=(0, 10))

disciplinas = buscar_disciplinas_professor(professor_id_logado)
disciplinas_dict = {nome: id for id, nome in disciplinas}

combo_disciplinas = ttk.Combobox(frame_disciplina, values=list(disciplinas_dict.keys()), state="readonly", width=50)
combo_disciplinas.pack(side=tk.LEFT)
combo_disciplinas.bind("<<ComboboxSelected>>", ao_selecionar_disciplina)

# ===== Tabela =====
colunas = ("id", "nome", "nota_trabalho", "nota_prova", "media")
tabela_alunos = ttk.Treeview(janela, columns=colunas, show="headings")

tabela_alunos.heading("id", text="ID")
tabela_alunos.heading("nome", text="Nome")
tabela_alunos.heading("nota_trabalho", text="Trabalho")
tabela_alunos.heading("nota_prova", text="Prova")
tabela_alunos.heading("media", text="Média")

tabela_alunos.column("id", width=50, anchor=tk.CENTER)
tabela_alunos.column("nome", width=250, anchor="w")
tabela_alunos.column("nota_trabalho", width=120, anchor=tk.CENTER)
tabela_alunos.column("nota_prova", width=120, anchor=tk.CENTER)
tabela_alunos.column("media", width=120, anchor=tk.CENTER)

tabela_alunos.tag_configure("oddrow", background="#f0f0f0")
tabela_alunos.tag_configure("evenrow", background="white")

tabela_alunos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
tabela_alunos.bind("<<TreeviewSelect>>", ao_selecionar_aluno)

# ===== Exibir médias =====
frame_medias = ttk.Frame(janela, padding=10)
frame_medias.pack(fill=tk.X)

label_media_trabalhos = ttk.Label(frame_medias, text="Média Trabalhos: -", font=("Segoe UI", 9, "bold"))
label_media_trabalhos.pack(side=tk.LEFT, padx=(0, 20))

label_media_provas = ttk.Label(frame_medias, text="Média Provas: -", font=("Segoe UI", 9, "bold"))
label_media_provas.pack(side=tk.LEFT)

# ===== Edição de notas =====
frame_edicao = ttk.Frame(janela, padding=10)
frame_edicao.pack(fill=tk.X)

ttk.Label(frame_edicao, text="Nota Trabalho:").pack(side=tk.LEFT)
entrada_nota_trabalho = ttk.Entry(frame_edicao, width=10)
entrada_nota_trabalho.pack(side=tk.LEFT, padx=(5, 20))

ttk.Label(frame_edicao, text="Nota Prova:").pack(side=tk.LEFT)
entrada_nota_prova = ttk.Entry(frame_edicao, width=10)
entrada_nota_prova.pack(side=tk.LEFT, padx=(5, 20))

btn_salvar = ttk.Button(frame_edicao, text="Salvar Alterações", command=salvar_edicao)
btn_salvar.pack(side=tk.LEFT, padx=10)

btn_exportar = ttk.Button(frame_edicao, text="Exportar CSV", command=exportar_para_csv)
btn_exportar.pack(side=tk.RIGHT)

janela.mainloop()
