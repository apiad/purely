import pytest
from purely import Ok, Err, dispatcher

# --- Setup for Integration Test ---


@dispatcher
def process_response(res: Ok):
    return f"Success: {res.value}"


@process_response.dispatch
def _(res: Err):
    return f"Error: {res.error}"


# --- Test Cases ---


def test_monadic_flow():
    """Verify that .then() only executes on Success."""
    # Happy path: 10 -> 20 -> "20"
    res = Ok(10).then(lambda x: x * 2).then(str)
    assert res == Ok("20")

    # Error path: execution stops at Err
    res = Err("Initial Fail").then(lambda x: x * 2)
    assert res == Err("Initial Fail")


def test_exception_capture():
    """Verify that .then() captures internal exceptions as Err."""
    res = Ok(10).then(lambda x: x / 0)
    assert res.is_err()
    assert isinstance(res.error, ZeroDivisionError)


def test_recovery_with_catch():
    """Verify that .catch() allows recovery into an Ok state."""
    res = Err("Bad state").catch(lambda e: "recovered")
    assert res == Ok("recovered")

    # .catch is ignored on Ok
    res = Ok(10).catch(lambda e: 0)
    assert res == Ok(10)


def test_unwrap_behavior():
    """Verify unwrap returns value or raises/defaults."""
    assert Ok(5).unwrap() == 5
    assert Err("fail").unwrap(default=0) == 0

    with pytest.raises(ValueError, match="fail"):
        Err("fail").unwrap()


def test_dispatch_integration():
    """
    Verify the 'Purely' Masterstroke:
    Handling Result states via Multiple Dispatch.
    """
    success = Ok({"id": 123, "status": "active"})
    failure = Err("Connection Timeout")

    assert process_response(success) == "Success: {'id': 123, 'status': 'active'}"
    assert process_response(failure) == "Error: Connection Timeout"


def test_pattern_matching_compatibility():
    """Verify Python 3.10+ Structural Pattern Matching."""

    def match_test(res):
        match res:
            case Ok(val):
                return f"got {val}"
            case Err(e):
                return f"failed {e}"

    assert match_test(Ok(1)) == "got 1"
    assert match_test(Err("x")) == "failed x"
