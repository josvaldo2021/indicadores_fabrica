from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
from datetime import date, datetime
from decimal import Decimal

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# ✅ Pega a string de conexão do ambiente (Render → Environment → DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("❌ A variável de ambiente DATABASE_URL não foi configurada.")

# 🔌 Função para conectar ao PostgreSQL (Neon)
def conectar():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as e:
        print("Erro ao conectar no banco:", e)
        raise

# 🧰 Função para converter registros em JSON
def serialize_row(row):
    item = {}
    for key, val in row.items():
        if isinstance(val, (datetime, date)):
            item[key] = val.isoformat()
        elif isinstance(val, Decimal):
            item[key] = float(val)
        else:
            item[key] = val
    return item

# 🟢 Teste simples
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"msg": "API funcionando com PostgreSQL (Neon)!"})

# 🟢 Produção diária
@app.route("/producao", methods=["GET"])
def listar_producao():
    try:
        conn = conectar()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT id, setor, peso, data_registro FROM producao ORDER BY id")
        rows = cursor.fetchall()
        resultado = [serialize_row(row) for row in rows]
    except Exception as e:
        print("Erro em /producao:", e)
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()
    return jsonify(resultado)

# 🟢 Expedição anual
@app.route("/expedicao_anual", methods=["GET"])
def listar_expedicao_anual():
    try:
        conn = conectar()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT mes, valor FROM expedicao_anual ORDER BY mes")
        rows = cursor.fetchall()
        resultado = [serialize_row(row) for row in rows]
    except Exception as e:
        print("Erro em /expedicao_anual:", e)
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()
    return jsonify(resultado)

# 🟢 Adicionar Expedição anual
@app.route("/registro_expedicao", methods=["POST"])
def adicionar_expedicao_anual():
    try:
        dados = request.get_json()
        mes = dados.get("mes")
        valor = dados.get("valor")

        if not mes or valor is None:
            return jsonify({"erro": "Mês e valor são obrigatórios."}), 400

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expedicao_anual (mes, valor) VALUES (%s, %s)", (mes, valor))
        conn.commit()
        return jsonify({"mensagem": "Registro adicionado com sucesso!"}), 201
    except Exception as e:
        print("Erro em /registro_expedicao (POST):", e)
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# 🏠 Rota raiz servindo index.html
@app.route("/")
def index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    return send_from_directory(static_dir, "index.html")

# 🚀 Rodar localmente ou no Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

