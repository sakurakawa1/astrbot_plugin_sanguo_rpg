# -*- coding: utf-8 -*-
# @Time    : 2025/08/03
# @Author  : Cline
# @File    : auto_battle_service.py
# @Software: AstrBot
# @Description: 自动战斗服务，处理自动冒险和自动副本

import asyncio
import random
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from astrbot.core.event_bus import event_bus
from astrbot.core.plugin import IPlugin
from astrbot.core.channel import QQChannel

if TYPE_CHECKING:
    from astrbot_plugin_sanguo_rpg.core.services.user_service import UserService
    from astrbot_plugin_sanguo_rpg.core.services.general_service import GeneralService
    from astrbot_plugin_sanguo_rpg.core.services.dungeon_service import DungeonService


class AutoBattleService:
    def __init__(
        self,
        user_service: "UserService",
        general_service: "GeneralService",
        dungeon_service: "DungeonService",
        plugin: IPlugin,
        game_config: dict,
    ):
        self.user_service = user_service
        self.general_service = general_service
        self.dungeon_service = dungeon_service
        self.plugin = plugin
        self.game_config = game_config
        self._task: Optional[asyncio.Task] = None
        self.is_running = False

    def start(self):
        """启动自动战斗服务"""
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._run_auto_battle_loop())
            print("自动战斗服务已启动。")

    def stop(self):
        """停止自动战斗服务"""
        if self.is_running and self._task:
            self.is_running = False
            self._task.cancel()
            self._task = None
            print("自动战斗服务已停止。")

    async def _run_auto_battle_loop(self):
        """自动战斗的主循环"""
        adventure_config = self.game_config.get("adventure", {})
        min_interval = adventure_config.get("auto_adventure_min_interval_seconds", 60)
        max_interval = adventure_config.get("auto_adventure_max_interval_seconds", 180)

        while self.is_running:
            try:
                await self._process_auto_adventures(min_interval)
                # 可以在这里添加自动副本的逻辑
                # await self._process_auto_dungeons()

            except asyncio.CancelledError:
                print("自动战斗循环被取消。")
                break
            except Exception as e:
                print(f"自动战斗循环出现错误: {e}")

            # 等待一个随机的间隔时间
            await asyncio.sleep(random.randint(min_interval, max_interval))

    async def _process_auto_adventures(self, min_interval: int):
        """处理所有用户的自动冒险"""
        now = datetime.now()
        users_to_process = self.user_service.get_users_with_auto_adventure_enabled()

        for user in users_to_process:
            # 检查冒险冷却时间
            if user.last_adventure_time and (now - user.last_adventure_time) < timedelta(seconds=min_interval):
                continue

            print(f"为用户 {user.nickname} ({user.user_id}) 执行自动冒险...")

            # 执行一次完整的自动冒险
            result = await asyncio.to_thread(self.general_service.adventure, user.user_id, is_auto=True)

            # 更新最后的冒险时间
            await self.user_service.update_last_adventure_time(user.user_id)

            # 发送最终结果通知
            if result.get("success"):
                message = f"【自动冒险】\n{result['message']}"
                channel = QQChannel(user_id=user.user_id)
                await event_bus.publish("send_message", channel=channel, message=message)
            else:
                # 可以在这里处理失败的情况，例如记录日志
                print(f"用户 {user.nickname} 的自动冒险失败: {result.get('message')}")
                # 即使失败，也要确保清理状态
                await asyncio.to_thread(self.user_service.clear_user_adventure_state, user.user_id)
