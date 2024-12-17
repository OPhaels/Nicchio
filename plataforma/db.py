import psycopg2
from psycopg2 import OperationalError

def get_db_connection():
    try:
        # URL de conexão fornecida diretamente
        database_url = "postgres://u2mdnkmdhilhrv:p23aadd21b7676a83b8bb09e53da098de2626960f0a520328cb9a4f6d103c485f@cd5gks8n4kb20g.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/de9gu837qaadu7"

        # Conecta ao banco de dados PostgreSQL usando a URL de conexão
        conn = psycopg2.connect(database_url, sslmode='require')  # sslmode='require' garante uma conexão segura

        return conn
    except OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Exemplo de como consultar os dados de uma tabela
def fetch_data():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Substitua "sua_tabela" pelo nome real de uma das suas tabelas
            cur.execute("SELECT * FROM sua_tabela;")
            rows = cur.fetchall()

            for row in rows:
                print(row)  # Exibe os dados recuperados
            cur.close()
        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")
        finally:
            conn.close()

# Testando a função
fetch_data()
