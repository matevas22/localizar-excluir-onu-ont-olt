import streamlit as st
import sqlite3
from datetime import datetime
import telnetlib2
import bcrypt
import pandas as pd
import plotly.express as px
import re
import time

# --- seu código continua aqui ---
# Lista de IPs das OLTs
OLT_LIST = [
    '192.168.1.10', '192.168.1.20', '192.168.1.30', '192.168.1.40',
    '192.168.2.10', '192.168.2.20', '192.168.2.30', '192.168.2.40',
    '10.0.0.10', '10.0.0.20', '10.0.0.30', '10.0.0.40',
]

OLT_NOMES = {
    '192.168.1.10': 'Projeto Alpha',
    '192.168.1.20': 'Projeto Beta',
    '192.168.1.30': 'Projeto Gama',
    '192.168.1.40': 'Projeto Delta',
    '192.168.2.10': 'Projeto Epsilon',
    '192.168.2.20': 'Projeto Zeta',
    '192.168.2.30': 'Projeto Theta',
    '192.168.2.40': 'Projeto Lambda',
    '10.0.0.10': 'Projeto Sigma',
    '10.0.0.20': 'Projeto Omega',
    '10.0.0.30': 'Projeto Kappa',
    '10.0.0.40': 'Projeto Pi',
}

STATUS_DESCRICOES = {
    'Offline': 'Sem comunicação com a OLT.',
    'offline': 'Sem comunicação com a OLT.',
    'Working': 'Funcionando normalmente (Online).',
    'working': 'Funcionando normalmente (Online).',
    'Online': 'Conectada, mas possivelmente sem configuração completa.',
    'online': 'Conectada, mas possivelmente sem configuração completa.',
    'Auth-Fail': 'Falha na autenticação (SN inválido).',
    'auth-fail': 'Falha na autenticação (SN inválido).',
    'LOS': 'Sem sinal óptico (problema na fibra).',
    'los': 'Sem sinal óptico (problema na fibra).',
    'Dying-Gasp': 'Perda de energia na ONU.',
    'dying-gasp': 'Perda de energia na ONU.',
    'Config-Fail': 'Erro ao aplicar configuração.',
    'config-fail': 'Erro ao aplicar configuração.',
    'In-Service': 'Em operação (igual ao working).',
    'in-service': 'Em operação (igual ao working).',
    'OOS': 'Desativada manualmente.',
    'oos': 'Desativada manualmente.',
    'Initial': 'Conectada, aguardando autenticação/configuração.',
    'initial': 'Conectada, aguardando autenticação/configuração.',
    'Deactivated': 'Conectada, mas desabilitada.',
    'deactivated': 'Conectada, mas desabilitada.',
    'Disabled': 'Reconhecida, porém bloqueada.',
    'disabled': 'Reconhecida, porém bloqueada.'
}

def conectar_banco():
    return sqlite3.connect("usuarios.db")

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
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

def registrar_log(usuario, message):
    conn = conectar_banco()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (timestamp, usuario, message) VALUES (?, ?, ?)", (timestamp, usuario, message))
    conn.commit()
    conn.close()

def visualizar_logs():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, usuario, message FROM logs ORDER BY id DESC")
    logs = cursor.fetchall()
    conn.close()
    return logs

def pesquisar(sn_onu):
    dic_pesquisar = {}
    for ip in OLT_LIST:
        try:
            t = telnetlib2.telnet()
            t.login(ip, username='seu_usuario', password='sua_senha', p=23, timeout=30)
            output = t.execute(f'show gpon onu by sn {sn_onu}')
            output = output.split('\\r\\n')
            onu_list = [i for i in output if "onu" in i]
            if onu_list:
                dic_pesquisar[ip] = onu_list
            t.close()
        except Exception as e:
            st.error(f"Erro ao conectar na OLT {ip}: {e}")
    return dic_pesquisar

