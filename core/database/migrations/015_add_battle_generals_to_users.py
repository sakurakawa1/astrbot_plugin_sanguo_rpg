# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 015_add_battle_generals_to_users.py
# @Software: AstrBot
# @Description: 为 users 表添加出战武将字段

def column_exists(cursor, table_name, column_name):
    """检查表中是否存在指定的列"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def up(cursor):
    """
    升级数据库
    """
    table_name = "users"
    columns_to_add = {
        "battle_generals": "TEXT"
    }

    for column, definition in columns_to_add.items():
        if not column_exists(cursor, table_name, column):
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {definition}")

def down(cursor):
    """
    降级数据库
    """
    pass
