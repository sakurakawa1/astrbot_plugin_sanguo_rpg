# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : sqlite_item_repo.py
# @Software: AstrBot
# @Description: 物品相关的数据库操作

import json
import sqlite3
from typing import List, Optional

from astrbot_plugin_sanguo_rpg.core.domain.models import Item


class ItemRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _create_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_item(self, row: sqlite3.Row) -> Optional[Item]:
        if not row:
            return None
        
        effects = None
        if row['effects']:
            try:
                effects = json.loads(row['effects'])
            except (json.JSONDecodeError, TypeError):
                effects = {}  # or handle error appropriately
        
        return Item(
            id=row['id'],
            name=row['name'],
            type=row['type'],
            quality=row['quality'],
            description=row['description'],
            effects=effects,
            is_consumable=bool(row['is_consumable']),
            base_price_coins=row['base_price_coins'],
            base_price_yuanbao=row['base_price_yuanbao']
        )

    def get_all_items(self) -> List[Item]:
        """获取所有物品"""
        conn = self._create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM items")
        rows = c.fetchall()
        conn.close()
        return [self._row_to_item(row) for row in rows if self._row_to_item(row) is not None]

    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """通过ID获取物品"""
        conn = self._create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = c.fetchone()
        conn.close()
        return self._row_to_item(row)

    def get_names_by_ids(self, item_ids: List[int]) -> List[str]:
        """通过ID列表获取物品名称列表"""
        if not item_ids:
            return []
        
        conn = self._create_connection()
        c = conn.cursor()
        
        placeholders = ','.join('?' for _ in item_ids)
        query = f"SELECT name FROM items WHERE id IN ({placeholders})"
        
        c.execute(query, item_ids)
        rows = c.fetchall()
        conn.close()
        
        return [row['name'] for row in rows]
