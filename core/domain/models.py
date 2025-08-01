# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : models.py
# @Software: AstrBot
# @Description: 定义插件的核心业务模型

import datetime
import random
from dataclasses import dataclass
from typing import Optional

class User:
    """玩家信息"""
    def __init__(self, user_id: str, nickname: str, coins: int, yuanbao: int, exp: int, level: int, created_at: datetime.datetime, last_signed_in: Optional[datetime.datetime] = None, reputation: int = 0, health: int = 100, status: str = "正常", title: Optional[str] = None):
        self.user_id = user_id
        self.nickname = nickname
        self.coins = coins
        self.yuanbao = yuanbao
        self.exp = exp  # This is now the unassigned experience pool
        self.level = level
        self.created_at = created_at
        self.last_signed_in = last_signed_in
        self.reputation = reputation
        self.health = health
        self.status = status
        self.title = title

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
    enemy_strength_min: float
    enemy_strength_max: float
    rewards: dict
