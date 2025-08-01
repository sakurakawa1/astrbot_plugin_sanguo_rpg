# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : sqlite_shop_repo.py
# @Software: AstrBot
# @Description: 商店相关的数据库操作

import sqlite3
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

    def has_refreshed_today(self) -> bool:
        """检查今天是否已经刷新过商店"""
        today = date.today().isoformat()
        conn = self._create_connection()
        c = conn.cursor()
        c.execute("SELECT 1 FROM shop_items WHERE date = ?", (today,))
        result = c.fetchone()
        conn.close()
        return result is not None

    def refresh_shop(self, item_ids_with_quantities: List[Tuple[int, int]]):
        """
        用新的商品列表刷新商店。
        :param item_ids_with_quantities: 一个元组列表 [(item_id, quantity), ...]
        """
        today = date.today().isoformat()
        conn = self._create_connection()
        c = conn.cursor()
        try:
            # 为防止重复执行，可以先删除当天的记录，但更安全的做法是在服务层检查
            # c.execute("DELETE FROM shop_items WHERE date = ?", (today,))
            
            items_to_insert = [
                (item_id, quantity, today)
                for item_id, quantity in item_ids_with_quantities
            ]
            
            c.executemany('''
                INSERT INTO shop_items (item_id, remaining_quantity, date)
                VALUES (?, ?, ?)
            ''', items_to_insert)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
