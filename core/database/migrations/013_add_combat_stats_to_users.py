# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 013_add_combat_stats_to_users.py
# @Software: AstrBot
# @Description: Add attack, defense, and max_health to users table
import sqlite3

def up(cursor: sqlite3.Cursor):
    # Add attack column with a default value of 10
    cursor.execute("""
        ALTER TABLE users ADD COLUMN attack INTEGER NOT NULL DEFAULT 10
    """)
    
    # Add defense column with a default value of 5
    cursor.execute("""
        ALTER TABLE users ADD COLUMN defense INTEGER NOT NULL DEFAULT 5
    """)

    # Add max_health column with a default value of 100
    cursor.execute("""
        ALTER TABLE users ADD COLUMN max_health INTEGER NOT NULL DEFAULT 100
    """)

def down(cursor: sqlite3.Cursor):
    # Recreate the table without the new columns
    cursor.execute("PRAGMA foreign_keys=off;")

    try:
        cursor.execute("""
            CREATE TABLE users_new (
                user_id TEXT PRIMARY KEY,
                nickname TEXT NOT NULL,
                coins INTEGER NOT NULL,
                yuanbao INTEGER NOT NULL,
                exp INTEGER NOT NULL,
                level INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL,
                last_signed_in TIMESTAMP,
                reputation INTEGER DEFAULT 0,
                health INTEGER DEFAULT 100,
                status TEXT DEFAULT '正常',
                title TEXT,
                auto_adventure BOOLEAN DEFAULT FALSE,
                auto_dungeon_id INTEGER,
                pity_4_star_count INTEGER NOT NULL DEFAULT 0,
                pity_5_star_count INTEGER NOT NULL DEFAULT 0
            );
        """)
        
        cursor.execute("""
            INSERT INTO users_new (
                user_id, nickname, coins, yuanbao, exp, level, created_at, 
                last_signed_in, reputation, health, status, title, 
                auto_adventure, auto_dungeon_id, pity_4_star_count, pity_5_star_count
            )
            SELECT 
                user_id, nickname, coins, yuanbao, exp, level, created_at, 
                last_signed_in, reputation, health, status, title, 
                auto_adventure, auto_dungeon_id, pity_4_star_count, pity_5_star_count
            FROM users;
        """)
        
        cursor.execute("DROP TABLE users;")
        cursor.execute("ALTER TABLE users_new RENAME TO users;")

    except Exception as e:
        print(f"Error during down migration: {e}")
        raise e
    finally:
        cursor.execute("PRAGMA foreign_keys=on;")
