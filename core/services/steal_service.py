# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta
from typing import Dict, Any, TYPE_CHECKING

from ..repositories.sqlite_user_repo import SqliteUserRepository
from ..repositories.sqlite_inventory_repo import InventoryRepository
from ..services.inventory_service import InventoryService
from ..domain.models import User
if TYPE_CHECKING:
    from .general_service import GeneralService


class StealService:
    def __init__(
        self,
        user_repo: SqliteUserRepository,
        inventory_repo: InventoryRepository,
        inventory_service: InventoryService,
        general_service: "GeneralService",
        game_config: Dict[str, Any]
    ):
        self.user_repo = user_repo
        self.inventory_repo = inventory_repo
        self.inventory_service = inventory_service
        self.general_service = general_service
        self.game_config = game_config

    def attempt_steal(self, thief_id: str, target_id: str) -> Dict[str, Any]:
        """
        尝试从目标处偷窃。

        Args:
            thief_id: 偷窃者的用户ID。
            target_id: 目标的用户ID。

        Returns:
            一个包含操作结果的字典。
        """
        thief = self.user_repo.get_by_id(thief_id)
        target = self.user_repo.get_by_id(target_id)

        if not thief:
            return {"success": False, "message": "您尚未注册，无法进行偷窃。"}
        if not target:
            return {"success": False, "message": "目标用户不存在。"}
        
        if thief_id == target_id:
            return {"success": False, "message": "不能偷窃自己。"}

        # Cooldown check
        cooldown_seconds = self.game_config.get("steal_cooldown", 300)  # 5 minutes
        if thief.last_steal_time:
            time_since_last_steal = datetime.now() - thief.last_steal_time
            if time_since_last_steal < timedelta(seconds=cooldown_seconds):
                remaining_time = cooldown_seconds - time_since_last_steal.total_seconds()
                return {
                    "success": False,
                    "message": f"偷窃技能冷却中，请等待 {int(remaining_time // 60)} 分钟 {int(remaining_time % 60)} 秒后再试。"
                }

        thief.last_steal_time = datetime.now()
        result = {}

        # 1. 成功率判断 (50% 成功率)
        if random.random() < 0.5:
            # 失败逻辑
            backlash_coins = random.randint(10, 50)
            thief.coins = max(0, thief.coins - backlash_coins)
            result = {
                "success": False,
                "message": f"偷窃失败！你被发现了，并被罚款 {backlash_coins} 铜钱。"
            }
        else:
            # 2. 成功逻辑
            target_inventory = self.inventory_repo.get_user_inventory(target_id)
            
            # 优先偷窃物品
            if target_inventory:
                stolen_item = random.choice(target_inventory)
                
                # 从目标移除物品
                self.inventory_repo.remove_item_from_inventory(target_id, stolen_item.item_id, 1)
                # 向盗贼添加物品
                self.inventory_repo.add_item_to_inventory(thief_id, stolen_item.item_id, 1)
                
                result = {
                    "success": True,
                    "message": f"偷窃成功！你从 {target.nickname} 那里偷到了【{stolen_item.item.name}】x1。"
                }
            else:
                result = self._steal_currency(thief, target)
        
        # 记录日志
        log_message = f"对 {target.nickname} {result['message']}"
        self.general_service.add_battle_log(thief_id, "偷窃", log_message)
        
        self.user_repo.update(thief)
        return result

    def _steal_currency(self, thief: User, target: User) -> Dict[str, Any]:
        """处理偷窃金钱的逻辑"""
        # 随机决定偷铜钱还是元宝
        if random.random() < 0.8: # 80% 概率偷铜钱
            max_steal = int(target.coins * 0.1)
            if max_steal > 0:
                amount = random.randint(1, max_steal)
                target.coins -= amount
                thief.coins += amount
                self.user_repo.update(target)
                return {
                    "success": True,
                    "message": f"你发现 {target.nickname} 背包空空如也，但还是成功偷到了 {amount} 铜钱。"
                }
        else: # 20% 概率偷元宝
            max_steal = int(target.yuanbao * 0.05)
            if max_steal > 0:
                amount = random.randint(1, max_steal)
                target.yuanbao -= amount
                thief.yuanbao += amount
                self.user_repo.update(target)
                return {
                    "success": True,
                    "message": f"你发现 {target.nickname} 背包空空如也，但还是成功偷到了 {amount} 元宝。"
                }
        
        return {
            "success": True, # It's a success, but nothing was stolen
            "message": f"你成功接近了 {target.nickname}，但他身无分文，你一无所获。"
        }
