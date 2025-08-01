# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : sqlite_user_general_repo.py
# @Software: AstrBot
# @Description: User-General relationship repository

import sqlite3
from typing import Optional, List
from ..domain.models import UserGeneral, UserGeneralDetails

class SqliteUserGeneralRepository:
    def __init__(self, db_path):
        self.db_path = db_path

    def _create_connection(self):
        return sqlite3.connect(self.db_path)

    def add(self, user_general: UserGeneral):
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_generals (user_id, general_id, level, exp, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_general.user_id, user_general.general_id, user_general.level, user_general.exp, user_general.created_at)
            )
            conn.commit()

    def get_by_instance_id(self, instance_id: int) -> Optional[UserGeneralDetails]:
        with self._create_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ug.instance_id, ug.user_id, ug.general_id, ug.level, ug.exp, ug.created_at,
                       g.name, g.rarity, g.camp, g.wu_li, g.zhi_li, g.tong_shuai, g.su_du, g.skill_desc
                FROM user_generals ug
                JOIN generals g ON ug.general_id = g.general_id
                WHERE ug.instance_id = ?
            """, (instance_id,))
            row = cursor.fetchone()
            if row:
                return UserGeneralDetails(**row)
            return None

    def get_by_user_id(self, user_id: str) -> List[UserGeneralDetails]:
        with self._create_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ug.instance_id, ug.user_id, ug.general_id, ug.level, ug.exp, ug.created_at,
                       g.name, g.rarity, g.camp, g.wu_li, g.zhi_li, g.tong_shuai, g.su_du, g.skill_desc
                FROM user_generals ug
                JOIN generals g ON ug.general_id = g.general_id
                WHERE ug.user_id = ?
            """, (user_id,))
            rows = cursor.fetchall()
            return [UserGeneralDetails(**row) for row in rows]

    def update(self, user_general: UserGeneralDetails):
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE user_generals SET level = ?, exp = ? WHERE instance_id = ?",
                (user_general.level, user_general.exp, user_general.instance_id),
            )
            conn.commit()

    def count_by_user_id(self, user_id: str) -> int:
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_generals WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return row[0] if row else 0
