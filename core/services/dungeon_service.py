# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : dungeon_service.py
# @Software: AstrBot
# @Description: 副本服务

import random
from typing import List
from ..repositories.sqlite_dungeon_repo import DungeonRepository
from ..repositories.sqlite_user_repo import SqliteUserRepository
from ..domain.models import User

class DungeonService:
    def __init__(self, dungeon_repo: DungeonRepository, user_repo: SqliteUserRepository):
        self.dungeon_repo = dungeon_repo
        self.user_repo = user_repo

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
            
            message += f"{status_emoji} {d.name} (推荐等级: {d.recommended_level})\n"
            message += f"   - {d.description}\n\n"
        
        message += "使用 `/三国副本 [副本名称]` 来开始挑战。"
        return message.strip()

    def start_dungeon(self, user: User, dungeon_name: str) -> str:
        """开始挑战一个副本"""
        dungeon = self.dungeon_repo.get_dungeon_by_name(dungeon_name)

        if not dungeon:
            return f"未找到名为“{dungeon_name}”的副本。"

        # 1. 检查等级
        if user.level < dungeon.recommended_level:
            return f"🔒 等级不足，无法挑战【{dungeon.name}】。推荐等级: {dungeon.recommended_level}，您的等级: {user.level}。"

        # 2. 检查入场费
        if user.coins < dungeon.entry_fee:
            return f"💰 铜钱不足！进入【{dungeon.name}】需要 {dungeon.entry_fee} 铜钱，您只有 {user.coins}。"

        # 3. 扣除费用
        user.coins -= dungeon.entry_fee
        self.user_repo.update(user)

        # 4. 模拟战斗 (简化版)
        # 战斗成功率 = 50% + (玩家等级 - 推荐等级) * 5%
        success_chance = 0.5 + (user.level - dungeon.recommended_level) * 0.05
        # 确保概率在 10% 到 90% 之间
        success_chance = max(0.1, min(success_chance, 0.9)) 

        if random.random() < success_chance:
            # 挑战成功
            rewards = dungeon.rewards
            user.exp += rewards.get("exp", 0)
            user.coins += rewards.get("coins", 0)
            user.reputation += rewards.get("reputation", 0)
            self.user_repo.update(user)

            reward_messages = []
            if rewards.get("exp"): reward_messages.append(f"{rewards['exp']} 经验")
            if rewards.get("coins"): reward_messages.append(f"{rewards['coins']} 铜钱")
            if rewards.get("reputation"): reward_messages.append(f"{rewards['reputation']} 声望")
            
            message = f"🎉 恭喜！您成功挑战了【{dungeon.name}】！\n"
            message += f"获得了奖励: {', '.join(reward_messages)}。"
            return message
        else:
            # 挑战失败
            message = f"很遗憾，您在挑战【{dungeon.name}】时失败了..."
            # 失败也可能有少量安慰奖，或者没有，这里简化为没有
            return message
