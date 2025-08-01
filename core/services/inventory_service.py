# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : inventory_service.py
# @Software: AstrBot
# @Description: 玩家库存相关的业务逻辑

from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_inventory_repo import InventoryRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository

class InventoryService:
    def __init__(self, inventory_repo: InventoryRepository, user_repo: SqliteUserRepository):
        self.inventory_repo = inventory_repo
        self.user_repo = user_repo

    def get_inventory_display(self, user_id: str) -> str:
        """获取玩家库存的展示信息"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return "您尚未注册，请先使用 /三国注册 命令。"

        inventory_items = self.inventory_repo.get_user_inventory(user_id)
        
        if not inventory_items:
            return "您的背包空空如也。"
            
        display_lines = [f"【{user.name}的背包】\n"]
        for item, quantity in inventory_items:
            line = (
                f"物品: {item.name} (ID: {item.id}) | 数量: {quantity}\n"
                f"稀有度: {item.rarity}★ | 效果: {item.description}"
            )
            display_lines.append(line)
            
        return "\n".join(display_lines)
