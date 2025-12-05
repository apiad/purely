from typing import TypeVar, Callable, Generic, Optional, Any, Union, List

# -----------------------------------------------------------------------------
# 1. THE ESSENTIALS (Direct helpers)
# -----------------------------------------------------------------------------

def ensure[T](value: Optional[T], error: Union[str, Exception] = ValueError("Value is None")) -> T:
    """
    Takes a value T | None. Returns T or raises an exception.
    """
    if value is None:
        if isinstance(error, str):
            raise ValueError(error)
        raise error
    return value

def tap[T](value: T, func: Callable[[T], Any]) -> T:
    """
    Executes a function for side effects and returns the original value.
    """
    func(value)
    return value

def pipe[T](value: T, *funcs: Callable[[Any], Any]) -> Any:
    """
    Pipes a value through a sequence of functions.
    """
    result = value
    for func in funcs:
        result = func(result)
    return result

# -----------------------------------------------------------------------------
# 2. THE FLUENT INTERFACE (Chain)
# -----------------------------------------------------------------------------

class Chain[T]:
    """
    A wrapper to allow method chaining on any object.
    Usage: Chain(5) | double | str
    """
    def __init__(self, value: T):
        self._value = value

    def map[U](self, func: Callable[[T], U]) -> 'Chain[U]':
        return Chain(func(self._value))

    def then[U](self, func: Callable[[T], U]) -> 'Chain[U]':
        return self.map(func)

    def __or__[U](self, func: Callable[[T], U]) -> 'Chain[U]':
        return self.map(func)

    def tap(self, func: Callable[[T], Any]) -> 'Chain[T]':
        func(self._value)
        return self

    def ensure(self, error: Union[str, Exception] = ValueError("Chain value is None")) -> 'Chain[T]':
        ensure(self._value, error)
        return self

    def unwrap(self) -> T:
        return self._value

# -----------------------------------------------------------------------------
# 3. RUST-STYLE OPTION (Safe handling)
# -----------------------------------------------------------------------------

class Option[T]:
    """
    A container that represents either a value (Some) or nothing (None).
    """
    def __init__(self, value: Optional[T]):
        self._value = value

    @classmethod
    def of(cls, value: Optional[T]) -> 'Option[T]':
        return cls(value)

    def is_some(self) -> bool:
        return self._value is not None

    def is_none(self) -> bool:
        return self._value is None

    def __nonzero__(self) -> bool:
        return self.is_some()

    def unwrap(self, error: Union[str, Exception] = ValueError("Called unwrap on None")) -> T:
        return ensure(self._value, error)

    def unwrap_or(self, default: T) -> T:
        return self._value if self._value is not None else default

    def map(self, func: Callable[[T], U]) -> 'Option[U]':
        if self._value is None:
            return Option(None)

        return Option(func(self._value))

    def filter(self, predicate: Callable[[T], bool]) -> 'Option[T]':
        if self._value is not None and predicate(self._value):
            return self

        return Option(None)