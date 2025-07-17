import sqlite3
import bcrypt

# Conectar ao banco de dados (ou criar um se não existir)
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

# Criar a tabela de usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# Função para inserir um novo usuário com senha criptografada
def adicionar_usuario(username, senha):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())  # Gera o hash da senha
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, senha_hash))
        conn.commit()
        print(f"Usuário {username} cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print(f"O usuário {username} já existe!")

# Adiciona um usuário de teste
adicionar_usuario("admin", "1234")  # Troque "1234" pela senha desejada

conn.close()
