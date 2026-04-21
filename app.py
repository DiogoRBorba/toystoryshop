from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "toy-story-shop-secret"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        categoria = request.form.get("categoria", "").strip()
        quantidade = request.form.get("quantidade", "").strip()
        preco = request.form.get("preco", "").strip()

        if not nome or not categoria or not quantidade or not preco:
            flash("Preencha todos os campos.")
            return redirect(url_for("adicionar"))

        try:
            quantidade = int(quantidade)
            preco = float(preco)
        except ValueError:
            flash("Quantidade e preço precisam ser números válidos.")
            return redirect(url_for("adicionar"))

        conn = get_connection()
        conn.execute(
            "INSERT INTO produtos (nome, categoria, quantidade, preco) VALUES (?, ?, ?, ?)",
            (nome, categoria, quantidade, preco)
        )
        conn.commit()
        conn.close()

        flash("Produto adicionado com sucesso.")
        return redirect(url_for("listar"))

    return render_template("adicionar.html")


@app.route("/listar")
def listar():
    conn = get_connection()
    produtos = conn.execute("SELECT * FROM produtos ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("listar.html", produtos=produtos)


@app.route("/remover", methods=["GET", "POST"])
def remover():
    conn = get_connection()

    if request.method == "POST":
        produto_id = request.form.get("id", "").strip()

        if not produto_id:
            flash("Informe o ID do produto.")
            conn.close()
            return redirect(url_for("remover"))

        produto = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()

        if not produto:
            conn.close()
            flash("Produto não encontrado.")
            return redirect(url_for("remover"))

        conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        conn.commit()
        conn.close()

        flash("Produto removido com sucesso.")
        return redirect(url_for("listar"))

    produtos = conn.execute("SELECT * FROM produtos ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("remover.html", produtos=produtos)


@app.route("/atualizar", methods=["GET", "POST"])
def atualizar():
    conn = get_connection()

    if request.method == "POST":
        produto_id = request.form.get("id", "").strip()
        nova_quantidade = request.form.get("quantidade", "").strip()
        novo_preco = request.form.get("preco", "").strip()

        if not produto_id or not nova_quantidade or not novo_preco:
            flash("Preencha todos os campos.")
            conn.close()
            return redirect(url_for("atualizar"))

        produto = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()

        if not produto:
            conn.close()
            flash("Produto não encontrado.")
            return redirect(url_for("atualizar"))

        try:
            nova_quantidade = int(nova_quantidade)
            novo_preco = float(novo_preco)
        except ValueError:
            conn.close()
            flash("Quantidade e preço precisam ser números válidos.")
            return redirect(url_for("atualizar"))

        conn.execute(
            "UPDATE produtos SET quantidade = ?, preco = ? WHERE id = ?",
            (nova_quantidade, novo_preco, produto_id)
        )
        conn.commit()
        conn.close()

        flash("Produto atualizado com sucesso.")
        return redirect(url_for("listar"))

    produtos = conn.execute("SELECT * FROM produtos ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("atualizar.html", produtos=produtos)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)