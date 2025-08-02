# -*- coding: utf-8 -*-
# @Time    : 2025/07/29
# @Author  : Cline
# @File    : 002_add_exp_to_users.py
# @Software: AstrBot
# @Description: Add exp column to users table

def up(cursor):
    """
    升级数据库
    """
    # 检查列是否存在
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'exp' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN exp INTEGER DEFAULT 0")

def down(cursor):
    """
    降级数据库
    """
    # SQLite doesn't directly support dropping columns in a simple way.
    # For a real-world scenario, this would involve creating a new table,
    # copying data, dropping the old table, and renaming the new one.
    # For this plugin, we'll assume migrations are forward-only during development.
    pass
