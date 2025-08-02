# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : dungeon_service.py
# @Software: AstrBot
# @Description: 副本与战斗服务

import random
import math
from typing import List, TYPE_CHECKING
from ..repositories.sqlite_dungeon_repo import DungeonRepository
from ..repositories.sqlite_user_repo import SqliteUserRepository
from ..repositories.sqlite_general_repo import SqliteGeneralRepository
from ..domain.models import User, UserGeneralDetails
if TYPE_CHECKING:
    from .user_service import UserService
    from .general_service import GeneralService


class DungeonService:
    def __init__(self, dungeon_repo: DungeonRepository, user_repo: SqliteUserRepository, general_repo: SqliteGeneralRepository, user_service: 'UserService', general_service: 'GeneralService'):
        self.dungeon_repo = dungeon_repo
        self.user_repo = user_repo
        self.general_repo = general_repo
        self.user_service = user_service
        self.general_service = general_service

    def list_dungeons(self, user: User) -> str:
        """获取并格式化副本列表"""
        dungeons = self.dungeon_repo.get_all_dungeons()
        if not dungeons:
            return "当前没有可用的副本。"

        message = "【副本列表】\n\n"
        for d in dungeons:
            # 简单的解锁逻辑：玩家等级大于等于推荐等级
            unlocked = user.level >= d.recommended_level
            status_emoji = "✅" if unlocked else "🔒"
            
            message += f"{status_emoji} [ID: {d.dungeon_id}] {d.name} (推荐等级: {d.recommended_level})\n"
            message += f"   - {d.description}\n\n"
        
        message += "使用 `/三国战斗 [副本ID]` 来查看详情并发起挑战。"
        return message.strip()

    def get_eligible_generals_for_dungeon(self, user_id: str, dungeon_id: int) -> str:
        """
        处理 `/三国战斗 [副本ID]` 命令。
        检查是否可以挑战，并列出符合条件的武将。
        """
        dungeon = self.dungeon_repo.get_dungeon_by_id(dungeon_id)
        if not dungeon:
            return f"未找到ID为 {dungeon_id} 的副本。"

        all_user_generals = self.general_repo.get_user_generals_with_details(user_id)
        eligible_generals = [g for g in all_user_generals if g.level >= dungeon.recommended_level]

        if not eligible_generals:
            return f"你没有任何武将达到推荐等级 {dungeon.recommended_level}，无法挑战【{dungeon.name}】。"

        message = f"请选择武将挑战【{dungeon.name}】(推荐等级: {dungeon.recommended_level}):\n\n"
        for g in eligible_generals:
            message += f"🔹 [ID: {g.instance_id}] {g.name} (Lv.{g.level}, 战力: {g.combat_power:.0f})\n"
        
        message += f"\n👉 请回复 `/三国出征 [武将ID1] [武将ID2]...` 来开始战斗。"
        return message.strip()

    def execute_battle(self, user_id: str, dungeon_id: int, general_instance_ids: List[int]) -> str:
        """
        执行战斗逻辑。
        """
        dungeon = self.dungeon_repo.get_dungeon_by_id(dungeon_id)
        if not dungeon:
            return f"未找到ID为 {dungeon_id} 的副本。"

        user = self.user_repo.get_by_id(user_id)
        if not user:
            return "未找到玩家信息。"

        if not general_instance_ids:
            return "请至少选择一名武将出战。"

        # 获取玩家选择的武将的详细信息
        selected_generals_details = self.general_repo.get_user_generals_with_details_by_instance_ids(user_id, general_instance_ids)

        if len(selected_generals_details) != len(general_instance_ids):
            return "选择的武将中包含无效或不属于你的武将ID。"

        if dungeon.max_generals > 0 and len(selected_generals_details) > dungeon.max_generals:
            return f"该副本最多允许 {dungeon.max_generals} 名武将出战。"

        # --- 战斗力计算 (V5 - 引入主公加成) ---
        # 1. 计算主公提供的战斗力
        #    - 攻击和防御对战斗力的贡献权重可以调整
        lord_power = (user.attack * 1.5) + (user.defense * 1.0)

        # 2. 计算武将总战力
        generals_power = 0
        general_names = []
        for g in selected_generals_details:
            if g.level < dungeon.recommended_level:
                return f"武将 {g.name} (Lv.{g.level}) 未达到副本推荐等级 {dungeon.recommended_level}。"
            generals_power += g.combat_power
            general_names.append(g.name)
            
        # 3. 计算最终玩家总战力
        player_combat_power = generals_power + lord_power
        # --- 战斗力计算结束 ---

        # --- 新的敌人战力计算逻辑 (V4 - by Cline) ---
        # 1. 获取基准战力
        avg_power_per_general = self.general_repo.get_average_combat_power_for_level(dungeon.recommended_level)

        # 2. 根据新逻辑计算敌人战力范围
        # N: 副本最大人数
        # M: 偶尔能赢的人数
        n = dungeon.max_generals if dungeon.max_generals > 0 else len(selected_generals_details)
        m = math.ceil(n / 2.5)

        # 敌人战力中心点更靠近M，但随N增加而增加
        enemy_strength_center = (m + (n - m) * 0.5) * avg_power_per_general
        
        # 3. 增加一点随机性
        enemy_combat_power = enemy_strength_center * random.uniform(0.9, 1.1)
        # --- 敌人战力计算结束 ---

        # --- 判定胜负 (优化版 V2 - by Cline) ---
        # 引入更精细的“压制”规则
        win = False
        # 必胜: 玩家战力是敌人的1.5倍以上
        if player_combat_power >= enemy_combat_power * 1.5:
            win = True
        # 必败: 玩家战力不到敌人的60%
        elif player_combat_power < enemy_combat_power * 0.6:
            win = False
        else:
            # 在此区间内，按比例计算胜率
            total_power = player_combat_power + enemy_combat_power
            win_chance = player_combat_power / total_power if total_power > 0 else 0
            if random.random() < win_chance:
                win = True
        
        # 战斗描述
        narrative = f"你率领着 {'、'.join(general_names)} 挑战【{dungeon.name}】。\n"
        narrative += f"主公加成: {lord_power:.0f} 战力 | 武将总和: {generals_power:.0f} 战力\n"
        narrative += f"队伍总战力: {player_combat_power:.0f}\n"
        narrative += f"遭遇了强大的敌人 (战力: {enemy_combat_power:.0f})！\n"
        
        log_message = narrative # 记录战斗过程
        
        if win:
            # 胜利
            rewards = dungeon.rewards
            
            # 1. 处理武将经验 (独立于user_service)
            general_exp_reward = rewards.get("general_exp", 0)
            exp_per_general = 0
            if general_exp_reward > 0 and selected_generals_details:
                exp_per_general = general_exp_reward // len(selected_generals_details)
                for g in selected_generals_details:
                    self.general_repo.add_exp_to_general(g.instance_id, exp_per_general)

            # 2. 准备并应用给用户的奖励
            user_rewards = {
                "coins": rewards.get("coins", 0),
                "yuanbao": rewards.get("yuanbao", 0),
                "lord_exp": rewards.get("user_exp", 0) # 将副本的user_exp映射为主公经验
            }
            
            reward_result = self.user_service.apply_adventure_rewards(user.user_id, user_rewards)
            actual_rewards = reward_result.get("actual_rewards", {})
            level_up_msg = reward_result.get("level_up_message")

            # 3. 构建胜利消息
            narrative += "⚔️ 激战过后，你取得了胜利！ 🎉\n\n"
            narrative += "【奖励结算】\n"
            
            coin_reward = actual_rewards.get("coins", 0)
            yuanbao_reward = actual_rewards.get("yuanbao", 0)
            lord_exp_reward = actual_rewards.get("lord_exp", 0)

            if coin_reward: narrative += f"💰 铜钱: +{coin_reward}\n"
            if yuanbao_reward: narrative += f"💎 元宝: +{yuanbao_reward}\n"
            if lord_exp_reward: narrative += f"📈 主公经验: +{lord_exp_reward}\n"
            if general_exp_reward: narrative += f"⭐ 武将经验: +{general_exp_reward} (每位出战武将 +{exp_per_general})\n"
            
            if level_up_msg:
                narrative += f"\n{level_up_msg}\n"
            
            log_message += f"胜利！获得铜钱: {coin_reward}, 元宝: {yuanbao_reward}, 主公经验: {lord_exp_reward}, 武将经验: {general_exp_reward}"
            self.general_service.add_battle_log(user_id, "副本", log_message)
            return narrative.strip()
        else:
            # 失败
            narrative += "一番苦战，不幸落败... 💔\n"
            narrative += "请提升实力后再次挑战！"
            log_message += "失败！"
            self.general_service.add_battle_log(user_id, "副本", log_message)
            return narrative.strip()
