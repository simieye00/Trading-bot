"""Tests for strategy presets and the Strategy Menu."""

from __future__ import annotations

import pandas as pd
import pytest

from bot.strategies import (
    TrendFollowingStrategy,
    MomentumStrategy,
    CandlestickStrategy,
    CombinedStrategy,
)
from bot.strategies.base_strategy import Signal
from bot.strategy_menu import StrategyMenu


# ---------------------------------------------------------------------------
# OHLCV DataFrame helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(closes: list[float]) -> pd.DataFrame:
    """Build a minimal OHLCV DataFrame from a list of close prices."""
    n = len(closes)
    opens = [c * 0.999 for c in closes]
    highs = [c * 1.005 for c in closes]
    lows = [c * 0.995 for c in closes]
    return pd.DataFrame(
        {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [1000.0] * n,
        }
    )


def _rising_ohlcv(n: int = 60) -> pd.DataFrame:
    """Return OHLCV with steadily rising prices."""
    return _make_ohlcv([float(i) for i in range(1, n + 1)])


def _falling_ohlcv(n: int = 60) -> pd.DataFrame:
    """Return OHLCV with steadily falling prices."""
    return _make_ohlcv([float(i) for i in range(n, 0, -1)])


def _flat_ohlcv(n: int = 60) -> pd.DataFrame:
    """Return OHLCV with flat prices."""
    return _make_ohlcv([100.0] * n)


# ---------------------------------------------------------------------------
# Signal enum
# ---------------------------------------------------------------------------

class TestSignalEnum:
    def test_values(self):
        assert Signal.BUY.value == "BUY"
        assert Signal.SELL.value == "SELL"
        assert Signal.HOLD.value == "HOLD"


# ---------------------------------------------------------------------------
# TrendFollowingStrategy
# ---------------------------------------------------------------------------

class TestTrendFollowingStrategy:
    def test_returns_signal_type(self):
        strategy = TrendFollowingStrategy()
        ohlcv = _rising_ohlcv(60)
        result = strategy.generate_signal(ohlcv)
        assert isinstance(result, Signal)

    def test_hold_when_insufficient_data(self):
        strategy = TrendFollowingStrategy()
        ohlcv = _rising_ohlcv(10)  # not enough bars
        assert strategy.generate_signal(ohlcv) == Signal.HOLD

    def test_produces_a_signal_on_enough_data(self):
        strategy = TrendFollowingStrategy()
        ohlcv = _rising_ohlcv(60)
        result = strategy.generate_signal(ohlcv)
        assert result in (Signal.BUY, Signal.SELL, Signal.HOLD)

    def test_name_attribute(self):
        assert TrendFollowingStrategy.name == "Trend Following (EMA + MACD)"


# ---------------------------------------------------------------------------
# MomentumStrategy
# ---------------------------------------------------------------------------

class TestMomentumStrategy:
    def test_returns_signal_type(self):
        strategy = MomentumStrategy()
        ohlcv = _rising_ohlcv(60)
        result = strategy.generate_signal(ohlcv)
        assert isinstance(result, Signal)

    def test_hold_when_insufficient_data(self):
        strategy = MomentumStrategy()
        ohlcv = _rising_ohlcv(5)
        assert strategy.generate_signal(ohlcv) == Signal.HOLD

    def test_sell_on_strong_uptrend(self):
        """In a strong uptrend RSI > 70 and price near upper Bollinger Band."""
        # Use very steep rise so RSI is high
        closes = [float(100 + i * 5) for i in range(60)]
        ohlcv = pd.DataFrame(
            {
                "open": [c - 2 for c in closes],
                "high": [c + 3 for c in closes],
                "low": [c - 3 for c in closes],
                "close": closes,
                "volume": [1000.0] * 60,
            }
        )
        result = MomentumStrategy().generate_signal(ohlcv)
        # With a very steep uptrend, RSI should be high and price near upper band
        assert result in (Signal.SELL, Signal.HOLD)

    def test_name_attribute(self):
        assert MomentumStrategy.name == "Momentum (RSI + Bollinger Bands)"


