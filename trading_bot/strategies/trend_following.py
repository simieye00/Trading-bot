"""Trend-following strategy using EMA and MACD."""

import pandas as pd

from trading_bot.indicators.moving_averages import ema
from trading_bot.indicators.macd import macd
from .base_strategy import BaseStrategy, Signal


class TrendFollowingStrategy(BaseStrategy):
    """Trend-following strategy based on EMA direction and MACD crossover.

    Entry logic (1-min / 5-min candles):

    * **BUY**  – Price is above the 20-period EMA **and** the MACD line
      crosses above the signal line on the most recent candle.
    * **SELL** – Price is below the 20-period EMA **and** the MACD line
      crosses below the signal line on the most recent candle.
    * **HOLD** – Neither condition is met.
    """

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

    @property
    def name(self) -> str:
        return "Trend Following (EMA + MACD)"

    @property
    def description(self) -> str:
        return (
            f"Generates BUY/SELL signals when price is on the correct side of "
            f"the {self.ema_period}-period EMA and the MACD line crosses the "
            f"signal line."
        )

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """Return a trading signal based on EMA direction and MACD crossover.

        Args:
            df: OHLC DataFrame with at least ``close`` column.

        Returns:
            ``"BUY"``, ``"SELL"``, or ``"HOLD"``.
        """
        close = df["close"]
        ema_values = ema(close, self.ema_period)
        macd_df = macd(close, self.macd_fast, self.macd_slow, self.macd_signal)

        current_close = close.iloc[-1]
        current_ema = ema_values.iloc[-1]
        current_macd = macd_df["macd"].iloc[-1]
        current_signal = macd_df["signal"].iloc[-1]
        prev_macd = macd_df["macd"].iloc[-2]
        prev_signal = macd_df["signal"].iloc[-2]

        above_ema = current_close > current_ema
        macd_crossed_up = prev_macd <= prev_signal and current_macd > current_signal
        macd_crossed_down = prev_macd >= prev_signal and current_macd < current_signal

        if above_ema and macd_crossed_up:
            return "BUY"
        if not above_ema and macd_crossed_down:
            return "SELL"
        return "HOLD"
