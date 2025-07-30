# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : main.py
# @Software: AstrBot
# @Description: 三国文字RPG插件主文件 (二分法排错 - 测试GeneralService实例化)

import os
from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star

from astrbot_plugin_sanguo_rpg.core.database.migration import run_migrations
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_general_repo import SqliteGeneralRepository
from astrbot_plugin_sanguo_rpg.core.services.user_service import UserService
from astrbot_plugin_sanguo_rpg.core.services.general_service import GeneralService # 恢复
from astrbot_plugin_sanguo_rpg.core.services.data_setup_service import DataSetupService
from astrbot_plugin_sanguo_rpg.draw.help import draw_help_image

class SanGuoRPGPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        logger.info("三国RPG插件加载中... (二分法排错 - 测试GeneralService实例化)")

        # --- 1. 加载配置 ---
        self.game_config = { "user": { "initial_coins": 1000, "initial_yuanbao": 100 } }

        # --- 2. 数据库和基础数据初始化 ---
        db_path = "data/sanguo_rpg.db"
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        plugin_root_dir = os.path.dirname(__file__)
        migrations_path = os.path.join(plugin_root_dir, "core", "database", "migrations")
        run_migrations(db_path, migrations_path)

        # --- 3. 组合根：实例化仓储和服务 ---
        self.user_repo = SqliteUserRepository(db_path)
        self.general_repo = SqliteGeneralRepository(db_path)
        
        data_setup_service = DataSetupService(self.general_repo, db_path)
        data_setup_service.setup_initial_data()
        
        self.user_service = UserService(self.user_repo, self.game_config)
        self.general_service = GeneralService(self.general_repo, self.user_repo, self.game_config) # 恢复
        
        # self.adventure_context = {} # 隔离


    async def initialize(self):
        """插件异步初始化"""
        logger.info("三国文字RPG插件加载成功！(二分法排错 - 测试GeneralService实例化)")

    @filter.command("三国帮助", alias={"三国菜单"})
    async def sanguo_help(self, event: AstrMessageEvent):
        """显示三国RPG插件帮助信息"""
        try:
            image_path = draw_help_image()
            yield event.image_result(image_path)
        except Exception as e:
            logger.error(f"绘制帮助图片时出错: {e}")
            yield event.plain_result(f"绘制帮助图片时出错: {e}")

    @filter.command("三国注册")
    async def register_user(self, event: AstrMessageEvent):
        """注册用户"""
        user_id = event.get_sender_id()
        nickname = event.get_sender_name() if event.get_sender_name() is not None else event.get_sender_id()
        result = self.user_service.register(user_id, nickname)
        yield event.plain_result(result["message"])

    @filter.command("三国签到")
    async def sign_in(self, event: AstrMessageEvent):
        """每日签到"""
        user_id = event.get_sender_id()
        result = self.user_service.daily_sign_in(user_id)
        yield event.plain_result(result["message"])
