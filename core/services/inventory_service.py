# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : inventory_service.py
# @Software: AstrBot
# @Description: 玩家库存相关的业务逻辑

import json
import random
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_inventory_repo import InventoryRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_item_repo import ItemRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_general_repo import SqliteGeneralRepository
from astrbot_plugin_sanguo_rpg.core.domain.models import User

class InventoryService:
    def __init__(self, inventory_repo: InventoryRepository, user_repo: SqliteUserRepository, item_repo: ItemRepository, general_repo: SqliteGeneralRepository):
        self.inventory_repo = inventory_repo
        self.user_repo = user_repo
        self.item_repo = item_repo
        self.general_repo = general_repo

    def _generate_dynamic_item_properties(self, user: User) -> dict:
        """根据用户最高等级武将生成动态物品属性"""
        highest_general = self.general_repo.get_highest_level_general_by_user(user.user_id)
        lvtop = highest_general.level if highest_general else user.level

        # 价值计算，上下浮动20%
        yuanbao_value = round(lvtop * random.uniform(0.8, 1.2))
        coins_value = round(lvtop * 10 * random.uniform(0.8, 1.2))
        exp_value = round(lvtop * random.uniform(0.8, 1.2))

        description = f"一件凡品，使用后可获得约 {exp_value} 经验，或出售换取 {coins_value} 铜钱或 {yuanbao_value} 元宝。"

        return {
            "quality": "白",
            "description": description,
            "effects": {
                "sell_coins": coins_value,
                "sell_yuanbao": yuanbao_value,
                "use_exp": exp_value
            }
        }

    def add_item(self, user_id: str, item_id: int, quantity: int = 1, is_dynamic: bool = False):
        """
        向玩家库存中添加物品。
        如果 is_dynamic 为 True，则会生成动态属性。
        """
        instance_properties = None
        if is_dynamic:
            user = self.user_repo.get_by_id(user_id)
            if user:
                instance_properties = self._generate_dynamic_item_properties(user)

        self.inventory_repo.add_item_to_inventory(
            user_id=user_id,
            item_id=item_id,
            quantity=quantity,
            instance_properties=instance_properties
        )

    def get_inventory_display(self, user_id: str) -> str:
        """获取玩家库存的展示信息"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return "您尚未注册，请先使用 /三国注册 命令。"

        inventory_items = self.inventory_repo.get_user_inventory(user_id)
        
        if not inventory_items:
            return "您的背包空空如也。"
            
        display_lines = [f"【{user.nickname}的背包】"]
        for inv_item in inventory_items:
            # 优先显示实例描述，否则显示基础描述
            description = inv_item.description
            
            line = (
                f"【{inv_item.name}】(ID: {inv_item.inventory_id}) | 数量: {inv_item.quantity}\n"
                f"  品质: {inv_item.quality}\n"
                f"  效果: {description}"
            )
            display_lines.append(line)
            
        return "\n".join(display_lines)

    def _apply_item_effects(self, user: User, effects: dict) -> list:
        """应用物品效果并返回反馈消息列表"""
        feedback_messages = []
        
        # 资源增益
        if 'add_coins' in effects:
            amount = effects['add_coins']
            user.coins += amount
            feedback_messages.append(f"获得了 {amount} 铜钱")
        if 'add_yuanbao' in effects:
            amount = effects['add_yuanbao']
            user.yuanbao += amount
            feedback_messages.append(f"获得了 {amount} 元宝")
        if 'add_exp' in effects:
            amount = effects['add_exp']
            user.exp += amount
            feedback_messages.append(f"增加了 {amount} 经验")
        if 'add_reputation' in effects:
            amount = effects['add_reputation']
            user.reputation += amount
            feedback_messages.append(f"增加了 {amount} 声望")

        # 兼容旧的 'use_exp'
        if 'use_exp' in effects and 'add_exp' not in effects:
            amount = effects['use_exp']
            user.exp += amount
            feedback_messages.append(f"经验增加了 {amount} 点")

        # 恢复类
        if 'health' in effects:
            max_health = getattr(user, 'max_health', 100)
            heal_amount = effects['health']
            original_health = user.health
            user.health = min(max_health, user.health + heal_amount)
            healed = user.health - original_health
            if healed > 0:
                feedback_messages.append(f"恢复了 {healed} 点体力")
        
        return feedback_messages

    def use_item(self, user_id: str, inventory_id: int) -> str:
        """使用背包中的物品"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return "您尚未注册，请先使用 /三国注册 命令。"

        inventory_item = self.inventory_repo.get_item_in_inventory_by_instance_id(inventory_id)
        if not inventory_item or inventory_item.user_id != user_id:
            return "您的背包中没有这个物品。"

        if not inventory_item.item.is_consumable:
            return f"【{inventory_item.name}】不是消耗品，无法使用。"

        effects = inventory_item.effects
        if not effects:
            return f"【{inventory_item.name}】似乎没有特殊效果，无法使用。"

        feedback_messages = self._apply_item_effects(user, effects)

        if not feedback_messages:
            return f"您使用了【{inventory_item.name}】，但似乎什么也没发生。"

        self.user_repo.update(user)
        # 从库存中移除一个该物品
        self.inventory_repo.remove_item_from_inventory(inventory_id=inventory_item.inventory_id)

        return f"您使用了【{inventory_item.name}】！\n" + "，".join(feedback_messages) + "。"
