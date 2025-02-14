
import sqlite3
 
# Função para inicializar o banco de dados
def init_db():
    conn = sqlite3.connect("chatbot.db")  # Nome do banco de dados
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cadastro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        telefone TEXT NOT NULL,
        senha TEXT NOT NULL
    )
                   
    """
    )
    conn.commit()
    conn.close()
 
   
 
# Executa a criação do banco de dados ao rodar o script
if __name__ == "__main__":
    init_db()