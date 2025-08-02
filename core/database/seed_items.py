# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : seed_items.py
# @Software: AstrBot
# @Description: 初始化并填充 items 表

import sqlite3
import json

def seed_items_data(db_path: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    items = [
        # 黄级 (Common): 1000 铜钱 / 100 元宝
        # 消耗品
        ('粗劣的磨刀石', 'consumable', '黄', '使用后永久增加1点攻击力。', json.dumps({'permanent_buff': {'attack': 1}}), True, 1000, 0),
        ('破旧的兵书', 'consumable', '黄', '使用后获得20点主公经验。', json.dumps({'add_lord_exp': 20}), True, 1000, 0),
        ('村长的推荐信', 'consumable', '黄', '使用后增加5点声望。', json.dumps({'add_reputation': 5}), True, 0, 100),
        ('一袋铜钱', 'consumable', '黄', '使用后获得100铜钱。', json.dumps({'add_coins': 100}), True, 1000, 0),
        ('义军的干粮', 'consumable', '黄', '使用后获得10点武将经验。', json.dumps({'add_exp': 10}), True, 1000, 0),
        ('劣质的护具片', 'consumable', '黄', '使用后永久增加1点防御力。', json.dumps({'permanent_buff': {'defense': 1}}), True, 1000, 0),
        ('黄巾兵的头巾', 'consumable', '黄', '使用后增加1点声望。', json.dumps({'add_reputation': 1}), True, 1000, 0),
        ('一小撮金砂', 'consumable', '黄', '使用后获得1元宝。', json.dumps({'add_yuanbao': 1}), True, 0, 100),
        ('训练假人', 'consumable', '黄', '使用后获得30点武将经验。', json.dumps({'add_exp': 30}), True, 1000, 0),
        ('老旧的地图', 'consumable', '黄', '使用后获得50铜钱。', json.dumps({'add_coins': 50}), True, 1000, 0),

        # 装备
        ('木剑', 'equipment', '黄', '攻击力+5', json.dumps({'attack': 5}), False, 1000, 0),
        ('布衣', 'equipment', '黄', '防御力+5', json.dumps({'defense': 5}), False, 1000, 0),
        ('藤甲', 'equipment', '黄', '防御力+8', json.dumps({'defense': 8}), False, 1000, 0),
        ('短弓', 'equipment', '黄', '攻击力+7', json.dumps({'attack': 7}), False, 1000, 0),
        ('铁护腕', 'equipment', '黄', '攻击力+3，防御力+3', json.dumps({'attack': 3, 'defense': 3}), False, 1000, 0),
        
        # 新增黄级装备 (50件)
        # 武器
        ('生锈的铁斧', 'equipment', '黄', '攻击力+6', json.dumps({'attack': 6}), False, 950, 0),
        ('短矛', 'equipment', '黄', '攻击力+8', json.dumps({'attack': 8}), False, 1100, 0),
        ('铜锤', 'equipment', '黄', '攻击力+9', json.dumps({'attack': 9}), False, 1200, 0),
        ('硬木弓', 'equipment', '黄', '攻击力+7', json.dumps({'attack': 7}), False, 0, 110),
        ('青铜匕首', 'equipment', '黄', '攻击力+5', json.dumps({'attack': 5}), False, 850, 0),
        ('武官剑', 'equipment', '黄', '攻击力+8', json.dumps({'attack': 8}), False, 1150, 0),
        ('校尉刀', 'equipment', '黄', '攻击力+9', json.dumps({'attack': 9}), False, 0, 120),
        # 防具
        ('皮背心', 'equipment', '黄', '防御力+6', json.dumps({'defense': 6}), False, 900, 0),
        ('铜护胸', 'equipment', '黄', '防御力+7', json.dumps({'defense': 7}), False, 1050, 0),
        ('铁片甲', 'equipment', '黄', '防御力+9', json.dumps({'defense': 9}), False, 0, 115),
        ('加厚布衣', 'equipment', '黄', '防御力+5', json.dumps({'defense': 5}), False, 800, 0),
        ('藤条甲', 'equipment', '黄', '防御力+8', json.dumps({'defense': 8}), False, 1100, 0),
        # 饰品
        ('皮护腿', 'equipment', '黄', '防御力+4', json.dumps({'defense': 4}), False, 980, 0),
        ('铜戒指', 'equipment', '黄', '攻击力+2', json.dumps({'attack': 2}), False, 0, 90),
        ('士兵的项链', 'equipment', '黄', '血量+10', json.dumps({'health': 10}), False, 1020, 0),
        ('勇士护符', 'equipment', '黄', '攻击力+3, 血量+5', json.dumps({'attack': 3, 'health': 5}), False, 1180, 0),
        ('守护指环', 'equipment', '黄', '防御力+3, 血量+5', json.dumps({'defense': 3, 'health': 5}), False, 0, 110),
        ('力量手套', 'equipment', '黄', '攻击力+4', json.dumps({'attack': 4}), False, 990, 0),
        ('坚固草鞋', 'equipment', '黄', '防御力+2, 血量+8', json.dumps({'defense': 2, 'health': 8}), False, 950, 0),
        ('旅者披风', 'equipment', '黄', '防御力+5', json.dumps({'defense': 5}), False, 1080, 0),
        
        # 新增黄级消耗品 (30件)
        ('军用干粮', 'consumable', '黄', '使用后获得15点武将经验。', json.dumps({'add_exp': 15}), True, 900, 0),
        ('疗伤草药', 'consumable', '黄', '使用后永久增加5点血量上限。', json.dumps({'permanent_buff': {'health': 5}}), True, 1100, 0),
        ('《武经总要》残页', 'consumable', '黄', '使用后获得25点主公经验。', json.dumps({'add_lord_exp': 25}), True, 0, 105),
        ('一小袋军饷', 'consumable', '黄', '使用后获得120铜钱。', json.dumps({'add_coins': 120}), True, 980, 0),
        ('新兵训练手册', 'consumable', '黄', '使用后获得20点武将经验。', json.dumps({'add_exp': 20}), True, 1050, 0),
        ('磨损的铁锭', 'consumable', '黄', '使用后永久增加1点攻击力。', json.dumps({'permanent_buff': {'attack': 1}}), True, 1150, 0),
        ('硬化皮革', 'consumable', '黄', '使用后永久增加1点防御力。', json.dumps({'permanent_buff': {'defense': 1}}), True, 1120, 0),
        ('村庄的委托书', 'consumable', '黄', '使用后增加8点声望。', json.dumps({'add_reputation': 8}), True, 0, 95),
        ('一小袋金砂', 'consumable', '黄', '使用后获得2元宝。', json.dumps({'add_yuanbao': 2}), True, 0, 110),
        ('《论语》残篇', 'consumable', '黄', '使用后获得30点主公经验。', json.dumps({'add_lord_exp': 30}), True, 1200, 0),
        ('普通的箭矢', 'consumable', '黄', '使用后获得10铜钱。', json.dumps({'add_coins': 10}), True, 850, 0),
        ('清澈的泉水', 'consumable', '黄', '使用后永久增加3点血量上限。', json.dumps({'permanent_buff': {'health': 3}}), True, 950, 0),
        ('士兵的家书', 'consumable', '黄', '使用后增加3点声望。', json.dumps({'add_reputation': 3}), True, 0, 80),
        ('发霉的馒头', 'consumable', '黄', '使用后获得5点武将经验。', json.dumps({'add_exp': 5}), True, 820, 0),
        ('生锈的匕首', 'consumable', '黄', '使用后永久增加1点攻击力。', json.dumps({'permanent_buff': {'attack': 1}}), True, 1080, 0),
        ('破损的盾牌', 'consumable', '黄', '使用后永久增加1点防御力。', json.dumps({'permanent_buff': {'defense': 1}}), True, 1060, 0),
        ('乡绅的认可', 'consumable', '黄', '使用后增加10点声望。', json.dumps({'add_reputation': 10}), True, 0, 115),
        ('小块碎银', 'consumable', '黄', '使用后获得50铜钱。', json.dumps({'add_coins': 50}), True, 990, 0),
        ('《三字经》', 'consumable', '黄', '使用后获得15点主公经验。', json.dumps({'add_lord_exp': 15}), True, 920, 0),
        ('一捆干柴', 'consumable', '黄', '使用后获得5铜钱。', json.dumps({'add_coins': 5}), True, 810, 0),
        ('强身健体丸', 'consumable', '黄', '使用后永久增加2点攻击和2点防御。', json.dumps({'permanent_buff': {'attack': 2, 'defense': 2}}), True, 0, 120),
        ('益气散', 'consumable', '黄', '使用后永久增加8点血量上限。', json.dumps({'permanent_buff': {'health': 8}}), True, 1150, 0),
        ('招募告示', 'consumable', '黄', '使用后增加5点声望。', json.dumps({'add_reputation': 5}), True, 950, 0),
        ('武将挑战状', 'consumable', '黄', '使用后获得10点武将经验。', json.dumps({'add_exp': 10}), True, 880, 0),
        ('官府通告', 'consumable', '黄', '使用后获得10点主公经验。', json.dumps({'add_lord_exp': 10}), True, 860, 0),
        ('一小撮盐', 'consumable', '黄', '使用后获得20铜钱。', json.dumps({'add_coins': 20}), True, 930, 0),
        ('磨刀油', 'consumable', '黄', '使用后永久增加1点攻击力。', json.dumps({'permanent_buff': {'attack': 1}}), True, 1010, 0),
        ('补丁', 'consumable', '黄', '使用后永久增加1点防御力。', json.dumps({'permanent_buff': {'defense': 1}}), True, 1030, 0),
        ('好人卡', 'consumable', '黄', '使用后增加2点声望。', json.dumps({'add_reputation': 2}), True, 0, 85),
        ('小血瓶', 'consumable', '黄', '使用后永久增加5点血量上限。', json.dumps({'permanent_buff': {'health': 5}}), True, 1110, 0),

        # 玄级 (Uncommon): 5000 铜 / 500 元宝
        # 消耗品
        ('《太平要术》残卷', 'consumable', '玄', '使用后获得100点主公经验。', json.dumps({'add_lord_exp': 100}), True, 5000, 0),
        ('百战心得', 'consumable', '玄', '使用后获得100点武将经验。', json.dumps({'add_exp': 100}), True, 5000, 0),
        ('官府的赏金', 'consumable', '玄', '使用后获得500铜钱。', json.dumps({'add_coins': 500}), True, 5000, 0),
        ('一袋元宝', 'consumable', '玄', '使用后获得10元宝。', json.dumps({'add_yuanbao': 10}), True, 0, 500),
        ('精良的磨刀石', 'consumable', '玄', '使用后永久增加3点攻击力。', json.dumps({'permanent_buff': {'attack': 3}}), True, 5000, 0),
        ('加固的护具片', 'consumable', '玄', '使用后永久增加3点防御力。', json.dumps({'permanent_buff': {'defense': 3}}), True, 5000, 0),
        ('将军的推荐信', 'consumable', '玄', '使用后增加20点声望。', json.dumps({'add_reputation': 20}), True, 0, 500),
        ('《孟德新书》节选', 'consumable', '玄', '使用后获得150点主公经验。', json.dumps({'add_lord_exp': 150}), True, 5000, 0),
        ('百炼精钢', 'consumable', '玄', '使用后永久增加2点攻击力和2点防御力。', json.dumps({'permanent_buff': {'attack': 2, 'defense': 2}}), True, 5000, 0),
        ('商队的货物清单', 'consumable', '玄', '使用后获得300铜钱和5点声望。', json.dumps({'add_coins': 300, 'add_reputation': 5}), True, 5000, 0),

        # 装备
        ('铁剑', 'equipment', '玄', '攻击力+12', json.dumps({'attack': 12}), False, 5000, 0),
        ('皮甲', 'equipment', '玄', '防御力+12', json.dumps({'defense': 12}), False, 5000, 0),
        ('长矛', 'equipment', '玄', '攻击力+15', json.dumps({'attack': 15}), False, 5000, 0),
        ('铁甲', 'equipment', '玄', '防御力+15', json.dumps({'defense': 15}), False, 5000, 0),
        ('精钢护腕', 'equipment', '玄', '攻击力+8，防御力+8', json.dumps({'attack': 8, 'defense': 8}), False, 5000, 0),

        # 新增玄级装备 (30件)
        # 武器
        ('精钢长剑', 'equipment', '玄', '攻击力+14', json.dumps({'attack': 14}), False, 4800, 0),
        ('百炼大刀', 'equipment', '玄', '攻击力+16', json.dumps({'attack': 16}), False, 5200, 0),
        ('破甲斧', 'equipment', '玄', '攻击力+18', json.dumps({'attack': 18}), False, 0, 550),
        ('铁胎弓', 'equipment', '玄', '攻击力+15', json.dumps({'attack': 15}), False, 5100, 0),
        ('龙泉剑', 'equipment', '玄', '攻击力+17', json.dumps({'attack': 17}), False, 0, 530),
        # 防具
        ('明光铠', 'equipment', '玄', '防御力+16', json.dumps({'defense': 16}), False, 5300, 0),
        ('玄铁甲', 'equipment', '玄', '防御力+18', json.dumps({'defense': 18}), False, 0, 560),
        ('鱼鳞甲', 'equipment', '玄', '防御力+15', json.dumps({'defense': 15}), False, 4900, 0),
        # 饰品
        ('白玉佩', 'equipment', '玄', '血量+50', json.dumps({'health': 50}), False, 5000, 0),
        ('将军的护符', 'equipment', '玄', '攻击力+5, 防御力+5', json.dumps({'attack': 5, 'defense': 5}), False, 0, 510),
        ('虎皮护腿', 'equipment', '玄', '防御力+8, 血量+20', json.dumps({'defense': 8, 'health': 20}), False, 5250, 0),
        ('狼牙项链', 'equipment', '玄', '攻击力+8, 血量+20', json.dumps({'attack': 8, 'health': 20}), False, 0, 540),
        ('统领之戒', 'equipment', '玄', '攻击力+6, 防御力+6, 血量+10', json.dumps({'attack': 6, 'defense': 6, 'health': 10}), False, 5500, 0),
        
        # 新增玄级消耗品 (17件)
        ('金疮药', 'consumable', '玄', '使用后永久增加20点血量上限。', json.dumps({'permanent_buff': {'health': 20}}), True, 4800, 0),
        ('《六韬》节选', 'consumable', '玄', '使用后获得120点主公经验。', json.dumps({'add_lord_exp': 120}), True, 0, 480),
        ('一箱军饷', 'consumable', '玄', '使用后获得600铜钱。', json.dumps({'add_coins': 600}), True, 5100, 0),
        ('朝廷的嘉奖令', 'consumable', '玄', '使用后增加25点声望。', json.dumps({'add_reputation': 25}), True, 0, 520),
        ('大块牛肉干', 'consumable', '玄', '使用后获得120点武将经验。', json.dumps({'add_exp': 120}), True, 4950, 0),
        ('淬火的铁锭', 'consumable', '玄', '使用后永久增加4点攻击力。', json.dumps({'permanent_buff': {'attack': 4}}), True, 5300, 0),
        ('百炼钢板', 'consumable', '玄', '使用后永久增加4点防御力。', json.dumps({'permanent_buff': {'defense': 4}}), True, 5280, 0),
        ('一袋珠宝', 'consumable', '玄', '使用后获得12元宝。', json.dumps({'add_yuanbao': 12}), True, 0, 550),
        ('《尉缭子》', 'consumable', '玄', '使用后获得180点主公经验。', json.dumps({'add_lord_exp': 180}), True, 0, 580),
        ('凝神丹', 'consumable', '玄', '使用后永久增加5点攻击和5点防御。', json.dumps({'permanent_buff': {'attack': 5, 'defense': 5}}), True, 0, 600),
        ('壮骨粉', 'consumable', '玄', '使用后永久增加25点血量上限。', json.dumps({'permanent_buff': {'health': 25}}), True, 5400, 0),
        ('太守的手令', 'consumable', '玄', '使用后增加30点声望。', json.dumps({'add_reputation': 30}), True, 0, 570),
        ('陈年女儿红', 'consumable', '玄', '使用后获得150点武将经验。', json.dumps({'add_exp': 150}), True, 5150, 0),
        ('一卷丝绸', 'consumable', '玄', '使用后获得550铜钱。', json.dumps({'add_coins': 550}), True, 4850, 0),
        ('精锐训练法', 'consumable', '玄', '使用后获得200点武将经验。', json.dumps({'add_exp': 200}), True, 5600, 0),
        ('《墨子》残卷', 'consumable', '玄', '使用后永久增加6点防御力。', json.dumps({'permanent_buff': {'defense': 6}}), True, 0, 590),
        ('《鬼谷子》残卷', 'consumable', '玄', '使用后永久增加6点攻击力。', json.dumps({'permanent_buff': {'attack': 6}}), True, 0, 590),

        # 地级 (Rare): 10000 铜钱 / 1000 元宝
        # 消耗品
        ('传国玉玺（仿）', 'consumable', '地', '使用后增加50点声望。', json.dumps({'add_reputation': 50}), True, 0, 1000),
        ('《孙子兵法》抄本', 'consumable', '地', '使用后获得500点主公经验。', json.dumps({'add_lord_exp': 500}), True, 0, 1000),
        ('武力果', 'consumable', '地', '使用后永久增加5点攻击力。', json.dumps({'permanent_buff': {'attack': 5}}), True, 0, 1000),
        ('统率书', 'consumable', '地', '使用后永久增加5点防御力。', json.dumps({'permanent_buff': {'defense': 5}}), True, 0, 1000),
        ('一箱金银', 'consumable', '地', '使用后获得2000铜钱。', json.dumps({'add_coins': 2000}), True, 10000, 0),
        ('一箱元宝', 'consumable', '地', '使用后获得50元宝。', json.dumps({'add_yuanbao': 50}), True, 0, 1000),
        ('《兵法二十四篇》', 'consumable', '地', '使用后获得500点武将经验。', json.dumps({'add_exp': 500}), True, 0, 1000),
        ('传国将领的信物', 'consumable', '地', '使用后增加100点声望。', json.dumps({'add_reputation': 100}), True, 0, 1000),
        ('龙涎香', 'consumable', '地', '使用后永久增加4点攻击力和4点防御力。', json.dumps({'permanent_buff': {'attack': 4, 'defense': 4}}), True, 0, 1000),
        ('传世兵书', 'consumable', '地', '使用后获得800点主公经验。', json.dumps({'add_lord_exp': 800}), True, 0, 1000),

        # 装备
        ('青钢剑', 'equipment', '地', '攻击力+25', json.dumps({'attack': 25}), False, 0, 1000),
        ('锁子甲', 'equipment', '地', '防御力+25', json.dumps({'defense': 25}), False, 0, 1000),
        ('方天画戟（仿）', 'equipment', '地', '攻击力+30', json.dumps({'attack': 30}), False, 0, 1000),
        ('亮银甲', 'equipment', '地', '防御力+30', json.dumps({'defense': 30}), False, 0, 1000),
        ('龙鳞护腕', 'equipment', '地', '攻击力+15，防御力+15', json.dumps({'attack': 15, 'defense': 15}), False, 0, 1000),

        # 天级 (Epic): 50000 铜钱 / 5000 元宝
        # 消耗品
        ('杜康酒', 'consumable', '天', '传说中的美酒，使用后增加200点主公经验和100点声望。', json.dumps({'add_lord_exp': 200, 'add_reputation': 100}), True, 0, 5000),
        ('千年人参', 'consumable', '天', '使用后永久增加10点攻击力和10点防御力。', json.dumps({'permanent_buff': {'attack': 10, 'defense': 10}}), True, 0, 5000),
        ('神力丹', 'consumable', '天', '使用后永久增加15点攻击力。', json.dumps({'permanent_buff': {'attack': 15}}), True, 0, 5000),
        ('九转金丹', 'consumable', '天', '使用后永久增加15点防御力。', json.dumps({'permanent_buff': {'defense': 15}}), True, 0, 5000),
        ('智慧果', 'consumable', '天', '使用后获得2000点主公经验。', json.dumps({'add_lord_exp': 2000}), True, 0, 5000),
        ('传国玉玺', 'consumable', '天', '真正的传国玉玺，使用后增加500点声望。', json.dumps({'add_reputation': 500}), True, 0, 5000),
        ('《太平天书》', 'consumable', '天', '使用后获得2000点武将经验。', json.dumps({'add_exp': 2000}), True, 0, 5000),
        ('一箱奇珍异宝', 'consumable', '天', '使用后获得10000铜钱和100元宝。', json.dumps({'add_coins': 10000, 'add_yuanbao': 100}), True, 50000, 0),
        ('麒麟血', 'consumable', '天', '使用后永久增加20点攻击力。', json.dumps({'permanent_buff': {'attack': 20}}), True, 0, 5000),
        ('玄武甲片', 'consumable', '天', '使用后永久增加20点防御力。', json.dumps({'permanent_buff': {'defense': 20}}), True, 0, 5000),

        # 装备
        ('倚天剑', 'equipment', '天', '攻击力+40', json.dumps({'attack': 40}), False, 0, 5000),
        ('黄金甲', 'equipment', '天', '防御力+40', json.dumps({'defense': 40}), False, 0, 5000),
        ('青龙偃月刀', 'equipment', '天', '攻击力+50', json.dumps({'attack': 50}), False, 0, 5000),
        ('朱雀羽扇', 'equipment', '天', '攻击力+35', json.dumps({'attack': 35}), False, 0, 5000),
        ('麒麟臂', 'equipment', '天', '攻击力+25，防御力+25', json.dumps({'attack': 25, 'defense': 25}), False, 0, 5000),

        # 特殊 (Special) - 根据品质定价
        ('铜币袋', 'special', '黄', '一个装有铜币的袋子，使用后随机获得100-500铜钱。', json.dumps({'add_coins': [100, 500]}), True, 1000, 0),
        ('小经验丹', 'special', '黄', '使用后获得50点武将经验。', json.dumps({'add_exp': 50}), True, 1000, 0),
        ('元宝袋', 'special', '玄', '一个装有元宝的袋子，使用后随机获得10-50元宝。', json.dumps({'add_yuanbao': [10, 50]}), True, 0, 500),
        ('声望令', 'special', '玄', '使用后增加20点声望。', json.dumps({'add_reputation': 20}), True, 0, 500),
        ('失传的兵法', 'special', '地', '一本失传已久的兵法书，使用后可以增加1000点武将经验。', json.dumps({'add_exp': 1000}), True, 10000, 0),
        ('一套枪法', 'special', '地', '古代将军之魂传授的枪法，使用后可永久提升5点攻击力。', json.dumps({'permanent_buff': {'attack': 5}}), True, 10000, 0),
        ('《论语》注解', 'special', '玄', '儒生赠予的书籍，蕴含着智慧，使用后增加500点主公经验。', json.dumps({'add_lord_exp': 500}), True, 5000, 0),
        ('县尉的推荐信', 'special', '地', '一封来自县尉的推荐信，使用后获得200声望。', json.dumps({'add_reputation': 200}), True, 0, 1000),
        ('黄巾军详细部署图', 'special', '地', '一份详细的黄巾军部署图，可以卖给官府换取大量铜币和声望。', json.dumps({'sell_value': {'coins': 5000, 'reputation': 50}}), False, 10000, 0),
        ('招募令', 'special', '地', '可以招募一名新的武将。', json.dumps({'action': 'recruit_general'}), True, 0, 1000),
        ('神秘钥匙', 'special', '地', '可以用来打开一个神秘的宝箱。', json.dumps({'action': 'open_chest'}), True, 10000, 0),
        ('挑战书', 'special', '地', '向指定玩家发起挑战的凭证。', json.dumps({'action': 'challenge_player'}), True, 0, 1000),
        ('休战符', 'special', '玄', '使用后24小时内不会被其他玩家攻击。', json.dumps({'status': 'truce', 'duration_hours': 24}), True, 0, 500),
        ('双倍经验卡', 'special', '地', '使用后1小时内打怪经验双倍。', json.dumps({'buff': 'double_exp', 'duration_hours': 1}), True, 0, 1000),
        ('鉴定卷轴', 'special', '玄', '可以鉴定未知的装备。', json.dumps({'action': 'identify_item'}), True, 5000, 0),
        ('回城符', 'special', '黄', '可以立刻回到主城。', json.dumps({'action': 'return_to_city'}), True, 1000, 0),
        ('盗贼的地图', 'special', '玄', '标记了一个小型宝藏的位置。', json.dumps({'action': 'trigger_thief_cache'}), True, 5000, 0),
        ('幸运草', 'special', '地', '使用后短时间内提升掉宝率。', json.dumps({'buff': 'luck', 'duration_minutes': 30}), True, 0, 1000),
        ('天师符', 'special', '天', '可以封印弱小的妖魔。', json.dumps({'action': 'seal_demon'}), True, 0, 5000),
        ('将军的信物', 'special', '地', '一个可以证明你与某位将军有交情的信物，也许能在特定时候派上用场。', '{}', False, 10000, 0),
        ('《伤寒杂病论》', 'special', '天', '医圣张仲景所著的医书，使用后永久增加全队10%生命值。', json.dumps({'permanent_buff': {'team_health_percent': 0.1}}), True, 0, 5000),
        ('避水珠', 'special', '天', '传说中可以分水的宝珠，在特定水下副本中有奇效。', '{}', False, 0, 5000),
        ('稀有的黑铁矿石', 'special', '玄', '可以用于锻造高级装备的稀有材料。', '{}', False, 5000, 0),
        ('一匹良驹', 'special', '地', '装备后提升移动速度，减少冒险冷却时间10%。', json.dumps({'adventure_cooldown_reduction': 0.1}), False, 0, 1000),
        ('无用的玻璃球', 'special', '黄', '一个看起来像宝珠的玻璃球，一文不值。', '{}', False, 1000, 0),
        ('易容面具', 'special', '天', '可以伪装成其他身份。', '{}', False, 0, 5000),
        ('神农锄', 'special', '天', '用于草药采集，有几率获得稀有草药。', '{}', False, 0, 5000),
        ('鲁班斧', 'special', '天', '用于木材采集，有几率获得稀有木材。', '{}', False, 0, 5000),
        ('矿工镐', 'special', '天', '用于矿石挖掘，有几率获得稀有矿石。', '{}', False, 0, 5000)
    ]

    try:
        # 确保 effects 列存在
        c.execute("PRAGMA table_info(items)")
        columns = [column[1] for column in c.fetchall()]
        if 'effects' not in columns:
            print("错误：'items' 表中缺少 'effects' 列。请先运行数据库迁移。")
            return

        # 清空现有物品，以便重新插入
        c.execute("DELETE FROM items")
        print("已清空旧的物品数据。")

        c.executemany('''
            INSERT INTO items (name, type, quality, description, effects, is_consumable, base_price_coins, base_price_yuanbao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', items)
        conn.commit()
        
        print(f"数据库同步完成。{len(items)} 个新物品被添加。")

    except sqlite3.Error as e:
        print(f"添加物品时出错: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    # 用于直接运行此脚本进行测试
    db_file = 'data/sanguo_rpg.db'
    seed_items_data(db_file)
