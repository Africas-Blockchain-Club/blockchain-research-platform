"""
Email delivery adapter.

The single boundary for SMTP in this codebase: nothing else imports smtplib.
Configuration comes entirely from .env (SMTP_HOST, SMTP_PORT, SMTP_USER,
SMTP_PASSWORD). The off state is explicit: when any of those are missing,
is_configured() returns False and send_report_receipt() raises
EmailNotConfiguredError rather than failing quietly. Swapping providers
(Gmail SMTP to SES, Postmark, or anything else that speaks SMTP) is a
config change only.
"""
import logging
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

from config import SETTINGS
from data_science.compliance import SHORT_DISCLAIMER

log = logging.getLogger(__name__)

load_dotenv()


class EmailNotConfiguredError(Exception):
    """SMTP settings are absent from the environment. The defined off state."""


class EmailDeliveryError(Exception):
    """SMTP settings are present but the send failed (auth, network, rejection)."""


_REQUIRED_VARS = ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD")


def _config():
    return {name: os.getenv(name, "").strip() for name in _REQUIRED_VARS}


def is_configured():
    """True when every SMTP variable is set. Callers use this to decide
    whether to offer email delivery at all."""
    return all(_config().values())


def send_report_receipt(payer_email, token, report_markdown, receipt):
    """Sends the finished research report to the payer with a payment receipt.

    payer_email:      destination address.
    token:            token symbol, e.g. "SOL".
    report_markdown:  the full saved report, attached as a .md file.
    receipt:          dict with tx_hash, amount_decimal, chain_id, flagged, clear, no_data.

    Raises EmailNotConfiguredError when SMTP is not set up (the off state)
    and EmailDeliveryError on any send failure. Never fails silently; the
    caller decides how to surface the error.
    """
    cfg = _config()
    if not all(cfg.values()):
        missing = [name for name, value in cfg.items() if not value]
        raise EmailNotConfiguredError(
            f"Email is switched off: {', '.join(missing)} not set in .env"
        )

    token = token.upper()
    msg = EmailMessage()
    msg["Subject"] = f"{token} research report and payment receipt"
    msg["From"] = cfg["SMTP_USER"]
    msg["To"] = payer_email
    msg.set_content(
        f"Your {token} research report is attached.\n"
        f"\n"
        f"Payment receipt{' (testnet)' if receipt.get('testnet') else ''}\n"
        f"-------------------------\n"
        f"Token researched: {token}\n"
        f"Amount paid:      {receipt.get('amount_decimal')} {receipt.get('asset', 'USDC')}\n"
        f"Network:          {receipt.get('chain_name')} (chain id {receipt.get('chain_id')})\n"
        f"Transaction hash: {receipt.get('tx_hash')}\n"
        f"\n"
        + (
            "Test USDC has no real-world value. The payment demonstrates on-chain\n"
            "payments for learning purposes.\n"
            if receipt.get("testnet") else
            "Blockchain payments cannot be reversed. Keep this receipt.\n"
        )
        + f"You paid for the computing cost of an AI-written explanation, not for advice.\n"
        f"\n"
        f"Risk checks: {receipt.get('flagged')} flagged, {receipt.get('clear')} clear, "
        f"{receipt.get('no_data')} with no data.\n"
        f"\n"
        f"{SHORT_DISCLAIMER}\n"
        f"\n"
        f"The full report is attached as a PDF, and as markdown for any text editor.\n"
        f"\n"
        f"{SETTINGS.brand_name} - {SETTINGS.app_name}\n"
    )
    from tools.pdf_export import markdown_to_pdf

    pdf, _error = markdown_to_pdf(report_markdown)
    if pdf:
        msg.add_attachment(pdf, maintype="application", subtype="pdf", filename=f"{token}_research_report.pdf")
    msg.add_attachment(
        report_markdown.encode("utf-8"),
        maintype="text",
        subtype="markdown",
        filename=f"{token}_research_report.md",
    )

    try:
        with smtplib.SMTP(cfg["SMTP_HOST"], int(cfg["SMTP_PORT"]), timeout=30) as server:
            server.starttls()
            server.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
            server.send_message(msg)
    except (smtplib.SMTPException, OSError, ValueError) as e:
        raise EmailDeliveryError(f"Report email failed to send: {e}") from e



def alert_owner(subject, body):
    """Email the operator (OWNER_ALERT_EMAIL) about something that needs
    attention: a payment, or a paid write-up that failed. Never raises: an
    alert that cannot be sent must not break the payer's flow, so the failure
    is logged instead. Returns True when the email was sent."""
    owner = os.getenv("OWNER_ALERT_EMAIL", "").strip()
    cfg = _config()
    if not owner or not all(cfg.values()):
        log.warning("Owner alert not sent (OWNER_ALERT_EMAIL or SMTP not set): %s", subject)
        return False
    msg = EmailMessage()
    msg["Subject"] = f"[{SETTINGS.app_name}] {subject}"
    msg["From"] = cfg["SMTP_USER"]
    msg["To"] = owner
    msg.set_content(body)
    try:
        with smtplib.SMTP(cfg["SMTP_HOST"], int(cfg["SMTP_PORT"]), timeout=30) as server:
            server.starttls()
            server.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
            server.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError, ValueError) as e:
        log.error("Owner alert failed to send (%s): %s", subject, e)
        return False


if __name__ == "__main__":
    # Smoke test: python3 emailer.py sends a stub receipt to TEST_EMAIL_RECIPIENT.
    recipient = os.getenv("TEST_EMAIL_RECIPIENT", "").strip()
    if not recipient:
        raise SystemExit("Set TEST_EMAIL_RECIPIENT in .env to run the smoke test.")
    send_report_receipt(
        payer_email=recipient,
        # Bandit reads a keyword named token as a password; this is a placeholder ticker
        token="TEST",  # nosec B106
        report_markdown="# Test report\n\nThis is a delivery smoke test, not a real report.\n",
        receipt={
            "amount_decimal": "0.10",
            "chain_id": 84532,
            "tx_hash": "0xtest",
            "flagged": 0,
            "clear": 0,
            "no_data": 0,
        },
    )
    print(f"Smoke test email sent to {recipient}.")
