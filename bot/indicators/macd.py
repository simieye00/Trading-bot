"""MACD – Moving Average Convergence Divergence indicator."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .moving_averages import ema


@dataclass
class MACDResult:
    """Container for the three MACD output lines."""

    macd_line: pd.Series
    """MACD line: fast EMA minus slow EMA."""

    signal_line: pd.Series
    """Signal line: EMA of the MACD line."""

    histogram: pd.Series
    """Histogram: MACD line minus signal line."""


def macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> MACDResult:
    """Compute MACD, signal, and histogram for a price series.

    Parameters
    ----------
    prices:
        Closing prices as a pandas Series.
    fast:
        Period for the fast EMA (default 12).
    slow:
        Period for the slow EMA (default 26).
    signal:
        Period for the signal EMA applied to the MACD line (default 9).

    Returns
    -------
    MACDResult
        Named fields: ``macd_line``, ``signal_line``, ``histogram``.
    """
    if fast >= slow:
        raise ValueError(
            f"fast period ({fast}) must be less than slow period ({slow})"
        )
    fast_ema = ema(prices, fast)
    slow_ema = ema(prices, slow)
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    histogram = macd_line - signal_line
    return MACDResult(
        macd_line=macd_line,
        signal_line=signal_line,
        histogram=histogram,
    )
