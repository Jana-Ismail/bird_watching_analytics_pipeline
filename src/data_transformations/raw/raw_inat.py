from src.utils.storage_utils import create_duckdb_s3_conn

def create_raw_inat_view(conn):
    with open('src/sql/raw_views/raw_inat.sql', 'r') as file:
        conn.execute(file.read())

def main():
    duckdb_db = ':memory:'
    conn = create_duckdb_s3_conn(duckdb_db)
    conn.execute("CREATE SCHEMA IF NOT EXISTS bronze;")


    create_raw_inat_view(conn)
    
    conn.close()


if __name__ == "__main__":
    main()