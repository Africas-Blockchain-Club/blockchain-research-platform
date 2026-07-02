"""Mock x402 paywall server — requires a signed payment for premium endpoints.

Run:  python x402/mock_server.py
      (default port 5402)
"""

import base64
import json
import time

from eth_account import Account
from eth_account.messages import encode_defunct
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# Anvil account 1 as the payment recipient (pre-funded on local anvil)
PAYWALL_ADDRESS = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
REQUIRED_AMOUNT = "1000000000000000"  # 0.001 ETH in wei
NETWORK = "anvil"
RESOURCE_URL = "http://localhost:5402/premium-data"

PAYMENT_REQUIREMENTS = {
    "scheme": "exact",
    "network": NETWORK,
    "maxAmountRequired": REQUIRED_AMOUNT,
    "resource": RESOURCE_URL,
    "description": "Access to research-team premium market data endpoint",
    "mimeType": "application/json",
    "payTo": PAYWALL_ADDRESS,
    "maxTimeoutSeconds": 300,
    "asset": "native",
    "outputSchema": None,
    "extra": {},
}


def _verify_payment(payment_header: str) -> tuple[bool, str]:
    """Verify an x402 payment header. Returns (ok, reason)."""
    try:
        payment = json.loads(base64.b64decode(payment_header).decode())
    except Exception:
        return False, "malformed payment header — expected base64-encoded JSON"

    payload = payment.get("payload", {})
    signature = payment.get("signature", "")

    if int(payload.get("value", 0)) < int(REQUIRED_AMOUNT):
        return False, f"insufficient amount: {payload.get('value')} < {REQUIRED_AMOUNT}"

    if payload.get("validUntil", 0) < int(time.time()):
        return False, "payment authorisation expired"

    if payload.get("to", "").lower() != PAYWALL_ADDRESS.lower():
        return False, f"wrong recipient: {payload.get('to')}"

    msg = encode_defunct(text=json.dumps(payload, sort_keys=True))
    try:
        sig_bytes = bytes.fromhex(signature.removeprefix("0x"))
        recovered = Account.recover_message(msg, signature=sig_bytes)
    except Exception as exc:
        return False, f"signature recovery failed: {exc}"

    if recovered.lower() != payload.get("from", "").lower():
        return False, f"signature mismatch: recovered {recovered}"

    return True, "ok"


@app.get("/premium-data")
def premium_data():
    payment_header = request.headers.get("X-PAYMENT")

    if not payment_header:
        body = json.dumps({"x402Version": 1, "accepts": [PAYMENT_REQUIREMENTS]})
        return Response(
            body,
            status=402,
            mimetype="application/json",
            headers={"X-PAYMENT-REQUIRED": "true"},
        )

    ok, reason = _verify_payment(payment_header)
    if not ok:
        return jsonify({"error": f"invalid payment: {reason}"}), 402

    return jsonify({
        "status": "success",
        "data": {
            "message": "Premium market data unlocked via x402 payment",
            "btc_price_usd": 105000,
            "eth_price_usd": 3800,
            "source": "mock-paywall-server",
        },
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok", "paywall": PAYWALL_ADDRESS, "network": NETWORK})


if __name__ == "__main__":
    print(f"[x402] Mock paywall server — http://localhost:5402")
    print(f"[x402] Payment required : {REQUIRED_AMOUNT} wei (native ETH)")
    print(f"[x402] Recipient        : {PAYWALL_ADDRESS}")
    print(f"[x402] Network          : {NETWORK}\n")
    app.run(host="0.0.0.0", port=5402)
