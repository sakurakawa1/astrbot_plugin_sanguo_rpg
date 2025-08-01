# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : seed_items.py
# @Software: AstrBot
# @Description: 填充初始装备数据

import sqlite3
import random
from astrbot.api import logger

# 定义品阶和价格范围
QUALITY_PRICES = {
    "黄": {"coins": (800, 1200), "yuanbao": (80, 120)},
    "玄": {"coins": (4000, 6000), "yuanbao": (400, 600)},
    "地": {"coins": (8000, 12000), "yuanbao": (800, 1200)},
    "天": {"coins": (16000, 24000), "yuanbao": (1600, 2400)},
}

# 定义装备数据
# 格式: (名称, 类型, 品阶, 效果类型, 效果值, 是否消耗品, 描述)
ITEMS_DATA = [
    # --- 消耗品 (丹药/兵书) ---
    # 黄品
    ("行军丹", "丹药", "黄", "exp_boost", 50, True, "基础丹药，能快速恢复体力，补充少量武将经验。"),
    ("止血草", "丹药", "黄", "exp_boost", 60, True, "常见的草药，用于处理皮外伤，补充少量武将经验。"),
    ("兵法心得", "兵书", "黄", "exp_boost", 80, True, "记录了基础用兵技巧的小册子，能提升武将经验。"),
    ("论语残篇", "兵书", "黄", "reputation_boost", 10, True, "儒家经典，研读可增加少量声望。"),

    # 玄品
    ("炼体丸", "丹药", "玄", "exp_boost", 250, True, "能强化筋骨的丹药，大幅提升武将经验。"),
    ("续命散", "丹药", "玄", "exp_boost", 280, True, "据说能延续生命的药散，效果显著，能提升武将经验。"),
    ("孟德新书", "兵书", "玄", "reputation_boost", 50, True, "曹操所著的兵法书，研读可增加不少声望。"),
    ("兵书二十四篇", "兵书", "玄", "exp_boost", 350, True, "诸葛亮所著，包含丰富的军事策略，能极大提升武将经验。"),

    # 地品
    ("九转还魂丹", "丹药", "地", "exp_boost", 1000, True, "传说中的灵丹妙药，能起死回生，提供巨量武将经验。"),
    ("孙子兵法", "兵书", "地", "reputation_boost", 200, True, "兵家圣典，持有者声望大增。"),
    ("六韬", "兵书", "地", "exp_boost", 1200, True, "古代著名的兵书，蕴含高深的军事思想，提供巨量武将经验。"),

    # 天品
    ("太平要术", "兵书", "天", "exp_boost", 5000, True, "张角所持的仙书，蕴含通天彻地之能，提供海量武将经验。"),
    ("仙丹·龙元", "丹药", "天", "exp_boost", 6000, True, "以龙之精气炼制的仙丹，凡人服用可脱胎换骨，提供海量武将经验。"),
    ("封禅玉牒", "珍宝", "天", "reputation_boost", 1000, False, "帝王用于封禅大典的玉牒，是无上权力的象征，持有者声望剧增。"),

    # --- 非消耗品 (兵器/防具/坐骑/珍宝) ---
    # 黄品
    ("铁剑", "兵器", "黄", "sellable", 0, False, "普通士兵使用的铁剑，聊胜于无。"),
    ("皮甲", "防具", "黄", "sellable", 0, False, "用兽皮制成的甲胄，能提供基础的防护。"),
    ("黄骠马", "坐骑", "黄", "sellable", 0, False, "常见的战马，耐力尚可。"),
    ("传国玉玺（仿）", "珍宝", "黄", "reputation_boost", 20, False, "仿制的传国玉玺，做工粗糙但也能唬人，能增加少量声望。"),
    ("铜雀", "珍宝", "黄", "sellable", 0, False, "铜制的麻雀，是某种身份的象征。"),
    
    # 玄品
    ("青釭剑", "兵器", "玄", "sellable", 0, False, "削铁如泥的宝剑，原为曹操所有，后被赵云夺走。"),
    ("明光铠", "防具", "玄", "sellable", 0, False, "打磨光滑的精铁铠甲，在阳光下熠熠生辉。"),
    ("爪黄飞电", "坐骑", "玄", "sellable", 0, False, "曹操的爱马之一，速度极快。"),
    ("玉佩", "珍宝", "玄", "reputation_boost", 60, False, "雕工精美的玉佩，是身份和地位的象征，能增加不少声望。"),
    ("金丝软甲", "防具", "玄", "sellable", 0, False, "用金丝和软铁打造的内甲，轻便且防御力不俗。"),

    # 地品
    ("方天画戟", "兵器", "地", "sellable", 0, False, "吕布所使用的传奇兵器，威震天下。"),
    ("赤兔马", "坐骑", "地", "sellable", 0, False, "人中吕布，马中赤兔。日行千里的宝马。"),
    ("传国玉玺", "珍宝", "地", "reputation_boost", 250, False, "真正的传国玉玺，得之可号令天下，持有者声望大增。"),
    ("诸葛连弩", "兵器", "地", "sellable", 0, False, "诸葛亮发明的连发弩，可一次发射十支箭。"),
    ("白银狮子盔", "防具", "地", "sellable", 0, False, "马超所戴的头盔，银光闪闪，威风凛凛。"),

    # 天品
    ("倚天剑", "兵器", "天", "sellable", 0, False, "与青釭剑齐名的神兵，锋利无比，为曹操佩剑。"),
    ("麒麟", "坐骑", "天", "sellable", 0, False, "传说中的瑞兽，非有德之君不能驾驭。"),
    ("玉玺·受命于天", "珍宝", "天", "reputation_boost", 1200, False, "刻有“受命于天，既寿永昌”的传国玉玺真品，是天命所归的象征。"),
]

