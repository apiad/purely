from __future__ import annotations
from typing import Callable, Any


class Ok[T]:
    """Represents a successful computation."""

    __match_args__ = ("value",)

    def __init__(self, value: T):
        self.value = value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self, default: Any = None) -> T:
        return self.value

    def then[E, U](self, func: Callable[[T], U]) -> Result[U, E]:
        """Maps the value if Ok, otherwise returns the Err."""
        try:
            return Ok(func(self.value))
        except Exception as e:
            return Err(e)  # type: ignore

    def catch[E](self, func: Callable[[E], T]) -> Result[T, E]:
        """Skips if Ok."""
        return self

    def __repr__(self):
        return f"Ok({self.value!r})"

    def __eq__(self, other):
        return isinstance(other, Ok) and self.value == other.value


class Err[E]:
    """Represents a failed computation."""

    __match_args__ = ("error",)

    def __init__(self, error: E):
        self.error = error

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self, default: Any = None) -> Any:
        if default is not None:
            return default
        if isinstance(self.error, Exception):
            raise self.error
        raise ValueError(str(self.error))

    def then[T, U](self, func: Callable[[T], U]) -> Result[U, E]:
        """Skips if Err."""
        return self  # type: ignore

    def catch[T](self, func: Callable[[E], T]) -> Result[T, E]:
        """Recovers from an error state."""
        try:
            return Ok(func(self.error))
        except Exception as e:
            return Err(e)  # type: ignore

    def __repr__(self):
        return f"Err({self.error!r})"

    def __eq__(self, other):
        return isinstance(other, Err) and self.error == other.error


# Type Alias for convenience
type Result[T, E] = Ok[T] | Err[E]
