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
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

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
    """Sends the finished audit report to the payer with a payment receipt.

    payer_email:      destination address.
    token:            token symbol, e.g. "SOL".
    report_markdown:  the full saved report, attached as a .md file.
    receipt:          dict with tx_hash, amount_decimal, chain_id, score, verdict.

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
    msg["Subject"] = f"{token} forensic audit report and payment receipt"
    msg["From"] = cfg["SMTP_USER"]
    msg["To"] = payer_email
    msg.set_content(
        f"Thank you for your payment. Your {token} forensic audit report is attached.\n"
        f"\n"
        f"Payment receipt\n"
        f"---------------\n"
        f"Token analysed:   {token}\n"
        f"Amount paid:      {receipt.get('amount_decimal')} USDC\n"
        f"Chain:            Base Sepolia (chain id {receipt.get('chain_id')})\n"
        f"Transaction hash: {receipt.get('tx_hash')}\n"
        f"\n"
        f"Report summary\n"
        f"--------------\n"
        f"Blueprint Score:  {receipt.get('score')}/100\n"
        f"Final Verdict:    {receipt.get('verdict')}\n"
        f"\n"
        f"The full report is attached as markdown. Open it in any text editor\n"
        f"or markdown viewer.\n"
        f"\n"
        f"Africa's Blockchain Club - Research Team\n"
    )
    msg.add_attachment(
        report_markdown.encode("utf-8"),
        maintype="text",
        subtype="markdown",
        filename=f"{token}_audit_report.md",
    )

    try:
        with smtplib.SMTP(cfg["SMTP_HOST"], int(cfg["SMTP_PORT"]), timeout=30) as server:
            server.starttls()
            server.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
            server.send_message(msg)
    except (smtplib.SMTPException, OSError, ValueError) as e:
        raise EmailDeliveryError(f"Report email failed to send: {e}") from e


if __name__ == "__main__":
    # Smoke test: python3 emailer.py sends a stub receipt to TEST_EMAIL_RECIPIENT.
    recipient = os.getenv("TEST_EMAIL_RECIPIENT", "").strip()
    if not recipient:
        raise SystemExit("Set TEST_EMAIL_RECIPIENT in .env to run the smoke test.")
    send_report_receipt(
        payer_email=recipient,
        token="TEST",
        report_markdown="# Test report\n\nThis is a delivery smoke test, not a real audit.\n",
        receipt={
            "amount_decimal": "0.10",
            "chain_id": 84532,
            "tx_hash": "0xtest",
            "score": 0,
            "verdict": "Smoke test",
        },
    )
    print(f"Smoke test email sent to {recipient}.")
