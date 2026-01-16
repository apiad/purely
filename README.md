# Purely 💧

**A lightweight elixir for cleaner, safer, and more fluent Python.**

![PyPI - Version](https://img.shields.io/pypi/v/purely)
![PyPi - Python Version](https://img.shields.io/pypi/pyversions/purely)
![Github - Open Issues](https://img.shields.io/github/issues-raw/apiad/purely)
![PyPi - Downloads (Monthly)](https://img.shields.io/pypi/dm/purely)
![Github - Commits](https://img.shields.io/github/commit-activity/m/apiad/purely)

---

**Purely** is a zero-dependency library designed to bring the best parts of functional programming—safety, pipelines, and immutability—into Python without the academic overhead or complex types. It allows you to write code that reads from top to bottom, rather than inside out.

## 📦 Installation

**Purely** leverages modern Python features (generics) and requires **Python 3.12+**.

```bash
pip install purely
```

## ✨ Features

* **Functional Containers**: `Option` for null-safety and `Result` for explicit error handling.
* **Safe Navigation**: Access deeply nested attributes without worrying about `AttributeError`.
* **Fluent Pipelines**: Chain operations and vectorize list transformations with `Chain` and `pipe`.
* **Architectural Decoupling**: Interface-aware Dependency Injection and Multiple Dispatch.
* **Ergonomic Currying**: Partial application with full type-hint support for IDEs.

## 📚 User Guide

### 1. Functional Containers (Low-Level)

#### Option

Handles missing values without explicit `if x is None` checks.

```python
from purely import Option

# Option(10) -> convert to 20 -> keep because > 5
val = Option(10).convert(lambda x: x * 2).keepif(lambda x: x > 5)
assert val.unwrap() == 20

# Option(None) -> chain broken
empty = Option(None).convert(lambda x: x + 1)
assert empty.is_none()
```

#### Result

Explicit success (`Ok`) or failure (`Err`) states for "Railway Oriented Programming".

```python
from purely.result import Ok, Err

def divide(a, b):
    return Ok(a / b) if b != 0 else Err("Division by zero")

# Fluent error handling without try/except blocks
res = divide(10, 2).then(lambda x: x * 2).unwrap()
assert res == 10.0
```

#### ensure

Asserts the existence of a value. It unwraps an `Option` or checks if a raw value is `None`, raising a custom error if the check fails.

```python
from purely import ensure, Option

# Unwraps a Some(value)
val = ensure(Option(10))
assert val == 10

# Raises ValueError if None
try:
    ensure(None, error="Missing data")
except ValueError as e:
    print(e)  # "Missing data"
```

### 2. Flow & Navigation (Middle-Level)

#### safe

Enables null-safe navigation through nested objects while maintaining IDE autocompletion.

```python
from purely import safe, ensure

user = get_user_or_none() # Could be None

# Access .address.city.name safely. Returns Option(None) if any step fails.
city_name = safe(user).address.city.name

# Crash intentionally only when you must have the value
print(ensure(city_name, "City name is required"))
```

#### pipe

A simple utility to pass a value through a sequence of functions.

```python
from purely import pipe

# 5 -> 10 -> 20 -> "20"
result = pipe(5, lambda x: x * 2, lambda x: x + 10, str)
assert result == "20"
```

#### Chain

A unified container for pipelines, vectorized list operations, and captured error handling.

```python
from purely import Chain

names = (
    Chain(["alice", "bob", "charlie"])
    .filter(lambda n: len(n) > 3)  # ["alice", "charlie"]
    .map(lambda n: n.upper())      # ["ALICE", "CHARLIE"]
    .unwrap()
)

# Exception handling inside the chain
recovered = (
    Chain(10)
    .then(lambda x: x / 0)        # Captures ZeroDivisionError
    .catch(lambda e: 0)           # Recovers with fallback
    .unwrap()
)
assert recovered == 0
```

### 3. High-Level Architecture

#### curry

Transforms functions of multiple arguments into a series of partial applications.

```python
from purely import curry

@curry
def multiply(a, b):
    return a * b

double = multiply(2)
assert double(10) == 20
```

#### Registry (Dependency Injection)

A scoped, interface-aware DI system with automatic MRO (Method Resolution Order) discovery.

```python
from purely import Registry, depends

reg = Registry()
# Registering Postgres automatically satisfies Database and Storage interfaces
reg.register(PostgresDatabase())

@reg.inject
def save_user(user, db: Database = depends(Database)):
    db.save(user)

save_user(new_user)
```

#### dispatcher (Multiple Dispatch)

Runtime polymorphism based on type signatures and value-based predicates.

```python
from purely import dispatcher

@dispatcher
def process(data):
    return "Generic data"

@process.dispatch
def _(data: list):
    return f"List of length {len(data)}"

@process.when(lambda d: isinstance(d, int) and d < 0)
def _(data):
    return "Negative number"

assert process([1, 2]) == "List of length 2"
assert process(-5) == "Negative number"
```

## 🛠 Contribution

We use `uv` for dependency management and a `makefile` for orchestration.

1. **Setup**: Clone the repository and run `make`.
2. **Formatting**: Ensure code adheres to `black` formatting using `make format`.
3. **Testing**: Run the full test suite with `make test-all`.

## 📝 License

Distributed under the MIT License.