import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os
from database_manager import gerenciar_conexao_bd
#caminho para rodar no PC do Caio outros usuarios favor comentar a linha abaixo
sys.path.append('C:/Users/Usuario/AppData/Roaming/Python/Python313/site-packages')
import bcrypt

# --- Funções de Banco de Dados ---
def buscar_usuarios_por_tipo(tipo_usuario):
    """Busca todos os usuários de um determinado tipo (ex: 'professor', 'aluno')."""
    with gerenciar_conexao_bd() as cursor:
        if not cursor: return []
        cursor.execute("SELECT id, nome FROM usuarios WHERE tipo = ? ORDER BY nome", (tipo_usuario,))
        return cursor.fetchall()
    return [] # Retorna lista vazia se a conexão falhar

def buscar_todos_usuarios():
    """Busca todos os usuários (id, nome, cpf, email, tipo) do banco de dados."""
    with gerenciar_conexao_bd() as cursor:
        if not cursor: return []
        cursor.execute("SELECT id, nome, cpf, email, tipo FROM usuarios ORDER BY nome")
        return cursor.fetchall()
    return []


# --- Funções da Interface ---

def cadastrar_usuario(widgets, janela_cadastro):
    """Lê os dados dos widgets e cadastra o usuário no banco."""
    try:
        nome = widgets['nome'].get()
        cpf = widgets['cpf'].get()
        email = widgets['email'].get()
        senha = widgets['senha'].get()
        tipo = widgets['tipo'].get()

        if not all([nome, cpf, email, senha, tipo]):
            messagebox.showwarning("Campos Incompletos", "Por favor, preencha todos os campos.", parent=janela_cadastro)
            return

        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        with gerenciar_conexao_bd() as cursor:
            if cursor is None: return # Não prossegue se a conexão falhou
            
            # Verifica se CPF ou Email já existem
            cursor.execute("SELECT 1 FROM usuarios WHERE cpf = ? OR email = ?", (cpf, email))
            if cursor.fetchone():
                messagebox.showerror("Erro!", "CPF ou E-mail já cadastrado.", parent=janela_cadastro)
                return
            
            # Insere o novo usuário
            sql_usuario = "INSERT INTO usuarios(nome, cpf, email, senha, tipo) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(sql_usuario, (nome, cpf, email, senha_hash, tipo))
            user_id = cursor.lastrowid

            if tipo == 'aluno':
                cursor.execute("INSERT INTO alunos(id, curso) VALUES (?, ?)", (user_id, 'Não definido'))
            elif tipo == 'professor':
                cursor.execute("INSERT INTO professores(id, titulacao, area_atuacao) VALUES (?, ?, ?)", (user_id, 'Não definido', 'Não definida'))

        messagebox.showinfo("Confirmado!", f"Usuário '{nome}' cadastrado com sucesso com o ID: {user_id}", parent=janela_cadastro)
        
        # Limpa os campos após o sucesso
        limpar_campos(widgets)
        widgets['nome'].focus() # Devolve o foco para o primeiro campo

    except sqlite3.IntegrityError: # Esta captura pode ser redundante agora, mas mantida por segurança
        messagebox.showerror("Erro!", "CPF ou E-mail já cadastrado.", parent=janela_cadastro)
    except Exception as e: # Captura outras exceções inesperadas
        messagebox.showerror("Erro Inesperado", str(e), parent=janela_cadastro)

def limpar_campos(widgets): # Esta função é usada por cadastrar_usuario
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
        return False

    professor_id = combo_prof.professores_dict[professor_selecionado]

    with gerenciar_conexao_bd() as cursor:
        if not cursor: return False
        cursor.execute("INSERT INTO disciplinas (nome, professor_id) VALUES (?, ?)", (nome_disciplina, professor_id))

    messagebox.showinfo("Sucesso", f"Disciplina '{nome_disciplina}' criada com sucesso!", parent=combo_prof.winfo_toplevel())
    return True

