"""Moving Average Convergence Divergence (MACD) indicator."""

import pandas as pd
from .moving_averages import ema


def macd(
    prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    """Calculate the MACD indicator.

    MACD Line  = EMA(fast_period) - EMA(slow_period)
    Signal Line = EMA(signal_period) of MACD Line
    Histogram   = MACD Line - Signal Line

    Args:
        prices: Series of closing prices.
        fast_period: Period for the fast EMA (default 12).
        slow_period: Period for the slow EMA (default 26).
        signal_period: Period for the signal line EMA (default 9).

    Returns:
        DataFrame with columns: ``macd``, ``signal``, ``histogram``.
    """
    fast_ema = ema(prices, fast_period)
    slow_ema = ema(prices, slow_period)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal_period)
    histogram = macd_line - signal_line
    return pd.DataFrame(
        {"macd": macd_line, "signal": signal_line, "histogram": histogram}
    )
