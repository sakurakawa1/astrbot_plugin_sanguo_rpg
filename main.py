# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : main.py
# @Software: AstrBot
# @Description: 三国文字RPG插件主文件 (最终修复版 - 调试)

import os
import random
import re
from datetime import datetime, timedelta

from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star
from astrbot.core.star.filter.permission import PermissionType

from astrbot_plugin_sanguo_rpg.core.database.migration import run_migrations
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_user_repo import SqliteUserRepository
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_general_repo import SqliteGeneralRepository
from astrbot_plugin_sanguo_rpg.core.services.data_setup_service import DataSetupService
from astrbot_plugin_sanguo_rpg.draw.help import draw_help_image
from astrbot_plugin_sanguo_rpg.core.adventure_templates import ADVENTURE_TEMPLATES
from astrbot_plugin_sanguo_rpg.core.domain.models import User

class SanGuoRPGPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        logger.info("三国RPG插件加载中... (最终修复版 - 调试)")

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
        
        # 用于存储冷却时间的字典
        self._recruit_cooldowns = {}
        self._adventure_cooldowns = {}
        # 用于存储闯关上下文的字典
        self.adventure_context = {}


    async def initialize(self):
        """插件异步初始化"""
        logger.info("三国文字RPG插件加载成功！(最终修复版 - 调试)")

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
        
        if self.user_repo.get_by_id(user_id):
            yield event.plain_result("您已经注册过了，无需重复注册。")
            return

        new_user = User(
            user_id=user_id,
            nickname=nickname,
            coins=self.game_config.get("user", {}).get("initial_coins", 1000),
            yuanbao=self.game_config.get("user", {}).get("initial_yuanbao", 100),
            exp=0,
            created_at=datetime.now(),
            last_signed_in=None
        )
        self.user_repo.add(new_user)
        yield event.plain_result(f"欢迎主公 {nickname}！您已成功注册，获得初始资金，开启您的三国霸业！")

    @filter.command("三国签到")
    async def sign_in(self, event: AstrMessageEvent):
        """每日签到"""
        user_id = event.get_sender_id()
        user = self.user_repo.get_by_id(user_id)
        if not user:
            yield event.plain_result("您尚未注册，请先使用 /三国注册 命令。")
            return
        
        now = datetime.now()
        if user.last_signed_in and user.last_signed_in.date() == now.date():
            yield event.plain_result("你今天已经签到过了，明天再来吧！")
            return
            
        coins_reward = 200
        exp_reward = 10
        user.coins += coins_reward
        user.exp += exp_reward
        user.last_signed_in = now
        self.user_repo.update(user)
        
        yield event.plain_result(f"签到成功！获得 {coins_reward} 铜钱，{exp_reward} 经验。")
        
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
        if user.yuanbao < recruit_cost:
            yield event.plain_result(f"💎 元宝不足！招募需要 {recruit_cost} 元宝，您当前只有 {user.yuanbao} 元宝。")
            return
        
        recruited_general = self.general_repo.get_random_general_by_rarity_pool()
        if not recruited_general:
            yield event.plain_result("❌ 招募失败，请稍后再试。")
            return
        
        user.yuanbao -= recruit_cost
        self.user_repo.update(user)
        
        success = self.general_repo.add_user_general(user_id, recruited_general.general_id)
        if not success:
            user.yuanbao += recruit_cost
            self.user_repo.update(user)
            yield event.plain_result("❌ 招募失败，请稍后再试。")
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
💰 花费：{recruit_cost} 元宝
💎 剩余元宝：{user.yuanbao}
使用 /三国我的武将 查看所有武将！
"""
        yield event.plain_result(message.strip())

    # @filter.command("三国闯关", alias={"三国冒险", "三国战斗", "三国挑战"})
    # async def adventure(self, event: AstrMessageEvent):
    #     """闯关冒险"""
    #     pass

    # @filter.command("三国挂机闯关")
    # async def auto_adventure(self, event: AstrMessageEvent):
    #     """自动闯关"""
    #     pass

    # @filter.permission_type(PermissionType.ADMIN)
    # @filter.command("三国管理")
    # async def sanguo_admin(self, event: AstrMessageEvent):
    #     """三国RPG插件管理命令"""
    #     pass
