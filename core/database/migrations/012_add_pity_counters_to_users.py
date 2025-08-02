# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 012_add_pity_counters_to_users.py
# @Software: AstrBot
# @Description: 为用户表添加抽卡保底计数器
import sqlite3

def up(cursor: sqlite3.Cursor):
    """
    为 users 表添加 pity_4_star_count 和 pity_5_star_count 列。
    """
    
    # 检查 pity_4_star_count 列是否存在
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'pity_4_star_count' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN pity_4_star_count INTEGER NOT NULL DEFAULT 0;")
        print("Added pity_4_star_count column to users table.")
    
    # 检查 pity_5_star_count 列是否存在
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'pity_5_star_count' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN pity_5_star_count INTEGER NOT NULL DEFAULT 0;")
        print("Added pity_5_star_count column to users table.")
    

def down(cursor: sqlite3.Cursor):
    """
    从 users 表中移除 pity_4_star_count 和 pity_5_star_count 列。
    在 SQLite 中，这通常需要重建表。
    """
    
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
                auto_dungeon_id INTEGER
            );
        """)
        
        cursor.execute("""
            INSERT INTO users_new (
                user_id, nickname, coins, yuanbao, exp, level, created_at, 
                last_signed_in, reputation, health, status, title, 
                auto_adventure, auto_dungeon_id
            )
            SELECT 
                user_id, nickname, coins, yuanbao, exp, level, created_at, 
                last_signed_in, reputation, health, status, title, 
                auto_adventure, auto_dungeon_id
            FROM users;
        """)
        
        cursor.execute("DROP TABLE users;")
        cursor.execute("ALTER TABLE users_new RENAME TO users;")

    except Exception as e:
        print(f"Error during down migration: {e}")
        raise e
    finally:
        cursor.execute("PRAGMA foreign_keys=on;")
