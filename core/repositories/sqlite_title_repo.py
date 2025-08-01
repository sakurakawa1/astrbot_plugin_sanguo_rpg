# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : sqlite_title_repo.py
# @Software: AstrBot
# @Description: 称号数据仓储实现

import sqlite3
from typing import List, Optional
from astrbot_plugin_sanguo_rpg.core.domain.models import Title

class SqliteTitleRepository:
    def __init__(self, db_path):
        self.db_path = db_path

    def _create_connection(self):
        return sqlite3.connect(self.db_path)

    def get_all_titles(self) -> List[Title]:
        with self._create_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, required_reputation FROM titles ORDER BY required_reputation ASC")
            rows = cursor.fetchall()
            return [Title(row["id"], row["name"], row["required_reputation"]) for row in rows]

    def get_title_by_name(self, name: str) -> Optional[Title]:
        with self._create_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, required_reputation FROM titles WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return Title(row["id"], row["name"], row["required_reputation"])
            return None