def matricular_aluno(combo_aluno, combo_disciplina): # Esta função é usada por abrir_tela_realizar_matricula
    aluno_selecionado = combo_aluno.get()
    disciplina_selecionada = combo_disciplina.get()
    janela_pai = combo_aluno.winfo_toplevel()

    if not aluno_selecionado or not disciplina_selecionada:
        messagebox.showwarning("Campos Incompletos", "Selecione um aluno e uma disciplina para matricular.", parent=janela_pai)
        return

    aluno_id = combo_aluno.alunos_dict[aluno_selecionado]
    disciplina_id = combo_disciplina.disciplinas_dict[disciplina_selecionada]

    with gerenciar_conexao_bd() as cursor:
        if not cursor: return False
        
        # Verifica se a matrícula já existe
        cursor.execute("SELECT 1 FROM matriculas WHERE aluno_id = ? AND disciplina_id = ?", (aluno_id, disciplina_id))
        if cursor.fetchone():
            messagebox.showerror("Erro de Matrícula", "Este aluno já está matriculado nesta disciplina.", parent=janela_pai)
            return

        # 1. Inserir na tabela de matrículas
        cursor.execute("INSERT INTO matriculas (aluno_id, disciplina_id) VALUES (?, ?)", (aluno_id, disciplina_id))
        matricula_id = cursor.lastrowid

        # 2. Obter o ID do professor da disciplina para inserir na tabela de notas
        cursor.execute("SELECT professor_id FROM disciplinas WHERE id = ?", (disciplina_id,))
        resultado_prof = cursor.fetchone()
        if not resultado_prof:
             messagebox.showerror("Erro", "Disciplina sem professor associado.", parent=janela_pai)
             raise sqlite3.Error("Professor não encontrado para a disciplina.") # Força o rollback
        professor_id = resultado_prof[0]

        # 3. Inserir um registro inicial na tabela de notas
        cursor.execute("""
            INSERT INTO notas (disciplina_id, aluno_id, professor_id, nota_trabalho, nota_prova, matricula_id)
            VALUES (?, ?, ?, 0.0, 0.0, ?)
        """, (disciplina_id, aluno_id, professor_id, matricula_id))

    messagebox.showinfo("Sucesso", f"Aluno '{aluno_selecionado}' matriculado com sucesso!", parent=janela_pai)
    return True # Retorna sucesso para que a tela possa ser fechada

def buscar_todas_disciplinas():
    """Busca todas as disciplinas cadastradas."""
    with gerenciar_conexao_bd() as cursor:
        if not cursor: return []
        cursor.execute("SELECT id, nome FROM disciplinas ORDER BY nome")
        return cursor.fetchall()
    return []

def buscar_nome_usuario_por_id(usuario_id):
    """Busca o nome de um usuário específico pelo seu ID."""
    with gerenciar_conexao_bd() as cursor:
        if not cursor: return "Usuário"
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else "Usuário"

def atualizar_usuario(usuario_id, nome, cpf, email, janela_pai):
    """Atualiza os dados de um usuário no banco de dados."""
    if not all([nome, cpf, email]):
        messagebox.showwarning("Campos Incompletos", "Nome, CPF e E-mail são obrigatórios.", parent=janela_pai)
        return False
    
    with gerenciar_conexao_bd() as cursor:
        if not cursor: return False
        try:
            cursor.execute("UPDATE usuarios SET nome = ?, cpf = ?, email = ? WHERE id = ?", (nome, cpf, email, usuario_id))
            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!", parent=janela_pai)
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "CPF ou E-mail já pertence a outro usuário.", parent=janela_pai)
            return False

def deletar_usuario(usuario_id, janela_pai):
    """Deleta um usuário do banco de dados, tratando as restrições."""
    confirmar = messagebox.askyesno(
        "Confirmar Exclusão",
        "Tem certeza que deseja excluir este usuário?\nPara alunos, todas as matrículas e notas serão removidas.\nEsta ação não pode ser desfeita.",
        parent=janela_pai
    )
    if not confirmar:
        return False

    try:
        with gerenciar_conexao_bd() as cursor:
            if not cursor: return False
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!", parent=janela_pai)
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Erro de Restrição",
            "Não foi possível excluir este usuário. Provavelmente é um professor vinculado a uma ou mais disciplinas.\n\nAltere o professor responsável pela(s) disciplina(s) antes de tentar excluir.",
            parent=janela_pai
        )
        return False

