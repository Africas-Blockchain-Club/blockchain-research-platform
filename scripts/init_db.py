"""Run once per fresh environment to create the payments and reports tables.

    python scripts/init_db.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import init_db, get_engine

if __name__ == "__main__":
    init_db()
    print(f"Tables created (or already existed) at {get_engine().url}")
