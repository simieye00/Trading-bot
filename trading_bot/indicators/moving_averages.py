"""Simple Moving Average (SMA) and Exponential Moving Average (EMA) indicators."""

import pandas as pd


def sma(prices: pd.Series, period: int) -> pd.Series:
    """Calculate the Simple Moving Average (SMA).

    Args:
        prices: Series of closing prices.
        period: Number of periods to average over.

    Returns:
        Series with the SMA values (NaN for insufficient data).
    """
    if period < 1:
        raise ValueError("period must be >= 1")
    return prices.rolling(window=period).mean()


def ema(prices: pd.Series, period: int) -> pd.Series:
    """Calculate the Exponential Moving Average (EMA).

    Uses the standard smoothing factor: alpha = 2 / (period + 1).

    Args:
        prices: Series of closing prices.
        period: Number of periods (span) for the EMA.

    Returns:
        Series with the EMA values.
    """
    if period < 1:
        raise ValueError("period must be >= 1")
    return prices.ewm(span=period, adjust=False).mean()
