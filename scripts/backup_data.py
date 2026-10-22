"""
Pack everything on the volume that cannot be rebuilt into one archive, for the
nightly off-site backup (.github/workflows/backup.yml).

  python scripts/backup_data.py /tmp/brp-backup.tar.gz     on the machine: write the archive
  python scripts/backup_data.py --verify brp-backup.tar.gz  anywhere: prove it restores

What is kept: the database (payments, report history, searches), the saved
reports (paid AI write-ups cannot be regenerated for free) and the AI usage
log. What is not: the built site, the PDF cache and the network snapshots,
which the platform rebuilds by itself. The database is copied with SQLite's
own backup method, which is consistent even while the app is writing to it.
"""
import argparse
import sqlite3
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DATA_DIR, REPORTS_DIR  # noqa: E402

DB_NAME = "local_dev.db"


def pack(out_path):
    out_path = Path(out_path)
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / DB_NAME
        source = sqlite3.connect(DATA_DIR / DB_NAME, timeout=30)
        target = sqlite3.connect(copy)
        with target:
            source.backup(target)
        source.close()
        target.close()
        with tarfile.open(out_path, "w:gz") as tar:
            tar.add(copy, arcname=DB_NAME)
            if REPORTS_DIR.exists():
                tar.add(REPORTS_DIR, arcname="reports")
            usage = DATA_DIR / "usage_log.txt"
            if usage.exists():
                tar.add(usage, arcname="usage_log.txt")
    print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes)")


def verify(archive):
    """Restore into a temporary folder and check the database is whole and has
    its tables. Exits non-zero on any problem, so the workflow fails loudly."""
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(tmp, filter="data")
        db = sqlite3.connect(Path(tmp) / DB_NAME)
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        missing = {"payments", "reports"} - tables
        counts = {t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in sorted(tables)}  # nosec B608
        reports = len(list((Path(tmp) / "reports").glob("*_research_report.md")))
        db.close()
    print(f"Integrity: {integrity}; rows: {counts}; saved reports: {reports}")
    if integrity != "ok" or missing:
        sys.exit(f"Backup does not restore cleanly (integrity {integrity}, missing tables {sorted(missing)})")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("archive")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    verify(args.archive) if args.verify else pack(args.archive)


if __name__ == "__main__":
    main()
