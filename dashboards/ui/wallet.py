"""
Browser wallet components (MetaMask and other EIP-1193 wallets).

Plain-HTML Streamlit components: no build step and no npm dependency. Both
are optional; the platform works fully without a wallet.
"""
from pathlib import Path

import streamlit.components.v1 as components

_HERE = Path(__file__).resolve().parent.parent

# Returns {"tx_hash": ..., "payer_wallet": ...} once the user approves the transfer
wallet_pay = components.declare_component("wallet_pay", path=str(_HERE / "wallet_pay"))

# Returns {"address": ...} once connected. Session 3: a wallet address as an
# identity the user owns outright, unlike an account a provider can suspend.
wallet_connect = components.declare_component("wallet_connect", path=str(_HERE / "wallet_connect"))
