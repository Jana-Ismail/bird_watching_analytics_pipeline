from src.utils.storage_utils import create_duckdb_s3_conn

def create_raw_ebird_daily_view(conn):
    with open('src/sql/raw_views/raw_ebird.sql', 'r') as file:
        conn.execute(file.read())

def main():
    duckdb_db = ':memory:'
    # duckdb_db = '/Users/janaismail/workspace/de_2025/capstone/bird_sighting_analytics_pipeline/data/ducklake/bird_sightings.ducklake'
    conn = create_duckdb_s3_conn(duckdb_db)
    conn.execute("CREATE SCHEMA IF NOT EXISTS bronze;")
    # df = conn.execute("""SELECT * FROM information_schema.schemata;""").df()
    # print(df)
    create_raw_ebird_daily_view(conn)
    conn.close()


if __name__ == "__main__":
    main()
    