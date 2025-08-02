# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 019_add_lord_exp_to_users.py
# @Software: AstrBot
# @Description: Add lord_exp to users table

import logging

# 设置日志记录
logger = logging.getLogger(__name__)

def up(cursor):
    """
    Adds a lord_exp column to the users table.
    """
    try:
        # 检查列是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'lord_exp' not in columns:
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN lord_exp INTEGER NOT NULL DEFAULT 0
            """)
            logger.info("Column 'lord_exp' added to 'users' table.")
        else:
            logger.info("Column 'lord_exp' already exists in 'users' table.")
    except Exception as e:
        logger.error(f"Error applying migration: {e}")
        raise

def down(cursor):
    """
    Removes the lord_exp column from the users table.
    """
    try:
        # SQLite doesn't directly support DROP COLUMN in older versions.
        # A common workaround is to recreate the table, but this is complex and risky for a rollback.
        # For this case, we'll assume the operation is not easily reversible in a simple script.
        # A more robust solution would involve creating a new table and copying data.
        # However, given the context, we will log the action.
        logger.warning("Rollback for 'add_lord_exp_to_users' is not implemented to avoid data loss risk.")
        # If you are sure about the rollback, you would need to:
        # 1. Create a new table without the 'lord_exp' column.
        # 2. Copy all data from the old table to the new one.
        # 3. Drop the old table.
        # 4. Rename the new table to 'users'.
        # This is intentionally left blank to prevent accidental data loss.
        pass
    except Exception as e:
        logger.error(f"Error rolling back migration: {e}")
        raise
