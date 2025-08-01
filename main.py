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

from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star
from astrbot.core.star.filter.permission import PermissionType

from astrbot_plugin_sanguo_rpg.core.database.migration import run_migrations
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_general_repo import SqliteGeneralRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_general_repo import SqliteUserGeneralRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_title_repo import SqliteTitleRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_dungeon_repo import DungeonRepository
from astrbot_plugin_sanguo_rpg.core.services.data_setup_service import DataSetupService
from astrbot_plugin_sanguo_rpg.core.services.leveling_service import LevelingService
from astrbot_plugin_sanguo_rpg.core.services.dungeon_service import DungeonService
from astrbot_plugin_sanguo_rpg.core.services.user_service import UserService
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
            "user": { "initial_coins": 50, "initial_yuanbao": 50 },
            "recruit": { "cost_yuanbao": 50, "cooldown_seconds": 300 },
            "adventure": { "cost_coins": 20, "cooldown_seconds": 600 }
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
            self._verify_and_heal_db()

        except Exception as e:
            logger.error(f"在 __init__ 期间执行数据库迁移或验证时出错: {e}")

        # --- 3. 组合根：实例化仓储和服务 ---
        self.user_repo = SqliteUserRepository(self.db_path)
        self.general_repo = SqliteGeneralRepository(self.db_path)
        self.user_general_repo = SqliteUserGeneralRepository(self.db_path)
        self.title_repo = SqliteTitleRepository(self.db_path)
        self.dungeon_repo = DungeonRepository(self.db_path)

        self.leveling_service = LevelingService(self.user_repo, self.user_general_repo)
        self.dungeon_service = DungeonService(self.dungeon_repo, self.user_repo, self.general_repo)
        self.user_service = UserService(self.user_repo, self.game_config)
        
        data_setup_service = DataSetupService(self.general_repo, self.db_path)
        data_setup_service.setup_initial_data()
        
        # 用于存储冷却时间的字典
        self._recruit_cooldowns = {}
        self._adventure_cooldowns = {}

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

    @filter.command("三国招募", alias={"三国招募武将", "三国抽卡"})
    async def recruit_general(self, event: AstrMessageEvent):
        """招募武将"""
        user_id = event.get_sender_id()
        user = self.user_repo.get_by_id(user_id)
        if not user:
            yield event.plain_result("请先使用 /三国注册 命令注册账户！")
            return
        
        cooldown_key = f"recruit_{user_id}"
        current_time = datetime.now()
        
        if cooldown_key in self._recruit_cooldowns:
            last_recruit_time = self._recruit_cooldowns[cooldown_key]
            cooldown_seconds = self.game_config.get("recruit", {}).get("cooldown_seconds", 300)
            time_diff = (current_time - last_recruit_time).total_seconds()
            
            if time_diff < cooldown_seconds:
                remaining_time = int(cooldown_seconds - time_diff)
                yield event.plain_result(f"⏰ 招募冷却中，还需等待 {remaining_time} 秒后才能再次招募。")
                return
        
        recruit_cost = self.game_config.get("recruit", {}).get("cost_yuanbao", 50)
        
        # --- “望族”技能折扣计算 ---
        user_generals = self.general_repo.get_user_generals_with_details(user_id)
        wangzu_count = sum(1 for g in user_generals if "望族" in g.skill_desc)
        discount_rate = min(wangzu_count * 0.1, 0.2) # 最多20%折扣
        
        final_cost = int(recruit_cost * (1 - discount_rate))
        discount_info = f" (原价: {recruit_cost})" if discount_rate > 0 else ""
        
        if user.yuanbao < final_cost:
            yield event.plain_result(f"💎 元宝不足！招募需要 {final_cost} 元宝{discount_info}，您当前只有 {user.yuanbao} 元宝。")
            return
        
        # --- 声望影响招募 ---
        reputation_luck_bonus = min(user.reputation / 5000, 0.2) # 每500声望提升10%稀有度概率，最高20%
        
        recruited_general = self.general_repo.get_random_general_by_rarity_pool(reputation_luck_bonus)
        if not recruited_general:
            yield event.plain_result("❌ 招募系统繁忙，请稍后再试。")
            return

        # 检查用户是否已拥有该武将
        if self.general_repo.check_user_has_general(user_id, recruited_general.general_id):
            # 更新冷却时间，即使招募到重复的武将也进入冷却
            self._recruit_cooldowns[cooldown_key] = current_time
            yield event.plain_result(f"您已拥有武将【{recruited_general.name}】，本次招募未消耗元宝，但招募机会已使用，进入冷却。")
            return

        # 确认不重复后，再扣费和添加
        user.yuanbao -= final_cost
        self.user_repo.update(user)
        
        success = self.general_repo.add_user_general(user_id, recruited_general.general_id)
        if not success:
            # 如果添加失败，需要回滚费用
            user.yuanbao += recruit_cost
            self.user_repo.update(user)
            yield event.plain_result("❌ 数据库繁忙，招募失败，元宝已退还。")
            return
        
        self._recruit_cooldowns[cooldown_key] = current_time
        
        rarity_stars = "⭐" * recruited_general.rarity
        camp_emoji = {"蜀": "🟢", "魏": "🔵", "吴": "🟡", "群": "🔴"}.get(recruited_general.camp, "⚪")
        
        if recruited_general.rarity >= 5: effect = "✨🎉 传说降临！🎉✨"
        elif recruited_general.rarity >= 4: effect = "🌟 稀有出现！🌟"
        elif recruited_general.rarity >= 3: effect = "💫 精英到来！"
        else: effect = "⚡ 新的伙伴！"
        
        message = f"""
{effect}
{camp_emoji} {recruited_general.name} {rarity_stars}
阵营：{recruited_general.camp}
武力：{recruited_general.wu_li} | 智力：{recruited_general.zhi_li}
统帅：{recruited_general.tong_shuai} | 速度：{recruited_general.su_du}
技能：{recruited_general.skill_desc}
💰 花费：{final_cost} 元宝{discount_info}
💎 剩余元宝：{user.yuanbao}
使用 /三国我的武将 查看所有武将！
"""
        yield event.plain_result(message.strip())

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

    @filter.command("三国闯关", alias={"三国冒险", "三国挑战"})
    async def adventure(self, event: AstrMessageEvent):
        """开始或继续一次闯关冒险"""
        user_id = event.get_sender_id()
        user = self.user_repo.get_by_id(user_id)

        if not user:
            yield event.plain_result("您尚未注册，请先使用 /三国注册 命令。")
            return

        # --- 智能路由：如果玩家在冒险中，且命令带有数字，则视为选择 ---
        args_str = event.message_str.replace("三国闯关", "", 1).strip()
        if self.user_service.get_user_adventure_state(user_id) and args_str.isdigit():
            import copy
            fake_event = copy.copy(event)
            fake_event.message_str = f"三国选择 {args_str}"
            async for result in self.adventure_choice(fake_event):
                yield result
            return

        # 如果玩家正在冒险中，但没有提供数字，则显示当前状态（已优化，会显示故事上下文）
        current_state = self.user_service.get_user_adventure_state(user_id)
        if current_state:
            # 从状态中获取故事文本和选项
            story_text = current_state.get("story_text", "你正面临一个抉择...") # 如果没有文本，则使用默认提示
            options = current_state.get("options", [])
            
            options_text = [f"{i+1}. {opt['text']}" for i, opt in enumerate(options)]
            
            message = f"【冒险进行中】\n{story_text}\n\n请做出您的选择:\n" + "\n".join(options_text)
            message += "\n\n使用 `/三国选择 [选项编号]` 来决定您的行动。"
            yield event.plain_result(message.strip())
            return

        # --- 开始新的冒险 ---
        cooldown_key = f"adventure_{user_id}"
        current_time = datetime.now()
        cooldown_seconds = self.game_config.get("adventure", {}).get("cooldown_seconds", 600)

        if cooldown_key in self._adventure_cooldowns:
            last_adventure_time = self._adventure_cooldowns[cooldown_key]
            time_diff = (current_time - last_adventure_time).total_seconds()
            if time_diff < cooldown_seconds:
                remaining_time = int(cooldown_seconds - time_diff)
                yield event.plain_result(f"⚔️ 闯关冷却中，还需等待 {remaining_time} 秒。")
                return

        cost = self.game_config.get("adventure", {}).get("cost_coins", 20)
        if user.coins < cost:
            yield event.plain_result(f"💰 铜钱不足！闯关需要 {cost} 铜钱，您只有 {user.coins}。")
            return
        
        user.coins -= cost
        self.user_repo.update(user) # 先扣费
        
        # --- 使用 AdventureGenerator 生成新故事 ---
        adv_gen = AdventureGenerator(user_id, self.user_service)
        result = adv_gen.start_adventure()

        if not result or not result.get("text"):
            # 如果生成失败，需要回滚费用
            user.coins += cost
            self.user_repo.update(user)
            yield event.plain_result("❌ 冒险故事生成失败，费用已退还，请稍后再试。")
            return

        options_text = [f"{i+1}. {opt}" for i, opt in enumerate(result["options"])]
        
        message = f"【新的冒险】\n{result['text']}\n\n请做出您的选择:\n" + "\n".join(options_text)
        message += "\n\n使用 `/三国选择 [选项编号]` 来决定您的行动。"
        
        self._adventure_cooldowns[cooldown_key] = current_time
        yield event.plain_result(message.strip())

    @filter.command("三国选择")
    async def adventure_choice(self, event: AstrMessageEvent):
        """在闯关冒险中做出选择"""
        user_id = event.get_sender_id()
        
        if not self.user_service.get_user_adventure_state(user_id):
            yield event.plain_result("您当前没有正在进行的冒险。请使用 /三国闯关 开始新的冒险。")
            return
            
        choice_text = event.message_str.replace("三国选择", "", 1).strip()
        if not choice_text.isdigit():
            yield event.plain_result("无效的选项，请输入数字。")
            return
            
        choice_index = int(choice_text) - 1
        
        adv_gen = AdventureGenerator(user_id, self.user_service)
        result = adv_gen.advance_adventure(choice_index) # result is a dict

        message = result["text"]

        if not result["is_final"]:
            options_text = [f"{i+1}. {opt}" for i, opt in enumerate(result["options"])]
            message += "\n\n请做出您的选择:\n" + "\n".join(options_text)
            message += "\n\n使用 `/三国选择 [选项编号]` 来决定您的行动。"
        else:
            # 冒险结束，可以显示一下当前状态
            user = self.user_repo.get_by_id(user_id)
            if user:
                 message += f"\n\n当前状态：\n铜钱: {user.coins}, 经验: {user.exp}, 声望: {user.reputation}"

        yield event.plain_result(message.strip())

    @filter.command("三国挂机闯关")
    async def auto_adventure(self, event: AstrMessageEvent):
        """自动闯关"""
        yield event.plain_result("该功能正在开发中，敬请期待！")

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
        args = event.message_str.split()
        if len(args) < 2 or not args[1].isdigit():
            yield event.plain_result("指令格式错误，请使用：/三国战斗 [副本ID]")
            return

        dungeon_id = int(args[1])
        
        message = self.dungeon_service.get_eligible_generals_for_dungeon(user_id, dungeon_id)
        yield event.plain_result(message)

    @filter.command("确认出战")
    async def battle_execute(self, event: AstrMessageEvent):
        """确认出战武将，执行战斗"""
        user_id = event.get_sender_id()
        args = event.message_str.split()
        if len(args) < 3:
            yield event.plain_result("指令格式错误，请使用：/确认出战 [副本ID] [武将ID1] [武将ID2]...")
            return

        try:
            dungeon_id = int(args[1])
            general_instance_ids = [int(gid) for gid in args[2:]]
        except ValueError:
            yield event.plain_result("副本ID和武将ID必须是数字。")
            return
        
        message = self.dungeon_service.execute_battle(user_id, dungeon_id, general_instance_ids)
        yield event.plain_result(message)

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
