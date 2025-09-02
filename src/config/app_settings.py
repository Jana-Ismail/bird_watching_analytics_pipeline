from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

LOG_DIR = PROJECT_ROOT / 'logs'
LOG_FILE = LOG_DIR / 'bird_watching_analytics_pipeline.log'