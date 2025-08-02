# -*- coding: utf-8 -*-
import os
import sys

# Add plugin root to path to allow for relative imports
plugin_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(plugin_root, '..')))
sys.path.append(os.path.abspath(os.path.join(plugin_root, '..', 'AstrBot')))

from astrbot_plugin_sanguo_rpg.core.database.migration import run_migrations

def main():
    """
    Runs the database migrations.
    """
    plugin_root_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(plugin_root_dir, "data"))
    db_path = os.path.join(data_dir, "sanguo_rpg.db")
    migrations_path = os.path.join(plugin_root_dir, "core", "database", "migrations")

    print(f"Database path: {db_path}")
    print(f"Migrations path: {migrations_path}")

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")

    try:
        run_migrations(db_path, migrations_path)
        print("✅ Database migrations completed successfully.")
    except Exception as e:
        print(f"❌ An error occurred during migration: {e}")

if __name__ == "__main__":
    main()
