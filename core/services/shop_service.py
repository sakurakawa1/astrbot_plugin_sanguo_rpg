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

    def _refresh_shop_if_needed(self):
        """如果当天商店未刷新，则刷新商店商品"""
        if not self.shop_repo.has_refreshed_today():
            all_items = self.item_repo.get_all_items()
            if not all_items:
                return

            # 随机选择5-10种商品
            num_items_to_feature = random.randint(5, min(10, len(all_items)))
            featured_items = random.sample(all_items, num_items_to_feature)
            
            # 为每种商品设置随机数量
            items_with_quantities = [
                (item.id, random.randint(1, 5)) for item in featured_items
            ]
            
            self.shop_repo.refresh_shop(items_with_quantities)

    def get_shop_display(self) -> str:
        """获取商店的展示信息"""
        self._refresh_shop_if_needed()
        
        shop_items = self.shop_repo.get_today_shop_items()
        
        if not shop_items:
            return "今日商店正在补货中，请稍后再来！"
            
        display_lines = ["【今日商店】\n"]
        for shop_item_id, item, quantity in shop_items:
            price_str = f"{item.price_coins}铜钱" if item.price_coins > 0 else f"{item.price_yuanbao}元宝"
            line = (
                f"ID: {shop_item_id} | {item.name} ({item.rarity}★)\n"
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
        if item.price_coins > 0 and user.coins < item.price_coins:
            return {"message": f"铜钱不足！购买【{item.name}】需要 {item.price_coins} 铜钱，您只有 {user.coins}。"}
        if item.price_yuanbao > 0 and user.yuanbao < item.price_yuanbao:
            return {"message": f"元宝不足！购买【{item.name}】需要 {item.price_yuanbao} 元宝，您只有 {user.yuanbao}。"}

        # 尝试减少商店库存
        if not self.shop_repo.decrease_shop_item_quantity(shop_item_id):
            return {"message": f"手慢了！【{item.name}】刚刚被别人买走了。"}

        # 扣除货币
        if item.price_coins > 0:
            user.coins -= item.price_coins
        if item.price_yuanbao > 0:
            user.yuanbao -= item.price_yuanbao
        self.user_repo.update(user)
        
        # 添加到玩家库存
        self.inventory_repo.add_item_to_inventory(user_id, item.id)
        
        return {"message": f"购买成功！您获得了【{item.name}】。"}
