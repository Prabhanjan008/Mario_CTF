"""
Pytest configuration fixture for Mario OJAS CTF.
Isolates test runs into a temporary SQLite database to avoid polluting the production database.
"""

import os
import tempfile
import pytest

# Point tests to a separate temporary database
TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "mario_ctf_test_isolated.db").replace("\\", "/")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

@pytest.fixture(scope="session", autouse=True)
def clean_test_environment():
    """Removes previous test database file if it exists, ensuring clean test state."""
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    yield
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
