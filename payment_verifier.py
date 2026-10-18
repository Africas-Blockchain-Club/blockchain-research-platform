"""
On-chain payment verification for AI write-ups.

A payer may send REPORT_PRICE_USDC worth of USDC or USDT on any network in
PAYMENT_CHAINS, so nobody has to swap or bridge before paying. A payment
counts when the transaction:
  - succeeded on the chain the payer names,
  - moved an accepted stablecoin on that chain to REPORT_RECIPIENT_ADDRESS,
  - moved at least the price (each token's own decimals are respected),
  - is recent (PAYMENT_MAX_AGE_MINUTES) and has enough confirmations.

Every chain is read through a direct RPC first, then Etherscan's multichain
API as a fallback. A definitive rejection (wrong amount, wrong recipient,
reverted) from any source is trusted at once; only transport failures fall
through to the next source. Nothing is ever treated as paid by default.

USDC and USDT are both treated as one US Dollar. That is close enough for a
small fixed price; a depeg would need this rule revisited.
"""
import os
import time
from decimal import Decimal

import requests

# Every contract below was checked on-chain on 18 October 2026 (symbol and
# decimals). USDT on BNB Chain and USDC on BNB Chain use 18 decimals.
NETWORKS = {
    84532: {
        "name": "Base Sepolia",
        "testnet": True,
        "rpc": "https://sepolia.base.org",
        "explorer": "https://sepolia.basescan.org",
        "native": "ETH",
        "tokens": {"USDC": ("0x036CbD53842c5426634e7929541eC2318f3dCF7e", 6)},
    },
    8453: {
        "name": "Base",
        "testnet": False,
        "rpc": "https://mainnet.base.org",
        "explorer": "https://basescan.org",
        "native": "ETH",
        "tokens": {
            "USDC": ("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", 6),
            "USDT": ("0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2", 6),
        },
    },
    42161: {
        "name": "Arbitrum",
        "testnet": False,
        "rpc": "https://arb1.arbitrum.io/rpc",
        "explorer": "https://arbiscan.io",
        "native": "ETH",
        "tokens": {
            "USDC": ("0xaf88d065e77c8cC2239327C5EDb3A432268e5831", 6),
            "USDT": ("0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", 6),
        },
    },
    10: {
        "name": "Optimism",
        "testnet": False,
        "rpc": "https://mainnet.optimism.io",
        "explorer": "https://optimistic.etherscan.io",
        "native": "ETH",
        "tokens": {
            "USDC": ("0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85", 6),
            "USDT": ("0x94b008aA00579c1307B0EF2c499aD98a8ce58e58", 6),
        },
    },
    137: {
        "name": "Polygon",
        "testnet": False,
        "rpc": "https://polygon-bor-rpc.publicnode.com",
        "explorer": "https://polygonscan.com",
        "native": "POL",
        "tokens": {
            "USDC": ("0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359", 6),
            "USDT": ("0xc2132D05D31c914a87C6611C10748AEb04B58e8F", 6),
        },
    },
    56: {
        "name": "BNB Chain",
        "testnet": False,
        "rpc": "https://bsc-dataseed.bnbchain.org",
        "explorer": "https://bscscan.com",
        "native": "BNB",
        "tokens": {
            "USDC": ("0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", 18),
            "USDT": ("0x55d398326f99059fF775485246999027B3197955", 18),
        },
    },
    1: {
        "name": "Ethereum",
        "testnet": False,
        "rpc": "https://ethereum-rpc.publicnode.com",
        "explorer": "https://etherscan.io",
        "native": "ETH",
        "tokens": {
            "USDC": ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6),
            "USDT": ("0xdAC17F958D2ee523a2206206994597C13D831ec7", 6),
        },
    },
}


def _chain_list():
    # CHAIN_ID is the older single-network setting, still read for old .env files
    raw = os.getenv("PAYMENT_CHAINS") or os.getenv("CHAIN_ID") or "84532"
    chains = [int(part) for part in raw.split(",") if part.strip()]
    unknown = [c for c in chains if c not in NETWORKS]
    if unknown:
        raise ValueError(f"PAYMENT_CHAINS has unsupported chain ids {unknown}; use any of {sorted(NETWORKS)}")
    if len({NETWORKS[c]["testnet"] for c in chains}) > 1:
        raise ValueError("PAYMENT_CHAINS mixes testnets and mainnets; pick one kind")
    return chains


