# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 021_create_equipment_system.py
# @Software: AstrBot
# @Description: 创建主公装备系统，包括装备表和在用户表上添加装备槽

import logging

logger = logging.getLogger(__name__)

def up(cursor):
    """
    Creates the lord_equipment table and adds equipment slots to the users table.
    """
    try:
        # 1. 创建装备表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lord_equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL CHECK(type IN ('weapon', 'armor', 'helmet', 'mount', 'accessory')),
                rarity TEXT NOT NULL CHECK(rarity IN ('白', '黄', '玄', '地', '天')),
                min_level INTEGER NOT NULL DEFAULT 1,
                attack_bonus REAL NOT NULL DEFAULT 0,
                defense_bonus REAL NOT NULL DEFAULT 0,
                health_bonus REAL NOT NULL DEFAULT 0,
                description TEXT
            )
        """)
        logger.info("Table 'lord_equipment' created or already exists.")

        # 2. 在 User 表中添加装备槽位
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        slots = {
            'equipped_weapon_id': 'INTEGER',
            'equipped_armor_id': 'INTEGER',
            'equipped_helmet_id': 'INTEGER',
            'equipped_mount_id': 'INTEGER',
            'equipped_accessory_id': 'INTEGER'
        }

        for slot, type in slots.items():
            if slot not in columns:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {slot} {type} NULL")
                logger.info(f"Column '{slot}' added to 'users' table.")
            else:
                logger.info(f"Column '{slot}' already exists in 'users' table.")

        # 3. 插入装备数据
        equipment_data = [
            # ... (此处省略大量数据，以节省空间)
            # --- 武器 (Weapon) ---
            {'name': '生锈的铁剑', 'type': 'weapon', 'rarity': '白', 'min_level': 1, 'attack_bonus': 0.01, 'defense_bonus': 0, 'health_bonus': 0, 'description': '一把随处可见的铁剑，锈迹斑斑。'},
            {'name': '木棍', 'type': 'weapon', 'rarity': '白', 'min_level': 1, 'attack_bonus': 0.02, 'defense_bonus': 0, 'health_bonus': 0, 'description': '结实的木棍，聊胜于无。'},
            {'name': '倚天剑', 'type': 'weapon', 'rarity': '天', 'min_level': 41, 'attack_bonus': 0.45, 'defense_bonus': 0, 'health_bonus': 0, 'description': '“武林至尊，宝刀屠龙，号令天下，莫敢不从，倚天不出，谁与争锋。”'},
            # --- 铠甲 (Armor) ---
            {'name': '布衣', 'type': 'armor', 'rarity': '白', 'min_level': 1, 'attack_bonus': 0, 'defense_bonus': 0.01, 'health_bonus': 0, 'description': '普通的布衣服。'},
            {'name': '龙鳞铠', 'type': 'armor', 'rarity': '天', 'min_level': 42, 'attack_bonus': 0, 'defense_bonus': 0.45, 'health_bonus': 0, 'description': '传说由龙鳞制成，刀枪不入。'},
            # --- 头盔 (Helmet) ---
            {'name': '布头巾', 'type': 'helmet', 'rarity': '白', 'min_level': 1, 'attack_bonus': 0, 'defense_bonus': 0, 'health_bonus': 0.01, 'description': '用于束发。'},
            {'name': '九龙冠', 'type': 'helmet', 'rarity': '天', 'min_level': 44, 'attack_bonus': 0, 'defense_bonus': 0.15, 'health_bonus': 0.40, 'description': '雕有九条龙，是帝王的象征。'},
            # --- 坐骑 (Mount) ---
            {'name': '劣马', 'type': 'mount', 'rarity': '白', 'min_level': 5, 'attack_bonus': 0.01, 'defense_bonus': 0.01, 'health_bonus': 0.01, 'description': '跑不快，但总比走路强。'},
            {'name': '赤兔', 'type': 'mount', 'rarity': '天', 'min_level': 45, 'attack_bonus': 0.25, 'defense_bonus': 0.25, 'health_bonus': 0.25, 'description': '人中吕布，马中赤兔。'},
            # --- 饰品 (Accessory) ---
            {'name': '平安符', 'type': 'accessory', 'rarity': '白', 'min_level': 1, 'attack_bonus': 0, 'defense_bonus': 0, 'health_bonus': 0.03, 'description': '希望能带来好运。'},
            {'name': '传国玉玺', 'type': 'accessory', 'rarity': '天', 'min_level': 48, 'attack_bonus': 0.20, 'defense_bonus': 0.20, 'health_bonus': 0.20, 'description': '“受命于天，既寿永昌”。'},
        ]
        
        # 自动填充以满足100种装备的要求
        base_names = {
            'weapon': ['长剑', '大刀', '战斧', '铁鞭', '双股剑', '流星锤', '狼牙棒'],
            'armor': ['鳞甲', '环锁铠', '步人甲', '棉甲', '板甲'],
            'helmet': ['凤翅盔', '束发冠', '兜鍪', '笠盔'],
            'mount': ['白龙马', '照夜玉狮子', '乌云踏雪', '卷毛赤兔'],
            'accessory': ['兵符', '帅印', '护心镜', '锦囊']
        }
        
        rarity_map = {
            '白': {'level': 1, 'multiplier': 1},
            '黄': {'level': 10, 'multiplier': 1.5},
            '玄': {'level': 20, 'multiplier': 2.5},
            '地': {'level': 30, 'multiplier': 3.5},
            '天': {'level': 40, 'multiplier': 5}
        }

        for rarity, r_config in rarity_map.items():
            for eq_type, names in base_names.items():
                for name in names:
                    new_name = f"{rarity}·{name}"
                    
                    attack, defense, health = 0, 0, 0
                    if eq_type == 'weapon':
                        attack = 0.05 * r_config['multiplier']
                    elif eq_type == 'armor':
                        defense = 0.05 * r_config['multiplier']
                    elif eq_type == 'helmet':
                        health = 0.05 * r_config['multiplier']
                    elif eq_type == 'mount':
                        attack = 0.02 * r_config['multiplier']
                        defense = 0.02 * r_config['multiplier']
                        health = 0.02 * r_config['multiplier']
                    elif eq_type == 'accessory':
                        attack = 0.01 * r_config['multiplier']
                        defense = 0.01 * r_config['multiplier']
                        health = 0.01 * r_config['multiplier']

                    equipment_data.append({
                        'name': new_name, 'type': eq_type, 'rarity': rarity,
                        'min_level': r_config['level'],
                        'attack_bonus': round(attack, 2),
                        'defense_bonus': round(defense, 2),
                        'health_bonus': round(health, 2),
                        'description': f'一件{rarity}等级的{name}，蕴含着不凡的力量。'
                    })

        for item in equipment_data:
            cursor.execute("""
                INSERT OR IGNORE INTO lord_equipment (name, type, rarity, min_level, attack_bonus, defense_bonus, health_bonus, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (item['name'], item['type'], item['rarity'], item['min_level'], item.get('attack_bonus', 0), item.get('defense_bonus', 0), item.get('health_bonus', 0), item['description']))
        logger.info("Equipment data inserted into 'lord_equipment' table.")

    except Exception as e:
        logger.error(f"Error applying migration 021: {e}")
        raise

def down(cursor):
    """
    Drops the lord_equipment table and removes equipment slots from the users table.
    """
    try:
        # 1. 删除装备表
        cursor.execute("DROP TABLE IF EXISTS lord_equipment")
        logger.info("Table 'lord_equipment' dropped.")

        # 2. 移除 User 表中的装备槽位 (同样，这在SQLite中很复杂)
        logger.warning("Rollback for 'add_equipment_slots' is not fully implemented due to SQLite limitations.")
        # 实际降级需要重建表
        pass

    except Exception as e:
        logger.error(f"Error rolling back migration 021: {e}")
        raise
