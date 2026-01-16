import pytest
from curry import curry

# --- Setup Functions for Testing ---


@curry
def add(a: int, b: int) -> int:
    return a + b


@curry
def full_house(a: int, b: int, c: int, d: int, e: int) -> int:
    return a + b + c + d + e


@curry
def with_kwargs(a: int, b: int, c: int = 10) -> int:
    return a + b + c


# --- Test Cases ---


def test_full_application():
    """Test that providing all arguments at once works normally."""
    assert add(1, 2) == 3
    assert full_house(1, 1, 1, 1, 1) == 5


def test_step_by_step_currying():
    """Test one-argument-at-a-time application."""
    # 2-arity
    plus_one = add(1)
    assert callable(plus_one)
    assert plus_one(2) == 3

    # 5-arity
    step1 = full_house(1)
    step2 = step1(2)
    step3 = step2(3)
    step4 = step3(4)
    result = step4(5)
    assert result == 15


def test_grouped_partial_application():
    """Test providing multiple but not all arguments."""
    partial_fh = full_house(1, 2)
    assert callable(partial_fh)

    partial_more = partial_fh(3, 4)
    assert callable(partial_more)

    assert partial_more(5) == 15


def test_keyword_arguments():
    """Test that currying respects keyword arguments."""
    # Full with keywords
    assert add(a=1, b=2) == 3

    # Partial with keywords
    plus_ten = add(b=10)
    assert plus_ten(a=5) == 15

    # Mix of positional and keyword
    assert with_kwargs(1)(2) == 13  # a=1, b=2, c defaults to 10
    assert with_kwargs(1, 2, c=20) == 23


def test_over_application():
    """Test providing more arguments than the signature requires (standard Python behavior)."""
    # This should behave like the underlying function
    with pytest.raises(TypeError):
        add(1, 2, 3)


def test_metadata_preservation():
    """Test that @wraps correctly preserves function identity."""
    assert add.__name__ == "add"
    assert "full_house" in str(full_house)


def test_reusability_of_partials():
    """Test that a partial function can be called multiple times with different values."""
    base = full_house(1, 2, 3)  # needs 2 more

    assert base(4, 5) == 15
    assert base(10, 20) == 36
    assert base(0, 0) == 6


def test_zero_arity():
    """Test that a function with no arguments returns immediately."""

    @curry
    def say_hi():
        return "hi"

    assert say_hi() == "hi"


def test_type_hints_sanity():
    """
    Note: Real type checking happens via Mypy/Pyright,
    but we can verify the protocols at runtime if needed.
    """

    @curry
    def triple(a: int, b: int, c: int) -> int:
        return a * b * c

    # Verify the chain of callables
    res1 = triple(2)
    assert callable(res1)
    res2 = res1(3)
    assert callable(res2)
    assert res2(4) == 24


if __name__ == "__main__":
    pytest.main([__file__])
