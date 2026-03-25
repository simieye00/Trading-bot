"""Base strategy interface shared by all strategy presets."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

import pandas as pd


class Signal(str, Enum):
    """Trading signal emitted by a strategy."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class BaseStrategy(ABC):
    """Abstract base class for all strategy presets.

    Subclasses must implement :meth:`generate_signal` which accepts an OHLCV
    DataFrame and returns the signal for the **most recent** bar.
    """

    name: str = "BaseStrategy"

    @abstractmethod
    def generate_signal(self, ohlcv: pd.DataFrame) -> Signal:
        """Analyse *ohlcv* data and return a :class:`Signal`.

        Parameters
        ----------
        ohlcv:
            DataFrame with at least the columns ``open``, ``high``, ``low``,
            ``close``, and ``volume``.  Rows are ordered oldest-first.

        Returns
        -------
        Signal
            ``BUY``, ``SELL``, or ``HOLD``.
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
