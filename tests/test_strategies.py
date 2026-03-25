"""Tests for trading strategies."""

import pytest
import numpy as np
import pandas as pd

from trading_bot.strategies import STRATEGY_PRESETS
from trading_bot.strategies.trend_following import TrendFollowingStrategy
from trading_bot.strategies.momentum import MomentumStrategy
from trading_bot.strategies.combined import CombinedStrategy


VALID_SIGNALS = {"BUY", "SELL", "HOLD"}


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Neutral OHLC DataFrame (100 candles, flat price)."""
    rng = np.random.default_rng(42)
    n = 100
    close = pd.Series(100.0 + rng.normal(0, 0.5, n).cumsum())
    high = close + rng.uniform(0.05, 0.3, n)
    low = close - rng.uniform(0.05, 0.3, n)
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close})


@pytest.fixture
def rising_df() -> pd.DataFrame:
    """Strong uptrend OHLC DataFrame."""
    n = 100
    close = pd.Series(np.linspace(90, 120, n))
    high = close + 0.2
    low = close - 0.2
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close})


@pytest.fixture
def falling_df() -> pd.DataFrame:
    """Strong downtrend OHLC DataFrame."""
    n = 100
    close = pd.Series(np.linspace(120, 90, n))
    high = close + 0.2
    low = close - 0.2
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close})


# ---------------------------------------------------------------------------
# Strategy preset registry
# ---------------------------------------------------------------------------

class TestStrategyPresets:
    def test_all_presets_present(self):
        assert set(STRATEGY_PRESETS.keys()) == {"trend", "momentum", "combined"}

    def test_preset_values_are_classes(self):
        for cls in STRATEGY_PRESETS.values():
            assert isinstance(cls, type)


# ---------------------------------------------------------------------------
# TrendFollowingStrategy
# ---------------------------------------------------------------------------

class TestTrendFollowingStrategy:
    def test_returns_valid_signal(self, sample_df):
        strategy = TrendFollowingStrategy()
        assert strategy.generate_signal(sample_df) in VALID_SIGNALS

    def test_has_name_and_description(self):
        s = TrendFollowingStrategy()
        assert isinstance(s.name, str) and s.name
        assert isinstance(s.description, str) and s.description

    def test_rising_trend_no_sell(self, rising_df):
        strategy = TrendFollowingStrategy()
        signal = strategy.generate_signal(rising_df)
        # In a clean uptrend the strategy should not issue SELL
        assert signal != "SELL"

    def test_falling_trend_no_buy(self, falling_df):
        strategy = TrendFollowingStrategy()
        signal = strategy.generate_signal(falling_df)
        assert signal != "BUY"


# ---------------------------------------------------------------------------
# MomentumStrategy
# ---------------------------------------------------------------------------

class TestMomentumStrategy:
    def test_returns_valid_signal(self, sample_df):
        strategy = MomentumStrategy()
        assert strategy.generate_signal(sample_df) in VALID_SIGNALS

    def test_has_name_and_description(self):
        s = MomentumStrategy()
        assert isinstance(s.name, str) and s.name
        assert isinstance(s.description, str) and s.description

    def test_buy_on_oversold_conditions(self):
        """Force RSI < 30 and price below lower BB by constructing a falling series."""
        n = 60
        # Sharply falling prices → RSI will be very low
        close = pd.Series(np.linspace(100, 50, n))
        high = close + 0.1
        low = close - 0.1
        open_ = close.shift(1).fillna(close.iloc[0])
        df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close})
        strategy = MomentumStrategy()
        signal = strategy.generate_signal(df)
        # Either BUY (if both conditions met) or at worst HOLD, never SELL in a crash
        assert signal != "SELL"

    def test_sell_on_overbought_conditions(self):
        """Force RSI > 70 and price above upper BB by constructing a rising series."""
        n = 60
        close = pd.Series(np.linspace(50, 100, n))
        high = close + 0.1
        low = close - 0.1
        open_ = close.shift(1).fillna(close.iloc[0])
        df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close})
        strategy = MomentumStrategy()
        signal = strategy.generate_signal(df)
        assert signal != "BUY"


# ---------------------------------------------------------------------------
# CombinedStrategy
# ---------------------------------------------------------------------------

class TestCombinedStrategy:
    def test_returns_valid_signal(self, sample_df):
        strategy = CombinedStrategy()
        assert strategy.generate_signal(sample_df) in VALID_SIGNALS

    def test_has_name_and_description(self):
        s = CombinedStrategy()
        assert isinstance(s.name, str) and s.name
        assert isinstance(s.description, str) and s.description

    def test_custom_min_confirmations(self, sample_df):
        strategy = CombinedStrategy(min_confirmations=1)
        assert strategy.generate_signal(sample_df) in VALID_SIGNALS

    def test_rising_trend_no_sell(self, rising_df):
        strategy = CombinedStrategy(min_confirmations=2)
        signal = strategy.generate_signal(rising_df)
        assert signal != "SELL"

    def test_falling_trend_no_buy(self, falling_df):
        strategy = CombinedStrategy(min_confirmations=2)
        signal = strategy.generate_signal(falling_df)
        assert signal != "BUY"
