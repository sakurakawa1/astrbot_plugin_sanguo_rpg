import json

def up(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dungeons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        recommended_level INTEGER NOT NULL,
        entry_fee INTEGER NOT NULL DEFAULT 0,
        rewards TEXT
    )
    """)

    # Define rewards as dictionaries
    rewards_data = {
        "黄巾前哨": {"exp": 20, "coins": 50, "reputation": 1},
        "汜水关": {"exp": 30, "coins": 80, "reputation": 2},
        "虎牢关": {"exp": 50, "coins": 120, "reputation": 3},
        "北海救援": {"exp": 70, "coins": 150, "reputation": 4},
        "徐州之战": {"exp": 90, "coins": 200, "reputation": 5},
        "官渡前哨": {"exp": 120, "coins": 250, "reputation": 7},
        "长坂坡": {"exp": 150, "coins": 300, "reputation": 8},
        "赤壁疑兵": {"exp": 180, "coins": 350, "reputation": 10},
        "合肥之战": {"exp": 220, "coins": 400, "reputation": 12},
        "汉中定军山": {"exp": 250, "coins": 500, "reputation": 15}
    }

    dungeons_data = [
        # name, description, recommended_level, entry_fee, rewards (as JSON string)
        ('黄巾前哨', '遭遇零散的黄巾军，小试牛刀。', 1, 10, json.dumps(rewards_data["黄巾前哨"])),
        ('汜水关', '联合军在此受阻，需要一位英雄打开局面。', 3, 20, json.dumps(rewards_data["汜水关"])),
        ('虎牢关', '吕布之威震慑天下，挑战他的先锋部队。', 5, 30, json.dumps(rewards_data["虎牢关"])),
        ('北海救援', '孔融被围，你需要突破敌军的封锁。', 7, 40, json.dumps(rewards_data["北海救援"])),
        ('徐州之战', '曹操与陶谦的纷争，战场局势复杂。', 9, 50, json.dumps(rewards_data["徐州之战"])),
        ('官渡前哨', '袁绍大军压境，在官渡外围展开激战。', 11, 70, json.dumps(rewards_data["官渡前哨"])),
        ('长坂坡', '在曹军的追击下，保护百姓，杀出重围。', 13, 90, json.dumps(rewards_data["长坂坡"])),
        ('赤壁疑兵', '草船借箭，利用大雾和智谋扰乱曹军。', 15, 110, json.dumps(rewards_data["赤壁疑兵"])),
        ('合肥之战', '张辽威震逍遥津，你需要面对精锐的魏军。', 17, 130, json.dumps(rewards_data["合肥之战"])),
        ('汉中定军山', '老将黄忠刀劈夏侯渊，争夺汉中的关键一役。', 20, 150, json.dumps(rewards_data["汉中定军山"]))
    ]

    cursor.executemany(
        "INSERT INTO dungeons (name, description, recommended_level, entry_fee, rewards) VALUES (?, ?, ?, ?, ?)",
        dungeons_data
    )

def down(cursor):
    cursor.execute("DROP TABLE IF EXISTS dungeons")
