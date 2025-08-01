# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 009_create_shop_items_table.py
# @Software: AstrBot
# @Description: 创建商店商品表

def upgrade(conn):
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS shop_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            remaining_quantity INTEGER NOT NULL DEFAULT 1,
            date DATE NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (id)
        );
    ''')

    # 创建索引
    c.execute('CREATE INDEX IF NOT EXISTS idx_shop_items_date ON shop_items (date);')

    conn.commit()

def downgrade(conn):
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS shop_items;')
    conn.commit()
