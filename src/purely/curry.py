from functools import wraps
from inspect import signature
from typing import Callable, Any, TypeVar, Protocol, overload

R = TypeVar("R", covariant=True)
P1 = TypeVar("P1", contravariant=True)
P2 = TypeVar("P2", contravariant=True)
P3 = TypeVar("P3", contravariant=True)
P4 = TypeVar("P4", contravariant=True)
P5 = TypeVar("P5", contravariant=True)

# -----------------------------------------------------------------------------
# 1. CURRIED PROTOCOLS (For Type Hinting)
# -----------------------------------------------------------------------------


class Curried2(Protocol[P1, P2, R]):
    @overload
    def __call__(self, arg1: P1) -> Callable[[P2], R]: ...
    @overload
    def __call__(self, arg1: P1, arg2: P2) -> R: ...
    def __call__(self, *args, **kwargs): ...


class Curried3(Protocol[P1, P2, P3, R]):
    @overload
    def __call__(self, arg1: P1) -> Curried2[P2, P3, R]: ...
    @overload
    def __call__(self, arg1: P1, arg2: P2) -> Callable[[P3], R]: ...
    @overload
    def __call__(self, arg1: P1, arg2: P2, arg3: P3) -> R: ...
    def __call__(self, *args, **kwargs): ...


class Curried4(Protocol[P1, P2, P3, P4, R]):
    @overload
    def __call__(self, arg1: P1) -> Curried3[P2, P3, P4, R]: ...
    @overload
    def __call__(self, arg1: P1, arg2: P2) -> Curried2[P3, P4, R]: ...
    @overload
    def __call__(self, arg1: P1, arg2: P2, arg3: P3) -> Callable[[P4], R]: ...
    @overload
    def __call__(self, arg1: P1, arg2: P2, arg3: P3, arg4: P4) -> R: ...
    def __call__(self, *args, **kwargs): ...


class Curried5(Protocol[P1, P2, P3, P4, P5, R]):
    @overload
    def __call__(self, arg1: P1) -> Curried4[P2, P3, P4, P5, R]: ...
    @overload
    def __call__(self, arg1: P1, arg2: P2) -> Curried3[P3, P4, P5, R]: ...
    @overload
    def __call__(self, arg1: P1, arg2: P2, arg3: P3) -> Curried2[P4, P5, R]: ...
    @overload
    def __call__(self, arg1: P1, arg2: P2, arg3: P3, arg4: P4) -> Callable[[P5], R]: ...
    @overload
    def __call__(self, arg1: P1, arg2: P2, arg3: P3, arg4: P4, arg5: P5) -> R: ...
    def __call__(self, *args, **kwargs): ...


# -----------------------------------------------------------------------------
# 2. THE CURRY DECORATOR
# -----------------------------------------------------------------------------


@overload
def curry(func: Callable[[P1, P2], R]) -> Curried2[P1, P2, R]: ...


@overload
def curry(func: Callable[[P1, P2, P3], R]) -> Curried3[P1, P2, P3, R]: ...


@overload
def curry(func: Callable[[P1, P2, P3, P4], R]) -> Curried4[P1, P2, P3, P4, R]: ...


@overload
def curry(
    func: Callable[[P1, P2, P3, P4, P5], R],
) -> Curried5[P1, P2, P3, P4, P5, R]: ...


def curry(func: Callable[..., R]) -> Any:
    """
    Transforms a function into a curried version.
    Supports partial application across any number of calls.
    """
    sig = signature(func)
    arity = len(
        [
            p
            for p in sig.parameters.values()
            if p.default is p.empty and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
        ]
    )

    def make_wrapper(*args, **kwargs):
        @wraps(func)
        def curried(*next_args, **next_kwargs):
            combined_args = args + next_args
            combined_kwargs = {**kwargs, **next_kwargs}

            if len(combined_args) + len(combined_kwargs) >= arity:
                return func(*combined_args, **combined_kwargs)

            # Recursively wrap to keep the currying state
            return make_wrapper(*combined_args, **combined_kwargs)

        # This handles the initial call with no arguments or a partial call
        return curried

    # Immediately evaluate with initial args provided at decoration (usually none)
    return make_wrapper()
