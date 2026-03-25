"""Strategy Preset Menu.

Provides a registry of named strategy presets and a simple text-based
interactive menu so the user can toggle between them at runtime.

Usage
-----
From the REPL or a script::

    from bot.strategy_menu import StrategyMenu

    menu = StrategyMenu()
    strategy = menu.select_interactive()   # prompts the user
    signal = strategy.generate_signal(ohlcv_dataframe)

Or non-interactively::

    strategy = menu.get("momentum")
    signal = strategy.generate_signal(ohlcv_dataframe)
"""

from __future__ import annotations

from typing import Dict, Optional

from bot.strategies import (
    TrendFollowingStrategy,
    MomentumStrategy,
    CandlestickStrategy,
    CombinedStrategy,
)
from bot.strategies.base_strategy import BaseStrategy


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_REGISTRY: Dict[str, BaseStrategy] = {
    "trend_following": TrendFollowingStrategy(),
    "momentum": MomentumStrategy(),
    "candlestick": CandlestickStrategy(),
    "combined": CombinedStrategy(),
}

_DESCRIPTIONS: Dict[str, str] = {
    "trend_following": (
        "EMA (20) + MACD  –  Follows the dominant trend direction.  "
        "Buys when price > EMA and MACD crosses up; sells on the reverse."
    ),
    "momentum": (
        "RSI + Bollinger Bands  –  Mean-reversion / momentum strategy.  "
        "Buys when RSI < 30 and price near the lower band; sells when RSI > 70 "
        "and price near the upper band."
    ),
    "candlestick": (
        "Hammer / Inverted Hammer / Engulfing  –  Detects reversal candlestick "
        "patterns filtered by a 20-period EMA trend direction."
    ),
    "combined": (
        "Combined (Trend + Momentum + Candlestick)  –  Aggregates all three "
        "presets via majority vote for a more robust signal."
    ),
}


class StrategyMenu:
    """Registry and interactive selector for strategy presets.

    Parameters
    ----------
    custom_strategies:
        Optional mapping of additional ``{key: strategy}`` pairs to register
        alongside the built-in presets.
    """

    def __init__(
        self,
        custom_strategies: Optional[Dict[str, BaseStrategy]] = None,
    ) -> None:
        self._strategies: Dict[str, BaseStrategy] = dict(_REGISTRY)
        self._descriptions: Dict[str, str] = dict(_DESCRIPTIONS)
        if custom_strategies:
            self._strategies.update(custom_strategies)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def available(self) -> list[str]:
        """Return sorted list of registered strategy keys."""
        return sorted(self._strategies.keys())

    def get(self, key: str) -> BaseStrategy:
        """Return the strategy registered under *key*.

        Parameters
        ----------
        key:
            One of the keys from :attr:`available`.

        Raises
        ------
        KeyError
            If *key* is not registered.
        """
        if key not in self._strategies:
            raise KeyError(
                f"Unknown strategy '{key}'. "
                f"Available: {', '.join(self.available)}"
            )
        return self._strategies[key]

    def register(self, key: str, strategy: BaseStrategy, description: str = "") -> None:
        """Register a new strategy preset.

        Parameters
        ----------
        key:
            Unique identifier string.
        strategy:
            An instance of a :class:`~bot.strategies.base_strategy.BaseStrategy`
            subclass.
        description:
            Human-readable description shown in the menu.
        """
        self._strategies[key] = strategy
        self._descriptions[key] = description

    def display(self) -> None:
        """Print the strategy menu to stdout."""
        print("\n" + "=" * 60)
        print("  Strategy Preset Menu")
        print("=" * 60)
        for idx, key in enumerate(self.available, start=1):
            strategy = self._strategies[key]
            desc = self._descriptions.get(key, "")
            print(f"\n  [{idx}] {key}")
            print(f"      Name : {strategy.name}")
            if desc:
                print(f"      Info : {desc}")
        print("\n" + "=" * 60)

    def select_interactive(self) -> BaseStrategy:
        """Display the menu and prompt the user to pick a strategy.

        Returns
        -------
        BaseStrategy
            The chosen strategy instance.
        """
        self.display()
        keys = self.available
        while True:
            raw = input(
                f"\nEnter strategy number (1-{len(keys)}) or key name: "
            ).strip()
            # Accept numeric input
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(keys):
                    chosen = keys[idx]
                    print(f"\n  ✔  Selected: {self._strategies[chosen].name}\n")
                    return self._strategies[chosen]
            # Accept key name input
            elif raw in self._strategies:
                print(f"\n  ✔  Selected: {self._strategies[raw].name}\n")
                return self._strategies[raw]
            print(f"  Invalid selection '{raw}'. Please try again.")
