# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : 005_add_level_to_users.py
# @Software: AstrBot
# @Description: 为 users 表添加 level 字段

def column_exists(cursor, table_name, column_name):
    """检查表中是否存在指定的列"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def up(cursor):
    """
    升级数据库
    """
    if not column_exists(cursor, "users", "level"):
        cursor.execute("ALTER TABLE users ADD COLUMN level INTEGER NOT NULL DEFAULT 1;")

def down(cursor):
    """
    降级数据库
    """
    # 在此迁移中，我们选择不实现移除 level 列的逻辑，
    # 因为这通常需要重建表，并且在大多数情况下是不必要的。
    pass
