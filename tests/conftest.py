"""
Pytest configuration and shared fixtures for Nautilus tests.

This file is automatically discovered by pytest and provides:
- Session setup/teardown
- Shared fixtures for all tests
- Custom markers
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Define custom markers
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "safety: Safety constraint tests")
    config.addinivalue_line("markers", "slow: Slow tests (full conversations)")


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def data_dir():
    """Return the data directory."""
    return PROJECT_ROOT / "data"


@pytest.fixture(scope="session")
def rules_dir():
    """Return the rules directory."""
    return PROJECT_ROOT / "rules"


@pytest.fixture(scope="session")
def test_data_dir():
    """Return the test data directory."""
    return PROJECT_ROOT / "tests" / "conversations"


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging state between tests."""
    from app_logging.logger import get_logger
    logger = get_logger(__name__)
    logger.set_trace_id()
    yield


@pytest.fixture
def mock_nemo_session():
    """Fixture: Mock NeMo session state."""
    return {
        "machine_name": "Williams Attack from Mars",
        "manufacturer": "Williams",
        "era": "WPC_90s",
        "skill_level": "beginner",
        "current_symptom": "left_flipper_dead",
        "confidence": 0.75,
        "evidence": [],
        "variables": {}
    }


@pytest.fixture
def mock_yaml_rules(data_dir):
    """Fixture: Load actual YAML rules for testing."""
    import yaml
    
    rules_path = PROJECT_ROOT / "rules"
    rules = {}
    
    for rule_file in ["global.yaml", "beginner.yaml", "intermediate.yaml", "pro.yaml"]:
        with open(rules_path / rule_file) as f:
            rules[rule_file.replace(".yaml", "")] = yaml.safe_load(f)
    
    return rules
