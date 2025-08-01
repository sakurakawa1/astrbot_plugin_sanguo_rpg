# -*- coding: utf-8 -*-
ADVENTURE_TEMPLATES = [
    {
        "id": 1,
        "name": "黄巾之乱",
        "description": "你遇到了一小股黄巾军，他们看起来很弱小。",
        "options": [
            {"text": "正面攻击", "success_rate": 0.8, "rewards": {"coins": 50, "exp": 10}, "failure_text": "你被黄巾军击败了！"},
            {"text": "绕道而行", "success_rate": 1.0, "rewards": {"coins": 5, "exp": 1}, "failure_text": ""},
        ],
    },
    {
        "id": 2,
        "name": "山中奇遇",
        "description": "你在山中发现一个山洞，里面似乎有宝藏。",
        "options": [
            {"text": "进入山洞", "success_rate": 0.5, "rewards": {"coins": 200, "exp": 50}, "failure_text": "山洞里空无一物，你失望而归。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"coins": 10, "exp": 5}, "failure_text": ""},
        ],
    },
    # Add at least 50 templates here
    {
        "id": 3,
        "name": "遭遇猛虎",
        "description": "你在森林里遇到了一只猛虎。",
        "options": [
            {"text": "与猛虎搏斗", "success_rate": 0.3, "rewards": {"coins": 150, "exp": 80}, "failure_text": "你被猛虎咬伤，仓皇逃跑。"},
            {"text": "悄悄溜走", "success_rate": 0.9, "rewards": {"coins": 20, "exp": 10}, "failure_text": "你成功地避开了猛虎。"},
        ],
    },
    {
        "id": 4,
        "name": "解救村民",
        "description": "你看到一群土匪在欺负村民。",
        "options": [
            {"text": "上前解救", "success_rate": 0.7, "rewards": {"coins": 100, "exp": 60}, "failure_text": "你不是土匪的对手，被打得落花流水。"},
            {"text": "视而不见", "success_rate": 1.0, "rewards": {"coins": -10, "exp": -5}, "failure_text": ""},
        ],
    },
    {
        "id": 5,
        "name": "古墓探险",
        "description": "你发现了一座古墓，里面可能藏有宝物。",
        "options": [
            {"text": "进入古墓", "success_rate": 0.4, "rewards": {"coins": 300, "exp": 100}, "failure_text": "古墓里机关重重，你差点丧命。"},
            {"text": "放弃探险", "success_rate": 1.0, "rewards": {"coins": 15, "exp": 8}, "failure_text": ""},
        ],
    },
    {
        "id": 6,
        "name": "偶遇名士",
        "description": "你遇到一位正在游历的名士。",
        "options": [
            {"text": "上前请教", "success_rate": 0.6, "rewards": {"exp": 150}, "failure_text": "名士对你的问题不屑一顾。"},
            {"text": "默默离开", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 7,
        "name": "商人求助",
        "description": "一位商人请求你护送他的货物。",
        "options": [
            {"text": "接受委托", "success_rate": 0.8, "rewards": {"coins": 120, "exp": 40}, "failure_text": "货物在途中被劫，你一无所获。"},
            {"text": "拒绝委托", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 8,
        "name": "神秘老人",
        "description": "一位神秘的老人向你兜售一本古籍。",
        "options": [
            {"text": "购买古籍", "success_rate": 0.2, "rewards": {"exp": 200}, "failure_text": "你花光了钱，却发现古籍是假的。"},
            {"text": "不予理会", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 9,
        "name": "河流挡路",
        "description": "一条湍急的河流挡住了你的去路。",
        "options": [
            {"text": "尝试渡河", "success_rate": 0.5, "rewards": {"exp": 30}, "failure_text": "你差点被淹死，只好原路返回。"},
            {"text": "寻找桥梁", "success_rate": 1.0, "rewards": {"exp": 10}, "failure_text": ""},
        ],
    },
    {
        "id": 10,
        "name": "瘟疫村庄",
        "description": "你路过一个正在闹瘟疫的村庄。",
        "options": [
            {"text": "进村帮助", "success_rate": 0.4, "rewards": {"coins": 50, "exp": 100}, "failure_text": "你不幸染上了瘟疫，元气大伤。"},
            {"text": "绕道而行", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 11,
        "name": "发现宝马",
        "description": "你发现一匹无人看管的宝马。",
        "options": [
            {"text": "试图驯服", "success_rate": 0.3, "rewards": {"exp": 120}, "failure_text": "宝马野性难驯，你被踢伤了。"},
            {"text": "悄悄离开", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 12,
        "name": "酒馆斗殴",
        "description": "酒馆里有人在斗殴，你被卷入其中。",
        "options": [
            {"text": "参与斗殴", "success_rate": 0.6, "rewards": {"coins": 80, "exp": 30}, "failure_text": "你被打得鼻青脸肿。"},
            {"text": "劝架", "success_rate": 0.8, "rewards": {"exp": 20}, "failure_text": "你被误伤了。"},
        ],
    },
    {
        "id": 13,
        "name": "迷路",
        "description": "你在森林里迷路了。",
        "options": [
            {"text": "寻找出路", "success_rate": 0.7, "rewards": {"exp": 25}, "failure_text": "你在森林里转了好几天，筋疲力尽。"},
            {"text": "原地等待", "success_rate": 0.3, "rewards": {"exp": 5}, "failure_text": "你等了很久，没有人来救你。"},
        ],
    },
    {
        "id": 14,
        "name": "山贼巢穴",
        "description": "你发现了山贼的巢穴。",
        "options": [
            {"text": "潜入侦查", "success_rate": 0.5, "rewards": {"coins": 150, "exp": 70}, "failure_text": "你被山贼发现了，差点没命。"},
            {"text": "报告官府", "success_rate": 0.9, "rewards": {"coins": 50, "exp": 20}, "failure_text": "官府不相信你的话。"},
        ],
    },
    {
        "id": 15,
        "name": "干旱的村庄",
        "description": "你路过一个因干旱而缺水的村庄。",
        "options": [
            {"text": "帮助找水", "success_rate": 0.6, "rewards": {"coins": 60, "exp": 50}, "failure_text": "你没能找到水源，村民们很失望。"},
            {"text": "继续赶路", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 16,
        "name": "悬崖上的草药",
        "description": "你发现悬崖上长着一株珍贵的草药。",
        "options": [
            {"text": "冒险采摘", "success_rate": 0.4, "rewards": {"exp": 180}, "failure_text": "你从悬崖上摔了下来，受了重伤。"},
            {"text": "放弃", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 17,
        "name": "被冤枉的囚犯",
        "description": "你遇到一个声称被冤枉的囚犯。",
        "options": [
            {"text": "帮助他", "success_rate": 0.5, "rewards": {"coins": 100, "exp": 60}, "failure_text": "你被官府当成了同伙。"},
            {"text": "不予理会", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 18,
        "name": "废弃的兵营",
        "description": "你发现了一个废弃的兵营。",
        "options": [
            {"text": "搜索兵营", "success_rate": 0.7, "rewards": {"coins": 80, "exp": 30}, "failure_text": "兵营里什么都没有。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 19,
        "name": "神秘的地图",
        "description": "你得到了一张神秘的地图。",
        "options": [
            {"text": "按图索骥", "success_rate": 0.3, "rewards": {"coins": 500, "exp": 200}, "failure_text": "地图是假的，你被骗了。"},
            {"text": "丢弃地图", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 20,
        "name": "逃难的贵族",
        "description": "你遇到一位正在逃难的贵族。",
        "options": [
            {"text": "帮助他", "success_rate": 0.6, "rewards": {"coins": 200, "exp": 80}, "failure_text": "贵族是个骗子，你被他骗走了钱财。"},
            {"text": "视而不见", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 21,
        "name": "比武大会",
        "description": "你路过一个正在举办比武大会的城镇。",
        "options": [
            {"text": "参加比武", "success_rate": 0.4, "rewards": {"coins": 300, "exp": 150}, "failure_text": "你在比武中惨败。"},
            {"text": "观看比武", "success_rate": 1.0, "rewards": {"exp": 20}, "failure_text": ""},
        ],
    },
    {
        "id": 22,
        "name": "被困的商队",
        "description": "一个商队被困在山谷里。",
        "options": [
            {"text": "帮助他们", "success_rate": 0.8, "rewards": {"coins": 150, "exp": 50}, "failure_text": "你没能帮上忙，商队损失惨重。"},
            {"text": "绕道而行", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 23,
        "name": "古老的传说",
        "description": "你听说了一个关于古代英雄的传说。",
        "options": [
            {"text": "探寻真相", "success_rate": 0.3, "rewards": {"exp": 250}, "failure_text": "传说只是个故事，你一无所获。"},
            {"text": "不感兴趣", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 24,
        "name": "饥饿的难民",
        "description": "你遇到一群饥饿的难民。",
        "options": [
            {"text": "分给他们食物", "success_rate": 1.0, "rewards": {"coins": -50, "exp": 30}, "failure_text": ""},
            {"text": "置之不理", "success_rate": 1.0, "rewards": {"coins": 0, "exp": -10}, "failure_text": ""},
        ],
    },
    {
        "id": 25,
        "name": "神秘的遗迹",
        "description": "你发现了一处神秘的遗迹。",
        "options": [
            {"text": "探索遗迹", "success_rate": 0.5, "rewards": {"coins": 250, "exp": 120}, "failure_text": "遗迹里充满了危险，你差点丧命。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"exp": 10}, "failure_text": ""},
        ],
    },
    {
        "id": 26,
        "name": "被追杀的信使",
        "description": "你看到一个信使正在被追杀。",
        "options": [
            {"text": "救下信使", "success_rate": 0.7, "rewards": {"coins": 100, "exp": 70}, "failure_text": "你和信使都被抓住了。"},
            {"text": "躲起来", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 27,
        "name": "荒废的寺庙",
        "description": "你发现了一座荒废的寺庙。",
        "options": [
            {"text": "进入寺庙", "success_rate": 0.6, "rewards": {"coins": 90, "exp": 40}, "failure_text": "寺庙里什么都没有。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 28,
        "name": "受伤的士兵",
        "description": "你遇到一个受伤的士兵。",
        "options": [
            {"text": "救助他", "success_rate": 0.9, "rewards": {"exp": 50}, "failure_text": "士兵伤势过重，没能救活。"},
            {"text": "置之不理", "success_rate": 1.0, "rewards": {"exp": -5}, "failure_text": ""},
        ],
    },
    {
        "id": 29,
        "name": "被污染的水源",
        "description": "你发现一处被污染的水源。",
        "options": [
            {"text": "寻找污染源", "success_rate": 0.5, "rewards": {"exp": 80}, "failure_text": "你没能找到污染源。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 30,
        "name": "神秘的歌声",
        "description": "你听到远处传来神秘的歌声。",
        "options": [
            {"text": "循声而去", "success_rate": 0.4, "rewards": {"exp": 100}, "failure_text": "你被歌声迷惑，迷失了方向。"},
            {"text": "不予理会", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 31,
        "name": "被盗的宝物",
        "description": "一个富商的宝物被盗，他请求你帮忙找回。",
        "options": [
            {"text": "接受委托", "success_rate": 0.6, "rewards": {"coins": 200, "exp": 90}, "failure_text": "你没能找回宝物。"},
            {"text": "拒绝委托", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 32,
        "name": "山洪暴发",
        "description": "你遇到了山洪暴发。",
        "options": [
            {"text": "寻找高地", "success_rate": 0.8, "rewards": {"exp": 30}, "failure_text": "你被洪水冲走了。"},
            {"text": "原地等待", "success_rate": 0.2, "rewards": {"exp": 5}, "failure_text": "你被洪水淹没了。"},
        ],
    },
    {
        "id": 33,
        "name": "神秘的石碑",
        "description": "你发现一块刻有神秘文字的石碑。",
        "options": [
            {"text": "研究石碑", "success_rate": 0.3, "rewards": {"exp": 150}, "failure_text": "你看不懂石碑上的文字。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 34,
        "name": "被围困的村庄",
        "description": "一个村庄被敌军围困。",
        "options": [
            {"text": "帮助村民", "success_rate": 0.5, "rewards": {"coins": 120, "exp": 80}, "failure_text": "你和村民一起被俘虏了。"},
            {"text": "绕道而行", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 35,
        "name": "神秘的商人",
        "description": "一个神秘的商人向你出售一件奇特的物品。",
        "options": [
            {"text": "购买物品", "success_rate": 0.2, "rewards": {"exp": 200}, "failure_text": "你花光了钱，却发现物品毫无用处。"},
            {"text": "不予理会", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 36,
        "name": "被遗弃的婴儿",
        "description": "你发现一个被遗弃的婴儿。",
        "options": [
            {"text": "收养婴儿", "success_rate": 1.0, "rewards": {"exp": 50}, "failure_text": ""},
            {"text": "置之不理", "success_rate": 1.0, "rewards": {"exp": -20}, "failure_text": ""},
        ],
    },
    {
        "id": 37,
        "name": "神秘的洞穴",
        "description": "你发现一个深不见底的洞穴。",
        "options": [
            {"text": "进入洞穴", "success_rate": 0.4, "rewards": {"coins": 300, "exp": 150}, "failure_text": "你在洞穴里迷路了。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"exp": 10}, "failure_text": ""},
        ],
    },
    {
        "id": 38,
        "name": "被追捕的义士",
        "description": "你遇到一位正在被官兵追捕的义士。",
        "options": [
            {"text": "帮助他", "success_rate": 0.6, "rewards": {"coins": 150, "exp": 100}, "failure_text": "你和义士一起被抓住了。"},
            {"text": "躲起来", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 39,
        "name": "神秘的祭坛",
        "description": "你发现一个古老的祭坛。",
        "options": [
            {"text": "举行祭祀", "success_rate": 0.3, "rewards": {"exp": 200}, "failure_text": "什么都没有发生。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"exp": 10}, "failure_text": ""},
        ],
    },
    {
        "id": 40,
        "name": "被困的动物",
        "description": "你发现一只被困在陷阱里的动物。",
        "options": [
            {"text": "解救它", "success_rate": 0.9, "rewards": {"exp": 30}, "failure_text": "你被动物咬伤了。"},
            {"text": "置之不理", "success_rate": 1.0, "rewards": {"exp": -5}, "failure_text": ""},
        ],
    },
    {
        "id": 41,
        "name": "神秘的森林",
        "description": "你进入了一片神秘的森林。",
        "options": [
            {"text": "探索森林", "success_rate": 0.5, "rewards": {"coins": 200, "exp": 100}, "failure_text": "你在森林里迷路了。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"exp": 10}, "failure_text": ""},
        ],
    },
    {
        "id": 42,
        "name": "被抢劫的村庄",
        "description": "你路过一个被抢劫一空的村庄。",
        "options": [
            {"text": "追击劫匪", "success_rate": 0.4, "rewards": {"coins": 250, "exp": 120}, "failure_text": "你不是劫匪的对手。"},
            {"text": "帮助村民", "success_rate": 0.8, "rewards": {"exp": 50}, "failure_text": "你无能为力。"},
        ],
    },
    {
        "id": 43,
        "name": "神秘的古井",
        "description": "你发现一口神秘的古井。",
        "options": [
            {"text": "下井探查", "success_rate": 0.3, "rewards": {"coins": 400, "exp": 180}, "failure_text": "井里什么都没有。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"exp": 10}, "failure_text": ""},
        ],
    },
    {
        "id": 44,
        "name": "被陷害的官员",
        "description": "你遇到一位被陷害的官员。",
        "options": [
            {"text": "帮助他", "success_rate": 0.6, "rewards": {"coins": 180, "exp": 90}, "failure_text": "你被当成了同伙。"},
            {"text": "不予理会", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 45,
        "name": "神秘的废墟",
        "description": "你发现一处神秘的废墟。",
        "options": [
            {"text": "探索废墟", "success_rate": 0.7, "rewards": {"coins": 100, "exp": 50}, "failure_text": "废墟里什么都没有。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"exp": 10}, "failure_text": ""},
        ],
    },
    {
        "id": 46,
        "name": "被围攻的商队",
        "description": "一个商队正在被山贼围攻。",
        "options": [
            {"text": "帮助商队", "success_rate": 0.7, "rewards": {"coins": 150, "exp": 80}, "failure_text": "你和商队一起被打败了。"},
            {"text": "绕道而行", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 47,
        "name": "神秘的宝藏图",
        "description": "你得到了一张神秘的宝藏图。",
        "options": [
            {"text": "寻找宝藏", "success_rate": 0.2, "rewards": {"coins": 1000, "exp": 300}, "failure_text": "宝藏图是假的。"},
            {"text": "丢弃宝藏图", "success_rate": 1.0, "rewards": {"coins": 0, "exp": 0}, "failure_text": ""},
        ],
    },
    {
        "id": 48,
        "name": "被追杀的少女",
        "description": "你看到一个少女正在被追杀。",
        "options": [
            {"text": "救下少女", "success_rate": 0.8, "rewards": {"exp": 100}, "failure_text": "你被追杀者打伤了。"},
            {"text": "躲起来", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
    {
        "id": 49,
        "name": "神秘的祭祀仪式",
        "description": "你看到一群人在举行神秘的祭祀仪式。",
        "options": [
            {"text": "加入仪式", "success_rate": 0.3, "rewards": {"exp": 200}, "failure_text": "你被当成了祭品。"},
            {"text": "悄悄离开", "success_rate": 1.0, "rewards": {"exp": 10}, "failure_text": ""},
        ],
    },
    {
        "id": 50,
        "name": "被遗弃的宝箱",
        "description": "你发现一个被遗弃的宝箱。",
        "options": [
            {"text": "打开宝箱", "success_rate": 0.6, "rewards": {"coins": 200, "exp": 50}, "failure_text": "宝箱是空的。"},
            {"text": "离开", "success_rate": 1.0, "rewards": {"exp": 5}, "failure_text": ""},
        ],
    },
]
