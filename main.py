# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : main.py
# @Software: AstrBot
# @Description: 三国文字RPG插件主文件 (增量恢复 - 步骤4.1)

import os
from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star

from astrbot_plugin_sanguo_rpg.core.database.migration import run_migrations
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_general_repo import SqliteGeneralRepository
from astrbot_plugin_sanguo_rpg.core.services.user_service import UserService
from astrbot_plugin_sanguo_rpg.core.services.general_service import GeneralService
from astrbot_plugin_sanguo_rpg.core.services.data_setup_service import DataSetupService
from astrbot_plugin_sanguo_rpg.draw.help import draw_help_image

class SanGuoRPGPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        logger.info("三国RPG插件加载中... (增量恢复 - 步骤4.1)")

        # --- 1. 加载配置 ---
        self.game_config = {
            "user": { "initial_coins": 1000, "initial_yuanbao": 100 },
            "recruit": { "cost_yuanbao": 50, "cooldown_seconds": 300 },
            "adventure": { "cost_coins": 50, "cooldown_seconds": 600 }
        }

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
        self.general_service = GeneralService(self.general_repo, self.user_repo, self.game_config)
        
        self.adventure_context = {}


    async def initialize(self):
        """插件异步初始化"""
        logger.info("三国文字RPG插件加载成功！(增量恢复 - 步骤4.1)")

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
        
    @filter.command("三国我的信息")
    async def my_info(self, event: AstrMessageEvent):
        """查看我的信息"""
        user_id = event.get_sender_id()
        user = self.user_repo.get_by_id(user_id)
        if not user:
            yield event.plain_result("您尚未注册，请先使用 /三国注册 命令。")
            return

        info = (
            f"【主公信息】\n"
            f"👤 昵称: {user.nickname}\n"
            f"经验: {getattr(user, 'exp', 0)}\n"
            f"💰 铜钱: {user.coins}\n"
            f"💎 元宝: {user.yuanbao}\n"
            f"📅 注册时间: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        yield event.plain_result(info)
        
    @filter.command("三国我的武将", alias={"三国武将列表", "三国查看武将"})
    async def my_generals(self, event: AstrMessageEvent):
        """查看我的武将"""
        user_id = event.get_sender_id()
        user_generals = self.general_repo.get_user_generals(user_id)
        
        if not user_generals:
            yield event.plain_result("您还没有任何武将，请先进行招募！\n使用 /三国招募 来获取您的第一个武将。")
            return
        
        general_info_list = []
        for user_general in user_generals:
            general_template = self.general_repo.get_general_by_id(user_general.general_id)
            if general_template:
                level_bonus = (user_general.level - 1) * 0.1
                wu_li = int(general_template.wu_li * (1 + level_bonus))
                zhi_li = int(general_template.zhi_li * (1 + level_bonus))
                tong_shuai = int(general_template.tong_shuai * (1 + level_bonus))
                su_du = int(general_template.su_du * (1 + level_bonus))
                
                rarity_stars = "⭐" * general_template.rarity
                camp_emoji = {"蜀": "🟢", "魏": "🔵", "吴": "🟡", "群": "🔴"}.get(general_template.camp, "⚪")
                
                general_info = f"""
{camp_emoji} {general_template.name} {rarity_stars}
等级：{user_general.level} | 经验：{user_general.exp}/100
武力：{wu_li} | 智力：{zhi_li}
统帅：{tong_shuai} | 速度：{su_du}
技能：{general_template.skill_desc}
"""
                general_info_list.append(general_info.strip())
        
        total_count = len(user_generals)
        message = f"📜 【我的武将】({total_count}个)\n\n" + "\n\n".join(general_info_list)
        
        yield event.plain_result(message)
