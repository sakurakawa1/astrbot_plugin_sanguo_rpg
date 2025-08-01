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

def run_migrations(db_path: str, migrations_path: str, force: bool = False):
    """
    运行所有数据库迁移。
    :param db_path: 数据库文件路径。
    :param migrations_path: 迁移脚本所在目录。
    :param force: 如果为 True，则强制运行所有迁移，无论它们是否已被应用。
    """
    if force:
        logger.info("正在强制执行所有数据库迁移...")
    else:
        logger.info("正在检查并运行数据库迁移...")
        
    conn = sqlite3.connect(db_path)
    applied_migrations = _get_applied_migrations(conn)
    
    migration_files = sorted([f for f in os.listdir(migrations_path) if f.endswith('.py') and f != '__init__.py'])
    
    for migration_file in migration_files:
        migration_name = migration_file.split('.')[0]
        
        if force or migration_name not in applied_migrations:
            try:
                spec = importlib.util.spec_from_file_location(
                    migration_name, os.path.join(migrations_path, migration_file)
                )
                migration_module = importlib.util.module_from_spec(spec)
                sys.modules[migration_name] = migration_module
                spec.loader.exec_module(migration_module)

                with conn:
                    cursor = conn.cursor()
                    
                    if hasattr(migration_module, 'upgrade'):
                        migration_module.upgrade(cursor)
                    else:
                        logger.warning(f"迁移 {migration_name} 中未找到 'upgrade' 函数。")

                    # 使用 INSERT OR IGNORE 避免在强制执行时出错
                    cursor.execute("INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)", (migration_name,))
                
                if migration_name not in applied_migrations:
                    logger.info(f"成功应用迁移: {migration_name}")
                elif force:
                    logger.info(f"已强制重新应用迁移: {migration_name}")

            except Exception as e:
                logger.error(f"应用迁移 {migration_name} 时出错: {e}", exc_info=True)
                conn.close()
                raise
    
    conn.close()
    logger.info("数据库迁移检查完成。")
