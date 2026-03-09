
import json
import os
from dotenv import load_dotenv
import psycopg


load_dotenv()  
DATABASE_URL = os.getenv("DATABASE_URL")

def _get_connection():
    """Establish a connection to the PostgreSQL database."""
    if DATABASE_URL is None:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return psycopg.connect(DATABASE_URL)

def ensure_table():
    """Create the drive_config table if it doesn't exist."""
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS drive_config (
                id SERIAL PRIMARY KEY,
                config_json JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)

def load_db_config():
    """Load the latest drive configuration from the database."""
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT config_json 
                        FROM drive_config
                        ORDER BY created_at DESC
                        LIMIT 1;
                        """)
            row = cur.fetchone()
            if row:
                return row[0]  # Return the JSON config
            return None  # No config found

def save_db_config(config):
    """Save the drive configuration to the database."""
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO drive_config (config_json) VALUES (%s)", 
                (json.dumps(config),)
                )