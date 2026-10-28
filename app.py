from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-catalogo-filmes")

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_BANCO = os.path.join(PASTA, "instance")
BANCO = os.path.join(PASTA_BANCO, "filmes.db")

def conectar_banco():
    conexao = sqlite3.connect(BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao

def criar_banco():
    os.makedirs(PASTA_BANCO, exist_ok=True)

    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS filmes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            genero TEXT NOT NULL,
            ano INTEGER NOT NULL,
            nota INTEGER NOT NULL CHECK (nota BETWEEN 1 AND 10)
        )
    """)

    conexao.commit()
    conexao.close()

@app.route("/")
def index():
    conexao = conectar_banco()

    filmes = conexao.execute(
        "SELECT * FROM filmes ORDER BY id DESC"
    ).fetchall()

    conexao.close()

    return render_template("index.html", filmes=filmes)

@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        genero = request.form.get("genero", "").strip()

        try:
            ano = int(request.form.get("ano", ""))
            nota = int(request.form.get("nota", ""))
        except ValueError:
            flash("Informe um ano e uma nota válidos.")
            return redirect(url_for("adicionar"))

        if not titulo or not genero:
            flash("Preencha o título e o gênero.")
            return redirect(url_for("adicionar"))

        if len(titulo) > 150 or len(genero) > 80:
            flash("O título ou o gênero ultrapassou o limite de caracteres.")
            return redirect(url_for("adicionar"))

        if ano < 1888 or ano > 2100:
            flash("Informe um ano entre 1888 e 2100.")
            return redirect(url_for("adicionar"))

        if nota < 1 or nota > 10:
            flash("A nota deve estar entre 1 e 10.")
            return redirect(url_for("adicionar"))

        conexao = conectar_banco()

        conexao.execute(
            """
            INSERT INTO filmes (titulo, genero, ano, nota)
            VALUES (?, ?, ?, ?)
            """,
            (titulo, genero, ano, nota)
        )

        conexao.commit()
        conexao.close()

        flash("Filme cadastrado com sucesso!")
        return redirect(url_for("index"))

    return render_template("form.html", filme=None)


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexao = conectar_banco()

    filme = conexao.execute(
        "SELECT * FROM filmes WHERE id = ?",
        (id,)
    ).fetchone()

    conexao.close()

    if filme is None:
        flash("Filme não encontrado.")
        return redirect(url_for("index"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        genero = request.form.get("genero", "").strip()

        try:
            ano = int(request.form.get("ano", ""))
            nota = int(request.form.get("nota", ""))
        except ValueError:
            flash("Informe um ano e uma nota válidos.")
            return redirect(url_for("editar", id=id))

        if not titulo or not genero:
            flash("Preencha o título e o gênero.")
            return redirect(url_for("editar", id=id))

        if len(titulo) > 150 or len(genero) > 80:
            flash("O título ou o gênero ultrapassou o limite de caracteres.")
            return redirect(url_for("editar", id=id))

        if ano < 1888 or ano > 2100:
            flash("Informe um ano entre 1888 e 2100.")
            return redirect(url_for("editar", id=id))

        if nota < 1 or nota > 10:
            flash("A nota deve estar entre 1 e 10.")
            return redirect(url_for("editar", id=id))

        conexao = conectar_banco()

        conexao.execute(
            """
            UPDATE filmes
            SET titulo = ?, genero = ?, ano = ?, nota = ?
            WHERE id = ?
            """,
            (titulo, genero, ano, nota, id)
        )

        conexao.commit()
        conexao.close()

        flash("Filme atualizado com sucesso!")
        return redirect(url_for("index"))

    return render_template("form.html", filme=filme)


# Exclusão de filme (DELETE)
@app.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    conexao = conectar_banco()

    conexao.execute(
        "DELETE FROM filmes WHERE id = ?",
        (id,)
    )

    conexao.commit()
    conexao.close()

    flash("Filme excluído com sucesso!")
    return redirect(url_for("index"))


criar_banco()

if __name__ == "__main__":
    app.run(debug=True)