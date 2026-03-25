"""Main trading bot entry point with strategy preset menu."""

from __future__ import annotations

import sys

import pandas as pd

from trading_bot.strategies import STRATEGY_PRESETS
from trading_bot.strategies.base_strategy import BaseStrategy


def print_menu() -> None:
    """Display the strategy preset selection menu."""
    print("\n=== Trading Bot – Strategy Preset Menu ===")
    print("Select a strategy to analyse your price data:\n")
    for i, (key, strategy_cls) in enumerate(STRATEGY_PRESETS.items(), start=1):
        strategy = strategy_cls()
        print(f"  [{i}] {strategy.name}")
        print(f"      {strategy.description}\n")
    print("  [q] Quit")
    print("==========================================")


def select_strategy() -> BaseStrategy | None:
    """Prompt the user to pick a strategy preset.

    Returns:
        An instantiated :class:`BaseStrategy` or ``None`` if the user quits.
    """
    keys = list(STRATEGY_PRESETS.keys())
    while True:
        choice = input("\nEnter choice: ").strip().lower()
        if choice == "q":
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

    Args:
        df: Optional OHLC DataFrame to use. If ``None``, synthetic data is
            generated for demonstration.
    """
    if df is None:
        df = load_sample_data()
        print("\n[INFO] No data provided – using synthetic demo data.")

    print_menu()
    strategy = select_strategy()
    if strategy is None:
        print("Goodbye!")
        return

    print(f"\n>>> Running strategy: {strategy.name}")
    signal = strategy.generate_signal(df)
    print(f">>> Signal: {signal}")


if __name__ == "__main__":
    run()
