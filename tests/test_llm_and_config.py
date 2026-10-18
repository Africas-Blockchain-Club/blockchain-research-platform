import dataclasses

import pytest

from config import Settings
from data_science import llm


def test_ai_is_off_without_a_key(monkeypatch):
    monkeypatch.setenv("AI_ENABLED", "true")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    settings = Settings()
    assert not settings.ai_enabled
    assert "ANTHROPIC_API_KEY" in settings.ai_off_reason


def test_payments_are_off_by_default(monkeypatch):
    monkeypatch.delenv("PAYMENTS_ENABLED", raising=False)
    assert Settings().payments_enabled is False


def test_model_list_comes_from_config(monkeypatch):
    monkeypatch.setenv("AI_MODELS", "model-a, model-b")
    settings = Settings()
    assert settings.ai_models == ("model-a", "model-b")
    assert settings.default_model == "model-a"


def test_complete_fails_loudly_when_ai_is_off(monkeypatch):
    off = dataclasses.replace(Settings(), ai_switch=False)
    monkeypatch.setattr(llm, "SETTINGS", off)
    with pytest.raises(llm.AIUnavailableError):
        llm.complete("system", "user")


def test_cost_estimate_is_none_for_unknown_models():
    assert llm.estimate_cost("unknown-model", 1000, 1000) is None
    assert llm.estimate_cost("claude-opus-5-5", 1_000_000, 0) == pytest.approx(4.0)


def test_public_deployments_can_require_payment_for_ai(monkeypatch):
    monkeypatch.setenv("AI_REQUIRES_PAYMENT", "true")
    monkeypatch.delenv("PAYMENTS_ENABLED", raising=False)
    settings = Settings()
    assert settings.ai_requires_payment and not settings.payments_enabled
