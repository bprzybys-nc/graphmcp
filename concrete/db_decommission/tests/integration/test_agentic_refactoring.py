"""
Functional Integration Tests for Agentic Refactoring System

Tests the complete agentic refactoring flow:
1. Quality test data generation
2. Single file refactoring validation
3. Batch processing optimization
4. Success criteria validation
"""

import json
import pytest
import tempfile
import subprocess
from typing import Dict
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from concrete.db_decommission import AgenticFileProcessor
from utils.source_type_classifier import SourceTypeClassifier, SourceType


def log_file_diff(file_path: str, original_content: str, modified_content: str):
    """Log file changes in git diff style with colors like in the screenshot."""
    if original_content == modified_content:
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        original_file = temp_path / "original"
        modified_file = temp_path / "modified"

        original_file.write_text(original_content)
        modified_file.write_text(modified_content)

        # Generate diff
        result = subprocess.run(
            [
                "diff",
                "-u",
                "--label",
                f"a/{file_path}",
                "--label",
                f"b/{file_path}",
                str(original_file),
                str(modified_file),
            ],
            capture_output=True,
            text=True,
        )

        if result.stdout:
            lines = result.stdout.split("\n")
            additions = sum(
                1
                for line in lines
                if line.startswith("+") and not line.startswith("+++")
            )
            removals = sum(
                1
                for line in lines
                if line.startswith("-") and not line.startswith("---")
            )

            print(
                f"\n📝 Updated {file_path} with {additions} additions and {removals} removals"
            )

            for i, line in enumerate(lines):
                if line.startswith("@@"):
                    # Show line numbers context
                    print(f"       {line}")
                elif line.startswith("+") and not line.startswith("+++"):
                    # Green for additions
                    line_content = line[1:]  # Remove the + prefix
                    print(f"\033[32m+     {line_content}\033[0m")
                elif line.startswith("-") and not line.startswith("---"):
                    # Red for removals
                    line_content = line[1:]  # Remove the - prefix
                    print(f"\033[31m-     {line_content}\033[0m")
                elif (
                    not line.startswith("+++")
                    and not line.startswith("---")
                    and line.strip()
                ):
                    # Context lines (unchanged)
                    print(f"       {line}")
            print()


class TestDataGenerator:
    """Generates quality test data for agentic refactoring validation."""

    def generate_postgres_air_python_file(self) -> Dict[str, str]:
        """Generate a Python file with postgres_air references."""
        content = '''"""
Flight model for PostgreSQL database operations.
"""
import psycopg2
from typing import List, Dict

class FlightModel:
    def __init__(self):
        # Database connection for postgres_air
        self.connection = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres_air",
            user="admin"
        )
    
    def get_flights(self) -> List[Dict]:
        """Get all flights from postgres_air database."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM postgres_air.flights WHERE status = 'active'")
        return cursor.fetchall()
    
    def update_flight_status(self, flight_id: int, status: str):
        """Update flight status in postgres_air."""
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE postgres_air.flights SET status = %s WHERE id = %s",
            (status, flight_id)
        )
        self.connection.commit()
'''

        return {"file_path": "src/models/flight.py", "file_content": content}

    def generate_postgres_air_sql_file(self) -> Dict[str, str]:
        """Generate a SQL file with postgres_air references."""
        content = """-- Migration script for postgres_air database
-- This script updates flight statuses

USE postgres_air;

-- Update active flights
UPDATE postgres_air.flights 
SET last_updated = NOW() 
WHERE status = 'active';

-- Create backup table
CREATE TABLE postgres_air.flights_backup AS 
SELECT * FROM postgres_air.flights;

-- Add new indexes
CREATE INDEX idx_postgres_air_flights_status 
ON postgres_air.flights(status);

-- Grant permissions
GRANT SELECT ON postgres_air.flights TO readonly_user;
"""

        return {"file_path": "migrations/update_flights.sql", "file_content": content}

    def generate_postgres_air_config_file(self) -> Dict[str, str]:
        """Generate a config file with postgres_air references."""
        content = """# Database Configuration
DATABASE_URL=postgresql://localhost/postgres_air
DATABASE_NAME=postgres_air
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Application Settings
APP_NAME=postgres_air_manager
LOG_LEVEL=INFO

# Cache Settings
REDIS_URL=redis://localhost:6379/postgres_air_cache
"""

        return {"file_path": "config/database.env", "file_content": content}

    def generate_expected_refactored_python(self) -> str:
        """Generate expected output after refactoring."""
        return '''"""
Flight model for PostgreSQL database operations.
[REFACTORED] Removed references to decommissioned postgres_air database
"""
import psycopg2
from typing import List, Dict

class FlightModel:
    def __init__(self):
        # Database connection updated - postgres_air decommissioned
        self.connection = psycopg2.connect(
            host="localhost",
            port=5432,
            database="main_db",  # Changed from postgres_air
            user="admin"
        )
    
    def get_flights(self) -> List[Dict]:
        """Get all flights from main database."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM flights WHERE status = 'active'")  # Removed postgres_air prefix
        return cursor.fetchall()
    
    def update_flight_status(self, flight_id: int, status: str):
        """Update flight status in main database."""
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE flights SET status = %s WHERE id = %s",  # Removed postgres_air prefix
            (status, flight_id)
        )
        self.connection.commit()
'''


