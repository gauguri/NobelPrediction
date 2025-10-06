"""Minimal pandas-like interface for offline execution.

This module provides the limited functionality required by the NobelPrediction
backend without depending on the external pandas package. It supports the
DataFrame operations that the ETL, modeling, and reporting flows rely on.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, List, Sequence
import csv
import json

Scalar = float | int | str | bool | None


def _coerce_numeric(value: str | None) -> Scalar:
    if value is None:
        return None
    if value == "":
        return ""
    try:
        if value.isdigit():
            return int(value)
    except AttributeError:
        return value
    try:
        return float(value)
    except ValueError:
        return value


class Series:
    def __init__(self, values: Iterable[Scalar]):
        self._values: List[Scalar] = list(values)

    def _coerce(self, other: Any, op: str) -> List[Scalar]:
        if isinstance(other, Series):
            if len(other) != len(self):
                raise ValueError("Series length mismatch")
            return list(other._values)
        if isinstance(other, Sequence) and not isinstance(other, (str, bytes)):
            if len(other) != len(self):
                raise ValueError("Sequence length mismatch")
            return list(other)
        if isinstance(other, (int, float, bool)):
            return [other] * len(self)
        raise TypeError(f"Unsupported operand type for {op}: {type(other)!r}")

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[Scalar]:
        return iter(self._values)

    def __getitem__(self, index: int) -> Scalar:
        return self._values[index]

    def __setitem__(self, index: int, value: Scalar) -> None:
        self._values[index] = value

    def __repr__(self) -> str:
        return f"Series({self._values!r})"

    def __add__(self, other: Any) -> "Series":
        values = self._coerce(other, "+")
        return Series(a + b for a, b in zip(self._values, values))

    def __radd__(self, other: Any) -> "Series":
        return self.__add__(other)

    def __sub__(self, other: Any) -> "Series":
        values = self._coerce(other, "-")
        return Series(a - b for a, b in zip(self._values, values))

    def __rsub__(self, other: Any) -> "Series":
        values = self._coerce(other, "-")
        return Series(b - a for a, b in zip(self._values, values))

    def __mul__(self, other: Any) -> "Series":
        values = self._coerce(other, "*")
        return Series(a * b for a, b in zip(self._values, values))

    def __rmul__(self, other: Any) -> "Series":
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> "Series":
        values = self._coerce(other, "/")
        return Series(a / b for a, b in zip(self._values, values))

    def __rtruediv__(self, other: Any) -> "Series":
        values = self._coerce(other, "/")
        return Series(b / a for a, b in zip(self._values, values))

    def __neg__(self) -> "Series":
        return Series(-value for value in self._values)

    def __iadd__(self, other: Any) -> "Series":
        result = self.__add__(other)
        self._values = result._values
        return self

    def __isub__(self, other: Any) -> "Series":
        result = self.__sub__(other)
        self._values = result._values
        return self

    def __eq__(self, other: Any) -> "Series":  # type: ignore[override]
        values = self._coerce(other, "==")
        return Series(a == b for a, b in zip(self._values, values))

    def __ne__(self, other: Any) -> "Series":  # type: ignore[override]
        values = self._coerce(other, "!=")
        return Series(a != b for a, b in zip(self._values, values))

    def __ge__(self, other: Any) -> "Series":
        values = self._coerce(other, ">=")
        return Series(a >= b for a, b in zip(self._values, values))

    def unique(self) -> list[Scalar]:
        seen: list[Scalar] = []
        for value in self._values:
            if value not in seen:
                seen.append(value)
        return seen

    def notnull(self) -> "Series":
        return Series(value is not None for value in self._values)

    def all(self) -> bool:
        return all(bool(value) for value in self._values)

    def tolist(self) -> list[Scalar]:
        return list(self._values)


@dataclass
class _RowView:
    data: dict[str, Scalar]

    def __getitem__(self, key: str) -> Scalar:
        return self.data[key]


class DataFrame:
    def __init__(self, rows: Iterable[dict[str, Scalar]]):
        self._rows: List[dict[str, Scalar]] = [dict(row) for row in rows]
        columns: list[str] = []
        for row in self._rows:
            for key in row.keys():
                if key not in columns:
                    columns.append(key)
        self._columns = columns

    def __len__(self) -> int:
        return len(self._rows)

    def __iter__(self) -> Iterator[str]:
        return iter(self._columns)

    @property
    def columns(self) -> list[str]:
        return list(self._columns)

    @property
    def empty(self) -> bool:
        return not self._rows

    def copy(self) -> "DataFrame":
        return DataFrame(self._rows)

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, Series):
            mask = [bool(value) for value in key]
            filtered = [row for row, keep in zip(self._rows, mask) if keep]
            return DataFrame(filtered)
        if isinstance(key, list) and key and isinstance(key[0], bool):
            mask = [bool(value) for value in key]
            filtered = [row for row, keep in zip(self._rows, mask) if keep]
            return DataFrame(filtered)
        if isinstance(key, str):
            values = [row.get(key) for row in self._rows]
            return Series(values)
        raise TypeError("Unsupported key type for DataFrame")

    def __setitem__(self, key: str, values: Any) -> None:
        if isinstance(values, (int, float, str, bool)) or values is None:
            values_list = [values] * len(self._rows)
        else:
            values_list = list(values)
        if len(values_list) != len(self._rows):
            raise ValueError("Length of values does not match DataFrame")
        for row, value in zip(self._rows, values_list):
            row[key] = value
        if key not in self._columns:
            self._columns.append(key)

    def to_csv(self, path: Path | str, index: bool = False) -> None:
        if index:
            raise NotImplementedError("index export is not supported")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self._columns)
            writer.writeheader()
            for row in self._rows:
                writer.writerow({column: row.get(column) for column in self._columns})

    def to_dict(self, orient: str = "records") -> list[dict[str, Scalar]]:
        if orient != "records":
            raise NotImplementedError("Only records orient is supported")
        return [dict(row) for row in self._rows]

    def iterrows(self) -> Iterator[tuple[int, _RowView]]:
        for index, row in enumerate(self._rows):
            yield index, _RowView(dict(row))
def read_csv(path: Path | str) -> DataFrame:
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        records = []
        for raw_row in reader:
            row = {key: _coerce_numeric(value) for key, value in raw_row.items()}
            records.append(row)
    return DataFrame(records)


def read_json(path: Path | str) -> DataFrame:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        return DataFrame(data)
    raise TypeError("JSON structure not supported for DataFrame")
