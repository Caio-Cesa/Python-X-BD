import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import sys
import os
import subprocess
from database_manager import gerenciar_conexao_bd

def buscar_disciplinas_professor(professor_id):
    """Busca as disciplinas lecionadas pelo professor."""
    with gerenciar_conexao_bd() as cursor:
        if not cursor: return []
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
        if not cursor: return []
        cursor.execute(query, (disciplina_id,))
        return cursor.fetchall()
    return []

def atualizar_notas_aluno(aluno_id, disciplina_id, nota_trabalho, nota_prova):
    """Atualiza as notas de um aluno no banco de dados."""
    with gerenciar_conexao_bd() as cursor:
        if not cursor: return
        cursor.execute("""
            UPDATE notas 
            SET nota_trabalho = ?, nota_prova = ? 
            WHERE aluno_id = ? AND disciplina_id = ?
        """, (nota_trabalho, nota_prova, aluno_id, disciplina_id))
    messagebox.showinfo("Sucesso", "Notas atualizadas com sucesso!")

# --- Funções da Interface ---

def ao_selecionar_disciplina(event):
    """Callback para quando uma disciplina é selecionada no ComboBox."""
    # Limpa as médias antigas
    label_media_trabalhos.config(text="Média Trabalhos: -")
    label_media_provas.config(text="Média Provas: -")
    # Limpa a tabela e os campos de edição
    for i in tabela_alunos.get_children():
        tabela_alunos.delete(i)
    entrada_nota_trabalho.delete(0, tk.END)
    entrada_nota_prova.delete(0, tk.END)
    
    disciplina_selecionada_nome = combo_disciplinas.get()
    disciplina_id = disciplinas_dict[disciplina_selecionada_nome]
    
    alunos = buscar_alunos_e_notas(disciplina_id)
    
    total_trabalho = 0
    total_prova = 0
    num_alunos = len(alunos)

    for aluno in alunos:
        aluno_id, nome, nota_trabalho, nota_prova = aluno
        media = (nota_trabalho + nota_prova)
        total_trabalho += nota_trabalho
        total_prova += nota_prova
        tabela_alunos.insert('', tk.END, values=(aluno_id, nome, nota_trabalho, nota_prova, f"{media:.2f}"))

    # Calcula e exibe as médias da turma
    if num_alunos > 0:
        media_trabalhos = total_trabalho / num_alunos
        media_provas = total_prova / num_alunos
        label_media_trabalhos.config(text=f"Média Trabalhos: {media_trabalhos:.2f}")
        label_media_provas.config(text=f"Média Provas: {media_provas:.2f}")

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
    
    # Validação do intervalo das notas
    if not (0 <= nova_nota_trabalho <= 5 and 0 <= nova_nota_prova <= 5):
        messagebox.showerror("Nota Inválida", "As notas devem estar entre 0 e 5.")
        return

    valores = tabela_alunos.item(item_selecionado, 'values')
    aluno_id = valores[0]
    disciplina_id = disciplinas_dict[combo_disciplinas.get()]

    atualizar_notas_aluno(aluno_id, disciplina_id, nova_nota_trabalho, nova_nota_prova)
    # Recarrega a lista de alunos para mostrar os dados atualizados
    ao_selecionar_disciplina(None)

def exportar_para_csv():
    """Exporta os dados da tabela de notas para um arquivo CSV."""
    disciplina_selecionada = combo_disciplinas.get()
    if not disciplina_selecionada:
        messagebox.showwarning("Nenhuma Disciplina", "Selecione uma disciplina para exportar as notas.")
        return

    # Pede ao usuário para escolher onde salvar o arquivo
    filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
        title="Salvar relatório de notas",
        initialfile=f"Relatorio_Notas_{disciplina_selecionada.replace(' ', '_')}.csv"
    )

    if not filepath:
        return # Usuário cancelou a caixa de diálogo

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            # Altere o delimitador aqui. Ex: delimiter=';' para ponto e vírgula
            writer = csv.writer(file, delimiter=';')
            # Escreve o cabeçalho
            writer.writerow(['ID Aluno', 'Nome', 'Nota Trabalho', 'Nota Prova', 'Média Final'])
            # Escreve os dados da tabela
            for item_id in tabela_alunos.get_children():
                row_values = tabela_alunos.item(item_id, 'values')
                writer.writerow(row_values)
        
        messagebox.showinfo("Sucesso", f"Relatório salvo com sucesso em:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo.\nErro: {e}")

# --- Interface Gráfica ---

# Pega o ID do professor passado como argumento da linha de comando
professor_id_logado = sys.argv[1] if len(sys.argv) > 1 else None

janela = tk.Tk()
janela.title("Painel do Professor")
janela.geometry("800x600")

# Frame para seleção de disciplina
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

# Tabela para exibir alunos e notas
colunas = ('id', 'nome', 'nota_trabalho', 'nota_prova', 'media')
tabela_alunos = ttk.Treeview(janela, columns=colunas, show='headings')
tabela_alunos.heading('id', text='ID')
tabela_alunos.heading('nome', text='Nome do Aluno')
tabela_alunos.heading('nota_trabalho', text='Nota Trabalho')
tabela_alunos.heading('nota_prova', text='Nota Prova')
tabela_alunos.heading('media', text='Nota Final')
tabela_alunos.column('id', width=50, anchor=tk.CENTER)
tabela_alunos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
tabela_alunos.bind("<<TreeviewSelect>>", ao_selecionar_aluno)

# Frame para exibir as médias da turma
frame_medias = ttk.Frame(janela, padding=(10, 0, 10, 10))
frame_medias.pack(fill=tk.X)
label_media_trabalhos = ttk.Label(frame_medias, text="Média Trabalhos: -", font=("Segoe UI", 9, "bold"))
label_media_trabalhos.pack(side=tk.LEFT, padx=(0, 20))
label_media_provas = ttk.Label(frame_medias, text="Média Provas: -", font=("Segoe UI", 9, "bold"))
label_media_provas.pack(side=tk.LEFT)


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

btn_exportar = ttk.Button(frame_edicao, text="Exportar para CSV", command=exportar_para_csv)
btn_exportar.pack(side=tk.RIGHT, padx=(10, 0))

janela.mainloop()
