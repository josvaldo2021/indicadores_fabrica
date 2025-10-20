from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import date, datetime
from decimal import Decimal

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# Caminho do banco SQLite (na raiz do projeto)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dados.db")  # Troque para seu arquivo SQLite

# Função para conectar
def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
    return conn

# Helper para serializar tipos
def serialize_row(row):
    item = {}
    for key in row.keys():
        val = row[key]
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
    return jsonify({"msg": "API funcionando com SQLite!"})

# 🟢 Produção diária
@app.route("/producao", methods=["GET"])
def listar_producao():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, setor, peso FROM producao ORDER BY id")
        rows = cursor.fetchall()
        resultado = [serialize_row(row) for row in rows]
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()
    return jsonify(resultado)

# 🟢 Expedição anual
@app.route("/expedicao_anual", methods=["GET"])
def listar_expedicao_anual():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expedicao_anual ORDER BY mes")  # supondo coluna 'mes'
        rows = cursor.fetchall()
        resultado = [serialize_row(row) for row in rows]
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()
    return jsonify(resultado)

# 🚀 Rodar no Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