PAYMENT_CHAINS = _chain_list()
IS_TESTNET = NETWORKS[PAYMENT_CHAINS[0]]["testnet"]
ASSET_LABEL = "test USDC" if IS_TESTNET else "USDC or USDT"
RECIPIENT_ADDRESS = (os.getenv("REPORT_RECIPIENT_ADDRESS") or "").strip().lower()
REPORT_PRICE_USDC = Decimal(os.getenv("REPORT_PRICE_USDC") or "2.00")
MIN_CONFIRMATIONS = int(os.getenv("PAYMENT_MIN_CONFIRMATIONS") or ("1" if IS_TESTNET else "3"))
# A payment older than this cannot unlock a report. Without the limit, anyone
# could claim an old transfer to the business wallet that was never theirs.
MAX_PAYMENT_AGE_MINUTES = int(os.getenv("PAYMENT_MAX_AGE_MINUTES") or "60")
REQUEST_TIMEOUT = 10

# keccak256("Transfer(address,address,uint256)") - the ERC-20 transfer event topic
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ETHERSCAN_V2 = "https://api.etherscan.io/v2/api"


class PaymentVerificationError(Exception):
    """Raised for any unverified payment - callers must show this to the user, never swallow it."""


def rpc_url(chain_id):
    return os.getenv(f"RPC_URL_{chain_id}") or NETWORKS[chain_id]["rpc"]


def required_atomic(decimals):
    return int(REPORT_PRICE_USDC * (10 ** decimals))


def payment_options():
    """Every accepted (network, token) pair, in PAYMENT_CHAINS order. The
    wallet component offers these and checks the payer's balance of each."""
    options = []
    for chain_id in PAYMENT_CHAINS:
        network = NETWORKS[chain_id]
        for symbol, (contract, decimals) in network["tokens"].items():
            options.append({
                "chain_id": chain_id,
                "chain_name": network["name"],
                "rpc_url": rpc_url(chain_id),
                "explorer_url": network["explorer"],
                "native_symbol": network["native"],
                "token_symbol": f"test {symbol}" if network["testnet"] else symbol,
                "token_contract": contract,
                "decimals": decimals,
                "amount_atomic": str(required_atomic(decimals)),
            })
    return options


