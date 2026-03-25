"""Momentum strategy using RSI and Bollinger Bands."""

import pandas as pd

from trading_bot.indicators.rsi import rsi
from trading_bot.indicators.bollinger_bands import bollinger_bands
from .base_strategy import BaseStrategy, Signal


class MomentumStrategy(BaseStrategy):
    """Momentum / mean-reversion strategy using RSI and Bollinger Bands.

    Entry logic (1-min / 5-min candles):

    * **BUY**  – RSI < ``oversold`` threshold **and** the closing price
      touches or falls below the lower Bollinger Band.
    * **SELL** – RSI > ``overbought`` threshold **and** the closing price
      touches or rises above the upper Bollinger Band.
    * **HOLD** – Neither condition is met.

    The dual-confirmation requirement reduces false signals in ranging markets.
    """

    def __init__(
        self,
        rsi_period: int = 14,
        oversold: float = 30.0,
        overbought: float = 70.0,
        bb_period: int = 20,
        bb_std: float = 2.0,
    ) -> None:
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        self.bb_period = bb_period
        self.bb_std = bb_std

    @property
    def name(self) -> str:
        return "Momentum (RSI + Bollinger Bands)"

    @property
    def description(self) -> str:
        return (
            f"Generates BUY when RSI < {self.oversold} and price <= lower "
            f"Bollinger Band; SELL when RSI > {self.overbought} and price >= "
            f"upper Bollinger Band."
        )

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """Return a trading signal based on RSI and Bollinger Bands.

        Args:
            df: OHLC DataFrame with at least ``close`` column.

        Returns:
            ``"BUY"``, ``"SELL"``, or ``"HOLD"``.
        """
        close = df["close"]
        rsi_values = rsi(close, self.rsi_period)
        bb = bollinger_bands(close, self.bb_period, self.bb_std)

        current_close = close.iloc[-1]
        current_rsi = rsi_values.iloc[-1]
        current_upper = bb["upper"].iloc[-1]
        current_lower = bb["lower"].iloc[-1]

        if current_rsi < self.oversold and current_close <= current_lower:
            return "BUY"
        if current_rsi > self.overbought and current_close >= current_upper:
            return "SELL"
        return "HOLD"
