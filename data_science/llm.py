"""
AI adapter: the only module that talks to a model provider.

Swapping provider, changing models or switching AI off touches this file and
config.py, nothing else. Every call is logged with the model that answered,
because when a write-up is questioned later the first useful fact is which
model wrote it.

Off state: when AI is disabled or no key is set, complete() raises
AIUnavailableError and the caller falls back to the data-only report.
"""
import datetime
import logging

from config import DATA_DIR, SETTINGS

log = logging.getLogger(__name__)

USAGE_LOG = DATA_DIR / "usage_log.txt"

# USD per million tokens (input, output), Anthropic list prices as of October
# 2026. Used for an on-screen estimate only; check the live price list before
# relying on it.
PRICES = {
    "claude-fable-5-1": (10.0, 50.0),
    "claude-opus-5-5": (4.0, 20.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-opus-5": (5.0, 25.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-sonnet-4-6": (3.0, 15.0),
}


class AIUnavailableError(Exception):
    """AI is switched off, has no key, or the provider could not be reached."""


class AIRefusalError(Exception):
    """The model declined the request, and so did the fallback model."""


class AIResponseError(Exception):
    """The model answered, but the answer is unusable (empty or cut off)."""


def estimate_cost(model, input_tokens, output_tokens):
    """Estimated USD cost of one call, or None for a model with no known price."""
    price = PRICES.get(model)
    if not price:
        return None
    return (input_tokens * price[0] + output_tokens * price[1]) / 1_000_000


def _log_usage(model, input_tokens, output_tokens, cost, purpose):
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cost_text = "unknown" if cost is None else f"{cost:.6f}"
    line = (
        f"[{timestamp}] purpose={purpose} model={model} input_tokens={input_tokens} "
        f"output_tokens={output_tokens} est_cost_usd={cost_text}\n"
    )
    log.info(line.strip())
    try:
        with open(USAGE_LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError as e:
        log.warning("Could not write the usage log: %s", e)


def _call(client, model, system, user, max_tokens):
    import anthropic

    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    if SETTINGS.ai_effort:
        kwargs["output_config"] = {"effort": SETTINGS.ai_effort}
    try:
        # Streaming keeps a long report clear of the HTTP timeout on
        # non-streaming requests; we only need the final message.
        with client.messages.stream(**kwargs) as stream:
            return stream.get_final_message()
    except anthropic.AuthenticationError as e:
        raise AIUnavailableError("The Anthropic API key was rejected. Check ANTHROPIC_API_KEY in .env.") from e
    except anthropic.NotFoundError as e:
        raise AIUnavailableError(f"The model {model} was not found. Check AI_MODELS in .env.") from e
    except anthropic.RateLimitError as e:
        raise AIUnavailableError("The AI provider is rate limiting requests. Try again in a minute.") from e
    except anthropic.APIStatusError as e:
        raise AIUnavailableError(f"The AI provider returned an error ({e.status_code}): {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise AIUnavailableError("Could not reach the AI provider. Check the network connection.") from e


def complete(system, user, model=None, max_tokens=16000, purpose="report"):
    """Send one request and return {text, model, input_tokens, output_tokens, cost_usd}.

    On a refusal the request is retried once on AI_FALLBACK_MODEL. Raises
    AIUnavailableError, AIRefusalError or AIResponseError; never returns an
    empty or partial answer as if it were whole.
    """
    if not SETTINGS.ai_enabled:
        raise AIUnavailableError(SETTINGS.ai_off_reason)

    import anthropic

    model = model or SETTINGS.default_model
    client = anthropic.Anthropic(api_key=SETTINGS.anthropic_api_key)

    response = _call(client, model, system, user, max_tokens)
    if response.stop_reason == "refusal" and SETTINGS.ai_fallback_model and SETTINGS.ai_fallback_model != model:
        log.warning("%s declined the %s request; retrying on %s.", model, purpose, SETTINGS.ai_fallback_model)
        model = SETTINGS.ai_fallback_model
        response = _call(client, model, system, user, max_tokens)
    if response.stop_reason == "refusal":
        raise AIRefusalError(f"{model} declined to write this {purpose}. The data-only report is still available.")
    if response.stop_reason == "max_tokens":
        raise AIResponseError(
            f"The {purpose} from {model} was cut off before it finished. Nothing was saved; try again."
        )

    text = "".join(block.text for block in response.content if block.type == "text").strip()
    if not text:
        raise AIResponseError(f"{model} returned an empty {purpose}. Nothing was saved.")

    usage = response.usage
    served_by = getattr(response, "model", None) or model
    cost = estimate_cost(model, usage.input_tokens, usage.output_tokens)
    _log_usage(served_by, usage.input_tokens, usage.output_tokens, cost, purpose)
    return {
        "text": text,
        "model": served_by,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "cost_usd": cost,
    }
