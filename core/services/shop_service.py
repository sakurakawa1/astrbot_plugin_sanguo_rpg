# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : shop_service.py
# @Software: AstrBot
# @Description: 商店相关的业务逻辑

import random
from typing import Dict

from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_shop_repo import ShopRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_item_repo import ItemRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_inventory_repo import InventoryRepository

class ShopService:
    def __init__(self, shop_repo: ShopRepository, user_repo: SqliteUserRepository, item_repo: ItemRepository, inventory_repo: InventoryRepository):
        self.shop_repo = shop_repo
        self.user_repo = user_repo
        self.item_repo = item_repo
        self.inventory_repo = inventory_repo

    def get_shop_display(self) -> str:
        """
        获取商店的展示信息。
        如果当天商店为空，则会自动刷新。
        """
        shop_items = self.shop_repo.get_today_shop_items()
        
        # 如果商店为空（无论是未刷新还是已售罄），则刷新
        if not shop_items:
            self.shop_repo.refresh_shop()
            shop_items = self.shop_repo.get_today_shop_items() # 再次获取
            
            if not shop_items:
                return "今日商店正在补货中，请稍后再来！(如果持续出现此问题，请联系管理员检查物品列表)"
            
        display_lines = ["【今日商店】\n"]
        for shop_item_id, item, quantity in shop_items:
            price_str = f"{item.base_price_coins}铜钱" if item.base_price_coins > 0 else f"{item.base_price_yuanbao}元宝"
            line = (
                f"ID: {shop_item_id} | {item.name} ({item.quality})\n"
                f"效果: {item.description}\n"
                f"价格: {price_str} | 剩余: {quantity}\n"
            )
            display_lines.append(line)
            
        display_lines.append("使用 `/三国购买 [商品ID]` 来购买商品。")
        return "\n".join(display_lines)

    def purchase_item(self, user_id: str, shop_item_id: int) -> Dict[str, str]:
        """处理玩家购买商品"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"message": "您尚未注册，请先使用 /三国注册 命令。"}

        shop_item_details = self.shop_repo.get_shop_item_by_id(shop_item_id)
        if not shop_item_details:
            return {"message": "该商品不存在或已售罄。"}
            
        item, remaining_quantity = shop_item_details
        
        if remaining_quantity <= 0:
            return {"message": f"抱歉，【{item.name}】已售罄。"}

        # 检查货币
        if item.base_price_coins > 0 and user.coins < item.base_price_coins:
            return {"message": f"铜钱不足！购买【{item.name}】需要 {item.base_price_coins} 铜钱，您只有 {user.coins}。"}
        if item.base_price_yuanbao > 0 and user.yuanbao < item.base_price_yuanbao:
            return {"message": f"元宝不足！购买【{item.name}】需要 {item.base_price_yuanbao} 元宝，您只有 {user.yuanbao}。"}

        # 尝试减少商店库存
        if not self.shop_repo.decrease_shop_item_quantity(shop_item_id):
            return {"message": f"手慢了！【{item.name}】刚刚被别人买走了。"}

        # 扣除货币
        if item.base_price_coins > 0:
            user.coins -= item.base_price_coins
        if item.base_price_yuanbao > 0:
            user.yuanbao -= item.base_price_yuanbao
        self.user_repo.update(user)
        
        # 添加到玩家库存
        self.inventory_repo.add_item_to_inventory(user_id, item.id)
        
        return {"message": f"购买成功！您获得了【{item.name}】。"}

    def sell_item(self, user_id: str, item_id: int, quantity: int) -> Dict[str, str]:
        """处理玩家出售物品"""
        if quantity <= 0:
            return {"message": "出售数量必须大于0。"}

        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"message": "您尚未注册，请先使用 /三国注册 命令。"}

        # 检查玩家是否拥有足够数量的物品
        inventory_item = self.inventory_repo.get_item_in_inventory(user_id, item_id)
        if not inventory_item or inventory_item.quantity < quantity:
            return {"message": f"您的背包中没有足够数量的该物品。"}

        item = inventory_item.item

        # 计算总售价 (例如，按基础价格的50%回收)
        sell_price_per_item = item.base_price_coins // 2
        total_sell_price = sell_price_per_item * quantity

        if total_sell_price <= 0 and item.base_price_coins > 0:
             total_sell_price = quantity # 至少卖1块钱

        if item.base_price_coins == 0:
            return {"message": f"【{item.name}】是无价之宝，无法出售。"}

        # 从玩家库存中移除物品
        if not self.inventory_repo.remove_item_from_inventory(user_id, item_id, quantity):
            return {"message": "出售失败，物品数量不足。"} # 理论上不应该发生，因为前面检查过了
        
        # 增加玩家的铜钱
        user.coins += total_sell_price
        self.user_repo.update(user)
        
        return {
            "message": f"成功出售 {quantity} 个【{item.name}】，获得 {total_sell_price} 铜钱。\n您当前拥有 {user.coins} 铜钱。"
        }
