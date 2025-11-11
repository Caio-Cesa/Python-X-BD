import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os
#caminho para rodar no PC do Caio outros usuarios favor comentar a linha abaixo
sys.path.append('C:/Users/Usuario/AppData/Roaming/Python/Python313/site-packages')
import bcrypt

# --- Configuração de Caminhos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "gerenciamento_notas.db")

# --- Funções de Banco de Dados ---

def buscar_usuarios_por_tipo(tipo_usuario):
    """Busca todos os usuários de um determinado tipo (ex: 'professor', 'aluno')."""
    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome FROM usuarios WHERE tipo = ? ORDER BY nome", (tipo_usuario,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao buscar usuários: {e}")
        return []
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()

def buscar_todas_disciplinas():
    """Busca todas as disciplinas cadastradas."""
    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome FROM disciplinas ORDER BY nome")
        return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao buscar disciplinas: {e}")
        return []
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()

def buscar_nome_usuario_por_id(usuario_id):
    """Busca o nome de um usuário específico pelo seu ID."""
    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else "Usuário"
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao buscar nome: {e}")
        return "Usuário"
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()

# --- Funções da Interface ---

def cadastrar_usuario(widgets, janela_cadastro):
    """Lê os dados dos widgets e cadastra o usuário no banco."""
    nome = widgets['nome'].get()
    cpf = widgets['cpf'].get()
    email = widgets['email'].get()
    senha = widgets['senha'].get()
    tipo = widgets['tipo'].get()

    if not all([nome, cpf, email, senha, tipo]):
        messagebox.showwarning("Campos Incompletos", "Por favor, preencha todos os campos.", parent=janela_cadastro)
        return

    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    try:
        sql_usuario = "INSERT INTO usuarios(nome, cpf, email, senha, tipo) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(sql_usuario, (nome, cpf, email, senha_hash, tipo))
        user_id = cursor.lastrowid

        if tipo == 'aluno':
            cursor.execute("INSERT INTO alunos(id, curso) VALUES (?, ?)", (user_id, 'Não definido'))
        elif tipo == 'professor':
            cursor.execute("INSERT INTO professores(id, titulacao, area_atuacao) VALUES (?, ?, ?)", (user_id, 'Não definido', 'Não definida'))

        conexao.commit()
        messagebox.showinfo("Confirmado!", f"Usuário '{nome}' cadastrado com sucesso com o ID: {user_id}", parent=janela_cadastro)
        
        # Limpa os campos após o sucesso
        for widget in widgets.values():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set('')
        widgets['nome'].focus() # Devolve o foco para o primeiro campo

    except sqlite3.IntegrityError:
        messagebox.showerror("Erro!", "CPF ou E-mail já cadastrado.", parent=janela_cadastro)
    except sqlite3.Error as erro:
        messagebox.showerror("Erro de Banco de Dados!", erro, parent=janela_cadastro)
    finally:
        if conexao:
            conexao.close()

def limpar_campos(widgets):
    for widget in widgets.values():
        if isinstance(widget, ttk.Entry):
            widget.delete(0, tk.END)
        elif isinstance(widget, ttk.Combobox):
            widget.set('')

def criar_disciplina(entrada_nome, combo_prof):
    nome_disciplina = entrada_nome.get()
    professor_selecionado = combo_prof.get()

    if not nome_disciplina or not professor_selecionado:
        messagebox.showwarning("Campos Incompletos", "Preencha o nome da disciplina e selecione um professor.", parent=combo_prof.winfo_toplevel())
        return

    professor_id = combo_prof.professores_dict[professor_selecionado]

    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO disciplinas (nome, professor_id) VALUES (?, ?)", (nome_disciplina, professor_id))
        conexao.commit()
        messagebox.showinfo("Sucesso", f"Disciplina '{nome_disciplina}' criada com sucesso!", parent=combo_prof.winfo_toplevel())
        combo_prof.winfo_toplevel().destroy() # Fecha a janela Toplevel
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao criar disciplina: {e}")
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()

