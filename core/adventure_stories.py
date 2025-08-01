# -*- coding: utf-8 -*-
# @Time    : 2025/07/31
# @Author  : Cline
# @File    : adventure_stories.py
# @Software: AstrBot
# @Description: 
# 定义模块化、可随机组合的冒险故事组件。
#
# 设计思路:
# 1. 故事被拆分为三个核心模块: 开场(OPENINGS), 事件(EVENTS), 和结局/后续(RESOLUTIONS)。
# 2. 每个模块包含多个独立的条目，通过 "tags" 进行分类关联。
# 3. 冒险生成器可以按以下流程工作:
#    a. 随机选择一个 "OPENING"。
#    b. 根据 "OPENING" 的 "tags"，筛选并随机选择一个匹配的 "EVENT"。
#    c. "EVENT" 中的玩家选项(options)会指向 "RESOLUTIONS" 中的一个具体 "next_stage"。
#    d. "RESOLUTION" 条目可能是最终结局 (type: "final")，也可能引出新的选择 (type: "choice")，
#       形成一个简单的故事链。
# 4. 这种结构便于未来不断扩充，只需向对应的列表中添加新的模块即可。
#
# 注意: 需要修改游戏核心逻辑中的故事生成函数，以适配此新数据结构。
#
# --- 故事模板变量 ---
# 你可以使用以下变量来丰富故事描述，生成时会自动替换：
# {player_name}: 玩家名
# {random_general_name}: 随机生成一个武将名
# {random_city_name}: 随机生成一个城市名
# {random_item_name}: 随机生成一个物品名
# {random_amount}: 随机生成一个金额
#

# --- 故事组件模块 ---

# 1. 开场模块 (Opening)
# 定义故事发生的地点和基本情景
OPENINGS = [
    {
        "id": "village_distress",
        "tags": ["village", "conflict", "social"],
        "template": "你行至一个村庄，发现这里民不聊生，似乎遭了灾祸。",
    },
    {
        "id": "mountain_path",
        "tags": ["wild", "encounter", "travel"],
        "template": "你正走在一条僻静的山路上，四周寂静无人。",
    },
    {
        "id": "city_gate",
        "tags": ["city", "social", "conflict"],
        "template": "你来到一座城池的门前，守城的官兵正在盘查过往行人。",
    },
    {
        "id": "roadside_tavern",
        "tags": ["social", "rest", "information"],
        "template": "天色已晚，你走进路边的一家酒馆歇脚，里面三教九流，好不热闹。",
    },
    {
        "id": "ancient_ruins",
        "tags": ["wild", "exploration", "mystery"],
        "template": "你在山林深处偶然发现了一片古老的废墟，断壁残垣间似乎隐藏着什么秘密。",
    },
    {
        "id": "river_ferry",
        "tags": ["social", "travel", "encounter"],
        "template": "你来到渡口，准备乘船过河。船上已经有几位乘客，看起来身份各异。",
    },
    {
        "id": "busy_marketplace",
        "tags": ["city", "social", "information"],
        "template": "你穿行在熙熙攘攘的市集中，小贩的叫卖声和路人的谈笑声不绝于耳。",
    },
    {
        "id": "military_camp",
        "tags": ["military", "conflict", "social"],
        "template": "你途经一座军营，士兵们正在操练，喊杀声震天。",
    },
    {
        "id": "dense_forest",
        "tags": ["wild", "exploration", "ambush"],
        "template": "你为了抄近路，走进了一片茂密的森林，林中光线昏暗，气氛有些诡异。",
    },
    {
        "id": "farmland",
        "tags": ["village", "social", "rest"],
        "template": "你走在一片广袤的农田间，田里的农夫正在辛勤劳作。",
    },
    {
        "id": "taoist_temple",
        "tags": ["wild", "mystery", "social", "rest"],
        "template": "你攀上一座高山，山顶云雾缭绕处有一座古朴的道观。你决定进去歇歇脚。",
    },
    {
        "id": "famous_battlefield",
        "tags": ["wild", "exploration", "mystery", "military"],
        "template": "你来到了官渡古战场，空气中似乎还弥漫着当年的肃杀之气。",
    },
    {
        "id": "luxurious_manor",
        "tags": ["city", "social", "information"],
        "template": "你受邀来到当地一位豪绅的府邸赴宴，府内雕梁画栋，奢华无比。",
    },
    {
        "id": "refugee_camp",
        "tags": ["village", "conflict", "social"],
        "template": "因战乱，你混在逃难的流民队伍中，周围尽是哀嚎与绝望。",
    },
    {
        "id": "hermit_hut",
        "tags": ["wild", "social", "information", "mystery"],
        "template": "你在深山中寻访名士，终于找到了一位隐士的茅庐。",
    },
    {
        "id": "flooded_village",
        "tags": ["village", "conflict", "disaster"],
        "template": "连日暴雨，河水暴涨，你路过的一个村庄被洪水围困，村民们在水中挣扎。",
    },
    {
        "id": "plague_ridden_town",
        "tags": ["city", "conflict", "disaster"],
        "template": "你进入一座城镇，发现街上行人稀少，许多房屋门口都挂着隔离的标志，空气中弥漫着一股草药和死亡的气息。这里似乎爆发了瘟疫。",
    },
    {
        "id": "hunting_ground",
        "tags": ["wild", "exploration", "encounter"],
        "template": "你进入了一片皇家猎场，据说这里有许多珍禽异兽，但也可能遇到巡逻的禁军。",
    },
    {
        "id": "abandoned_mine",
        "tags": ["wild", "exploration", "mystery"],
        "template": "你在山脚下发现一个废弃的矿洞，洞口黑漆漆的，不时有阴风吹出。",
    },
    {
        "id": "yellow_turban_camp",
        "tags": ["military", "conflict", "yellow_turban"],
        "template": "你潜入了一个黄巾军的营地，周围都是巡逻的士兵，你需要小心行事。",
    },
    {
        "id": "militia_muster_point",
        "tags": ["village", "social", "military"],
        "template": "你来到了一个乡勇集结点，许多热血青年正在响应号召，准备讨伐黄巾军。",
    },
]

