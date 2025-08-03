# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : general_service.py
# @Software: AstrBot
# @Description: 武将相关的业务逻辑服务

import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_general_repo import SqliteGeneralRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
from astrbot_plugin_sanguo_rpg.core.domain.models import General, UserGeneral
from astrbot_plugin_sanguo_rpg.core.adventure_generator import AdventureGenerator
from astrbot_plugin_sanguo_rpg.core.services.user_service import UserService


class GeneralService:
    """武将业务服务"""
    
    def __init__(self, general_repo: SqliteGeneralRepository, user_repo: SqliteUserRepository, user_service: UserService, config: dict):
        self.general_repo = general_repo
        self.user_repo = user_repo
        self.user_service = user_service
        self.config = config
        
        # 招募冷却时间缓存
        self._recruit_cooldowns = {}

    def add_battle_log(self, user_id: str, log_type: str, log_details: str):
        """
        添加战斗日志，这是一个对 astra_repo 方法的封装，以简化服务层代码。
        """
        self.general_repo.add_battle_log(user_id=user_id, log_type=log_type, log_details=log_details)

    def set_battle_generals(self, user_id: str, general_instance_ids: List[int]) -> Dict:
        """设置玩家的出战武将"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "找不到用户。"}

        # 验证玩家是否拥有这些武将
        owned_generals = self.general_repo.get_user_generals_by_instance_ids(user_id, general_instance_ids)
        owned_instance_ids = {g.instance_id for g in owned_generals}

        if len(owned_instance_ids) != len(general_instance_ids):
            missing_ids = set(general_instance_ids) - owned_instance_ids
            return {"success": False, "message": f"您不拥有以下武将ID: {', '.join(map(str, missing_ids))}"}

        # 更新用户的出战武将列表
        import json
        user.battle_generals = json.dumps(general_instance_ids)
        self.user_repo.update(user)

        general_names = self.general_repo.get_generals_names_by_instance_ids(general_instance_ids)
        return {"success": True, "message": f"已成功设置出战武将: {', '.join(general_names)}"}
    
    def get_user_generals_info(self, user_id: str) -> Dict:
        """获取玩家武将信息"""
        user_generals = self.general_repo.get_user_generals(user_id)
        
        if not user_generals:
            return {
                "success": False,
                "message": "您还没有任何武将，请先进行招募！\n使用 /招募 来获取您的第一个武将。"
            }
        
        # 构建武将详细信息
        general_info_list = []
        for user_general in user_generals:
            general_template = self.general_repo.get_general_by_id(user_general.general_id)
            if general_template:
                # 计算等级加成后的属性
                level_bonus = (user_general.level - 1) * 0.1  # 每级提升10%
                wu_li = int(general_template.wu_li * (1 + level_bonus))
                zhi_li = int(general_template.zhi_li * (1 + level_bonus))
                tong_shuai = int(general_template.tong_shuai * (1 + level_bonus))
                su_du = int(general_template.su_du * (1 + level_bonus))
                
                rarity_stars = "⭐" * general_template.rarity
                camp_emoji = {"蜀": "🟢", "魏": "🔵", "吴": "🟡", "群": "🔴"}.get(general_template.camp, "⚪")
                
                general_info = f"""
{camp_emoji} {general_template.name} {rarity_stars}
等级：{user_general.level} | 经验：{user_general.exp}/100
武力：{wu_li} | 智力：{zhi_li}
统帅：{tong_shuai} | 速度：{su_du}
技能：{general_template.skill_desc}
背景：{general_template.background}
获得时间：{user_general.created_at.strftime('%Y-%m-%d %H:%M')}
"""
                general_info_list.append(general_info.strip())
        
        total_count = len(user_generals)
        message = f"📜 【我的武将】({total_count}个)\n\n" + "\n\n".join(general_info_list)
        
        return {
            "success": True,
            "message": message,
            "count": total_count
        }
    
    def recruit_general(self, user_id: str) -> Dict:
        """招募武将"""
        # 检查用户是否存在
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {
                "success": False,
                "message": "请先使用 /注册 命令注册账户！"
            }
        
        # 检查招募冷却时间
        cooldown_key = f"recruit_{user_id}"
        current_time = datetime.now()
        
        if cooldown_key in self._recruit_cooldowns:
            last_recruit_time = self._recruit_cooldowns[cooldown_key]
            cooldown_seconds = self.config.get("recruit", {}).get("cooldown_seconds", 300)  # 默认5分钟
            time_diff = (current_time - last_recruit_time).total_seconds()
            
            if time_diff < cooldown_seconds:
                remaining_time = int(cooldown_seconds - time_diff)
                return {
                    "success": False,
                    "message": f"⏰ 招募冷却中，还需等待 {remaining_time} 秒后才能再次招募。"
                }
        
        # 检查元宝是否足够
        recruit_cost = self.config.get("recruit", {}).get("cost_yuanbao", 50)
        if user.yuanbao < recruit_cost:
            return {
                "success": False,
                "message": f"💎 元宝不足！招募需要 {recruit_cost} 元宝，您当前只有 {user.yuanbao} 元宝。"
            }
        
        # 保底系统
        pity_5_star_trigger = self.config.get("gacha", {}).get("pity_5_star", 80) - 1
        pity_4_star_trigger = self.config.get("gacha", {}).get("pity_4_star", 10) - 1

        if user.pity_5_star_count >= pity_5_star_trigger:
            recruited_general = self.general_repo.get_random_general_by_rarity(5)
        elif user.pity_4_star_count >= pity_4_star_trigger:
            recruited_general = self.general_repo.get_random_general_by_rarity(4)
        else:
            # 随机获取武将
            recruited_general = self.general_repo.get_random_general_by_rarity_pool()

        if not recruited_general:
            return {
                "success": False,
                "message": "❌ 招募失败，卡池暂无武将，请联系管理员。"
            }
        
        # 更新保底计数
        self.user_service.update_pity_counters(user_id, recruited_general.rarity)
        
        # 扣除元宝
        new_yuanbao = user.yuanbao - recruit_cost
        self.user_repo.update_user_yuanbao(user_id, new_yuanbao)
        
        # 添加武将到玩家账户
        success = self.general_repo.add_user_general(user_id, recruited_general.general_id)
        if not success:
            # 招募失败，退还元宝
            self.user_repo.update_user_yuanbao(user_id, user.yuanbao)
            return {
                "success": False,
                "message": "❌ 招募失败，请稍后再试。"
            }
        
        # 更新冷却时间
        self._recruit_cooldowns[cooldown_key] = current_time
        
        # 构建成功消息
        rarity_stars = "⭐" * recruited_general.rarity
        camp_emoji = {"蜀": "🟢", "魏": "🔵", "吴": "🟡", "群": "🔴"}.get(recruited_general.camp, "⚪")
        
        # 根据稀有度显示不同的效果
        if recruited_general.rarity >= 5:
            effect = "✨🎉 传说降临！🎉✨"
        elif recruited_general.rarity >= 4:
            effect = "🌟 稀有出现！🌟"
        elif recruited_general.rarity >= 3:
            effect = "💫 精英到来！"
        else:
            effect = "⚡ 新的伙伴！"
        
        message = f"""
{effect}

