# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : user_service.py
# @Software: AstrBot
# @Description: 用户服务，处理与用户相关的业务逻辑

from datetime import datetime
from astrbot_plugin_sanguo_rpg.core.domain.models import User
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository

class UserService:
    def __init__(self, user_repo: SqliteUserRepository, game_config: dict):
        self.user_repo = user_repo
        self.game_config = game_config

    def register(self, user_id: str, nickname: str) -> dict:
        """
        注册新用户
        :param user_id: 用户ID
        :param nickname: 用户昵称
        :return: 包含成功/失败消息的字典
        """
        if self.user_repo.get_by_id(user_id):
            return {"success": False, "message": "您已经注册过了，无需重复注册。"}

        try:
            new_user = User(
                user_id=user_id,
                nickname=nickname,
                coins=self.game_config.get("user", {}).get("initial_coins", 1000),
                yuanbao=self.game_config.get("user", {}).get("initial_yuanbao", 100),
                exp=0,
                created_at=datetime.now(),
                last_signed_in=None
            )
            self.user_repo.add(new_user)
            return {"success": True, "message": f"欢迎主公 {nickname}！您已成功注册，获得初始资金，开启您的三国霸业！"}
        except Exception as e:
            # logger.error(f"注册用户时发生错误: {e}") # 在服务层最好不要直接用logger，让上层处理
            return {"success": False, "message": f"注册时发生未知错误: {e}"}

    def get_user_info(self, user_id: str) -> dict:
        """
        获取用户详细信息
        :param user_id: 用户ID
        :return: 包含用户信息的字典或错误消息
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "您尚未注册，请先使用 /三国注册 命令。"}

        try:
            title_display = f"称号: {user.title}\n" if user.title else ""
            info = (
                f"【主公信息】\n"
                f"👤 昵称: {user.nickname}\n"
                f"{title_display}"
                f"声望: {user.reputation}\n"
                f"经验: {getattr(user, 'exp', 0)}\n"
                f"💰 铜钱: {user.coins}\n"
                f"💎 元宝: {user.yuanbao}\n"
                f"📅 注册时间: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            return {"success": True, "message": info}
        except Exception as e:
            return {"success": False, "message": f"获取信息时发生未知错误: {e}"}

    def sign_in(self, user_id: str) -> dict:
        """
        用户每日签到
        :param user_id: 用户ID
        :return: 包含签到结果的字典
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "您尚未注册，请先使用 /三国注册 命令。"}

        now = datetime.now()
        if user.last_signed_in and user.last_signed_in.date() == now.date():
            return {"success": False, "message": "你今天已经签到过了，明天再来吧！"}

        try:
            coins_reward = 50
            yuanbao_reward = 50
            exp_reward = 10
            user.coins += coins_reward
            user.yuanbao += yuanbao_reward
            user.exp += exp_reward
            user.last_signed_in = now
            self.user_repo.update(user)
            
            return {"success": True, "message": f"签到成功！获得 {coins_reward} 铜钱，{yuanbao_reward} 元宝，{exp_reward} 经验。"}
        except Exception as e:
            return {"success": False, "message": f"签到时发生未知错误: {e}"}