def _rpc_call(chain_id, method, params):
    resp = requests.post(
        rpc_url(chain_id),
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    body = resp.json()
    if "error" in body:
        raise ConnectionError(f"RPC returned an error: {body['error']}")
    return body.get("result")


def _etherscan_call(chain_id, method, params):
    query = {"module": "proxy", "action": method, "chainid": chain_id}
    if method == "eth_getTransactionReceipt":
        query["txhash"] = params[0]
    elif method == "eth_getBlockByNumber":
        query["tag"] = params[0]
        query["boolean"] = "false"
    api_key = os.getenv("ETHERSCAN_API_KEY")
    if api_key:
        query["apikey"] = api_key
    resp = requests.get(ETHERSCAN_V2, params=query, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("result")


def _validate_receipt(receipt, latest_block, verification_method, block_timestamp, chain_id):
    if receipt.get("status") != "0x1":
        raise PaymentVerificationError("transaction reverted on-chain")

    age_minutes = (time.time() - block_timestamp) / 60
    if age_minutes > MAX_PAYMENT_AGE_MINUTES:
        raise PaymentVerificationError(
            f"this payment is {age_minutes:,.0f} minutes old; only payments made in the last "
            f"{MAX_PAYMENT_AGE_MINUTES} minutes can unlock a report"
        )

    network = NETWORKS[chain_id]
    accepted = {contract.lower(): (symbol, decimals) for symbol, (contract, decimals) in network["tokens"].items()}
    payer_address = (receipt.get("from") or "").lower()
    block_number = int(receipt.get("blockNumber", "0x0"), 16)
    confirmations = max(0, latest_block - block_number + 1)

    for log in receipt.get("logs") or []:
        token = accepted.get((log.get("address") or "").lower())
        topics = log.get("topics") or []
        if not token or len(topics) < 3 or topics[0].lower() != TRANSFER_TOPIC:
            continue
        if ("0x" + topics[2][-40:]).lower() != RECIPIENT_ADDRESS:
            continue

        symbol, decimals = token
        amount_atomic = int(log.get("data", "0x0"), 16)
        if amount_atomic < required_atomic(decimals):
            raise PaymentVerificationError(
                f"payment too small: {Decimal(amount_atomic) / Decimal(10 ** decimals)} {symbol}, "
                f"needed {REPORT_PRICE_USDC}"
            )
        if confirmations < MIN_CONFIRMATIONS:
            raise PaymentVerificationError(
                f"only {confirmations} confirmation(s) so far, needs {MIN_CONFIRMATIONS}"
            )
        return {
            "payer_address": payer_address,
            "chain_id": chain_id,
            "chain_name": network["name"],
            "asset_symbol": symbol,
            "asset_contract": log["address"].lower(),
            "amount_atomic": amount_atomic,
            "amount_decimal": Decimal(amount_atomic) / Decimal(10 ** decimals),
            "verification_method": verification_method,
            "confirmations": confirmations,
        }

    accepted_names = " or ".join(network["tokens"])
    raise PaymentVerificationError(
        f"no {accepted_names} transfer to {RECIPIENT_ADDRESS} on {network['name']} found in this transaction"
    )


def verify_payment(tx_hash: str, chain_id: int) -> dict:
    """
    Look up tx_hash on chain_id and check it pays the price in an accepted
    stablecoin to RECIPIENT_ADDRESS. Returns the payment details, or raises
    PaymentVerificationError with a specific reason.
    """
    if not RECIPIENT_ADDRESS:
        raise PaymentVerificationError("REPORT_RECIPIENT_ADDRESS is not configured - cannot verify payments")
    if chain_id not in PAYMENT_CHAINS:
        raise PaymentVerificationError(f"payments are not accepted on chain {chain_id}")
    if not tx_hash or not tx_hash.startswith("0x"):
        raise PaymentVerificationError("that does not look like a transaction hash (expected 0x...)")

    sources = [("rpc", _rpc_call)]
    if not NETWORKS[chain_id]["testnet"]:
        sources.append(("etherscan_fallback", _etherscan_call))

    transport_errors = []
    for verification_method, call in sources:
        try:
            receipt = call(chain_id, "eth_getTransactionReceipt", [tx_hash])
            if receipt is None:
                transport_errors.append(f"{verification_method}: transaction not found (yet)")
                continue
            latest_block = int(call(chain_id, "eth_blockNumber", []), 16)
            block = call(chain_id, "eth_getBlockByNumber", [receipt.get("blockNumber"), False]) or {}
            if not block.get("timestamp"):
                # Fail closed: without the block time the age limit cannot be checked
                raise ConnectionError("block timestamp unavailable")
            block_timestamp = int(block["timestamp"], 16)
        except Exception as exc:
            transport_errors.append(f"{verification_method}: {exc}")
            continue

        return _validate_receipt(receipt, latest_block, verification_method, block_timestamp, chain_id)

    raise PaymentVerificationError(
        "could not verify this transaction - every lookup source failed: " + "; ".join(transport_errors)
    )


def wait_for_payment(tx_hash: str, chain_id: int, timeout_seconds: int = 120, poll_seconds: int = 3) -> dict:
    """
    Like verify_payment, but tolerates a freshly broadcast transaction: retries
    while the receipt is not yet mined or lacks confirmations, up to
    timeout_seconds. Definitive rejections raise immediately.
    """
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            return verify_payment(tx_hash, chain_id)
        except PaymentVerificationError as exc:
            message = str(exc)
            retryable = (
                "not found" in message
                or "confirmation(s) so far" in message
                or "every lookup source failed" in message
            )
            if not retryable or time.monotonic() >= deadline:
                raise
            time.sleep(poll_seconds)
