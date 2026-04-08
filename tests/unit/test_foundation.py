import pytest

from copilot_orchestrator.core.config import settings
from copilot_orchestrator.core.logger import setup_logging


def test_settings_load() -> None:
    """Verify that settings can be loaded and have default values."""
    assert settings.PROJECT_NAME == "copilot-orchestrator"
    assert settings.VERSION == "0.0.0"


def test_logging_setup() -> None:
    """Verify that logging setup executes without raising exceptions."""
    try:
        setup_logging()
    except Exception as e:
        pytest.fail(f"Logging setup failed with exception: {e}")
