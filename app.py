from flask import Flask, request, redirect, render_template, session, flash
import sqlite3
import projetofinal
 
 
app = Flask(__name__)
app.secret_key = "79b2f5b603efa31bce02c15158c006dc"
 
# Rota para exibir a página de cadastro
@app.route("/cadastrar")
def cadastrar():
    return render_template("cadastrar.html")
 
# Rota para processar o cadastro
@app.route("/salvar_cadastro", methods=["POST"])
def salvar_cadastro():
    nome = request.form.get("nome")
    email = request.form.get("email")
    telefone = request.form.get("telefone")
    senha = request.form.get("senha")
    confirmar_senha = request.form.get("confirmar_senha")
 
    # Se as senhas não coincidem
    if senha != confirmar_senha:
        flash("Erro: As senhas não coincidem.")
        return redirect("/cadastrar")
 
    # Conectar ao banco de dados
    try:
        conn = sqlite3.connect("chatbot.db", timeout=10)  # Evita erro de "database is locked"
        cursor = conn.cursor()
 
        # Inserir os dados
        cursor.execute("INSERT INTO cadastro (nome, email, telefone, senha) VALUES (?, ?, ?, ?)",
                       (nome, email, telefone, senha))
 
        conn.commit()
 
    except sqlite3.IntegrityError:
        flash("Erro: Este e-mail já está cadastrado.")
        return redirect("/cadastrar")
 
    except sqlite3.OperationalError as e:
        flash(f"Erro no banco de dados: {e}")
        return redirect("/cadastrar")
 
    finally:
        cursor.close()
        conn.close()  # Fecha a conexão corretamente
 
    flash("Cadastro realizado com sucesso! Faça login.")
    return redirect("/")
 
# Rota para exibir a tela de login
@app.route("/")
def login():
    return render_template("login.html")
 
# Rota para processar o login
@app.route("/logar", methods=["POST"])
def logar():
    nome = request.form.get("nome")
    senha = request.form.get("senha")    
 
    # Conectar ao banco de dados para verificar as credenciais
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cadastro WHERE nome = ? AND senha = ?", (nome, senha))
    usuario = cursor.fetchone()
    conn.close()
 
    if usuario:
        session["usuario"] = usuario[0]  # Armazena o ID do usuário na sessão
        return redirect("/chat")  # Redireciona para a página de chat
    else:
        flash("Erro: E-mail ou senha inválidos.")
        return redirect("/")
 
# Rota para a página de interação com a IA
@app.route("/chat")
def chat():
    projetofinal.init_db()
    if "usuario" not in session:
        flash("Você precisa fazer login para acessar esta página.")
        return redirect("/")
   
    return render_template("chat.html")  
 
# Rota para logout
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Você saiu da conta.")
    return redirect("/")
 
if __name__ == "__main__":
    app.run(debug=True)