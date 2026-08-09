import psycopg2

# Parametry połączenia
conn_params: dict[str, str | int] = {
    "host": "postgres18",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "mysecret"
}

try:
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"Połączono z PostgreSQL:\n{version[0]}")
except psycopg2.OperationalError as e:
    print(f"Błąd połączenia: {e}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()

# I will create database objects by DBeaver application connected to postgres18 container
# DDL will be placed in assets folder