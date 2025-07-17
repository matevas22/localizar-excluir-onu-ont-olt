import streamlit as st

# Configuração da página, deve ser a PRIMEIRA chamada do Streamlit no arquivo principal
st.set_page_config(
    page_title="APP - ONU/OLT",
    page_icon="logo_icon.png",  # Coloque esse arquivo na mesma pasta do app.py
    layout="centered"
)

import login
import home
import admin

# Inicializa a sessão
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# Navegação entre páginas
if st.session_state.pagina == "login":
    login.mostrar()
elif st.session_state.pagina == "home":
    home.mostrar()
elif st.session_state.pagina == "admin":
    admin.mostrar()
