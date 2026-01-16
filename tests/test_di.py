import pytest
from purely import Registry, depends


class Database:
    def query(self):
        pass


class Postgres(Database):
    def query(self):
        return "Postgres"


# --- Test Cases ---


def test_register_callable_with_interface():
    """Verify that we can register a lambda/callable for a specific interface."""
    reg = Registry()

    # Register a simple lambda for the Database interface
    reg.register(lambda: Postgres(), interface=Database)

    @reg.inject
    def use_db(db: Database = depends(Database)):
        return db.query()

    assert use_db() == "Postgres"


def test_register_instance_with_explicit_interface():
    """Verify that explicit interface takes precedence and ignores MRO."""
    reg = Registry()
    pg = Postgres()

    # Manually bind pg to 'object' (highly unusual, but proves the point)
    reg.register(pg, interface=object)

    assert reg.resolve(object) is pg

    # Since we used an explicit interface, it didn't do the MRO climb for Database
    with pytest.raises(LookupError):
        reg.resolve(Database)


def test_factory_without_interface_fallback():
    """Verify that even without an interface, a factory's MRO is discovered."""
    reg = Registry()
    reg.register(Postgres())  # No interface provided

    assert isinstance(reg.resolve(Database), Postgres)
    assert isinstance(reg.resolve(Postgres), Postgres)
