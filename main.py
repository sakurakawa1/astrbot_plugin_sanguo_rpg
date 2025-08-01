# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : main.py
# @Software: AstrBot
# @Description: 三国文字RPG插件主文件 (最终修复版 - 桩函数调试)

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
        timestamp = datetime.now().strftime("%H:%M:%S")
        logger.info(f"三国RPG插件加载中... (V2 - {timestamp})")

        # --- 1. 加载配置 ---
        self.game_config = {
            "user": { "initial_coins": 50, "initial_yuanbao": 50 },
            "recruit": { "cost_yuanbao": 50, "cooldown_seconds": 300 },
            "adventure": { "cost_coins": 20, "cooldown_seconds": 600 }
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
        timestamp = datetime.now().strftime("%H:%M:%S")
        logger.info(f"三国文字RPG插件加载成功！(V2 - {timestamp})")

    @filter.command("三国帮助", alias={"三国菜单"})
    async def sanguo_help(self, event: AstrMessageEvent):
        """显示三国RPG插件帮助信息"""
        help_text = """
        【三国RPG 帮助菜单】
        /三国注册 - 创建你的角色
        /三国签到 - 每日领取奖励
        /三国我的信息 - 查看你的状态
        /三国招募 - 招募新的武将
        /三国我的武将 - 查看你拥有的武将
        /三国闯关 - 开始一次冒险
        /三国选择 [序号] - 在冒险中做出选择
        /三国管理 - (管理员)管理插件
        """
        yield event.plain_result(help_text.strip())

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
            
        coins_reward = 50
        yuanbao_reward = 50
        exp_reward = 10
        user.coins += coins_reward
        user.yuanbao += yuanbao_reward
        user.exp += exp_reward
        user.last_signed_in = now
        self.user_repo.update(user)
        
        yield event.plain_result(f"签到成功！获得 {coins_reward} 铜钱，{yuanbao_reward} 元宝，{exp_reward} 经验。")
        
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
        # 使用优化后的方法一次性获取所有武将信息
        detailed_generals = self.general_repo.get_user_generals_with_details(user_id)
        
        if not detailed_generals:
            yield event.plain_result("您还没有任何武将，请先进行招募！\n使用 /三国招募 来获取您的第一个武将。")
            return
        
        general_info_list = []
        for general in detailed_generals:
            # 计算等级加成
            level_bonus = (general.level - 1) * 0.1
            wu_li = int(general.wu_li * (1 + level_bonus))
            zhi_li = int(general.zhi_li * (1 + level_bonus))
            tong_shuai = int(general.tong_shuai * (1 + level_bonus))
            su_du = int(general.su_du * (1 + level_bonus))
            
            rarity_stars = "⭐" * general.rarity
            camp_emoji = {"蜀": "🟢", "魏": "🔵", "吴": "🟡", "群": "🔴"}.get(general.camp, "⚪")
            
            # 获取技能描述 (需要额外查询，但可以接受，因为这是模板信息)
            # 为了保持简单，我们暂时不显示技能描述，或者可以从detailed_generals中添加
            # general_template = self.general_repo.get_general_by_id(general.general_id)
            # skill_desc = general_template.skill_desc if general_template else "无"

            general_info = f"""
{camp_emoji} {general.name} {rarity_stars}
等级：{general.level} | 经验：{general.exp}/100
武力：{wu_li} | 智力：{zhi_li}
统帅：{tong_shuai} | 速度：{su_du}
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

    @filter.command("三国闯关", alias={"三国冒险", "三国战斗", "三国挑战"})
    async def adventure(self, event: AstrMessageEvent):
        """开始一次新的闯关冒险"""
        user_id = event.get_sender_id()
        user = self.user_repo.get_by_id(user_id)

        if not user:
            yield event.plain_result("您尚未注册，请先使用 /三国注册 命令。")
            return
            
        if user_id in self.adventure_context:
            yield event.plain_result("您还有一个正在进行的冒险，请先做出选择！\n使用 `/三国选择 [选项编号]` 来继续。")
            return

        # 冷却时间检查
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

        # 检查并扣除费用
        cost = self.game_config.get("adventure", {}).get("cost_coins", 20)
        if user.coins < cost:
            yield event.plain_result(f"💰 铜钱不足！闯关需要 {cost} 铜钱，您只有 {user.coins}。")
            return
        
        user.coins -= cost
        self.user_repo.update(user) # 先扣钱

        # --- 交互式冒险逻辑 ---
        template = random.choice(ADVENTURE_TEMPLATES)
        self.adventure_context[user_id] = template # 存储整个事件模板
        
        options_text = []
        for i, option in enumerate(template["options"]):
            options_text.append(f"{i+1}. {option['text']}")
        
        message = f"""
【{template['name']}】
{template['description']}

请做出您的选择:
{chr(10).join(options_text)}

使用 `/三国选择 [选项编号]` 来决定您的行动。
"""
        # 更新冷却时间
        self._adventure_cooldowns[cooldown_key] = current_time
        
        yield event.plain_result(message.strip())

    @filter.command("三国选择")
    async def adventure_choice(self, event: AstrMessageEvent):
        """在闯关冒险中做出选择"""
        user_id = event.get_sender_id()
        user = self.user_repo.get_by_id(user_id)

        if not user:
            yield event.plain_result("您尚未注册，请先使用 /三国注册 命令。")
            return
            
        if user_id not in self.adventure_context:
            yield event.plain_result("您当前没有正在进行的冒险。请使用 /三国闯关 开始新的冒险。")
            return
            
        choice_text = event.get_plain_text().strip()
        if not choice_text.isdigit():
            yield event.plain_result("无效的选项，请输入数字。")
            return
            
        choice_index = int(choice_text) - 1
        template = self.adventure_context[user_id]
        
        if not (0 <= choice_index < len(template["options"])):
            yield event.plain_result("无效的选项编号。")
            return
            
        option = template["options"][choice_index]
        
        # --- 处理结果 ---
        rewards = option.get("rewards", {})
        coins_change = rewards.get("coins", 0)
        exp_gain = rewards.get("exp", 0)
        
        user.coins += coins_change
        user.exp += exp_gain
        
        # 构建结果消息
        action_text = option.get("text", "进行了一番探索")
        result_message = f"【{template['name']}】\n你选择了“{action_text}”。"

        if coins_change > 0:
            result_message += f"\n\n💰 您获得了 {coins_change} 铜钱。"
        elif coins_change < 0:
            result_message += f"\n\n💸 您损失了 {abs(coins_change)} 铜钱。"
        
        if exp_gain > 0:
            result_message += f"\n📈 您获得了 {exp_gain} 经验。"
        elif exp_gain < 0:
            result_message += f"\n📉 您损失了 {abs(exp_gain)} 经验。"

        if coins_change == 0 and exp_gain == 0:
             result_message += "\n\n平平无奇，什么也没有发生。"

        result_message += f"\n\n当前铜钱: {user.coins}, 当前经验: {user.exp}"

        # 更新数据库并清除上下文
        self.user_repo.update(user)
        del self.adventure_context[user_id]
        
        yield event.plain_result(result_message)

    @filter.command("三国挂机闯关")
    async def auto_adventure(self, event: AstrMessageEvent):
        """自动闯关"""
        yield event.plain_result("该功能正在开发中，敬请期待！")

    @filter.permission_type(PermissionType.ADMIN)
    @filter.command("三国管理")
    async def sanguo_admin(self, event: AstrMessageEvent):
        """三国RPG插件管理命令"""
        args_text = event.get_plain_text().strip()
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
                db_path = "data/sanguo_rpg.db"
                plugin_root_dir = os.path.dirname(__file__)
                migrations_path = os.path.join(plugin_root_dir, "core", "database", "migrations")
                run_migrations(db_path, migrations_path)
                yield event.plain_result("✅ 数据库迁移成功完成。")
            except Exception as e:
                logger.error(f"手动执行数据库迁移时出错: {e}")
                yield event.plain_result(f"❌ 数据库迁移失败: {e}")
            return
            
        # 如果没有匹配的子命令，显示帮助信息
        help_text = """
        【三国管理】可用命令:
        - /三国管理 migrate
          手动执行数据库迁移。
        - /三国管理 add <type> <amount> <user_id>
          为指定用户添加资源。
          <type>: coins, yuanbao, exp
        """
        yield event.plain_result(help_text.strip())