def buscar_alunos_por_disciplina(disciplina_id):
    """Busca todos os alunos matriculados em uma disciplina específica."""
    with gerenciar_conexao_bd() as cursor:
        if not cursor: return []
        query = """
            SELECT u.id, u.nome, m.id 
            FROM usuarios u 
            JOIN matriculas m ON u.id = m.aluno_id 
            WHERE m.disciplina_id = ? ORDER BY u.nome
        """
        cursor.execute(query, (disciplina_id,))
        return cursor.fetchall()
    return []

def desmatricular_aluno(matricula_id, janela_pai):
    """Remove uma matrícula do banco de dados."""
    with gerenciar_conexao_bd() as cursor:
        if not cursor: return False
        cursor.execute("DELETE FROM matriculas WHERE id = ?", (matricula_id,))
    return True

def abrir_popup_criar_disciplina(janela_pai, callback_refresh): # Usada por abrir_tela_realizar_matricula
    """Abre uma janela popup para criar uma nova disciplina."""
    popup = tk.Toplevel(janela_pai)
    popup.title("Criar Nova Disciplina")
    popup.geometry("450x200")
    popup.transient(janela_pai) # Mantém o popup sobre a janela pai
    popup.grab_set() # Bloqueia interações com a janela pai

    frame_disciplinas = ttk.Labelframe(popup, text="Dados da Nova Disciplina", padding=10)
    frame_disciplinas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    ttk.Label(frame_disciplinas, text="Nome da Disciplina:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entrada_nome_disciplina = ttk.Entry(frame_disciplinas, width=40)
    entrada_nome_disciplina.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame_disciplinas, text="Professor Responsável:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    professores = buscar_usuarios_por_tipo('professor')
    professores_dict = {nome: id for id, nome in professores}
    combo_professores = ttk.Combobox(frame_disciplinas, values=list(professores_dict.keys()), state="readonly", width=38)
    combo_professores.professores_dict = professores_dict
    combo_professores.grid(row=1, column=1, padx=5, pady=5)

    def ao_criar():
        if criar_disciplina(entrada_nome_disciplina, combo_professores):
            popup.destroy() # Fecha o popup em caso de sucesso

    btn_criar = ttk.Button(frame_disciplinas, text="Criar Disciplina", command=ao_criar)
    btn_criar.grid(row=2, column=1, sticky="e", padx=5, pady=10)

    # Garante que a função de refresh seja chamada quando o popup fechar
    popup.protocol("WM_DELETE_WINDOW", lambda: (callback_refresh(), popup.destroy()))

def abrir_tela_realizar_matricula(): # Chamada pelo botão "Realizar Matrícula" na tela principal
    """Abre a tela para matricular um aluno, com opção de criar disciplina."""
    janela.withdraw()
    janela_matricula = tk.Toplevel(janela)
    janela_matricula.title("Realizar Matrícula")
    janela_matricula.geometry("550x250")

    frame_matricula = ttk.Labelframe(janela_matricula, text="Matricular Aluno em Disciplina", padding=10)
    frame_matricula.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Widgets ---
    ttk.Label(frame_matricula, text="Selecione o Aluno:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
    alunos = buscar_usuarios_por_tipo('aluno')
    alunos_dict = {nome: id for id, nome in alunos}
    combo_alunos = ttk.Combobox(frame_matricula, values=list(alunos_dict.keys()), state="readonly", width=50)
    combo_alunos.alunos_dict = alunos_dict
    combo_alunos.grid(row=0, column=1, columnspan=2, padx=5, pady=10)

    ttk.Label(frame_matricula, text="Selecione a Disciplina:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
    combo_disciplinas = ttk.Combobox(frame_matricula, state="readonly", width=40)
    combo_disciplinas.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

    def refresh_disciplinas():
        """Atualiza a lista de disciplinas no combobox."""
        disciplinas = buscar_todas_disciplinas()
        combo_disciplinas.disciplinas_dict = {nome: id for id, nome in disciplinas}
        combo_disciplinas['values'] = list(combo_disciplinas.disciplinas_dict.keys())

    btn_nova_disciplina = ttk.Button(frame_matricula, text="Nova...", width=8, command=lambda: abrir_popup_criar_disciplina(janela_matricula, refresh_disciplinas))
    btn_nova_disciplina.grid(row=1, column=2, padx=(0, 5), pady=10)

    def ao_matricular():
        if matricular_aluno(combo_alunos, combo_disciplinas):
            janela_matricula.destroy()

    btn_matricular = ttk.Button(frame_matricula, text="Matricular Aluno", command=ao_matricular)
    btn_matricular.grid(row=2, column=1, columnspan=2, sticky="e", padx=5, pady=20)

    refresh_disciplinas() # Carrega as disciplinas iniciais
    janela.wait_window(janela_matricula)
    janela.deiconify()

def abrir_tela_cadastro(janela_pai, callback_refresh=None):
    """Abre a tela de cadastro de novo usuário como um popup.
    
    Args:
        janela_pai: A janela que está chamando o cadastro.
        callback_refresh: Função para atualizar a lista de usuários após o cadastro.
    """
    janela_cadastro = tk.Toplevel(janela_pai)
    janela_cadastro.title("Cadastro de Novo Usuário")
    janela_cadastro.geometry("350x350")
    janela_cadastro.transient(janela_pai)
    janela_cadastro.grab_set()

    frame_cadastro = ttk.Frame(janela_cadastro, padding=10)
    frame_cadastro.pack(fill=tk.BOTH, expand=True)

    # Dicionário para guardar os widgets
    widgets = {}

    ttk.Label(frame_cadastro, text="Nome Completo:").pack(pady=(5,0))
    widgets['nome'] = ttk.Entry(frame_cadastro, width=40)
    widgets['nome'].pack()

    ttk.Label(frame_cadastro, text="CPF:").pack(pady=(5,0))
    widgets['cpf'] = ttk.Entry(frame_cadastro, width=40)
    widgets['cpf'].pack()

    ttk.Label(frame_cadastro, text="E-mail:").pack(pady=(5,0))
    widgets['email'] = ttk.Entry(frame_cadastro, width=40)
    widgets['email'].pack()

    ttk.Label(frame_cadastro, text="Senha:").pack(pady=(5,0))
    widgets['senha'] = ttk.Entry(frame_cadastro, width=40, show="*")
    widgets['senha'].pack()

    ttk.Label(frame_cadastro, text="Tipo de Usuário:").pack(pady=(5,0))
    widgets['tipo'] = ttk.Combobox(frame_cadastro, values=['aluno', 'professor', 'secretaria'], state="readonly")
    widgets['tipo'].pack()

    ttk.Button(frame_cadastro, text="Cadastrar", command=lambda: cadastrar_usuario(widgets, janela_cadastro)).pack(pady=20)

    def on_close():
        if callback_refresh:
            callback_refresh()
        janela_cadastro.destroy()

    janela_cadastro.protocol("WM_DELETE_WINDOW", on_close)

def abrir_tela_gerenciar_usuarios():
    """Abre a tela para visualizar e editar todos os usuários."""
    janela.withdraw()
    janela_usuarios = tk.Toplevel(janela)
    janela_usuarios.title("Gerenciar Usuários")
    janela_usuarios.geometry("800x600")

    # Frame de Edição
    frame_edicao = ttk.Labelframe(janela_usuarios, text="Editar Usuário Selecionado", padding=10)
    frame_edicao.pack(fill=tk.X, padx=10, pady=10)

    ttk.Label(frame_edicao, text="Nome:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    entry_nome = ttk.Entry(frame_edicao, width=40)
    entry_nome.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

    ttk.Label(frame_edicao, text="CPF:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    entry_cpf = ttk.Entry(frame_edicao, width=40)
    entry_cpf.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

    ttk.Label(frame_edicao, text="Email:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    entry_email = ttk.Entry(frame_edicao, width=40)
    entry_email.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
    
    frame_edicao.columnconfigure(1, weight=1)

    # Frame de Busca
    frame_busca = ttk.Frame(janela_usuarios, padding=(10, 0, 10, 10))
    frame_busca.pack(fill=tk.X)
    ttk.Label(frame_busca, text="Buscar por Nome ou CPF:").pack(side=tk.LEFT, padx=(0, 5))
    entry_busca = ttk.Entry(frame_busca)
    entry_busca.pack(fill=tk.X, expand=True)

    def filtrar_usuarios(event=None):
        termo_busca = entry_busca.get().lower()
        recarregar_usuarios(filtro=termo_busca)

    entry_busca.bind("<KeyRelease>", filtrar_usuarios)


    # Tabela de Usuários
    frame_tabela = ttk.Frame(janela_usuarios)
    frame_tabela.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    tabela = ttk.Treeview(frame_tabela, columns=('id', 'nome', 'cpf', 'email', 'tipo'), show='headings')
    tabela.heading('id', text='ID')
    tabela.heading('nome', text='Nome')
    tabela.heading('cpf', text='CPF')
    tabela.heading('email', text='Email')
    tabela.heading('tipo', text='Tipo')
    tabela.column('id', width=50, anchor='center')
    tabela.column('nome', width=250)
    tabela.column('cpf', width=120)
    tabela.column('email', width=250)
    tabela.column('tipo', width=80, anchor='center')
    tabela.pack(fill=tk.BOTH, expand=True)

    def recarregar_usuarios(filtro=""):
        for i in tabela.get_children():
            tabela.delete(i)
        for user in buscar_todos_usuarios():
            # user -> (id, nome, cpf, email, tipo)
            nome_usuario = str(user[1]).lower()
            cpf_usuario = str(user[2]).lower()
            if filtro in nome_usuario or filtro in cpf_usuario:
                tabela.insert('', tk.END, values=user)
        # Limpa os campos de edição após recarregar
        for entry in [entry_nome, entry_cpf, entry_email]:
            entry.delete(0, tk.END)

    def on_user_select(event):
        item_selecionado = tabela.focus()
        if not item_selecionado: return
        valores = tabela.item(item_selecionado, 'values')
        entry_nome.delete(0, tk.END); entry_nome.insert(0, valores[1])
        entry_cpf.delete(0, tk.END); entry_cpf.insert(0, valores[2])
        entry_email.delete(0, tk.END); entry_email.insert(0, valores[3])

    tabela.bind("<<TreeviewSelect>>", on_user_select)

    def salvar_alteracoes():
        item_selecionado = tabela.focus()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário para editar.", parent=janela_usuarios)
            return
        
        usuario_id = tabela.item(item_selecionado, 'values')[0]
        if atualizar_usuario(usuario_id, entry_nome.get(), entry_cpf.get(), entry_email.get(), janela_usuarios):
            recarregar_usuarios()

    def deletar_usuario_selecionado():
        item_selecionado = tabela.focus()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário para deletar.", parent=janela_usuarios)
            return
        
        usuario_id = tabela.item(item_selecionado, 'values')[0]
        if deletar_usuario(usuario_id, janela_usuarios):
            filtrar_usuarios() # Recarrega a lista com o filtro atual

    # Botões de ação para a tela de Gerenciar Usuários
    frame_botoes_gerenciar_usuarios = ttk.Frame(frame_edicao)
    frame_botoes_gerenciar_usuarios.grid(row=3, column=1, padx=5, pady=10, sticky="e")
    ttk.Button(frame_botoes_gerenciar_usuarios, text="Adicionar Novo Usuário", command=lambda: abrir_tela_cadastro(janela_usuarios, filtrar_usuarios)).pack(side=tk.LEFT, padx=5)
    ttk.Button(frame_botoes_gerenciar_usuarios, text="Salvar Alterações", command=salvar_alteracoes).pack(side=tk.LEFT, padx=5)
    ttk.Button(frame_botoes_gerenciar_usuarios, text="Deletar Usuário", command=deletar_usuario_selecionado).pack(side=tk.LEFT, padx=5)

    recarregar_usuarios()
    janela.wait_window(janela_usuarios)
    janela.deiconify()

def abrir_tela_gerenciar_matriculas():
    """Abre a tela para visualizar matrículas por disciplina e desmatricular alunos."""
    janela.withdraw()
    janela_ger_matricula = tk.Toplevel(janela)
    janela_ger_matricula.title("Gerenciar Matrículas")
    janela_ger_matricula.geometry("700x500")

    # Frame Superior: Seleção
    frame_selecao = ttk.Frame(janela_ger_matricula, padding=10)
    frame_selecao.pack(fill=tk.X)
    ttk.Label(frame_selecao, text="Selecione a Disciplina:").pack(side=tk.LEFT, padx=5)
    disciplinas = buscar_todas_disciplinas()
    disciplinas_dict = {nome: id for id, nome in disciplinas}
    combo_disciplinas = ttk.Combobox(frame_selecao, values=list(disciplinas_dict.keys()), state="readonly", width=50)
    combo_disciplinas.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Frame Inferior: Tabela de Alunos
    frame_tabela = ttk.Labelframe(janela_ger_matricula, text="Alunos Matriculados", padding=10)
    frame_tabela.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tabela = ttk.Treeview(frame_tabela, columns=('aluno_id', 'nome', 'acao'), show='headings')
    tabela.heading('aluno_id', text='ID Aluno')
    tabela.heading('nome', text='Nome do Aluno')
    tabela.heading('acao', text='Ação')
    tabela.column('aluno_id', width=80, anchor='center')
    tabela.column('nome', width=350)
    tabela.column('acao', width=120, anchor='center')
    tabela.pack(fill=tk.BOTH, expand=True)

    # Dicionário para guardar o ID da matrícula
    tabela.matriculas_map = {}

    def carregar_alunos_matriculados(event=None):
        for i in tabela.get_children():
            tabela.delete(i)
        tabela.matriculas_map.clear()

        disciplina_nome = combo_disciplinas.get()
        if not disciplina_nome: return

        disciplina_id = disciplinas_dict[disciplina_nome]
        alunos = buscar_alunos_por_disciplina(disciplina_id)
        for aluno_id, nome, matricula_id in alunos:
            item_id = tabela.insert('', tk.END, values=(aluno_id, nome, "Desmatricular 🗑️"))
            tabela.matriculas_map[item_id] = matricula_id

    combo_disciplinas.bind("<<ComboboxSelected>>", carregar_alunos_matriculados)

    def on_tabela_click(event):
        regiao = tabela.identify("region", event.x, event.y)
        coluna = tabela.identify_column(event.x)
        if regiao != "cell" or coluna != "#3": # Coluna 'acao'
            return

        item_id = tabela.identify_row(event.y)
        matricula_id = tabela.matriculas_map.get(item_id)
        nome_aluno = tabela.item(item_id, 'values')[1]

        if matricula_id and messagebox.askyesno("Confirmar", f"Tem certeza que deseja desmatricular o aluno '{nome_aluno}'?", parent=janela_ger_matricula):
            if desmatricular_aluno(matricula_id, janela_ger_matricula):
                messagebox.showinfo("Sucesso", "Aluno desmatriculado com sucesso.", parent=janela_ger_matricula)
                carregar_alunos_matriculados()

    tabela.bind("<Button-1>", on_tabela_click)

    janela.wait_window(janela_ger_matricula)
    janela.deiconify()

# --- Interface Gráfica ---

secretaria_id_logado = sys.argv[1] if len(sys.argv) > 1 else None

janela = tk.Tk()
janela.title("Painel Administrativo - Secretaria")
janela.geometry("400x300")

nome_usuario = buscar_nome_usuario_por_id(secretaria_id_logado) if secretaria_id_logado else "Usuário"

ttk.Label(janela, text=f"Bem-vindo(a), {nome_usuario}!", font=("Segoe UI", 16)).pack(pady=20)

frame_botoes = ttk.Frame(janela)
frame_botoes.pack(pady=10)

ttk.Button(frame_botoes, text="Gerenciar Usuários", command=abrir_tela_gerenciar_usuarios, width=40).pack(pady=5, ipady=5)
ttk.Button(frame_botoes, text="Gerenciar Matrículas", command=abrir_tela_gerenciar_matriculas, width=40).pack(pady=5, ipady=5)
ttk.Button(frame_botoes, text="Realizar Matrícula", command=abrir_tela_realizar_matricula, width=40).pack(pady=5, ipady=5)

janela.mainloop()
