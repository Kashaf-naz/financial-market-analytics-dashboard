# pages/utils/formatters.py

def fmt_money(x, currency=True, precision=2):
    """Format numbers into readable finance-friendly units."""
    if x is None:
        return "N/A"
    try:
        x = float(x)
    except Exception:
        return str(x)

    sign = "$" if currency else ""
    a = abs(x)
    if a >= 1e12:
        s = f"{x/1e12:.{precision}f}T"
    elif a >= 1e9:
        s = f"{x/1e9:.{precision}f}B"
    elif a >= 1e6:
        s = f"{x/1e6:.{precision}f}M"
    elif a >= 1e3:
        s = f"{x/1e3:.{precision}f}K"
    else:
        s = f"{x:.{precision}f}"
    return f"{sign}{s}"
