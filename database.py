import os
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# This tells Python to open your .env file and read the secret URL
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

# This creates the "bridge" to your Supabase cloud database
engine = create_engine(DB_URL)

def init_db():
    """Creates the table inside Supabase if it doesn't exist yet."""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS price_history (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                platform TEXT NOT NULL,
                model TEXT NOT NULL,
                storage TEXT NOT NULL,
                condition TEXT NOT NULL,
                price REAL NOT NULL,
                in_stock INTEGER NOT NULL,
                url TEXT,
                notes TEXT
            )
        """))
        conn.commit()

def record_price(platform, model, storage, condition, price, in_stock, url="", notes=""):
    """Sends a single scraped price up to Supabase."""
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO price_history (timestamp, platform, model, storage, condition, price, in_stock, url, notes)
            VALUES (:timestamp, :platform, :model, :storage, :condition, :price, :in_stock, :url, :notes)
        """), {
            "timestamp": datetime.now(),
            "platform": platform,
            "model": model,
            "storage": storage,
            "condition": condition,
            "price": price,
            "in_stock": int(in_stock),
            "url": url,
            "notes": notes
        })
        conn.commit()

def load_history():
    """Downloads the history from Supabase to draw your charts."""
    df = pd.read_sql_query("SELECT * FROM price_history ORDER BY timestamp ASC", engine)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def get_latest_snapshot():
    """Downloads only the most recent prices for the dashboard table."""
    query = """
        SELECT * FROM price_history
        WHERE id IN (
            SELECT MAX(id) FROM price_history GROUP BY platform, model, storage
        )
        ORDER BY price ASC
    """
    return pd.read_sql_query(query, engine)

if __name__ == "__main__":
    init_db()
    print("Supabase PostgreSQL initialized successfully.")