import pytest
from purely import dispatcher
from purely.dispatch import AmbiguityError


# --- Hierarchy Setup ---
class Shape:
    pass


class Circle(Shape):
    pass


class Square(Shape):
    size: int


class Renderer:
    pass


class Canvas(Renderer):
    pass


class WebGL(Renderer):
    pass


# --- Dispatcher setup ---
@dispatcher
def draw(shape: Shape, renderer: Renderer):
    return "Generic draw"


@draw.dispatch
def _(shape: Circle, renderer: Renderer):
    return "Drawing circle"


@draw.dispatch
def _(shape: Circle, renderer: Canvas):
    return "Drawing circle on Canvas"


@draw.when(lambda s, r: isinstance(s, Square) and getattr(s, "size", 0) > 100)
def _(shape, renderer):
    return "Drawing HUGE square"


# --- Test Cases ---


def test_hierarchical_dispatch():
    """Verify that more specific arguments (left-to-right) win."""
    # Matches (Circle, Canvas) -> Most specific
    assert draw(Circle(), Canvas()) == "Drawing circle on Canvas"

    # Matches (Circle, Renderer) -> Circle is specific, WebGL falls back to Renderer
    assert draw(Circle(), WebGL()) == "Drawing circle"

    # Matches (Shape, Renderer) -> Falls back to default
    assert draw(Square(), WebGL()) == "Generic draw"


def test_predicate_priority():
    """Verify that .when() conditions are checked before type dispatch."""
    huge_square = Square()
    huge_square.size = 200

    small_square = Square()
    small_square.size = 10

    assert draw(huge_square, Canvas()) == "Drawing HUGE square"
    assert draw(small_square, Canvas()) == "Generic draw"


def test_ambiguity_raises():
    """Verify that identical type signatures raise AmbiguityError."""

    @dispatcher
    def conflict(a, b):
        pass

    @conflict.dispatch
    def _(a: int, b: int):
        return 1

    @conflict.dispatch
    def _(a: int, b: int):
        return 2

    with pytest.raises(AmbiguityError, match="Ambiguous dispatch"):
        conflict(1, 1)


def test_isolation():
    """Verify that different dispatchers don't share registries."""

    @dispatcher
    def func_a(x: int):
        return "a"

    @dispatcher
    def func_b(x: int):
        return "b"

    assert func_a(1) == "a"
    assert func_b(1) == "b"
