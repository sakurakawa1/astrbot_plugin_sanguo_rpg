# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : models.py
# @Software: AstrBot
# @Description: 定义插件的核心业务模型

import datetime
import json
import random
from dataclasses import dataclass, field
from typing import Optional

class User:
    """玩家信息"""
    def __init__(self, user_id: str, nickname: str, coins: int, yuanbao: int, exp: int, level: int, lord_exp: int, lord_level: int,
                 created_at: datetime.datetime, last_signed_in: Optional[datetime.datetime] = None,
                 reputation: int = 0, health: int = 100, status: str = "正常",
                 title: Optional[str] = None, pity_4_star_count: int = 0, pity_5_star_count: int = 0,
                 attack: int = 10, defense: int = 5, max_health: int = 100,
                 auto_adventure_enabled: bool = False, auto_dungeon_id: Optional[int] = None,
                 last_adventure_time: Optional[datetime.datetime] = None,
                 last_steal_time: Optional[datetime.datetime] = None,
                 battle_generals: Optional[str] = None,
                 equipped_weapon_id: Optional[int] = None,
                 equipped_armor_id: Optional[int] = None,
                 equipped_helmet_id: Optional[int] = None,
                 equipped_mount_id: Optional[int] = None,
                 equipped_accessory_id: Optional[int] = None):
        self.user_id = user_id
        self.nickname = nickname
        self.coins = coins
        self.yuanbao = yuanbao
        self.exp = exp
        self.level = level
        self.lord_exp = lord_exp
        self.lord_level = lord_level
        self.created_at = created_at
        self.last_signed_in = last_signed_in
        self.reputation = reputation
        self.health = health
        self.status = status
        self.title = title
        self.pity_4_star_count = pity_4_star_count
        self.pity_5_star_count = pity_5_star_count
        self.attack = attack
        self.defense = defense
        self.max_health = max_health
        self.auto_adventure_enabled = auto_adventure_enabled
        self.auto_dungeon_id = auto_dungeon_id
        self.last_adventure_time = last_adventure_time
        self.last_steal_time = last_steal_time
        self.battle_generals = battle_generals
        self.equipped_weapon_id = equipped_weapon_id
        self.equipped_armor_id = equipped_armor_id
        self.equipped_helmet_id = equipped_helmet_id
        self.equipped_mount_id = equipped_mount_id
        self.equipped_accessory_id = equipped_accessory_id

    @property
    def max_generals(self) -> int:
        """根据玩家等级确定最大可拥有武将数"""
        if 1 <= self.level <= 10:
            return 3
        elif 11 <= self.level <= 20:
            return 5
        elif self.level > 20:
            return 7 # Default for higher levels
        return 1

class General:
    """武将模板"""
    def __init__(self, general_id: int, name: str, rarity: int, camp: str, wu_li: int, zhi_li: int, tong_shuai: int, su_du: int, skill_desc: str, background: str):
        self.general_id = general_id
        self.name = name
        self.rarity = rarity
        self.camp = camp
        self.wu_li = wu_li
        self.zhi_li = zhi_li
        self.tong_shuai = tong_shuai
        self.su_du = su_du
        self.skill_desc = skill_desc
        self.background = background

class UserGeneral:
    """玩家拥有的武将实例"""
    def __init__(self, instance_id: int, user_id: str, general_id: int, level: int, exp: int, created_at: datetime.datetime):
        self.instance_id = instance_id
        self.user_id = user_id
        self.general_id = general_id
        self.level = level
        self.exp = exp
        self.created_at = created_at

    def get_exp_to_next_level(self) -> int:
        """计算当前等级升级到下一级所需经验"""
        return 100 * self.level  # Example formula

    def can_level_up(self, user_exp_pool: int) -> bool:
        """检查是否有足够经验升级"""
        return user_exp_pool >= self.get_exp_to_next_level()

