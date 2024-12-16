import psycopg2
from psycopg2 import OperationalError

def get_db_connection():
    try:
        # Conecta ao banco de dados PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            dbname="nicchio",
            user="postgres",
            password="Marcal1!",
            port="5432"
        )
        return conn
    except OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
