# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : sqlite_inventory_repo.py
# @Software: AstrBot
# @Description: 玩家库存相关的数据库操作

import sqlite3
from typing import List, Tuple

from astrbot_plugin_sanguo_rpg.core.domain.models import Item

class InventoryRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _create_connection(self):
        return sqlite3.connect(self.db_path)

    def add_item_to_inventory(self, user_id: str, item_id: int, quantity: int = 1):
        """向玩家库存中添加物品"""
        conn = self._create_connection()
        c = conn.cursor()
        try:
            # 检查物品是否已存在
            c.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            result = c.fetchone()
            
            if result:
                # 更新数量
                new_quantity = result[0] + quantity
                c.execute("UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?", (new_quantity, user_id, item_id))
            else:
                # 插入新记录
                c.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)", (user_id, item_id, quantity))
            
            conn.commit()
        finally:
            conn.close()

    def remove_item_from_inventory(self, user_id: str, item_id: int, quantity: int = 1) -> bool:
        """从玩家库存中移除物品"""
        conn = self._create_connection()
        c = conn.cursor()
        try:
            c.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            result = c.fetchone()

            if not result or result[0] < quantity:
                return False  # 物品不存在或数量不足

            new_quantity = result[0] - quantity
            if new_quantity > 0:
                c.execute("UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?", (new_quantity, user_id, item_id))
            else:
                c.execute("DELETE FROM inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            
            conn.commit()
            return True
        finally:
            conn.close()

    def get_user_inventory(self, user_id: str) -> List[Tuple[Item, int]]:
        """获取玩家的所有物品及其数量"""
        conn = self._create_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute('''
            SELECT i.*, inv.quantity
            FROM inventory inv
            JOIN items i ON inv.item_id = i.id
            WHERE inv.user_id = ?
        ''', (user_id,))
        
        items = []
        for row in c.fetchall():
            item = Item.from_row(row)
            items.append((item, row['quantity']))
            
        conn.close()
        return items
