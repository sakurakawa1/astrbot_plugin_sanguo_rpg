# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : 004_add_title_to_users_and_create_titles_table.py
# @Software: AstrBot
# @Description: 添加称号到用户表并创建称号表

def upgrade(cursor):
    # 1. 检查 users 表中是否已存在 title 列
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'title' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN title TEXT")

    # 2. 创建 titles 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS titles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        required_reputation INTEGER NOT NULL DEFAULT 0
    )
    """)

    # 3. 插入默认的称号数据
    default_titles = [
        ('初出茅庐', 100),
        ('小有名气', 500),
        ('声名鹊起', 2000),
        ('威震一方', 5000),
        ('名扬四海', 10000)
    ]
    
    # 使用 IGNORE 防止重复插入
    cursor.executemany("INSERT OR IGNORE INTO titles (name, required_reputation) VALUES (?, ?)", default_titles)
    
    cursor.connection.commit()

def downgrade(cursor):
    
    # 在降级时，我们只移除 titles 表，而不从 users 表中删除列，以防数据丢失
    # 如果需要，可以取消下面的注释来删除列
    # cursor.execute("ALTER TABLE users DROP COLUMN title")
    
    cursor.execute("DROP TABLE IF EXISTS titles")
    
    cursor.connection.commit()
