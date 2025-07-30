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

    def add_sample_generals(self, generals_data: List[tuple]):
        """添加示例武将数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.executemany(
                "INSERT INTO generals (general_id, name, rarity, camp, wu_li, zhi_li, tong_shuai, su_du, skill_desc, background) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                generals_data
            )
            conn.commit()
        finally:
            conn.close()

    def get_generals_count(self) -> int:
        """获取武将总数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM generals")
            count = cursor.fetchone()[0]
            return count
        finally:
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
