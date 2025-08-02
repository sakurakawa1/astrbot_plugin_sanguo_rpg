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
        # ID: 1-10 (消耗品)
        ('小笼包', 'consumable', 'common', '恢复20点体力。', json.dumps({'health': 20}), True, 50, 0), # 1
        ('行军散', 'consumable', 'common', '恢复50点体力。', json.dumps({'health': 50}), True, 120, 0), # 2
        ('缴获的军粮', 'consumable', 'common', '一份普通的军粮，使用后增加10点经验和1点声望。', json.dumps({'exp': 10, 'reputation': 1}), True, 25, 0), # 3
        ('《太平要术》残卷', 'consumable', 'uncommon', '使用后获得100点经验。', json.dumps({'exp': 100}), True, 200, 0), # 4
        ('传国玉玺（仿）', 'consumable', 'rare', '使用后增加50点声望。', json.dumps({'reputation': 50}), True, 0, 50), # 5
        ('杜康酒', 'consumable', 'epic', '传说中的美酒，使用后增加200经验和100声望。', json.dumps({'exp': 200, 'reputation': 100}), True, 0, 200), # 6
        ('强身健体的丹药', 'consumable', 'uncommon', '隐士赠予的丹药，使用后永久增加属性。', json.dumps({'permanent_buff': 'health_10'}), True, 0, 0), # 7

        # ID: 11-20 (装备)
        ('木剑', 'equipment', 'common', '攻击力+5', json.dumps({'attack': 5}), False, 100, 0), # 8
        ('铁剑', 'equipment', 'uncommon', '攻击力+10', json.dumps({'attack': 10}), False, 250, 0), # 9
        ('青钢剑', 'equipment', 'rare', '攻击力+20', json.dumps({'attack': 20}), False, 0, 200), # 10
        ('布衣', 'equipment', 'common', '防御力+5', json.dumps({'defense': 5}), False, 80, 0), # 11
        ('皮甲', 'equipment', 'uncommon', '防御力+10', json.dumps({'defense': 10}), False, 200, 0), # 12
        ('锁子甲', 'equipment', 'rare', '防御力+20', json.dumps({'defense': 20}), False, 0, 180), # 13
        ('生锈的古剑', 'equipment', 'uncommon', '一柄在战场遗迹中发现的古剑，似乎颇有来历。', json.dumps({'attack': 12}), False, 0, 0), # 14

        # ID: 21-40 (特殊/任务物品)
        ('招募令', 'special', 'rare', '可以招募一名新的武将。', json.dumps({'action': 'recruit_general'}), True, 0, 100), # 15
        ('黄巾军详细部署图', 'special', 'rare', '一份详细的黄巾军部署图，价值连城。', '{}', False, 0, 0), # 16
        ('县尉的推荐信', 'special', 'rare', '一封来自县尉的推荐信，可以让你在官场上获得便利。', '{}', False, 0, 0), # 17
        ('神秘的藏宝图', 'special', 'uncommon', '一张残缺的地图，指向未知的宝藏。', '{}', False, 0, 0), # 18
        ('《论语》注解', 'special', 'uncommon', '儒生赠予的书籍，蕴含着智慧。', '{}', False, 0, 0), # 19
        ('将军的信物', 'special', 'rare', '一个可以证明你与某位将军有交情的信物。', '{}', False, 0, 0), # 20
        ('《伤寒杂病论》', 'special', 'epic', '医圣张仲景所著的医书，价值连城。', '{}', False, 0, 0), # 21
        ('避水珠', 'special', 'epic', '传说中可以分水的宝珠。', '{}', False, 0, 0), # 22
        ('稀有的黑铁矿石', 'special', 'uncommon', '可以用于锻造高级装备的稀有材料。', '{}', False, 0, 0), # 23
        ('一匹良驹', 'special', 'rare', '一匹日行千里的骏马，是英雄的标配。', '{}', False, 0, 0), # 24
        ('失传的兵法', 'special', 'rare', '一本失传已久的兵法书，使用后可以增加大量经验。', json.dumps({'exp': 200}), True, 0, 0), # 25
        ('无用的玻璃球', 'special', 'common', '一个看起来像宝珠的玻璃球，一文不值。', '{}', False, 0, 0), # 26
        ('一套枪法', 'special', 'rare', '古代将军之魂传授的枪法，使用后可提升能力。', json.dumps({'permanent_buff': 'attack_5'}), True, 0, 0), # 27
    ]

    try:
        # 确保 effects 列存在
        c.execute("PRAGMA table_info(items)")
        columns = [column[1] for column in c.fetchall()]
        if 'effects' not in columns:
            print("错误：'items' 表中缺少 'effects' 列。请先运行数据库迁移。")
            return

        c.executemany('''
            INSERT OR IGNORE INTO items (name, type, quality, description, effects, is_consumable, base_price_coins, base_price_yuanbao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', items)
        conn.commit()
        
        # 获取实际插入的行数
        changes = conn.total_changes
        print(f"数据库同步完成。{changes} 个新物品被添加或更新。")

    except sqlite3.Error as e:
        print(f"添加物品时出错: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    # 用于直接运行此脚本进行测试
    db_file = 'data/sanguo_rpg.db'
    seed_items_data(db_file)
