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
                "INSERT INTO users (user_id, nickname, coins, yuanbao, exp, level, reputation, health, status, created_at, last_signed_in, title) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user.user_id, user.nickname, user.coins, user.yuanbao, user.exp, user.level, user.reputation, user.health, user.status, user.created_at, user.last_signed_in, user.title)
            )
            conn.commit()

    def get_by_id(self, user_id: str) -> Optional[User]:
        with self._create_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                try:
                    row_keys = row.keys()

                    # 核心字段检查
                    if "user_id" not in row_keys or "nickname" not in row_keys:
                        return None

                    last_signed_in_str = row["last_signed_in"] if "last_signed_in" in row_keys and row["last_signed_in"] else None
                    last_signed_in = None
                    if last_signed_in_str:
                        try:
                            last_signed_in = datetime.fromisoformat(last_signed_in_str)
                        except (ValueError, TypeError):
                            pass  # Keep as None

                    created_at_str = row["created_at"] if "created_at" in row_keys and row["created_at"] else None
                    created_at = datetime.now()  # Default
                    if created_at_str:
                        try:
                            created_at = datetime.fromisoformat(created_at_str)
                        except (ValueError, TypeError):
                            pass  # Keep default

                    return User(
                        user_id=row["user_id"],
                        nickname=row["nickname"],
                        coins=row["coins"] if "coins" in row_keys else 0,
                        yuanbao=row["yuanbao"] if "yuanbao" in row_keys else 0,
                        exp=row["exp"] if "exp" in row_keys else 0,
                        level=row["level"] if "level" in row_keys else 1,
                        created_at=created_at,
                        last_signed_in=last_signed_in,
                        reputation=row["reputation"] if "reputation" in row_keys else 0,
                        health=row["health"] if "health" in row_keys else 100,
                        status=row["status"] if "status" in row_keys else "正常",
                        title=row["title"] if "title" in row_keys else None
                    )
                except KeyError:
                    return None
            return None

    def update(self, user: User):
        with self._create_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE users 
                    SET nickname = ?, coins = ?, yuanbao = ?, exp = ?, level = ?, reputation = ?, health = ?, status = ?, last_signed_in = ?, title = ?
                    WHERE user_id = ?
                    """,
                    (user.nickname, user.coins, user.yuanbao, user.exp, user.level, user.reputation, user.health, user.status, user.last_signed_in, user.title, user.user_id)
                )
                conn.commit()
            except sqlite3.Error as e:
                # 可以添加日志记录
                print(f"Database update failed: {e}")
                raise
    
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
