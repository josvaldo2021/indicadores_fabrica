from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
from datetime import date, datetime
from decimal import Decimal

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# ========================
# 🔧 CONFIGURAÇÃO DO BANCO
# ========================

# As variáveis abaixo devem ser definidas no painel do Render (Environment Variables)
DB_HOST = os.getenv("DB_HOST", "ep-seu-endereco-do-neon.aws.neon.tech")
DB_NAME = os.getenv("DB_NAME", "nome_do_banco")
DB_USER = os.getenv("DB_USER", "usuario")
DB_PASS = os.getenv("DB_PASS", "senha")
DB_PORT = os.getenv("DB_PORT", "5432")

def conectar():
    """Conecta ao banco PostgreSQL no Neon."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            sslmode="require"  # Neon exige SSL
        )
        return conn
    except Exception as e:
        print("❌ Erro ao conectar no PostgreSQL:", e)
        raise


# ========================
# 🧩 FUNÇÃO DE SERIALIZAÇÃO
# ========================

def serialize_row(row):
    """Converte registros (Row) em dicionários compatíveis com JSON."""
    item = {}
    for key, val in row.items():
        if isinstance(val, (datetime, date)):
            item[key] = val.isoformat()
        elif isinstance(val, Decimal):
            item[key] = float(val)
        else:
            item[key] = val
    return item


# ========================
# 🧱 ENDPOINTS DA API
# ========================

# 🟢 Teste simples
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"msg": "API funcionando com PostgreSQL no Neon!"})


# 🟢 Produção diária
@app.route("/producao", methods=["GET"])
def listar_producao():
    try:
        conn = conectar()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT id, setor, peso FROM producao ORDER BY id;")
        rows = cursor.fetchall()
        resultado = [serialize_row(row) for row in rows]
    except Exception as e:
        print("Erro em /producao:", e)
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(resultado)


# 🟢 Expedição anual
@app.route("/expedicao_anual", methods=["GET"])
def listar_expedicao_anual():
    try:
        conn = conectar()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT id, mes, valor FROM expedicao_anual ORDER BY mes;")
        rows = cursor.fetchall()
        resultado = [serialize_row(row) for row in rows]
    except Exception as e:
        print("Erro em /expedicao_anual:", e)
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify(resultado)


# 🟢 Adicionar Expedição anual
@app.route("/registro_expedicao", methods=["POST"])
def adicionar_expedicao_anual():
    try:
        dados = request.get_json()
        mes = dados.get("mes")
        valor = dados.get("valor")

        if not mes or not valor:
            return jsonify({"erro": "Mês e valor são obrigatórios."}), 400

        # Conversão opcional (se vier em formato brasileiro)
        try:
            mes_formatado = datetime.strptime(mes, "%d/%m/%Y").date()
        except ValueError:
            try:
                mes_formatado = datetime.strptime(mes, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD ou DD/MM/YYYY."}), 400

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expedicao_anual (mes, valor) VALUES (%s, %s);",
            (mes_formatado, valor)
        )
        conn.commit()
        return jsonify({"mensagem": "Registro adicionado com sucesso!"}), 201
    except Exception as e:
        print("Erro em /registro_expedicao (POST):", e)
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()


# 🧱 Criar tabelas (rota opcional, útil para inicialização no Render)
@app.route("/initdb", methods=["GET"])
def inicializar_banco():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expedicao_anual (
                id SERIAL PRIMARY KEY,
                mes DATE NOT NULL,
                valor NUMERIC(12,2) NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS producao (
                id SERIAL PRIMARY KEY,
                setor VARCHAR(100),
                peso NUMERIC(12,2)
            );
        """)
        conn.commit()
        return jsonify({"mensagem": "Tabelas criadas/verificadas com sucesso!"})
    except Exception as e:
        print("Erro em /initdb:", e)
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn:
            conn.close()


# 🏠 Página inicial (opcional, se houver front em /static)
@app.route("/")
def index():
    return app.send_static_file("index.html")


# ========================
# 🚀 EXECUÇÃO NO RENDER
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render define a porta automaticamente
    app.run(host="0.0.0.0", port=port, debug=True)
