import anthropic
import os
import datetime
from pathlib import Path

RESOURCES_DIR = Path(__file__).parent.parent.parent / "resources"
USAGE_LOG = Path(__file__).parent.parent / "usage_log.txt"

HAIKU = "claude-haiku-4-5"
SONNET = "claude-sonnet-4-6"
OPUS = "claude-opus-4-8"
MAX_TOKENS = {HAIKU: 1024, SONNET: 2048, OPUS: 4096}
COST_PER_INPUT = {HAIKU: 0.00000025, SONNET: 0.000003, OPUS: 0.000015}
COST_PER_OUTPUT = {HAIKU: 0.00000125, SONNET: 0.000015, OPUS: 0.000075}

_RESOURCE_FILES = [
    "about-me.md",
    "my_writing_style.md",
    "anti-ai-writing-style.md",
    "cant_prompt_blindly.md",
]


def load_resources_prompt():
    """Loads all four /resources/ identity and style files into one system prompt string."""
    parts = []
    for filename in _RESOURCE_FILES:
        path = RESOURCES_DIR / filename
        if path.exists():
            parts.append(f"### {filename}\n{path.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def generate_anthropic_brief(token, data_summary, report_text, model=HAIKU):
    """
    Takes the existing forensic report and raw data payload, returns a plain-English
    investment brief in Peter's voice, plus the estimated USD cost of the call.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY is not set in the environment.")

    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = load_resources_prompt()

    # Trim the report to avoid exceeding context; first 6000 chars covers all phases
    trimmed_report = report_text[:6000] if report_text else ""

    # Pull the key numbers from data_summary for extra grounding
    token_info = data_summary.get("token_info", {}) if data_summary else {}
    price = token_info.get("current_price", "N/A")
    market_cap = token_info.get("market_cap", "N/A")
    liquidity = token_info.get("liquidity_usd", "N/A")
    volume = token_info.get("24h_volume", "N/A")

    user_msg = (
        f"Token: {token}\n"
        f"Price: ${price} | Market Cap: ${market_cap} | Liquidity: ${liquidity} | 24h Volume: ${volume}\n\n"
        f"Forensic audit report (pipeline output):\n{trimmed_report}\n\n"
        "Write a plain-English investment brief for this token. "
        "Summarise the key findings from the forensic report in your own voice. "
        "State the verdict clearly, name the single biggest risk, and give one specific actionable observation. "
        "Do not repeat the forensic report verbatim; synthesise it. "
        "Keep the brief under 300 words."
    )

    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS[model],
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )

    brief = response.content[0].text
    usage = response.usage
    cost = (
        usage.input_tokens * COST_PER_INPUT[model]
        + usage.output_tokens * COST_PER_OUTPUT[model]
    )
    log_usage(model, usage.input_tokens, usage.output_tokens, cost)
    return brief, cost


def log_usage(model, input_tokens, output_tokens, est_cost_usd):
    """Appends one timestamped line to usage_log.txt after each API call."""
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = (
        f"[{timestamp}] model={model} "
        f"input_tokens={input_tokens} "
        f"output_tokens={output_tokens} "
        f"est_cost_usd={est_cost_usd:.8f}\n"
    )
    with open(USAGE_LOG, "a", encoding="utf-8") as f:
        f.write(line)
