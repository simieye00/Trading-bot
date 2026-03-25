# Trading Bot

A Python trading bot with technical indicators and a **Strategy Preset Menu** designed for 1-minute and 5-minute trading cycles.

---

## Features

### Indicators

| Indicator | Module | Purpose |
|-----------|--------|---------|
| SMA / EMA | `bot/indicators/moving_averages.py` | Trend direction filter (20-period EMA) |
| MACD | `bot/indicators/macd.py` | Trend momentum & reversal timing |
| RSI | `bot/indicators/rsi.py` | Overbought / oversold detection |
| Bollinger Bands | `bot/indicators/bollinger_bands.py` | Price channel & volatility |
| Candlestick Patterns | `bot/indicators/candlestick_patterns.py` | Hammer, Inverted Hammer, Bullish/Bearish Engulfing |

### Strategy Presets

| Key | Name | Logic |
|-----|------|-------|
| `trend_following` | Trend Following (EMA + MACD) | BUY when price > EMA(20) and MACD crosses up; SELL on reverse |
| `momentum` | Momentum (RSI + Bollinger Bands) | BUY when RSI < 30 and price ≤ lower band; SELL when RSI > 70 and price ≥ upper band |
| `candlestick` | Candlestick Patterns | Hammer / Bullish Engulfing → BUY below EMA; Inverted Hammer / Bearish Engulfing → SELL above EMA |
| `combined` | Combined | Majority vote across all three presets |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with the Combined strategy (non-interactive)
python main.py --strategy combined

# Run the interactive strategy menu
python main.py

# Use a custom config file
python main.py --config config.yaml --strategy momentum
```

### Programmatic Usage

```python
import pandas as pd
from bot.strategy_menu import StrategyMenu

menu = StrategyMenu()

# Non-interactive selection
strategy = menu.get("combined")

# ohlcv must have columns: open, high, low, close, volume (oldest first)
ohlcv = pd.read_csv("candles.csv")
signal = strategy.generate_signal(ohlcv)
print(signal)  # Signal.BUY / Signal.SELL / Signal.HOLD

# Interactive selection
strategy = menu.select_interactive()
```

---

## Configuration

Edit `config.yaml` to adjust indicator parameters and the default strategy:

```yaml
active_strategy: "combined"   # default preset used when no --strategy flag given

indicators:
  ema_period: 20
  rsi_overbought: 70
  rsi_oversold: 30
  bollinger_period: 20
  bollinger_std_dev: 2.0
  macd_fast: 12
  macd_slow: 26
  macd_signal: 9
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Project Structure

```
Trading-bot/
├── main.py                          # Entry point with CLI
├── config.yaml                      # Configuration file
├── requirements.txt
├── bot/
│   ├── indicators/
│   │   ├── moving_averages.py       # SMA, EMA
│   │   ├── macd.py                  # MACD
│   │   ├── rsi.py                   # RSI
│   │   ├── bollinger_bands.py       # Bollinger Bands
│   │   └── candlestick_patterns.py  # Hammer, Engulfing patterns
│   ├── strategies/
│   │   ├── base_strategy.py         # Abstract base + Signal enum
│   │   ├── trend_following.py       # EMA + MACD strategy
│   │   ├── momentum.py              # RSI + Bollinger Bands strategy
│   │   ├── candlestick.py           # Candlestick pattern strategy
│   │   └── combined.py              # Majority-vote combined strategy
│   └── strategy_menu.py             # Strategy Preset Menu
└── tests/
    ├── test_indicators.py
    └── test_strategies.py
```

Trading bot
