# PrimeTrade - Binance Futures Testnet Trading Bot

CLI trading bot for Binance Futures Testnet (USDT-M). Places MARKET and LIMIT orders.

## Setup

1. Activate your Binance Futures Testnet account at [testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Generate API credentials with futures trading enabled
3. Set environment variables:

```bash
set BINANCE_TESTNET_API_KEY=your_api_key
set BINANCE_TESTNET_API_SECRET=your_api_secret
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Market BUY
python -m trading_bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit SELL
python -m trading_bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000

# Or via installed script
trading-bot --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

## Project Structure

```
trading_bot/
  bot/
    client.py         # Binance Futures API wrapper
    logging_config.py # Logging setup
    orders.py         # Order placement logic
    validators.py     # Input validation
  cli.py              # CLI entry point
```

## Assumptions

- Orders use USDT-M futures on testnet
- API keys from env vars `BINANCE_TESTNET_API_KEY` / `BINANCE_TESTNET_API_SECRET`
- LIMIT orders use GTC time-in-force
- Quantity/lot size validation is server-side
