from functools import wraps
from inspect import signature
from typing import Callable, Any, Type, TypeVar, List, Tuple, Dict

T = TypeVar("T")


class AmbiguityError(TypeError):
    """Raised when multiple dispatch candidates are equally specific."""

    pass


class Dispatcher:
    """
    A hierarchical, lexicographical multiple dispatcher.
    Dispatches based on the closest MRO match for each argument in order.
    """

    def __init__(self, default_func: Callable):
        self.default_func = default_func
        self.predicates: List[Tuple[Callable, Callable]] = []
        # List of (tuple_of_types, implementation_func)
        self.registry: List[Tuple[Tuple[Type, ...], Callable]] = []
        wraps(default_func)(self)

    def dispatch(self, func: Callable) -> Callable:
        """Registers an implementation based on type annotations."""
        sig = signature(func)
        types = tuple(
            param.annotation if param.annotation is not param.empty else object
            for param in sig.parameters.values()
        )
        self.registry.append((types, func))
        return func

    def when(self, condition: Callable) -> Callable:
        """Registers an implementation based on a predicate (value-based)."""

        def decorator(func: Callable):
            self.predicates.append((condition, func))
            return func

        return decorator

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        # 1. Predicates take absolute priority (exact match logic)
        for condition, func in self.predicates:
            try:
                if condition(*args, **kwargs):
                    return func(*args, **kwargs)
            except Exception:
                continue

        # 2. Hierarchical Lexicographical MRO Dispatch
        candidates = self.registry

        # Filter candidates by looking at each positional argument
        for i, val in enumerate(args):
            if not candidates:
                break

            val_type = type(val)
            matches = []
            min_dist = float("inf")

            for types, func in candidates:
                # If the implementation has fewer parameters than provided, skip
                if i >= len(types):
                    continue

                target_type = types[i]
                if issubclass(val_type, target_type):
                    # Calculate MRO distance (0 is exact match)
                    try:
                        dist = val_type.mro().index(target_type)
                    except ValueError:
                        dist = 1000  # Interface/Protocol fallback

                    if dist < min_dist:
                        min_dist = dist
                        matches = [(types, func)]
                    elif dist == min_dist:
                        matches.append((types, func))

            candidates = matches

        # 3. Final Resolution
        if not candidates:
            return self.default_func(*args, **kwargs)

        if len(candidates) > 1:
            # Check if signatures are truly identical to raise Ambiguity
            # We filter for candidates that have the same number of arguments as provided
            final_candidates = [c for c in candidates if len(c[0]) == len(args)]
            if len(final_candidates) > 1:
                sigs = [str(t) for t, _ in final_candidates]
                raise AmbiguityError(
                    f"Ambiguous dispatch for {self.default_func.__name__}. "
                    f"Multiple candidates matched with same specificity: {sigs}"
                )
            return final_candidates[0][1](*args, **kwargs)

        return candidates[0][1](*args, **kwargs)


def dispatcher(func: Callable) -> Dispatcher:
    """Decorator to create a new isolated dispatcher."""
    return Dispatcher(func)
