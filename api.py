from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import date, datetime
from decimal import Decimal

app = Flask(__name__)
CORS(app)

# Caminho do banco SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(BASE_DIR, "dados.db")

# 🟢 Função de conexão
def conectar():
    conn = sqlite3.connect(CAMINHO_BANCO)
    conn.row_factory = sqlite3.Row  # permite acessar por nome da coluna
    return conn

# 🟢 Serializar dados
def serializar_registro(row):
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

# 🟢 Listar produção
@app.route("/producao", methods=["GET"])
def listar_producao():
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, setor, peso FROM producao ORDER BY id")
        dados = cursor.fetchall()
        resultado = [dict(row) for row in dados]
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# 🟢 Listar expedição anual
@app.route("/expedicao_anual", methods=["GET"])
def listar_expedicao_anual():
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expedicao_anual ORDER BY 1")
        dados = cursor.fetchall()
        resultado = [serializar_registro(row) for row in dados]
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)

