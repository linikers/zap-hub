#!/usr/bin/env python3
"""
Formata valor numérico no formato monetário brasileiro (R$ 1.234,56).

Uso:
  python3 fmt_brl.py 24914.70
  python3 fmt_brl.py 3985.68 --no-sign
  echo "20929.02" | python3 fmt_brl.py

Útil para relatórios da API do Mercado Livre onde os valores vêm como float
e precisam de formatação BR para WhatsApp/relatórios.
"""

import sys


def fmt_brl(val: float, show_sign: bool = True) -> str:
    """Format a number as Brazilian currency string.

    Examples:
        fmt_brl(24914.70)      -> "R$ 24.914,70"
        fmt_brl(3985.68)       -> "R$ 3.985,68"
        fmt_brl(3985.68, False) -> "3.985,68"
    """
    formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if show_sign:
        return f"R$ {formatted}"
    return formatted


if __name__ == "__main__":
    # Read from argument or stdin
    if len(sys.argv) > 1:
        raw = sys.argv[1]
    else:
        raw = sys.stdin.read().strip()

    show_sign = True
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--no-sign" in sys.argv:
        show_sign = False

    try:
        value = float(raw.replace(".", "").replace(",", "."))  # handle already-formatted input
    except ValueError:
        value = float(raw)

    print(fmt_brl(value, show_sign=show_sign))
