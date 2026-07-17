import pytest
from trading_bot.cli import build_parser


class TestCLIParser:
    def test_market(self):
        args = build_parser().parse_args([
            "--symbol", "BTCUSDT", "--side", "BUY",
            "--type", "MARKET", "--quantity", "0.001",
        ])
        assert args.order_type == "MARKET"

    def test_limit(self):
        args = build_parser().parse_args([
            "--symbol", "ETHUSDT", "--side", "SELL",
            "--type", "LIMIT", "--quantity", "0.01", "--price", "4000",
        ])
        assert args.order_type == "LIMIT"
        assert args.price == "4000"

    def test_stop_limit(self):
        args = build_parser().parse_args([
            "--symbol", "BTCUSDT", "--side", "BUY",
            "--type", "STOP_LIMIT", "--quantity", "0.001",
            "--price", "71000", "--stop-price", "70500",
        ])
        assert args.order_type == "STOP_LIMIT"
        assert args.stop_price == "70500"

    def test_oco(self):
        args = build_parser().parse_args([
            "--symbol", "BTCUSDT", "--side", "SELL",
            "--type", "OCO", "--quantity", "0.001",
            "--price", "72000", "--stop-price", "69000",
        ])
        assert args.order_type == "OCO"
        assert args.stop_price == "69000"

    def test_invalid_side_rejected(self):
        with pytest.raises(SystemExit):
            build_parser().parse_args([
                "--symbol", "BTCUSDT", "--side", "HOLD",
                "--type", "MARKET", "--quantity", "0.001",
            ])