# 自动生成更多装备以达到100+
def generate_more_items():
    generated_items = []
    adjectives = ["破旧的", "精良的", "华丽的", "传说的", "无双的", "雕花的", "镶金的", "古朴的", "锋利的"]
    nouns = [
        "长枪", "大刀", "弓", "头盔", "胸甲", "战靴", "玉璧", "酒杯", "兵符",
        "短剑", "护腕", "项链", "戒指", "卷轴", "令牌"
    ]
    types = ["兵器", "防具", "珍宝"]
    qualities = ["黄", "玄", "地"]  # 增加地品装备的生成

    for i in range(len(ITEMS_DATA), 105):
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        item_type = random.choice(types)
        quality = random.choice(qualities)
        name = f"{adj}{noun}"
        
        # 确保名称不重复
        if any(item[0] == name for item in ITEMS_DATA + generated_items):
            name = f"{adj}{noun}_{i}"

        desc = f"一件{quality}品的{item_type}，看起来有些年头了。"
        
        if item_type == "珍宝":
            effect_type = "reputation_boost"
            if quality == "黄":
                effect_value = random.randint(5, 25)
            elif quality == "玄":
                effect_value = random.randint(30, 70)
            else: # 地
                effect_value = random.randint(80, 150)
        else:
            effect_type = "sellable"
            effect_value = 0

        generated_items.append((name, item_type, quality, effect_type, effect_value, False, desc))
        
    return generated_items

ITEMS_DATA.extend(generate_more_items())


def seed_items_data(db_path: str):
    """将初始装备数据填充到数据库"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # 检查 items 表是否为空
        c.execute("SELECT COUNT(*) FROM items")
        if c.fetchone()[0] > 0:
            logger.info("装备数据已存在，跳过填充过程。")
            return

        logger.info("正在填充初始装备数据...")
        
        items_to_insert = []
        for name, type, quality, effect_type, effect_value, is_consumable, description in ITEMS_DATA:
            price_range = QUALITY_PRICES[quality]
            coins = random.randint(*price_range["coins"])
            yuanbao = random.randint(*price_range["yuanbao"])
            
            items_to_insert.append((
                name, type, quality, description, 
                effect_type, effect_value, is_consumable, 
                coins, yuanbao
            ))

        c.executemany('''
            INSERT INTO items (name, type, quality, description, effect_type, effect_value, is_consumable, base_price_coins, base_price_yuanbao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', items_to_insert)

        conn.commit()
        logger.info(f"成功填充了 {len(items_to_insert)} 条装备数据。")

    except Exception as e:
        logger.error(f"填充装备数据时出错: {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()
