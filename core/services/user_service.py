# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : user_service.py
# @Software: AstrBot
# @Description: 用户服务，处理与用户相关的业务逻辑

import datetime
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
from astrbot_plugin_sanguo_rpg.core.domain.models import User

class UserService:
    def __init__(self, user_repo: SqliteUserRepository, game_config: dict):
        self.user_repo = user_repo
        self.game_config = game_config

    def register(self, user_id: str, nickname: str) -> dict:
        """注册新用户"""
        if self.user_repo.get_by_id(user_id):
            return {"success": False, "message": "您已经注册过了，无需重复注册。"}
        
        new_user = User(
            user_id=user_id,
            nickname=nickname,
            coins=self.game_config.get("user", {}).get("initial_coins", 1000),
            yuanbao=self.game_config.get("user", {}).get("initial_yuanbao", 100),
            exp=0,
            created_at=datetime.datetime.now(),
            last_signed_in=None
        )
        self.user_repo.add(new_user)
        return {"success": True, "message": f"欢迎主公 {nickname}！您已成功注册，获得初始资金，开启您的三国霸业！"}

    def daily_sign_in(self, user_id: str) -> dict:
        """每日签到"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "您尚未注册，请先使用 /注册 命令。"}
        
        now = datetime.datetime.now()
        if user.last_signed_in and user.last_signed_in.date() == now.date():
            return {"success": False, "message": "您今日已经签到过了。"}
            
        # 签到奖励
        coins_reward = 200
        exp_reward = 10
        user.coins += coins_reward
        user.exp += exp_reward
        user.last_signed_in = now
        self.user_repo.update(user)
        
        return {"success": True, "message": f"签到成功！获得 {coins_reward} 铜钱，{exp_reward} 经验。"}

    def get_user_info(self, user_id: str) -> dict:
        """获取用户详细信息"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "您尚未注册，请先使用 /注册 命令。"}

        info = (
            f"【主公信息】\n"
            f"👤 昵称: {user.nickname}\n"
            f"经验: {user.exp}\n"
            f"💰 铜钱: {user.coins}\n"
            f"💎 元宝: {user.yuanbao}\n"
            f"📅 注册时间: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return {"success": True, "message": info}
