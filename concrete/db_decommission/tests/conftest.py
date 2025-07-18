"""
Test configuration for database decommissioning tests.
"""

import sys
import pytest
from pathlib import Path

# Add project root to path so we can import from the main framework
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# DB-specific fixtures
@pytest.fixture
def mock_config_path():
    """Provide a mock config path for testing."""
    return "test_config.json"

@pytest.fixture
def postgres_air_database():
    """Provide test database name."""
    return "postgres_air"

@pytest.fixture
def test_data_generator():
    """Test data generator fixture."""
    from concrete.db_decommission.tests.integration.test_agentic_refactoring import TestDataGenerator
    return TestDataGenerator()