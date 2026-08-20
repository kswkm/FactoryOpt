"""
One-time migration: CSV -> PostgreSQL
"""
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / 'machine_uptime_export.csv'

engine = create_engine(os.environ.get("DB_URL"))

df = pd.read_csv(CSV_FILE)
df.to_sql('machine_uptime', engine, if_exists='replace', index=False)

print(f"✅ Migrated {len(df)} rows from {CSV_FILE.name} into 'machine_uptime' table")
