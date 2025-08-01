# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : adventure_generator.py
# @Software: AstrBot
# @Description: 动态生成冒险故事

import random

# 定义故事模板
STORY_TEMPLATES = [
    "你来到了{location}，突然{event}。",
    "在{location}，你遇到了{event}。",
    "当你正在{location}休息时，{event}发生了。"
]

# 定义故事模块
LOCATIONS = [
    "一片阴森的树林", "一个繁华的市集", "一座废弃的古战场", "一条湍急的河流旁", "一座高耸的山峰上"
]

EVENTS = [
    {
        "event": "发现了一个神秘的宝箱",
        "choices": ["打开宝箱", "离开"],
        "outcomes": [
            {"coins": 50, "exp": 10, "reputation": 1, "health": 0, "status": "无", "description": "你获得了50铜钱和10点经验，声望增加了1。"},
            {"coins": 0, "exp": 5, "reputation": 0, "health": 0, "status": "无", "description": "你谨慎地离开了，获得了5点经验。"}
        ]
    },
    {
        "event": "遇到了一位受伤的商人",
        "choices": ["帮助他", "抢劫他"],
        "outcomes": [
            {"coins": 30, "exp": 15, "reputation": 2, "health": 0, "status": "无", "description": "商人感谢你的帮助，送给你30铜钱和15点经验，声望增加了2。"},
            {"coins": 100, "exp": -10, "reputation": -5, "health": 0, "status": "无", "description": "你抢走了商人所有的钱，但你的声望大幅下降了。"}
        ]
    },
    {
        "event": "碰到了一群山贼",
        "choices": ["战斗", "逃跑"],
        "outcomes": [
            {"coins": 80, "exp": 20, "reputation": 3, "health": -20, "status": "受伤", "description": "你英勇地击败了山贼，获得了80铜钱和20点经验，但你也受了伤。"},
            {"coins": -10, "exp": 5, "reputation": -1, "health": 0, "status": "无", "description": "你成功逃脱了，但掉了一些钱。"}
        ]
    }
]

def generate_adventure():
    """随机生成一个冒险故事"""
    template = random.choice(STORY_TEMPLATES)
    location = random.choice(LOCATIONS)
    event_data = random.choice(EVENTS)

    story_text = template.format(location=location, event=event_data["event"])

    return {
        "story": story_text,
        "choices": event_data["choices"],
        "outcomes": event_data["outcomes"]
    }

if __name__ == '__main__':
    # 测试生成一个冒险故事
    adventure = generate_adventure()
    import json
    print(json.dumps(adventure, ensure_ascii=False, indent=4))