{camp_emoji} {recruited_general.name} {rarity_stars}
阵营：{recruited_general.camp}
武力：{recruited_general.wu_li} | 智力：{recruited_general.zhi_li}
统帅：{recruited_general.tong_shuai} | 速度：{recruited_general.su_du}
技能：{recruited_general.skill_desc}

💰 花费：{recruit_cost} 元宝
💎 剩余元宝：{new_yuanbao}

使用 /我的武将 查看所有武将！
"""
        
        return {
            "success": True,
            "message": message.strip(),
            "general": recruited_general,
            "cost": recruit_cost
        }
    
    def _generate_adventure_settlement(self, cost: int, reward_result: dict) -> str:
        """
        根据奖励应用结果生成格式化的结算文本。
        """
        actual_rewards = reward_result.get("actual_rewards", {})
        level_up_message = reward_result.get("level_up_message")

        settlement_parts = []
        
        # 花费始终显示
        settlement_parts.append(f"闯关花费: -{cost} 铜钱")

        # 各种奖励
        coins_reward = actual_rewards.get("coins", 0)
        if coins_reward > 0:
            settlement_parts.append(f"获得铜钱: +{coins_reward}")

        lord_exp_reward = actual_rewards.get("lord_exp", 0)
        if lord_exp_reward > 0:
            settlement_parts.append(f"主公经验: +{lord_exp_reward}")

        rep_reward = actual_rewards.get("reputation", 0)
        if rep_reward != 0:
            settlement_parts.append(f"声望: {rep_reward:^+}")

        if actual_rewards.get("items"):
            settlement_parts.append(f"获得物品: {', '.join(actual_rewards['items'])}")

        health_change = actual_rewards.get("health", 0)
        if health_change != 0:
            settlement_parts.append(f"血量变化: {health_change:^+}")

        # 计算净收益
        net_gain = coins_reward - cost
        
        settlement_block = "\n--- 结算 ---\n"
        settlement_block += "\n".join(settlement_parts)
        settlement_block += f"\n===============\n本次净赚: {net_gain} 铜钱"

        if level_up_message:
            settlement_block += f"\n\n{level_up_message}"
            
        return settlement_block

    def adventure(self, user_id: str, option_index: int = -1, is_auto: bool = False) -> Dict:
        """
        处理单次闯关的完整逻辑。
        - is_auto: True表示为自动闯关，遇到选择时会自动处理。
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "您尚未注册，请先使用 /三国注册 命令。"}

        adv_gen = AdventureGenerator(user_id, self.user_service)
        
        # --- 自动闯关模式 ---
        if is_auto:
            # 检查成本
            cost = self.config.get("adventure", {}).get("cost_coins", 20)
            if user.coins < cost:
                return {"success": False, "message": f"💰 铜钱不足！闯关需要 {cost} 铜钱，您只有 {user.coins}。"}

            # 开始新冒险
            result = adv_gen.start_adventure()
            if not (result and result.get("text")):
                return {"success": False, "message": "❌ 冒险故事生成失败，请稍后再试。"}
            
            # 循环处理直到冒险结束
            while not result.get("is_final"):
                # 随机选择一个选项
                options = result.get("options", [])
                if not options:
                    # 如果没有选项但不是最终事件，说明逻辑有误，中断以防死循环
                    self.user_service.clear_user_adventure_state(user_id)
                    return {"success": False, "message": "冒险中遇到意外情况，已中断。"}
                
                auto_choice = random.randint(0, len(options) - 1)
                result = adv_gen.advance_adventure(auto_choice)
                if not result:
                    self.user_service.clear_user_adventure_state(user_id)
                    return {"success": False, "message": "自动选择时出错，已中断。"}
            
            # 冒险结束，进入结算
            response_message = result["text"]
            log_message = result["text"]
            
            rewards = result.get("rewards", {}).copy()
            reward_application_result = self.user_service.apply_adventure_rewards(user_id, rewards, cost)
            settlement_block = self._generate_adventure_settlement(cost=cost, reward_result=reward_application_result)
            
            response_message += settlement_block

            final_user = self.user_repo.get_by_id(user_id)
            if final_user:
                response_message += f"\n\n【当前状态】\n铜钱: {final_user.coins} | 主公经验: {final_user.lord_exp} | 声望: {final_user.reputation}"

            self.user_service.clear_user_adventure_state(user_id)
            self.add_battle_log(user_id=user_id, log_type="闯关", log_details=log_message)
            
            return {"success": True, "message": response_message, "requires_follow_up": False}

        # --- 手动闯关模式 ---
        current_state = self.user_service.active_adventures.get(user_id)
        
        # 场景1: 玩家在冒险中
        if current_state:
            if option_index != -1:
                result = adv_gen.advance_adventure(option_index)
                if not result:
                    return {"success": False, "message": "处理您的选择时出错。"}
            else: # 提示用户选择
                story_text = current_state.get("story_text", "你正面临一个抉择...")
                options = current_state.get("options", [])
                options_text = [f"{i+1}. {opt['text']}" for i, opt in enumerate(options)]
                message = f"【冒险进行中】\n{story_text}\n\n请做出您的选择:\n" + "\n".join(options_text) + f"\n\n使用 `/三国闯关 [选项编号]` 来决定您的行动。"
                return {"success": True, "message": message, "requires_follow_up": True}
        
        # 场景2: 玩家不在冒险中，开始新冒险
        else:
            cooldown_seconds = self.config.get("adventure", {}).get("cooldown_seconds", 600)
            if user.last_adventure_time and (datetime.now() - user.last_adventure_time).total_seconds() < cooldown_seconds:
                remaining_time = int(cooldown_seconds - (datetime.now() - user.last_adventure_time).total_seconds())
                return {"success": False, "message": f"⚔️ 闯关冷却中，还需等待 {remaining_time} 秒。"}

            cost = self.config.get("adventure", {}).get("cost_coins", 20)
            if user.coins < cost:
                return {"success": False, "message": f"💰 铜钱不足！闯关需要 {cost} 铜钱，您只有 {user.coins}。"}

            result = adv_gen.start_adventure()
            if not (result and result.get("text")):
                return {"success": False, "message": "❌ 冒险故事生成失败，请稍后再试。"}

        # --- 手动模式结果处理 ---
        if not result:
             return {"success": False, "message": "❌ 冒险时发生未知错误。"}

        response_message = result["text"]
        log_message = result["text"]

        if not result["is_final"]:
            options = result.get("options", [])
            options_text = [f"{i+1}. {opt['text']}" for i, opt in enumerate(options)]
            response_message += "\n\n请做出您的选择:\n" + "\n".join(options_text) + f"\n\n使用 `/三国闯关 [选项编号]` 来决定您的行动。"
        else:
            # 最终事件，进行结算
            rewards = result.get("rewards", {}).copy()
            cost = self.config.get("adventure", {}).get("cost_coins", 20)
            
            reward_application_result = self.user_service.apply_adventure_rewards(user_id, rewards, cost)
            settlement_block = self._generate_adventure_settlement(cost=cost, reward_result=reward_application_result)
            
            response_message += settlement_block

            final_user = self.user_repo.get_by_id(user_id)
            if final_user:
                response_message += f"\n\n【当前状态】\n铜钱: {final_user.coins} | 主公经验: {final_user.lord_exp} | 声望: {final_user.reputation}"

            self.user_service.clear_user_adventure_state(user_id)
            self.add_battle_log(user_id=user_id, log_type="闯关", log_details=log_message)
            self.user_repo.update_last_adventure_time(user_id)

        return {
            "success": True,
            "message": response_message,
            "requires_follow_up": not result["is_final"]
        }

    def get_daily_adventure_logs(self, user_id: str) -> List[dict]:
        """获取每日闯关日志，返回带有时间和内容的字典列表"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        logs = self.general_repo.get_battle_logs_since(user_id, today_start, log_type="闯关")
        return [{"time": log.created_at, "details": log.log_details} for log in logs]

    def get_daily_dungeon_logs(self, user_id: str) -> List[dict]:
        """获取每日副本日志，返回带有时间和内容的字典列表"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        logs = self.general_repo.get_battle_logs_since(user_id, today_start, log_type="副本")
        return [{"time": log.created_at, "details": log.log_details} for log in logs]
