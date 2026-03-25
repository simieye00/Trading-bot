"""Candlestick pattern recognition."""

import pandas as pd


def _body_size(open_: float, close: float) -> float:
    return abs(close - open_)


def _upper_shadow(open_: float, high: float, close: float) -> float:
    return high - max(open_, close)


def _lower_shadow(open_: float, low: float, close: float) -> float:
    return min(open_, close) - low


def _total_range(high: float, low: float) -> float:
    return high - low


def is_hammer(
    open_: float,
    high: float,
    low: float,
    close: float,
    body_ratio: float = 0.3,
    shadow_ratio: float = 2.0,
) -> bool:
    """Detect a Hammer candlestick pattern (bullish reversal).

    Characteristics:
    - Small real body in the upper portion of the candle.
    - Lower shadow at least ``shadow_ratio`` times the body size.
    - Upper shadow is shorter than the body.

    Args:
        open_: Opening price.
        high: High price.
        low: Low price.
        close: Closing price.
        body_ratio: Max fraction of total range that the body may occupy.
        shadow_ratio: Min ratio of lower shadow to body size.

    Returns:
        True if the candle matches a Hammer pattern.
    """
    total = _total_range(high, low)
    if total == 0:
        return False
    body = _body_size(open_, close)
    lower = _lower_shadow(open_, low, close)
    upper = _upper_shadow(open_, high, close)
    return (
        body <= body_ratio * total
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
    """Detect an Inverted Hammer candlestick pattern (bullish reversal).

    Characteristics:
    - Small real body in the lower portion of the candle.
    - Upper shadow at least ``shadow_ratio`` times the body size.
    - Lower shadow is shorter than the body.

    Args:
        open_: Opening price.
        high: High price.
        low: Low price.
        close: Closing price.
        body_ratio: Max fraction of total range that the body may occupy.
        shadow_ratio: Min ratio of upper shadow to body size.

    Returns:
        True if the candle matches an Inverted Hammer pattern.
    """
    total = _total_range(high, low)
    if total == 0:
        return False
    body = _body_size(open_, close)
    lower = _lower_shadow(open_, low, close)
    upper = _upper_shadow(open_, high, close)
    return (
        body <= body_ratio * total
        and upper >= shadow_ratio * body
        and lower <= body
    )


def is_bullish_engulfing(
    prev_open: float,
    prev_close: float,
    curr_open: float,
    curr_close: float,
) -> bool:
    """Detect a Bullish Engulfing pattern (strong bullish reversal).

    The previous candle is bearish and the current candle is bullish,
    with its body fully engulfing the previous body.

    Args:
        prev_open: Previous candle opening price.
        prev_close: Previous candle closing price.
        curr_open: Current candle opening price.
        curr_close: Current candle closing price.

    Returns:
        True if the pattern is a Bullish Engulfing.
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
    """Detect a Bearish Engulfing pattern (strong bearish reversal).

    The previous candle is bullish and the current candle is bearish,
    with its body fully engulfing the previous body.

    Args:
        prev_open: Previous candle opening price.
        prev_close: Previous candle closing price.
        curr_open: Current candle opening price.
        curr_close: Current candle closing price.

    Returns:
        True if the pattern is a Bearish Engulfing.
    """
    prev_bullish = prev_close > prev_open
    curr_bearish = curr_close < curr_open
    engulfs = curr_open >= prev_close and curr_close <= prev_open
    return prev_bullish and curr_bearish and engulfs


def detect_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """Detect candlestick patterns across an OHLC DataFrame.

    Args:
        df: DataFrame with columns ``open``, ``high``, ``low``, ``close``.

    Returns:
        DataFrame with boolean columns for each detected pattern:
        ``hammer``, ``inverted_hammer``, ``bullish_engulfing``,
        ``bearish_engulfing``.
    """
    required = {"open", "high", "low", "close"}
    if not required.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required}")

    result = pd.DataFrame(index=df.index)

    result["hammer"] = [
        is_hammer(row.open, row.high, row.low, row.close)
        for row in df.itertuples()
    ]
    result["inverted_hammer"] = [
        is_inverted_hammer(row.open, row.high, row.low, row.close)
        for row in df.itertuples()
    ]

    bullish_eng = [False]
    bearish_eng = [False]
    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        bullish_eng.append(
            is_bullish_engulfing(prev.open, prev.close, curr.open, curr.close)
        )
        bearish_eng.append(
            is_bearish_engulfing(prev.open, prev.close, curr.open, curr.close)
        )

    result["bullish_engulfing"] = bullish_eng
    result["bearish_engulfing"] = bearish_eng

    return result
