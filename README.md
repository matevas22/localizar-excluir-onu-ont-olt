# Acesso-ONT

Sistema web para gerenciamento de ONUs/ONTs em redes ópticas, com autenticação, painel administrativo e operações de consulta, exclusão e monitoramento de dispositivos.

---

## Índice
- [Visão Geral](#visão-geral)
- [Arquitetura do Projeto](#arquitetura-do-projeto)
- [Funcionalidades](#funcionalidades)
- [Fluxo de Uso](#fluxo-de-uso)
- [Instalação e Execução](#instalação-e-execução)
- [Banco de Dados](#banco-de-dados)
- [Exemplo de Uso](#exemplo-de-uso)
- [Dependências](#dependências)
- [Observações](#observações)

---

## Visão Geral

Este sistema foi desenvolvido para facilitar o gerenciamento de dispositivos ONU/ONT conectados a OLTs em projetos de redes ópticas. Ele permite que operadores e administradores:
- Localizem, consultem e excluam ONUs/ONTs.
- Visualizem potência e status dos dispositivos.
- Gerenciem usuários e logs de operações.

A interface é web, construída com Streamlit, e o backend utiliza SQLite para persistência dos dados.

---

## Arquitetura do Projeto

```
app.py (ponto de entrada)
├── login.py      # Tela e lógica de autenticação
├── home.py       # Painel do usuário comum
├── admin.py      # Painel administrativo
├── sqlite.py     # Inicialização do banco de dados
├── atualizar_senha.py  # Script para redefinir senha
├── user_massa.py # Cadastro em massa de usuários
├── usuarios.db   # Banco de dados SQLite
├── requirements.txt
├── imagens (logo_icon.png, logoo.png, etc)
```

- **Frontend:** Streamlit (Python)
- **Backend:** Python puro, SQLite, Telnet para comunicação com OLTs
- **Banco de Dados:** SQLite (arquivo local `usuarios.db`)

---

## Funcionalidades

### 1. Autenticação de Usuários
- Login com senha criptografada (bcrypt).
- Controle de sessão via `st.session_state`.
- Usuário admin tem acesso ao painel administrativo.

### 2. Painel do Usuário (home.py)
- **Localizar ONU/ONT:**
  - Busca pelo número de série (SN) em todas as OLTs cadastradas.
  - Exibe lista de ONUs/ONTs encontradas, agrupadas por OLT.
- **Excluir ONU/ONT:**
  - Após localizar, permite excluir a ONU/ONT selecionada via Telnet.
- **Visualizar Potência e Status:**
  - Consulta detalhada do sinal RX/TX e status operacional (phase state) da ONU/ONT.
  - Mostra descrição amigável do status (ex: "Sem comunicação", "Funcionando normalmente").
- **Alterar Senha:**
  - Usuário pode alterar sua própria senha.
- **Dashboard de Atividades:**
  - Gráfico de ações realizadas (verificações, exclusões) usando Plotly.
- **Logs:**
  - Visualização dos logs das ações do usuário.

### 3. Painel Administrativo (admin.py)
- **Cadastro de Usuários:**
  - Adiciona novos usuários com senha criptografada.
- **Exclusão de Usuários:**
  - Remove usuários do sistema (exceto admin).
- **Atualização de Senha de Usuários:**
  - Permite redefinir a senha de qualquer usuário.
- **Visualização de Logs:**
  - Filtro de logs por data para auditoria.
- **Gerenciamento de Sessão:**
  - Logout e controle de acesso.

### 4. Banco de Dados (sqlite.py)
- Tabelas:
  - `users`: id, username (único), password (hash)
  - `logs`: id, timestamp, usuario, message
- Scripts auxiliares para inicialização e manipulação em massa de usuários.

### 5. Comunicação com OLTs
- Utiliza Telnet (`telnetlib2`) para executar comandos nas OLTs.
- Lista de OLTs configurada no código.
- Comandos executados:
  - Buscar ONU/ONT por SN
  - Excluir ONU/ONT
  - Consultar detalhes de potência e status

---

## Fluxo de Uso

1. **Login:**
   - Usuário acessa a tela de login e informa credenciais.
   - Se admin, é redirecionado ao painel administrativo; caso contrário, ao painel do usuário.
2. **Operações:**
   - Usuário pode buscar, consultar e excluir ONUs/ONTs, além de alterar sua senha.
   - Todas as ações são registradas em logs.
3. **Administração:**
   - Admin pode cadastrar/excluir usuários, redefinir senhas e auditar logs.

---

## Instalação e Execução

1. **Clone o repositório:**
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd Acesso-ONT
   ```
2. **(Opcional) Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Inicie o aplicativo:**
   ```bash
   streamlit run app.py
   ```
5. **Acesse pelo navegador:**
   - [http://localhost:8501](http://localhost:8501)

---

## Banco de Dados

- O banco é criado automaticamente ao rodar o sistema.
- Usuário padrão: `admin` (senha definida no script de inicialização, pode ser alterada).
- Scripts auxiliares:
  - `sqlite.py`: inicializa o banco e cria usuário admin.
  - `atualizar_senha.py`: redefine senha do admin.
  - `user_massa.py`: adiciona múltiplos usuários de uma vez.

---

## Exemplo de Uso

- **Buscar ONU/ONT:**
  1. Informe o SN (12 caracteres) e clique em "Localizar ONU/ONT".
  2. Veja a lista de dispositivos encontrados.
- **Excluir ONU/ONT:**
  1. Após localizar, selecione e exclua a ONU/ONT desejada.
- **Consultar Potência/Status:**
  1. Informe o SN e clique em "Ver Detalhes".
  2. Veja os valores de RX/TX e status.
- **Administração:**
  1. No painel admin, adicione/exclua usuários e redefina senhas.
  2. Filtre logs por data para auditoria.

---

## Dependências

Principais bibliotecas:
- sqlite3
- bcrypt
- pandas
- plotly
- telnetlib

Veja todas em `requirements.txt`.

---

## Observações
- O sistema foi projetado para uso interno, com foco em segurança e rastreabilidade.
- Certifique-se de que as OLTs estejam acessíveis na rede.
- Para produção, recomenda-se proteger o acesso à aplicação e ao banco de dados.
---
## Usuario padrão

```bash
   usuario: admin senha: admin
```

---

## Contato
Dúvidas ou sugestões? Entre em contato com o desenvolvedor responsável. 
