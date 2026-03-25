"""Trend-Following strategy preset.

Logic
-----
* Use a 20-period EMA as a trend direction filter:
  - Price above EMA → only consider BUY signals.
  - Price below EMA → only consider SELL signals.
* Use MACD crossovers to time entries:
  - MACD line crosses **above** signal line → BUY (when price > EMA).
  - MACD line crosses **below** signal line → SELL (when price < EMA).
* Otherwise → HOLD.
"""

from __future__ import annotations

import pandas as pd

from bot.indicators import ema, macd
from .base_strategy import BaseStrategy, Signal


class TrendFollowingStrategy(BaseStrategy):
    """EMA + MACD trend-following strategy.

    Parameters
    ----------
    ema_period:
        Period for the trend-direction EMA filter (default 20).
    macd_fast:
        MACD fast EMA period (default 12).
    macd_slow:
        MACD slow EMA period (default 26).
    macd_signal:
        MACD signal line EMA period (default 9).
    """

    name = "Trend Following (EMA + MACD)"

    def __init__(
        self,
        ema_period: int = 20,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
    ) -> None:
        self.ema_period = ema_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal

    def generate_signal(self, ohlcv: pd.DataFrame) -> Signal:
        """Return BUY, SELL, or HOLD based on EMA filter + MACD crossover."""
        close = ohlcv["close"]

        if len(close) < self.macd_slow + self.macd_signal:
            return Signal.HOLD

        ema_values = ema(close, self.ema_period)
        macd_result = macd(close, self.macd_fast, self.macd_slow, self.macd_signal)

        current_price = close.iloc[-1]
        current_ema = ema_values.iloc[-1]
        macd_now = macd_result.macd_line.iloc[-1]
        signal_now = macd_result.signal_line.iloc[-1]
        macd_prev = macd_result.macd_line.iloc[-2]
        signal_prev = macd_result.signal_line.iloc[-2]

        if any(v != v for v in (current_ema, macd_now, signal_now, macd_prev, signal_prev)):
            # NaN guard
            return Signal.HOLD

        bullish_crossover = macd_prev <= signal_prev and macd_now > signal_now
        bearish_crossover = macd_prev >= signal_prev and macd_now < signal_now

        if current_price > current_ema and bullish_crossover:
            return Signal.BUY
        if current_price < current_ema and bearish_crossover:
            return Signal.SELL
        return Signal.HOLD
