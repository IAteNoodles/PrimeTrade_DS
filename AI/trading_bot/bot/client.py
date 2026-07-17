import logging
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parents[2] / ".env")
except ImportError:
    pass

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
logger = logging.getLogger("trading_bot")


class BinanceFuturesClient:
    def __init__(self, api_key: str | None = None, api_secret: str | None = None):
        self.api_key = api_key or os.getenv("BINANCE_API") or os.getenv("BINANCE_TESTNET_API_KEY", "")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET") or os.getenv("BINANCE_TESTNET_API_SECRET", "")

        if not self.api_key or not self.api_secret:
            raise ValueError("API key and secret required. Set env vars or use AI/.env.")

        self._client = Client(self.api_key, self.api_secret)
        self._client.FUTURES_URL = TESTNET_BASE_URL

    def _call(self, method: str, **kwargs) -> dict:
        logger.debug("API %s | %s", method, {k: v for k, v in kwargs.items() if k not in ("apiKey", "apiSecret")})
        try:
            resp = self._client.futures_create_order(**kwargs)
            logger.debug("API response | %s", resp)
            return resp
        except BinanceAPIException as e:
            logger.error("Binance API error %s: %s", e.code, e.message)
            raise
        except BinanceRequestException as e:
            logger.error("Network error: %s", e)
            raise

    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        return self._call("MARKET", symbol=symbol, side=side, type="MARKET", quantity=quantity)

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> dict:
        return self._call("LIMIT", symbol=symbol, side=side, type="LIMIT", quantity=quantity, price=price, timeInForce="GTC")

    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, price: float, stop_price: float) -> dict:
        return self._call("STOP", symbol=symbol, side=side, type="STOP", quantity=quantity, price=price, stopPrice=stop_price, timeInForce="GTC")

    def place_oco_order(self, symbol: str, side: str, quantity: float, price: float, stop_price: float) -> dict:
        logger.debug("API OCO | symbol=%s side=%s qty=%s price=%s stop=%s", symbol, side, quantity, price, stop_price)
        try:
            resp = self._client._request_futures_api(
                "post", "orderList/oco", signed=True, data={
                    "symbol": symbol, "side": side, "quantity": quantity,
                    "price": price, "stopPrice": stop_price,
                    "stopLimitPrice": price, "stopLimitTimeInForce": "GTC",
                },
            )
            logger.debug("API response | %s", resp)
            return resp
        except BinanceAPIException as e:
            logger.error("Binance API error %s: %s", e.code, e.message)
            raise
        except BinanceRequestException as e:
            logger.error("Network error: %s", e)
            raise
