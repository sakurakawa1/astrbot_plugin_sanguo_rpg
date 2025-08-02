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
from astrbot_plugin_sanguo_rpg.core.domain.models import General, UserGeneral, UserGeneralDetails, BattleLog

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
                "INSERT OR IGNORE INTO generals (general_id, name, rarity, camp, wu_li, zhi_li, tong_shuai, su_du, skill_desc, background) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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

    def get_user_generals_with_details(self, user_id: str) -> List[UserGeneralDetails]:
        """获取玩家拥有的武将（包含详细信息）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 使用JOIN查询合并两个表的数据
        sql = """
            SELECT
                ug.instance_id,
                ug.user_id,
                ug.general_id,
                ug.level,
                ug.exp,
                ug.created_at,
                g.name,
                g.rarity,
                g.camp,
                g.wu_li,
                g.zhi_li,
                g.tong_shuai,
                g.su_du,
                g.skill_desc
            FROM user_generals ug
            JOIN generals g ON ug.general_id = g.general_id
            WHERE ug.user_id = ?
            ORDER BY g.rarity DESC, ug.level DESC, ug.created_at DESC
        """
        
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        detailed_generals = []
        for row in rows:
            # 将字符串时间转换为datetime对象
            created_at = datetime.fromisoformat(row[5]) if row[5] else datetime.now()
            # 实例化新的数据模型
            detailed_generals.append(UserGeneralDetails(
                instance_id=row[0],
                user_id=row[1],
                general_id=row[2],
                level=row[3],
                exp=row[4],
                created_at=created_at,
                name=row[6],
                rarity=row[7],
                camp=row[8],
                wu_li=row[9],
                zhi_li=row[10],
                tong_shuai=row[11],
                su_du=row[12],
                skill_desc=row[13]
            ))
            
        return detailed_generals

    def get_user_generals_by_instance_ids(self, user_id: str, instance_ids: List[int]) -> List[UserGeneral]:
        """根据实例ID列表获取玩家拥有的武将"""
        if not instance_ids:
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        placeholders = ','.join('?' for _ in instance_ids)
        sql = f"SELECT instance_id, user_id, general_id, level, exp, created_at FROM user_generals WHERE user_id = ? AND instance_id IN ({placeholders})"
        
        params = [user_id] + instance_ids
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        user_generals = []
        for row in rows:
            created_at = datetime.fromisoformat(row[5]) if row[5] else datetime.now()
            user_generals.append(UserGeneral(row[0], row[1], row[2], row[3], row[4], created_at))
        
        return user_generals

    def get_generals_names_by_instance_ids(self, instance_ids: List[int]) -> List[str]:
        """根据实例ID列表获取武将名称列表"""
        if not instance_ids:
            return []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        placeholders = ','.join('?' for _ in instance_ids)
        sql = f"""
            SELECT g.name
            FROM user_generals ug
            JOIN generals g ON ug.general_id = g.general_id
            WHERE ug.instance_id IN ({placeholders})
        """
        
        cursor.execute(sql, instance_ids)
        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows]

    def get_user_generals_with_details_by_instance_ids(self, user_id: str, instance_ids: List[int]) -> List[UserGeneralDetails]:
        """根据实例ID列表获取玩家拥有的武将（包含详细信息）"""
        if not instance_ids:
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 使用JOIN查询合并两个表的数据
        # 使用参数化查询防止SQL注入
        placeholders = ','.join('?' for _ in instance_ids)
        sql = f"""
            SELECT
                ug.instance_id,
                ug.user_id,
                ug.general_id,
                ug.level,
                ug.exp,
                ug.created_at,
                g.name,
                g.rarity,
                g.camp,
                g.wu_li,
                g.zhi_li,
                g.tong_shuai,
                g.su_du,
                g.skill_desc
            FROM user_generals ug
            JOIN generals g ON ug.general_id = g.general_id
            WHERE ug.user_id = ? AND ug.instance_id IN ({placeholders})
        """
        
        params = [user_id] + instance_ids
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        detailed_generals = []
        for row in rows:
            created_at = datetime.fromisoformat(row[5]) if row[5] else datetime.now()
            detailed_generals.append(UserGeneralDetails(
                instance_id=row[0],
                user_id=row[1],
                general_id=row[2],
                level=row[3],
                exp=row[4],
                created_at=created_at,
                name=row[6],
                rarity=row[7],
                camp=row[8],
                wu_li=row[9],
                zhi_li=row[10],
                tong_shuai=row[11],
                su_du=row[12],
                skill_desc=row[13]
            ))
            
        return detailed_generals
    
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

    def check_user_has_general(self, user_id: str, general_id: int) -> bool:
        """检查玩家是否已拥有特定武将"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM user_generals WHERE user_id = ? AND general_id = ?",
                (user_id, general_id)
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()
    
    def get_user_general_count(self, user_id: str) -> int:
        """获取玩家武将数量"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM user_generals WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_random_general_by_rarity_pool(self, luck_bonus: float = 0.0) -> Optional[General]:
        """
        根据稀有度概率池随机获取武将
        :param luck_bonus: 幸运加成，一个0到1之间的浮点数，会提升高稀有度的概率
        """
        all_generals = self.get_all_generals()
        if not all_generals:
            return None

        # 基础概率
        base_probs = {1: 0.0, 2: 0.70, 3: 0.20, 4: 0.09, 5: 0.01}
        
        # 重新分配概率
        # 将低稀有度的部分概率按比例加到高稀有度上
        bonus_to_distribute = base_probs[2] * luck_bonus
        base_probs[2] -= bonus_to_distribute
        
        # 按权重(3:2:1)分配给3,4,5星
        total_weight = 3 + 2 + 1
        base_probs[3] += bonus_to_distribute * (3 / total_weight)
        base_probs[4] += bonus_to_distribute * (2 / total_weight)
        base_probs[5] += bonus_to_distribute * (1 / total_weight)

        # 构建概率池
        rarities = list(base_probs.keys())
        probabilities = list(base_probs.values())
        
        while True:
            # 根据新的概率分布选择稀有度
            selected_rarity = random.choices(rarities, weights=probabilities, k=1)[0]
            
            generals_in_rarity = [g for g in all_generals if g.rarity == selected_rarity]
            
            if generals_in_rarity:
                return random.choice(generals_in_rarity)
            # 如果抽到的稀有度没有武将，则重新抽取

    def get_average_combat_power_for_level(self, level: int) -> float:
        """
        计算指定等级下所有武将的理论平均战力。
        **此逻辑必须与 UserGeneralDetails 中的战力计算保持一致。**
        """
        all_generals = self.get_all_generals()
        if not all_generals:
            return 100.0 # 返回一个合理的默认值

        total_combat_power = 0
        for g in all_generals:
            # 1. 计算等级带来的属性成长 (逻辑复制自 UserGeneralDetails._calculate_upgraded_stat)
            def _calculate_upgraded_stat(base_stat: int) -> int:
                growth_per_level = base_stat * 0.02
                total_growth = growth_per_level * (level - 1)
                return round(base_stat + total_growth)

            wu_li = _calculate_upgraded_stat(g.wu_li)
            zhi_li = _calculate_upgraded_stat(g.zhi_li)
            tong_shuai = _calculate_upgraded_stat(g.tong_shuai)
            su_du = _calculate_upgraded_stat(g.su_du)

            # 2. 计算战力 (逻辑复制自 UserGeneralDetails.combat_power)
            combat_power = wu_li * 1.2 + zhi_li * 0.8 + tong_shuai * 1.0 + su_du * 0.5
            total_combat_power += combat_power
            
        return total_combat_power / len(all_generals) if all_generals else 100.0

    def get_highest_level_general_by_user(self, user_id: str) -> Optional[UserGeneral]:
        """获取用户拥有的最高等级的武将"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT instance_id, user_id, general_id, level, exp, created_at FROM user_generals WHERE user_id = ? ORDER BY level DESC, exp DESC LIMIT 1",
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            created_at = datetime.fromisoformat(row[5]) if row[5] else datetime.now()
            return UserGeneral(row[0], row[1], row[2], row[3], row[4], created_at)
        
        return None

    def add_battle_log(self, user_id: str, log_type: str, log_details: str, user_general_instance_id: int = None, enemy_name: str = None, is_win: bool = None, rewards: str = None):
        """添加战斗或冒险日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO battle_logs (user_id, log_type, log_details, user_general_instance_id, enemy_name, is_win, rewards, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, log_type, log_details, user_general_instance_id, enemy_name, is_win, rewards, datetime.now().isoformat())
            )
            conn.commit()
        finally:
            conn.close()

    def get_battle_logs_since(self, user_id: str, start_time: datetime, log_type: Optional[str] = None) -> List[BattleLog]:
        """获取指定时间之后的所有战斗日志，可按类型筛选"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            sql = "SELECT * FROM battle_logs WHERE user_id = ? AND created_at >= ?"
            params = [user_id, start_time.isoformat()]

            if log_type:
                sql += " AND log_type = ?"
                params.append(log_type)

            sql += " ORDER BY created_at DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            logs = []
            for row in rows:
                logs.append(BattleLog(
                    log_id=row['log_id'],
                    user_id=row['user_id'],
                    user_general_instance_id=row['user_general_instance_id'],
                    enemy_name=row['enemy_name'],
                    is_win=row['is_win'],
                    log_details=row['log_details'],
                    rewards=row['rewards'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    log_type=row['log_type']
                ))
            return logs
        finally:
            conn.close()