def matricular_aluno(combo_aluno, combo_disciplina):
    aluno_selecionado = combo_aluno.get()
    disciplina_selecionada = combo_disciplina.get()

    if not aluno_selecionado or not disciplina_selecionada:
        messagebox.showwarning("Campos Incompletos", "Selecione um aluno e uma disciplina para matricular.", parent=combo_aluno.winfo_toplevel())
        return

    aluno_id = combo_aluno.alunos_dict[aluno_selecionado]
    disciplina_id = combo_disciplina.disciplinas_dict[disciplina_selecionada]

    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()
        
        # 1. Inserir na tabela de matrículas
        cursor.execute("INSERT INTO matriculas (aluno_id, disciplina_id) VALUES (?, ?)", (aluno_id, disciplina_id))
        matricula_id = cursor.lastrowid

        # 2. Obter o ID do professor da disciplina para inserir na tabela de notas
        cursor.execute("SELECT professor_id FROM disciplinas WHERE id = ?", (disciplina_id,))
        professor_id = cursor.fetchone()[0]

        # 3. Inserir um registro inicial na tabela de notas
        cursor.execute("""
            INSERT INTO notas (disciplina_id, aluno_id, professor_id, nota_trabalho, nota_prova, matricula_id)
            VALUES (?, ?, ?, 0.0, 0.0, ?)
        """, (disciplina_id, aluno_id, professor_id, matricula_id))

        conexao.commit()
        messagebox.showinfo("Sucesso", f"Aluno '{aluno_selecionado}' matriculado com sucesso!", parent=combo_aluno.winfo_toplevel())
        combo_aluno.winfo_toplevel().destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro de Matrícula", "Este aluno já está matriculado nesta disciplina.", parent=combo_aluno.winfo_toplevel())
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao matricular aluno: {e}")
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()

def abrir_tela_cadastro():
    """Esconde a janela principal e abre a de cadastro, esperando-a fechar."""
    janela.withdraw()
    janela_cadastro = tk.Toplevel(janela)
    janela_cadastro.title("Cadastro de Novo Usuário")
    janela_cadastro.geometry("350x350")

    frame_cadastro = ttk.Frame(janela_cadastro, padding=10)
    frame_cadastro.pack(fill=tk.BOTH, expand=True)

    # Dicionário para guardar os widgets
    widgets = {}

    ttk.Label(frame_cadastro, text="Nome Completo:").pack(pady=5)
    widgets['nome'] = ttk.Entry(frame_cadastro, width=40)
    widgets['nome'].pack()

    ttk.Label(frame_cadastro, text="CPF:").pack(pady=5)
    widgets['cpf'] = ttk.Entry(frame_cadastro, width=40)
    widgets['cpf'].pack()

    ttk.Label(frame_cadastro, text="E-mail:").pack(pady=5)
    widgets['email'] = ttk.Entry(frame_cadastro, width=40)
    widgets['email'].pack()

    ttk.Label(frame_cadastro, text="Senha:").pack(pady=5)
    widgets['senha'] = ttk.Entry(frame_cadastro, width=40, show="*")
    widgets['senha'].pack()

    ttk.Label(frame_cadastro, text="Tipo de Usuário:").pack(pady=5)
    widgets['tipo'] = ttk.Combobox(frame_cadastro, values=['aluno', 'professor', 'secretaria'], state="readonly")
    widgets['tipo'].pack()

    ttk.Button(frame_cadastro, text="Cadastrar", command=lambda: cadastrar_usuario(widgets, janela_cadastro)).pack(pady=20)

    janela.wait_window(janela_cadastro)
    janela.deiconify()

