"""Candlestick pattern recognition.

Supported patterns
------------------
* Hammer
* Inverted Hammer
* Bullish Engulfing
* Bearish Engulfing
"""

from __future__ import annotations

import pandas as pd


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _body(open_: float, close: float) -> float:
    """Return the absolute size of a candle's real body."""
    return abs(close - open_)


def _upper_shadow(open_: float, high: float, close: float) -> float:
    """Return the length of the upper wick/shadow."""
    return high - max(open_, close)


def _lower_shadow(open_: float, low: float, close: float) -> float:
    """Return the length of the lower wick/shadow."""
    return min(open_, close) - low


def _candle_range(high: float, low: float) -> float:
    """Return the full high-to-low range of a candle."""
    return high - low


# ---------------------------------------------------------------------------
# Single-candle patterns
# ---------------------------------------------------------------------------

def is_hammer(
    open_: float,
    high: float,
    low: float,
    close: float,
    body_ratio: float = 0.3,
    shadow_ratio: float = 2.0,
) -> bool:
    """Return ``True`` if the candle forms a **Hammer** pattern.

    A Hammer has:
    * A small real body in the upper portion of the range.
    * A long lower shadow at least *shadow_ratio* times the body.
    * A tiny (or absent) upper shadow.

    Parameters
    ----------
    open_, high, low, close:
        OHLC values for a single candle.
    body_ratio:
        Maximum ratio of body to full range (default 0.3 → body ≤ 30 % of range).
    shadow_ratio:
        Minimum ratio of lower shadow to body length (default 2.0).
    """
    full_range = _candle_range(high, low)
    if full_range == 0:
        return False

    body = _body(open_, close)
    lower = _lower_shadow(open_, low, close)
    upper = _upper_shadow(open_, high, close)

    if body == 0:
        return False

    return (
        body / full_range <= body_ratio
        and lower >= shadow_ratio * body
        and upper <= body
    )


def is_inverted_hammer(
    open_: float,
    high: float,
    low: float,
    close: float,
    body_ratio: float = 0.3,
    shadow_ratio: float = 2.0,
) -> bool:
    """Return ``True`` if the candle forms an **Inverted Hammer** pattern.

    An Inverted Hammer has:
    * A small real body in the lower portion of the range.
    * A long upper shadow at least *shadow_ratio* times the body.
    * A tiny (or absent) lower shadow.

    Parameters
    ----------
    open_, high, low, close:
        OHLC values for a single candle.
    body_ratio:
        Maximum ratio of body to full range (default 0.3).
    shadow_ratio:
        Minimum ratio of upper shadow to body length (default 2.0).
    """
    full_range = _candle_range(high, low)
    if full_range == 0:
        return False

    body = _body(open_, close)
    upper = _upper_shadow(open_, high, close)
    lower = _lower_shadow(open_, low, close)

    if body == 0:
        return False

    return (
        body / full_range <= body_ratio
        and upper >= shadow_ratio * body
        and lower <= body
    )


# ---------------------------------------------------------------------------
# Two-candle patterns
# ---------------------------------------------------------------------------

def is_bullish_engulfing(
    prev_open: float,
    prev_close: float,
    curr_open: float,
    curr_close: float,
) -> bool:
    """Return ``True`` if the two candles form a **Bullish Engulfing** pattern.

    A Bullish Engulfing requires:
    * The previous candle is bearish (close < open).
    * The current candle is bullish (close > open).
    * The current candle's body completely engulfs the previous candle's body.

    Parameters
    ----------
    prev_open, prev_close:
        OHLC open/close of the *previous* (bearish) candle.
    curr_open, curr_close:
        OHLC open/close of the *current* (bullish) candle.
    """
    prev_bearish = prev_close < prev_open
    curr_bullish = curr_close > curr_open
    engulfs = curr_open <= prev_close and curr_close >= prev_open
    return prev_bearish and curr_bullish and engulfs


def is_bearish_engulfing(
    prev_open: float,
    prev_close: float,
    curr_open: float,
    curr_close: float,
) -> bool:
    """Return ``True`` if the two candles form a **Bearish Engulfing** pattern.

    A Bearish Engulfing requires:
    * The previous candle is bullish (close > open).
    * The current candle is bearish (close < open).
    * The current candle's body completely engulfs the previous candle's body.

    Parameters
    ----------
    prev_open, prev_close:
        OHLC open/close of the *previous* (bullish) candle.
    curr_open, curr_close:
        OHLC open/close of the *current* (bearish) candle.
    """
    prev_bullish = prev_close > prev_open
    curr_bearish = curr_close < curr_open
    engulfs = curr_open >= prev_close and curr_close <= prev_open
    return prev_bullish and curr_bearish and engulfs
