import argparse
import logging
import sys

from binance.exceptions import BinanceAPIException, BinanceRequestException
from rich.console import Console
from rich.table import Table

from .bot.client import BinanceFuturesClient
from .bot.logging_config import setup_logging
from .bot.orders import place_order
from .bot.validators import (
    validate_order_type, validate_price, validate_stop_price,
    validate_quantity, validate_side, validate_symbol,
)

console = Console()
logger = logging.getLogger("trading_bot")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="trading-bot", description="Place orders on Binance Futures Testnet")
    p.add_argument("--symbol", required=True)
    p.add_argument("--side", required=True, choices=["BUY", "SELL"])
    p.add_argument("--type", required=True, choices=["MARKET", "LIMIT", "STOP_LIMIT", "OCO"], dest="order_type")
    p.add_argument("--quantity", required=True)
    p.add_argument("--price")
    p.add_argument("--stop-price")
    p.add_argument("--log-file", default="trading_bot.log")
    return p


def _table(title: str, rows: list) -> Table:
    t = Table(title=title)
    t.add_column("Field", style="cyan")
    t.add_column("Value", style="white")
    for k, v in rows:
        t.add_row(k, str(v) if v is not None else "—")
    return t


def main():
    args = build_parser().parse_args()
    setup_logging(args.log_file)

    try:
        kwargs = {
            "symbol": validate_symbol(args.symbol),
            "side": validate_side(args.side),
            "order_type": validate_order_type(args.order_type),
            "quantity": validate_quantity(args.quantity),
            "price": validate_price(args.price) if args.price else None,
            "stop_price": validate_stop_price(args.stop_price) if args.stop_price else None,
        }

        console.print(_table("Order Request", [
            ("Symbol", kwargs["symbol"]), ("Side", kwargs["side"]),
            ("Type", kwargs["order_type"]), ("Quantity", kwargs["quantity"]),
            ("Price", kwargs["price"]), ("Stop Price", kwargs["stop_price"]),
        ]))

        client = BinanceFuturesClient()
        resp = place_order(client, **kwargs)

        if "orderReports" in resp:
            reports = resp["orderReports"]
            for r in reports:
                console.print(_table(f"OCO Leg — {r['side']} {r['type']}", [
                    ("Order ID", r["orderId"]), ("Status", r["status"]),
                    ("Price", r["price"]), ("Stop Price", r.get("stopPrice", "N/A")),
                    ("Executed Qty", r["executedQty"]),
                ]))
            console.print(_table("OCO Summary", [
                ("Order List ID", resp.get("orderListId")),
                ("Status", resp.get("listStatusType")),
            ]))
        else:
            console.print(_table("Order Response", [
                ("Order ID", resp.get("orderId")),
                ("Status", resp.get("status")),
                ("Executed Qty", resp.get("executedQty", "N/A")),
                ("Avg Price", resp.get("avgPrice", "N/A")),
            ]))

        console.print("[bold green]SUCCESS[/] Order placed.\n")

    except BinanceAPIException as e:
        logger.error("Binance API error %s: %s", e.code, e.message)
        console.print(f"\n[bold red]Binance API Error ({e.code})[/] {e.message}\n")
        sys.exit(1)
    except BinanceRequestException as e:
        logger.error("Network error: %s", e)
        console.print(f"\n[bold red]Network Error[/] {e}\n")
        sys.exit(1)
    except ValueError as e:
        logger.error("Validation error: %s", e)
        console.print(f"\n[bold red]Invalid Input[/] {e}\n")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        console.print(f"\n[bold red]Unexpected Error[/] {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
