# -*- coding: utf-8 -*-
from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star

# 内存数据库，用于最简化测试
fake_db = {
    "users": {}
}

class SanGuoRPGPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        logger.info("三国RPG插件加载中... (重构模式)")

    async def initialize(self):
        logger.info("三国文字RPG插件加载成功！(重构模式)")

    @filter.command("注册")
    async def register_user(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        nickname = event.get_sender_name() or user_id

        if user_id in fake_db["users"]:
            yield event.plain_result(f"您已经注册过了：{nickname}")
        else:
            fake_db["users"][user_id] = {"nickname": nickname}
            yield event.plain_result(f"重构版注册成功！欢迎 {nickname}！")

    @filter.command("签到")
    async def sign_in(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id in fake_db["users"]:
            yield event.plain_result("重构版签到成功！")
        else:
            yield event.plain_result("您尚未注册，请先使用 /注册 命令。")
