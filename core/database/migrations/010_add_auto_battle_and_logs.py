import sqlite3
from astrbot.api import logger

def up(cursor: sqlite3.Cursor):
    """
    应用此迁移：为用户添加自动战斗设置，并创建每日战斗日志表。
    """
    logger.debug("正在执行 010_add_auto_battle_and_logs: 添加自动战斗字段和日志表...")

    # 1. 向 users 表添加新字段
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN auto_adventure_enabled INTEGER DEFAULT 0")
        logger.info("成功向 'users' 表添加 'auto_adventure_enabled' 字段。")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise e
        logger.warning("字段 'auto_adventure_enabled' 已存在，跳过添加。")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN auto_dungeon_id INTEGER DEFAULT NULL")
        logger.info("成功向 'users' 表添加 'auto_dungeon_id' 字段。")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise e
        logger.warning("字段 'auto_dungeon_id' 已存在，跳过添加。")

    # 2. 创建每日战斗日志表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_battle_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            log_type TEXT NOT NULL CHECK (log_type IN ('adventure', 'dungeon')),
            description TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    logger.info("成功创建或确认 'daily_battle_logs' 表。")

    # 3. 为新表创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_battle_logs_user_time ON daily_battle_logs(user_id, timestamp)")
    logger.info("成功为 'daily_battle_logs' 表创建索引。")

    logger.info("010_add_auto_battle_and_logs: 迁移完成。")

def down(cursor: sqlite3.Cursor):
    """
    回滚此迁移：移除自动战斗设置和每日战斗日志表。
    """
    logger.debug("正在回滚 010_add_auto_battle_and_logs: 移除自动战斗字段和日志表...")

    # 1. 移除 users 表中的字段 (SQLite 不直接支持 DROP COLUMN，需要重建表)
    # 这是一个复杂的降级，暂时只移除表
    
    # 2. 移除每日战斗日志表
    cursor.execute("DROP TABLE IF EXISTS daily_battle_logs")
    logger.info("成功移除 'daily_battle_logs' 表。")

    logger.info("010_add_auto_battle_and_logs: 回滚完成。")