def abrir_tela_disciplinas():
    """Esconde a janela principal e abre a de disciplinas, esperando-a fechar."""
    janela.withdraw()
    janela_disciplina = tk.Toplevel(janela)
    janela_disciplina.title("Gerenciar Disciplinas")
    janela_disciplina.geometry("450x200")

    frame_disciplinas = ttk.Labelframe(janela_disciplina, text="Criar Nova Disciplina", padding=10)
    frame_disciplinas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    ttk.Label(frame_disciplinas, text="Nome da Disciplina:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entrada_nome_disciplina = ttk.Entry(frame_disciplinas, width=40)
    entrada_nome_disciplina.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame_disciplinas, text="Professor Responsável:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    professores = buscar_usuarios_por_tipo('professor')
    professores_dict = {nome: id for id, nome in professores}
    combo_professores = ttk.Combobox(frame_disciplinas, values=list(professores_dict.keys()), state="readonly", width=38)
    combo_professores.professores_dict = professores_dict # Anexa o dicionário ao widget
    combo_professores.grid(row=1, column=1, padx=5, pady=5)

    btn_criar = ttk.Button(frame_disciplinas, text="Criar Disciplina",
                           command=lambda: criar_disciplina(entrada_nome_disciplina, combo_professores))
    btn_criar.grid(row=2, column=1, sticky="e", padx=5, pady=10)

    # A MÁGICA ACONTECE AQUI:
    janela.wait_window(janela_disciplina) # Pausa a execução até janela_disciplina ser fechada
    janela.deiconify() # Reexibe a janela principal

def abrir_tela_matriculas():
    """Esconde a janela principal e abre a de matrículas, esperando-a fechar."""
    janela.withdraw()
    janela_matricula = tk.Toplevel(janela)
    janela_matricula.title("Realizar Matrícula")
    janela_matricula.geometry("450x200")

    frame_matricula = ttk.Labelframe(janela_matricula, text="Matricular Aluno em Disciplina", padding=10)
    frame_matricula.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    ttk.Label(frame_matricula, text="Selecione o Aluno:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    alunos = buscar_usuarios_por_tipo('aluno')
    alunos_dict = {nome: id for id, nome in alunos}
    combo_alunos = ttk.Combobox(frame_matricula, values=list(alunos_dict.keys()), state="readonly", width=38)
    combo_alunos.alunos_dict = alunos_dict
    combo_alunos.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame_matricula, text="Selecione a Disciplina:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    disciplinas = buscar_todas_disciplinas()
    disciplinas_dict = {nome: id for id, nome in disciplinas}
    combo_disciplinas = ttk.Combobox(frame_matricula, values=list(disciplinas_dict.keys()), state="readonly", width=38)
    combo_disciplinas.disciplinas_dict = disciplinas_dict
    combo_disciplinas.grid(row=1, column=1, padx=5, pady=5)

    btn_matricular = ttk.Button(frame_matricula, text="Matricular Aluno",
                                command=lambda: matricular_aluno(combo_alunos, combo_disciplinas))
    btn_matricular.grid(row=2, column=1, sticky="e", padx=5, pady=10)

    # A MÁGICA ACONTECE AQUI TAMBÉM:
    janela.wait_window(janela_matricula) # Pausa a execução até janela_matricula ser fechada
    janela.deiconify() # Reexibe a janela principal

# --- Interface Gráfica ---

secretaria_id_logado = sys.argv[1] if len(sys.argv) > 1 else None

janela = tk.Tk()
janela.title("Painel Administrativo - Secretaria")
janela.geometry("400x300")

nome_usuario = buscar_nome_usuario_por_id(secretaria_id_logado) if secretaria_id_logado else "Usuário"

ttk.Label(janela, text=f"Bem-vindo(a), {nome_usuario}!", font=("Segoe UI", 16)).pack(pady=20)

frame_botoes = ttk.Frame(janela)
frame_botoes.pack(pady=10)

ttk.Button(frame_botoes, text="Cadastrar Novo Usuário", command=abrir_tela_cadastro, width=35).pack(pady=5, ipady=5)
ttk.Button(frame_botoes, text="Gerenciar Disciplinas", command=abrir_tela_disciplinas, width=35).pack(pady=5, ipady=5)
ttk.Button(frame_botoes, text="Realizar Matrículas", command=abrir_tela_matriculas, width=35).pack(pady=5, ipady=5)

janela.mainloop()
