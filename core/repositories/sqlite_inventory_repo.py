# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : sqlite_inventory_repo.py
# @Software: AstrBot
# @Description: 玩家库存相关的数据库操作

import json
import sqlite3
from typing import List, Optional, Tuple

from astrbot_plugin_sanguo_rpg.core.domain.models import InventoryItem, Item


class InventoryRepository:
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
                effects = {}
        
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

    def add_item_to_inventory(self, user_id: str, item_id: int, quantity: int = 1):
        """向玩家库存中添加物品"""
        conn = self._create_connection()
        c = conn.cursor()
        try:
            c.execute("SELECT quantity FROM user_inventory WHERE user_id = ? AND item_id = ?", (user_id, item_id))
            result = c.fetchone()
            
            if result:
                new_quantity = result[0] + quantity
                c.execute("UPDATE user_inventory SET quantity = ? WHERE user_id = ? AND item_id = ?", (new_quantity, user_id, item_id))
            else:
                c.execute("INSERT INTO user_inventory (user_id, item_id, quantity) VALUES (?, ?, ?)", (user_id, item_id, quantity))
            
            conn.commit()
        finally:
            conn.close()

    def remove_item_from_inventory(self, inventory_id: int, quantity: int = 1) -> bool:
        """通过库存ID从玩家库存中移除物品"""
        conn = self._create_connection()
        c = conn.cursor()
        try:
            c.execute("SELECT quantity FROM user_inventory WHERE id = ?", (inventory_id,))
            result = c.fetchone()

            if not result or result[0] < quantity:
                return False

            new_quantity = result[0] - quantity
            if new_quantity > 0:
                c.execute("UPDATE user_inventory SET quantity = ? WHERE id = ?", (new_quantity, inventory_id))
            else:
                c.execute("DELETE FROM user_inventory WHERE id = ?", (inventory_id,))
            
            conn.commit()
            return True
        finally:
            conn.close()

    def get_user_inventory(self, user_id: str) -> List[InventoryItem]:
        """获取玩家的所有物品及其数量"""
        conn = self._create_connection()
        c = conn.cursor()

        c.execute('''
            SELECT ui.id as inventory_id, ui.quantity, i.*, ui.instance_properties
            FROM user_inventory ui
            JOIN items i ON ui.item_id = i.id
            WHERE ui.user_id = ?
        ''', (user_id,))
        
        inventory_items = []
        for row in c.fetchall():
            item = self._row_to_item(row)
            if item:
                instance_properties = {}
                if row['instance_properties']:
                    try:
                        instance_properties = json.loads(row['instance_properties'])
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                inventory_item = InventoryItem(
                    inventory_id=row['inventory_id'],
                    user_id=user_id,
                    item_id=item.id,
                    quantity=row['quantity'],
                    item=item,
                    instance_properties=instance_properties
                )
                inventory_items.append(inventory_item)
            
        conn.close()
        return inventory_items

    def get_item_in_inventory(self, user_id: str, item_id: int) -> Optional[InventoryItem]:
        """获取玩家背包中指定ID的物品"""
        conn = self._create_connection()
        c = conn.cursor()

        c.execute('''
            SELECT ui.id as inventory_id, ui.quantity, i.*
            FROM user_inventory ui
            JOIN items i ON ui.item_id = i.id
            WHERE ui.user_id = ? AND ui.item_id = ?
        ''', (user_id, item_id))
        
        row = c.fetchone()
        conn.close()

        if row:
            item = self._row_to_item(row)
            if item:
                return InventoryItem(
                    inventory_id=row['inventory_id'],
                    user_id=user_id,
                    item_id=item.id,
                    quantity=row['quantity'],
                    item=item
                )
        return None

    def get_item_in_inventory_by_instance_id(self, inventory_id: int) -> Optional[InventoryItem]:
        """通过库存ID获取单个物品实例"""
        conn = self._create_connection()
        c = conn.cursor()

        c.execute('''
            SELECT ui.id as inventory_id, ui.user_id, ui.quantity, i.*, ui.instance_properties
            FROM user_inventory ui
            JOIN items i ON ui.item_id = i.id
            WHERE ui.id = ?
        ''', (inventory_id,))
        
        row = c.fetchone()
        conn.close()

        if row:
            item = self._row_to_item(row)
            if item:
                instance_properties = {}
                if row['instance_properties']:
                    try:
                        instance_properties = json.loads(row['instance_properties'])
                    except (json.JSONDecodeError, TypeError):
                        pass

                return InventoryItem(
                    inventory_id=row['inventory_id'],
                    user_id=row['user_id'],
                    item_id=item.id,
                    quantity=row['quantity'],
                    item=item,
                    instance_properties=instance_properties
                )
        return None
