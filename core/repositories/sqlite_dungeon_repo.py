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
            cursor.execute("SELECT id, name, description, recommended_level, enemy_strength_min, enemy_strength_max, rewards FROM dungeons ORDER BY recommended_level")
            rows = cursor.fetchall()
            
            dungeons = []
            for row in rows:
                import json
                rewards_dict = json.loads(row[6]) if row[6] else {}
                dungeons.append(Dungeon(
                    dungeon_id=row[0],
                    name=row[1],
                    description=row[2],
                    recommended_level=row[3],
                    enemy_strength_min=row[4],
                    enemy_strength_max=row[5],
                    rewards=rewards_dict
                ))
            return dungeons

    def get_dungeon_by_id(self, dungeon_id: int) -> Optional[Dungeon]:
        """根据ID获取单个副本信息"""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, recommended_level, enemy_strength_min, enemy_strength_max, rewards FROM dungeons WHERE id = ?", (dungeon_id,))
            row = cursor.fetchone()
            
            if row:
                import json
                rewards_dict = json.loads(row[6]) if row[6] else {}
                return Dungeon(
                    dungeon_id=row[0],
                    name=row[1],
                    description=row[2],
                    recommended_level=row[3],
                    enemy_strength_min=row[4],
                    enemy_strength_max=row[5],
                    rewards=rewards_dict
                )
            return None

    def get_dungeon_by_name(self, name: str) -> Optional[Dungeon]:
        """根据名称获取单个副本信息"""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, recommended_level, enemy_strength_min, enemy_strength_max, rewards FROM dungeons WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if row:
                import json
                rewards_dict = json.loads(row[6]) if row[6] else {}
                return Dungeon(
                    dungeon_id=row[0],
                    name=row[1],
                    description=row[2],
                    recommended_level=row[3],
                    enemy_strength_min=row[4],
                    enemy_strength_max=row[5],
                    rewards=rewards_dict
                )
            return None