class UserGeneralDetails:
    """用于展示的玩家武将详细信息"""
    def __init__(self,
                 instance_id: int,
                 user_id: str,
                 general_id: int,
                 level: int,
                 exp: int,
                 created_at: datetime.datetime,
                 name: str,
                 rarity: int,
                 camp: str,
                 wu_li: int,
                 zhi_li: int,
                 tong_shuai: int,
                 su_du: int,
                 skill_desc: str):
        self.instance_id = instance_id
        self.user_id = user_id
        self.general_id = general_id
        self.level = level
        self.exp = exp
        self.created_at = created_at
        self.name = name
        self.rarity = rarity
        self.camp = camp
        self.base_wu_li = wu_li
        self.base_zhi_li = zhi_li
        self.base_tong_shuai = tong_shuai
        self.base_su_du = su_du
        self.skill_desc = skill_desc

    @property
    def wu_li(self) -> int:
        """计算升级后的武力值"""
        return self._calculate_upgraded_stat(self.base_wu_li)

    @property
    def zhi_li(self) -> int:
        """计算升级后的智力值"""
        return self._calculate_upgraded_stat(self.base_zhi_li)

    @property
    def tong_shuai(self) -> int:
        """计算升级后的统帅值"""
        return self._calculate_upgraded_stat(self.base_tong_shuai)

    @property
    def su_du(self) -> int:
        """计算升级后的速度值"""
        return self._calculate_upgraded_stat(self.base_su_du)

    def _calculate_upgraded_stat(self, base_stat: int) -> int:
        """
        计算单项属性升级后的值 (线性成长模型)。
        每级提供基础属性 2% 的稳定成长。
        """
        # 每级提升基础属性的 2%
        growth_per_level = base_stat * 0.02
        # 总成长 = 每级成长 * (当前等级 - 1)
        total_growth = growth_per_level * (self.level - 1)
        return round(base_stat + total_growth)

    @property
    def combat_power(self) -> float:
        """计算战斗力"""
        return self.wu_li * 1.2 + self.zhi_li * 0.8 + self.tong_shuai * 1.0 + self.su_du * 0.5

class Title:
    """称号信息"""
    def __init__(self, title_id: int, name: str, required_reputation: int):
        self.title_id = title_id
        self.name = name
        self.required_reputation = required_reputation

@dataclass
class BattleLog:
    log_id: int
    user_id: int
    generals: str
    enemy: str
    result: str
    timestamp: str


@dataclass
class Dungeon:
    dungeon_id: int
    name: str
    description: str
    recommended_level: int
    max_generals: int
    enemy_strength_min: float
    enemy_strength_max: float
    rewards: dict

@dataclass
class Item:
    """物品模板"""
    id: int
    name: str
    type: str
    quality: str
    description: str
    is_consumable: bool
    base_price_coins: int
    base_price_yuanbao: int
    effects: dict = field(default_factory=dict)

    @classmethod
    def from_row(cls, row: tuple):
        """从数据库行元组创建 Item 对象"""
        # 假设行顺序: id, name, type, quality, description, is_consumable, base_price_coins, base_price_yuanbao, effects
        effects_data = row['effects']
        effects = json.loads(effects_data) if isinstance(effects_data, str) and effects_data else {}
        
        return cls(
            id=row['id'],
            name=row['name'],
            type=row['type'],
            quality=row['quality'],
            description=row['description'],
            is_consumable=bool(row['is_consumable']),
            base_price_coins=int(row['base_price_coins']) if row['base_price_coins'] is not None else 0,
            base_price_yuanbao=int(row['base_price_yuanbao']) if row['base_price_yuanbao'] is not None else 0,
            effects=effects
        )


@dataclass
class InventoryItem:
    """
    背包中的物品实例。
    这个模型结合了物品模板(Item)和实例的具体属性(instance_properties)。
    """
    inventory_id: int
    user_id: str
    item_id: int
    quantity: int
    item: Item  # 基础物品模板
    instance_properties: dict = field(default_factory=dict)  # 动态生成的属性，例如动态价格

    @property
    def name(self) -> str:
        return self.instance_properties.get('name', self.item.name)

    @property
    def description(self) -> str:
        return self.instance_properties.get('description', self.item.description)

    @property
    def quality(self) -> str:
        return self.instance_properties.get('quality', self.item.quality)

    @property
    def effects(self) -> dict:
        # 合并基础效果和实例效果
        base_effects = self.item.effects.copy()
        instance_effects = self.instance_properties.get('effects', {})
        base_effects.update(instance_effects)
        return base_effects

    @property
    def sell_price_coins(self) -> int:
        # 优先使用实例售价，否则使用模板基础价
        return self.instance_properties.get('effects', {}).get('sell_coins', self.item.base_price_coins)

    @property
    def sell_price_yuanbao(self) -> int:
        return self.instance_properties.get('effects', {}).get('sell_yuanbao', self.item.base_price_yuanbao)
    
    @property
    def use_exp(self) -> int:
        return self.instance_properties.get('effects', {}).get('use_exp', 0)


@dataclass
class LordEquipment:
    """主公装备"""
    id: int
    name: str
    type: str
    rarity: str
    min_level: int
    attack_bonus: float
    defense_bonus: float
    health_bonus: float
    description: str
