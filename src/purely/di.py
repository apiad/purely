from functools import wraps
from inspect import signature
from typing import Any, Callable, Dict, Type, TypeVar, Optional, cast

T = TypeVar("T")

# --- 1. THE MARKER ---


class _Depends:
    def __init__(self, interface: Type):
        self.interface = interface


def depends[T](interface: type[T]) -> T:
    return cast(T, _Depends(interface))


# --- 2. THE REGISTRY ---


class Registry:
    """
    A scoped container for dependencies.
    Supports registration via explicit interface or automatic MRO discovery.
    """

    def __init__(self):
        self._providers: Dict[Type, Callable[[], Any]] = {}

    def register(self, implementation: Any, interface: Optional[Type] = None):
        """
        Registers a provider.

        Implementation can be an instance, a type, or a callable.

        - If interface is provided: Maps implementation to that specific type.
        - If interface is None: Maps implementation to all types in its MRO.
        """
        # Determine the provider function
        if callable(implementation) and not isinstance(implementation, type):
            provider = implementation
        else:
            provider = lambda: implementation

        # Case 1: Explicit interface registration
        if interface is not None:
            self._providers[interface] = provider
            return

        # Case 2: Automatic MRO registration
        # Note: For factories without an explicit interface, we execute once to find the type
        instance = provider()
        target_type = type(instance)

        for cls in target_type.mro():
            if cls is object:
                continue
            if cls not in self._providers:
                self._providers[cls] = provider

    def resolve[T](self, interface: Type[T]) -> T:
        if interface not in self._providers:
            raise LookupError(
                f"No provider registered for interface: {interface.__name__}"
            )
        return self._providers[interface]()

    def inject[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        sig = signature(func)
        injection_points = {
            name: param.default.interface
            for name, param in sig.parameters.items()
            if isinstance(param.default, _Depends)
        }

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            resolved_kwargs = {}

            for name, interface in injection_points.items():
                if name not in kwargs:
                    resolved_kwargs[name] = self.resolve(interface)

            return func(*args, **{**resolved_kwargs, **kwargs})

        return wrapper
