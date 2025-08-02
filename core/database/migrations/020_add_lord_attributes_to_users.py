# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 020_add_lord_attributes_to_users.py
# @Software: AstrBot
# @Description: Add lord attributes to users table

import logging

logger = logging.getLogger(__name__)

def up(cursor):
    """
    Add lord_level, health, attack, defense columns to the users table.
    """
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]

        if 'lord_level' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN lord_level INTEGER NOT NULL DEFAULT 1")
            logger.info("Column 'lord_level' added to 'users' table.")
        else:
            logger.info("Column 'lord_level' already exists in 'users' table.")

        if 'health' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN health REAL NOT NULL DEFAULT 100.0")
            logger.info("Column 'health' added to 'users' table.")
        else:
            logger.info("Column 'health' already exists in 'users' table.")

        if 'attack' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN attack REAL NOT NULL DEFAULT 10.0")
            logger.info("Column 'attack' added to 'users' table.")
        else:
            logger.info("Column 'attack' already exists in 'users' table.")

        if 'defense' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN defense REAL NOT NULL DEFAULT 5.0")
            logger.info("Column 'defense' added to 'users' table.")
        else:
            logger.info("Column 'defense' already exists in 'users' table.")

    except Exception as e:
        logger.error(f"Error applying migration: {e}")
        raise

def down(cursor):
    """
    Remove lord_level, health, attack, defense columns from the users table.
    """
    logger.warning("Rollback for 'add_lord_attributes_to_users' is not fully implemented to avoid data loss risk.")
    # As with other migrations, dropping columns in SQLite is complex.
    # This is intentionally left blank.
    pass
