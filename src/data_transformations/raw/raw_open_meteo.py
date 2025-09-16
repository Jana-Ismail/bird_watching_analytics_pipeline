from src.utils.storage_utils import create_duckdb_s3_conn

def create_raw_open_meteo_view(conn):
    with open('src/sql/raw_views/raw_open_meteo.sql', 'r') as file:
        conn.execute(file.read())

def main():
    duckdb_db = ':memory:'
    conn = create_duckdb_s3_conn(duckdb_db)

    create_raw_open_meteo_view(conn)
    conn.close()


if __name__ == "__main__":
    main()