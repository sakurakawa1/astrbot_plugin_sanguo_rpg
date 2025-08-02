# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : main.py
# @Software: AstrBot
# @Description: 三国文字RPG插件主文件 (最终修复版 - 桩函数调试)

import os
import random
import sqlite3
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star
from astrbot.core.star.filter.permission import PermissionType

from astrbot_plugin_sanguo_rpg.core.database.migration import run_migrations
from astrbot_plugin_sanguo_rpg.core.database.seed_items import seed_items_data
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_general_repo import SqliteGeneralRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_general_repo import SqliteUserGeneralRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_title_repo import SqliteTitleRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_dungeon_repo import DungeonRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_item_repo import ItemRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_inventory_repo import InventoryRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_shop_repo import ShopRepository
from astrbot_plugin_sanguo_rpg.core.services.data_setup_service import DataSetupService
from astrbot_plugin_sanguo_rpg.core.services.leveling_service import LevelingService
from astrbot_plugin_sanguo_rpg.core.services.dungeon_service import DungeonService
from astrbot_plugin_sanguo_rpg.core.services.user_service import UserService
from astrbot_plugin_sanguo_rpg.core.services.shop_service import ShopService
from astrbot_plugin_sanguo_rpg.core.services.inventory_service import InventoryService
from astrbot_plugin_sanguo_rpg.core.services.general_service import GeneralService
from astrbot_plugin_sanguo_rpg.core.services.steal_service import StealService
from astrbot_plugin_sanguo_rpg.core.services.auto_battle_service import AutoBattleService
from astrbot_plugin_sanguo_rpg.core.adventure_generator import AdventureGenerator
from astrbot_plugin_sanguo_rpg.draw.help import draw_help_image
from astrbot_plugin_sanguo_rpg.core.domain.models import User

class SanGuoRPGPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        timestamp = datetime.now().strftime("%H:%M:%S")
        logger.info(f"三国RPG插件加载中... (V2 - {timestamp})")

        # --- 1. 加载配置 ---
        self.game_config = {
            "user": {
                "initial_coins": 50,
                "initial_yuanbao": 50,
                "initial_health": 100,
                "initial_attack": 10,
                "initial_defense": 5,
                "initial_max_health": 100
            },
            "recruit": { "cost_yuanbao": 50, "cooldown_seconds": 300 },
            "adventure": { "cost_coins": 20, "cooldown_seconds": 600 },
            "dungeon": { "cooldown_seconds": 600 },
            "steal": { "cooldown_seconds": 300 }
        }

        # --- 2. 数据库和基础数据初始化 (使用绝对路径) ---
        plugin_root_dir = os.path.dirname(os.path.abspath(__file__))
        # 数据库路径指向插件目录的父级目录下的 data 目录
        data_dir = os.path.abspath(os.path.join(plugin_root_dir, "..", "data"))
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "sanguo_rpg.db")
        self.migrations_path = os.path.join(plugin_root_dir, "core", "database", "migrations")
        
        logger.info(f"数据库绝对路径: {self.db_path}")

        # --- 2.5. 运行数据库迁移并验证 ---
        try:
            run_migrations(self.db_path, self.migrations_path)
            logger.info("数据库迁移检查完成。")
            # 填充初始数据
            seed_items_data(self.db_path)
            self._verify_and_heal_db()

        except Exception as e:
            logger.error(f"在 __init__ 期间执行数据库迁移或验证时出错: {e}")

        # --- 3. 组合根：实例化仓储和服务 ---
        self.user_repo = SqliteUserRepository(self.db_path)
        self.general_repo = SqliteGeneralRepository(self.db_path)
        self.user_general_repo = SqliteUserGeneralRepository(self.db_path)
        self.title_repo = SqliteTitleRepository(self.db_path)
        self.dungeon_repo = DungeonRepository(self.db_path)
        self.item_repo = ItemRepository(self.db_path)
        self.inventory_repo = InventoryRepository(self.db_path)
        self.shop_repo = ShopRepository(self.db_path)

        # --- 4. 服务实例化 ---
        self.inventory_service = InventoryService(self.inventory_repo, self.user_repo, self.item_repo, self.general_repo)
        self.user_service = UserService(self.user_repo, self.inventory_service, self.item_repo, self.general_repo, self.game_config)
        self.general_service = GeneralService(self.general_repo, self.user_repo, self.user_service, self.game_config)
        self.leveling_service = LevelingService(self.user_repo, self.general_repo)
        self.dungeon_service = DungeonService(self.dungeon_repo, self.user_repo, self.general_repo, self.user_service, self.general_service)
        self.shop_service = ShopService(self.shop_repo, self.user_repo, self.item_repo, self.inventory_repo)
        self.auto_battle_service = AutoBattleService(
            self.user_service,
            self.dungeon_service,
            self.general_service,
            self.game_config
        )
        self.steal_service = StealService(
            self.user_repo,
            self.inventory_repo,
            self.inventory_service,
            self.general_service,
            self.game_config
        )
        
        data_setup_service = DataSetupService(self.general_repo, self.db_path)
        data_setup_service.setup_initial_data()
        
        # 用于存储冷却时间的字典
        self._recruit_cooldowns = {}
        
        # 用于存储冷却时间的字典
        self._recruit_cooldowns = {}
        self._adventure_cooldowns = {}
        self._dungeon_cooldowns = {}
        self._battle_states = {}

    def _force_migrate(self):
        """
        强制重新应用所有数据库迁移。
        利用 migration 模块的 force=True 参数。
        """
        try:
            logger.warning("开始执行强制数据库迁移...")
            run_migrations(self.db_path, self.migrations_path, force=True)
            logger.info("✅ 强制迁移成功完成。所有迁移已重新应用。")
            return True, "✅ 强制迁移成功完成。所有迁移已重新应用。"
        except Exception as e:
            logger.error(f"执行强制数据库迁移时出错: {e}", exc_info=True)
            return False, f"❌ 强制数据库迁移失败: {e}"

    def _verify_and_heal_db(self):
        """
        验证数据库结构是否与代码期望一致，如果不一致则尝试自动修复。
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查 'users' 表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            if cursor.fetchone() is None:
                logger.error("CRITICAL: 'users' 表不存在！数据库可能已损坏。正在尝试强制迁移...")
                self._force_migrate()
                return

            # 检查 'users' 表是否包含 'level' 列
            cursor.execute("PRAGMA table_info(users);")
            columns = [row[1] for row in cursor.fetchall()]
            if 'level' not in columns:
                logger.warning("数据库 'users' 表缺少 'level' 列。这可能是由于迁移失败导致的。")
                logger.warning("正在尝试通过强制迁移自动修复...")
                self._force_migrate()
            else:
                logger.info("数据库基础表 'users' 结构验证通过。")

            conn.close()
        except Exception as e:
            logger.error(f"数据库验证和修复过程中发生严重错误: {e}")



    async def on_load(self):
        """插件加载时执行，启动调度器"""
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        self.scheduler.add_job(self.auto_battle_service.run_auto_battles, 'interval', minutes=30)
        self.scheduler.start()
        logger.info("自动战斗调度器已启动，每分钟检查一次。")

    async def on_unload(self):
        """插件卸载时执行，关闭调度器"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("自动战斗调度器已关闭。")

    async def initialize(self):
        """插件异步初始化"""
        # 迁移已在 __init__ 中完成
        timestamp = datetime.now().strftime("%H:%M:%S")
        logger.info(f"三国文字RPG插件加载成功！(V2 - {timestamp})")

    @filter.command("三国帮助", alias={"三国菜单"})
    async def sanguo_help(self, event: AstrMessageEvent):
        """显示三国RPG插件帮助信息"""
        try:
            # 调用绘图函数
            image_path = draw_help_image()
            # 发送图片
            yield event.image_result(image_path)
        except Exception as e:
            logger.error(f"生成帮助图片时出错: {e}", exc_info=True)
            yield event.plain_result("生成帮助图片时遇到问题，请联系管理员。")

    @filter.command("三国注册")
    async def register_user(self, event: AstrMessageEvent):
        """注册用户"""
        user_id = event.get_sender_id()
        nickname = event.get_sender_name()
        
        result = self.user_service.register(user_id, nickname)
        yield event.plain_result(result["message"])

    @filter.command("三国签到")
    async def sign_in(self, event: AstrMessageEvent):
        """每日签到"""
        user_id = event.get_sender_id()
        result = self.user_service.sign_in(user_id)
        yield event.plain_result(result["message"])
        
    @filter.command("三国我的信息")
    async def my_info(self, event: AstrMessageEvent):
        """查看我的信息"""
        user_id = event.get_sender_id()
        result = self.user_service.get_user_info(user_id)
        
        # 获取出战武将信息
        user = self.user_repo.get_by_id(user_id)
        if user and user.battle_generals:
            try:
                import json
                battle_general_ids = json.loads(user.battle_generals)
                # 获取武将名字
                general_names = self.general_repo.get_generals_names_by_instance_ids(battle_general_ids)
                if general_names:
                    result["message"] += f"\n\n⚔️ 出战武将: {', '.join(general_names)}"
            except (json.JSONDecodeError, TypeError):
                pass # 如果解析失败则不显示

        yield event.plain_result(result["message"])
        
    @filter.command("三国我的武将", alias={"三国武将列表", "三国查看武将"})
    async def my_generals(self, event: AstrMessageEvent):
        """查看我的武将"""
        user_id = event.get_sender_id()
        # 使用优化后的方法一次性获取所有武将信息
        detailed_generals = self.general_repo.get_user_generals_with_details(user_id)
        
        if not detailed_generals:
            yield event.plain_result("您还没有任何武将，请先进行招募！\n使用 /三国招募 来获取您的第一个武将。")
            return
        
        general_info_list = []
        for general in detailed_generals:
            rarity_stars = "⭐" * general.rarity
            camp_emoji = {"蜀": "🟢", "魏": "🔵", "吴": "🟡", "群": "🔴"}.get(general.camp, "⚪")

            general_info = f"""
{camp_emoji} {general.name} {rarity_stars} (ID: {general.instance_id})
等级：{general.level} | 经验：{general.exp}/100
武力：{general.wu_li} | 智力：{general.zhi_li}
统帅：{general.tong_shuai} | 速度：{general.su_du}
战斗力：{general.combat_power:.2f}
"""
            general_info_list.append(general_info.strip())
        
        total_count = len(detailed_generals)
        message = f"📜 【我的武将】({total_count}个)\n\n" + "\n\n".join(general_info_list)
        
        yield event.plain_result(message)

    @filter.command("三国设置出战")
    async def set_battle_generals(self, event: AstrMessageEvent):
        """设置出战武将"""
        user_id = event.get_sender_id()
        args = event.message_str.split()
        
        if len(args) < 2:
            yield event.plain_result("请提供要设置为出战的武将ID，用空格分隔。\n例如：/三国设置出战 1 2 3")
            return

        try:
            general_instance_ids = [int(gid) for gid in args[1:]]
        except ValueError:
            yield event.plain_result("武将ID必须是数字。")
            return

        result = self.general_service.set_battle_generals(user_id, general_instance_ids)
        yield event.plain_result(result["message"])

    @filter.command("三国招募", alias={"三国招募武将", "三国抽卡"})
    async def recruit_general(self, event: AstrMessageEvent):
        """招募武将"""
        user_id = event.get_sender_id()
        result = self.general_service.recruit_general(user_id)
        yield event.plain_result(result["message"])

    @filter.command("三国升级武将", alias={"三国武将升级"})
    async def level_up_general(self, event: AstrMessageEvent):
        """升级指定的武将"""
        user_id = event.get_sender_id()
        args = event.message_str.split()
        if len(args) < 2 or not args[1].isdigit():
            yield event.plain_result("指令格式错误，请使用：/三国升级武将 [武将ID]")
            return

        general_instance_id = int(args[1])
        result_message = self.leveling_service.level_up_general(user_id, general_instance_id)
        yield event.plain_result(result_message)

    @filter.command("三国称号")
    async def title_system(self, event: AstrMessageEvent):
        """称号系统，包括列表和兑换"""
        user_id = event.get_sender_id()
        user = self.user_repo.get_by_id(user_id)
        if not user:
            yield event.plain_result("您尚未注册，请先使用 /三国注册 命令。")
            return

        args = event.message_str.replace("三国称号", "").strip().split()
        sub_command = args[0] if args else "列表"

        if sub_command in ["列表", "list"]:
            titles = self.title_repo.get_all_titles()
            if not titles:
                yield event.plain_result("暂无可用称号。")
                return
            
            title_list_text = "【称号列表】\n\n"
            for title in titles:
                status = "✅" if user.reputation >= title.required_reputation else "❌"
                title_list_text += f"{status} {title.name} (要求声望: {title.required_reputation})\n"
            
            title_list_text += "\n使用 `/三国称号兑换 [称号名称]` 来兑换称号。"
            yield event.plain_result(title_list_text)

        elif sub_command in ["兑换", "exchange"]:
            if len(args) < 2:
                yield event.plain_result("请输入要兑换的称号名称。格式: /三国称号兑换 [称号名称]")
                return
            
            title_name = args[1]
            target_title = self.title_repo.get_title_by_name(title_name)

            if not target_title:
                yield event.plain_result(f"未找到名为“{title_name}”的称号。")
                return

            if user.reputation < target_title.required_reputation:
                yield event.plain_result(f"声望不足！兑换“{target_title.name}”需要 {target_title.required_reputation} 声望，您当前拥有 {user.reputation} 声望。")
                return
            
            user.title = target_title.name
            self.user_repo.update(user)
            yield event.plain_result(f"恭喜！您已成功装备称号：【{target_title.name}】")
        
        else:
            yield event.plain_result("无效的子命令。可用命令: /三国称号列表, /三国称号兑换 [名称]")

    @filter.command("三国闯关", alias={"三国冒险", "三国挑战", "三国选择"})
    async def adventure(self, event: AstrMessageEvent):
        """开始或继续一次闯关冒险。使用 /三国闯关 [选项] 来推进。"""
        user_id = event.get_sender_id()
        
        # 从消息中提取选项
        # 移除命令前缀，例如 "/三国闯关 1" -> "1"
        command_parts = event.message_str.split(maxsplit=1)
        args_str = command_parts[1] if len(command_parts) > 1 else ""

        option_index = -1
        if args_str.strip().isdigit():
            option_index = int(args_str.strip()) - 1

        # 将所有逻辑委托给 general_service
        result = self.general_service.adventure(user_id, option_index)
        
        message = result["message"]
        
        # 如果需要后续操作，添加提示
        if result.get("requires_follow_up"):
            message += "\n\n使用 `/三国闯关 [选项编号]` 来决定您的行动。"
            
        yield event.plain_result(message.strip())

    @filter.command("三国自动冒险")
    async def toggle_auto_adventure(self, event: AstrMessageEvent):
        """开启或关闭自动冒险"""
        user_id = event.get_sender_id()
        args = event.message_str.split()
        if len(args) < 2 or args[1] not in ["开启", "关闭"]:
            yield event.plain_result("指令格式错误，请使用：/三国自动冒险 [开启/关闭]")
            return
        
        enabled = True if args[1] == "开启" else False
        result = self.user_service.set_auto_adventure(user_id, enabled)
        yield event.plain_result(result["message"])

    @filter.command("三国自动副本")
    async def set_auto_dungeon(self, event: AstrMessageEvent):
        """设置自动副本"""
        user_id = event.get_sender_id()
        args = event.message_str.split()
        
        dungeon_id = None
        if len(args) > 1 and args[1].isdigit():
            dungeon_id = int(args[1])
        elif len(args) > 1 and args[1] == "关闭":
            dungeon_id = None
        else:
            yield event.plain_result("指令格式错误，请使用：/三国自动副本 [副本ID] 或 /三国自动副本 关闭")
            return

        result = self.user_service.set_auto_dungeon(user_id, dungeon_id)
        yield event.plain_result(result["message"])

    @filter.command("每日闯关记录")
    async def daily_adventure_logs(self, event: AstrMessageEvent):
        """查看今日的闯关记录"""
        user_id = event.get_sender_id()
        logs = self.general_service.get_daily_adventure_logs(user_id)
        if not logs:
            yield event.plain_result("今日暂无闯关记录。")
            return
        
        log_messages = [f"[{log['time'].strftime('%H:%M')}] {log['details']}" for log in logs]
        message = "【每日闯关记录】\n" + "\n".join(log_messages)
        yield event.plain_result(message)

    @filter.command("每日战斗记录")
    async def daily_dungeon_logs(self, event: AstrMessageEvent):
        """查看今日的副本战斗记录"""
        user_id = event.get_sender_id()
        logs = self.general_service.get_daily_dungeon_logs(user_id)
        if not logs:
            yield event.plain_result("今日暂无副本战斗记录。")
            return
        
        log_messages = [f"[{log['time'].strftime('%H:%M')}] {log['details']}" for log in logs]
        message = "【每日战斗记录】\n" + "\n".join(log_messages)
        yield event.plain_result(message)

    @filter.command("副本列表")
    async def list_dungeons(self, event: AstrMessageEvent):
        """显示可用副本列表"""
        user_id = event.get_sender_id()
        user = self.user_repo.get_by_id(user_id)
        if not user:
            yield event.plain_result("您尚未注册，请先使用 /三国注册 命令。")
            return
        
        message = self.dungeon_service.list_dungeons(user)
        yield event.plain_result(message)

    @filter.command("三国战斗")
    async def battle_start(self, event: AstrMessageEvent):
        """发起副本挑战，选择武将"""
        user_id = event.get_sender_id()

        # 检查冷却时间
        cooldown_key = f"dungeon_{user_id}"
        current_time = datetime.now()
        cooldown_seconds = self.game_config.get("dungeon", {}).get("cooldown_seconds", 600)

        if cooldown_key in self._dungeon_cooldowns:
            last_battle_time = self._dungeon_cooldowns[cooldown_key]
            time_diff = (current_time - last_battle_time).total_seconds()
            if time_diff < cooldown_seconds:
                remaining_time = int(cooldown_seconds - time_diff)
                yield event.plain_result(f"⚔️ 副本挑战冷却中，还需等待 {remaining_time} 秒。")
                return

        args = event.message_str.split()
        if len(args) < 2 or not args[1].isdigit():
            yield event.plain_result("指令格式错误，请使用：/三国战斗 [副本ID]")
            return

        dungeon_id = int(args[1])
        
        # 存储战斗状态
        self._battle_states[user_id] = {"dungeon_id": dungeon_id}
        
        message = self.dungeon_service.get_eligible_generals_for_dungeon(user_id, dungeon_id)
        yield event.plain_result(message)

    @filter.command("三国出征")
    async def battle_execute(self, event: AstrMessageEvent):
        """确认出战武将，执行战斗"""
        user_id = event.get_sender_id()
        
        if user_id not in self._battle_states:
            yield event.plain_result("请先使用 `/三国战斗 [副本ID]` 选择一个副本。")
            return
            
        dungeon_id = self._battle_states[user_id]["dungeon_id"]
        
        args = event.message_str.split()
        if len(args) < 2:
            yield event.plain_result("指令格式错误，请使用：/三国出征 [武将ID1] [武将ID2]...")
            return

        try:
            general_instance_ids = [int(gid) for gid in args[1:]]
        except ValueError:
            yield event.plain_result("武将ID必须是数字。")
            return
        
        message = self.dungeon_service.execute_battle(user_id, dungeon_id, general_instance_ids)
        
        # 战斗结束后设置冷却并清除状态
        cooldown_key = f"dungeon_{user_id}"
        self._dungeon_cooldowns[cooldown_key] = datetime.now()
        if user_id in self._battle_states:
            del self._battle_states[user_id]
        
        yield event.plain_result(message)

    @filter.command("三国商店", alias={"商店"})
    async def show_shop(self, event: AstrMessageEvent):
        """显示今日商店"""
        message = self.shop_service.get_shop_display()
        yield event.plain_result(message)

    @filter.command("三国购买", alias={"购买"})
    async def purchase_item(self, event: AstrMessageEvent):
        """从商店购买商品"""
        user_id = event.get_sender_id()
        args = event.message_str.split()
        if len(args) < 2 or not args[1].isdigit():
            yield event.plain_result("指令格式错误，请使用：/三国购买 [商品ID]")
            return

        shop_item_id = int(args[1])
        result = self.shop_service.purchase_item(user_id, shop_item_id)
        yield event.plain_result(result["message"])

    @filter.command("三国背包", alias={"背包"})
    async def show_inventory(self, event: AstrMessageEvent):
        """显示玩家的背包"""
        user_id = event.get_sender_id()
        message = self.inventory_service.get_inventory_display(user_id)
        yield event.plain_result(message)

    @filter.command("三国使用", alias={"使用"})
    async def use_item(self, event: AstrMessageEvent):
        """使用背包中的物品"""
        user_id = event.get_sender_id()
        args = event.message_str.split()
        if len(args) < 2 or not args[1].isdigit():
            yield event.plain_result("指令格式错误，请使用：/三国使用 [物品ID]")
            return

        item_id = int(args[1])
        message = self.inventory_service.use_item(user_id, item_id)
        yield event.plain_result(message)

    @filter.command("三国出售", alias={"出售"})
    async def sell_item(self, event: AstrMessageEvent):
        """出售背包中的物品"""
        user_id = event.get_sender_id()
        args = event.message_str.split()
        
        # 格式: /三国出售 [物品ID] [数量]
        if len(args) < 3 or not args[1].isdigit() or not args[2].isdigit():
            yield event.plain_result("指令格式错误，请使用：/三国出售 [物品ID] [数量]")
            return

        item_id = int(args[1])
        quantity = int(args[2])
        
        result = self.shop_service.sell_item(user_id, item_id, quantity)
        yield event.plain_result(result["message"])

    @filter.command("三国偷窃", alias={"偷窃"})
    async def steal_from_player(self, event: AstrMessageEvent):
        """从其他玩家处偷窃"""
        thief_id = event.get_sender_id()
        
        # 检查是否有 at (mention)
        mentioned_users = event.get_mentioned_user_ids()
        if not mentioned_users:
            yield event.plain_result("请 @ 你要偷窃的目标。")
            return
            
        target_id = mentioned_users[0]
        
        result = self.steal_service.attempt_steal(thief_id, target_id)
        yield event.plain_result(result["message"])

    @filter.permission_type(PermissionType.ADMIN)
    @filter.command("三国管理")
    async def sanguo_admin(self, event: AstrMessageEvent):
        """三国RPG插件管理命令"""
        # 从消息中移除命令本身，只保留参数
        args_text = event.message_str.replace("三国管理", "", 1).strip()
        logger.info(f"处理后的三国管理参数: '{args_text}'")
        parts = args_text.split()
        
        # 增加一个给予玩家资源的子命令
        # 格式: /三国管理 add <resource_type> <amount> <user_id>
        # 例如: /三国管理 add coins 10000 123456789
        if len(parts) > 0 and parts[0] == "add":
            if len(parts) != 4:
                yield event.plain_result("❌ 参数格式错误。\n正确格式: /三国管理 add <resource_type> <amount> <user_id>")
                return
            
            _, resource_type, amount_str, user_id = parts
            
            user = self.user_repo.get_by_id(user_id)
            if not user:
                yield event.plain_result(f"❌ 找不到用户: {user_id}")
                return
            
            try:
                amount = int(amount_str)
            except ValueError:
                yield event.plain_result(f"❌ 数量必须是整数: {amount_str}")
                return

            if resource_type.lower() == "coins":
                user.coins += amount
                self.user_repo.update(user)
                yield event.plain_result(f"✅ 成功为用户 {user.nickname} ({user_id}) 添加了 {amount} 铜钱。")
            elif resource_type.lower() == "yuanbao":
                user.yuanbao += amount
                self.user_repo.update(user)
                yield event.plain_result(f"✅ 成功为用户 {user.nickname} ({user_id}) 添加了 {amount} 元宝。")
            elif resource_type.lower() == "exp":
                user.exp += amount
                self.user_repo.update(user)
                yield event.plain_result(f"✅ 成功为用户 {user.nickname} ({user_id}) 添加了 {amount} 经验。")
            else:
                yield event.plain_result(f"❌ 未知的资源类型: {resource_type}。可用: coins, yuanbao, exp")
            return

        # 保留数据库迁移功能
        if args_text == "migrate":
            try:
                run_migrations(self.db_path, self.migrations_path)
                yield event.plain_result("✅ 数据库迁移成功完成。")
            except Exception as e:
                logger.error(f"手动执行数据库迁移时出错: {e}", exc_info=True)
                yield event.plain_result(f"❌ 数据库迁移失败: {e}")
            return

        # 添加强制迁移功能
        if args_text == "force-migrate":
            try:
                run_migrations(self.db_path, self.migrations_path, force=True)
                yield event.plain_result("✅ 强制迁移成功完成。所有迁移已重新应用。")
            except Exception as e:
                logger.error(f"手动执行强制数据库迁移时出错: {e}", exc_info=True)
                yield event.plain_result(f"❌ 强制数据库迁移失败: {e}")
            return
            
        # 如果没有匹配的子命令，显示帮助信息
        help_text = """
        【三国管理】可用命令:
        - /三国管理 migrate
          手动执行数据库迁移。
        - /三国管理 force-migrate
          强制重新应用所有数据库迁移。
        - /三国管理 add <type> <amount> <user_id>
          为指定用户添加资源。
          <type>: coins, yuanbao, exp
        """
        yield event.plain_result(help_text.strip())
