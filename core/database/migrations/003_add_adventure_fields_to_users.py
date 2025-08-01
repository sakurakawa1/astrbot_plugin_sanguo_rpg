# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : 003_add_adventure_fields_to_users.py
# @Software: AstrBot
# @Description: 为 users 表添加冒险所需的新字段

def upgrade(cursor):
    """
    升级数据库
    """
    # 使用安全的方式添加新列，避免在列已存在时出错
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN reputation INTEGER NOT NULL DEFAULT 0;")
    except Exception:
        pass  # 列可能已存在

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN health INTEGER NOT NULL DEFAULT 100;")
    except Exception:
        pass  # 列可能已存在

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT '正常';")
    except Exception:
        pass  # 列可能已存在

def downgrade(cursor):
    """
    降级数据库 (注意: SQLite 不支持直接移除列，这里是象征性的)
    """
    # SQLite 不支持简单地 DROP COLUMN。
    # 在生产环境中，这通常需要创建一个新表，复制数据，然后重命名。
    # 对于此插件，我们暂时不实现降级逻辑。
    pass
