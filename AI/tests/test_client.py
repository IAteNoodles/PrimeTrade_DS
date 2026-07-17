from unittest.mock import patch, MagicMock, call

import pytest

from trading_bot.bot.client import BinanceFuturesClient, TESTNET_BASE_URL


@pytest.fixture
def mock_client():
    with patch("trading_bot.bot.client.Client") as MockClient:
        instance = MockClient.return_value
        instance.futures_create_order = MagicMock()
        instance._request_futures_api = MagicMock()
        yield BinanceFuturesClient(
            api_key="test_key", api_secret="test_secret"
        ), instance


class TestInit:
    def test_sets_testnet_url(self, mock_client):
        c, mock = mock_client
        assert c._client.FUTURES_URL == TESTNET_BASE_URL

    def test_raises_without_creds(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key and secret required"):
                BinanceFuturesClient(api_key="", api_secret="")


class TestMarketOrder:
    def test_places_correctly(self, mock_client):
        c, mock = mock_client
        mock.futures_create_order.return_value = {"orderId": 123, "status": "FILLED"}
        resp = c.place_market_order("BTCUSDT", "BUY", 0.001)
        mock.futures_create_order.assert_called_once_with(
            symbol="BTCUSDT", side="BUY", type="MARKET", quantity=0.001
        )
        assert resp["orderId"] == 123


class TestLimitOrder:
    def test_places_correctly(self, mock_client):
        c, mock = mock_client
        mock.futures_create_order.return_value = {"orderId": 456, "status": "NEW"}
        resp = c.place_limit_order("BTCUSDT", "SELL", 0.001, 70000)
        mock.futures_create_order.assert_called_once_with(
            symbol="BTCUSDT", side="SELL", type="LIMIT",
            quantity=0.001, price=70000, timeInForce="GTC",
        )
        assert resp["orderId"] == 456


class TestStopLimitOrder:
    def test_places_correctly(self, mock_client):
        c, mock = mock_client
        mock.futures_create_order.return_value = {"orderId": 789, "status": "NEW"}
        resp = c.place_stop_limit_order("BTCUSDT", "BUY", 0.001, 71000, 70500)
        mock.futures_create_order.assert_called_once_with(
            symbol="BTCUSDT", side="BUY", type="STOP",
            quantity=0.001, price=71000, stopPrice=70500, timeInForce="GTC",
        )
        assert resp["orderId"] == 789


class TestOCOOrder:
    def test_places_correctly(self, mock_client):
        c, mock = mock_client
        mock._request_futures_api.return_value = {
            "orderListId": 999, "listStatusType": "EXEC_STARTED",
            "orderReports": [{"orderId": 10}, {"orderId": 11}],
        }
        resp = c.place_oco_order("BTCUSDT", "SELL", 0.001, 71000, 69000)
        mock._request_futures_api.assert_called_once_with(
            "post", "orderList/oco", signed=True, data={
                "symbol": "BTCUSDT", "side": "SELL", "quantity": 0.001,
                "price": 71000, "stopPrice": 69000,
                "stopLimitPrice": 71000, "stopLimitTimeInForce": "GTC",
            },
        )
        assert resp["orderListId"] == 999
