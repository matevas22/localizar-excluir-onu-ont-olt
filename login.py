import streamlit as st
import sqlite3
import bcrypt

def validar_login(username, password):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        hashed_password = user[0]
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode()
        return bcrypt.checkpw(password.encode(), hashed_password)
    return False

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "login"


def mostrar():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logoo.png", width=180)


    st.markdown("<h2 style='text-align: center;'>Bem-vindo!</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Faça login para continuar</h4>", unsafe_allow_html=True)


    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

    if entrar:
        if validar_login(username, password):
            st.success("Login bem-sucedido!")
            st.session_state.usuario = username
            st.session_state.pagina = "admin" if username == "admin" else "home"
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")
