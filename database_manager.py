import sqlite3
import os
from contextlib import contextmanager
from tkinter import messagebox

# --- Configuração de Caminhos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "gerenciamento_notas.db")

@contextmanager
def gerenciar_conexao_bd():
    """
    Gerencia a conexão com o banco de dados (abre, commita, fecha).
    Fornece um cursor e garante que a conexão seja fechada.
    """
    conexao = None
    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()
        yield cursor  # Fornece o cursor para o bloco 'with'
        conexao.commit() # Salva as alterações se tudo correu bem
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro: {e}")
        if conexao:
            conexao.rollback() # Reverte as alterações em caso de erro
    finally:
        if conexao:
            conexao.close()