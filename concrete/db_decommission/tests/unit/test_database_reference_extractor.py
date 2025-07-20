"""
Essential tests for DatabaseReferenceExtractor.
"""

import pytest
import tempfile
import os
from pathlib import Path
from ...entity_reference_extractor import DatabaseReferenceExtractor, MatchedFile


class TestDatabaseReferenceExtractor:
    """Test suite for database reference extraction."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_references_basic(self):
        """Test basic extraction with mock data."""
        # Create mock repomix file content
        mock_content = '''This file is a merged representation of the entire codebase.

<file path="config/database.yml">
production:
  adapter: postgresql
  database: postgres_air
  username: postgres
  password: secret
  host: localhost
  port: 5432
</file>

<file path="scripts/migrate.py">
#!/usr/bin/env python3
"""Migration script for postgres_air database."""

import os
import psycopg2

DATABASE_URL = "postgresql://user:pass@localhost:5432/postgres_air"

def connect_to_postgres_air():
    """Connect to the postgres_air database."""
    return psycopg2.connect(DATABASE_URL)
</file>'''

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(mock_content)
            temp_file = f.name

        try:
            # Test extraction
            extractor = DatabaseReferenceExtractor()
            result = await extractor.extract_references(
                database_name="postgres_air", target_repo_pack_path=temp_file
            )

            # Assert results
            assert result["success"] is True
            assert result["database_name"] == "postgres_air"
            assert result["total_references"] > 0
            assert len(result["matched_files"]) == 2  # Both files have references

            # Check that files were extracted
            extraction_dir = Path(result["extraction_directory"])
            assert extraction_dir.exists()
            assert (extraction_dir / "config" / "database.yml").exists()
            assert (extraction_dir / "scripts" / "migrate.py").exists()

        finally:
            # Cleanup
            os.unlink(temp_file)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_directory_preservation(self):
        """Test directory structure is preserved."""
        # Create mock content with nested directories
        mock_content = """<file path="deep/nested/path/config.json">
{
  "database": "postgres_air",
  "host": "localhost"
}
</file>

<file path="another/very/deep/path/settings.py">
DATABASE_NAME = "postgres_air"
DATABASE_HOST = "localhost"
</file>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(mock_content)
            temp_file = f.name

        try:
            extractor = DatabaseReferenceExtractor()
            result = await extractor.extract_references(
                database_name="postgres_air", target_repo_pack_path=temp_file
            )

            # Verify nested directory structure is preserved
            extraction_dir = Path(result["extraction_directory"])
            assert (
                extraction_dir / "deep" / "nested" / "path" / "config.json"
            ).exists()
            assert (
                extraction_dir / "another" / "very" / "deep" / "path" / "settings.py"
            ).exists()

            # Verify file contents are preserved
            with open(extraction_dir / "deep" / "nested" / "path" / "config.json") as f:
                content = f.read()
                assert "postgres_air" in content
                assert '"database": "postgres_air"' in content

        finally:
            os.unlink(temp_file)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_no_matches_found(self):
        """Test behavior when no database references found."""
        # Create mock content with no database references
        mock_content = """<file path="README.md">
# Project Documentation

This is a sample project without any database references.
</file>

<file path="utils/helpers.py">
def helper_function():
    return "no database references here"
</file>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(mock_content)
            temp_file = f.name

        try:
            extractor = DatabaseReferenceExtractor()
            result = await extractor.extract_references(
                database_name="postgres_air", target_repo_pack_path=temp_file
            )

            # Assert graceful handling of no matches
            assert result["success"] is True
            assert result["total_references"] == 0
            assert len(result["matched_files"]) == 0

            # Directory should still be created but empty
            extraction_dir = Path(result["extraction_directory"])
            assert extraction_dir.exists()

        finally:
            os.unlink(temp_file)

