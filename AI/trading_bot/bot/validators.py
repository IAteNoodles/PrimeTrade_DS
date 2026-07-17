import re

VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT", "STOP_LIMIT", "OCO")
SYMBOL_RE = re.compile(r"^[A-Z0-9]{5,20}$")


def _to_float(val: str, name: str) -> float:
    try:
        n = float(val)
    except (ValueError, TypeError):
        raise ValueError(f"{name} must be a number, got {val!r}")
    if n <= 0:
        raise ValueError(f"{name} must be positive, got {n}")
    return n


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not SYMBOL_RE.match(s):
        raise ValueError(f"Invalid symbol: {symbol!r}")
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValueError(f"Side must be BUY/SELL, got {side!r}")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValueError(f"Order type must be MARKET/LIMIT/STOP_LIMIT/OCO, got {order_type!r}")
    return t


def validate_quantity(qty: str) -> float:
    return _to_float(qty, "Quantity")


def validate_price(price: str) -> float:
    return _to_float(price, "Price")


def validate_stop_price(sp: str) -> float:
    return _to_float(sp, "Stop price")
