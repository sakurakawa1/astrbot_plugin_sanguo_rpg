# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : sqlite_user_repo.py
# @Software: AstrBot
# @Description: 用户数据仓储实现

import sqlite3
from datetime import datetime
from typing import Optional
from astrbot_plugin_sanguo_rpg.core.domain.models import User

class SqliteUserRepository:
    def __init__(self, db_path):
        self.db_path = db_path

    def _create_connection(self):
        return sqlite3.connect(self.db_path)

    def add(self, user: User):
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (user_id, nickname, coins, yuanbao, created_at, last_signed_in) VALUES (?, ?, ?, ?, ?, ?)",
                (user.user_id, user.nickname, user.coins, user.yuanbao, user.created_at, user.last_signed_in)
            )
            conn.commit()

    def get_by_id(self, user_id: str) -> Optional[User]:
        with self._create_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(
                    user_id=row["user_id"],
                    nickname=row["nickname"],
                    coins=row["coins"],
                    yuanbao=row["yuanbao"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_signed_in=datetime.fromisoformat(row["last_signed_in"]) if row["last_signed_in"] else None
                )
            return None

    def update(self, user: User):
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET nickname = ?, coins = ?, yuanbao = ?, last_signed_in = ? WHERE user_id = ?",
                (user.nickname, user.coins, user.yuanbao, user.last_signed_in, user.user_id)
            )
            conn.commit()
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户信息（别名方法）"""
        return self.get_by_id(user_id)
    
    def update_user_coins(self, user_id: str, coins: int):
        """更新用户铜钱"""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET coins = ? WHERE user_id = ?",
                (coins, user_id)
            )
            conn.commit()
    
    def update_user_yuanbao(self, user_id: str, yuanbao: int):
        """更新用户元宝"""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET yuanbao = ? WHERE user_id = ?",
                (yuanbao, user_id)
            )
            conn.commit()
