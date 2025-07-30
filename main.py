# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : main.py
# @Software: AstrBot
# @Description: 三国文字RPG插件主文件 (最小化重构版)

import os
from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star

# 暂时移除所有服务和数据库的导入，以进行最小化测试
# from astrbot_plugin_sanguo_rpg.core.database.migration import run_migrations
# from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
# from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_general_repo import SqliteGeneralRepository
# from astrbot_plugin_sanguo_rpg.core.services.user_service import UserService
# from astrbot_plugin_sanguo_rpg.core.services.general_service import GeneralService
# from astrbot_plugin_sanguo_rpg.draw.help import draw_help_image

class SanGuoRPGPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        logger.info("三国RPG插件加载中... (最小化模式)")

        # --- 所有复杂初始化暂时禁用 ---
        # self.game_config = {}
        # db_path = "data/sanguo_rpg.db"
        # os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # plugin_root_dir = os.path.dirname(__file__)
        # migrations_path = os.path.join(plugin_root_dir, "core", "database", "migrations")
        # run_migrations(db_path, migrations_path)
        # self.user_repo = SqliteUserRepository(db_path)
        # self.general_repo = SqliteGeneralRepository(db_path)
        # self.user_service = UserService(self.user_repo, self.game_config)
        # self.general_service = GeneralService(self.general_repo, self.user_repo, self.game_config)
        # self.adventure_context = {}

    async def initialize(self):
        """插件异步初始化"""
        logger.info("""
        =========================================
        三国文字RPG插件加载成功！(最小化模式)
        =========================================
        """)

    @filter.command("注册")
    async def register_user(self, event: AstrMessageEvent):
        """注册用户 (最小化测试)"""
        yield event.plain_result("注册功能测试成功！框架已正确调用此命令。")

    # --- 其他所有命令暂时禁用 ---
    # @filter.command("签到")
    # async def sign_in(self, event: AstrMessageEvent):
    #     """每日签到"""
    #     user_id = event.get_sender_id()
    #     result = self.user_service.daily_sign_in(user_id)
    #     yield event.plain_result(result["message"])
