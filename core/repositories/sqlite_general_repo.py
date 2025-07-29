# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : sqlite_general_repo.py
# @Software: AstrBot
# @Description: 武将相关的数据访问层

import sqlite3
import random
from datetime import datetime
from typing import List, Optional
from astrbot_plugin_sanguo_rpg.core.domain.models import General, UserGeneral

class SqliteGeneralRepository:
    """武将数据仓储 - SQLite实现"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_sample_generals()
    
    def _init_sample_generals(self):
        """初始化示例武将数据"""
        sample_generals = [
    (16, '张让', 1, '群', 61, 64, 63, 61, '无', '侍奉灵帝的宦官十常侍之首，暗杀了何进，但被袁绍追杀时投河自杀。'),
    (17, '张角', 2, '群', 70, 69, 66, 69, '太平道：所有攻击有20%概率转化为妖术伤害。', '钜鹿郡的在野人士。为太平道的教祖，向民众广传教义。趁社会动乱，得到广大民众支持。结成黄巾党对抗汉王朝，发动黄巾之乱。\n中郎将皇甫嵩奉令讨伐张角时，张角不久即因病去世，他死后不久，十月，皇甫嵩和张梁在广宗大战，张梁大败战死，张角也被剖开棺木，戮尸枭首，将人头送到洛阳示众'),
    (18, '张宝', 4, '群', 88, 87, 89, 90, '地公将军：闯关时，失败惩罚降低50%。', '张角之弟。和张角一起举兵欲推翻汉王朝，而发动黄巾之乱。自称地公将军，用兄长传授的妖术指挥叛乱，后被属下严政刺杀。'),
    (19, '张梁', 4, '群', 89, 91, 89, 90, '人公将军：闯关时，获得金币增加20%。', '张角、张宝之弟。和兄长们一起举兵欲推翻汉王朝，而发动黄巾之乱。自称人公将军，张角死后继续指挥叛乱，败给了官军，在曲阳之战战死。'),
    (20, '张飞', 5, '蜀', 99, 100, 99, 96, '当阳桥：闯关时，有10%概率直接胜利。', '演义中为蜀汉五虎大将之一。与刘备、关羽结为异姓兄弟。在长坂坡之战中，单枪匹马在长坂桥上，喝退曹操万大军的追击。后因关羽死于东吴之手，急于为兄报仇，要在三天以内做成大量白色的铠甲。但迁怒部将范疆、张达，在睡觉时被范疆、张达所杀。'),
]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表（如果不存在）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS generals (
            general_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            rarity INTEGER NOT NULL,
            camp TEXT NOT NULL,
            wu_li INTEGER NOT NULL,
            zhi_li INTEGER NOT NULL,
            tong_shuai INTEGER NOT NULL,
            su_du INTEGER NOT NULL,
            skill_desc TEXT NOT NULL,
            background TEXT NOT NULL
        )
        """)
        
        # 创建user_generals表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_generals (
            instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            general_id INTEGER NOT NULL,
            level INTEGER NOT NULL,
            exp INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (general_id) REFERENCES generals (general_id)
        )
        """)
        
        # 检查并添加 background 列以实现向后兼容
        cursor.execute("PRAGMA table_info(generals)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'background' not in columns:
            cursor.execute("ALTER TABLE generals ADD COLUMN background TEXT NOT NULL DEFAULT ''")

        # 检查是否已有数据
        cursor.execute("SELECT COUNT(*) FROM generals")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.executemany(
                "INSERT INTO generals (general_id, name, rarity, camp, wu_li, zhi_li, tong_shuai, su_du, skill_desc, background) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                sample_generals
            )
            conn.commit()
        
        conn.close()
    
    def get_general_by_id(self, general_id: int) -> Optional[General]:
        """根据ID获取武将模板"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT general_id, name, rarity, camp, wu_li, zhi_li, tong_shuai, su_du, skill_desc, background FROM generals WHERE general_id = ?",
            (general_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return General(*row)
        return None
    
    def get_all_generals(self) -> List[General]:
        """获取所有武将模板"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT general_id, name, rarity, camp, wu_li, zhi_li, tong_shuai, su_du, skill_desc, background FROM generals ORDER BY rarity DESC, general_id"
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [General(*row) for row in rows]
    
    def get_generals_by_rarity(self, rarity: int) -> List[General]:
        """根据稀有度获取武将"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT general_id, name, rarity, camp, wu_li, zhi_li, tong_shuai, su_du, skill_desc, background FROM generals WHERE rarity = ?",
            (rarity,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [General(*row) for row in rows]
    
    def get_user_generals(self, user_id: str) -> List[UserGeneral]:
        """获取玩家拥有的武将"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT instance_id, user_id, general_id, level, exp, created_at FROM user_generals WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        user_generals = []
        for row in rows:
            # 将字符串时间转换为datetime对象
            created_at = datetime.fromisoformat(row[5]) if row[5] else datetime.now()
            user_generals.append(UserGeneral(row[0], row[1], row[2], row[3], row[4], created_at))
        
        return user_generals
    
    def add_user_general(self, user_id: str, general_id: int) -> bool:
        """为玩家新增武将"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO user_generals (user_id, general_id, level, exp, created_at) VALUES (?, ?, 1, 0, ?)",
                (user_id, general_id, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_user_general_count(self, user_id: str) -> int:
        """获取玩家武将数量"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM user_generals WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_random_general_by_rarity_pool(self) -> Optional[General]:
        """根据稀有度概率池随机获取武将"""
        all_generals = self.get_all_generals()
        if not all_generals:
            return None

        # 稀有度概率：5星(1%), 4星(9%), 3星(20%), 2星(70%)
        rarity_pool = [2] * 70 + [3] * 20 + [4] * 9 + [5] * 1
        
        while True:
            selected_rarity = random.choice(rarity_pool)
            generals_in_rarity = [g for g in all_generals if g.rarity == selected_rarity]
            
            if generals_in_rarity:
                return random.choice(generals_in_rarity)
            # 如果当前抽到的稀有度在数据库中不存在对应武将，则重新抽取。
            # 这样可以避免在样本数据不全时（如缺少3星武将）程序出错。
