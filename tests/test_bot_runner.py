"""Tests for BotState and BotRunner."""

import pytest
import numpy as np
import pandas as pd

from trading_bot.bot_runner import BotRunner, BotState
from trading_bot.strategies.trend_following import TrendFollowingStrategy
from trading_bot.strategies.momentum import MomentumStrategy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_df() -> pd.DataFrame:
    """100-candle OHLC DataFrame for testing."""
    rng = np.random.default_rng(0)
    n = 100
    close = pd.Series(100.0 + rng.normal(0, 0.5, n).cumsum())
    high = close + rng.uniform(0.05, 0.3, n)
    low = close - rng.uniform(0.05, 0.3, n)
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close})


@pytest.fixture
def runner(sample_df) -> BotRunner:
    return BotRunner(TrendFollowingStrategy())


# ---------------------------------------------------------------------------
# BotState
# ---------------------------------------------------------------------------

class TestBotState:
    def test_all_states_exist(self):
        assert BotState.IDLE is not None
        assert BotState.RUNNING is not None
        assert BotState.STOPPED is not None

    def test_idle_icon(self):
        assert BotState.IDLE.icon == "⚪"

    def test_running_icon(self):
        assert BotState.RUNNING.icon == "🟢"

    def test_stopped_icon(self):
        assert BotState.STOPPED.icon == "🔴"

    def test_str_includes_icon_and_value(self):
        assert "⚪" in str(BotState.IDLE) and "IDLE" in str(BotState.IDLE)
        assert "🟢" in str(BotState.RUNNING) and "RUNNING" in str(BotState.RUNNING)
        assert "🔴" in str(BotState.STOPPED) and "STOPPED" in str(BotState.STOPPED)


# ---------------------------------------------------------------------------
# BotRunner – initial state
# ---------------------------------------------------------------------------

class TestBotRunnerInitialState:
    def test_starts_idle(self, runner):
        assert runner.state == BotState.IDLE

    def test_no_signal_before_start(self, runner):
        assert runner.last_signal is None

    def test_strategy_is_stored(self, runner):
        assert isinstance(runner.strategy, TrendFollowingStrategy)


# ---------------------------------------------------------------------------
# BotRunner – start
# ---------------------------------------------------------------------------

class TestBotRunnerStart:
    def test_transitions_to_running(self, runner, sample_df):
        runner.start(sample_df)
        assert runner.state == BotState.RUNNING

    def test_returns_valid_signal(self, runner, sample_df):
        signal = runner.start(sample_df)
        assert signal in {"BUY", "SELL", "HOLD"}

    def test_last_signal_updated(self, runner, sample_df):
        signal = runner.start(sample_df)
        assert runner.last_signal == signal

    def test_start_accepts_different_strategies(self, sample_df):
        runner = BotRunner(MomentumStrategy())
        signal = runner.start(sample_df)
        assert signal in {"BUY", "SELL", "HOLD"}


# ---------------------------------------------------------------------------
# BotRunner – stop
# ---------------------------------------------------------------------------

class TestBotRunnerStop:
    def test_stop_from_idle_transitions_to_stopped(self, runner):
        runner.stop()
        assert runner.state == BotState.STOPPED

    def test_stop_from_running_transitions_to_stopped(self, runner, sample_df):
        runner.start(sample_df)
        runner.stop()
        assert runner.state == BotState.STOPPED

    def test_double_stop_is_noop(self, runner):
        runner.stop()
        runner.stop()  # Should not raise
        assert runner.state == BotState.STOPPED

    def test_cannot_start_after_stop(self, runner, sample_df):
        runner.stop()
        with pytest.raises(RuntimeError, match="stopped"):
            runner.start(sample_df)


# ---------------------------------------------------------------------------
# BotRunner – full lifecycle
# ---------------------------------------------------------------------------

class TestBotRunnerLifecycle:
    def test_full_lifecycle(self, sample_df):
        runner = BotRunner(TrendFollowingStrategy())
        assert runner.state == BotState.IDLE
        signal = runner.start(sample_df)
        assert runner.state == BotState.RUNNING
        assert signal in {"BUY", "SELL", "HOLD"}
        runner.stop()
        assert runner.state == BotState.STOPPED
        assert runner.last_signal == signal
