# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 008_create_items_and_inventory_tables.py
# @Software: AstrBot
# @Description: 创建装备和玩家背包表

def up(cursor):
    # 1. 创建 items 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            quality TEXT NOT NULL,
            description TEXT,
            effect_type TEXT,
            effect_value INTEGER,
            is_consumable BOOLEAN NOT NULL,
            base_price_coins INTEGER NOT NULL,
            base_price_yuanbao INTEGER NOT NULL
        );
    ''')

    # 2. 创建 user_inventory 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (item_id) REFERENCES items (id)
        );
    ''')
    
    # 创建索引以提高查询效率
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_inventory_user_id ON user_inventory (user_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_quality ON items (quality);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_type ON items (type);')

def down(cursor):
    cursor.execute('DROP TABLE IF EXISTS user_inventory;')
    cursor.execute('DROP TABLE IF EXISTS items;')
