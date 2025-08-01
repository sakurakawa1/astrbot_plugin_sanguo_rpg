# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : adventure_generator.py
# @Software: AstrBot
# @Description: 全新的多环节、分支式冒险故事生成器

import random
from .adventure_stories import OPENINGS, EVENTS, RESOLUTIONS

# --- 随机数据池 ---
# 为了让故事更生动，我们在这里定义一些随机名称池
RANDOM_POOLS = {
    "general_names": ["张角", "关羽", "张飞", "董卓", "吕布", "貂蝉", "袁绍", "曹操", "孙坚", "刘备"],
    "city_names": ["长安", "洛阳", "许昌", "邺城", "成都", "建业", "襄阳", "宛城", "下邳", "官渡"],
    "item_names": ["一袋米", "破旧的草鞋", "一壶浊酒", "发黄的布帛", "生锈的铜镜", "奇怪的石头"]
}

class AdventureGenerator:
    """
    一个能够生成和管理多环节、分支式冒险故事的类。
    它利用 adventure_stories.py 中定义的结构来创建动态的故事情节。
    """

    def __init__(self, user_id, user_service):
        self.user_id = user_id
        self.user_service = user_service
        # active_adventures 将存储玩家的当前冒险状态
        # 格式: {user_id: {"current_stage": "stage_id", "context": {}}}
        # 为简化，我们可以在 user_service 中管理这个状态
        pass

    def _render_template(self, template, context=None):
        """
        渲染故事模板，替换占位符。
        :param template: 包含占位符的字符串。
        :param context: 包含替换值的字典。
        :return: 渲染后的字符串。
        """
        # 基础占位符
        player = self.user_service.get_user(self.user_id)
        replacements = {
            "{player_name}": player.nickname if player else "你",
            # --- 从随机池中动态获取 ---
            "{random_general_name}": random.choice(RANDOM_POOLS["general_names"]),
            "{random_city_name}": random.choice(RANDOM_POOLS["city_names"]),
            "{random_item_name}": random.choice(RANDOM_POOLS["item_names"]),
            "{random_amount}": str(random.randint(50, 200))
        }
        if context:
            replacements.update(context)

        for key, value in replacements.items():
            template = template.replace(key, value)
        return template

    def start_adventure(self):
        """
        开始一个新的冒险。
        1. 随机选择一个开场 (OPENING)。
        2. 根据开场的标签，筛选并随机选择一个匹配的事件 (EVENT)。
        3. 返回初始的故事描述和选项。
        """
        # 1. 选择开场
        opening = random.choice(OPENINGS)
        
        # 2. 根据标签筛选并选择事件
        possible_events = [
            event for event in EVENTS 
            if any(tag in opening["tags"] for tag in event["tags"])
        ]
        if not possible_events:
            # 如果没有匹配的事件，可以返回一个通用事件或错误
            # 为简单起见，我们这里重新随机选一个，实际应用中应有更好处理
            event = random.choice(EVENTS)
        else:
            event = random.choice(possible_events)

        # 3. 组合故事文本
        story_text = self._render_template(opening["template"]) + "\n" + self._render_template(event["template"])
        
        # 4. 保存玩家状态 (重要！)
        # 状态应包含当前事件ID，以便后续处理选项
        self.user_service.set_user_adventure_state(self.user_id, {
            "current_event_id": event["id"],
            "options": event["options"]
        })

        return {
            "text": story_text,
            "options": [opt["text"] for opt in event["options"]],
            "is_final": False
        }

    def advance_adventure(self, choice_index):
        """
        根据玩家的选择推进冒险。
        1. 获取玩家当前的冒险状态。
        2. 根据选择的索引，找到对应的 next_stage。
        3. 在 RESOLUTIONS 中查找 next_stage 的定义。
        4. 处理结局或新的选择。
        """
        state = self.user_service.get_user_adventure_state(self.user_id)
        if not state:
            return {"text": "你当前没有正在进行的冒险。", "options": [], "is_final": True}

        try:
            selected_option = state["options"][choice_index]
            next_stage_id = selected_option["next_stage"]
        except (IndexError, KeyError):
            return {"text": "无效的选择。", "options": [], "is_final": True}

        # 在 RESOLUTIONS 中查找下一个阶段
        resolution = RESOLUTIONS.get(next_stage_id)
        if not resolution:
            return {"text": "故事线断了，出现了一个未定义的结局。", "options": [], "is_final": True}

        # 清除当前冒险状态，因为已经进入下一阶段
        self.user_service.clear_user_adventure_state(self.user_id)

        story_text = self._render_template(resolution["template"])
        
        if resolution.get("type") == "final":
            # 故事结束
            rewards = resolution.get("rewards", {})
            # 应用奖励
            self.user_service.apply_adventure_rewards(self.user_id, rewards)
            
            # --- 构建奖励描述文本 (优化版) ---
            cost = self.user_service.game_config.get("adventure", {}).get("cost_coins", 20)
            coin_reward = rewards.get("coins", 0)
            net_coins = coin_reward - cost

            reward_texts = [f"🔸 闯关花费: -{cost} 铜钱"]
            if coin_reward > 0:
                reward_texts.append(f"💰 铜钱收益: +{coin_reward}")
            if "exp" in rewards and rewards["exp"] > 0:
                reward_texts.append(f"📈 经验: +{rewards['exp']}")
            if "reputation" in rewards and rewards["reputation"] > 0:
                reward_texts.append(f"🌟 声望: +{rewards['reputation']}")
            if "items" in rewards and rewards["items"]:
                reward_texts.append(f"🎁 获得物品: {', '.join(rewards['items'])}")
            
            reward_texts.append("="*15)
            reward_texts.append(f"本次净赚: {net_coins} 铜钱")
            
            story_text += "\n--- 结算 ---\n" + "\n".join(reward_texts)

            return {
                "text": story_text,
                "options": [],
                "is_final": True
            }
        
        elif resolution.get("type") == "choice":
            # 故事继续，有新的选择
            new_options = resolution["options"]
            # 将故事文本也存入状态，以便玩家随时查看
            self.user_service.set_user_adventure_state(self.user_id, {
                "current_event_id": None, # 后续阶段没有事件ID
                "options": new_options,
                "story_text": story_text # 保存当前的故事文本
            })
            return {
                "text": story_text,
                "options": [opt["text"] for opt in new_options],
                "is_final": False
            }
        else:
            # 默认作为最终结局处理
            return {
                "text": story_text,
                "options": [],
                "is_final": True
            }

# 注意: 这个文件现在依赖于 user_service 来管理状态。
# 在 main.py 中使用时，需要实例化 user_service 并传递给 AdventureGenerator。
# 例如:
# user_service = UserService(db_path)
# adv_gen = AdventureGenerator(user_id, user_service)
# result = adv_gen.start_adventure()
# ...
# result = adv_gen.advance_adventure(choice_index)
