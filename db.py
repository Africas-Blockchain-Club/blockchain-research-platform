"""
Payment and report persistence.

DATABASE_URL drives the backend: a real Postgres URL in production (Fly Postgres),
or left unset for a local SQLite file during development. Same schema, same
functions, either way - only the connection string changes.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    TIMESTAMP,
    Table,
    Text,
    create_engine,
    func,
    insert,
    select,
    update,
)

load_dotenv()

_ROOT = Path(__file__).resolve().parent
_DEFAULT_SQLITE_URL = f"sqlite:///{_ROOT / 'local_dev.db'}"

metadata = MetaData()

_PK = BigInteger().with_variant(Integer, "sqlite")  # SQLite only autoincrements a plain INTEGER PK

payments = Table(
    "payments",
    metadata,
    Column("id", _PK, primary_key=True, autoincrement=True),
    Column("request_id", String, nullable=False),
    Column("token_symbol", String, nullable=False),
    Column("payer_address", String, nullable=False),
    Column("recipient_address", String, nullable=False),
    Column("chain_id", Integer, nullable=False),
    Column("asset_contract", String, nullable=False),
    Column("asset_symbol", String, nullable=False),
    Column("amount_atomic", Numeric(38, 0), nullable=False),
    Column("amount_decimal", Numeric(20, 6), nullable=False),
    Column("tx_hash", String, nullable=False, unique=True),
    Column("status", String, nullable=False, server_default="pending"),
    Column("confirmations", Integer, nullable=False, server_default="0"),
    Column("failure_reason", Text),
    Column("payer_email", String),
    # Which check confirmed this payment: "rpc", "etherscan_fallback", or "blockscout_fallback".
    # Lets a future drift in any verification path show up in the data.
    Column("verification_method", String),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
    Column("verified_at", TIMESTAMP(timezone=True)),
)
Index("idx_payments_token_status", payments.c.token_symbol, payments.c.status)

reports = Table(
    "reports",
    metadata,
    Column("id", _PK, primary_key=True, autoincrement=True),
    Column("token_symbol", String, nullable=False),
    Column("payment_id", BigInteger, ForeignKey("payments.id"), nullable=True),
    Column("model", String, nullable=False),
    Column("score", Integer),
    Column("verdict", String),
    Column("screenshot_path", String),
    Column("markdown", Text, nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
)
Index("idx_reports_token_created", reports.c.token_symbol, reports.c.created_at.desc())

_engine = None


def get_engine():
    """Lazily creates and caches a SQLAlchemy engine from DATABASE_URL, falling
    back to a local SQLite file when unset (matches .env.example's empty default)."""
    global _engine
    if _engine is None:
        database_url = os.getenv("DATABASE_URL") or _DEFAULT_SQLITE_URL
        _engine = create_engine(database_url)
    return _engine


def init_db():
    """Creates the payments and reports tables if they do not already exist."""
    metadata.create_all(get_engine())


def record_payment_attempt(
    request_id,
    token_symbol,
    payer_address,
    recipient_address,
    chain_id,
    asset_contract,
    asset_symbol,
    amount_atomic,
    amount_decimal,
    tx_hash,
    payer_email=None,
    verification_method=None,
):
    """Inserts a new payments row with status='pending'. Returns the new payment id.
    Raises sqlalchemy.exc.IntegrityError if tx_hash already exists - this is the
    replay guard; callers must catch it and treat the payment as already used."""
    with get_engine().begin() as conn:
        result = conn.execute(
            insert(payments).values(
                request_id=request_id,
                token_symbol=token_symbol,
                payer_address=payer_address,
                recipient_address=recipient_address,
                chain_id=chain_id,
                asset_contract=asset_contract,
                asset_symbol=asset_symbol,
                amount_atomic=amount_atomic,
                amount_decimal=amount_decimal,
                tx_hash=tx_hash,
                payer_email=payer_email,
                verification_method=verification_method,
            )
        )
        return result.inserted_primary_key[0]


def mark_payment_confirmed(payment_id, confirmations):
    """Sets status='confirmed', verified_at=now(), confirmations=N."""
    with get_engine().begin() as conn:
        conn.execute(
            update(payments)
            .where(payments.c.id == payment_id)
            .values(status="confirmed", confirmations=confirmations, verified_at=func.now())
        )


def mark_payment_failed(payment_id, reason):
    """Sets status='failed', failure_reason=reason."""
    with get_engine().begin() as conn:
        conn.execute(
            update(payments).where(payments.c.id == payment_id).values(status="failed", failure_reason=reason)
        )


def get_payment_by_tx_hash(tx_hash):
    """Looks up an existing payment row by tx_hash. Returns a dict or None."""
    with get_engine().connect() as conn:
        row = conn.execute(select(payments).where(payments.c.tx_hash == tx_hash)).mappings().first()
        return dict(row) if row else None


def save_report(token_symbol, payment_id, model, score, verdict, screenshot_path, markdown):
    """Inserts a row into reports. Returns the new report id."""
    with get_engine().begin() as conn:
        result = conn.execute(
            insert(reports).values(
                token_symbol=token_symbol,
                payment_id=payment_id,
                model=model,
                score=score,
                verdict=verdict,
                screenshot_path=screenshot_path,
                markdown=markdown,
            )
        )
        return result.inserted_primary_key[0]


def get_latest_report(token_symbol):
    """Returns the most recent reports row for a token, or None."""
    with get_engine().connect() as conn:
        row = (
            conn.execute(
                select(reports)
                .where(reports.c.token_symbol == token_symbol)
                .order_by(reports.c.created_at.desc())
                .limit(1)
            )
            .mappings()
            .first()
        )
        return dict(row) if row else None


def get_payments_by_payer(payer_address, limit=20):
    """Returns confirmed payments made by a wallet address, newest first.
    Backs the Session 3 wallet sign-in: your address is your purchase history."""
    with get_engine().connect() as conn:
        rows = (
            conn.execute(
                select(payments)
                .where(payments.c.payer_address == payer_address.lower())
                .where(payments.c.status == "confirmed")
                .order_by(payments.c.created_at.desc())
                .limit(limit)
            )
            .mappings()
            .all()
        )
        return [dict(r) for r in rows]


def list_recent_reports(limit=10):
    """Returns the N most recent reports across all tokens, newest first."""
    with get_engine().connect() as conn:
        rows = conn.execute(select(reports).order_by(reports.c.created_at.desc()).limit(limit)).mappings().all()
        return [dict(r) for r in rows]
