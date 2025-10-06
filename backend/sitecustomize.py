"""Runtime compatibility patches for the execution environment."""
from __future__ import annotations

import typing

# Pydantic < 1.10.13 expects ForwardRef._evaluate to accept only positional
# arguments. Python 3.12 added a new keyword-only argument. We shim in a wrapper
# that provides the compatibility parameter when running in this environment.
if hasattr(typing, "ForwardRef"):
    _orig_evaluate = typing.ForwardRef._evaluate

    def _patched_evaluate(self, globalns, localns, third=None, *, recursive_guard=None):  # type: ignore[override]
        positional_guard = third
        keyword_guard = recursive_guard

        if keyword_guard is None and positional_guard is not None:
            # Backwards compatibility path: pydantic<1.10.13 calls the function with
            # a single positional set() argument representing the recursive guard.
            keyword_guard = positional_guard
            positional_guard = None

        try:
            return _orig_evaluate(
                self,
                globalns,
                localns,
                positional_guard,
                recursive_guard=keyword_guard,
            )
        except TypeError as exc:
            if "multiple values for argument 'recursive_guard'" not in str(exc):
                raise

            # Some Python/Pydantic combinations expect the recursive guard as the
            # final positional argument rather than as a keyword-only argument.
            return _orig_evaluate(self, globalns, localns, keyword_guard)

    typing.ForwardRef._evaluate = _patched_evaluate  # type: ignore[assignment]
