"""
Essential tests for FileDecommissionProcessor.
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from utils.file_processor import FileDecommissionProcessor


def log_file_diff(file_path: str, original_content: str, modified_content: str):
    """Log file changes in git diff style with colors and dark theme styling."""
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

            # Dark theme header with file path
            print(
                "\n\033[1;36m═══════════════════════════════════════════════════════════════\033[0m"
            )
            print(f"\033[1;33m📝 DIFF: {file_path}\033[0m")
            print(
                f"\033[1;32m+{additions} additions\033[0m \033[1;31m-{removals} removals\033[0m"
            )
            print(
                "\033[1;36m═══════════════════════════════════════════════════════════════\033[0m"
            )

            for i, line in enumerate(lines):
                if line.startswith("---"):
                    # Dark theme file header - original
                    print(f"\033[1;31m--- {line[4:]}\033[0m")
                elif line.startswith("+++"):
                    # Dark theme file header - modified
                    print(f"\033[1;32m+++ {line[4:]}\033[0m")
                elif line.startswith("@@"):
                    # Dark theme line numbers context
                    print(f"\033[1;34m{line}\033[0m")
                elif line.startswith("+") and not line.startswith("+++"):
                    # Bright green for additions (dark theme)
                    line_content = line[1:]  # Remove the + prefix
                    print(f"\033[1;32m+{line_content}\033[0m")
                elif line.startswith("-") and not line.startswith("---"):
                    # Bright red for removals (dark theme)
                    line_content = line[1:]  # Remove the - prefix
                    print(f"\033[1;31m-{line_content}\033[0m")
                elif line.strip():
                    # Context lines (unchanged) - dim white for dark theme
                    print(f"\033[0;37m {line}\033[0m")

            print(
                "\033[1;36m═══════════════════════════════════════════════════════════════\033[0m"
            )
            print()


class TestFileDecommissionProcessor:
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_terraform_file(self):
        """Test Terraform file processing."""
        processor = FileDecommissionProcessor()
        original_content = (
            'resource "azurerm_postgresql" "postgres_air" {\n  name = "postgres_air"\n}'
        )
        header = processor._generate_header(
            "postgres_air", "DB-DECOMM-001", "infrastructure"
        )

        result = processor._process_infrastructure(
            original_content, "postgres_air", header
        )

        # Log diff for visualization
        log_file_diff("terraform_prod_critical_databases.tf", original_content, result)

        assert "# resource" in result
        assert "postgres_air" in result
        assert "PROCESSED" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_config_file(self):
        """Test configuration file processing."""
        processor = FileDecommissionProcessor()
        original_content = "database: postgres_air\nhost: localhost"
        header = processor._generate_header(
            "postgres_air", "DB-DECOMM-001", "configuration"
        )

        result = processor._process_configuration(
            original_content, "postgres_air", header
        )

        # Log diff for visualization
        log_file_diff("config/database.yml", original_content, result)

        assert "# database: postgres_air" in result
        assert "host: localhost" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_code_file(self):
        """Test code file processing."""
        processor = FileDecommissionProcessor()
        original_content = 'def connect():\n    return psycopg2.connect("postgres_air")'
        header = processor._generate_header("postgres_air", "DB-DECOMM-001", "code")

        result = processor._process_code(original_content, "postgres_air", header)

        # Log diff for visualization
        log_file_diff("scripts/migrate.py", original_content, result)

        assert "def connect_to_postgres_air():" in result
        assert "raise Exception" in result
        assert "processed" in result

