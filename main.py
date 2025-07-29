# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : main.py
# @Software: AstrBot
# @Description: 三国文字RPG插件主文件

import os
from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot_plugin_sanguo_rpg.core.database.migration import run_migrations
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_general_repo import SqliteGeneralRepository
from astrbot_plugin_sanguo_rpg.core.services.user_service import UserService
from astrbot_plugin_sanguo_rpg.core.services.general_service import GeneralService
from astrbot_plugin_sanguo_rpg.draw.help import draw_help_image

@register("astrbot_plugin_sanguo_rpg", "Cline", "A simple Three Kingdoms RPG plugin", "0.1.0", "")
class SanGuoRPGPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        logger.info("三国RPG插件加载中...")

        # --- 1. 加载配置 ---
        self.game_config = {
            "user": {
                "initial_coins": config.get("initial_coins", 1000),
                "initial_yuanbao": config.get("initial_yuanbao", 100)
            },
            "recruit": {
                "cost_yuanbao": config.get("recruit_cost_yuanbao", 50),
                "cooldown_seconds": config.get("recruit_cooldown_seconds", 300)
            },
            "adventure": {
                "cost_coins": config.get("adventure_cost_coins", 50),
                "cooldown_seconds": config.get("adventure_cooldown_seconds", 600)
            }
        }

        # --- 2. 数据库初始化 ---
        db_path = "data/sanguo_rpg.db"
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        plugin_root_dir = os.path.dirname(__file__)
        migrations_path = os.path.join(plugin_root_dir, "core", "database", "migrations")
        run_migrations(db_path, migrations_path)

        # --- 3. 组合根：实例化仓储和服务 ---
        self.user_repo = SqliteUserRepository(db_path)
        self.general_repo = SqliteGeneralRepository(db_path)
        self.user_service = UserService(self.user_repo, self.game_config)
        self.general_service = GeneralService(self.general_repo, self.user_repo, self.game_config)

        # 用于存储闯关上下文的字典
        self.adventure_context = {}


    async def initialize(self):
        """插件异步初始化"""
        logger.info("""
        =========================================
        三国文字RPG插件加载成功！
        =========================================
        """)

    @filter.command("三国帮助", alias={"三国菜单"})
    async def sanguo_help(self, event: AstrMessageEvent):
        """显示三国RPG插件帮助信息"""
        image_path = draw_help_image()
        yield event.image_result(image_path)

    @filter.command("注册")
    async def register_user(self, event: AstrMessageEvent):
        """注册用户"""
        user_id = event.get_sender_id()
        nickname = event.get_sender_name() if event.get_sender_name() is not None else event.get_sender_id()
        result = self.user_service.register(user_id, nickname)
        yield event.plain_result(result["message"])

    @filter.command("签到")
    async def sign_in(self, event: AstrMessageEvent):
        """每日签到"""
        user_id = event.get_sender_id()
        result = self.user_service.daily_sign_in(user_id)
        yield event.plain_result(result["message"])

    @filter.command("我的信息")
    async def my_info(self, event: AstrMessageEvent):
        """查看我的信息"""
        user_id = event.get_sender_id()
        result = self.user_service.get_user_info(user_id)
        yield event.plain_result(result["message"])

    @filter.command("我的武将", alias={"武将列表", "查看武将"})
    async def my_generals(self, event: AstrMessageEvent):
        """查看我的武将"""
        user_id = event.get_sender_id()
        result = self.general_service.get_user_generals_info(user_id)
        yield event.plain_result(result["message"])

    @filter.command("招募", alias={"招募武将", "抽卡"})
    async def recruit_general(self, event: AstrMessageEvent, *args):
        """招募武将"""
        user_id = event.get_sender_id()
        result = self.general_service.recruit_general(user_id)
        yield event.plain_result(result["message"])

    @filter.command("闯关", alias={"冒险", "战斗", "挑战"})
    async def adventure(self, event: AstrMessageEvent, *args):
        """闯关冒险"""
        user_id = event.get_sender_id()
        
        try:
            # 检查是否是后续操作
            last_adventure = self.adventure_context.get(user_id)
            if last_adventure and "requires_follow_up" in last_adventure:
                try:
                    option_index = int(event.get_plain_text()) - 1
                    result = self.general_service.adventure(user_id, option_index=option_index)
                    # 成功处理后，删除上下文
                    if user_id in self.adventure_context:
                        del self.adventure_context[user_id]
                except (ValueError, IndexError):
                    yield event.plain_result("无效的选项，请输入数字。")
                    return
            else:
                # 首次闯关
                result = self.general_service.adventure(user_id)

            # 如果需要后续操作，则保存上下文
            if result.get("requires_follow_up"):
                self.adventure_context[user_id] = result
            
            yield event.plain_result(result["message"])

        except Exception as e:
            logger.error(f"闯关时发生意外错误: {e}")
            yield event.plain_result("闯关时发生意外错误，请联系管理员。")

    @filter.command("挂机闯关")
    async def auto_adventure(self, event: AstrMessageEvent):
        """自动闯关"""
        user_id = event.get_sender_id()
        result = self.general_service.auto_adventure(user_id)
        yield event.plain_result(result["message"] + "\n（本次为挂机闯关，已为您随机选择）")
