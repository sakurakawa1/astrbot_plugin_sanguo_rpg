# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : migration.py
# @Software: AstrBot
# @Description: 数据库迁移管理

import sqlite3
import os
from astrbot.api import logger

def _get_applied_migrations(conn):
    """获取已应用的迁移版本"""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT version FROM schema_migrations")
        return {row[0] for row in cursor.fetchall()}
    except sqlite3.OperationalError:
        # 如果 schema_migrations 表不存在，则创建一个
        cursor.execute("""
            CREATE TABLE schema_migrations (
                version TEXT PRIMARY KEY NOT NULL
            )
        """)
        return set()

def run_migrations(db_path: str, migrations_path: str):
    """运行所有待处理的数据库迁移"""
    logger.info("正在检查并运行数据库迁移...")
    conn = sqlite3.connect(db_path)
    applied_migrations = _get_applied_migrations(conn)
    
    migration_files = sorted([f for f in os.listdir(migrations_path) if f.endswith('.py') and f != '__init__.py'])
    
    for migration_file in migration_files:
        migration_name = migration_file.split('.')[0]
        if migration_name not in applied_migrations:
            try:
                # 动态导入迁移模块
                module_name = f"astrbot_plugin_sanguo_rpg.core.database.migrations.{migration_name}"
                migration_module = __import__(module_name, fromlist=['upgrade'])
                
                with conn:
                    cursor = conn.cursor()
                    
                    # 执行 upgrade 函数
                    migration_module.upgrade(cursor)
                    
                    # 记录迁移版本
                    cursor.execute("INSERT INTO schema_migrations (version) VALUES (?)", (migration_name,))
                    
                logger.info(f"成功应用迁移: {migration_name}")
            except Exception as e:
                logger.error(f"应用迁移 {migration_name} 时出错: {e}")
                conn.close()
                raise
    
    conn.close()
    logger.info("数据库迁移检查完成。")
