# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : main.py
# @Software: AstrBot
# @Description: 三国文字RPG插件主文件 (最终修复版 - 桩函数调试)

import os
import random
import re
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
from astrbot_plugin_sanguo_rpg.draw.help import draw_help_image
from astrbot_plugin_sanguo_rpg.core.adventure_stories import OPENINGS, EVENTS, RESOLUTIONS
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
        data_dir = os.path.join(plugin_root_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "sanguo_rpg.db")
        self.migrations_path = os.path.join(plugin_root_dir, "core", "database", "migrations")
        
        logger.info(f"数据库绝对路径: {self.db_path}")

        # --- 2.5. 运行数据库迁移并验证 ---
        try:
            run_migrations(self.db_path, self.migrations_path)
            logger.info("数据库迁移检查完成。")

            # 验证 'users' 表是否已创建
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            if cursor.fetchone() is None:
                logger.error("CRITICAL: 迁移后 'users' 表不存在！数据库可能已损坏或权限不足。")
                logger.error("建议管理员运行 '/三国管理 force-migrate' 命令来强制重建数据库。")
            else:
                logger.info("数据库基础表 'users' 已确认存在。")
            conn.close()

        except Exception as e:
            logger.error(f"在 __init__ 期间执行数据库迁移或验证时出错: {e}")

        # --- 3. 组合根：实例化仓储和服务 ---
        self.user_repo = SqliteUserRepository(self.db_path)
        self.general_repo = SqliteGeneralRepository(self.db_path)
        self.user_general_repo = SqliteUserGeneralRepository(self.db_path)
        self.title_repo = SqliteTitleRepository(self.db_path)
        self.dungeon_repo = DungeonRepository(self.db_path)

        self.leveling_service = LevelingService(self.user_repo, self.user_general_repo)
        self.dungeon_service = DungeonService(self.dungeon_repo, self.user_repo)
        self.user_service = UserService(self.user_repo, self.game_config)
        
        data_setup_service = DataSetupService(self.general_repo, self.db_path)
        data_setup_service.setup_initial_data()
        
        # 用于存储冷却时间的字典
        self._recruit_cooldowns = {}
        self._adventure_cooldowns = {}
        # 用于存储用户冒险状态的字典 {user_id: {"description": "...", "options": [...], "state_context": {...}}}
        self.user_adventure_states = {}

    def _get_random_general_name(self):
        """获取一个随机的武将名（桩函数）"""
        # 理想情况下，这应该从一个预定义的列表中随机选择
        return random.choice(["曹操", "刘备", "孙权", "路人甲"])

    def _process_story_template(self, template_text: str, user: User) -> str:
        """处理故事模板中的变量"""
        
        # 玩家信息
        template_text = template_text.replace("{player_name}", user.nickname)
        
        # 随机信息
        template_text = template_text.replace("{random_general_name}", self._get_random_general_name())
        template_text = template_text.replace("{random_amount}", str(random.randint(50, 200)))
        template_text = template_text.replace("{random_item_name}", random.choice(["草药", "铁矿石", "兵法心得"]))
        
        # 动态计算
        if "{calculated_bribe}" in template_text:
            bribe_amount = int(user.coins * 0.1) # 示例：贿赂金额为当前铜钱的10%
            template_text = template_text.replace("{calculated_bribe}", str(bribe_amount))
            
        return template_text

    async def initialize(self):
        """插件异步初始化"""
        # 迁移已在 __init__ 中完成
        timestamp = datetime.now().strftime("%H:%M:%S")
        logger.info(f"三国文字RPG插件加载成功！(V2 - {timestamp})")

    @filter.command("三国帮助", alias={"三国菜单"})
    async def sanguo_help(self, event: AstrMessageEvent):
        """显示三国RPG插件帮助信息"""
        help_text = """
        【三国RPG 帮助菜单】
        /三国注册 - 开启你的三国之旅
        /三国签到 - 每日领取奖励
        /三国我的信息 - 查看你的角色状态
        /三国我的武将 - 查看你拥有的武将
        /三国招募 - 招募新的武将
        /三国升级武将 [武将ID] - 升级你的武将
        /三国闯关 - 开始一段随机冒险
        /三国选择 [选项] - 在冒险中做出选择
        /三国副本 - 查看或挑战副本
        /三国称号 - 查看或兑换称号
        /三国管理 - (管理员)管理插件
        """
        yield help_text.strip()

    @filter.command("三国注册")
    async def register_user(self, event: AstrMessageEvent):
        """注册用户"""
        user_id = event.get_user_id()
        nickname = event.get_user_name()
        
        result = self.user_service.register(user_id, nickname)
        yield result["message"]

    @filter.command("三国签到")
    async def sign_in(self, event: AstrMessageEvent):
        """每日签到"""
        user_id = event.get_user_id()
        result = self.user_service.sign_in(user_id)
        yield result["message"]
        
    @filter.command("三国我的信息")
    async def my_info(self, event: AstrMessageEvent):
        """查看我的信息"""
        user_id = event.get_user_id()
        result = self.user_service.get_user_info(user_id)
        yield result["message"]
        
    @filter.command("三国我的武将", alias={"三国武将列表", "三国查看武将"})
    async def my_generals(self, event: AstrMessageEvent):
        """查看我的武将"""
        user_id = event.get_user_id()
        # 使用优化后的方法一次性获取所有武将信息
        detailed_generals = self.general_repo.get_user_generals_with_details(user_id)
        
        if not detailed_generals:
            yield "您还没有任何武将，请先进行招募！\n使用 /三国招募 来获取您的第一个武将。"
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
{camp_emoji} {general.name} {rarity_stars} (ID: {general.instance_id})
等级：{general.level} | 经验：{general.exp}/100
武力：{wu_li} | 智力：{zhi_li}
统帅：{tong_shuai} | 速度：{su_du}
"""
            general_info_list.append(general_info.strip())
        
        total_count = len(detailed_generals)
        message = f"📜 【我的武将】({total_count}个)\n\n" + "\n\n".join(general_info_list)
        
        yield message

    @filter.command("三国招募", alias={"三国招募武将", "三国抽卡"})
    async def recruit_general(self, event: AstrMessageEvent):
        """招募武将"""
        user_id = event.get_user_id()
        user = self.user_repo.get_by_id(user_id)
        if not user:
            yield "请先使用 /三国注册 命令注册账户！"
            return
        
        cooldown_key = f"recruit_{user_id}"
        current_time = datetime.now()
        
        if cooldown_key in self._recruit_cooldowns:
            last_recruit_time = self._recruit_cooldowns[cooldown_key]
            cooldown_seconds = self.game_config.get("recruit", {}).get("cooldown_seconds", 300)
            time_diff = (current_time - last_recruit_time).total_seconds()
            
            if time_diff < cooldown_seconds:
                remaining_time = int(cooldown_seconds - time_diff)
                yield f"⏰ 招募冷却中，还需等待 {remaining_time} 秒后才能再次招募。"
                return
        
        recruit_cost = self.game_config.get("recruit", {}).get("cost_yuanbao", 50)
        
        # --- “望族”技能折扣计算 ---
        user_generals = self.general_repo.get_user_generals_with_details(user_id)
        wangzu_count = sum(1 for g in user_generals if "望族" in g.skill_desc)
        discount_rate = min(wangzu_count * 0.1, 0.2) # 最多20%折扣
        
        final_cost = int(recruit_cost * (1 - discount_rate))
        discount_info = f" (原价: {recruit_cost})" if discount_rate > 0 else ""
        
        if user.yuanbao < final_cost:
            yield f"💎 元宝不足！招募需要 {final_cost} 元宝{discount_info}，您当前只有 {user.yuanbao} 元宝。"
            return
        
        # --- 声望影响招募 ---
        reputation_luck_bonus = min(user.reputation / 5000, 0.2) # 每500声望提升10%稀有度概率，最高20%
        
        recruited_general = self.general_repo.get_random_general_by_rarity_pool(reputation_luck_bonus)
        if not recruited_general:
            yield "❌ 招募系统繁忙，请稍后再试。"
            return

        # 检查用户是否已拥有该武将
        if self.general_repo.check_user_has_general(user_id, recruited_general.general_id):
            # 更新冷却时间，即使招募到重复的武将也进入冷却
            self._recruit_cooldowns[cooldown_key] = current_time
            yield f"您已拥有武将【{recruited_general.name}】，本次招募未消耗元宝，但招募机会已使用，进入冷却。"
            return

        # 确认不重复后，再扣费和添加
        user.yuanbao -= final_cost
        self.user_repo.update(user)
        
        success = self.general_repo.add_user_general(user_id, recruited_general.general_id)
        if not success:
            # 如果添加失败，需要回滚费用
            user.yuanbao += recruit_cost
            self.user_repo.update(user)
            yield "❌ 数据库繁忙，招募失败，元宝已退还。"
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
        yield message.strip()

    @filter.command("三国升级武将", alias={"三国武将升级"})
    async def level_up_general(self, event: AstrMessageEvent):
        """升级指定的武将"""
        user_id = event.get_user_id()
        args = event.message_str.split()
        if len(args) < 2 or not args[1].isdigit():
            yield "指令格式错误，请使用：/三国升级武将 [武将ID]"
            return

        general_instance_id = int(args[1])
        result_message = self.leveling_service.level_up_general(user_id, general_instance_id)
        yield result_message

    @filter.command("三国称号")
    async def title_system(self, event: AstrMessageEvent):
        """称号系统，包括列表和兑换"""
        user_id = event.get_user_id()
        user = self.user_repo.get_by_id(user_id)
        if not user:
            yield "您尚未注册，请先使用 /三国注册 命令。"
            return

        args = event.message_str.replace("三国称号", "").strip().split()
        sub_command = args[0] if args else "列表"

        if sub_command in ["列表", "list"]:
            titles = self.title_repo.get_all_titles()
            if not titles:
                yield "暂无可用称号。"
                return
            
            title_list_text = "【称号列表】\n\n"
            for title in titles:
                status = "✅" if user.reputation >= title.required_reputation else "❌"
                title_list_text += f"{status} {title.name} (要求声望: {title.required_reputation})\n"
            
            title_list_text += "\n使用 `/三国称号兑换 [称号名称]` 来兑换称号。"
            yield title_list_text

        elif sub_command in ["兑换", "exchange"]:
            if len(args) < 2:
                yield "请输入要兑换的称号名称。格式: /三国称号兑换 [称号名称]"
                return
            
            title_name = args[1]
            target_title = self.title_repo.get_title_by_name(title_name)

            if not target_title:
                yield f"未找到名为“{title_name}”的称号。"
                return

            if user.reputation < target_title.required_reputation:
                yield f"声望不足！兑换“{target_title.name}”需要 {target_title.required_reputation} 声望，您当前拥有 {user.reputation} 声望。"
                return
            
            user.title = target_title.name
            self.user_repo.update(user)
            yield f"恭喜！您已成功装备称号：【{target_title.name}】"
        
        else:
            yield "无效的子命令。可用命令: /三国称号列表, /三国称号兑换 [名称]"

    def _generate_new_adventure(self, user: User):
        """从模块化组件生成新的冒险，并处理模板。"""
        opening = random.choice(OPENINGS)
        
        compatible_events = [
            event for event in EVENTS if any(tag in opening["tags"] for tag in event["tags"])
        ]
        
        if not compatible_events:
            return None, None, None

        event_module = random.choice(compatible_events)
        
        # 组合并处理模板
        raw_description = f"{opening['template']} {event_module['template']}"
        processed_description = self._process_story_template(raw_description, user)
        
        # 处理选项中的模板
        processed_options = []
        for option in event_module['options']:
            processed_text = self._process_story_template(option['text'], user)
            processed_options.append({**option, "text": processed_text})

        initial_state_context = {"type": "event", "id": event_module["id"]}
        
        return processed_description, processed_options, initial_state_context

    @filter.command("三国闯关", alias={"三国冒险", "三国战斗", "三国挑战"})
    async def adventure(self, event: AstrMessageEvent):
        """开始或继续一次闯关冒险"""
        user_id = event.get_user_id()
        user = self.user_repo.get_by_id(user_id)

        if not user:
            yield "您尚未注册，请先使用 /三国注册 命令。"
            return

        # --- 智能路由：如果玩家在冒险中，且命令带有数字，则视为选择 ---
        args_str = event.message_str.replace("三国闯关", "", 1).strip()
        if user_id in self.user_adventure_states and args_str.isdigit():
            # 伪造一个新的事件对象，将消息内容替换为“三国选择”
            # 这样可以直接复用 adventure_choice 的逻辑
            import copy
            fake_event = copy.copy(event)
            fake_event.message_str = f"三国选择 {args_str}"
            # 使用 yield from 来委托执行
            async for result in self.adventure_choice(fake_event):
                yield result
            return

        # 如果玩家正在冒险中，但没有提供数字，则显示当前状态
        if user_id in self.user_adventure_states:
            state_data = self.user_adventure_states[user_id]
            description = state_data["description"]
            options = state_data["options"]
            
            options_text = [f"{i+1}. {opt['text']}" for i, opt in enumerate(options)]
            message = f"""
