# Trading Bot

A Python trading bot that applies technical analysis indicators and candlestick pattern recognition to generate **BUY / SELL / HOLD** signals for 1-minute and 5-minute trading cycles.

---

## Features

### Trend Tracing
| Indicator | Description |
|-----------|-------------|
| **SMA / EMA** | Simple and Exponential Moving Averages. The bot only looks for BUY signals when the price is above the 20-period EMA (and vice-versa for SELL). |
| **MACD** | Moving Average Convergence Divergence — detects trend reversals via crossovers of the MACD line and the signal line. |

### Momentum & Volatility
| Indicator | Description |
|-----------|-------------|
| **RSI** | Relative Strength Index. RSI > 70 → overbought (prepare to Sell); RSI < 30 → oversold (prepare to Buy). |
| **Bollinger Bands** | Price channel using a rolling SMA ± 2 standard deviations. Price touching the outer bands signals a potential reversion. |

### Candlestick Pattern Recognition
| Pattern | Signal |
|---------|--------|
| **Hammer** | Bullish reversal |
| **Inverted Hammer** | Bullish reversal |
| **Bullish Engulfing** | Strong bullish reversal |
| **Bearish Engulfing** | Strong bearish reversal |

---

## Strategy Preset Menu

Three built-in strategies are available:

| Key | Strategy | Logic |
|-----|----------|-------|
| `trend` | **Trend Following** | EMA direction + MACD crossover |
| `momentum` | **Momentum** | RSI oversold/overbought + Bollinger Band touch |
| `combined` | **Combined** | All indicators vote; signal fires when ≥ 2 agree |

---

## Project Structure

```
trading_bot/
├── indicators/
│   ├── moving_averages.py      # SMA, EMA
│   ├── macd.py                 # MACD
│   ├── rsi.py                  # RSI
│   ├── bollinger_bands.py      # Bollinger Bands
│   └── candlestick_patterns.py # Hammer, Engulfing, …
├── strategies/
│   ├── base_strategy.py        # Abstract base class
│   ├── trend_following.py      # EMA + MACD strategy
│   ├── momentum.py             # RSI + Bollinger Bands strategy
│   └── combined.py             # All-in-one strategy
└── main.py                     # Interactive strategy preset menu
tests/
├── test_indicators.py
└── test_strategies.py
```

---

## Getting Started

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the interactive bot

```bash
python -m trading_bot.main
```

The bot displays the strategy preset menu, prompts you to choose a strategy, and prints the generated signal using built-in synthetic demo data. Supply your own OHLC `pandas.DataFrame` (columns: `open`, `high`, `low`, `close`) via the `run(df)` function in `trading_bot/main.py`.

### Run tests

```bash
python -m pytest tests/ -v
```
