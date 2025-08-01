def up(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS battle_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        user_general_instance_id INTEGER NOT NULL,
        enemy_name TEXT NOT NULL,
        is_win BOOLEAN NOT NULL,
        log_details TEXT NOT NULL,
        rewards TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

def down(cursor):
    cursor.execute("DROP TABLE IF EXISTS battle_logs")
