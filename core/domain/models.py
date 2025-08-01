# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : models.py
# @Software: AstrBot
# @Description: 定义插件的核心业务模型

import datetime
from typing import Optional

class User:
    """玩家信息"""
    def __init__(self, user_id: str, nickname: str, coins: int, yuanbao: int, exp: int, created_at: datetime.datetime, last_signed_in: Optional[datetime.datetime] = None):
        self.user_id = user_id
        self.nickname = nickname
        self.coins = coins
        self.yuanbao = yuanbao
        self.exp = exp
        self.created_at = created_at
        self.last_signed_in = last_signed_in

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
                 su_du: int):
        self.instance_id = instance_id
        self.user_id = user_id
        self.general_id = general_id
        self.level = level
        self.exp = exp
        self.created_at = created_at
        self.name = name
        self.rarity = rarity
        self.camp = camp
        self.wu_li = wu_li
        self.zhi_li = zhi_li
        self.tong_shuai = tong_shuai
        self.su_du = su_du
