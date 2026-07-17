import logging

from .client import BinanceFuturesClient

logger = logging.getLogger("trading_bot")

ORDER_HANDLERS = {
    "MARKET": lambda c, kw: c.place_market_order(kw["symbol"], kw["side"], kw["quantity"]),
    "LIMIT": lambda c, kw: c.place_limit_order(kw["symbol"], kw["side"], kw["quantity"], kw["price"]),
    "STOP_LIMIT": lambda c, kw: c.place_stop_limit_order(kw["symbol"], kw["side"], kw["quantity"], kw["price"], kw["stop_price"]),
    "OCO": lambda c, kw: c.place_oco_order(kw["symbol"], kw["side"], kw["quantity"], kw["price"], kw["stop_price"]),
}

REQUIRED_FOR = {
    "LIMIT": ["price"],
    "STOP_LIMIT": ["price", "stop_price"],
    "OCO": ["price", "stop_price"],
}


def _check_required(order_type: str, kwargs: dict):
    for field in REQUIRED_FOR.get(order_type, []):
        if kwargs.get(field) is None:
            raise ValueError(f"{field} is required for {order_type} orders")


def place_order(client: BinanceFuturesClient, **kwargs) -> dict:
    order_type = kwargs["order_type"]
    _check_required(order_type, kwargs)

    logger.info(
        "Placing %s %s | symbol=%s qty=%s price=%s stop=%s",
        kwargs["side"], order_type, kwargs["symbol"],
        kwargs["quantity"], kwargs.get("price", "N/A"), kwargs.get("stop_price", "N/A"),
    )

    handler = ORDER_HANDLERS.get(order_type)
    if handler is None:
        raise ValueError(f"Unsupported order type: {order_type}")

    resp = handler(client, kwargs)

    logger.info(
        "Done | orderId=%s status=%s executedQty=%s",
        resp.get("orderId") or resp.get("orderListId", "N/A"),
        resp.get("status", "N/A"),
        resp.get("executedQty", "0"),
    )
    return resp
