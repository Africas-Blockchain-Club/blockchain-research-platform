import emailer


class FakeSMTP:
    sent = []

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        pass

    def login(self, *args):
        pass

    def send_message(self, msg):
        FakeSMTP.sent.append(msg)


def _configure(monkeypatch):
    for key, value in {"SMTP_HOST": "smtp.test", "SMTP_PORT": "587", "SMTP_USER": "from@test", "SMTP_PASSWORD": "x"}.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(emailer.smtplib, "SMTP", FakeSMTP)
    FakeSMTP.sent = []


def test_payer_receives_the_report_as_pdf_and_markdown(monkeypatch):
    _configure(monkeypatch)
    emailer.send_report_receipt(
        "payer@test", "sol", "# SOL Research Report\n\n| A | B |\n|---|---|\n| 1 | 2 |\n",
        {"amount_decimal": "2", "asset": "USDT", "chain_id": 42161, "chain_name": "Arbitrum",
         "tx_hash": "0xabc", "flagged": 1, "clear": 8, "no_data": 1},
    )
    msg = FakeSMTP.sent[0]
    assert msg["To"] == "payer@test"
    names = [part.get_filename() for part in msg.iter_attachments()]
    assert names == ["SOL_research_report.pdf", "SOL_research_report.md"]
    body = msg.get_body().get_content()
    assert "2 USDT" in body and "Arbitrum" in body and "not for advice" in body


def test_owner_alert_goes_to_the_owner(monkeypatch):
    _configure(monkeypatch)
    monkeypatch.setenv("OWNER_ALERT_EMAIL", "owner@test")
    assert emailer.alert_owner("Payment received", "details") is True
    assert FakeSMTP.sent[0]["To"] == "owner@test"
