# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : dungeon_service.py
# @Software: AstrBot
# @Description: 副本与战斗服务

import random
from typing import List
from ..repositories.sqlite_dungeon_repo import DungeonRepository
from ..repositories.sqlite_user_repo import SqliteUserRepository
from ..repositories.sqlite_general_repo import SqliteGeneralRepository
from ..domain.models import User, UserGeneralDetails

class DungeonService:
    def __init__(self, dungeon_repo: DungeonRepository, user_repo: SqliteUserRepository, general_repo: SqliteGeneralRepository):
        self.dungeon_repo = dungeon_repo
        self.user_repo = user_repo
        self.general_repo = general_repo

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

        # 验证武将等级和计算总战力
        player_combat_power = 0
        general_names = []
        for g in selected_generals_details:
            if g.level < dungeon.recommended_level:
                return f"武将 {g.name} (Lv.{g.level}) 未达到副本推荐等级 {dungeon.recommended_level}。"
            player_combat_power += g.combat_power
            general_names.append(g.name)

        # --- 敌人战力计算 (基于副本强度和玩家平均等级) ---
        # 1. 计算玩家出战武将的平均等级
        avg_player_level = sum(g.level for g in selected_generals_details) / len(selected_generals_details) if selected_generals_details else 1

        # 2. 定义一个“标准同级武将”的战斗力基准
        #    这个基准可以根据游戏平衡进行调整。这里我们简化处理，假设战斗力与等级线性相关。
        #    例如，一个1级武将标准战力为50，10级为500。
        base_power_per_level = 50 
        standard_general_power = base_power_per_level * avg_player_level

        # 3. 根据副本的强度范围，计算敌人总战力
        strength_multiplier = random.uniform(dungeon.enemy_strength_min, dungeon.enemy_strength_max)
        enemy_combat_power = standard_general_power * strength_multiplier
        # --- 敌人战力计算结束 ---

        # --- 判定胜负 (优化版) ---
        # 引入“压制”规则，提升游戏体验
        win = False
        if player_combat_power >= enemy_combat_power * 2:
            win = True # 战力是敌人2倍以上，必定胜利
        elif enemy_combat_power >= player_combat_power * 2:
            win = False # 敌人战力是玩家2倍以上，必定失败
        else:
            # 差距在2倍以内，按概率计算
            total_power = player_combat_power + enemy_combat_power
            win_chance = player_combat_power / total_power if total_power > 0 else 0
            if random.random() < win_chance:
                win = True
        
        # 战斗描述
        narrative = f"你率领着 {'、'.join(general_names)} (总战力: {player_combat_power:.0f}) 挑战【{dungeon.name}】。\n"
        narrative += f"遭遇了强大的敌人 (战力: {enemy_combat_power:.0f})！\n"
        
        if win:
            # 胜利
            rewards = dungeon.rewards
            coin_reward = rewards.get("coins", 0)
            yuanbao_reward = rewards.get("yuanbao", 0)
            user_exp_reward = rewards.get("user_exp", 0)
            general_exp_reward = rewards.get("general_exp", 0)

            user.coins += coin_reward
            user.yuanbao += yuanbao_reward
            user.exp += user_exp_reward
            
            # 分配武将经验
            exp_per_general = 0
            if general_exp_reward > 0 and selected_generals_details:
                exp_per_general = general_exp_reward // len(selected_generals_details)
                for g in selected_generals_details:
                    self.general_repo.add_exp_to_general(g.instance_id, exp_per_general)

            self.user_repo.update(user)

            narrative += "⚔️ 激战过后，你取得了胜利！ 🎉\n\n"
            narrative += f"【奖励结算】\n"
            if coin_reward: narrative += f"💰 铜钱: +{coin_reward}\n"
            if yuanbao_reward: narrative += f"💎 元宝: +{yuanbao_reward}\n"
            if user_exp_reward: narrative += f"📈 玩家经验: +{user_exp_reward}\n"
            if general_exp_reward: narrative += f"⭐ 武将经验: +{general_exp_reward} (每位出战武将 +{exp_per_general})\n"
            
            return narrative.strip()
        else:
            # 失败
            narrative += "一番苦战，不幸落败... 💔\n"
            narrative += "请提升实力后再次挑战！"
            return narrative.strip()
