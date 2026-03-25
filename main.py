"""Trading Bot – main entry point.

Usage
-----
Run interactively (choose strategy via menu)::

    python main.py

Run with a specific strategy key (non-interactive)::

    python main.py --strategy combined

Run with a custom config file::

    python main.py --config my_config.yaml --strategy trend_following

The bot prints the generated signal for the synthetic sample data included
for demonstration purposes.  Replace ``_load_sample_ohlcv`` with real market
data fetched from your preferred exchange API.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

from bot.strategy_menu import StrategyMenu

try:
    import yaml  # type: ignore[import]
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Demo / sample data helpers
# ---------------------------------------------------------------------------

def _load_sample_ohlcv() -> pd.DataFrame:
    """Return a small synthetic OHLCV DataFrame for demonstration.

    In production, replace this function with a call to your exchange API
    (e.g., Binance, PocketOption) to fetch real 1-minute or 5-minute candles.
    """
    data = {
        "open":   [100, 101, 102, 101, 100, 99, 98, 97, 96, 95,
                   94, 93, 92, 91, 90, 91, 92, 93, 94, 95,
                   96, 97, 98, 99, 100, 101, 102, 103, 104, 105,
                   106, 107, 108, 107, 106, 105, 104, 103, 102, 101],
        "high":   [102, 103, 104, 103, 102, 101, 100, 99, 98, 97,
                   96, 95, 94, 93, 92, 93, 94, 95, 96, 97,
                   98, 99, 100, 101, 102, 103, 104, 105, 106, 107,
                   108, 109, 110, 109, 108, 107, 106, 105, 104, 103],
        "low":    [99, 100, 101, 100, 99, 98, 97, 96, 95, 94,
                   93, 92, 91, 90, 89, 90, 91, 92, 93, 94,
                   95, 96, 97, 98, 99, 100, 101, 102, 103, 104,
                   105, 106, 107, 106, 105, 104, 103, 102, 101, 100],
        "close":  [101, 102, 101, 100, 99, 98, 97, 96, 95, 94,
                   93, 92, 91, 90, 91, 92, 93, 94, 95, 96,
                   97, 98, 99, 100, 101, 102, 103, 104, 105, 106,
                   107, 108, 107, 106, 105, 104, 103, 102, 101, 100],
        "volume": [1000] * 40,
    }
    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def _load_config(config_path: str) -> dict:
    """Load YAML config from *config_path*, returning an empty dict on failure."""
    if not _YAML_AVAILABLE:
        print("[WARNING] PyYAML not installed – using default settings.")
        return {}
    path = Path(config_path)
    if not path.exists():
        print(f"[WARNING] Config file '{config_path}' not found – using defaults.")
        return {}
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Trading Bot – signal generator with strategy presets."
    )
    parser.add_argument(
        "--strategy",
        default=None,
        help=(
            "Strategy preset key to use without interactive prompt.  "
            "Options: trend_following, momentum, candlestick, combined."
        ),
    )
    parser.add_argument(
        "--config",
        default=os.path.join(os.path.dirname(__file__), "config.yaml"),
        help="Path to YAML configuration file (default: config.yaml).",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = _parse_args()
    config = _load_config(args.config)

    menu = StrategyMenu()

    # Determine strategy – CLI flag > config file > interactive menu
    strategy_key = args.strategy or config.get("active_strategy")

    if strategy_key:
        try:
            strategy = menu.get(strategy_key)
            print(f"\n[INFO] Using strategy: {strategy.name}")
        except KeyError as exc:
            print(f"[ERROR] {exc}")
            strategy = menu.select_interactive()
    else:
        strategy = menu.select_interactive()

    # Load market data (replace with real API call in production)
    ohlcv = _load_sample_ohlcv()
    print(f"[INFO] Loaded {len(ohlcv)} candles.")

    # Generate and display the signal
    signal = strategy.generate_signal(ohlcv)
    print(f"\n{'='*40}")
    print(f"  Strategy : {strategy.name}")
    print(f"  Signal   : {signal.value}")
    print(f"{'='*40}\n")


if __name__ == "__main__":
    main()
