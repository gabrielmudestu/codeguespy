from flask import Flask, render_template, request, redirect, flash
import sqlite3
import re
import os

app = Flask(__name__)
app.secret_key = "codego2025"

# --- Criar o banco de dados se não existir ---
def init_db():
    if not os.path.exists("codego.db"):
        conn = sqlite3.connect("codego.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                login TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                departamento TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

# --- Validação do e-mail ---
def email_valido(email):
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(padrao, email) is not None

# --- Validação da senha ---
def senha_valida(senha):
    tem_maiuscula = any(c.isupper() for c in senha)
    tem_especial = any(c in "!@#$%^&*()-_=+[]{};:,.<>?" for c in senha)
    return tem_maiuscula and tem_especial

# --- Rota inicial (login) ---
@app.route("/")
def login():
    return render_template("index.html")

# --- Rota de recuperação de senha ---
@app.route("/recuperar")
def recuperar():
    return render_template("recuperar.html")

# --- Rota de cadastro (GET mostra página, POST salva dados) ---
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        login = request.form["login"].strip()
        email = request.form["email"].strip()
        senha = request.form["senha"].strip()
        departamento = request.form["departamento"]

        # Validações
        if not email_valido(email):
            flash("❌ E-mail inválido!", "erro")
            return redirect("/cadastro")

        if not senha_valida(senha):
            flash("❌ A senha deve conter pelo menos uma letra maiúscula e um caractere especial!", "erro")
            return redirect("/cadastro")

        conn = sqlite3.connect("codego.db")
        cursor = conn.cursor()

        # Verificar duplicidade
        cursor.execute("SELECT * FROM usuarios WHERE login=? OR email=?", (login, email))
        existente = cursor.fetchone()

        if existente:
            flash("⚠️ Login ou e-mail já cadastrados!", "erro")
            conn.close()
            return redirect("/cadastro")

        # Inserir no banco
        cursor.execute("""
            INSERT INTO usuarios (nome, login, email, senha, departamento)
            VALUES (?, ?, ?, ?, ?)
        """, (nome, login, email, senha, departamento))
        conn.commit()
        conn.close()

        flash("✅ Cadastro realizado com sucesso!", "sucesso")
        return redirect("/")

    return render_template("cadastro.html")

# --- Inicializar banco e servidor ---
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
