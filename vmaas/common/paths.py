"""
Commonly used constant paths (sql scripts etc.)
"""
from pathlib import Path

VMAAS_DIR = Path(__file__).resolve().parent.parent.parent
DB_UPGRADES_PATH = VMAAS_DIR.joinpath("database", "upgrade_scripts")
DB_CREATE_SQL_PATH = VMAAS_DIR.joinpath("database", "vmaas_db_postgresql.sql")
