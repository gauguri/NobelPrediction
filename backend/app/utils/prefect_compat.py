"""Lightweight stand-ins for Prefect decorators used in the project.

This module provides ``flow`` and ``task`` decorators with the same call
signature as the Prefect 2.x equivalents that we rely on.  They simply return
the wrapped function and record a few descriptive attributes so that the rest
of the application can continue to call the decorated functions directly.

The aim is to avoid a heavy dependency on Prefect while preserving the public
API expected by the flow modules.  Should the real Prefect package be installed
later these wrappers can easily be replaced by the genuine decorators without
changing any call sites.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class _WrapperMetadata:
    """Attach minimal metadata mirroring Prefect's attributes."""

    name: str
    kind: str


def _attach_metadata(func: F, *, name: Optional[str], kind: str) -> F:
    metadata = _WrapperMetadata(name=name or func.__name__, kind=kind)
    setattr(func, "_prefect_metadata", metadata)
    return func


def task(func: Optional[F] = None, *, name: Optional[str] = None, **_: Any) -> F | Callable[[F], F]:
    """Return a decorator that simply preserves the wrapped function.

    The Prefect ``task`` decorator accepts a large collection of keyword
    arguments.  We only need to accept the call signature so we swallow extra
    keyword arguments via ``**_`` and ignore them.
    """

    def decorator(inner: F) -> F:
        @wraps(inner)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return inner(*args, **kwargs)

        return _attach_metadata(cast(F, wrapper), name=name, kind="task")

    if func is not None:
        return decorator(func)
    return decorator


def flow(func: Optional[F] = None, *, name: Optional[str] = None, **_: Any) -> F | Callable[[F], F]:
    """Return a decorator mirroring ``prefect.flow`` for our limited use."""

    def decorator(inner: F) -> F:
        @wraps(inner)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return inner(*args, **kwargs)

        return _attach_metadata(cast(F, wrapper), name=name, kind="flow")

    if func is not None:
        return decorator(func)
    return decorator

