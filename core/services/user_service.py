# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : user_service.py
# @Software: AstrBot
# @Description: 用户服务，处理与用户相关的业务逻辑

import random
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from astrbot_plugin_sanguo_rpg.core.domain.models import User, Item
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
if TYPE_CHECKING:
    from astrbot_plugin_sanguo_rpg.core.services.inventory_service import InventoryService
    from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_item_repo import ItemRepository
    from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_general_repo import SqliteGeneralRepository


class UserService:
    def __init__(self, user_repo: SqliteUserRepository, inventory_service: 'InventoryService', item_repo: 'ItemRepository', general_repo: 'SqliteGeneralRepository', game_config: dict):
        self.user_repo = user_repo
        self.inventory_service = inventory_service
        self.item_repo = item_repo
        self.general_repo = general_repo
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
            user_config = self.game_config.get("user", {})
            new_user = User(
                user_id=user_id,
                nickname=nickname,
                coins=1000,
                yuanbao=10,
                exp=0,
                level=1,
                lord_exp=0,
                lord_level=1,
                created_at=datetime.now(),
                last_signed_in=None,
                reputation=0,
                health=100,
                status="正常",
                title=None,
                pity_4_star_count=0,
                pity_5_star_count=0,
                attack=10,
                defense=5,
                max_health=100,
                auto_adventure_enabled=False,
                auto_dungeon_id=None,
                last_adventure_time=datetime.now(),
                battle_generals=None
            )
            self.user_repo.create(new_user)
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
            auto_adventure_status = "开启" if user.auto_adventure_enabled else "关闭"
            auto_dungeon_status = f"副本ID {user.auto_dungeon_id}" if user.auto_dungeon_id else "未设置"

            info = (
                f"【主公信息】\n"
                f"👤 昵称: {user.nickname}\n"
                f"{title_display}"
                f"❤️ 血量: {user.health}/{user.max_health}\n"
                f"⚔️ 攻击: {user.attack}\n"
                f"🛡️ 防御: {user.defense}\n"
                f"⭐ 主公等级: {user.lord_level}\n"
                f"📈 主公经验: {user.lord_exp}\n"
                f"⭐ 武将等级: {user.level}\n"
                f"📈 武将经验: {user.exp}\n"
                f"🎖️ 声望: {user.reputation}\n"
                f"💰 铜钱: {user.coins}\n"
                f"💎 元宝: {user.yuanbao}\n"
                f"--- 抽卡保底 ---\n"
                f"四星保底计数: {user.pity_4_star_count}\n"
                f"五星保底计数: {user.pity_5_star_count}\n"
                f"--- 自动战斗 ---\n"
                f"自动冒险: {auto_adventure_status}\n"
                f"自动副本: {auto_dungeon_status}\n"
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

    def add_lord_exp(self, user: User, exp_to_add: int) -> Optional[str]:
        """
        增加主公经验并处理升级，支持一次升多级。
        :param user: 用户对象
        :param exp_to_add: 要增加的经验值
        :return: 如果升级，则返回升级消息，否则返回None
        """
        if exp_to_add <= 0:
            return None

        user.lord_exp += exp_to_add
        
        lord_level_config = self.game_config.get("lord_level", {})
        base_exp = lord_level_config.get("base_exp", 100)
        exp_factor = lord_level_config.get("exp_factor", 1.5)
        
        leveled_up = False
        level_up_messages = []

        # 循环处理升级
        exp_for_next_level = int(base_exp * (exp_factor ** (user.lord_level - 1)))
        while user.lord_exp >= exp_for_next_level:
            leveled_up = True
            
            # 升级
            user.lord_exp -= exp_for_next_level
            user.lord_level += 1
            
            # 属性提升
            attack_increase = lord_level_config.get("attack_increase", 5)
            defense_increase = lord_level_config.get("defense_increase", 3)
            health_increase = lord_level_config.get("health_increase", 10)
            
            user.attack += attack_increase
            user.defense += defense_increase
            user.max_health += health_increase
            user.health = user.max_health  # 升级后满血

            level_up_messages.append(
                f"恭喜主公！您的等级提升至 {user.lord_level}！\n"
                f"⚔️ 攻击 +{attack_increase}，🛡️ 防御 +{defense_increase}，❤️ 血量 +{health_increase}"
            )
            
            # 计算下一级所需经验
            exp_for_next_level = int(base_exp * (exp_factor ** (user.lord_level - 1)))

        # 只有在升级时才需要调用update，避免不必要的数据库写入
        if leveled_up:
            self.user_repo.update(user)
            return "\n\n".join(level_up_messages)
        else:
            # 如果没有升级，但经验值变化了，也需要更新
            self.user_repo.update(user)
            return None

    def apply_adventure_rewards(self, user_id: str, rewards: dict) -> dict:
        """
        将冒险奖励应用到用户身上, 并返回包含实际奖励和升级消息的字典
        :param user_id: 用户ID
        :param rewards: 奖励字典
        :return: 一个包含实际奖励和升级消息的字典
        """
        user = self.get_user(user_id)
        if not user:
            return {"actual_rewards": {}, "level_up_message": None}

        actual_rewards = {}
        level_up_message = None
        try:
            # 应用金钱、声望等
            coins_change = rewards.get("coins", 0)
            if coins_change != 0:
                user.coins += coins_change
                actual_rewards["coins"] = coins_change

            reputation_change = rewards.get("reputation", 0)
            if reputation_change != 0:
                user.reputation += reputation_change
                actual_rewards["reputation"] = reputation_change

            # 应用武将经验
            exp_change = rewards.get("exp", 0)
            if exp_change != 0:
                user.exp += exp_change
                actual_rewards["exp"] = exp_change
            
            # 应用主公经验并检查升级
            lord_exp_reward = rewards.get("lord_exp", 0)
            if lord_exp_reward != 0:
                # add_lord_exp 内部会处理数据库更新
                level_up_message = self.add_lord_exp(user, lord_exp_reward)
                actual_rewards["lord_exp"] = lord_exp_reward

            user.coins = max(0, user.coins)
            user.reputation = max(0, user.reputation)

            # --- 处理物品奖励 ---
            obtained_item_names = []
            dynamic_item_count = rewards.get("dynamic_item_count", 0)
            if dynamic_item_count > 0:
                dynamic_item_pool = self.game_config.get("adventure", {}).get("dynamic_reward_item_ids", [1])
                for _ in range(dynamic_item_count):
                    item_id_to_add = random.choice(dynamic_item_pool)
                    self.inventory_service.add_item(user_id, item_id_to_add, 1, is_dynamic=True)
                    base_item = self.item_repo.get_by_id(item_id_to_add)
                    if base_item:
                        obtained_item_names.append(base_item.name)

            item_ids_to_add = rewards.get("item_ids", [])
            if item_ids_to_add:
                for item_id in item_ids_to_add:
                    self.inventory_service.add_item(user_id, item_id, 1)
                    base_item = self.item_repo.get_by_id(item_id)
                    if base_item:
                        obtained_item_names.append(base_item.name)
            
            if obtained_item_names:
                actual_rewards["items"] = obtained_item_names

            # 处理血量变化
            health_change = rewards.get("health", 0)
            if health_change != 0:
                user.health = max(0, min(user.max_health, user.health + health_change))
                actual_rewards["health"] = health_change

            # 如果没有经验变化，则需要手动更新用户状态
            if lord_exp_reward == 0:
                self.user_repo.update(user)

        except Exception as e:
            print(f"Error applying rewards to user {user_id}: {e}")
        
        return {"actual_rewards": actual_rewards, "level_up_message": level_up_message}

    def get_item_names_by_ids(self, item_ids: List[int]) -> List[str]:
        """
        根据物品ID列表获取物品名称列表
        """
        if not item_ids:
            return []
        
        items = self.item_repo.get_by_ids(item_ids)
        return [item.name for item in items if item]

    # --- 自动战斗管理 ---

    def set_auto_adventure(self, user_id: str, enabled: bool):
        user = self.get_user(user_id)
        if not user:
            return {"success": False, "message": "找不到用户。"}
        self.user_repo.set_auto_adventure(user_id, enabled)
        status = "开启" if enabled else "关闭"
        return {"success": True, "message": f"自动冒险已{status}。"}

    def set_auto_dungeon(self, user_id: str, dungeon_id: Optional[int]):
        user = self.get_user(user_id)
        if not user:
            return {"success": False, "message": "找不到用户。"}

        # 检查是否设置了出战武将
        if dungeon_id is not None:
            if not user.battle_generals or user.battle_generals == '[]':
                return {"success": False, "message": "请先使用 /三国设置出战 [武将ID] 命令设置出战武将，才能开启自动副本。"}

        self.user_repo.set_auto_dungeon(user_id, dungeon_id)
        if dungeon_id:
            return {"success": True, "message": f"自动副本已设置为 副本ID: {dungeon_id}。"}
        else:
            return {"success": True, "message": "自动副本已关闭。"}

    def get_all_users_with_auto_battle(self) -> List[User]:
        return self.user_repo.get_all_users_with_auto_battle()

    def update_last_adventure_time(self, user_id: str):
        self.user_repo.update_last_adventure_time(user_id)

    def update_pity_counters(self, user_id: str, rarity: int):
        """
        更新用户的抽卡保底计数器
        :param user_id: 用户ID
        :param rarity: 抽到的物品稀有度
        """
        user = self.get_user(user_id)
        if not user:
            return

        user.pity_4_star_count += 1
        user.pity_5_star_count += 1

        if rarity == 4:
            user.pity_4_star_count = 0
        elif rarity == 5:
            user.pity_4_star_count = 0
            user.pity_5_star_count = 0
        
        self.user_repo.update(user)
