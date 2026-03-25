"""Trading strategy presets."""

from .trend_following import TrendFollowingStrategy
from .momentum import MomentumStrategy
from .combined import CombinedStrategy

STRATEGY_PRESETS = {
    "trend": TrendFollowingStrategy,
    "momentum": MomentumStrategy,
    "combined": CombinedStrategy,
}

__all__ = [
    "TrendFollowingStrategy",
    "MomentumStrategy",
    "CombinedStrategy",
    "STRATEGY_PRESETS",
]