def excluir(ip, interface, index):
    try:
        t = telnetlib2.telnet()
        t.login(ip, username='seu_usuario', password='sua_senha', p=23, timeout=30)
        t.execute(f'conf t\n')
        t.execute(f'interface gpon-olt_{interface}\n')
        t.execute(f'no onu {index}\n')
        t.close()
        return True
    except Exception as e:
        return False

def atualizar_senha(username, nova_senha):
    if not username or not nova_senha:
        st.error("Usuário ou nova senha inválidos.")
        return False

    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    nova_senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt())
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (nova_senha_hash, username))
    conn.commit()
    conn.close()
    st.success("Senha atualizada com sucesso!")
    return True

def listar_usuarios():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]

def login_usuario():
    return st.session_state.get("usuario")

def dashboard_logs(usuario):
    logs = visualizar_logs()
    df = pd.DataFrame(logs, columns=["timestamp", "usuario", "message"])
    df_usuario = df[df['usuario'] == usuario]
    df_usuario['acao'] = df_usuario['message'].apply(lambda x: 'verificou' if 'verificou' in x else 'excluiu' if 'excluiu' in x else 'outro')
    df_filtrado = df_usuario[df_usuario['acao'].isin(['verificou', 'excluiu'])]
    contagem = df_filtrado['acao'].value_counts().reset_index()
    contagem.columns = ['Ação', 'Quantidade']
    st.subheader("Dashboard de Atividades")
    fig = px.pie(contagem, names='Ação', values='Quantidade', title='Proporção de Ações do Usuário')
    st.plotly_chart(fig, use_container_width=True)

def parse_onu_state(output):
    # Regex corrigido para pegar a ordem correta dos campos
    pattern = r"(\d+/\d+/\d+):(\d+)\s+(\w+)\s+(\w+)\s+(\w+)\s+\d+\(GPON\)"
    onus = []
    for match in re.finditer(pattern, output):
        onus.append({
            "interface": match.group(1),
            "onu_id": match.group(2),
            "admin_state": match.group(3),
            "omcc_state": match.group(4),
            "phase_state": match.group(5)
        })
    return onus

def parse_onu_detail(output):
    if '%Error' in output or 'Invalid input' in output:
        return {
            "name": None,
            "type": None,
            "status": None,
            "serial": None,
            "erro": "Não foi possível obter detalhes desta ONU. Verifique se está online/provisionada."
        }
    name = re.search(r"Name:\s+([^\n\r]+)", output)
    serial = re.search(r"Serial number:\s+([A-Z0-9]+)", output)
    status = re.search(r"ONU Status:\s+([^\n\r]+)", output)
    return {
        "name": name.group(1).strip() if name else None,
        "serial": serial.group(1).strip() if serial else None,
        "status": status.group(1).strip() if status else None,
    }

def parse_signal_power(output, interface, onu_id):
    output_clean = output.replace('\\r\\n', '\n').replace('\r\n', '\n')
    
    # Busca simples: gpon-onu_1/1/1:10   -20.988(dbm)
    pattern = rf"gpon-onu_{interface}:{onu_id}\s+(-?\d+\.\d+)\(dbm\)"
    match = re.search(pattern, output_clean)
    if match:
        return match.group(1)
    
    pattern2 = rf"{onu_id}\s+(-?\d+\.\d+)\(dbm\)"
    match2 = re.search(pattern2, output_clean)
    if match2:
        return match2.group(1)
    
    if "no signal" in output_clean:
        return "no signal"
    
    return None

