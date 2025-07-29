# -*- coding: utf-8 -*-
# @Time    : 2025/07/28
# @Author  : Cline
# @File    : migration.py
# @Software: AstrBot
# @Description: 数据库迁移管理

import sqlite3
import os
import importlib.util
import sys
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
                # 使用 importlib 动态导入迁移模块，以支持数字开头的模块名
                spec = importlib.util.spec_from_file_location(
                    migration_name, os.path.join(migrations_path, migration_file)
                )
                migration_module = importlib.util.module_from_spec(spec)
                sys.modules[migration_name] = migration_module
                spec.loader.exec_module(migration_module)

                with conn:
                    cursor = conn.cursor()
                    
                    # 执行 upgrade 函数
                    if hasattr(migration_module, 'upgrade'):
                        migration_module.upgrade(cursor)
                    else:
                        logger.warning(f"迁移 {migration_name} 中未找到 upgrade 函数。")

                    # 记录迁移版本
                    cursor.execute("INSERT INTO schema_migrations (version) VALUES (?)", (migration_name,))
                    
                logger.info(f"成功应用迁移: {migration_name}")
            except Exception as e:
                logger.error(f"应用迁移 {migration_name} 时出错: {e}")
                conn.close()
                raise
    
    conn.close()
    logger.info("数据库迁移检查完成。")
