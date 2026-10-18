"""Number formatting shared by the risk checks, the data report and the UI."""


def to_float(value):
    """Return value as a float, or None when it is missing or not a number."""
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number


def usd(value, digits=0):
    number = to_float(value)
    if number is None:
        return "N/A"
    if digits == 0 and abs(number) < 10:
        digits = 4 if abs(number) < 1 else 2
    return f"${number:,.{digits}f}"


def usd_zar(value, usd_zar_rate, digits=0):
    """USD with the Rand equivalent in brackets, the house style for currency."""
    number = to_float(value)
    if number is None:
        return "N/A"
    rand = number * usd_zar_rate
    zar_digits = digits
    if digits == 0 and abs(rand) < 10:
        zar_digits = 4 if abs(rand) < 1 else 2
    return f"{usd(number, digits)} (R{rand:,.{zar_digits}f})"


def pct(value, digits=2):
    number = to_float(value)
    if number is None:
        return "N/A"
    return f"{number:,.{digits}f}%"


def count(value):
    number = to_float(value)
    if number is None:
        return "N/A"
    return f"{number:,.0f}"
