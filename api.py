from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import date, datetime
from decimal import Decimal

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# Caminho do banco SQLite (relativo à raiz do projeto)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dados.db")  # Certifique-se de que o arquivo está no Git

# Função para conectar
def conectar():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
        return conn
    except Exception as e:
        print("Erro ao conectar no banco:", e)
        raise

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
        cursor = conn.cursor()
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
@app.route("/expedicao_anual", methods=["POST"])
def adicionar_expedicao_anual():
    try:
        dados = request.get_json()
        mes = dados.get("mes")
        valor = dados.get("valor")

        if not mes or not valor:
            return jsonify({"erro": "Mês e valor são obrigatórios."}), 400

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expedicao_anual (mes, valor) VALUES (?, ?)", (mes, valor))
        conn.commit()
        return jsonify({"mensagem": "Registro adicionado com sucesso!"}), 201
    except Exception as e:
        print("Erro em /expedicao_anual (POST):", e)
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'conn' in locals() and conn: conn.close()

# 🚀 Rodar no Render
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Render define a porta dinamicamente
    app.run(host="0.0.0.0", port=port, debug=True)
