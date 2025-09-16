from src.utils.storage_utils import create_duckdb_s3_conn

def clean_ebird(conn):
    with open('src/sql/cleaning_tables/clean_ebird.sql', 'r') as file:
        conn.execute(file.read())

def main():
    duckdb_db = ':memory:'
    # duckdb_db = '/Users/janaismail/workspace/de_2025/capstone/bird_sighting_analytics_pipeline/data/ducklake/bird_sightings.ducklake'
    conn = create_duckdb_s3_conn(duckdb_db)

    clean_ebird(conn)
    
    conn.close()

if __name__ == "__main__":
    main()
