# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 018_add_last_steal_time_to_users.py
# @Software: AstrBot
# @Description: 添加最后偷窃时间到用户表

def up(cursor):
    # 检查列是否已存在
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'last_steal_time' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN last_steal_time TIMESTAMP")

def down(cursor):
    # SQLite 不直接支持 DROP COLUMN，需要通过重建表的方式实现
    # 为简化，此处仅作记录，实际生产中可能需要更复杂的降级策略
    pass
