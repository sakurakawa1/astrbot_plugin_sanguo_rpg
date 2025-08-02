# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : auto_battle_service.py
# @Software: AstrBot
# @Description: 自动战斗服务 (重构版)

import random
from datetime import datetime, timedelta
from astrbot.api import logger
from astrbot_plugin_sanguo_rpg.core.services.user_service import UserService
from astrbot_plugin_sanguo_rpg.core.services.dungeon_service import DungeonService
from astrbot_plugin_sanguo_rpg.core.services.general_service import GeneralService
from astrbot_plugin_sanguo_rpg.core.adventure_generator import AdventureGenerator

class AutoBattleService:
    def __init__(self, user_service: UserService, dungeon_service: DungeonService, general_service: GeneralService, game_config: dict):
        self.user_service = user_service
        self.dungeon_service = dungeon_service
        self.general_service = general_service
        self.game_config = game_config

    def run_auto_battles(self):
        """
        为所有符合条件的用户执行自动战斗
        """
        users_for_battle = self.user_service.get_all_users_with_auto_battle()
        adventure_cooldown = timedelta(minutes=self.game_config.get("adventure", {}).get("cooldown_seconds", 600) / 60)
        dungeon_cooldown = timedelta(minutes=self.game_config.get("dungeon", {}).get("cooldown_seconds", 600) / 60)

        for user in users_for_battle:
            now = datetime.now()
            
            # --- 自动闯关 ---
            if user.auto_adventure_enabled:
                last_time = user.last_adventure_time or datetime.min
                if (now - last_time) >= adventure_cooldown:
                    logger.info(f"为用户 {user.nickname} ({user.user_id}) 执行自动闯关。")
                    self._perform_auto_adventure(user)

            # --- 自动副本 ---
            if user.auto_dungeon_id:
                last_time = user.last_dungeon_time or datetime.min
                if (now - last_time) >= dungeon_cooldown:
                    logger.info(f"为用户 {user.nickname} ({user.user_id}) 执行自动副本 {user.auto_dungeon_id}。")
                    self._perform_auto_dungeon(user)

    def _perform_auto_adventure(self, user):
        """
        执行完整的、带随机选择的自动冒险流程。
        """
        # 检查用户是否已经在冒险中，如果是，则不启动新的
        if self.user_service.get_user_adventure_state(user.user_id):
            logger.warning(f"用户 {user.nickname} 已在冒险中，跳过本次自动闯关。")
            return

        # 检查费用
        cost = self.game_config.get("adventure", {}).get("cost_coins", 20)
        if user.coins < cost:
            self.general_service.add_battle_log(user.user_id, "自动闯关失败：铜钱不足。")
            return
        
        # 扣除费用
        user.coins -= cost
        self.user_service.user_repo.update(user)
        
        # 为该用户创建专用的 AdventureGenerator
        adv_gen = AdventureGenerator(user.user_id, self.user_service)
        
        # 开始冒险
        result = adv_gen.start_adventure()
        if not result or not result.get("text"):
            # 如果生成失败，回滚费用
            user.coins += cost
            self.user_service.user_repo.update(user)
            self.general_service.add_battle_log(user.user_id, "自动闯关失败：无法生成冒险故事。")
            return

        self.general_service.add_battle_log(user.user_id, f"自动闯关开始，花费 {cost} 铜钱。")
        self.general_service.add_battle_log(user.user_id, f"[自动闯关] {result['text']}")

        # 循环直到冒险结束
        max_steps = 10 # 防止无限循环
        step_count = 0
        while not result.get("is_final", False) and step_count < max_steps:
            options = result.get("options", [])
            if not options:
                break # 没有选项，冒险意外终止
            
            # 随机选择一个选项
            choice_index = random.randint(0, len(options) - 1)
            
            # 推进冒险
            result = adv_gen.advance_adventure(choice_index)
            
            # 记录日志
            log_message = f"[自动闯关] {result['text']}"
            self.general_service.add_battle_log(user.user_id, log_message)
            
            step_count += 1

        # 更新最后冒险时间
        self.user_service.update_last_adventure_time(user.user_id)
        logger.info(f"用户 {user.nickname} 的自动闯关已完成。")


    def _perform_auto_dungeon(self, user):
        """
        执行自动副本
        """
        # 获取玩家最强的武将
        generals = self.general_service.general_repo.get_user_generals_with_details(user.user_id)
        if not generals:
            self.general_service.add_battle_log(user.user_id, "自动副本失败：没有任何武将。")
            return

        dungeon = self.dungeon_service.dungeon_repo.get_by_id(user.auto_dungeon_id)
        if not dungeon:
            self.general_service.add_battle_log(user.user_id, f"自动副本失败：找不到ID为 {user.auto_dungeon_id} 的副本。")
            return
            
        # 检查等级要求
        if user.level < dungeon.required_level:
            self.general_service.add_battle_log(user.user_id, f"自动副本【{dungeon.name}】失败：等级不足，需要 {dungeon.required_level} 级。")
            return

        # 按战力排序并选择最强的几个
        generals.sort(key=lambda g: g.combat_power, reverse=True)
        
        # 根据副本最大队伍规模选择武将
        party_limit = dungeon.max_party_size
        party_ids = [g.instance_id for g in generals[:party_limit]]
        
        # 执行战斗
        result_message = self.dungeon_service.execute_battle(user.user_id, user.auto_dungeon_id, party_ids)
        
        # 更新最后副本时间
        self.user_service.update_last_dungeon_time(user.user_id)
        
        # 记录日志
        log_message = f"自动副本【{dungeon.name}】: {result_message}"
        self.general_service.add_battle_log(user.user_id, log_message)
        logger.info(f"用户 {user.nickname} 的自动副本【{dungeon.name}】已完成。")
