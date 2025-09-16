import streamlit as st
import duckdb

DUCKLAKE_PATH = 'data/ducklake/bird_sightings.ducklake'
from src.config.app_settings import (
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_DUCKDB_S3_ENDPOINT
)

@st.cache_resource
def get_connection():
    conn = duckdb.connect(database=':memory:')
    conn.execute("INSTALL ducklake;")
    conn.execute("LOAD ducklake;")
    conn.execute(f"ATTACH 'ducklake:{DUCKLAKE_PATH}' AS bird_ducklake;")
    conn.execute("USE bird_ducklake;")

    conn.execute("INSTALL httpfs;")
    conn.execute("LOAD httpfs;")
    conn.execute(f"SET s3_endpoint='{MINIO_DUCKDB_S3_ENDPOINT}'")
    conn.execute(f"SET s3_access_key_id='{MINIO_ACCESS_KEY}'")
    conn.execute(f"SET s3_secret_access_key='{MINIO_SECRET_KEY}'")
    conn.execute("SET s3_use_ssl=false")
    conn.execute("SET s3_region='us-east-1'")
    conn.execute("SET s3_url_style='path'")
    
    return conn

try:
    conn = get_connection()
except Exception as e:
    st.error(f"Could not connect to DuckLake catalog: {e}")
    st.stop()

st.title("Bird Sighting Analytics")

schemas = conn.execute("""SELECT schema_name FROM information_schema.schemata;""").fetchdf()
# st.write("DuckLake Schemas:", schemas)

tables = conn.execute("""
                      SELECT table_schema, table_name
                      FROM information_schema.tables
                      WHERE table_schema = 'silver'""").fetchdf()

# st.write("Silver Schema Tables:", tables)

inat_species_count = conn.execute("""
                  SELECT species_guess, observed_on, COUNT(*) as total_sightings
                  FROM bird_ducklake.silver.clean_inat
                  GROUP BY species_guess, observed_on
                  ORDER BY observed_on DESC
                  LIMIT 10;
""").fetchdf()

# st.line_chart(inat_species_count.set_index('observed_on')['total_sightings'])

# Bar chart
st.subheader("Bar Chart")
st.bar_chart(inat_species_count.set_index('species_guess')['total_sightings'])

recent_species_location = conn.execute("""
                SELECT * 
                FROM bird_ducklake.silver.clean_ebird
                            
                             """).fetchdf()

st.header("Recent Species Locations")
st.map(recent_species_location)

weather_stats = conn.execute("""
    
""")