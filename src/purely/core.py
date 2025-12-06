from __future__ import annotations
import functools
from typing import Callable, Any, TypeVar, overload, TYPE_CHECKING, cast

"""
PURELY 💧
A lightweight library for cleaner, safer, and more fluent Python.
Embrace purity, banish boilerplate.
"""

# Sentinel for missing values
_SENTINEL = object()

# Type variable for generics
T = TypeVar("T")


# -----------------------------------------------------------------------------
# 1. RUST-STYLE OPTION (Defined first for dependency reasons)
# -----------------------------------------------------------------------------


class Option[T]:
    """
    A container that represents either a value (Some) or nothing (None).

    It wraps any object and provides general attribute access (getattr),
    item getters and setters, and calling, to allow null-safe navigation.
    """

    def __init__(self, value: T | None):
        self._value = value

    def is_some(self) -> bool:
        return self._value is not None

    def is_none(self) -> bool:
        return self._value is None

    def unwrap(
        self,
        default: Any = _SENTINEL,
        error: str | Exception = ValueError("Called unwrap on None"),
    ) -> T:
        """Returns the contained value or raises error/returns default."""
        if self._value is not None:
            return self._value

        if default is not _SENTINEL:
            return default

        # Use the global ensure logic (which handles exceptions)
        if isinstance(error, str):
            raise ValueError(error)

        raise error

    def map[U](self, func: Callable[[T], U]) -> Option[U]:
        """Strictly typed transformation."""
        if self._value is None:
            return Option(None)
        return Option(func(self._value))

    def filter(self, predicate: Callable[[T], bool]) -> Option[T]:
        if self._value is not None and predicate(self._value):
            return self
        return Option(None)

    # --- Null Coalescing / Safe Navigation Proxies ---

    def __getattr__(self, name: str) -> Option[Any]:
        """
        Runtime hook for safe attribute access.
        Option(obj).attr returns Option(obj.attr) or Option(None).
        """
        if self._value is None:
            return Option(None)

        return Option(getattr(self._value, name))

    def __call__(self, *args: Any, **kwargs: Any) -> Option[Any]:
        """
        Runtime hook for safe method calls.
        Option(func)(args) returns Option(func(args)) or Option(None).
        """
        if self._value is None:
            return Option(None)

        caller = getattr(self._value, "__call__")
        return Option(caller(*args, **kwargs))

    def __getitem__(self, key: Any) -> Option[Any]:
        """
        Runtime hook for safe item access.
        Option(obj)[key] returns Option(obj[key]) or Option(None).
        """
        if self._value is None:
            return Option(None)

        getter = getattr(self._value, "__getitem__")
        return Option(getter(key))

    def __setitem__(self, key: Any, value: Any):
        """
        Runtime hook for safe item setting.
        Option(obj)[key] = value will work if the underlying works.
        """
        if self._value is None:
            pass

        setter = getattr(self._value, "__setitem__")
        setter(key, value)

    def __eq__(self, other: object) -> bool:
        """
        Check the underlying value for equality.
        """
        if isinstance(other, Option):
            return self._value == other._value

        return self._value == other


# -----------------------------------------------------------------------------
# 2. CORE UTILITIES (ensure, tap, safe)
# -----------------------------------------------------------------------------


def ensure(
    value: T | Option[T] | None, error: str | Exception = ValueError("Value is None")
) -> T:
    """
    Asserts existence.

    If 'value' is an Option (from safe() runtime), it unwraps it.
    If 'value' is a raw value (from safe() static lie), it checks for None.
    """
    # Runtime check: Handle the 'Safe' proxy case
    if isinstance(value, Option):
        return value.unwrap(error=error)

    if value is None:
        if isinstance(error, str):
            raise ValueError(error)

        raise error

    return cast(T, value)


def safe[T](obj: T | None) -> T:
    """
    Wraps a object in Option[T] but returns T typehint.

    This allows the user you continue using Intellisense
    and type-checking from the IDE but maintaining the
    null-safe navigation.
    """
    return cast(T, Option(obj))


def tap[T](value: T, func: Callable[[T], Any]) -> T:
    """Executes func for side effects and returns value."""
    func(value)
    return value


def pipe[T](value: T, *funcs: Callable[[Any], Any]) -> Any:
    """Pipes value through functions."""
    result = value
    for func in funcs:
        result = func(result)
    return result


# -----------------------------------------------------------------------------
# 3. FLUENT INTERFACE (Chain)
# -----------------------------------------------------------------------------


class Chain[T]:
    """Wrapper for method chaining."""

    def __init__(self, value: T):
        self._value = value

    def map[U](self, func: Callable[[T], U]) -> Chain[U]:
        return Chain(func(self._value))

    def then[U](self, func: Callable[[T], U]) -> Chain[U]:
        return self.map(func)

    def __or__[U](self, func: Callable[[T], U]) -> Chain[U]:
        return self.map(func)

    def tap(self, func: Callable[[T], Any]) -> Chain[T]:
        func(self._value)
        return self

    def ensure(
        self, error: str | Exception = ValueError("Chain value is None")
    ) -> Chain[T]:
        ensure(self._value, error)
        return self

    @property
    def value(self) -> T:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Chain):
            return self._value == other._value
        return self._value == other