def buscar_detalhes_onu(ip, interface, onu_id):
    detalhes = {}
    try:
        t1 = telnetlib2.telnet()
        t1.login(ip, username='seu_usuario', password='sua_senha', p=23, timeout=30)
        
        output_state = t1.execute(f'show gpon onu state gpon-olt_{interface}')
        lista_onus = parse_onu_state(output_state)
        status_onu = next((onu for onu in lista_onus if onu["onu_id"] == str(onu_id)), None)
        if status_onu:
            detalhes["status_onu"] = status_onu
        
        output_detail = t1.execute(f'show gpon onu detail-info gpon-onu_{interface}:{onu_id}')
        detalhes_detail = parse_onu_detail(output_detail)
        for k, v in detalhes_detail.items():
            detalhes[k] = v
        t1.close()
        
        t2 = telnetlib2.telnet()
        t2.login(ip, username='seu_usuario', password='sua_senha', p=23, timeout=30)
        output_tx = t2.execute(f'show pon power olt-rx gpon-onu_{interface}:{onu_id}')
        detalhes["sinal_tx"] = parse_signal_power(output_tx, interface, onu_id)
        t2.close()
        
        t3 = telnetlib2.telnet()
        t3.login(ip, username='seu_usuario', password='sua_senha', p=23, timeout=30)
        output_rx = t3.execute(f'show pon power onu-rx gpon-onu_{interface}:{onu_id}')
        detalhes["sinal_rx"] = parse_signal_power(output_rx, interface, onu_id)
        t3.close()
        
    except Exception as e:
        detalhes["erro"] = str(e)
    return detalhes

