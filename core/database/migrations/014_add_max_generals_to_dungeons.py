# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 014_add_max_generals_to_dungeons.py
# @Software: AstrBot
# @Description: Add max_generals to dungeons table

import sqlite3

def up(cursor: sqlite3.Cursor):
    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(dungeons)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'max_generals' not in columns:
            cursor.execute("""
                ALTER TABLE dungeons ADD COLUMN max_generals INTEGER NOT NULL DEFAULT 3
            """)
    except sqlite3.OperationalError as e:
        # This can happen if the table doesn't exist yet, which is fine
        # as the create script should handle it.
        if "no such table" in str(e):
            pass
        else:
            raise

def down(cursor: sqlite3.Cursor):
    try:
        # Recreate the table without the column
        cursor.execute("PRAGMA foreign_keys=off;")
        cursor.execute("""
            CREATE TABLE dungeons_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                recommended_level INTEGER NOT NULL,
                enemy_strength_min REAL NOT NULL,
                enemy_strength_max REAL NOT NULL,
                rewards TEXT
            );
        """)
        cursor.execute("""
            INSERT INTO dungeons_new (id, name, description, recommended_level, enemy_strength_min, enemy_strength_max, rewards)
            SELECT id, name, description, recommended_level, enemy_strength_min, enemy_strength_max, rewards FROM dungeons;
        """)
        cursor.execute("DROP TABLE dungeons;")
        cursor.execute("ALTER TABLE dungeons_new RENAME TO dungeons;")
        cursor.execute("PRAGMA foreign_keys=on;")
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            pass
        else:
            raise
