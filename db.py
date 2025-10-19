import sqlite3

conn = sqlite3.connect("dados.db")
cursor = conn.cursor()

# Tabelas equivalentes às do Access
cursor.execute("""
CREATE TABLE IF NOT EXISTS producao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setor TEXT,
    peso REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS expedicao_anual (
    mes TEXT,
    valor REAL
)
""")

# Dados fictícios de exemplo
cursor.execute("INSERT INTO producao (setor, peso) VALUES ('Corte', 32000)")
cursor.execute("INSERT INTO producao (setor, peso) VALUES ('Laminação', 22000)")
cursor.execute("INSERT INTO producao (setor, peso) VALUES ('Expedição', 40000)")
cursor.execute("INSERT INTO expedicao_anual (mes, valor) VALUES ('Janeiro', 120000)")
cursor.execute("INSERT INTO expedicao_anual (mes, valor) VALUES ('Fevereiro', 90000)")

conn.commit()
conn.close()

print("Banco SQLite criado com sucesso!")
