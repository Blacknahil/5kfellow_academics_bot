from file_manager.postgres_store import _get_connection

def ensure_analytics_tables():
    with _get_connection() as conn:
        with conn.cursor() as cur:
            # Update daily downloads
            cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL
            );
            """)
            # daily stats
            cur.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                requests INTEGER DEFAULT 0,
                downloads INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0
            );
            """)
            # department usage 
            cur.execute(
            """ CREATE TABLE IF NOT EXISTS department_stats(
                department TEXT PRIMARY KEY,
                downloads INTEGER DEFAULT 0
            );
            """)
    