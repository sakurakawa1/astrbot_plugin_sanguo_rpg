# -*- coding: utf-8 -*-
# @Time    : 2025/08/02
# @Author  : Cline
# @File    : 017_add_instance_properties_to_inventory.py
# @Software: AstrBot
# @Description: 为背包物品添加实例属性，以支持动态物品

def up(c):
    """
    为 user_inventory 表添加一个列来存储每个物品实例的动态属性。
    使用 TEXT 类型来存储 JSON 字符串。
    """
    try:
        c.execute("""
            ALTER TABLE user_inventory
            ADD COLUMN instance_properties TEXT;
        """)
    except Exception as e:
        # 在迁移过程中，如果列已存在，可能会抛出异常，这是正常的
        # 我们可以打印一个信息，而不是让迁移失败
        print(f"Info: Column 'instance_properties' might already exist. Error: {e}")


def down(c):
    """
    降级操作，从 user_inventory 表中移除 instance_properties 列。
    采用安全的方式：创建备份 -> 复制数据 -> 删除旧表 -> 重命名备份。
    """
    c.execute('PRAGMA foreign_keys=off;')
    c.execute('BEGIN TRANSACTION;')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_inventory_backup (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (item_id) REFERENCES items (id)
        );
    ''')
    
    c.execute('''
        INSERT INTO user_inventory_backup (id, user_id, item_id, quantity)
        SELECT id, user_id, item_id, quantity FROM user_inventory;
    ''')
    
    c.execute('DROP TABLE user_inventory;')
    
    c.execute('ALTER TABLE user_inventory_backup RENAME TO user_inventory;')
    
    c.execute('CREATE INDEX IF NOT EXISTS idx_user_inventory_user_id ON user_inventory (user_id);')

    c.execute('COMMIT;')
    c.execute('PRAGMA foreign_keys=on;')
