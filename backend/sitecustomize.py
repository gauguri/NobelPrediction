"""Runtime compatibility patches for the execution environment."""
from __future__ import annotations

import typing

# Pydantic < 1.10.13 expects ForwardRef._evaluate to accept only positional
# arguments. Python 3.12 added a new keyword-only argument. We shim in a wrapper
# that provides the compatibility parameter when running in this environment.
if hasattr(typing, "ForwardRef"):
    _orig_evaluate = typing.ForwardRef._evaluate

    def _patched_evaluate(self, globalns, localns, third=None, *, recursive_guard=None):  # type: ignore[override]
        if recursive_guard is None:
            # Backwards compatibility path: pydantic<1.10.13 calls the function with
            # a single positional set() argument representing the recursive guard.
            recursive_guard = third
            third = None
        return _orig_evaluate(self, globalns, localns, third, recursive_guard=recursive_guard)

    typing.ForwardRef._evaluate = _patched_evaluate  # type: ignore[assignment]
