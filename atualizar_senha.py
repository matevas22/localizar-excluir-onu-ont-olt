import sqlite3
import bcrypt

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
        print(f"Senha do usuário '{username}' atualizada com sucesso!")
    else:
        print(f"Usuário '{username}' não encontrado!")

    conn.close()

# Alterar senha do usuário admin
atualizar_senha("admin", "admin")
