"""Combined strategy preset – aggregates all three strategy presets.

Logic
-----
Each sub-strategy (TrendFollowing, Momentum, Candlestick) casts a vote:
  * BUY  → +1
  * SELL → -1
  * HOLD →  0

The final signal is determined by majority vote:
  * Sum > 0  → BUY
  * Sum < 0  → SELL
  * Sum == 0 → HOLD
"""

from __future__ import annotations

import pandas as pd

from .base_strategy import BaseStrategy, Signal
from .trend_following import TrendFollowingStrategy
from .momentum import MomentumStrategy
from .candlestick import CandlestickStrategy


_VOTE = {Signal.BUY: 1, Signal.SELL: -1, Signal.HOLD: 0}


class CombinedStrategy(BaseStrategy):
    """Aggregated strategy that combines TrendFollowing, Momentum, and Candlestick.

    Parameters
    ----------
    ema_period:
        EMA period forwarded to TrendFollowing and Candlestick sub-strategies.
    macd_fast, macd_slow, macd_signal:
        MACD parameters for TrendFollowing.
    rsi_period, rsi_overbought, rsi_oversold:
        RSI parameters for Momentum.
    bb_period, bb_std_dev:
        Bollinger Band parameters for Momentum.
    """

    name = "Combined (Trend + Momentum + Candlestick)"

    def __init__(
        self,
        ema_period: int = 20,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        rsi_period: int = 14,
        rsi_overbought: float = 70.0,
        rsi_oversold: float = 30.0,
        bb_period: int = 20,
        bb_std_dev: float = 2.0,
    ) -> None:
        self._trend = TrendFollowingStrategy(ema_period, macd_fast, macd_slow, macd_signal)
        self._momentum = MomentumStrategy(rsi_period, rsi_overbought, rsi_oversold, bb_period, bb_std_dev)
        self._candlestick = CandlestickStrategy(ema_period)

    def generate_signal(self, ohlcv: pd.DataFrame) -> Signal:
        """Aggregate sub-strategy votes and return the majority signal."""
        votes = (
            _VOTE[self._trend.generate_signal(ohlcv)]
            + _VOTE[self._momentum.generate_signal(ohlcv)]
            + _VOTE[self._candlestick.generate_signal(ohlcv)]
        )
        if votes > 0:
            return Signal.BUY
        if votes < 0:
            return Signal.SELL
        return Signal.HOLD
