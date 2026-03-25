"""Combined strategy using all indicators and candlestick patterns."""

import pandas as pd

from trading_bot.indicators.moving_averages import ema
from trading_bot.indicators.macd import macd
from trading_bot.indicators.rsi import rsi
from trading_bot.indicators.bollinger_bands import bollinger_bands
from trading_bot.indicators.candlestick_patterns import detect_patterns
from .base_strategy import BaseStrategy, Signal


class CombinedStrategy(BaseStrategy):
    """All-in-one strategy combining trend, momentum, and candlestick signals.

    A BUY signal requires **at least two** of the following bullish
    confirmations on the most recent candle:

    1. Price is above the 20-period EMA (trend filter).
    2. MACD line is above the signal line (trend momentum).
    3. RSI < ``oversold`` (momentum is oversold).
    4. Price <= lower Bollinger Band (price at support).
    5. Bullish candlestick pattern detected (Hammer, Inverted Hammer, or
       Bullish Engulfing).

    A SELL signal requires **at least two** of the following bearish
    confirmations:

    1. Price is below the 20-period EMA.
    2. MACD line is below the signal line.
    3. RSI > ``overbought``.
    4. Price >= upper Bollinger Band.
    5. Bearish Engulfing pattern detected.

    Otherwise the signal is ``"HOLD"``.
    """

    def __init__(
        self,
        ema_period: int = 20,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        rsi_period: int = 14,
        oversold: float = 30.0,
        overbought: float = 70.0,
        bb_period: int = 20,
        bb_std: float = 2.0,
        min_confirmations: int = 2,
    ) -> None:
        self.ema_period = ema_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.min_confirmations = min_confirmations

    @property
    def name(self) -> str:
        return "Combined (EMA + MACD + RSI + Bollinger Bands + Candlesticks)"

    @property
    def description(self) -> str:
        return (
            f"Aggregates signals from all indicators. Generates BUY/SELL when "
            f"at least {self.min_confirmations} out of 5 indicators agree."
        )

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """Return a trading signal using all indicators.

        Args:
            df: OHLC DataFrame with columns ``open``, ``high``, ``low``,
                ``close``.

        Returns:
            ``"BUY"``, ``"SELL"``, or ``"HOLD"``.
        """
        close = df["close"]

        ema_values = ema(close, self.ema_period)
        macd_df = macd(close, self.macd_fast, self.macd_slow, self.macd_signal)
        rsi_values = rsi(close, self.rsi_period)
        bb = bollinger_bands(close, self.bb_period, self.bb_std)
        patterns = detect_patterns(df)

        current_close = close.iloc[-1]
        current_ema = ema_values.iloc[-1]
        current_macd = macd_df["macd"].iloc[-1]
        current_signal_line = macd_df["signal"].iloc[-1]
        current_rsi = rsi_values.iloc[-1]
        current_upper = bb["upper"].iloc[-1]
        current_lower = bb["lower"].iloc[-1]

        last_pattern = patterns.iloc[-1]
        bullish_candle = last_pattern["hammer"] or last_pattern["inverted_hammer"] or last_pattern["bullish_engulfing"]
        bearish_candle = last_pattern["bearish_engulfing"]

        bullish_score = sum([
            current_close > current_ema,
            current_macd > current_signal_line,
            current_rsi < self.oversold,
            current_close <= current_lower,
            bullish_candle,
        ])

        bearish_score = sum([
            current_close < current_ema,
            current_macd < current_signal_line,
            current_rsi > self.overbought,
            current_close >= current_upper,
            bearish_candle,
        ])

        if bullish_score >= self.min_confirmations and bullish_score > bearish_score:
            return "BUY"
        if bearish_score >= self.min_confirmations and bearish_score > bullish_score:
            return "SELL"
        return "HOLD"
