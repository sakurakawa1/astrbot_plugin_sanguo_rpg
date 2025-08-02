def up(cursor):
    """
    Modify battle_logs table to make several columns nullable and ensure log_type exists.
    """
    # Rename the existing table to avoid conflicts
    cursor.execute("ALTER TABLE battle_logs RENAME TO battle_logs_old")

    # Create the new table with the desired schema (nullable columns)
    cursor.execute("""
    CREATE TABLE battle_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        log_type TEXT,
        log_details TEXT NOT NULL,
        user_general_instance_id INTEGER,
        enemy_name TEXT,
        is_win BOOLEAN,
        rewards TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Get the columns of the old table to handle different schemas gracefully
    cursor.execute("PRAGMA table_info(battle_logs_old)")
    old_columns = [row[1] for row in cursor.fetchall()]

    # Define the columns to copy
    columns_to_copy = [
        "log_id", "user_id", "log_details", "user_general_instance_id",
        "enemy_name", "is_win", "rewards", "created_at"
    ]
    
    # Construct the SELECT statement based on existing columns
    select_cols = ", ".join([f'"{col}"' for col in columns_to_copy if col in old_columns])

    # Add log_type to insert if it exists, otherwise add a default value
    if 'log_type' in old_columns:
        insert_cols = f"{select_cols}, log_type"
        select_stmt = f"SELECT {insert_cols} FROM battle_logs_old"
    else:
        insert_cols = f"{select_cols}, log_type"
        select_stmt = f"SELECT {select_cols}, 'dungeon' FROM battle_logs_old"

    # Copy data from the old table to the new one
    cursor.execute(f"INSERT INTO battle_logs ({insert_cols}) {select_stmt}")

    # Remove the old table
    cursor.execute("DROP TABLE battle_logs_old")

def down(cursor):
    """
    Reverts the changes by restoring the previous table structure.
    This is a best-effort reversion and might not perfectly restore the state
    if the original table had a different schema from migration 022.
    """
    cursor.execute("DROP TABLE IF EXISTS battle_logs")
    
    # Recreate the table based on the schema after migration 022
    cursor.execute("""
    CREATE TABLE battle_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        log_type TEXT NOT NULL,
        log_details TEXT NOT NULL,
        user_general_instance_id INTEGER,
        enemy_name TEXT,
        is_win BOOLEAN,
        rewards TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
