"""Momentum strategy preset.

Logic
-----
* RSI thresholds:
  - RSI > *overbought* (default 70) → SELL signal.
  - RSI < *oversold*   (default 30) → BUY signal.
* Bollinger Band confirmation:
  - Price touches or breaks below the **lower** band → reinforces BUY.
  - Price touches or breaks above the **upper** band → reinforces SELL.
* Both RSI **and** Bollinger Band must agree for the signal to fire; otherwise
  HOLD is returned.
"""

from __future__ import annotations

import pandas as pd

from bot.indicators import bollinger_bands, rsi
from .base_strategy import BaseStrategy, Signal


class MomentumStrategy(BaseStrategy):
    """RSI + Bollinger Bands momentum/mean-reversion strategy.

    Parameters
    ----------
    rsi_period:
        RSI calculation period (default 14).
    rsi_overbought:
        RSI level treated as overbought (default 70).
    rsi_oversold:
        RSI level treated as oversold (default 30).
    bb_period:
        Bollinger Bands SMA period (default 20).
    bb_std_dev:
        Standard deviation multiplier for the bands (default 2.0).
    """

    name = "Momentum (RSI + Bollinger Bands)"

    def __init__(
        self,
        rsi_period: int = 14,
        rsi_overbought: float = 70.0,
        rsi_oversold: float = 30.0,
        bb_period: int = 20,
        bb_std_dev: float = 2.0,
    ) -> None:
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.bb_period = bb_period
        self.bb_std_dev = bb_std_dev

    def generate_signal(self, ohlcv: pd.DataFrame) -> Signal:
        """Return BUY when RSI oversold + price near lower band; SELL when overbought."""
        close = ohlcv["close"]

        min_bars = max(self.rsi_period, self.bb_period) + 1
        if len(close) < min_bars:
            return Signal.HOLD

        rsi_values = rsi(close, self.rsi_period)
        bb = bollinger_bands(close, self.bb_period, self.bb_std_dev)

        current_rsi = rsi_values.iloc[-1]
        current_price = close.iloc[-1]
        upper = bb.upper.iloc[-1]
        lower = bb.lower.iloc[-1]

        if current_rsi != current_rsi or upper != upper or lower != lower:
            # NaN guard
            return Signal.HOLD

        oversold = current_rsi < self.rsi_oversold
        overbought = current_rsi > self.rsi_overbought
        near_lower_band = current_price <= lower
        near_upper_band = current_price >= upper

        if oversold and near_lower_band:
            return Signal.BUY
        if overbought and near_upper_band:
            return Signal.SELL
        return Signal.HOLD
