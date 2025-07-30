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
from astrbot_plugin_sanguo_rpg.core.adventure_templates import ADVENTURE_TEMPLATES
class GeneralService:
    """武将业务服务"""
    
    def __init__(self, general_repo: SqliteGeneralRepository, user_repo: SqliteUserRepository, config: dict):
        self.general_repo = general_repo
        self.user_repo = user_repo
        self.config = config
        
        # 招募冷却时间缓存
        self._recruit_cooldowns = {}
        
        # 闯关冷却时间缓存
        self._adventure_cooldowns = {}
    
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
        
        # 随机获取武将
        recruited_general = self.general_repo.get_random_general_by_rarity_pool()
        if not recruited_general:
            return {
                "success": False,
                "message": "❌ 招募失败，请稍后再试。"
            }
        
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
    
    def adventure(self, user_id: str, option_index: int = -1, auto: bool = False) -> Dict:
        """闯关功能"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"success": False, "message": "您尚未注册，请先使用 /注册 命令。"}

        user_generals = self.general_repo.get_user_generals(user_id)
        if not user_generals:
            return {"success": False, "message": "您还没有任何武将，请先进行招募！"}

        # 检查闯关冷却时间
        cooldown_key = f"adventure_{user_id}"
        current_time = datetime.now()
        
        if cooldown_key in self._adventure_cooldowns:
            last_adventure_time = self._adventure_cooldowns[cooldown_key]
            cooldown_seconds = self.config.get("adventure", {}).get("cooldown_seconds", 600)
            time_diff = (current_time - last_adventure_time).total_seconds()
            
            if time_diff < cooldown_seconds:
                remaining_time = int(cooldown_seconds - time_diff)
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                return {
                    "success": False,
                    "message": f"⏰ 闯关冷却中，还需等待 {minutes}分{seconds}秒后才能再次闯关。"
                }

        template = random.choice(ADVENTURE_TEMPLATES)
        
        if auto:
            option_index = random.randint(0, len(template['options']) - 1)

        if option_index == -1:
            options_text = "\n".join([f"{i+1}. {opt['text']}" for i, opt in enumerate(template['options'])])
            return {
                "success": True,
                "message": f"【{template['name']}】\n{template['description']}\n\n请选择：\n{options_text}",
                "requires_follow_up": True,
                "adventure_id": template['id']
            }
        else:
            # 处理玩家的选择
            option = template['options'][option_index]
            
            # 获取出战武将
            active_generals = self.general_repo.get_user_generals(user_id)[:3]
            
            # 计算技能加成
            success_rate_bonus = 0
            coin_bonus_multiplier = 1.0
            exp_bonus_multiplier = 1.0
            
            for ug in active_generals:
                g = self.general_repo.get_general_by_id(ug.general_id)
                if g and g.skill_desc != "无":
                    # 解析技能描述
                    bonuses = re.findall(r"(\w+)增加(\d+)%", g.skill_desc)
                    for bonus_type, bonus_value in bonuses:
                        if "成功率" in bonus_type:
                            success_rate_bonus += int(bonus_value) / 100
                        elif "金币" in bonus_type:
                            coin_bonus_multiplier += int(bonus_value) / 100
                        elif "经验" in bonus_type:
                            exp_bonus_multiplier += int(bonus_value) / 100
            
            success_rate = option['success_rate'] + success_rate_bonus
            success = random.random() < success_rate
            
            if success:
                rewards = option['rewards']
                coins_reward = int(rewards.get('coins', 0) * coin_bonus_multiplier)
                exp_reward = int(rewards.get('exp', 0) * exp_bonus_multiplier)
                
                user.coins += coins_reward
                # Assuming user has exp attribute
                # user.exp += exp_reward
                self.user_repo.update(user)
                
                reward_text = []
                if coins_reward != 0:
                    reward_text.append(f"{coins_reward} 铜钱")
                if exp_reward != 0:
                    reward_text.append(f"{exp_reward} 经验")
                
                self._adventure_cooldowns[cooldown_key] = current_time
                return {
                    "success": True,
                    "message": f"【{template['name']}】\n成功！你获得了 {'、'.join(reward_text)}。"
                }
            else:
                # 失败惩罚
                self._adventure_cooldowns[cooldown_key] = current_time + timedelta(minutes=5) # 增加5分钟冷却
                return {
                    "success": True,
                    "message": f"【{template['name']}】\n{option['failure_text']}\n闯关冷却时间增加5分钟。"
                }
    
    def auto_adventure(self, user_id: str) -> Dict:
        """挂机闯关"""
        return self.adventure(user_id, auto=True)
