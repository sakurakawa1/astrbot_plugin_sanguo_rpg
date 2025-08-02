def up(cursor):
    # Add the log_type column to the battle_logs table
    cursor.execute("""
    ALTER TABLE battle_logs
    ADD COLUMN log_type TEXT
    """)

def down(cursor):
    # SQLite does not support dropping columns directly.
    # The process involves creating a new table without the column,
    # copying the data, dropping the old table, and renaming the new one.
    cursor.execute("""
    CREATE TABLE battle_logs_new (
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
    cursor.execute("""
    INSERT INTO battle_logs_new (log_id, user_id, user_general_instance_id, enemy_name, is_win, log_details, rewards, created_at)
    SELECT log_id, user_id, user_general_instance_id, enemy_name, is_win, log_details, rewards, created_at
    FROM battle_logs
    """)
    cursor.execute("DROP TABLE battle_logs")
    cursor.execute("ALTER TABLE battle_logs_new RENAME TO battle_logs")
