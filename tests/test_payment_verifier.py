import time

import pytest

import payment_verifier as pv

RECIPIENT = "0x" + "ab" * 20
PAYER = "0x" + "cd" * 20


@pytest.fixture(autouse=True)
def recipient(monkeypatch):
    monkeypatch.setattr(pv, "RECIPIENT_ADDRESS", RECIPIENT)


BASE = 8453
USDC_BASE = pv.NETWORKS[BASE]["tokens"]["USDC"][0]


def _receipt(amount_atomic, to=RECIPIENT, status="0x1", contract=None):
    return {
        "status": status,
        "from": PAYER,
        "blockNumber": hex(100),
        "logs": [{
            "address": contract or USDC_BASE,
            "topics": [pv.TRANSFER_TOPIC, "0x" + "0" * 24 + PAYER[2:], "0x" + "0" * 24 + to[2:]],
            "data": hex(amount_atomic),
        }],
    }


def _price_atomic(decimals=6):
    return pv.required_atomic(decimals)


def test_a_recent_full_payment_verifies():
    result = pv._validate_receipt(_receipt(_price_atomic()), 110, "rpc", time.time() - 60, BASE)
    assert result["payer_address"] == PAYER
    assert result["confirmations"] == 11


def test_an_old_payment_is_rejected():
    old = time.time() - (pv.MAX_PAYMENT_AGE_MINUTES + 5) * 60
    with pytest.raises(pv.PaymentVerificationError, match="minutes old"):
        pv._validate_receipt(_receipt(_price_atomic()), 110, "rpc", old, BASE)


def test_a_short_payment_is_rejected():
    with pytest.raises(pv.PaymentVerificationError, match="too small"):
        pv._validate_receipt(_receipt(_price_atomic() - 1), 110, "rpc", time.time(), BASE)


def test_a_payment_to_someone_else_is_rejected():
    with pytest.raises(pv.PaymentVerificationError, match="no USDC or USDT transfer"):
        pv._validate_receipt(_receipt(_price_atomic(), to=PAYER), 110, "rpc", time.time(), BASE)


def test_a_different_token_is_rejected():
    with pytest.raises(pv.PaymentVerificationError, match="no USDC or USDT transfer"):
        pv._validate_receipt(_receipt(_price_atomic(), contract="0x" + "ef" * 20), 110, "rpc", time.time(), BASE)


def test_a_reverted_transaction_is_rejected():
    with pytest.raises(pv.PaymentVerificationError, match="reverted"):
        pv._validate_receipt(_receipt(_price_atomic(), status="0x0"), 110, "rpc", time.time(), BASE)


def test_usdt_with_18_decimals_on_bnb_chain_verifies():
    usdt_bnb, decimals = pv.NETWORKS[56]["tokens"]["USDT"]
    result = pv._validate_receipt(_receipt(_price_atomic(18), contract=usdt_bnb), 110, "rpc", time.time(), 56)
    assert result["asset_symbol"] == "USDT" and result["amount_decimal"] == pv.REPORT_PRICE_USDC


def test_usdt_with_6_decimals_paid_as_if_18_is_rejected():
    usdt_arb = pv.NETWORKS[42161]["tokens"]["USDT"][0]
    with pytest.raises(pv.PaymentVerificationError, match="too small"):
        pv._validate_receipt(_receipt(_price_atomic(6) - 1, contract=usdt_arb), 110, "rpc", time.time(), 42161)


def test_a_token_from_another_chain_is_rejected():
    # Base USDC's contract is not an accepted token on Arbitrum
    with pytest.raises(pv.PaymentVerificationError, match="no USDC or USDT"):
        pv._validate_receipt(_receipt(_price_atomic()), 110, "rpc", time.time(), 42161)


def test_mainnet_preset_uses_real_usdc():
    assert pv.NETWORKS[8453]["tokens"]["USDC"][0].lower() == "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
    assert pv.NETWORKS[8453]["testnet"] is False


def test_payment_options_cover_every_token_on_every_chain(monkeypatch):
    monkeypatch.setattr(pv, "PAYMENT_CHAINS", [8453, 56])
    options = pv.payment_options()
    assert {(o["chain_id"], o["token_symbol"]) for o in options} == {(8453, "USDC"), (8453, "USDT"), (56, "USDC"), (56, "USDT")}
    bnb_usdt = next(o for o in options if o["chain_id"] == 56 and o["token_symbol"] == "USDT")
    assert bnb_usdt["amount_atomic"] == str(pv.required_atomic(18))


def test_testnets_and_mainnets_cannot_be_mixed(monkeypatch):
    monkeypatch.setenv("PAYMENT_CHAINS", "84532,8453")
    with pytest.raises(ValueError):
        pv._chain_list()
