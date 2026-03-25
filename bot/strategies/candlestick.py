"""Candlestick Pattern strategy preset.

Logic
-----
* Scan the last two candles for reversal patterns:
  - **Hammer** or **Bullish Engulfing** → BUY signal.
  - **Inverted Hammer** (in a downtrend) or **Bearish Engulfing** → SELL signal.
* A 20-period EMA is used as a trend filter so that:
  - Hammer / Bullish Engulfing signals are only taken when price is **below**
    the EMA (potential bounce from oversold territory).
  - Inverted Hammer / Bearish Engulfing signals are only taken when price is
    **above** the EMA (potential rejection from overbought territory).
"""

from __future__ import annotations

import pandas as pd

from bot.indicators import ema
from bot.indicators.candlestick_patterns import (
    is_bullish_engulfing,
    is_bearish_engulfing,
    is_hammer,
    is_inverted_hammer,
)
from .base_strategy import BaseStrategy, Signal


class CandlestickStrategy(BaseStrategy):
    """Candlestick reversal pattern strategy with EMA trend filter.

    Parameters
    ----------
    ema_period:
        Period for the EMA trend filter (default 20).
    """

    name = "Candlestick Patterns (Hammer / Engulfing)"

    def __init__(self, ema_period: int = 20) -> None:
        self.ema_period = ema_period

    def generate_signal(self, ohlcv: pd.DataFrame) -> Signal:
        """Return BUY/SELL based on candlestick reversal patterns + EMA filter."""
        if len(ohlcv) < self.ema_period + 1:
            return Signal.HOLD

        close = ohlcv["close"]
        ema_values = ema(close, self.ema_period)
        current_ema = ema_values.iloc[-1]

        if current_ema != current_ema:
            return Signal.HOLD

        # Current and previous candles
        curr = ohlcv.iloc[-1]
        prev = ohlcv.iloc[-2]

        curr_o, curr_h, curr_l, curr_c = curr["open"], curr["high"], curr["low"], curr["close"]
        prev_o, prev_c = prev["open"], prev["close"]

        price_below_ema = curr_c < current_ema
        price_above_ema = curr_c > current_ema

        # Bullish reversal signals (look for them when price is below EMA)
        hammer = is_hammer(curr_o, curr_h, curr_l, curr_c)
        bull_engulf = is_bullish_engulfing(prev_o, prev_c, curr_o, curr_c)

        if price_below_ema and (hammer or bull_engulf):
            return Signal.BUY

        # Bearish reversal signals (look for them when price is above EMA)
        inv_hammer = is_inverted_hammer(curr_o, curr_h, curr_l, curr_c)
        bear_engulf = is_bearish_engulfing(prev_o, prev_c, curr_o, curr_c)

        if price_above_ema and (inv_hammer or bear_engulf):
            return Signal.SELL

        return Signal.HOLD
