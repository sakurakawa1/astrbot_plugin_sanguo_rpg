# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 016_add_last_adventure_time_to_users.py
# @Software: AstrBot
# @Description: Add last_adventure_time to users table

def up(cursor):
    """
    Adds the last_adventure_time column to the users table.
    """
    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'last_adventure_time' not in columns:
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN last_adventure_time TIMESTAMP
            """)
            print("Column 'last_adventure_time' added to 'users' table.")
        else:
            print("Column 'last_adventure_time' already exists in 'users' table.")
    except Exception as e:
        print(f"Error upgrading database: {e}")
        # Optionally re-raise or handle the error
        raise

def down(cursor):
    """
    Removes the last_adventure_time column from the users table.
    This is not safely supported in SQLite, so we will skip it.
    """
    # SQLite does not support dropping columns directly in a simple way.
    # The recommended approach is to create a new table, copy data, and rename.
    # For simplicity in this context, we will just print a message.
    print("Downgrade for '016_add_last_adventure_time_to_users.py' is not implemented due to SQLite limitations.")
    pass
