# -*- coding: utf-8 -*-
# @Time    : 2025/08/01
# @Author  : Cline
# @File    : 005_add_level_to_users.py
# @Software: AstrBot
# @Description: Add level to users table

def upgrade(db_conn):
    db_conn.execute("ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1")

def downgrade(db_conn):
    # SQLite doesn't easily support dropping columns.
    # A more complex migration would be needed to recreate the table without the column.
    pass