# 2. 事件模块 (Event)
# 定义具体发生的事件和玩家的初步选择
# 每个事件通过 tags 关联到适用的开场
EVENTS = [
    # --- 新增低等级事件 ---
    {
        "id": "encounter_yellow_turban_scout",
        "tags": ["yellow_turban", "wild"],
        "template": "你发现了一个鬼鬼祟祟的黄巾斥候，他似乎正在侦察地形。",
        "options": [
            {"text": "上前消灭他。", "next_stage": "kill_scout_success"},
            {"text": "悄悄尾随，找到他们的据点。", "next_stage": "follow_scout_success"},
        ]
    },
    {
        "id": "rescue_trapped_villagers",
        "tags": ["yellow_turban", "village"],
        "template": "一股黄巾乱兵将村民围困在村庄的祠堂里，情况危急。",
        "options": [
            {"text": "声东击西，引开部分敌人。", "next_stage": "distract_enemy_success"},
            {"text": "正面突围，强行救人。", "next_stage": "force_rescue_success"},
        ]
    },
    # --- 原有事件 ---
    {
        "id": "yellow_turban_plunder",
        "tags": ["village", "conflict"],
        "template": "突然，一群头裹黄巾的乱兵冲入村庄开始劫掠。一位老者跪倒在你面前，哭喊着：\"英雄，救救我们吧！\"",
        "options": [
            {"text": "挺身而出，击退乱兵。", "next_stage": "y_turban_fight_success"},
            {"text": "悄悄绕开，避免麻烦。", "next_stage": "y_turban_escape_encounter"},
        ]
    },
    {
        "id": "mysterious_merchant",
        "tags": ["encounter", "social", "city", "wild"],
        "template": "一个神秘的西域商人叫住了你，他压低声音说：\"这位朋友，我看你骨骼惊奇，这里有稀世珍宝，要不要看看？\"",
        "options": [
            {"text": "上前看看他卖什么。", "next_stage": "merchant_show_goods"},
            {"text": "觉得可疑，直接走开。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "wounded_soldier",
        "tags": ["wild", "conflict"],
        "template": "你发现路边躺着一个身受重伤的官兵，他气息微弱，似乎需要帮助。",
        "options": [
            {"text": "上前救助他。", "next_stage": "help_soldier_success"},
            {"text": "置之不理，继续赶路。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "tavern_brawl",
        "tags": ["social", "rest", "information"],
        "template": "酒馆里，两个醉汉因为一点口角争执起来，眼看就要大打出手。",
        "options": [
            {"text": "上前劝架。", "next_stage": "stop_brawl_success"},
            {"text": "坐山观虎斗。", "next_stage": "watch_brawl_outcome"},
        ]
    },
    {
        "id": "ruins_treasure_map",
        "tags": ["exploration", "wild", "mystery"],
        "template": "你在废墟的一块石板下，发现了一个破旧的铁盒。打开一看，里面是一张残缺的地图。",
        "options": [
            {"text": "收下地图，日后研究。", "next_stage": "end_ruins_map_get"},
            {"text": "觉得不祥，放回原处。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "ferry_scholar_talk",
        "tags": ["social", "travel"],
        "template": "船上，一位儒生模样的中年人主动与你攀谈，他似乎对天下大势有独到的见解。",
        "options": [
            {"text": "与他高谈阔论。", "next_stage": "scholar_debate_success"},
            {"text": "敷衍几句，闭目养神。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "marketplace_thief",
        "tags": ["city", "social"],
        "template": "你看到一个小孩偷了包子铺的包子就跑，老板在后面气得直跳脚。",
        "options": [
            {"text": "抓住小孩，送还给老板。", "next_stage": "thief_capture_success"},
            {"text": "假装没看见。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "city_guard_trouble",
        "tags": ["city", "social", "conflict"],
        "template": "守城官兵拦住了你，声称你形迹可疑，需要缴纳一笔“保证金”才能进城。",
        "options": [
            {"text": "缴纳“保证金”。", "next_stage": "end_guard_bribe"},
            {"text": "理论一番，拒绝缴纳。", "next_stage": "guard_argue_fail"},
        ]
    },
    # --- 新增事件 ---
    {
        "id": "camp_recruitment",
        "tags": ["military", "social"],
        "template": "军营门口贴着招兵买马的告示，一位军官见你体格健壮，便上前询问你是否有意参军。",
        "options": [
            {"text": "欣然应允，报效国家。", "next_stage": "end_join_army_direct"},
            {"text": "志不在此，婉言谢绝。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "forest_ambush",
        "tags": ["wild", "ambush", "conflict"],
        "template": "你正走着，突然从林中跳出几个山贼，手持兵刃，将你团团围住。“此树是我栽，此路是我开！”",
        "options": [
            {"text": "交出钱财保平安。", "next_stage": "end_bandit_robbery"},
            {"text": "奋力一搏，杀出重围。", "next_stage": "bandit_fight_outcome"},
        ]
    },
    {
        "id": "farmer_request",
        "tags": ["village", "social"],
        "template": "一位老农焦急地向你求助，说他家的耕牛挣脱了缰绳，跑进了附近的山林，希望你能帮忙找回来。",
        "options": [
            {"text": "答应帮忙寻找耕牛。", "next_stage": "find_ox_success"},
            {"text": "表示自己还有要事，爱莫能助。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "tavern_storyteller",
        "tags": ["information", "social", "rest"],
        "template": "酒馆的角落里，一位说书人正在讲述当今英雄豪杰的故事，周围聚满了听客。你听到了关于一位著名将领的传闻。",
        "options": [
            {"text": "打赏说书人，询问更多细节。", "next_stage": "storyteller_ask_detail"},
            {"text": "默默听完，不作表示。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "ruins_ghostly_sound",
        "tags": ["mystery", "exploration"],
        "template": "夜幕降临，废墟中传来若有若无的哭泣声，让人毛骨悚然。",
        "options": [
            {"text": "壮着胆子，循声探去。", "next_stage": "ruins_ghost_investigate"},
            {"text": "心生畏惧，赶紧离开。", "next_stage": "end_ruins_flee"},
        ]
    },
    {
        "id": "lost_child",
        "tags": ["city", "village", "social"],
        "template": "你在路边发现一个与父母走散的孩童，他正无助地哭泣。",
        "options": [
            {"text": "上前安抚，并帮他寻找父母。", "next_stage": "help_child_find_parent"},
            {"text": "视而不见，继续赶路。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "taoist_divination",
        "tags": ["mystery", "social", "rest"],
        "template": "观中一位道长见你仙风道骨，主动提出要为你卜上一卦，窥探天机。",
        "options": [
            {"text": "欣然同意，请道长赐教。", "next_stage": "divination_good_omen"},
            {"text": "半信半疑，婉言谢绝。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "wanted_poster",
        "tags": ["city", "information", "conflict"],
        "template": "你在城中布告栏上看到一张悬赏令，官府正在悬赏捉拿附近山头的悍匪头目“独眼龙”。",
        "options": [
            {"text": "揭下悬赏令，决定为民除害。", "next_stage": "accept_bounty_quest"},
            {"text": "觉得太过危险，不愿插手。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    # --- 战场遗迹事件 ---
    {
        "id": "find_relic",
        "tags": ["military", "exploration"],
        "template": "你在战场上搜寻，希望能找到一些遗物。突然，你的脚踢到了一个坚硬的物体。",
        "options": [
            {"text": "挖出来看看。", "next_stage": "relic_weapon_found"},
            {"text": "不感兴趣，继续前行。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "ghostly_encounter",
        "tags": ["military", "mystery", "exploration"],
        "template": "夜幕降临，战场上阴风阵阵，你似乎听到了千军万马的嘶吼声。",
        "options": [
            {"text": "壮着胆子前去探查。", "next_stage": "ghost_general_challenge"},
            {"text": "心生畏惧，赶紧离开。", "next_stage": "end_ruins_flee"},
        ]
    },
    # --- 豪绅府邸事件 ---
    {
        "id": "poetry_contest",
        "tags": ["city", "social", "information"],
        "template": "宴会上，主人提议以诗助兴，众人纷纷叫好，胜者据说有重赏。",
        "options": [
            {"text": "一展才华，欣然参加。", "next_stage": "poetry_contest_win"},
            {"text": "不善此道，婉言谢绝。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    {
        "id": "assassination_plot",
        "tags": ["city", "social", "conflict"],
        "template": "席间，你无意中听到邻座两人在低声密谋，似乎想对主人不利。",
        "options": [
            {"text": "向主人告密。", "next_stage": "plot_foiled_reward"},
            {"text": "假装没听到。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    # --- 流民营地事件 ---
    {
        "id": "food_shortage",
        "tags": ["village", "social", "conflict"],
        "template": "营地里的粮食快要见底了，一位母亲抱着她饥饿的孩子向你乞求食物。",
        "options": [
            {"text": "分出自己的口粮。", "next_stage": "share_food_reward"},
            {"text": "表示自己也无能为力。", "next_stage": "refuse_food_consequence"},
        ]
    },
    # --- 隐士茅庐事件 ---
    {
        "id": "hermit_test",
        "tags": ["wild", "social", "mystery"],
        "template": "隐士见你前来，并不直接与你交谈，而是给你出了一道难题，考验你的能力。",
        "options": [
            {"text": "接受智慧考验。", "next_stage": "wisdom_test_pass"},
            {"text": "接受武力考验。", "next_stage": "strength_test_pass"},
        ]
    },
    # --- 洪水围村事件 ---
    {
        "id": "rescue_villagers",
        "tags": ["village", "disaster"],
        "template": "洪水湍急，许多村民被困在屋顶上，一个孩子脚滑即将落水。情况万分危急！",
        "options": [
            {"text": "奋不顾身，下水救人。", "next_stage": "rescue_child_success"},
            {"text": "寻找船只或木筏救人。", "next_stage": "find_raft_rescue"},
        ]
    },
    # --- 瘟疫城镇事件 ---
    {
        "id": "plague_doctor_request",
        "tags": ["city", "disaster"],
        "template": "一位戴着鸟嘴面具的医者拦住了你，他焦急地说药材已经用完，急需有人能去城外的山上采集一些特定的草药。",
        "options": [
            {"text": "冒着风险，出城采药。", "next_stage": "gather_herbs_success"},
            {"text": "担心被感染，拒绝请求。", "next_stage": "refuse_gather_herbs"},
        ]
    },
    # --- 皇家猎场事件 ---
    {
        "id": "hunting_rare_beast",
        "tags": ["wild", "encounter"],
        "template": "你发现了一只毛色雪白的鹿，它似乎是传说中的祥瑞之兽。不远处，一队禁军也发现了它，正张弓搭箭。",
        "options": [
            {"text": "抢先射杀白鹿。", "next_stage": "kill_white_deer"},
            {"text": "惊扰白鹿，让它逃走。", "next_stage": "help_white_deer_escape"},
            {"text": "与禁军交涉。", "next_stage": "negotiate_with_guards"},
        ]
    },
    # --- 废弃矿洞事件 ---
    {
        "id": "mine_investigation",
        "tags": ["wild", "exploration", "mystery"],
        "template": "你点燃火把，走进矿洞。洞壁上湿漉漉的，还能看到一些废弃的采矿工具。你似乎听到了洞穴深处传来了奇怪的声响。",
        "options": [
            {"text": "继续深入探索。", "next_stage": "mine_deep_explore"},
            {"text": "觉得不对劲，立刻退出。", "next_stage": "mine_exit_safely"},
        ]
    },
    # --- 新增：失窃的传家宝任务线 ---
    {
        "id": "eavesdrop_plot",
        "tags": ["social", "information", "rest"],
        "template": "你找了个角落坐下，点了一壶酒。邻桌两个商贾模样的人正在低声交谈，你无意中听到他们提及‘传家宝’、‘城外废塔’和‘今晚交易’等字眼。",
        "options": [
            {"text": "悄悄听下去，获取更多信息。", "next_stage": "plot_details"},
            {"text": "事不关己，不去理会。", "next_stage": "generic_end_nothing_happened"},
        ]
    },
    # --- 新增：剿灭黄巾据点任务线 ---
    {
        "id": "yellow_turban_stronghold_clue",
        "tags": ["yellow_turban", "wild", "conflict", "military"],
        "template": "你击溃了一小队黄巾巡逻兵，在他们的首领身上，你发现了一封密信，似乎指向了附近山中的一个秘密据点。",
        "options": [
            {"text": "查看密信，了解详情。", "next_stage": "yt_stronghold_investigate_choice"},
            {"text": "不感兴趣，将信件丢弃。", "next_stage": "generic_end_nothing_happened"},
        ]
    }
]

# 3. 结局/后续阶段模块 (Resolution)
# 3. 结局/后续阶段模块 (Resolution)
# 定义事件发展的结果，可以是最终结局，也可以是新的选择
RESOLUTIONS = {
    # --- 新增：剿灭黄巾据点任务线 ---
    "yt_stronghold_investigate_choice": {
        "type": "choice",
        "template": "密信揭示了黄巾军据点的具体位置和兵力部署。这是一个立功的好机会，你决定：",
        "options": [
            {"text": "单枪匹马，深入侦查。", "next_stage": "yt_stronghold_solo_choice"},
            {"text": "报告官府，寻求支援。", "next_stage": "yt_stronghold_report_choice"},
        ]
    },
    "yt_stronghold_solo_choice": {
        "type": "choice",
        "template": "你决定独自行动。来到据点外，你发现营寨防守严密。你要如何行动？",
        "options": [
            {"text": "趁夜色潜入，刺探情报。", "next_stage": "yt_stronghold_sneak_success"},
            {"text": "制造混乱，正面强攻。", "next_stage": "yt_stronghold_assault_fail"},
        ]
    },
    "yt_stronghold_report_choice": {
        "type": "choice",
        "template": "你将情报呈报给最近的县城。县尉大喜，但对你的能力表示怀疑，询问你希望如何参与。",
        "options": [
            {"text": "担当向导，与官兵同去。", "next_stage": "yt_stronghold_guide_success"},
            {"text": "仅提供情报，坐等奖赏。", "next_stage": "yt_stronghold_wait_reward"},
        ]
    },
    "yt_stronghold_sneak_success": {
        "type": "final",
        "template": "你凭借高超的技巧成功潜入据点，摸清了敌人的粮仓位置和首领营帐。你悄然纵火，据点顿时大乱，你趁机安全撤离。你的智谋和胆识获得了极高的评价。",
        "rewards": {"reputation": 15, "exp": 80, "items": ["黄巾军详细部署图"]},
        "end": True
    },
    "yt_stronghold_assault_fail": {
        "type": "final",
        "template": "你的鲁莽让你陷入了重围。虽然你奋力拼杀，最终得以逃脱，但也身受重伤，损失惨重。",
        "rewards": {"exp": 20, "health": -30, "coins": -50},
        "end": True
    },
    "yt_stronghold_guide_success": {
        "type": "final",
        "template": "在你的带领下，官军成功突袭了黄巾据点，大获全胜。作为首功之臣，你获得了丰厚的金钱和官职奖赏。",
        "rewards": {"coins": 400, "reputation": 10, "exp": 60, "items": ["县尉的推荐信"]},
        "end": True
    },
    "yt_stronghold_wait_reward": {
        "type": "final",
        "template": "官军根据你的情报成功剿匪，但把大部分功劳归于自己。你只获得了少量奖赏，心中颇为不平。",
        "rewards": {"coins": 100, "reputation": 2, "exp": 20},
        "end": True
    },

    # --- 新增低等级事件结局 ---
    "kill_scout_success": {
        "type": "final",
        "template": "你干净利落地解决了黄巾斥候，从他身上搜到了一些铜钱和一张简易的地图。",
        "rewards": {"coins": 15, "exp": 10, "items": ["黄巾军的简易地图"]},
        "end": True
    },
    "follow_scout_success": {
        "type": "final",
        "template": "你小心翼翼地尾随斥候，成功找到了黄巾军的一个小型据点。你将此情报报告给了附近的官军。",
        "rewards": {"reputation": 2, "exp": 15},
        "end": True
    },
    "distract_enemy_success": {
        "type": "final",
        "template": "你成功引开了部分黄巾军，村民趁机从祠堂逃脱。你的智谋为你赢得了声望。",
        "rewards": {"reputation": 3, "exp": 20},
        "end": True
    },
    "force_rescue_success": {
        "type": "final",
        "template": "你如猛虎下山般冲入敌阵，黄巾军被你的勇武所震慑，一番激战后四散而逃。你成功救出了村民。",
        "rewards": {"coins": 30, "exp": 25},
        "end": True
    },

    # --- 黄巾之乱分支 ---
    "y_turban_fight_success": {
        "type": "choice", 
        "template": "你凭借一身武艺成功击退了黄巾军，村民们对你感激不尽，村长颤巍巍地拿出一些钱币：\"英雄，这是我们的一点心意！\"",
        "options": [
            {"text": "接受谢礼。", "next_stage": "end_accept_reward"},
            {"text": "拒绝谢礼。", "next_stage": "end_refuse_reward"},
        ]
    },
    "y_turban_escape_encounter": {
        "type": "choice",
        "template": "你选择绕道而行，但没走多远就遇到了一小股溃败的官兵，他们邀请你一同追击黄巾军主力，并承诺事成之后必有重赏。",
        "options": [
            {"text": "同意加入。", "next_stage": "end_join_army_success"},
            {"text": "婉言谢绝。", "next_stage": "end_join_army_fail"},
        ]
    },

    # --- 神秘商人分支 ---
    "merchant_show_goods": {
        "type": "choice",
        "template": "商人向你展示了两件物品：一本看似平平无奇的旧书，和一个闪闪发光的宝珠。他让你选一个买下。",
        "options": [
            {"text": "买下旧书 (50铜钱)", "next_stage": "end_merchant_book"},
            {"text": "买下宝珠 (100铜钱)", "next_stage": "end_merchant_pearl"},
        ]
    },

    # --- 救助士兵分支 ---
    "help_soldier_success": {
        "type": "final", 
        "template": "你为士兵包扎了伤口，他感激地告诉你一个秘密藏宝地点作为报答。",
        "rewards": {"coins": 100, "items": ["藏宝图碎片"]},
        "end": True
    },

    # --- 酒馆斗殴分支 ---
    "stop_brawl_success": {
        "type": "final",
        "template": "在你的调解下，双方握手言和。酒馆老板为了感谢你免了你的酒钱，还额外送了你一些盘缠。",
        "rewards": {"coins": 30, "exp": 5},
        "end": True
    },
    "watch_brawl_outcome": {
        "type": "final",
        "template": "两个醉汉打得不可开交，一个失手将钱袋丢了出来，正好滚到你的脚边。你悄悄捡了起来。",
        "rewards": {"coins": 20, "exp": -2}, 
        "end": True
    },

    # --- 废墟探索分支 ---
    "end_ruins_map_get": {
        "type": "final",
        "template": "你收好了这张神秘的地图，虽然现在还看懂，但直觉告诉你它将来必有大用。",
        "rewards": {"items": ["残破的地图"], "exp": 15},
        "end": True
    },

    # --- 渡口交谈分支 ---
    "scholar_debate_success": {
        "type": "final",
        "template": "你与儒生相谈甚欢，他对你的见识大加赞赏，并赠予你一本他亲手注解的《论语》。",
        "rewards": {"items": ["《论语》注本"], "exp": 30},
        "end": True
    },

    # --- 市集小偷分支 ---
    "thief_capture_success": {
        "type": "choice",
        "template": "你抓住了偷包子的小孩，他看起来很瘦弱，眼眶里含着泪水。老板赶了过来，气冲冲地说要报官。",
        "options": [
            {"text": "替小孩求情，并帮他付了包子钱。", "next_stage": "end_thief_forgive"},
            {"text": "让老板按规矩办。", "next_stage": "end_thief_punish"},
        ]
    },
    "end_thief_forgive": {
        "type": "final",
        "template": "老板看在你的面子上，原谅了小孩。你帮他付了10铜钱，你的善举让你感到内心充实。",
        "rewards": {"coins": -10, "exp": 10, "reputation": 2},
        "end": True
    },
    "end_thief_punish": {
        "type": "final",
        "template": "小孩被老板扭送去了官府，市集恢复了秩序，但你总觉得心里有些不是滋味。",
        "rewards": {"exp": -5},
        "end": True
    },

    # --- 城门刁难分支 ---
    "end_guard_bribe": {
        "type": "final",
        "template": "你忍气吞声地交了50铜钱，官兵这才放你进城。你暗下决心，以后定要出人头地。",
        "rewards": {"coins": -50},
        "end": True
    },
    "guard_argue_fail": {
        "type": "final",
        "template": "你试图与官兵理论，结果被他们以“顶撞公门”为由，强行索要了更多钱财。",
        "rewards": {"coins": -80, "exp": -5},
        "end": True
    },

    # --- 新增分支 ---
    "end_join_army_direct": {
        "type": "final",
        "template": "你成功加入了军队，开启了你的军旅生涯。你获得了新兵装备和一些安家费。",
        "rewards": {"coins": 50, "items": ["新兵套装"], "exp": 20},
        "end": True
    },
    "end_bandit_robbery": {
        "type": "final",
        "template": "你不想惹麻烦，交出了身上一半的铜钱。山贼拿到钱后，便放你离开了。",
        "rewards": {"coins": -100}, # 假设玩家有200
        "end": True
    },
    "bandit_fight_outcome": {
        "type": "final",
        "template": "一场恶战后，你成功击退了山贼，还在他们身上找到了一些不义之财。",
        "rewards": {"coins": 80, "exp": 30},
        "end": True
    },
    "find_ox_success": {
        "type": "final",
        "template": "你在山林里找到了受惊的耕牛，并将其带回给老农。老农感激不尽，送给你一些自家种的粮食和一点心意。",
        "rewards": {"coins": 20, "items": ["干粮"], "reputation": 1},
        "end": True
    },
    "storyteller_ask_detail": {
        "type": "final",
        "template": "你打赏了10个铜钱，说书人眉飞色舞地向你透露了那位将领正在招贤纳士的传闻，并告知了具体地点。",
        "rewards": {"coins": -10, "exp": 5, "items": ["重要情报"]},
        "end": True
    },
    "ruins_ghost_investigate": {
        "type": "final",
        "template": "你壮着胆子走近，发现声音来自一个藏在暗处的女子。她是为了躲避战乱才藏身于此，你安抚了她，并给了她一些干粮。",
        "rewards": {"exp": 15, "reputation": 3},
        "end": True
    },
    "end_ruins_flee": {
        "type": "final",
        "template": "你被未知的声音吓住，不敢久留，匆忙离开了这片是非之地。",
        "rewards": {"exp": -3},
        "end": True
    },
    "help_child_find_parent": {
        "type": "final",
        "template": "经过一番周折，你终于帮孩子找到了他的父母。孩子的父亲是城里的一位富商，他重重地感谢了你。",
        "rewards": {"coins": 200, "reputation": 5},
        "end": True
    },
    "divination_good_omen": {
        "type": "final",
        "template": "道长为你卜得一上上签，预示你接下来将有贵人相助。你感到信心倍增。",
        "rewards": {"exp": 25, "reputation": 1},
        "end": True
    },
    "accept_bounty_quest": {
        "type": "final",
        "template": "你揭下了悬赏令，并从官府处获得了“独眼龙”出没的线索。一场新的挑战正在等着你。",
        "rewards": {"items": ["独眼龙的线索"], "exp": 10},
        "end": True
    },

    # --- 通用结局 ---
    "generic_end_nothing_happened": {
        "type": "final",
        "template": "你没有多管闲事，继续了自己的旅程，什么也没有发生。",
        "rewards": {},
        "end": True
    },
    "end_accept_reward": {
        "type": "final",
        "template": "你收下村民的谢礼，在他们的欢送声中离开了村庄。",
        "rewards": {"coins": 50, "exp": 10},
        "end": True
    },
    "end_refuse_reward": {
        "type": "final",
        "template": "你的义举赢得了村民的尊敬，声望得到了提升。",
        "rewards": {"exp": 20, "reputation": 5},
        "end": True
    },
    "end_join_army_success": {
        "type": "final",
        "template": "你加入了官兵的行列，凭借你的勇武，成功击溃了黄巾主力，获得了丰厚的奖赏。",
        "rewards": {"coins": 150, "exp": 50},
        "end": True
    },
    "end_join_army_fail": {
        "type": "final",
        "template": "你因胆怯错失了良机，还被官兵嘲笑了一番，并被索要了一些“辛苦费”。",
        "rewards": {"coins": -10},
        "end": True
    },
    "end_merchant_book": {
        "type": "final",
        "template": "你花50铜钱买下了旧书，翻开一看，竟是一本失传的兵法！你从中领悟良多，经验大增。",
        "rewards": {"coins": -50, "exp": 50},
        "end": True
    },
    "end_merchant_pearl": {
        "type": "final",
        "template": "你花100铜钱买下了宝珠，拿在手里仔细一看，发现只是个玻璃球。你上当了！",
        "rewards": {"coins": -100},
        "end": True
    },

    # --- 新增结局 ---
    "relic_weapon_found": {
        "type": "final",
        "template": "你挖开泥土，发现是一柄锈迹斑斑的古剑。擦去锈迹后，仍能感到其不凡的锋芒。",
        "rewards": {"items": ["生锈的古剑"], "exp": 20},
        "end": True
    },
    "ghost_general_challenge": {
        "type": "final",
        "template": "一个半透明的古代将军之魂出现在你面前，他赞许你的勇气，并提出要考验你的武艺。一番切磋后，他将一套枪法传授给了你。",
        "rewards": {"exp": 50, "items": ["初级枪法心得"]},
        "end": True
    },
    "poetry_contest_win": {
        "type": "final",
        "template": "你才思泉涌，吟诵出一首佳作，满堂喝彩。主人大喜，赏赐你百金。",
        "rewards": {"coins": 100, "reputation": 3, "exp": 15},
        "end": True
    },
    "plot_foiled_reward": {
        "type": "final",
        "template": "你悄悄将阴谋告知主人，主人早有防备，将刺客一网打尽。为感谢你，主人赠予你一匹良驹。",
        "rewards": {"items": ["良驹"], "reputation": 5},
        "end": True
    },
    "share_food_reward": {
        "type": "final",
        "template": "你将不多的干粮分给了母子，母亲感激地告诉你，她的丈夫是某位将军的亲兵，并给了你一个信物，让你有困难时可以去找那位将军。",
        "rewards": {"reputation": 5, "items": ["将军的信物"]},
        "end": True
    },
    "refuse_food_consequence": {
        "type": "final",
        "template": "你拒绝了她们的乞求，周围的流民向你投来鄙夷的目光。你感到一阵孤立。",
        "rewards": {"reputation": -3},
        "end": True
    },
    "wisdom_test_pass": {
        "type": "final",
        "template": "你成功解答了隐士的难题，他抚须而笑，将一本珍藏的医书赠予了你。",
        "rewards": {"items": ["青囊书残卷"], "exp": 40},
        "end": True
    },
    "strength_test_pass": {
        "type": "final",
        "template": "你展示了过人的武勇，成功完成了考验。隐士点点头，送给你一瓶能强身健体的丹药。",
        "rewards": {"items": ["淬体丹"], "exp": 20},
        "end": True
    },

    # --- 洪水围村分支 ---
    "rescue_child_success": {
        "type": "final",
        "template": "你冒着生命危险跳入洪水中，成功救起了孩子。村民们把你当做英雄，村长将传家宝“避水珠”赠予了你。",
        "rewards": {"items": ["避水珠"], "reputation": 10, "exp": 30},
        "end": True
    },
    "find_raft_rescue": {
        "type": "choice",
        "template": "你急中生智，用几根木头和绳子扎了一个简易的木筏，成功救下了几个村民。但洪水越来越大，木筏似乎快散架了。",
        "options": [
            {"text": "先将已救村民送至安全地带。", "next_stage": "raft_safe_return"},
            {"text": "冒险继续救更多的人。", "next_stage": "raft_risk_continue"},
        ]
    },
    "raft_safe_return": {
        "type": "final",
        "template": "你理智地选择将村民送到安全地带。虽然没能救下所有人，但你的义举还是为你赢得了声望。",
        "rewards": {"reputation": 5, "exp": 20},
        "end": True
    },
    "raft_risk_continue": {
        "type": "final",
        "template": "你的贪心导致木筏在洪水中解体，你和村民们都被卷入急流。一番挣扎后，你侥幸活了下来，但损失惨重。",
        "rewards": {"coins": -50, "exp": -10, "reputation": -2},
        "end": True
    },

    # --- 瘟疫城镇分支 ---
    "gather_herbs_success": {
        "type": "final",
        "template": "你成功采集到了草药，医者用它制作解药，控制了镇上的疫情。为了感谢你，他将一本珍贵的医书《伤寒杂病论》赠予了你。",
        "rewards": {"items": ["《伤寒杂病论》"], "reputation": 8, "exp": 40},
        "end": True
    },
    "refuse_gather_herbs": {
        "type": "final",
        "template": "你因害怕而拒绝了医者的请求。当你准备离开时，却发现城门已经封闭，你被困在了这座瘟疫之城。",
        "rewards": {"reputation": -5, "status": "染病风险"},
        "end": True
    },

    # --- 皇家猎场分支 ---
    "kill_white_deer": {
        "type": "final",
        "template": "你抢在禁军之前射杀了白鹿，但此举激怒了禁军。你被当做盗猎者抓了起来，送入大牢。",
        "rewards": {"reputation": -10, "status": "入狱"},
        "end": True
    },
    "help_white_deer_escape": {
        "type": "final",
        "template": "你制造混乱，白鹿趁机逃入了森林深处。你的善举似乎被某种神秘力量所感知，你感到精力更加充沛了。",
        "rewards": {"exp": 30, "reputation": 3},
        "end": True
    },
    "negotiate_with_guards": {
        "type": "choice",
        "template": "你上前与禁军校尉交涉，声称此鹿乃祥瑞之兆，不应猎杀。校尉对你的说辞将信将疑。",
        "options": [
            {"text": "用你的声望说服他。", "next_stage": "negotiate_reputation_check"},
            {"text": "用金钱贿赂他。", "next_stage": "negotiate_bribe_check"},
        ]
    },
    "negotiate_reputation_check": {
        "type": "final",
        "template": "你晓之以理，动之以情，凭借你的高声望成功说服了校尉。他决定放白鹿一条生路，并对你表示敬佩。",
        "rewards": {"reputation": 5, "exp": 20},
        "end": True
    },
    "negotiate_bribe_check": {
        "type": "final",
        "template": "你悄悄塞给校尉一袋金子({random_amount}铜钱)，他掂了掂分量，满意地笑了，挥手让士兵们放行。",
        "rewards": {"coins": -150, "reputation": -1},
        "end": True
    },

    # --- 废弃矿洞分支 ---
    "mine_deep_explore": {
        "type": "choice",
        "template": "你向深处走去，发现声音来自一群正在秘密开采稀有矿石的矿工。他们看到你后，立刻露出了敌意。",
        "options": [
            {"text": "解释自己只是迷路了。", "next_stage": "mine_explain_leave"},
            {"text": "试图抢夺他们的矿石。", "next_stage": "mine_fight_miners"},
        ]
    },
    "mine_exit_safely": {
        "type": "final",
        "template": "你觉得此地不宜久留，迅速退出了矿洞。虽然一无所获，但也避免了未知的危险。",
        "rewards": {"exp": 5},
        "end": True
    },
    "mine_explain_leave": {
        "type": "final",
        "template": "矿工们半信半疑地警告你不要声张，然后将你赶出了矿洞。",
        "rewards": {"exp": 10},
        "end": True
    },
    "mine_fight_miners": {
        "type": "final",
        "template": "你与矿工们发生激战，虽然你成功击败了他们，但也受了不轻的伤。你从他们身上搜刮到了一些稀有的黑铁矿石。",
        "rewards": {"items": ["黑铁矿石"], "exp": 25, "health": -20},
        "end": True
    },

    # --- 新增：失窃的传家宝任务线 ---
    "plot_details": {
        "type": "choice",
        "template": "你凝神细听，原来是本地富商张员外的传家宝玉佩被盗，盗贼正准备今晚在城外的废塔进行销赃。你知道了此事，心中思量起来。",
        "options": [
            {"text": "决定插手，前往废塔。", "next_stage": "go_to_tower"},
            {"text": "将此事告知官府。", "next_stage": "inform_officials"},
            {"text": "去通知张员外本人。", "next_stage": "inform_zhang"}
        ]
    },
    "go_to_tower": {
        "type": "choice",
        "template": "夜色如墨，你来到城外废塔。塔内果然有几个人影在鬼鬼祟祟地交易。你躲在暗处，看到盗贼拿出了那块晶莹剔透的玉佩。",
        "options": [
            {"text": "直接冲出去，武力夺回玉佩。", "next_stage": "tower_fight"},
            {"text": "制造声响，趁机偷回玉佩。", "next_stage": "tower_sneak"}
        ]
    },
    "tower_fight": {
        "type": "final",
        "template": "你如猛虎下山，冲向盗贼。他们猝不及防，一番打斗后被你尽数制服。你夺回了玉佩，第二天将其归还给了张员外，员外大喜，重赏了你。",
        "rewards": {"coins": 500, "reputation": 10, "exp": 50},
        "end": True
    },
    "tower_sneak": {
        "type": "final",
        "template": "你扔出一块石子，成功吸引了他们的注意。趁他们外出查看之际，你闪身而入，迅速拿走了桌上的玉佩，消失在夜色中。第二天你将玉佩归还张员外，他虽不知过程，但仍对你感激不尽。",
        "rewards": {"coins": 300, "reputation": 5, "exp": 60},
        "end": True
    },
    "inform_officials": {
        "type": "choice",
        "template": "你来到衙门，将听到的消息告知了当值的捕头。捕头听后，将信将疑地看着你。",
        "options": [
            {"text": "拿出你的侠义之气说服他。", "next_stage": "officials_persuade"},
            {"text": "表示愿意带路，一同前往。", "next_stage": "officials_lead"}
        ]
    },
    "officials_persuade": {
        "type": "final",
        "template": "你的言辞恳切，一身正气，捕头最终相信了你，立刻点齐人马前往废塔，成功将盗贼一网打尽。事后，你因举报有功，获得了官府的奖赏。",
        "rewards": {"coins": 200, "reputation": 8, "exp": 30},
        "end": True
    },
    "officials_lead": {
        "type": "final",
        "template": "你带领官兵埋伏在废塔周围，待盗贼交易时，一声令下，官兵们一拥而上，将人赃并获。你因协助办案，获得了丰厚的奖赏。",
        "rewards": {"coins": 250, "reputation": 10, "exp": 40},
        "end": True
    },
    "inform_zhang": {
        "type": "choice",
        "template": "你找到张员外的府邸，将事情原委告知。张员外听后大惊，随即请求你帮助他夺回玉佩，并许诺重金酬谢。",
        "options": [
            {"text": "答应请求，并要求他派家丁协助。", "next_stage": "zhang_with_help"},
            {"text": "答应请求，但决定单独行动。", "next_stage": "go_to_tower"}
        ]
    },
    "zhang_with_help": {
        "type": "final",
        "template": "你带着张员外府上的几名精壮家丁一同前往废塔。人多势众，你们很轻松地就制服了盗贼，夺回了玉佩。张员外兑现承诺，给了你一大笔酬金。",
        "rewards": {"coins": 600, "reputation": 5, "exp": 40},
        "end": True
    }
}
