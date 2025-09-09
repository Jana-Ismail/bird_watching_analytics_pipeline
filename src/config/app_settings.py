import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

# Logging Credentials
LOG_DIR = PROJECT_ROOT / 'logs'
LOG_FILE = LOG_DIR / 'bird_watching_analytics_pipeline.log'

# California Region Credentials
CA_REGION_CODE = 'US-CA'
# Note: rename to CA_BBOX_COORDINATES for clarity
CA_BBOX_COORDINATES = '-124.48,32.53,-114.13,42.01'  # SW longitude, SW latitude, NE longitude, NE  # minX,minY,maxX,maxY
CA_HOTSPOTS_BBOX_COORDINATES = '-123.00,35.3,-118.90,40.00'

CA_HOTSPOTS_BY_BBOX_COORDINATES = {
  "sacramento_valley": '-122.50,38.90,-121.30,40.00',
  "san_francisco_bay_suisun_marsh": '-123.00,37.30,-121.70,38.30',
  "san_joaquin_valley_grasslands": '-121.20,36.70,-120.20,37.40',
  "monterey_bay_central_coast": '-122.20,36.60,-121.30,37.10',
  "tulare_basin": '-120.80,35.30,-118.90,36.60'
}

CA_HOTSPOTS_BY_CENTER_POINT_COORDINATES = {
  "sacramento_valley": '39.45,-121.90',
  "san_francisco_bay_suisun_marsh": '37.80,-122.35',
  "san_joaquin_valley_grasslands": '37.05,-120.70',
  "monterey_bay_central_coast": '36.85,-121.75',
  "tulare_basin": '35.95,-119.85'
}

CA_BIRD_SPECIES_GENERAL = [
    'sparrow', 'finch', 'warbler', 'swallow', 'oriole', 'grosbeak', 'thrasher', 'wren', 'vireo',
    'woodpecker', 'flycatcher', 'cuckoo', 'nuthatch', 'titmouse', 'chickadee', 'kinglet', 'creeper',
    'robin', 'bluebird', 'thrush', 'mockingbird', 'catbird', 'starling', 'pipit', 'waxwing',
    'heron', 'egret', 'bittern', 'ibis', 'spoonbill',
    'duck', 'goose', 'swan',
    'gull', 'tern', 'auk',
    'hawk', 'eagle', 'falcon',
    'quail', 'grouse',
    'tanager', 'hummingbird', 'raptor'
    # Add more general bird species as needed
]

CA_BIRD_SPECIES_LIMITED = [
    'raptor', 'waterfowl', 'shorebird', 'songbird',
    'heron', 'egret', 'warbler', 'swallow', 'tanager', 'hummingbird'
]


# Ebird API Credentials
EBIRD_API_KEY = os.getenv('EBIRD_API_KEY')
EBIRD_BASE_URL = os.getenv('EBIRD_BASE_URL')


EBIRD_ENDPOINTS = {
    'taxonomy': '/ref/taxonomy/ebird',
    'regional_hotspots': '/ref/hotspot/{{regionCode}}',
    'hotspot_information': '/ref/hotspot/info/{{locId}}',
    'region_info': '/ref/region/info/{{regionCode}}'
}

# California bird migration/watching hotspots (latitude, longitude, radius_km)
# CA_BIRD_HOTSPOTS = {
#     'point_reyes': {'latitude': 38.0469, 'longitude': -122.8681, 'radius_km': 15},
#     'monterey_bay': {'latitude': 36.6002, 'longitude': -121.8947, 'radius_km': 20},
#     'salton_sea': {'latitude': 33.3039, 'longitude': -115.8375, 'radius_km': 25},
#     'farallon_islands': {'latitude': 37.6961, 'longitude': -123.0014, 'radius_km': 10},
#     'lake_almanor': {'latitude': 40.2419, 'longitude': -121.1253, 'radius_km': 15},
#     'bodega_bay': {'latitude': 38.3318, 'longitude': -123.0436, 'radius_km': 12},
#     'morro_bay': {'latitude': 35.3661, 'longitude': -120.8497, 'radius_km': 15},
#     'lake_merritt': {'latitude': 37.8044, 'longitude': -122.2581, 'radius_km': 8},
#     'san_francisco_bay': {'latitude': 37.6017, 'longitude': -122.2711, 'radius_km': 30},
#     'central_valley': {'latitude': 37.0902, 'longitude': -120.7129, 'radius_km': 40}
# }

BIRDS_TAXON_NAME = 'Aves'

# NASA FIRMS API Credentials
NASA_FIRMS_BASE_URL = 'https://firms.modaps.eosdis.nasa.gov/api/area/csv'
NASA_FIRMS_API_KEY = os.getenv('NASA_FIRMS_API_MAP_KEY')
NASA_FIRMS_DATA_SOURCE = 'MODIS_NRT'
NASA_FIRMS_HISTORICAL_DATA_SOURCE = 'MODIS_SP' # VIIRS_SNPP_SP for higher resolution


# Minio Credentials
MINIO_ENDPOINT = os.getenv('MINIO_URL_HOST_PORT')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
MINIO_RAW_BUCKET_NAME = os.getenv('MINIO_RAW_BUCKET_NAME')
MINIO_WAREHOUSE_BUCKET_NAME = os.getenv('MINIO_WH_BUCKET_NAME')