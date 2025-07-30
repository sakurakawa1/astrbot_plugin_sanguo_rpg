# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : 001_initial_setup.py
# @Software: AstrBot
# @Description: Initial database setup

def upgrade(cursor):
    """
    升级数据库
    """
    cursor.executescript("""
        -- 玩家表
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            nickname TEXT NOT NULL,
            coins INTEGER NOT NULL DEFAULT 0,
            yuanbao INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL,
            last_signed_in DATETIME
        );

        -- 武将模板表
        CREATE TABLE IF NOT EXISTS generals (
            general_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            rarity INTEGER NOT NULL,
            camp TEXT NOT NULL,
            wu_li INTEGER NOT NULL,
            zhi_li INTEGER NOT NULL,
            tong_shuai INTEGER NOT NULL,
            su_du INTEGER NOT NULL,
            skill_desc TEXT,
            background TEXT
        );

        -- 玩家武将实例表
        CREATE TABLE IF NOT EXISTS user_generals (
            instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            general_id INTEGER NOT NULL,
            level INTEGER NOT NULL DEFAULT 1,
            exp INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (general_id) REFERENCES generals(general_id)
        );
    """)

def downgrade(cursor):
    """
    降级数据库
    """
    pass
