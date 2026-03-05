"""
pytest configuration and shared fixtures for the framework test suite.
"""

import sys
from pathlib import Path
import pytest

# Always add project root to sys.path so `src.*` imports resolve.
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session", autouse=True)
def disable_exploit_verification():
    """
    By default, disable live exploit sandbox execution during unit tests to
    keep the suite fast and side-effect-free.  Individual test classes that
    specifically want to exercise the sandbox can re-enable it.
    """
    from src.utils.config import config
    _orig = config.enable_exploit_verification
    config.enable_exploit_verification = False
    yield
    config.enable_exploit_verification = _orig
