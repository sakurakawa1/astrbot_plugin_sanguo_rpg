# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : sqlite_user_repo.py
# @Software: AstrBot
# @Description: 用户数据仓储实现

import sqlite3
from datetime import datetime
from typing import Optional, List
from astrbot_plugin_sanguo_rpg.core.domain.models import User

class SqliteUserRepository:
    def __init__(self, db_path):
        self.db_path = db_path

    def _create_connection(self):
        return sqlite3.connect(self.db_path)

    def create(self, user: User):
        """Creates a new user in the database."""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (user_id, nickname, coins, yuanbao, exp, level, lord_exp, lord_level, created_at, last_signed_in,
                                 reputation, health, status, title, pity_4_star_count, pity_5_star_count,
                                 attack, defense, max_health, auto_adventure_enabled, auto_dungeon_id, last_adventure_time, battle_generals, last_steal_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user.user_id, user.nickname, user.coins, user.yuanbao, user.exp, user.level, user.lord_exp, user.lord_level, user.created_at,
                 user.last_signed_in, user.reputation, user.health, user.status, user.title,
                 user.pity_4_star_count, user.pity_5_star_count, user.attack, user.defense, user.max_health,
                 user.auto_adventure_enabled, user.auto_dungeon_id, user.last_adventure_time, user.battle_generals, user.last_steal_time)
            )
            conn.commit()

    def get_by_id(self, user_id: str) -> Optional[User]:
        with self._create_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_user(row)
            return None

    def update(self, user: User):
        with self._create_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE users
                    SET nickname = ?, coins = ?, yuanbao = ?, exp = ?, level = ?, lord_exp = ?, lord_level = ?, reputation = ?,
                        health = ?, status = ?, last_signed_in = ?, title = ?,
                        pity_4_star_count = ?, pity_5_star_count = ?,
                        attack = ?, defense = ?, max_health = ?,
                        auto_adventure_enabled = ?, auto_dungeon_id = ?, last_adventure_time = ?, battle_generals = ?, last_steal_time = ?
                    WHERE user_id = ?
                    """,
                    (user.nickname, user.coins, user.yuanbao, user.exp, user.level, user.lord_exp, user.lord_level, user.reputation,
                     user.health, user.status, user.last_signed_in, user.title,
                     user.pity_4_star_count, user.pity_5_star_count,
                     user.attack, user.defense, user.max_health,
                     user.auto_adventure_enabled, user.auto_dungeon_id, user.last_adventure_time, user.battle_generals, user.last_steal_time, user.user_id)
                )
                conn.commit()
            except sqlite3.Error as e:
                print(f"Database update failed: {e}")
                raise
    
    def get_user(self, user_id: str) -> Optional[User]:
        return self.get_by_id(user_id)
    
    def update_user_coins(self, user_id: str, coins: int):
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET coins = ? WHERE user_id = ?", (coins, user_id))
            conn.commit()
    
    def update_user_yuanbao(self, user_id: str, yuanbao: int):
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET yuanbao = ? WHERE user_id = ?", (yuanbao, user_id))
            conn.commit()

    def set_auto_adventure(self, user_id: str, enabled: bool):
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET auto_adventure_enabled = ? WHERE user_id = ?", (enabled, user_id))
            conn.commit()

    def set_auto_dungeon(self, user_id: str, dungeon_id: Optional[int]):
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET auto_dungeon_id = ? WHERE user_id = ?", (dungeon_id, user_id))
            conn.commit()

    def get_all_users_with_auto_battle(self) -> List[User]:
        users = []
        with self._create_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE auto_adventure_enabled = 1 OR auto_dungeon_id IS NOT NULL")
            rows = cursor.fetchall()
            for row in rows:
                users.append(self._row_to_user(row))
        return users

    def update_last_adventure_time(self, user_id: str):
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET last_adventure_time = ? WHERE user_id = ?", (datetime.now().isoformat(), user_id))
            conn.commit()

    def _row_to_user(self, row: sqlite3.Row) -> Optional[User]:
        try:
            row_keys = row.keys()

            def get_val(key, default=None):
                return row[key] if key in row_keys else default

            last_signed_in = None
            if get_val("last_signed_in"):
                try:
                    last_signed_in = datetime.fromisoformat(get_val("last_signed_in"))
                except (ValueError, TypeError):
                    pass

            created_at = datetime.now()
            if get_val("created_at"):
                try:
                    created_at = datetime.fromisoformat(get_val("created_at"))
                except (ValueError, TypeError):
                    pass
            
            last_adventure_time = None
            if get_val("last_adventure_time"):
                try:
                    last_adventure_time = datetime.fromisoformat(get_val("last_adventure_time"))
                except (ValueError, TypeError):
                    pass
            
            last_steal_time = None
            if get_val("last_steal_time"):
                try:
                    last_steal_time = datetime.fromisoformat(get_val("last_steal_time"))
                except (ValueError, TypeError):
                    pass

            return User(
                user_id=get_val("user_id"),
                nickname=get_val("nickname"),
                coins=get_val("coins", 0),
                yuanbao=get_val("yuanbao", 0),
                exp=get_val("exp", 0),
                level=get_val("level", 1),
                lord_exp=get_val("lord_exp", 0),
                lord_level=get_val("lord_level", 1),
                created_at=created_at,
                last_signed_in=last_signed_in,
                reputation=get_val("reputation", 0),
                health=get_val("health", 100),
                status=get_val("status", "正常"),
                title=get_val("title"),
                pity_4_star_count=get_val("pity_4_star_count", 0),
                pity_5_star_count=get_val("pity_5_star_count", 0),
                attack=get_val("attack", 10),
                defense=get_val("defense", 5),
                max_health=get_val("max_health", 100),
                auto_adventure_enabled=get_val("auto_adventure_enabled", False),
                auto_dungeon_id=get_val("auto_dungeon_id"),
                last_adventure_time=last_adventure_time,
                last_steal_time=last_steal_time,
                battle_generals=get_val("battle_generals")
            )
        except (KeyError, TypeError) as e:
            print(f"Error converting row to user: {e}")
            return None
