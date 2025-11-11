import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os

# --- Configuração de Caminhos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "gerenciamento_notas.db")

def buscar_disciplinas_professor(professor_id):
    """Busca as disciplinas lecionadas pelo professor."""
    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome FROM disciplinas WHERE professor_id = ?", (professor_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao buscar disciplinas: {e}")
        return []
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()

def buscar_alunos_e_notas(disciplina_id):
    """Busca alunos e suas notas para uma dada disciplina."""
    query = """
    SELECT u.id, u.nome, n.nota_trabalho, n.nota_prova
    FROM usuarios u
    JOIN notas n ON u.id = n.aluno_id
    WHERE n.disciplina_id = ?
    ORDER BY u.nome
    """
    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()
        cursor.execute(query, (disciplina_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao buscar alunos: {e}")
        return []
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()

def atualizar_notas_aluno(aluno_id, disciplina_id, nota_trabalho, nota_prova):
    """Atualiza as notas de um aluno no banco de dados."""
    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE notas 
            SET nota_trabalho = ?, nota_prova = ? 
            WHERE aluno_id = ? AND disciplina_id = ?
        """, (nota_trabalho, nota_prova, aluno_id, disciplina_id))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Notas atualizadas com sucesso!")
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao atualizar notas: {e}")
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()

# --- Funções da Interface ---

def ao_selecionar_disciplina(event):
    """Callback para quando uma disciplina é selecionada no ComboBox."""
    # Limpa a tabela e os campos de edição
    for i in tabela_alunos.get_children():
        tabela_alunos.delete(i)
    entrada_nota_trabalho.delete(0, tk.END)
    entrada_nota_prova.delete(0, tk.END)
    
    disciplina_selecionada_nome = combo_disciplinas.get()
    disciplina_id = disciplinas_dict[disciplina_selecionada_nome]
    
    alunos = buscar_alunos_e_notas(disciplina_id)
    for aluno in alunos:
        aluno_id, nome, nota_trabalho, nota_prova = aluno
        media = (nota_trabalho + nota_prova)
        tabela_alunos.insert('', tk.END, values=(aluno_id, nome, nota_trabalho, nota_prova, f"{media:.2f}"))

def ao_selecionar_aluno(event):
    """Callback para quando um aluno é selecionado na tabela."""
    item_selecionado = tabela_alunos.focus()
    if not item_selecionado: return

    valores = tabela_alunos.item(item_selecionado, 'values')
    nota_trabalho = valores[2]
    nota_prova = valores[3]

    entrada_nota_trabalho.delete(0, tk.END)
    entrada_nota_trabalho.insert(0, nota_trabalho)
    entrada_nota_prova.delete(0, tk.END)
    entrada_nota_prova.insert(0, nota_prova)

def salvar_edicao():
    """Salva as notas editadas."""
    item_selecionado = tabela_alunos.focus()
    if not item_selecionado:
        messagebox.showwarning("Nenhum Aluno Selecionado", "Por favor, selecione um aluno na tabela para editar as notas.")
        return

    try:
        nova_nota_trabalho = float(entrada_nota_trabalho.get())
        nova_nota_prova = float(entrada_nota_prova.get())
    except ValueError:
        messagebox.showerror("Valor Inválido", "Por favor, insira valores numéricos para as notas.")
        return

    valores = tabela_alunos.item(item_selecionado, 'values')
    aluno_id = valores[0]
    disciplina_id = disciplinas_dict[combo_disciplinas.get()]

    atualizar_notas_aluno(aluno_id, disciplina_id, nova_nota_trabalho, nova_nota_prova)
    # Recarrega a lista de alunos para mostrar os dados atualizados
    ao_selecionar_disciplina(None)

# --- Interface Gráfica ---

# Pega o ID do professor passado como argumento da linha de comando
professor_id_logado = sys.argv[1] if len(sys.argv) > 1 else None

janela = tk.Tk()
janela.title("Painel do Professor")
janela.geometry("800x600")

# Frame para seleção de disciplina
frame_disciplina = ttk.Frame(janela, padding=10)
frame_disciplina.pack(fill=tk.X)
ttk.Label(frame_disciplina, text="Selecione a Disciplina:").pack(side=tk.LEFT, padx=(0, 10))
disciplinas = buscar_disciplinas_professor(professor_id_logado)
disciplinas_dict = {nome: id for id, nome in disciplinas}
combo_disciplinas = ttk.Combobox(frame_disciplina, values=list(disciplinas_dict.keys()), state="readonly", width=50)
combo_disciplinas.pack(side=tk.LEFT)
combo_disciplinas.bind("<<ComboboxSelected>>", ao_selecionar_disciplina)

# Tabela para exibir alunos e notas
colunas = ('id', 'nome', 'nota_trabalho', 'nota_prova', 'media')
tabela_alunos = ttk.Treeview(janela, columns=colunas, show='headings')
tabela_alunos.heading('id', text='ID')
tabela_alunos.heading('nome', text='Nome do Aluno')
tabela_alunos.heading('nota_trabalho', text='Nota Trabalho')
tabela_alunos.heading('nota_prova', text='Nota Prova')
tabela_alunos.heading('media', text='Média Final')
tabela_alunos.column('id', width=50, anchor=tk.CENTER)
tabela_alunos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
tabela_alunos.bind("<<TreeviewSelect>>", ao_selecionar_aluno)

# Frame para edição de notas
frame_edicao = ttk.Frame(janela, padding=10)
frame_edicao.pack(fill=tk.X)
ttk.Label(frame_edicao, text="Nota Trabalho:").pack(side=tk.LEFT, padx=(0, 5))
entrada_nota_trabalho = ttk.Entry(frame_edicao, width=10)
entrada_nota_trabalho.pack(side=tk.LEFT, padx=(0, 20))
ttk.Label(frame_edicao, text="Nota Prova:").pack(side=tk.LEFT, padx=(0, 5))
entrada_nota_prova = ttk.Entry(frame_edicao, width=10)
entrada_nota_prova.pack(side=tk.LEFT, padx=(0, 20))

btn_salvar = ttk.Button(frame_edicao, text="Salvar Alterações", command=salvar_edicao)
btn_salvar.pack(side=tk.LEFT)

janela.mainloop()
