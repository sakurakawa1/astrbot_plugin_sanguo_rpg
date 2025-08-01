# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : 003_add_adventure_fields_to_users.py
# @Software: AstrBot
# @Description: 为 users 表添加冒险所需的新字段

def column_exists(cursor, table_name, column_name):
    """检查表中是否存在指定的列"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def upgrade(cursor):
    """
    升级数据库
    """
    table_name = "users"
    columns_to_add = {
        "reputation": "INTEGER NOT NULL DEFAULT 0",
        "health": "INTEGER NOT NULL DEFAULT 100",
        "status": "TEXT NOT NULL DEFAULT '正常'"
    }

    for column, definition in columns_to_add.items():
        if not column_exists(cursor, table_name, column):
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {definition};")

def downgrade(cursor):
    """
    降级数据库 (注意: SQLite 不支持直接移除列，这里是象征性的)
    """
    # SQLite 不支持简单地 DROP COLUMN。
    # 在生产环境中，这通常需要创建一个新表，复制数据，然后重命名。
    # 对于此插件，我们暂时不实现降级逻辑。
    pass
