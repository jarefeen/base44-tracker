def abbreviate_number(n) -> str:
    """1234 -> '1.2K', 1234567 -> '1.2M'"""
    if n is None:
        return "N/A"
    n = float(n)
    for suffix, threshold in [("B", 1e9), ("M", 1e6), ("K", 1e3)]:
        if abs(n) >= threshold:
            return f"{n / threshold:.1f}{suffix}"
    return f"{n:,.0f}"


def format_delta(current, previous) -> str | None:
    if current is None or previous is None or previous == 0:
        return None
    pct = ((current - previous) / abs(previous)) * 100
    return f"{pct:+.1f}%"
