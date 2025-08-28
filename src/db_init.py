# Buradaki amaç sql dosyalarını okuyup database.db (sqlite dosyasına) uygulamak

from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1] #dosyanın ana pathini bulmak için
db_path = ROOT / "data" / "database.db" #database'in yükleneceği yer
schema = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8") #schema sql dosyası
indexes = (ROOT / "sql" / "indexes.sql").read_text(encoding="utf-8") #index sql dosyası
seed_companies = (ROOT / "sql" / "seed_companies.sql").read_text(encoding="utf-8") #index sql dosyası


with sqlite3.connect(db_path) as conn:
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(schema)
    conn.executescript(indexes)
    conn.executescript(seed_companies)
print(f"Initialized {db_path}")
