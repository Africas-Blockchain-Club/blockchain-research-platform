"""CLI demo — end-to-end x402 payment flow against a local paywall server.

Prerequisites:
  1. Start the mock server:  python x402/mock_server.py
  2. Run this script:        python x402/demo.py

Uses the default anvil account 0 private key unless X402_PRIVATE_KEY is set.
"""

import base64
import json
import os
import sys

import requests

# Append parent so this script can be run from the repo root or research-team/
sys.path.insert(0, os.path.dirname(__file__))
from wallet_client import WalletClient

# Anvil account 0 — always pre-funded with 10 000 ETH on a fresh anvil instance
ANVIL_DEFAULT_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

SERVER_URL = os.getenv("X402_PAYWALL_URL", "http://localhost:5402")


def _encode(payment: dict) -> str:
    return base64.b64encode(json.dumps(payment).encode()).decode()


def run():
    private_key = os.getenv("X402_PRIVATE_KEY", ANVIL_DEFAULT_KEY)
    wallet = WalletClient(private_key)

    print(f"\n[wallet]  {wallet.address}")
    print(f"[server]  {SERVER_URL}/premium-data\n")

    # --- Step 1: unauthenticated request ---
    print("Step 1  Request without payment")
    resp = requests.get(f"{SERVER_URL}/premium-data", timeout=5)
    print(f"  -> {resp.status_code} Payment Required")
    if resp.status_code != 402:
        print(f"  [error] expected 402, got {resp.status_code}")
        sys.exit(1)

    body = resp.json()
    requirements = body["accepts"][0]
    print(f"  -> amount   : {requirements['maxAmountRequired']} wei")
    print(f"  -> recipient: {requirements['payTo']}")
    print(f"  -> network  : {requirements['network']}")

    # --- Step 2: sign payment ---
    print("\nStep 2  Sign payment authorisation")
    payment = wallet.sign_payment(requirements)
    print(f"  -> nonce      : {payment['payload']['nonce']}")
    print(f"  -> valid until: {payment['payload']['validUntil']}")
    print(f"  -> signature  : {payment['signature'][:20]}...")

    # --- Step 3: authenticated request ---
    print("\nStep 3  Resend request with X-PAYMENT header")
    resp = requests.get(
        f"{SERVER_URL}/premium-data",
        headers={"X-PAYMENT": _encode(payment)},
        timeout=5,
    )
    print(f"  -> {resp.status_code} OK")
    if resp.status_code != 200:
        print(f"  [error] {resp.text}")
        sys.exit(1)

    data = resp.json()["data"]
    print(f"\n  {json.dumps(data, indent=4)}")
    print("\n[x402] Payment accepted. Resource unlocked.\n")


if __name__ == "__main__":
    try:
        run()
    except requests.exceptions.ConnectionError:
        print(f"\n[error] Cannot reach {SERVER_URL}")
        print("        Start the server first:  python x402/mock_server.py")
        sys.exit(1)
