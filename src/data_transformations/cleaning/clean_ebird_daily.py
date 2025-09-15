from src.utils.storage_utils import attach_ducklake

def clean_ebird_daily(conn):
    with open('src/sql/cleaning/clean_ebird_daily.sql', 'r') as file:
        conn.execute(file.read())

def main():
    duckdb_db = ':memory:'
    conn = attach_ducklake(duckdb_db)
    conn.execute("CREATE SCHEMA IF NOT EXISTS silver;")
    clean_ebird_daily(conn)
    conn.close()

if __name__ == "__main__":
    main()