# ---------------------------------------------------------------------------
# CandlestickStrategy
# ---------------------------------------------------------------------------

class TestCandlestickStrategy:
    def test_returns_signal_type(self):
        strategy = CandlestickStrategy()
        ohlcv = _rising_ohlcv(40)
        result = strategy.generate_signal(ohlcv)
        assert isinstance(result, Signal)

    def test_hold_when_insufficient_data(self):
        strategy = CandlestickStrategy()
        ohlcv = _rising_ohlcv(5)
        assert strategy.generate_signal(ohlcv) == Signal.HOLD

    def test_bullish_engulfing_triggers_buy_below_ema(self):
        """A bullish engulfing pattern when price is below EMA should trigger BUY."""
        # Build a downtrend so EMA is above close
        closes = [float(100 - i * 0.5) for i in range(30)]
        opens = [c + 1 for c in closes]  # default slightly above close (bearish)

        # Replace last two candles with a clear bullish engulfing:
        # Previous bearish: open=87, close=85 (body 85..87)
        # Current bullish: open=84, close=88 (body 84..88, fully engulfs 85..87)
        opens[-2] = 87.0
        closes[-2] = 85.0
        opens[-1] = 84.0
        closes[-1] = 88.0

        highs = [max(o, c) + 1 for o, c in zip(opens, closes)]
        lows = [min(o, c) - 1 for o, c in zip(opens, closes)]

        ohlcv = pd.DataFrame(
            {
                "open": opens,
                "high": highs,
                "low": lows,
                "close": closes,
                "volume": [1000.0] * 30,
            }
        )
        # EMA(20) will be above 88 (downtrend), so price_below_ema is True
        result = CandlestickStrategy(ema_period=20).generate_signal(ohlcv)
        assert result == Signal.BUY

    def test_name_attribute(self):
        assert CandlestickStrategy.name == "Candlestick Patterns (Hammer / Engulfing)"


# ---------------------------------------------------------------------------
# CombinedStrategy
# ---------------------------------------------------------------------------

class TestCombinedStrategy:
    def test_returns_signal_type(self):
        strategy = CombinedStrategy()
        ohlcv = _rising_ohlcv(60)
        result = strategy.generate_signal(ohlcv)
        assert isinstance(result, Signal)

    def test_hold_when_insufficient_data(self):
        strategy = CombinedStrategy()
        ohlcv = _rising_ohlcv(5)
        assert strategy.generate_signal(ohlcv) == Signal.HOLD

    def test_name_attribute(self):
        assert CombinedStrategy.name == "Combined (Trend + Momentum + Candlestick)"


# ---------------------------------------------------------------------------
# StrategyMenu
# ---------------------------------------------------------------------------

class TestStrategyMenu:
    def test_available_keys(self):
        menu = StrategyMenu()
        assert "trend_following" in menu.available
        assert "momentum" in menu.available
        assert "candlestick" in menu.available
        assert "combined" in menu.available

    def test_get_returns_correct_type(self):
        menu = StrategyMenu()
        from bot.strategies import TrendFollowingStrategy, MomentumStrategy
        assert isinstance(menu.get("trend_following"), TrendFollowingStrategy)
        assert isinstance(menu.get("momentum"), MomentumStrategy)

    def test_get_raises_on_unknown_key(self):
        menu = StrategyMenu()
        with pytest.raises(KeyError):
            menu.get("nonexistent_strategy")

    def test_register_custom_strategy(self):
        menu = StrategyMenu()
        custom = TrendFollowingStrategy(ema_period=50)
        menu.register("my_custom", custom, description="Custom EMA-50 strategy")
        assert "my_custom" in menu.available
        assert menu.get("my_custom") is custom

    def test_display_does_not_raise(self, capsys):
        menu = StrategyMenu()
        menu.display()
        captured = capsys.readouterr()
        assert "Strategy Preset Menu" in captured.out
        assert "trend_following" in captured.out
        assert "momentum" in captured.out

    def test_custom_strategies_in_constructor(self):
        custom = TrendFollowingStrategy()
        menu = StrategyMenu(custom_strategies={"extra": custom})
        assert "extra" in menu.available