def mostrar():
    st.subheader("Gerenciar ONU/ONT dos Projetos")
    st.text(f"Bem-vindo, {login_usuario()}!")

    if "usuario" not in st.session_state or not st.session_state.usuario:
        st.warning("Você precisa estar logado para acessar esta página!")
        return

    usuario = st.session_state.usuario

    tab1, tab2, tab3 = st.tabs(["🔍 Localizar e Excluir ONU/ONT", "📊 Potencia da ONU/ONT", "🔐 Alterar Senha"])

    with tab1:
        st.subheader("🔍 Localizar ONU/ONT")
        onu_list = []
        olt_list = []

        with st.form(key='verificar_onu_form'):
            sn_onu = st.text_input('📝 Informe o SN da ONU/ONT para localizar:', value='', max_chars=12)
            verificar_button = st.form_submit_button(label='🔍 Localizar ONU/ONT')

        if verificar_button:
            if len(sn_onu) != 12:
                st.error('❌ SN inválido!')
            else:
                registrar_log(usuario, f"localizou ONU/ONT com SN {sn_onu}")
                resultado = pesquisar(sn_onu.upper())
                if resultado:
                    st.write("✅ ONU/ONT encontrada(s):")
                    for olt, onus in resultado.items():
                        nome_olt = OLT_NOMES.get(olt, olt)
                        for onu_info in onus:
                            onu_list.append(onu_info)
                            olt_list.append(olt)
                            st.write(f"📍 {nome_olt}: {onu_info}")
                    st.session_state.onu_list = onu_list
                    st.session_state.olt_list = olt_list
                    st.session_state.sn_onu = sn_onu
                else:
                    st.write('❌ Nenhuma ONU/ONT encontrada.')
                    st.session_state.onu_list = []
                    st.session_state.olt_list = []

        if "onu_list" in st.session_state and st.session_state.onu_list:
            with st.form(key='excluir_onu_form'):
                st.subheader("🗑️ Excluir ONU/ONT")
                for i in range(len(st.session_state.olt_list)):
                    olt = st.session_state.olt_list[i]
                    nome_olt = OLT_NOMES.get(olt, olt)
                    interface = st.session_state.onu_list[i].split(':')[0].split('_')[1]
                    index = st.session_state.onu_list[i].split(':')[1]
                    st.write(f"📍 {nome_olt}: gpon-onu_{interface}:{index}")
                col1, col2 = st.columns(2)
                confirmar = col1.form_submit_button(label='✅ Sim, excluir')
                cancelar = col2.form_submit_button(label='❌ Não, cancelar')

            if confirmar:
                for i in range(len(st.session_state.olt_list)):
                    olt = st.session_state.olt_list[i]
                    nome_olt = OLT_NOMES.get(olt, olt)
                    interface = st.session_state.onu_list[i].split(':')[0].split('_')[1]
                    index = st.session_state.onu_list[i].split(':')[1]
                    if excluir(olt, interface, index):
                        st.success(f"✅ ONU/ONT {index} excluída com sucesso na {nome_olt}!")
                        registrar_log(usuario, f"excluiu ONU/ONT {index} na {nome_olt}")
                    else:
                        st.error(f"❌ Falha ao excluir ONU/ONT {index} na OLT {nome_olt}")
            if cancelar:
                st.warning("⚠️ Exclusão cancelada!")
                st.session_state.onu_list = []
                st.rerun()

    with tab2:
        st.subheader("📊 Potencia da ONU/ONT")
        
        with st.form(key='detalhes_onu_form'):
            sn_onu_detalhes = st.text_input('📝 Informe o SN da ONU/ONT para ver detalhes:', value='', max_chars=12)
            detalhes_button = st.form_submit_button(label='📊 Ver Detalhes')

        if detalhes_button:
            if len(sn_onu_detalhes) != 12:
                st.error('❌ SN inválido!')
            else:
                registrar_log(usuario, f"verificou detalhes da ONU/ONT com SN {sn_onu_detalhes}")
                resultado = pesquisar(sn_onu_detalhes.upper())
                if resultado:
                    for olt, onus in resultado.items():
                        for onu_info in onus:
                            interface = onu_info.split(':')[0].split('_')[1]
                            index = onu_info.split(':')[1]
                            detalhes = buscar_detalhes_onu(olt, interface, index)
                            
                
                            sinal_rx = detalhes.get('sinal_rx', None)
                            if sinal_rx is None or (isinstance(sinal_rx, str) and 'Error' in sinal_rx):
                                st.markdown("📡 **Sinal RX:** None")
                            else:
                                valor_rx = str(sinal_rx).replace(' dBm','').replace('(dbm)','')
                                st.markdown(f"📡 **Sinal RX:** {valor_rx}")
                            
    
                            sinal_tx = detalhes.get('sinal_tx', None)
                            if sinal_tx is None or (isinstance(sinal_tx, str) and 'Error' in sinal_tx):
                                st.markdown("📡 **Sinal TX:** None")
                            else:
                                valor_tx = str(sinal_tx).replace(' dBm','').replace('(dbm)','')
                                st.markdown(f"📡 **Sinal TX:** {valor_tx}")
                            
                            status_onu = detalhes.get('status_onu')
                            status_phase = status_onu.get('phase_state') if status_onu else None
                            if status_phase:
                                descricao_status = STATUS_DESCRICOES.get(status_phase, f'Status desconhecido: {status_phase}')
                                st.markdown(f"🔄 **Status:** {status_phase} - {descricao_status}")
                            else:
                                st.markdown("🔄 **Status:** None")
                            if detalhes.get('erro'):
                                st.error(f"❌ Erro ao buscar detalhes: {detalhes['erro']}")
                else:
                    st.write('❌ Nenhuma ONU/ONT encontrada.')

    with tab3:
        st.subheader("🔐 Alterar Senha")
        st.text(f"👤 Usuário logado: **{usuario}**")
        nova_senha = st.text_input("🔑 Nova senha", type="password")
        confirmar_senha = st.text_input("🔑 Confirme a nova senha", type="password")
        if st.button("💾 Atualizar Senha"):
            if nova_senha == confirmar_senha:
                registrar_log(usuario, "usuario atualizou a senha")
                atualizar_senha(usuario, nova_senha)
            else:
                st.error("❌ As senhas não coincidem!")

    st.markdown("---")
    dashboard_logs(usuario)

    if st.button("🚪 Sair"):
        st.session_state.pagina = "login"
        st.session_state.usuario = None
        st.rerun()

inicializar_banco()
