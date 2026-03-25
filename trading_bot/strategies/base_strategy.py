"""Base class for all trading strategies."""

from abc import ABC, abstractmethod
from typing import Literal

import pandas as pd

Signal = Literal["BUY", "SELL", "HOLD"]


class BaseStrategy(ABC):
    """Abstract base class for a trading strategy.

    Subclasses must implement :meth:`generate_signal` which returns a
    ``Signal`` (``"BUY"``, ``"SELL"``, or ``"HOLD"``) given an OHLC
    DataFrame.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for the strategy."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of the strategy logic."""

    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """Analyse the provided OHLC data and return a trading signal.

        Args:
            df: DataFrame with columns ``open``, ``high``, ``low``, ``close``
                and a datetime index, ordered from oldest to newest.

        Returns:
            ``"BUY"``, ``"SELL"``, or ``"HOLD"``.
        """

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(name={self.name!r})"
