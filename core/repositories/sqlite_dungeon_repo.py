# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : sqlite_dungeon_repo.py
# @Software: AstrBot
# @Description: 副本数据仓库

import sqlite3
from typing import List, Optional
from ..domain.models import Dungeon

class DungeonRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _create_connection(self):
        return sqlite3.connect(self.db_path)

    def get_all_dungeons(self) -> List[Dungeon]:
        """获取所有副本信息"""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, recommended_level, entry_fee, rewards FROM dungeons ORDER BY recommended_level")
            rows = cursor.fetchall()
            
            dungeons = []
            for row in rows:
                # The rewards are stored as a JSON string, so we need to parse them.
                # For simplicity, we'll assume the service layer handles JSON parsing if needed,
                # or we can do it here. Let's assume the model expects a dict.
                import json
                rewards_dict = json.loads(row[5]) if row[5] else {}
                dungeons.append(Dungeon(
                    dungeon_id=row[0],
                    name=row[1],
                    description=row[2],
                    recommended_level=row[3],
                    entry_fee=row[4],
                    rewards=rewards_dict
                ))
            return dungeons

    def get_dungeon_by_name(self, name: str) -> Optional[Dungeon]:
        """根据名称获取单个副本信息"""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, recommended_level, entry_fee, rewards FROM dungeons WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if row:
                import json
                rewards_dict = json.loads(row[5]) if row[5] else {}
                return Dungeon(
                    dungeon_id=row[0],
                    name=row[1],
                    description=row[2],
                    recommended_level=row[3],
                    entry_fee=row[4],
                    rewards=rewards_dict
                )
            return None
