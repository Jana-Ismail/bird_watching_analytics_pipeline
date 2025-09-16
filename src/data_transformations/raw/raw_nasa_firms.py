from src.utils.storage_utils import create_duckdb_s3_conn

def create_raw_nasa_firms_view(conn):
    with open('src/sql/raw_views/raw_nasa_firms.sql', 'r') as file:
        conn.execute(file.read())

def main():
    duckdb_db = ':memory:'
    conn = create_duckdb_s3_conn(duckdb_db)

    create_raw_nasa_firms_view(conn)
    conn.close()


if __name__ == "__main__":
    main()