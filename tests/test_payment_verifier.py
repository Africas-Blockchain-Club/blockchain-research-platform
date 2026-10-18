import time

import pytest

import payment_verifier as pv

RECIPIENT = "0x" + "ab" * 20
PAYER = "0x" + "cd" * 20


@pytest.fixture(autouse=True)
def recipient(monkeypatch):
    monkeypatch.setattr(pv, "RECIPIENT_ADDRESS", RECIPIENT)


def _receipt(amount_atomic, to=RECIPIENT, status="0x1", contract=None):
    return {
        "status": status,
        "from": PAYER,
        "blockNumber": hex(100),
        "logs": [{
            "address": contract or pv.USDC_CONTRACT,
            "topics": [pv.TRANSFER_TOPIC, "0x" + "0" * 24 + PAYER[2:], "0x" + "0" * 24 + to[2:]],
            "data": hex(amount_atomic),
        }],
    }


def _price_atomic():
    return int(pv.REPORT_PRICE_USDC * 10 ** pv.USDC_DECIMALS)


def test_a_recent_full_payment_verifies():
    result = pv._validate_receipt(_receipt(_price_atomic()), 110, "rpc", time.time() - 60)
    assert result["payer_address"] == PAYER
    assert result["confirmations"] == 11


def test_an_old_payment_is_rejected():
    old = time.time() - (pv.MAX_PAYMENT_AGE_MINUTES + 5) * 60
    with pytest.raises(pv.PaymentVerificationError, match="minutes old"):
        pv._validate_receipt(_receipt(_price_atomic()), 110, "rpc", old)


def test_a_short_payment_is_rejected():
    with pytest.raises(pv.PaymentVerificationError, match="too small"):
        pv._validate_receipt(_receipt(_price_atomic() - 1), 110, "rpc", time.time())


def test_a_payment_to_someone_else_is_rejected():
    with pytest.raises(pv.PaymentVerificationError, match="no USDC transfer"):
        pv._validate_receipt(_receipt(_price_atomic(), to=PAYER), 110, "rpc", time.time())


def test_a_different_token_is_rejected():
    with pytest.raises(pv.PaymentVerificationError, match="no USDC transfer"):
        pv._validate_receipt(_receipt(_price_atomic(), contract="0x" + "ef" * 20), 110, "rpc", time.time())


def test_a_reverted_transaction_is_rejected():
    with pytest.raises(pv.PaymentVerificationError, match="reverted"):
        pv._validate_receipt(_receipt(_price_atomic(), status="0x0"), 110, "rpc", time.time())


def test_mainnet_preset_uses_real_usdc():
    assert pv.NETWORKS[8453]["usdc"].lower() == "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
    assert pv.NETWORKS[8453]["testnet"] is False
