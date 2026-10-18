"""
Recent payments and whether each one received its write-up. Read-only.

On the live machine:
  fly ssh console --app blockchain-research-platform -C "sh -c 'cd /app && python scripts/payments_report.py'"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select  # noqa: E402

import db  # noqa: E402
import payment_verifier  # noqa: E402


def main(limit=20):
    delivered = (
        select(func.count()).select_from(db.reports).where(db.reports.c.payment_id == db.payments.c.id)
        .scalar_subquery()
    )
    query = (
        select(db.payments, delivered.label("reports"))
        .order_by(db.payments.c.created_at.desc())
        .limit(limit)
    )
    with db.get_engine().connect() as conn:
        rows = conn.execute(query).mappings().all()
    if not rows:
        print("No payments recorded yet.")
        return 0
    missing = 0
    for row in rows:
        network = payment_verifier.NETWORKS.get(row["chain_id"], {"name": str(row["chain_id"]), "explorer": ""})
        flag = "OK     " if row["reports"] else "NO REPORT"
        missing += 0 if row["reports"] else 1
        print(f"{flag} {row['created_at']:%Y-%m-%d %H:%M} {row['token_symbol']:<8} {row['amount_decimal']} "
              f"{row['asset_symbol']} on {network['name']}  {network['explorer']}/tx/{row['tx_hash']}")
    print(f"\n{len(rows)} payment(s) shown; {missing} without a delivered write-up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
