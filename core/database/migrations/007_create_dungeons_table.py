import json

def upgrade(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dungeons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        recommended_level INTEGER NOT NULL,
        enemy_strength_min REAL NOT NULL,
        enemy_strength_max REAL NOT NULL,
        rewards TEXT
    )
    """)

    # Define rewards as dictionaries
    rewards_data = {
        "黄巾前哨": {"exp": 20, "coins": 50, "yuanbao": 10},
        "汜水关": {"exp": 30, "coins": 80, "yuanbao": 12},
        "虎牢关": {"exp": 50, "coins": 120, "yuanbao": 15},
        "北海救援": {"exp": 70, "coins": 150, "yuanbao": 18},
        "徐州之战": {"exp": 90, "coins": 200, "yuanbao": 22},
        "官渡前哨": {"exp": 120, "coins": 250, "yuanbao": 26},
        "长坂坡": {"exp": 150, "coins": 300, "yuanbao": 30},
        "赤壁疑兵": {"exp": 180, "coins": 350, "yuanbao": 35},
        "合肥之战": {"exp": 220, "coins": 400, "yuanbao": 40},
        "汉中定军山": {"exp": 250, "coins": 500, "yuanbao": 50}
    }

    dungeons_data = [
        # name, description, recommended_level, enemy_strength_min, enemy_strength_max, rewards (as JSON string)
        ('黄巾前哨', '遭遇零散的黄巾军，小试牛刀。', 1, 1.0, 1.5, json.dumps(rewards_data["黄巾前哨"])),
        ('汜水关', '联合军在此受阻，需要一位英雄打开局面。', 3, 1.2, 1.8, json.dumps(rewards_data["汜水关"])),
        ('虎牢关', '吕布之威震慑天下，挑战他的先锋部队。', 5, 1.5, 2.0, json.dumps(rewards_data["虎牢关"])),
        ('北海救援', '孔融被围，你需要突破敌军的封锁。', 7, 1.5, 2.2, json.dumps(rewards_data["北海救援"])),
        ('徐州之战', '曹操与陶谦的纷争，战场局势复杂。', 9, 1.8, 2.5, json.dumps(rewards_data["徐州之战"])),
        ('官渡前哨', '袁绍大军压境，在官渡外围展开激战。', 11, 2.0, 2.8, json.dumps(rewards_data["官渡前哨"])),
        ('长坂坡', '在曹军的追击下，保护百姓，杀出重围。', 13, 2.2, 3.0, json.dumps(rewards_data["长坂坡"])),
        ('赤壁疑兵', '草船借箭，利用大雾和智谋扰乱曹军。', 15, 2.5, 3.2, json.dumps(rewards_data["赤壁疑兵"])),
        ('合肥之战', '张辽威震逍遥津，你需要面对精锐的魏军。', 17, 2.8, 3.5, json.dumps(rewards_data["合肥之战"])),
        ('汉中定军山', '老将黄忠刀劈夏侯渊，争夺汉中的关键一役。', 20, 3.0, 4.0, json.dumps(rewards_data["汉中定军山"]))
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO dungeons (name, description, recommended_level, enemy_strength_min, enemy_strength_max, rewards) VALUES (?, ?, ?, ?, ?, ?)",
        dungeons_data
    )

def downgrade(cursor):
    cursor.execute("DROP TABLE IF EXISTS dungeons")
