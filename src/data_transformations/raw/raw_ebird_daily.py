from src.utils.storage_utils import attach_ducklake

def create_raw_ebird_daily_view(conn):
    with open('src/sql/raw/ebird_daily_view.sql', 'r') as file:
        conn.execute(file.read())

def main():
    duckdb_db = ':memory:'
    conn = attach_ducklake(duckdb_db)
    conn.execute("CREATE SCHEMA IF NOT EXISTS bronze;")
    # df = conn.execute("""SELECT * FROM information_schema.schemata;""").df()
    # print(df)
    create_raw_ebird_daily_view(conn)
    conn.close()


if __name__ == "__main__":
    main()
    