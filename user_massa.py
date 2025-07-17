import sqlite3
import bcrypt

def adicionar_usuarios(usuarios):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()

    for username, senha in usuarios.items():
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        user_exists = cursor.fetchone()

        if not user_exists:
            hashed_password = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            print(f"Usuário '{username}' adicionado com sucesso!")
        else:
            print(f"Usuário '{username}' já existe!")

    conn.commit()
    conn.close()


usuarios_para_adicionar = {
    "user1": "mudar@123",
    "user2": "mudar@123",
    "user3": "mudar@123",
    "user4": "mudar@123",
    "user5": "mudar@123",
}
adicionar_usuarios(usuarios_para_adicionar)