【冒险进行中】
{description}

请做出您的-选择:
{chr(10).join(options_text)}

使用 `/三国选择 [选项编号]` 来决定您的行动。
"""
            yield message.strip()
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
                yield f"⚔️ 闯关冷却中，还需等待 {remaining_time} 秒。"
                return

        cost = self.game_config.get("adventure", {}).get("cost_coins", 20)
        if user.coins < cost:
            yield f"💰 铜钱不足！闯关需要 {cost} 铜钱，您只有 {user.coins}。"
            return
        
        user.coins -= cost
        
        # --- 生成新故事并开始 ---
        description, options, state_context = self._generate_new_adventure(user)
        if not description:
            # 如果生成失败，需要回滚费用
            user.coins += cost
            self.user_repo.update(user)
            yield "❌ 冒险故事生成失败，费用已退还，请稍后再试。"
            return

        # 成功生成故事后才更新用户状态
        self.user_repo.update(user)

        self.user_adventure_states[user_id] = {
            "description": description,
            "options": options,
            "state_context": state_context
        }
        
        options_text = [f"{i+1}. {opt['text']}" for i, opt in enumerate(options)]
        
        message = f"""
【新的冒险】
{description}

请做出您的选择:
{chr(10).join(options_text)}

使用 `/三国选择 [选项编号]` 来决定您的行动。
"""
        self._adventure_cooldowns[cooldown_key] = current_time
        yield message.strip()

    @filter.command("三国选择")
    async def adventure_choice(self, event: AstrMessageEvent):
        """在闯关冒险中做出选择"""
        user_id = event.get_user_id()
        user = self.user_repo.get_by_id(user_id)

        if not user:
            yield "您尚未注册，请先使用 /三国注册 命令。"
            return
            
        if user_id not in self.user_adventure_states:
            yield "您当前没有正在进行的冒险。请使用 /三国闯关 开始新的冒险。"
            return
            
        choice_text = event.message_str.replace("三国选择", "", 1).strip()
        if not choice_text.isdigit():
            yield "无效的选项，请输入数字。"
            return
            
        choice_index = int(choice_text) - 1
        
        state_data = self.user_adventure_states[user_id]
        current_options = state_data["options"]

        if not (0 <= choice_index < len(current_options)):
            yield "无效的选项编号。"
            return
            
        option = current_options[choice_index]
        next_stage_id = option["next_stage"]
        
        resolution = RESOLUTIONS.get(next_stage_id)
        if not resolution:
            del self.user_adventure_states[user_id]
            yield f"错误：找不到后续剧情 '{next_stage_id}'，已重置状态。"
            return

        # --- 处理成本和奖励 ---
        cost_match = re.search(r'\((\d+)\s*铜钱\)', option['text'])
        if cost_match:
            cost = int(cost_match.group(1))
            if user.coins < cost:
                yield f"💰 铜钱不足！此选项需要 {cost} 铜钱，您只有 {user.coins}。"
                return
            user.coins -= cost

        rewards = resolution.get("rewards", {})
        reward_parts = []

        # --- 声望加成计算 ---
        reputation_bonus = min(user.reputation / 1000, 0.5) # 每10声望+1%，最高50%
        bonus_info = f" (声望加成 {reputation_bonus:.0%})" if reputation_bonus > 0 else ""

        # --- 统一处理所有奖励类型 ---
        for key, value in rewards.items():
            original_value = value
            if key in ["coins", "exp"]:
                value = int(value * (1 + reputation_bonus))
            
            if key == "coins":
                user.coins += value
                if value != 0: reward_parts.append(f"铜钱 {'+' if value > 0 else ''}{value}{bonus_info if key == 'coins' and reputation_bonus > 0 else ''}")
            elif key == "exp":
                user.exp += value
                if value != 0: reward_parts.append(f"经验 {'+' if value > 0 else ''}{value}{bonus_info if key == 'exp' and reputation_bonus > 0 else ''}")
            elif key == "yuanbao":
                user.yuanbao += value
                if value != 0: reward_parts.append(f"元宝 {'+' if value > 0 else ''}{value}")
            elif key == "health":
                user.health += value
                if value != 0: reward_parts.append(f"健康 {'+' if value > 0 else ''}{value}")
            elif key == "reputation":
                user.reputation += value
                if value != 0: reward_parts.append(f"声望 {'+' if value > 0 else ''}{value}")
            elif key == "status":
                # 状态是覆盖而不是增减
                user.status = value
                reward_parts.append(f"状态变为: {value}")
            elif key == "items" and value:
                # 假设物品是添加到某个列表，目前模型中没有，先记录文本
                reward_parts.append(f"获得物品: {', '.join(value)}")

        self.user_repo.update(user)

        # --- 故事推进 ---
        # 处理结果文本中的模板
        raw_result_text = resolution.get("template", "冒险继续...")
        processed_result_text = self._process_story_template(raw_result_text, user)

        if resolution.get("type") == "final":
            message = f"【冒险结局】\n{processed_result_text}"
            
            if reward_parts:
                message += "\n\n【结算】\n" + " | ".join(reward_parts)

            # 显示更新后的核心属性
            message += f"\n\n当前状态：\n铜钱: {user.coins}, 经验: {user.exp}, 声望: {user.reputation}"
            
            del self.user_adventure_states[user_id]
            yield message
        
        elif resolution.get("type") == "choice":
            new_description = processed_result_text
            
            # 处理新选项中的模板
            new_options = []
            for opt in resolution['options']:
                processed_text = self._process_story_template(opt['text'], user)
                new_options.append({**opt, "text": processed_text})
            
            new_state_context = {"type": "resolution", "id": next_stage_id}
            
            self.user_adventure_states[user_id] = {
                "description": new_description,
                "options": new_options,
                "state_context": new_state_context
            }
            
            options_text = [f"{i+1}. {opt['text']}" for i, opt in enumerate(new_options)]
            message = f"""
