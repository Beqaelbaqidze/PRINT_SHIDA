
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="licenses",
        user="postgres",
        password="1524Elbaqa",
        port=5432
    )
