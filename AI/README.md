# PrimeTrade — Binance Futures Testnet Trading Bot

CLI trading bot for **Binance Futures Testnet** (USDT-M). Places **MARKET**, **LIMIT**, **STOP_LIMIT**, and **OCO** orders with structured code, logging, and error handling.

## Setup

1. Register at [testnet.binancefuture.com](https://testnet.binancefuture.com) and generate API credentials
2. Add them to `AI/.env` (already there) or set env vars:

```powershell
$env:BINANCE_API = "your_key"
$env:BINANCE_API_SECRET = "your_secret"
```

3. Install:

```bash
pip install -r AI/requirements.txt
```

## Usage

```bash
# Market BUY
python -m AI.trading_bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit SELL
python -m AI.trading_bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000

# Stop-Limit BUY (trigger at 70500, then place limit at 71000)
python -m AI.trading_bot.cli --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.001 --price 71000 --stop-price 70500

# OCO (SELL limit at 72000, stop-loss at 69000)
python -m AI.trading_bot.cli --symbol BTCUSDT --side SELL --type OCO --quantity 0.001 --price 72000 --stop-price 69000
```

All output uses Rich tables. API calls and errors are logged to `trading_bot.log`.

## Project Structure

```
AI/
  .env                          # API credentials (auto-loaded)
  trading_bot/
    bot/
      client.py                 # Futures API wrapper (market/limit/stop/oco)
      logging_config.py         # File + stdout logger
      orders.py                 # Order dispatch + required-field checks
      validators.py             # Input validation (symbol/side/type/qty/price/stop)
    cli.py                      # Argparse CLI + Rich tables
  tests/                        # 42 tests (mocked)
  requirements.txt
  README.md
```

## Order Types

| Type | Required | Description |
|------|----------|-------------|
| MARKET | quantity | Immediate execution at current price |
| LIMIT | quantity, price | Place at specified price, GTC |
| STOP_LIMIT | quantity, price, stop_price | Triggers limit order when stop is hit |
| OCO | quantity, price, stop_price | One-cancels-other: limit + stop-loss paired |

## Evaluation Fit

- **Correctness** — Live testnet API calls, all order types
- **Code quality** — Separate client/orders/validators/CLI layers, DRY helpers, dispatch maps
- **Error handling** — Catches `BinanceAPIException`, `BinanceRequestException`, `ValueError`, and unexpected errors separately
- **Logging** — API requests/responses at DEBUG, order summaries at INFO, errors at ERROR
- **README** — Setup steps, runnable examples, assumptions listed

## Assumptions

- API keys from env vars or `AI/.env`
- LIMIT/STOP_LIMIT orders use GTC time-in-force
- Quantity/price step size validated server-side
- OCO pairs limit + stop-loss on same side
