import pytest

from data_science.ai_generator import SYSTEM_PROMPT
from data_science.compliance import (
    SHORT_DISCLAIMER,
    AdviceLanguageError,
    assert_educational,
    find_advice_language,
    long_disclaimer,
)

ADVICE = [
    "Rating: Strong Buy",
    "| **Rating** | Accumulate |",
    "We recommend a gradual approach.",
    "Investors should buy below $2.",
    "You should consider selling now.",
    "Set a stop-loss at $1.80.",
    "Our price target is $5.",
    "Entry trigger: price holds above $2.",
    "Build a position gradually.",
    "Reduce exposure if depth falls.",
    "Dollar-cost averaging suits this token.",
    "> **Phase 2 Signal: BEARISH** - depth is thin.",
    "This is a good time to buy.",
    "The token looks undervalued.",
    "It is worth holding for years.",
    "Blueprint Score: 64/100",
]

TEACHING = [
    "A large sell order moves the price in a thin pool.",
    "Funding rate: a periodic payment between long and short futures traders.",
    "When buyers outnumber sellers, the price rises.",
    "Traders who hold long positions pay a fee to those who hold short ones.",
    "Selling 10% of the pool's tokens lowers the price by about 19%.",
    "The project says the upgrade will reduce fees.",
]


@pytest.mark.parametrize("text", ADVICE)
def test_advice_language_is_caught(text):
    assert find_advice_language(text), text


@pytest.mark.parametrize("text", TEACHING)
def test_teaching_language_passes(text):
    assert find_advice_language(text) == []


def test_assert_educational_raises_with_findings():
    with pytest.raises(AdviceLanguageError) as error:
        assert_educational("Line one.\nRating: Strong Sell")
    assert error.value.findings[0]["line"] == 2


def test_disclaimers_pass_their_own_guard():
    assert_educational(SHORT_DISCLAIMER)
    assert_educational(long_disclaimer())


def test_prompt_never_asks_for_a_rating():
    # The prompt names what is forbidden, so the guard cannot run on it;
    # instead check that none of the old rating instructions survive.
    for old_instruction in ("Strong Buy", "Final Verdict", "Blueprint Score", "Signal:", "Conviction Score",
                            "Entry Trigger", "Probability Estimate"):
        assert old_instruction not in SYSTEM_PROMPT


def test_disclaimer_names_the_regulator():
    assert "FSCA" in long_disclaimer()
    assert "not financial advice" in long_disclaimer()
