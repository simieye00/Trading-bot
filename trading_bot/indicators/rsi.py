"""Relative Strength Index (RSI) indicator."""

import pandas as pd


def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate the Relative Strength Index (RSI).

    RSI measures the speed and magnitude of recent price changes to evaluate
    overbought (>70) or oversold (<30) conditions.

    Args:
        prices: Series of closing prices.
        period: Look-back period (default 14).

    Returns:
        Series with RSI values in the range [0, 100].
    """
    if period < 1:
        raise ValueError("period must be >= 1")

    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    # Use Wilder's smoothing (equivalent to EMA with alpha = 1/period)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
