"""RSI – Relative Strength Index indicator."""

from __future__ import annotations

import pandas as pd


def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Compute the Relative Strength Index (RSI) for a price series.

    Uses Wilder's smoothing (equivalent to EMA with ``alpha = 1 / period``).

    Parameters
    ----------
    prices:
        Closing prices as a pandas Series.
    period:
        Look-back period (default 14).

    Returns
    -------
    pd.Series
        RSI values in the range [0, 100].  The first ``period`` values are
        ``NaN``.
    """
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")

    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    # Wilder smoothing: equivalent to EMA with alpha = 1/period
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()

    # When avg_loss is 0 the RS is infinite → RSI = 100
    # Avoid division by zero by clamping: use NaN only for the warmup period
    result = avg_gain.copy() * float("nan")  # same index, start as NaN
    valid = avg_loss.notna() & avg_gain.notna()
    zero_loss = valid & (avg_loss == 0)
    normal = valid & (avg_loss > 0)
    result[zero_loss] = 100.0
    rs = avg_gain[normal] / avg_loss[normal]
    result[normal] = 100 - (100 / (1 + rs))
    return result
