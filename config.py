"""
Every setting the platform reads, in one place.

Provider choice, model names, feature switches and branding all come from the
environment (.env), so turning a feature off or rebranding a fork is a config
change, never a code change. Nothing else in the codebase should call
os.getenv for these values; import SETTINGS instead.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = ROOT_DIR / "reports"
BLUEPRINTS_DIR = ROOT_DIR / "blueprints"
IMAGES_DIR = ROOT_DIR / "data" / "images"

# Bump on every release. The footer shows it so a screenshot always says
# which build it came from.
BUILD = "2026.10.18-1"

# Current Claude models, cheapest last. Haiku is left out on purpose: a
# research write-up needs the depth of Sonnet or Opus.
DEFAULT_AI_MODELS = ("claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-1")


def _flag(name, default):
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _list(name, default):
    value = os.getenv(name, "").strip()
    if not value:
        return tuple(default)
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    # Branding. A fork changes these values and nothing else.
    brand_name: str = field(default_factory=lambda: os.getenv("BRAND_NAME", "Africa's Blockchain Club"))
    brand_short: str = field(default_factory=lambda: os.getenv("BRAND_SHORT", "ABC"))
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Blockchain Research Platform"))
    brand_accent: str = field(default_factory=lambda: os.getenv("BRAND_ACCENT", "#0b57c9"))
    # The accent on a dark ground must be lighter to keep AA contrast.
    brand_accent_dark: str = field(default_factory=lambda: os.getenv("BRAND_ACCENT_DARK", "#5ea3ff"))
    repo_url: str = field(default_factory=lambda: os.getenv(
        "REPO_URL", "https://github.com/Africas-Blockchain-Club/blockchain-research-platform"))

    # AI. Off when disabled or when no key is present; the data-only report
    # is the defined off state.
    ai_switch: bool = field(default_factory=lambda: _flag("AI_ENABLED", True))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", "").strip())
    ai_models: tuple = field(default_factory=lambda: _list("AI_MODELS", DEFAULT_AI_MODELS))
    ai_fallback_model: str = field(default_factory=lambda: os.getenv("AI_FALLBACK_MODEL", "claude-opus-5-5").strip())
    # Reasoning depth. Leave empty for a model that does not accept the effort setting.
    ai_effort: str = field(default_factory=lambda: os.getenv("AI_EFFORT", "high").strip())

    # Chart screenshots need Playwright and a browser; switch off on small hosts.
    screenshots_enabled: bool = field(default_factory=lambda: _flag("SCREENSHOTS_ENABLED", True))

    # Testnet payment demo. Off by default: with it off, reports are free.
    payments_enabled: bool = field(default_factory=lambda: _flag("PAYMENTS_ENABLED", False))

    # Exchange rate used only when the live rate cannot be fetched.
    fallback_usd_zar: float = field(default_factory=lambda: float(os.getenv("FALLBACK_USD_ZAR", "18.0")))

    @property
    def ai_enabled(self):
        return self.ai_switch and bool(self.anthropic_api_key)

    @property
    def ai_off_reason(self):
        if not self.ai_switch:
            return "AI is switched off in configuration (AI_ENABLED=false)."
        if not self.anthropic_api_key:
            return "No ANTHROPIC_API_KEY is set, so AI write-ups are switched off."
        return ""

    @property
    def default_model(self):
        return self.ai_models[0]


SETTINGS = Settings()
