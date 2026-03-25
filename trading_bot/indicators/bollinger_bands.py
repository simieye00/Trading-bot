"""Bollinger Bands indicator."""

import pandas as pd
from .moving_averages import sma


def bollinger_bands(
    prices: pd.Series, period: int = 20, num_std: float = 2.0
) -> pd.DataFrame:
    """Calculate Bollinger Bands.

    The bands create a price channel:
    - Upper Band = SMA + (num_std * rolling standard deviation)
    - Middle Band = SMA
    - Lower Band = SMA - (num_std * rolling standard deviation)

    When price touches or crosses the upper band the asset may be overbought;
    the lower band indicates an oversold condition.

    Args:
        prices: Series of closing prices.
        period: Look-back period for the SMA and std dev (default 20).
        num_std: Number of standard deviations for the bands (default 2.0).

    Returns:
        DataFrame with columns: ``upper``, ``middle``, ``lower``.
    """
    if period < 1:
        raise ValueError("period must be >= 1")

    middle = sma(prices, period)
    std = prices.rolling(window=period).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return pd.DataFrame({"upper": upper, "middle": middle, "lower": lower})
