"""
Education, not advice: the disclaimer text and the advice-language guard.

The platform explains what public data says about a token. It must never tell
a reader to buy, sell or hold one, because a recommendation like that is
financial advice and needs a licence (in South Africa, under the FAIS Act).
See docs/COMPLIANCE.md for the full rules.

The prompt asks the model not to give advice, but a prompt is a request, not
a control. This module is the control: every AI write-up passes through
find_advice_language() before it is saved, and a write-up that fails is
rejected loudly rather than published. The patterns are deliberately narrow
so that teaching sentences ("a large sell order moves the price") still pass.
"""
import re

from config import SETTINGS

SHORT_DISCLAIMER = (
    "Educational research only, not financial advice. Nothing here recommends "
    "buying, selling or holding any token."
)


def long_disclaimer():
    return (
        "> **Educational research, not financial advice.** This report explains what public "
        "data says about a token so that you can learn to read it. It does not recommend "
        "buying, selling or holding any token, and it does not take your circumstances into "
        f"account. {SETTINGS.brand_name} is not an authorised financial services provider. "
        "Crypto assets are high risk and their price can fall to zero. Before you invest, "
        "speak to a financial services provider authorised by the Financial Sector Conduct "
        "Authority (FSCA)."
    )


_ADVICE_PATTERNS = [
    (r"\bstrong\s+(buy|sell)\b", "a buy or sell rating"),
    (r"\b(buy|sell|hold|accumulate|distribute)\s+(rating|signal|recommendation|zone|call)s?\b", "a trading signal"),
    (r"\brating\W{0,6}(buy|sell|hold|accumulate|distribute|neutral)\b", "a rating"),
    (r"\b(entry|exit)\s+(trigger|point|price|signal|level)s?\b", "an entry or exit instruction"),
    (r"\bstop[- ]?loss", "a stop-loss instruction"),
    (r"\btake[- ]profit", "a take-profit instruction"),
    (r"\bprice\s+target", "a price target"),
    (r"\bposition\s+siz", "position sizing"),
    (r"\b(build|open|reduce|increase|add\s+to|trim)\s+(a\s+|your\s+|the\s+)?(position|exposure)\b", "a position instruction"),
    (r"\bdollar[- ]cost[- ]averag", "an investing strategy instruction"),
    (r"\b(you|investors|readers|holders|traders)\s+(should|must|ought\s+to)\s+(buy|sell|hold|invest|accumulate|exit|enter|avoid|consider)", "a personal instruction"),
    (r"\b(we|this\s+report|the\s+platform)\s+(recommends?|advises?|suggests?\s+(buying|selling|holding))\b", "a recommendation"),
    (r"\bsignal\W{0,6}(bullish|bearish)\b", "a directional signal"),
    (r"\b(good|great|bad|ideal|attractive|right)\s+(time|moment|entry|opportunity)\s+to\s+(buy|sell|invest|enter|exit)", "market timing"),
    (r"\bworth\s+(buying|holding|owning|investing)", "a judgement on investment merit"),
    (r"\b(undervalued|overvalued)\b", "a valuation judgement"),
    (r"\b(blueprint|conviction)\s+score\b", "a rating score"),
]
_COMPILED = [(re.compile(p, re.IGNORECASE), label) for p, label in _ADVICE_PATTERNS]


class AdviceLanguageError(Exception):
    """An AI write-up contained recommendation language and was not saved."""

    def __init__(self, findings):
        self.findings = findings
        sample = "; ".join(f'"{f["match"]}" ({f["kind"]})' for f in findings[:5])
        super().__init__(
            f"The AI write-up was rejected because it read as financial advice: {sample}. "
            "The data-only report is still available."
        )


def find_advice_language(text):
    """Return a list of {match, kind, line} for every advice-like phrase."""
    findings = []
    for number, line in enumerate(text.splitlines(), start=1):
        for pattern, kind in _COMPILED:
            for match in pattern.finditer(line):
                findings.append({"match": match.group(0), "kind": kind, "line": number})
    return findings


def assert_educational(text):
    """Raise AdviceLanguageError when text contains advice-like phrases."""
    findings = find_advice_language(text)
    if findings:
        raise AdviceLanguageError(findings)
