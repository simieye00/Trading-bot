"""Tests for technical indicators."""

import pytest
import pandas as pd
import numpy as np

from trading_bot.indicators.moving_averages import sma, ema
from trading_bot.indicators.macd import macd
from trading_bot.indicators.rsi import rsi
from trading_bot.indicators.bollinger_bands import bollinger_bands
from trading_bot.indicators.candlestick_patterns import (
    is_hammer,
    is_inverted_hammer,
    is_bullish_engulfing,
    is_bearish_engulfing,
    detect_patterns,
)


@pytest.fixture
def prices() -> pd.Series:
    """50-point synthetic price series."""
    rng = np.random.default_rng(0)
    return pd.Series(100 + rng.normal(0, 1, 50).cumsum())


@pytest.fixture
def ohlc_df(prices) -> pd.DataFrame:
    """Minimal OHLC DataFrame derived from the price series."""
    rng = np.random.default_rng(1)
    close = prices
    high = close + rng.uniform(0.1, 0.5, len(close))
    low = close - rng.uniform(0.1, 0.5, len(close))
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close})


# ---------------------------------------------------------------------------
# SMA
# ---------------------------------------------------------------------------

class TestSMA:
    def test_period_1_equals_prices(self, prices):
        result = sma(prices, 1)
        pd.testing.assert_series_equal(result, prices, check_names=False)

    def test_first_values_nan(self, prices):
        period = 5
        result = sma(prices, period)
        assert result.iloc[:period - 1].isna().all()

    def test_known_values(self):
        s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = sma(s, 3)
        assert result.iloc[2] == pytest.approx(2.0)
        assert result.iloc[4] == pytest.approx(4.0)

    def test_invalid_period(self, prices):
        with pytest.raises(ValueError):
            sma(prices, 0)


# ---------------------------------------------------------------------------
# EMA
# ---------------------------------------------------------------------------

class TestEMA:
    def test_length_matches_input(self, prices):
        result = ema(prices, 10)
        assert len(result) == len(prices)

    def test_no_nan_values(self, prices):
        result = ema(prices, 10)
        assert not result.isna().any()

    def test_single_value_series(self):
        s = pd.Series([42.0])
        result = ema(s, 1)
        assert result.iloc[0] == pytest.approx(42.0)

    def test_invalid_period(self, prices):
        with pytest.raises(ValueError):
            ema(prices, 0)


# ---------------------------------------------------------------------------
# MACD
# ---------------------------------------------------------------------------

class TestMACD:
    def test_returns_dataframe(self, prices):
        result = macd(prices)
        assert isinstance(result, pd.DataFrame)
        assert {"macd", "signal", "histogram"} == set(result.columns)

    def test_histogram_is_macd_minus_signal(self, prices):
        result = macd(prices)
        diff = (result["macd"] - result["signal"] - result["histogram"]).abs()
        assert (diff < 1e-10).all()

    def test_length_matches_input(self, prices):
        result = macd(prices)
        assert len(result) == len(prices)


# ---------------------------------------------------------------------------
# RSI
# ---------------------------------------------------------------------------

class TestRSI:
    def test_values_in_range(self, prices):
        result = rsi(prices, 14)
        valid = result.dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_all_rising_prices_high_rsi(self):
        s = pd.Series(range(1, 51), dtype=float)
        result = rsi(s, 14)
        assert result.iloc[-1] > 70

    def test_all_falling_prices_low_rsi(self):
        s = pd.Series(range(50, 0, -1), dtype=float)
        result = rsi(s, 14)
        assert result.iloc[-1] < 30

    def test_invalid_period(self, prices):
        with pytest.raises(ValueError):
            rsi(prices, 0)


# ---------------------------------------------------------------------------
# Bollinger Bands
# ---------------------------------------------------------------------------

