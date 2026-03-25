"""Bollinger Bands indicator."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .moving_averages import sma


@dataclass
class BollingerBandsResult:
    """Container for the three Bollinger Band lines."""

    upper: pd.Series
    """Upper band: middle + (std_dev * rolling standard deviation)."""

    middle: pd.Series
    """Middle band: simple moving average over *period* bars."""

    lower: pd.Series
    """Lower band: middle - (std_dev * rolling standard deviation)."""


def bollinger_bands(
    prices: pd.Series,
    period: int = 20,
    std_dev: float = 2.0,
) -> BollingerBandsResult:
    """Compute Bollinger Bands for a price series.

    Parameters
    ----------
    prices:
        Closing prices as a pandas Series.
    period:
        Rolling window for the middle SMA (default 20).
    std_dev:
        Number of standard deviations for the upper/lower bands (default 2).

    Returns
    -------
    BollingerBandsResult
        Named fields: ``upper``, ``middle``, ``lower``.
    """
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    if std_dev <= 0:
        raise ValueError(f"std_dev must be > 0, got {std_dev}")

    middle = sma(prices, period)
    rolling_std = prices.rolling(window=period, min_periods=period).std()
    band = std_dev * rolling_std
    return BollingerBandsResult(
        upper=middle + band,
        middle=middle,
        lower=middle - band,
    )
