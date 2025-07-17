import streamlit as st
import sqlite3
import bcrypt
from datetime import datetime

def conectar_banco():
    return sqlite3.connect("usuarios.db")

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        usuario TEXT NOT NULL,
        message TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def adicionar_usuario(username, senha):
    conn = conectar_banco()
    cursor = conn.cursor()
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, senha_hash))
        conn.commit()
        registrar_log(username, f"Usuário '{username}' cadastrado.")
        st.success(f"Usuário '{username}' cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        st.error(f"O usuário '{username}' já existe!")
    finally:
        conn.close()

def excluir_usuario(username):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    registrar_log(username, f"Usuário '{username}' excluído.")
    st.success(f"Usuário '{username}' excluído com sucesso!")

def listar_usuarios():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]

def registrar_log(usuario, mensagem):
    conn = conectar_banco()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (timestamp, usuario, message) VALUES (?, ?, ?)", (timestamp, usuario, mensagem))
    conn.commit()
    conn.close()

def atualizar_senha(username, nova_senha):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()

    # Verificar se o usuário existe
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    user_exists = cursor.fetchone()

    if user_exists:
        # Gerar novo hash da senha
        hashed_password = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt())

        # Atualizar a senha no banco de dados
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
        conn.commit()
        conn.close()
        return True  # Sucesso
    else:
        conn.close()
        return False

# Para buscar logs por filtro
def conectar_banco():
    return sqlite3.connect("usuarios.db")
def visualizar_logs_por_data(data):
    """Busca os logs de uma data específica."""
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, usuario, message FROM logs WHERE timestamp LIKE ?", (f"{data}%",))
    logs = cursor.fetchall()
    conn.close()
    return logs

# Front-end
def mostrar():
    st.title("Painel de Administração ⚠️")
    st.subheader("Casdastre um novo Usuario ✅")

    with st.form(key='add_user_form'):
        novo_usuario = st.text_input("Novo Usuário")
        nova_senha = st.text_input("Senha", type="password")
        add_user_button = st.form_submit_button("Adicionar Usuário")

    if add_user_button:
        if novo_usuario and nova_senha:
            adicionar_usuario(novo_usuario, nova_senha)
        else:
            st.error("Preencha todos os campos!")

    st.subheader("Excluir Usuário")
    usuarios = listar_usuarios()
    if usuarios:
        usuario_selecionado = st.selectbox("Selecione o usuário para excluir", usuarios)
        if st.button("Excluir Usuário"):
            if usuario_selecionado == "admin":
                st.error("O usuário admin não pode ser excluído!")
            else:
                excluir_usuario(usuario_selecionado)
    else:
        st.write("Nenhum usuário cadastrado.")

    # Trocar senha
    st.subheader("Atualizar Senha do Usuário")

    usuarios_filtrados = [user for user in usuarios if user != "admin"]

    usuarios_select = st.selectbox("Selecione o usuario para trocar a senha", usuarios_filtrados)
    nova_senha = st.text_input("Nova senha", type="password")

    if st.button("Atualizar Senha"):
        if usuarios_select and nova_senha:
            sucesso = atualizar_senha(usuarios_select, nova_senha)
            if sucesso:
                st.success(f"Senha do usuário '{usuarios_select}' atualizada com sucesso!")
            else:
                st.error(f"Usuário '{usuarios_select}' não encontrado!")
        else:
            st.warning("Preencha todos os campos antes de continuar!")

    # Filtro para buscar Data
    st.subheader("Logs do Sistema")
    # Criar seletor de data
    data_selecionada = st.date_input("Selecione uma data para visualizar os logs:", datetime.today())
    data_formatada = data_selecionada.strftime("%Y-%m-%d")
    logs = visualizar_logs_por_data(data_formatada)

    if logs:
        for log in logs:
            st.text(f"{log[0]} - {log[1]} - {log[2]}")
    else:
        st.write("Nenhum log encontrado para esta data.")

    if st.button("Sair"):
        st.session_state.pagina = "login"
        st.session_state.usuario = None
        st.rerun()

# Inicializa o banco de dados
inicializar_banco()
