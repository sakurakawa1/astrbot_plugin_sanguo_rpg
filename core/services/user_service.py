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
        # 用于在内存中存储玩家的临时状态，例如正在进行的冒险
        self.active_adventures = {}

    def get_user(self, user_id: str) -> User | None:
        """
        通过ID获取用户实体
        :param user_id: 用户ID
        :return: User对象或None
        """
        return self.user_repo.get_by_id(user_id)

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
                level=1,
                created_at=datetime.now(),
                last_signed_in=None,
                reputation=0,
                health=100,
                status="正常",
                title=None
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
        user = self.get_user(user_id)
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
        user = self.get_user(user_id)
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

    # --- 冒险状态管理 ---

    def get_user_adventure_state(self, user_id: str) -> dict | None:
        """获取用户的当前冒险状态"""
        return self.active_adventures.get(user_id)

    def set_user_adventure_state(self, user_id: str, state: dict):
        """设置用户的冒险状态"""
        self.active_adventures[user_id] = state

    def clear_user_adventure_state(self, user_id: str):
        """清除用户的冒险状态"""
        if user_id in self.active_adventures:
            del self.active_adventures[user_id]

    # --- 奖励应用 ---

    def apply_adventure_rewards(self, user_id: str, rewards: dict):
        """
        将冒险奖励应用到用户身上
        :param user_id: 用户ID
        :param rewards: 奖励字典，例如 {"coins": 100, "exp": 50, "reputation": 5}
        """
        user = self.get_user(user_id)
        if not user:
            return

        try:
            user.coins += rewards.get("coins", 0)
            user.exp += rewards.get("exp", 0)
            user.reputation += rewards.get("reputation", 0)
            
            # 防止属性变为负数
            user.coins = max(0, user.coins)
            user.reputation = max(0, user.reputation)

            # TODO: 添加物品处理逻辑
            # items_to_add = rewards.get("items", [])
            # if items_to_add:
            #     # 调用物品服务将物品添加到玩家背包
            #     pass

            self.user_repo.update(user)
        except Exception as e:
            # 在这里可以添加日志记录
            print(f"Error applying rewards to user {user_id}: {e}")