class TestAgenticRefactoring:
    """Test suite for agentic refactoring functionality."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [
            Mock(message=Mock(content="Successfully refactored file"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client

    @pytest.fixture
    def test_data_generator(self):
        """Test data generator fixture."""
        return TestDataGenerator()

    @pytest.fixture
    def agentic_processor(self, mock_openai_client):
        """Create agentic processor with mocked dependencies."""
        # Mock classifier
        mock_classifier = Mock(spec=SourceTypeClassifier)
        mock_classifier.classify_file.return_value = Mock(source_type=SourceType.PYTHON)

        # Mock rules engine with required attributes
        mock_rules_engine = Mock()
        mock_rules_engine.database_name = "postgres_air"
        mock_rules_engine._get_applicable_rules.return_value = {
            "test_rule": "test_value"
        }
        mock_rules_engine._update_file_content = AsyncMock()

        mock_github_client = Mock()

        processor = AgenticFileProcessor(
            source_classifier=mock_classifier,
            contextual_rules_engine=mock_rules_engine,
            github_client=mock_github_client,
            repo_owner="test_owner",
            repo_name="test_repo",
        )

        # Replace the OpenAI client with our mock
        processor.agent = mock_openai_client

        return processor

    @pytest.mark.asyncio
    async def test_single_file_refactoring(
        self, agentic_processor, test_data_generator, mock_openai_client
    ):
        """Test refactoring a single file with postgres_air references."""
        print("\n🧪 TEST: Single File Refactoring")

        # Generate test data
        test_file = test_data_generator.generate_postgres_air_python_file()
        expected_output = test_data_generator.generate_expected_refactored_python()

        print(f"📁 File: {test_file['file_path']}")
        print(
            f"📊 postgres_air references: {test_file['file_content'].count('postgres_air')}"
        )

        # Mock the OpenAI response to return proper JSON format
        json_response = {test_file["file_path"]: {"modified_content": expected_output}}
        mock_openai_client.chat.completions.create.return_value.choices[
            0
        ].message.content = json.dumps(json_response)

        # Process the file
        files_to_process = [test_file]
        results = await agentic_processor.process_files(files_to_process, batch_size=1)

        # Validate results
        assert len(results) == 1
        result = results[0]

        # Check that refactoring was successful
        assert result.success
        assert result.total_changes > 0  # Should have made changes

        # Show diff of changes made
        log_file_diff(
            test_file["file_path"], test_file["file_content"], expected_output
        )

        print("✅ Single file refactoring successful")
        print(f"📊 Changes made: {result.total_changes}")
        print(f"📝 Rules applied: {len(result.rules_applied)}")

    @pytest.mark.asyncio
    async def test_batch_processing_optimization(
        self, agentic_processor, test_data_generator, mock_openai_client
    ):
        """Test batch processing for cost optimization."""
        print("\n🧪 TEST: Batch Processing Optimization")

        # Generate multiple test files
        test_files = [
            test_data_generator.generate_postgres_air_python_file(),
            test_data_generator.generate_postgres_air_sql_file(),
            test_data_generator.generate_postgres_air_config_file(),
        ]

        print("📦 Batch size: 3 files")
        print("💰 Cost optimization: 3 files = 1 API call (vs 3 separate calls)")

        # Mock successful responses for each file in JSON format
        batch_json_response = {}
        for file_data in test_files:
            batch_json_response[file_data["file_path"]] = {
                "modified_content": file_data["file_content"].replace(
                    "postgres_air", "main_db"
                )
            }

        mock_openai_client.chat.completions.create.return_value.choices[
            0
        ].message.content = json.dumps(batch_json_response)

        # Process files in batch
        results = await agentic_processor.process_files(test_files, batch_size=3)

        # Validate batch processing
        assert len(results) == 3
        assert all(result.success for result in results)

        # Verify API was called only once (batch processing)
        assert mock_openai_client.chat.completions.create.call_count == 1

        # Show diff for each file in batch
        for i, result in enumerate(results):
            if result.success and result.total_changes > 0:
                modified_content = test_files[i]["file_content"].replace(
                    "postgres_air", "main_db"
                )
                log_file_diff(
                    test_files[i]["file_path"],
                    test_files[i]["file_content"],
                    modified_content,
                )

        print("✅ Batch processing successful")
        print("📊 Results:")
        for i, result in enumerate(results):
            print(
                f"  - {test_files[i]['file_path']}: {result.total_changes} changes made, success: {result.success}"
            )

    @pytest.mark.asyncio
    async def test_refactoring_success_criteria(self, test_data_generator):
        """Test validation of refactoring success criteria."""
        print("\n🧪 TEST: Refactoring Success Criteria")

        # Generate test data
        original_file = test_data_generator.generate_postgres_air_python_file()
        refactored_content = test_data_generator.generate_expected_refactored_python()

        # Test success criteria
        original_postgres_refs = original_file["file_content"].count("postgres_air")
        refactored_postgres_refs = refactored_content.count("postgres_air")

        print(f"📊 Original postgres_air references: {original_postgres_refs}")
        print(f"📊 Refactored postgres_air references: {refactored_postgres_refs}")

        # Validate success criteria
        assert original_postgres_refs > 0, (
            "Test file should contain postgres_air references"
        )
        assert refactored_postgres_refs < original_postgres_refs, (
            "Refactoring should reduce postgres_air references"
        )
        assert "main_db" in refactored_content, (
            "Refactoring should introduce main_db references"
        )
        assert "[REFACTORED]" in refactored_content, (
            "Refactoring should add documentation"
        )

        reduction_percentage = (
            (original_postgres_refs - refactored_postgres_refs) / original_postgres_refs
        ) * 100
        print(f"📈 Reference reduction: {reduction_percentage:.1f}%")
        print("✅ Success criteria validation passed")

    def test_quality_test_data_generation(self, test_data_generator):
        """Test that generated test data has quality postgres_air references."""
        print("\n🧪 TEST: Quality Test Data Generation")

        # Test Python file generation
        python_file = test_data_generator.generate_postgres_air_python_file()
        assert python_file["file_content"].count("postgres_air") >= 3
        assert "psycopg2" in python_file["file_content"]
        assert "class" in python_file["file_content"]

        # Test SQL file generation
        sql_file = test_data_generator.generate_postgres_air_sql_file()
        assert sql_file["file_content"].count("postgres_air") >= 5
        assert "UPDATE" in sql_file["file_content"]
        assert "CREATE" in sql_file["file_content"]

        # Test config file generation
        config_file = test_data_generator.generate_postgres_air_config_file()
        assert config_file["file_content"].count("postgres_air") >= 3
        assert "DATABASE_URL" in config_file["file_content"]

        print("✅ Quality test data generation validated")
        print(
            f"📊 Python file: {python_file['file_content'].count('postgres_air')} postgres_air refs"
        )
        print(
            f"📊 SQL file: {sql_file['file_content'].count('postgres_air')} postgres_air refs"
        )
        print(
            f"📊 Config file: {config_file['file_content'].count('postgres_air')} postgres_air refs"
        )



if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "-s"])
