import pytest
from trading_bot.bot.validators import (
    validate_symbol, validate_side, validate_order_type,
    validate_quantity, validate_price, validate_stop_price,
)


class TestValidateSymbol:
    def test_valid(self):
        assert validate_symbol("BTCUSDT") == "BTCUSDT"

    def test_lowercase_stripped_and_uppercased(self):
        assert validate_symbol("  btcusdt  ") == "BTCUSDT"

    def test_too_short(self):
        with pytest.raises(ValueError, match="Invalid symbol"):
            validate_symbol("AB")

    def test_invalid_chars(self):
        with pytest.raises(ValueError, match="Invalid symbol"):
            validate_symbol("BTC-USD")


class TestValidateSide:
    def test_buy(self):
        assert validate_side("BUY") == "BUY"

    def test_sell_case_insensitive(self):
        assert validate_side("sell") == "SELL"

    def test_invalid(self):
        with pytest.raises(ValueError, match="Side must be BUY/SELL"):
            validate_side("HOLD")


class TestValidateOrderType:
    def test_market(self):
        assert validate_order_type("MARKET") == "MARKET"

    def test_limit(self):
        assert validate_order_type("limit") == "LIMIT"

    def test_stop_limit(self):
        assert validate_order_type("stop_limit") == "STOP_LIMIT"

    def test_oco(self):
        assert validate_order_type("oco") == "OCO"

    def test_invalid(self):
        with pytest.raises(ValueError, match="Order type must be MARKET/LIMIT/STOP_LIMIT/OCO"):
            validate_order_type("GRID")


class TestValidateQuantity:
    def test_valid(self):
        assert validate_quantity("0.001") == 0.001

    def test_positive_int(self):
        assert validate_quantity("1") == 1.0

    def test_zero(self):
        with pytest.raises(ValueError, match="Quantity must be positive"):
            validate_quantity("0")

    def test_negative(self):
        with pytest.raises(ValueError, match="Quantity must be positive"):
            validate_quantity("-1")

    def test_non_numeric(self):
        with pytest.raises(ValueError, match="Quantity must be a number"):
            validate_quantity("abc")


class TestValidatePrice:
    def test_valid(self):
        assert validate_price("70000.50") == 70000.50

    def test_zero(self):
        with pytest.raises(ValueError, match="Price must be positive"):
            validate_price("0")

    def test_non_numeric(self):
        with pytest.raises(ValueError, match="Price must be a number"):
            validate_price("free")


class TestValidateStopPrice:
    def test_valid(self):
        assert validate_stop_price("69000") == 69000.0

    def test_zero(self):
        with pytest.raises(ValueError, match="Stop price must be positive"):
            validate_stop_price("0")

    def test_non_numeric(self):
        with pytest.raises(ValueError, match="Stop price must be a number"):
            validate_stop_price("abc")
