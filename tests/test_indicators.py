"""Tests for technical indicator calculations."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from bot.indicators import (
    sma,
    ema,
    macd,
    rsi,
    bollinger_bands,
    is_hammer,
    is_inverted_hammer,
    is_bullish_engulfing,
    is_bearish_engulfing,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def flat_prices() -> pd.Series:
    """A constant price series where most indicators should return stable values."""
    return pd.Series([100.0] * 30)


@pytest.fixture()
def rising_prices() -> pd.Series:
    """A steadily rising price series."""
    return pd.Series([float(i) for i in range(1, 51)])


@pytest.fixture()
def falling_prices() -> pd.Series:
    """A steadily falling price series."""
    return pd.Series([float(i) for i in range(50, 0, -1)])


# ---------------------------------------------------------------------------
# SMA
# ---------------------------------------------------------------------------

class TestSMA:
    def test_basic_average(self):
        prices = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = sma(prices, 3)
        assert math.isnan(result.iloc[0])
        assert math.isnan(result.iloc[1])
        assert result.iloc[2] == pytest.approx(2.0)
        assert result.iloc[3] == pytest.approx(3.0)
        assert result.iloc[4] == pytest.approx(4.0)

    def test_flat_prices(self, flat_prices):
        result = sma(flat_prices, 5)
        assert result.dropna().iloc[-1] == pytest.approx(100.0)

    def test_period_one(self):
        prices = pd.Series([10.0, 20.0, 30.0])
        result = sma(prices, 1)
        assert list(result) == pytest.approx([10.0, 20.0, 30.0])

    def test_invalid_period(self):
        prices = pd.Series([1.0, 2.0, 3.0])
        with pytest.raises(ValueError):
            sma(prices, 0)


# ---------------------------------------------------------------------------
# EMA
# ---------------------------------------------------------------------------

class TestEMA:
    def test_result_length(self, rising_prices):
        result = ema(rising_prices, 10)
        assert len(result) == len(rising_prices)

    def test_ema_lags_behind_rising(self, rising_prices):
        """EMA should be below close for a steadily rising series."""
        result = ema(rising_prices, 10)
        # Drop NaN and compare last value
        last_ema = result.dropna().iloc[-1]
        last_close = rising_prices.iloc[-1]
        assert last_ema < last_close

    def test_flat_prices(self, flat_prices):
        result = ema(flat_prices, 10)
        assert result.dropna().iloc[-1] == pytest.approx(100.0, rel=1e-3)

    def test_invalid_period(self):
        prices = pd.Series([1.0, 2.0, 3.0])
        with pytest.raises(ValueError):
            ema(prices, 0)


# ---------------------------------------------------------------------------
# MACD
# ---------------------------------------------------------------------------

class TestMACD:
    def test_output_fields(self, rising_prices):
        result = macd(rising_prices)
        assert hasattr(result, "macd_line")
        assert hasattr(result, "signal_line")
        assert hasattr(result, "histogram")

    def test_histogram_equals_macd_minus_signal(self, rising_prices):
        result = macd(rising_prices)
        diff = (result.macd_line - result.signal_line).dropna()
        hist = result.histogram.dropna()
        pd.testing.assert_series_equal(diff, hist, check_names=False, rtol=1e-6)

    def test_invalid_fast_slow(self):
        prices = pd.Series(range(1, 51), dtype=float)
        with pytest.raises(ValueError):
            macd(prices, fast=26, slow=12)

    def test_macd_positive_for_rising_prices(self, rising_prices):
        result = macd(rising_prices)
        valid = result.macd_line.dropna()
        # On a pure uptrend fast EMA > slow EMA → MACD positive
        assert valid.iloc[-1] > 0


# ---------------------------------------------------------------------------
# RSI
# ---------------------------------------------------------------------------

class TestRSI:
    def test_rsi_range(self, rising_prices):
        result = rsi(rising_prices)
        valid = result.dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_rsi_high_for_rising_prices(self, rising_prices):
        result = rsi(rising_prices)
        # Pure uptrend: all changes are gains → RSI should approach or equal 100
        valid = result.dropna()
        assert not valid.empty
        assert valid.iloc[-1] >= 70

    def test_rsi_low_for_falling_prices(self, falling_prices):
        result = rsi(falling_prices)
        assert result.dropna().iloc[-1] < 30

    def test_flat_prices(self, flat_prices):
        """RSI for a flat series – all gains and losses are zero, so RSI = 100."""
        result = rsi(flat_prices)
        valid = result.dropna()
        assert not valid.empty
        assert valid.iloc[-1] == pytest.approx(100.0)

    def test_invalid_period(self):
        prices = pd.Series([1.0, 2.0, 3.0])
        with pytest.raises(ValueError):
            rsi(prices, 0)


# ---------------------------------------------------------------------------
# Bollinger Bands
# ---------------------------------------------------------------------------

class TestBollingerBands:
    def test_output_fields(self, rising_prices):
        result = bollinger_bands(rising_prices)
        assert hasattr(result, "upper")
        assert hasattr(result, "middle")
        assert hasattr(result, "lower")

    def test_upper_gt_middle_gt_lower(self, rising_prices):
        result = bollinger_bands(rising_prices)
        valid_idx = result.middle.dropna().index
        assert (result.upper[valid_idx] > result.middle[valid_idx]).all()
        assert (result.middle[valid_idx] > result.lower[valid_idx]).all()

    def test_flat_prices_narrow_bands(self, flat_prices):
        result = bollinger_bands(flat_prices)
        upper = result.upper.dropna().iloc[-1]
        lower = result.lower.dropna().iloc[-1]
        # Standard deviation of constant series is 0 → bands collapse to middle
        assert upper == pytest.approx(100.0)
        assert lower == pytest.approx(100.0)

    def test_invalid_period(self):
        prices = pd.Series([1.0, 2.0, 3.0])
        with pytest.raises(ValueError):
            bollinger_bands(prices, period=0)

    def test_invalid_std_dev(self):
        prices = pd.Series([1.0, 2.0, 3.0])
        with pytest.raises(ValueError):
            bollinger_bands(prices, std_dev=0)


# ---------------------------------------------------------------------------
# Candlestick Patterns
# ---------------------------------------------------------------------------

class TestCandlestickPatterns:

    # -- Hammer --

    def test_hammer_detected(self):
        # Long lower shadow, tiny body at top, tiny upper shadow
        assert is_hammer(open_=99, high=100, low=90, close=100)

    def test_hammer_not_detected_large_body(self):
        # Body too large relative to range
        assert not is_hammer(open_=90, high=100, low=89, close=100)

    def test_hammer_zero_range(self):
        assert not is_hammer(open_=100, high=100, low=100, close=100)

    # -- Inverted Hammer --

    def test_inverted_hammer_detected(self):
        # Long upper shadow (9), tiny body (1), tiny lower shadow (0)
        # open=100, close=101 → body=1, upper=110-101=9, lower=100-100=0
        assert is_inverted_hammer(open_=100, high=110, low=100, close=101)

    def test_inverted_hammer_not_detected_large_body(self):
        assert not is_inverted_hammer(open_=90, high=110, low=89, close=110)

    # -- Bullish Engulfing --

    def test_bullish_engulfing_detected(self):
        # Previous: bearish (open 105, close 100)
        # Current:  bullish (open 99, close 106) – fully engulfs previous body
        assert is_bullish_engulfing(
            prev_open=105, prev_close=100,
            curr_open=99, curr_close=106,
        )

    def test_bullish_engulfing_not_detected_when_current_bearish(self):
        assert not is_bullish_engulfing(
            prev_open=105, prev_close=100,
            curr_open=106, curr_close=95,  # current is bearish
        )

    def test_bullish_engulfing_not_detected_when_partial(self):
        # Current body does not fully engulf previous
        assert not is_bullish_engulfing(
            prev_open=105, prev_close=100,
            curr_open=102, curr_close=104,  # only partial coverage
        )

    # -- Bearish Engulfing --

    def test_bearish_engulfing_detected(self):
        # Previous: bullish (open 100, close 105)
        # Current:  bearish (open 106, close 99) – fully engulfs previous body
        assert is_bearish_engulfing(
            prev_open=100, prev_close=105,
            curr_open=106, curr_close=99,
        )

    def test_bearish_engulfing_not_detected_when_current_bullish(self):
        assert not is_bearish_engulfing(
            prev_open=100, prev_close=105,
            curr_open=99, curr_close=106,  # current is bullish
        )

    def test_bearish_engulfing_not_detected_when_partial(self):
        assert not is_bearish_engulfing(
            prev_open=100, prev_close=105,
            curr_open=104, curr_close=102,  # only partial coverage
        )
