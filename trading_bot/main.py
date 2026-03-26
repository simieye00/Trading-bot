"""Main trading bot entry point with strategy preset menu."""

from __future__ import annotations

import pandas as pd

from trading_bot.bot_runner import BotRunner, BotState
from trading_bot.strategies import STRATEGY_PRESETS
from trading_bot.strategies.base_strategy import BaseStrategy

# Stop icon displayed in the menu
STOP_ICON = "⏹"


def print_menu(state: BotState = BotState.IDLE) -> None:
    """Display the strategy preset selection menu with the current state.

    Args:
        state: Current :class:`BotState` to show in the header.
    """
    print(f"\n=== Trading Bot – Strategy Preset Menu  |  State: {state} ===")
    print("Select a strategy to analyse your price data:\n")
    for i, (key, strategy_cls) in enumerate(STRATEGY_PRESETS.items(), start=1):
        strategy = strategy_cls()
        print(f"  [{i}] {strategy.name}")
        print(f"      {strategy.description}\n")
    print(f"  [{STOP_ICON}] s – Stop the bot")
    print(f"  [q]   q – Quit")
    print("=" * 60)


def select_strategy() -> BaseStrategy | None:
    """Prompt the user to pick a strategy preset or stop/quit.

    Returns:
        An instantiated :class:`BaseStrategy`, or ``None`` when the user
        chooses to stop or quit.
    """
    keys = list(STRATEGY_PRESETS.keys())
    while True:
        choice = input("\nEnter choice: ").strip().lower()
        if choice in ("q", "s"):
            return None
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(keys):
                return STRATEGY_PRESETS[keys[idx]]()
        print("Invalid choice. Please try again.")


def load_sample_data() -> pd.DataFrame:
    """Generate minimal synthetic OHLC data for demonstration purposes."""
    import numpy as np

    rng = np.random.default_rng(42)
    n = 100
    close = 100 + rng.normal(0, 1, n).cumsum()
    close = pd.Series(close, name="close")
    high = close + rng.uniform(0, 1, n)
    low = close - rng.uniform(0, 1, n)
    open_ = close.shift(1).fillna(close.iloc[0])

    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close}
    )


def run(df: pd.DataFrame | None = None) -> None:
    """Run the interactive trading bot loop.

    The bot starts in ``IDLE`` state, transitions to ``RUNNING`` once a
    strategy is selected and the signal is generated, and moves to
    ``STOPPED`` when the user presses **s** or **q**.

    Args:
        df: Optional OHLC DataFrame to use. If ``None``, synthetic data is
            generated for demonstration.
    """
    if df is None:
        df = load_sample_data()
        print("\n[INFO] No data provided – using synthetic demo data.")

    runner: BotRunner | None = None

    print_menu(BotState.IDLE)
    strategy = select_strategy()

    if strategy is None:
        # User chose stop or quit before running any strategy
        print(f"\n{STOP_ICON}  Bot stopped.  State: {BotState.STOPPED}")
        return

    runner = BotRunner(strategy)
    print(f"\n>>> State: {runner.state}")
    print(f">>> Running strategy: {runner.strategy.name}")

    signal = runner.start(df)
    print(f">>> State: {runner.state}")
    print(f">>> Signal: {signal}")

    runner.stop()
    print(f"\n{STOP_ICON}  Bot stopped.  State: {runner.state}")


if __name__ == "__main__":
    run()
