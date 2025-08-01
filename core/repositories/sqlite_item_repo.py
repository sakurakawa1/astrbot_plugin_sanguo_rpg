# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : sqlite_item_repo.py
# @Software: AstrBot
# @Description: 物品相关的数据库操作

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

    def get_all_items(self) -> List[Item]:
        """获取所有物品"""
        conn = self._create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM items")
        rows = c.fetchall()
        conn.close()
        return [Item.from_row(row) for row in rows]

    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """通过ID获取物品"""
        conn = self._create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return Item.from_row(row)
        return None
