"""
On-chain payment verification for paid report generation.

Confirms a user-submitted transaction hash pays REPORT_PRICE_USDC in USDC to
REPORT_RECIPIENT_ADDRESS on Base Sepolia. Tries a direct RPC read first; if the
RPC is unreachable, falls back to the same lookup via Etherscan's unified
multichain API, then Blockscout. All three read the same on-chain receipt, so
a definitive rejection (wrong amount, wrong recipient, reverted tx) from any
one of them is trusted immediately rather than retried against the others —
only transport failures (timeouts, unreachable host) fall through to the next
source. Chain, contract, recipient, and price are config, not hard-coded, and
every failure raises PaymentVerificationError with a specific reason; nothing
is ever treated as paid by default.
"""
import os
from decimal import Decimal

import requests

CHAIN_ID = int(os.getenv("CHAIN_ID", "84532"))
RPC_URL = os.getenv("BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org")
USDC_CONTRACT = os.getenv("USDC_CONTRACT_ADDRESS", "0x036CbD53842c5426634e7929541eC2318f3dCF7e").lower()
RECIPIENT_ADDRESS = os.getenv("REPORT_RECIPIENT_ADDRESS", "").lower()
REPORT_PRICE_USDC = Decimal(os.getenv("REPORT_PRICE_USDC", "1.10"))
USDC_DECIMALS = 6
MIN_CONFIRMATIONS = int(os.getenv("PAYMENT_MIN_CONFIRMATIONS", "1"))
REQUEST_TIMEOUT = 10

# keccak256("Transfer(address,address,uint256)") — the ERC-20 transfer event topic
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# (verification_method, base_url, api_key_env, needs_chainid_param)
_EXPLORER_FALLBACKS = [
    ("etherscan_fallback", "https://api.etherscan.io/v2/api", "ETHERSCAN_API_KEY", True),
    ("blockscout_fallback", "https://base-sepolia.blockscout.com/api", "BLOCKSCOUT_API_KEY", False),
]


class PaymentVerificationError(Exception):
    """Raised for any unverified payment — callers must show this to the user, never swallow it."""


def _rpc_call(method, params):
    resp = requests.post(
        RPC_URL,
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    body = resp.json()
    if "error" in body:
        raise ConnectionError(f"RPC returned an error: {body['error']}")
    return body.get("result")


def _explorer_call(base_url, api_key_env, needs_chainid, method, params):
    query = {"module": "proxy", "action": method}
    if needs_chainid:
        query["chainid"] = CHAIN_ID
    if method == "eth_getTransactionReceipt":
        query["txhash"] = params[0]
    api_key = os.getenv(api_key_env)
    if api_key:
        query["apikey"] = api_key
    resp = requests.get(base_url, params=query, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("result")


def _validate_receipt(receipt, latest_block, verification_method):
    if receipt.get("status") != "0x1":
        raise PaymentVerificationError("transaction reverted on-chain")

    payer_address = (receipt.get("from") or "").lower()
    block_number = int(receipt.get("blockNumber", "0x0"), 16)
    confirmations = max(0, latest_block - block_number + 1)

    required_atomic = int(REPORT_PRICE_USDC * (10 ** USDC_DECIMALS))

    for log in receipt.get("logs") or []:
        if (log.get("address") or "").lower() != USDC_CONTRACT:
            continue
        topics = log.get("topics") or []
        if len(topics) < 3 or topics[0].lower() != TRANSFER_TOPIC:
            continue
        log_recipient = "0x" + topics[2][-40:]
        if log_recipient.lower() != RECIPIENT_ADDRESS:
            continue

        amount_atomic = int(log.get("data", "0x0"), 16)
        if amount_atomic < required_atomic:
            raise PaymentVerificationError(
                f"payment too small: {amount_atomic} atomic units, needed {required_atomic}"
            )
        if confirmations < MIN_CONFIRMATIONS:
            raise PaymentVerificationError(
                f"only {confirmations} confirmation(s) so far, needs {MIN_CONFIRMATIONS}"
            )
        return {
            "payer_address": payer_address,
            "amount_atomic": amount_atomic,
            "amount_decimal": Decimal(amount_atomic) / Decimal(10 ** USDC_DECIMALS),
            "verification_method": verification_method,
            "confirmations": confirmations,
        }

    raise PaymentVerificationError(
        f"no USDC transfer to {RECIPIENT_ADDRESS} found in this transaction"
    )


def verify_payment(tx_hash: str) -> dict:
    """
    Looks up tx_hash on-chain and checks it pays REPORT_PRICE_USDC in USDC to
    RECIPIENT_ADDRESS with enough confirmations.

    Returns {"payer_address", "amount_atomic", "amount_decimal",
             "verification_method", "confirmations"} on success.
    Raises PaymentVerificationError with a specific reason on any failure —
    including when every lookup source is unreachable.
    """
    if not RECIPIENT_ADDRESS:
        raise PaymentVerificationError("REPORT_RECIPIENT_ADDRESS is not configured — cannot verify payments")
    if not tx_hash or not tx_hash.startswith("0x"):
        raise PaymentVerificationError("that doesn't look like a transaction hash (expected 0x...)")

    sources = [("rpc", lambda method, params: _rpc_call(method, params))] + [
        (
            name,
            lambda method, params, b=base_url, k=api_key_env, c=needs_chainid: _explorer_call(
                b, k, c, method, params
            ),
        )
        for name, base_url, api_key_env, needs_chainid in _EXPLORER_FALLBACKS
    ]

    transport_errors = []
    for verification_method, call in sources:
        try:
            receipt = call("eth_getTransactionReceipt", [tx_hash])
            if receipt is None:
                transport_errors.append(f"{verification_method}: transaction not found (yet)")
                continue
            latest_block = int(call("eth_blockNumber", []), 16)
        except Exception as exc:
            transport_errors.append(f"{verification_method}: {exc}")
            continue

        return _validate_receipt(receipt, latest_block, verification_method)

    raise PaymentVerificationError(
        "could not verify this transaction — every lookup source failed: " + "; ".join(transport_errors)
    )
