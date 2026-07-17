from unittest.mock import MagicMock

import pytest

from trading_bot.bot.client import BinanceFuturesClient
from trading_bot.bot.orders import place_order


@pytest.fixture
def client():
    c = MagicMock(spec=BinanceFuturesClient)
    c.place_market_order.return_value = {"orderId": 1, "status": "FILLED"}
    c.place_limit_order.return_value = {"orderId": 2, "status": "NEW"}
    c.place_stop_limit_order.return_value = {"orderId": 3, "status": "NEW"}
    c.place_oco_order.return_value = {"orderListId": 4, "listStatusType": "EXEC_STARTED"}
    return c


BASE_KW = dict(symbol="BTCUSDT", side="BUY", quantity=0.001)


class TestMarket:
    def test_places(self, client):
        resp = place_order(client, order_type="MARKET", **BASE_KW)
        client.place_market_order.assert_called_once_with("BTCUSDT", "BUY", 0.001)
        assert resp["orderId"] == 1


class TestLimit:
    def test_places(self, client):
        resp = place_order(client, order_type="LIMIT", **BASE_KW, price=70000)
        client.place_limit_order.assert_called_once_with("BTCUSDT", "BUY", 0.001, 70000)
        assert resp["orderId"] == 2

    def test_missing_price(self, client):
        with pytest.raises(ValueError, match="price is required for LIMIT"):
            place_order(client, order_type="LIMIT", **BASE_KW)


class TestStopLimit:
    def test_places(self, client):
        resp = place_order(client, order_type="STOP_LIMIT", **BASE_KW, price=71000, stop_price=70500)
        client.place_stop_limit_order.assert_called_once_with("BTCUSDT", "BUY", 0.001, 71000, 70500)
        assert resp["orderId"] == 3

    def test_missing_stop_price(self, client):
        with pytest.raises(ValueError, match="stop_price is required for STOP_LIMIT"):
            place_order(client, order_type="STOP_LIMIT", **BASE_KW, price=71000)


class TestOCO:
    def test_places(self, client):
        resp = place_order(client, order_type="OCO", **BASE_KW, price=71000, stop_price=69000)
        client.place_oco_order.assert_called_once_with("BTCUSDT", "BUY", 0.001, 71000, 69000)
        assert resp["orderListId"] == 4

    def test_missing_price(self, client):
        with pytest.raises(ValueError, match="price is required for OCO"):
            place_order(client, order_type="OCO", **BASE_KW, stop_price=69000)

    def test_missing_stop_price(self, client):
        with pytest.raises(ValueError, match="stop_price is required for OCO"):
            place_order(client, order_type="OCO", **BASE_KW, price=71000)
