# -*- coding: utf-8 -*-
# @Time    : 2025/07/30
# @Author  : Cline
# @File    : data_setup_service.py
# @Software: AstrBot
# @Description: 用于初始化核心游戏数据的服务

import sqlite3
from astrbot_plugin_sanguo_rpg.core.repositories.sqlite_general_repo import SqliteGeneralRepository

class DataSetupService:
    def __init__(self, general_repo: SqliteGeneralRepository, db_path: str):
        self.general_repo = general_repo
        self.db_path = db_path

    def setup_initial_data(self):
        """检查并初始化核心数据，如武将模板"""
        self._create_tables()
        self._seed_generals()

    def _create_tables(self):
        """创建数据库表（如果不存在）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # 创建 generals 表
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
            
            # 创建 user_generals 表
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
            conn.commit()
        finally:
            conn.close()

    def _seed_generals(self):
        """填充初始武将数据（如果为空）"""
        count = self.general_repo.get_generals_count()
        if count == 0:
            sample_generals = [
                (16, '张让', 1, '群', 61, 64, 63, 61, '无', '侍奉灵帝的宦官十常侍之首，暗杀了何进，但被袁绍追杀时投河自杀。'),
                (17, '张角', 2, '群', 70, 69, 66, 69, '太平道：所有攻击有20%概率转化为妖术伤害。', '钜鹿郡的在野人士。为太平道的教祖，向民众广传教义。趁社会动乱，得到广大民众支持。结成黄巾党对抗汉王朝，发动黄巾之乱。'),
                (18, '张宝', 4, '群', 88, 87, 89, 90, '地公将军：闯关时，失败惩罚降低50%。', '张角之弟。和张角一起举兵欲推翻汉王朝，而发动黄巾之乱。自称地公将军，用兄长传授的妖术指挥叛乱，后被属下严政刺杀。'),
                (19, '张梁', 4, '群', 89, 91, 89, 90, '人公将军：闯关时，获得金币增加20%。', '张角、张宝之弟。和兄长们一起举兵欲推翻汉王朝，而发动黄巾之乱。自称人公将军，张角死后继续指挥叛乱，败给了官军，在曲阳之战战死。'),
                (20, '张飞', 5, '蜀', 99, 100, 99, 96, '当阳桥：闯关时，有10%概率直接胜利。', '演义中为蜀汉五虎大将之一。与刘备、关羽结为异姓兄弟。在长坂坡之战中，单枪匹马在长坂桥上，喝退曹操万大军的追击。后因关羽死于东吴之手，急于为兄报仇，要在三天以内做成大量白色的铠甲。但迁怒部将范疆、张达，在睡觉时被范疆、张达所杀。'),
            ]
            self.general_repo.add_sample_generals(sample_generals)
