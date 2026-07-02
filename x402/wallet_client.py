"""x402 wallet client — signs payment authorisations for HTTP 402 flows."""

import json
import time

from eth_account import Account
from eth_account.messages import encode_defunct


class WalletClient:
    def __init__(self, private_key: str):
        self.account = Account.from_key(private_key)
        self.address = self.account.address

    def sign_payment(self, requirements: dict) -> dict:
        """Return a signed x402 payment payload for the given 402 requirements."""
        valid_until = int(time.time()) + requirements.get("maxTimeoutSeconds", 300)

        payload = {
            "x402Version": 1,
            "scheme": requirements["scheme"],
            "network": requirements["network"],
            "from": self.address,
            "to": requirements["payTo"],
            "value": requirements["maxAmountRequired"],
            "asset": requirements.get("asset", "native"),
            "resource": requirements["resource"],
            "validUntil": valid_until,
            "nonce": int(time.time() * 1000),
        }

        msg = encode_defunct(text=json.dumps(payload, sort_keys=True))
        signed = self.account.sign_message(msg)

        return {
            "payload": payload,
            "signature": signed.signature.hex(),
        }

    def __repr__(self) -> str:
        return f"WalletClient({self.address})"
