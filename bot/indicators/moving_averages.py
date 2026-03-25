"""Simple Moving Average (SMA) and Exponential Moving Average (EMA)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(prices: pd.Series, period: int) -> pd.Series:
    """Calculate the Simple Moving Average over *period* bars.

    Parameters
    ----------
    prices:
        A pandas Series of closing prices (or any numeric price series).
    period:
        Look-back window length in bars.

    Returns
    -------
    pd.Series
        SMA values aligned to the same index as *prices*.  The first
        ``period - 1`` values are ``NaN``.
    """
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    return prices.rolling(window=period, min_periods=period).mean()


def ema(prices: pd.Series, period: int) -> pd.Series:
    """Calculate the Exponential Moving Average over *period* bars.

    Parameters
    ----------
    prices:
        A pandas Series of closing prices.
    period:
        Span (number of bars) for the EMA.  The smoothing factor is
        ``2 / (period + 1)``.

    Returns
    -------
    pd.Series
        EMA values aligned to the same index as *prices*.  The first
        ``period - 1`` values are ``NaN`` (``adjust=False`` mode).
    """
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    return prices.ewm(span=period, adjust=False, min_periods=period).mean()
