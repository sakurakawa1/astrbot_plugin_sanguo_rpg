# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : sqlite_shop_repo.py
# @Software: AstrBot
# @Description: 商店相关的数据库操作

import sqlite3
import random
from datetime import date
from typing import List, Optional, Tuple

from astrbot_plugin_sanguo_rpg.core.domain.models import Item

class ShopRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _create_connection(self):
        return sqlite3.connect(self.db_path)

    def get_today_shop_items(self) -> List[Tuple[int, Item, int]]:
        """
        获取今天商店中所有在售的商品。
        返回一个元组列表: (shop_item_id, Item对象, remaining_quantity)
        """
        today = date.today().isoformat()
        conn = self._create_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute('''
            SELECT si.id as shop_item_id, si.remaining_quantity, i.*
            FROM shop_items si
            JOIN items i ON si.item_id = i.id
            WHERE si.date = ? AND si.remaining_quantity > 0
        ''', (today,))
        
        items = []
        for row in c.fetchall():
            item = Item.from_row(row)
            items.append((row['shop_item_id'], item, row['remaining_quantity']))
            
        conn.close()
        return items

    def get_shop_item_by_id(self, shop_item_id: int) -> Optional[Tuple[Item, int]]:
        """
        通过商店商品ID获取商品详情和剩余数量。
        返回 (Item对象, 剩余数量) 或 None
        """
        conn = self._create_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute('''
            SELECT i.*, si.remaining_quantity
            FROM shop_items si
            JOIN items i ON si.item_id = i.id
            WHERE si.id = ?
        ''', (shop_item_id,))
        
        row = c.fetchone()
        conn.close()
        
        if row:
            return Item.from_row(row), row['remaining_quantity']
        return None

    def decrease_shop_item_quantity(self, shop_item_id: int, quantity: int = 1) -> bool:
        """减少商店商品的数量"""
        conn = self._create_connection()
        c = conn.cursor()
        try:
            c.execute('''
                UPDATE shop_items
                SET remaining_quantity = remaining_quantity - ?
                WHERE id = ? AND remaining_quantity >= ?
            ''', (quantity, shop_item_id, quantity))
            
            if c.rowcount > 0:
                conn.commit()
                return True
            else:
                conn.rollback()
                return False
        finally:
            conn.close()

    def refresh_shop(self, limit: int = 10):
        """
        刷新当天的商店商品。
        该方法会清空当天的旧商品，然后从所有物品中随机抽取指定数量的新商品上架。
        """
        today = date.today().isoformat()
        conn = self._create_connection()
        c = conn.cursor()
        try:
            # 1. 清空当天的商店记录
            c.execute("DELETE FROM shop_items WHERE date = ?", (today,))

            # 2. 从 items 表中随机获取所有可用的 item_id
            c.execute("SELECT id FROM items")
            all_item_ids = [row[0] for row in c.fetchall()]
            
            # 如果物品总数少于限制，则全部上架
            limit = min(len(all_item_ids), limit)
            
            # 3. 随机选择指定数量的商品
            selected_item_ids = random.sample(all_item_ids, limit)

            # 4. 为选中的商品准备插入数据，随机生成数量
            items_to_insert = [
                (item_id, random.randint(1, 5), today)
                for item_id in selected_item_ids
            ]

            # 5. 插入新的商品记录
            c.executemany('''
                INSERT INTO shop_items (item_id, remaining_quantity, date)
                VALUES (?, ?, ?)
            ''', items_to_insert)

            conn.commit()
        except Exception as e:
            conn.rollback()
            # 在实际应用中，这里应该记录日志
            raise e
        finally:
            conn.close()
