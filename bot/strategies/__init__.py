"""Strategies package."""

from .trend_following import TrendFollowingStrategy
from .momentum import MomentumStrategy
from .candlestick import CandlestickStrategy
from .combined import CombinedStrategy

__all__ = [
    "TrendFollowingStrategy",
    "MomentumStrategy",
    "CandlestickStrategy",
    "CombinedStrategy",
]
