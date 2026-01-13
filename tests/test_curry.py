import pytest
from purely import curry, pipe

# -----------------------------------------------------------------------------
# 1. BASIC CURRYING TESTS
# -----------------------------------------------------------------------------


@curry
def add(a, b, c):
    """Adds three numbers."""
    return a + b + c


def test_curry_all_at_once():
    """Verify it works like a normal function when all args are passed."""
    assert add(1, 2, 3) == 6


def test_curry_step_by_step():
    """Verify one-by-one argument passing."""
    step1 = add(1)
    step2 = step1(2)
    result = step2(3)
    assert result == 6
    assert add(1)(2)(3) == 6


def test_curry_partial():
    """Verify passing multiple args in different chunks."""
    assert add(1, 2)(3) == 6
    assert add(1)(2, 3) == 6


# -----------------------------------------------------------------------------
# 2. ADVANCED SIGNATURES (Keywords & Defaults)
# -----------------------------------------------------------------------------


@curry
def greet(greeting, name, punctuation="."):
    return f"{greeting}, {name}{punctuation}"


def test_curry_with_keywords():
    """Verify keywords can be used in the curried chain."""
    assert greet("Hello")(name="Alice") == "Hello, Alice."
    assert greet(name="Bob")("Hi") == "Hi, Bob."


def test_curry_with_defaults():
    """
    Verify arity is determined by required arguments.
    'punctuation' has a default, so arity should be 2.
    """
    # Should execute after 2 arguments because the 3rd is optional
    assert greet("Welcome", "Home") == "Welcome, Home."

    # Overriding the default
    assert greet("Welcome", "Home", "!") == "Welcome, Home!"


# -----------------------------------------------------------------------------
# 3. METADATA & INTEGRATION
# -----------------------------------------------------------------------------


def test_curry_metadata():
    """Verify @wraps preserves the original function's identity."""
    assert add.__name__ == "add"
    assert "Adds three numbers" in add.__doc__


def test_curry_pipeline_integration():
    """Demonstrate why currying is useful with pipe()."""

    @curry
    def multiply(a, b):
        return a * b

    # 10 -> *2 -> +5
    # multiply(2) returns a function that takes one argument
    res = pipe(10, multiply(2), lambda x: x + 5)
    assert res == 25


def test_curry_variadic_limitations():
    """
    Verify behavior with *args.
    Arity is based on fixed required params.
    """

    @curry
    def sum_fixed_and_more(a, b, *args):
        return a + b + sum(args)

    # Arity is 2. It will execute as soon as a and b are provided.
    assert sum_fixed_and_more(1)(2) == 3
    # Extra args must be passed with the last required arg or after
    assert sum_fixed_and_more(1, 2, 3, 4) == 10
