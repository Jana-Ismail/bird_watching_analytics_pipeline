from src.utils.storage_utils import create_duckdb_s3_conn

def clean_inat(conn):
    with open('src/sql/cleaning_tables/clean_inat.sql', 'r') as file:
        conn.execute(file.read())

def main():
    duckdb_db = ':memory:'
    conn = create_duckdb_s3_conn(duckdb_db)
    
    clean_inat(conn)
    
    conn.close()

if __name__ == "__main__":
    main()