class TestBollingerBands:
    def test_returns_dataframe(self, prices):
        result = bollinger_bands(prices)
        assert {"upper", "middle", "lower"} == set(result.columns)

    def test_upper_above_lower(self, prices):
        result = bollinger_bands(prices)
        valid = result.dropna()
        assert (valid["upper"] >= valid["lower"]).all()

    def test_middle_between_bands(self, prices):
        result = bollinger_bands(prices)
        valid = result.dropna()
        assert (valid["middle"] <= valid["upper"]).all()
        assert (valid["middle"] >= valid["lower"]).all()

    def test_invalid_period(self, prices):
        with pytest.raises(ValueError):
            bollinger_bands(prices, 0)


# ---------------------------------------------------------------------------
# Candlestick patterns
# ---------------------------------------------------------------------------

class TestHammer:
    def test_detects_hammer(self):
        # Tiny body at the top, long lower shadow
        assert is_hammer(open_=10.0, high=10.1, low=7.0, close=9.9)

    def test_no_hammer_tall_body(self):
        assert not is_hammer(open_=7.0, high=10.0, low=6.0, close=10.0)

    def test_zero_range_returns_false(self):
        assert not is_hammer(open_=10.0, high=10.0, low=10.0, close=10.0)


class TestInvertedHammer:
    def test_detects_inverted_hammer(self):
        # Tiny body at the bottom, long upper shadow
        assert is_inverted_hammer(open_=9.9, high=13.0, low=9.8, close=10.0)

    def test_no_inverted_hammer_tall_body(self):
        assert not is_inverted_hammer(open_=7.0, high=12.0, low=6.0, close=12.0)

    def test_zero_range_returns_false(self):
        assert not is_inverted_hammer(open_=10.0, high=10.0, low=10.0, close=10.0)


class TestBullishEngulfing:
    def test_detects_bullish_engulfing(self):
        # Previous bearish, current bullish and engulfs
        assert is_bullish_engulfing(
            prev_open=10.0, prev_close=8.0,
            curr_open=7.5, curr_close=10.5,
        )

    def test_no_bullish_engulfing_if_not_engulfing(self):
        # Current candle does not engulf fully
        assert not is_bullish_engulfing(
            prev_open=10.0, prev_close=8.0,
            curr_open=8.5, curr_close=9.5,
        )

    def test_no_bullish_engulfing_if_prev_bullish(self):
        assert not is_bullish_engulfing(
            prev_open=8.0, prev_close=10.0,
            curr_open=7.5, curr_close=10.5,
        )


class TestBearishEngulfing:
    def test_detects_bearish_engulfing(self):
        # Previous bullish, current bearish and engulfs
        assert is_bearish_engulfing(
            prev_open=8.0, prev_close=10.0,
            curr_open=10.5, curr_close=7.5,
        )

    def test_no_bearish_engulfing_if_not_engulfing(self):
        assert not is_bearish_engulfing(
            prev_open=8.0, prev_close=10.0,
            curr_open=9.5, curr_close=8.5,
        )

    def test_no_bearish_engulfing_if_prev_bearish(self):
        assert not is_bearish_engulfing(
            prev_open=10.0, prev_close=8.0,
            curr_open=10.5, curr_close=7.5,
        )


class TestDetectPatterns:
    def test_returns_correct_columns(self, ohlc_df):
        result = detect_patterns(ohlc_df)
        expected_cols = {"hammer", "inverted_hammer", "bullish_engulfing", "bearish_engulfing"}
        assert expected_cols == set(result.columns)

    def test_same_length_as_input(self, ohlc_df):
        result = detect_patterns(ohlc_df)
        assert len(result) == len(ohlc_df)

    def test_first_row_engulfing_always_false(self, ohlc_df):
        result = detect_patterns(ohlc_df)
        assert not result["bullish_engulfing"].iloc[0]
        assert not result["bearish_engulfing"].iloc[0]

    def test_missing_column_raises(self):
        df = pd.DataFrame({"open": [1], "high": [2], "close": [1.5]})
        with pytest.raises(ValueError):
            detect_patterns(df)