【剧情发展】
{new_description}

请做出您的选择:
{chr(10).join(options_text)}

使用 `/三国选择 [选项编号]` 来决定您的行动。
"""
            yield message.strip()

    @filter.command("三国挂机闯关")
    async def auto_adventure(self, event: AstrMessageEvent):
        """自动闯关"""
        yield "该功能正在开发中，敬请期待！"

    @filter.command("三国副本", alias={"三国副本列表", "三国副本挑战"})
    async def dungeon_system(self, event: AstrMessageEvent):
        """副本系统，包括列表和挑战"""
        user_id = event.get_user_id()
        user = self.user_repo.get_by_id(user_id)
        if not user:
            yield "您尚未注册，请先使用 /三国注册 命令。"
            return

        # 更稳健的参数解析，移除所有可能的命令前缀
        command_prefixes = ["三国副本列表", "三国副本挑战", "三国副本"]
        args_str = event.message_str
        for prefix in command_prefixes:
            if args_str.startswith(prefix):
                args_str = args_str[len(prefix):].strip()
                break

        # 如果没有参数，或者参数是 "列表" 或 "list"，则显示列表
        if not args_str or args_str in ["列表", "list"]:
            dungeon_list_message = self.dungeon_service.list_dungeons(user)
            yield dungeon_list_message
        else:
            # 否则，将整个参数视为副本名称
            dungeon_name = args_str
            result_message = self.dungeon_service.start_dungeon(user, dungeon_name)
            yield result_message

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
                yield "❌ 参数格式错误。\n正确格式: /三国管理 add <resource_type> <amount> <user_id>"
                return
            
            _, resource_type, amount_str, user_id = parts
            
            user = self.user_repo.get_by_id(user_id)
            if not user:
                yield f"❌ 找不到用户: {user_id}"
                return
            
            try:
                amount = int(amount_str)
            except ValueError:
                yield f"❌ 数量必须是整数: {amount_str}"
                return

            if resource_type.lower() == "coins":
                user.coins += amount
                self.user_repo.update(user)
                yield f"✅ 成功为用户 {user.nickname} ({user_id}) 添加了 {amount} 铜钱。"
            elif resource_type.lower() == "yuanbao":
                user.yuanbao += amount
                self.user_repo.update(user)
                yield f"✅ 成功为用户 {user.nickname} ({user_id}) 添加了 {amount} 元宝。"
            elif resource_type.lower() == "exp":
                user.exp += amount
                self.user_repo.update(user)
                yield f"✅ 成功为用户 {user.nickname} ({user_id}) 添加了 {amount} 经验。"
            else:
                yield f"❌ 未知的资源类型: {resource_type}。可用: coins, yuanbao, exp"
            return

        # 获取正确的数据库绝对路径
        plugin_root_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(plugin_root_dir, "data")
        db_path = os.path.join(data_dir, "sanguo_rpg.db")
        migrations_path = os.path.join(plugin_root_dir, "core", "database", "migrations")

        # 保留数据库迁移功能
        if args_text == "migrate":
            try:
                run_migrations(db_path, migrations_path)
                yield "✅ 数据库迁移成功完成。"
            except Exception as e:
                logger.error(f"手动执行数据库迁移时出错: {e}")
                yield f"❌ 数据库迁移失败: {e}"
            return

        # 添加强制迁移功能
        if args_text == "force-migrate":
            try:
                # 1. 清空迁移记录
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                # 使用 DROP TABLE IF EXISTS 和 CREATE TABLE 来确保一个干净的状态
                cursor.execute("DROP TABLE IF EXISTS schema_migrations")
                cursor.execute("""
                    CREATE TABLE schema_migrations (
                        version TEXT PRIMARY KEY NOT NULL
                    )
                """)
                conn.commit()
                conn.close()
                logger.info("已重置 schema_migrations 表，准备强制重新迁移。")

                # 2. 重新运行所有迁移
                plugin_root_dir = os.path.dirname(__file__)
                migrations_path = os.path.join(plugin_root_dir, "core", "database", "migrations")
                run_migrations(db_path, migrations_path)
                yield "✅ 强制迁移成功完成。所有迁移已重新应用。"
            except Exception as e:
                logger.error(f"手动执行强制数据库迁移时出错: {e}")
                yield f"❌ 强制数据库迁移失败: {e}"
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
        yield help_text.strip()
