# -*- coding: utf-8 -*-
# @Time    : 2025/07/29
# @Author  : Cline
# @File    : 002_add_exp_to_users.py
# @Software: AstrBot
# @Description: Add exp column to users table

def upgrade(cursor):
    """
    升级数据库
    """
    # 检查列是否存在
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'exp' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN exp INTEGER DEFAULT 0")

def downgrade(cursor):
    """
    降级数据库
    """
    # SQLite 不支持直接删除列，需要通过创建新表、复制数据、删除旧表、重命名新表的方式实现
    # 为简化操作，此处仅作示例，实际生产环境请谨慎操作
    pass
