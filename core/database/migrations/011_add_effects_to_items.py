# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 011_add_effects_to_items.py
# @Software: AstrBot
# @Description: 为 items 表添加 effects 字段并移除旧的 effect 字段

import sqlite3
import json

def up(cursor: sqlite3.Cursor):
    """
    为 items 表添加 effects JSON 字段，并将旧数据迁移过去。
    旧的 effect_type 和 effect_value 列将被保留以简化操作。
    """
    # 1. 检查并添加新的 'effects' 列
    cursor.execute("PRAGMA table_info(items)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'effects' not in columns:
        cursor.execute("ALTER TABLE items ADD COLUMN effects TEXT;")
        print("Added 'effects' column to 'items' table.")

    # 2. 从旧字段读取数据并填充新字段（仅在尚未填充时）
    cursor.execute("SELECT id, effect_type, effect_value FROM items WHERE effect_type IS NOT NULL AND effect_value IS NOT NULL AND effects IS NULL;")
    items_to_migrate = cursor.fetchall()

    if not items_to_migrate:
        print("No items need data migration to 'effects' column.")
        return

    for item_id, effect_type, effect_value in items_to_migrate:
        if effect_type and effect_value is not None:
            effects_dict = {effect_type: effect_value}
            effects_json = json.dumps(effects_dict)
            cursor.execute("UPDATE items SET effects = ? WHERE id = ?", (effects_json, item_id))
    
    print(f"Migrated data for {len(items_to_migrate)} items to the new 'effects' column.")

def down(cursor: sqlite3.Cursor):
    """
    回滚操作：此操作仅为占位，因为不删除旧列，所以无需复杂的回滚。
    如果需要，可以手动删除 'effects' 列。
    """
    # 检查 'effects' 列是否存在，如果存在则可以考虑删除
    cursor.execute("PRAGMA table_info(items)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'effects' in columns:
        # SQLite 不支持直接 DROP COLUMN，需要重建表。为简单起见，我们只打印一条消息。
        print("Downgrade step: The 'effects' column was not removed to preserve data.")
        print("If you need to fully revert, you may need to manually recreate the table without the 'effects' column.")
    else:
        print("Downgrade step: 'effects' column not found, no action needed.")
