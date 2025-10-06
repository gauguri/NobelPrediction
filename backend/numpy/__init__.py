"""Lightweight numpy stand-in for offline execution."""
from __future__ import annotations

import math
import random as _random
from types import SimpleNamespace
from typing import Sequence

from pandas import Series


class _Generator:
    def __init__(self, seed: int | None = None):
        self._rng = _random.Random(seed)

    def normal(self, scale: float = 1.0, size: int = 1) -> list[float]:
        return [self._rng.gauss(0.0, scale) for _ in range(size)]


default_rng = lambda seed=None: _Generator(seed)

random = SimpleNamespace(default_rng=default_rng)


def exp(values: Sequence[float] | Series) -> Series:
    if isinstance(values, Series):
        source = values.tolist()
    else:
        source = list(values)
    return Series(math.exp(value) for value in source)


def full(size: int, fill_value: float) -> Series:
    return Series(fill_value for _ in range(size))
