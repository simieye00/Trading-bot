"""Bot state management for the trading bot."""

from __future__ import annotations

from enum import Enum

import pandas as pd

from trading_bot.strategies.base_strategy import BaseStrategy, Signal

# Icons shown next to each trading signal in the output
SIGNAL_ICONS: dict[Signal, str] = {
    "BUY": "📈",
    "SELL": "📉",
    "HOLD": "⏸",
}


def format_signal(signal: Signal) -> str:
    """Return the signal string decorated with its icon.

    Args:
        signal: One of ``"BUY"``, ``"SELL"``, or ``"HOLD"``.

    Returns:
        A string of the form ``"<icon> <SIGNAL>"``, e.g. ``"📈 BUY"``.
    """
    icon = SIGNAL_ICONS.get(signal, "")
    return f"{icon} {signal}" if icon else signal


class BotState(Enum):
    """Lifecycle states of the trading bot."""

    IDLE = "IDLE"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"

    # Unicode icon shown next to the state name in the UI
    @property
    def icon(self) -> str:
        _icons = {
            BotState.IDLE: "⚪",
            BotState.RUNNING: "🟢",
            BotState.STOPPED: "🔴",
        }
        return _icons[self]

    def __str__(self) -> str:
        return f"{self.icon} {self.value}"


class BotRunner:
    """Manages the lifecycle (state) of the trading bot.

    States
    ------
    IDLE     ⚪  – Bot has been created but has not started yet.
    RUNNING  🟢  – Bot is actively processing signals.
    STOPPED  🔴  – Bot has been stopped; no further signals will be generated.

    Transitions
    -----------
    IDLE → RUNNING  via :meth:`start`
    RUNNING → STOPPED via :meth:`stop`
    """

    def __init__(self, strategy: BaseStrategy) -> None:
        self._strategy = strategy
        self._state = BotState.IDLE
        self._last_signal: Signal | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def state(self) -> BotState:
        """Current lifecycle state of the bot."""
        return self._state

    @property
    def last_signal(self) -> Signal | None:
        """The most recent signal generated, or ``None`` if not yet run."""
        return self._last_signal

    @property
    def strategy(self) -> BaseStrategy:
        """The strategy used by this runner."""
        return self._strategy

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------

    def start(self, df: pd.DataFrame) -> Signal:
        """Start the bot, run the strategy, and return the signal.

        Args:
            df: OHLC DataFrame to analyse.

        Returns:
            The trading signal produced by the strategy.

        Raises:
            RuntimeError: If the bot has already been stopped.
        """
        if self._state == BotState.STOPPED:
            raise RuntimeError(
                "Cannot start a stopped bot. Create a new BotRunner instance."
            )
        self._state = BotState.RUNNING
        self._last_signal = self._strategy.generate_signal(df)
        return self._last_signal

    def stop(self) -> None:
        """Stop the bot.

        Can be called from any state; subsequent calls are no-ops.
        """
        self._state = BotState.STOPPED
