from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# CORS só para /api/*
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Config do banco (ajuste a senha se tiver)
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASS", ""),  # XAMPP costuma ser vazio
    "database": os.environ.get("DB_NAME", "gestao_alunos"),
    "charset": "utf8mb4"
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/")
def index():
    # renderiza templates/index.html
    return render_template("index.html")

@app.route("/api/cursos", methods=["GET"])
def listar_cursos():
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, nome_curso FROM cursos ORDER BY nome_curso")
        data = cur.fetchall()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao listar cursos: {str(e)}"}), 500
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

@app.route("/api/alunos", methods=["GET"])
def listar_alunos():
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT a.id, a.nome, a.email, a.data_matricula, c.nome_curso
            FROM alunos a
            JOIN cursos c ON c.id = a.curso_id
            ORDER BY a.id DESC
        """)
        data = cur.fetchall()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao listar alunos: {str(e)}"}), 500
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

@app.route("/api/alunos", methods=["POST"])
def cadastrar_aluno():
    try:
        payload = request.get_json(force=True) or {}
        nome = (payload.get("nome") or "").strip()
        email = (payload.get("email") or "").strip()
        data_matricula = (payload.get("data_matricula") or "").strip()
        curso_id = payload.get("curso_id")

        if not nome or not email or not data_matricula or not curso_id:
            return jsonify({"error": "Preencha todos os campos."}), 400

        conn = get_conn()
        cur = conn.cursor()
        sql = "INSERT INTO alunos (nome, email, curso_id, data_matricula) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (nome, email, int(curso_id), data_matricula))
        conn.commit()
        return jsonify({"message": "Aluno cadastrado com sucesso!"}), 201
    except mysql.connector.Error as db_err:
        return jsonify({"error": f"Erro de banco: {db_err.msg}"}), 500
    except Exception as e:
        return jsonify({"error": f"Erro inesperado: {str(e)}"}), 500
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    # debug=True para auto-reload
    app.run(debug=True)
