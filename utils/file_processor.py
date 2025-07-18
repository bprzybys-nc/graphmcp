"""
File Processor - General Purpose Implementation for Entity Processing

This module provides a general-purpose file processor that can be used for any entity type,
not just databases. It supports various processing strategies and can be extended for
different use cases.
"""

from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ProcessingStrategy(Enum):
    """Available processing strategies."""

    INFRASTRUCTURE = "infrastructure"
    CONFIGURATION = "configuration"
    CODE = "code"
    DOCUMENTATION = "documentation"
    CUSTOM = "custom"


@dataclass
class ProcessingResult:
    """Result of file processing operation."""

    entity_name: str
    source_directory: str
    output_directory: str
    processed_files: List[str]
    strategies_applied: Dict[str, str]
    success: bool
    error_message: Optional[str] = None


class FileProcessor:
    """
    General-purpose file processor for entity decommissioning and processing.

    This processor can be used for databases, services, applications, or any other
    entity type that needs systematic file processing.
    """

    def __init__(
        self, entity_type: str = "entity", contact_email: str = "ops-team@company.com"
    ):
        """
        Initialize the file processor.

        Args:
            entity_type: Type of entity being processed (e.g., 'database', 'service', 'application')
            contact_email: Contact email for processing inquiries
        """
        self.entity_type = entity_type
        self.contact_email = contact_email
        self.processing_date = datetime.now().strftime("%Y-%m-%d")
        self.custom_processors: Dict[str, Callable] = {}

    def add_custom_processor(
        self, strategy: str, processor: Callable[[str, str, str], str]
    ) -> None:
        """
        Add a custom processing strategy.

        Args:
            strategy: Name of the custom strategy
            processor: Function that takes (content, entity_name, header) and returns processed content
        """
        self.custom_processors[strategy] = processor

    async def process_files(
        self,
        source_dir: str,
        entity_name: str,
        ticket_id: str = "PROC-001",
        output_suffix: str = "processed",
    ) -> ProcessingResult:
        """
        Process all files in source directory with appropriate strategies.

        Args:
            source_dir: Source directory to process
            entity_name: Name of the entity being processed
            ticket_id: Ticket ID for tracking
            output_suffix: Suffix for output directory

        Returns:
            ProcessingResult with details of the processing operation
        """
        try:
            source_path = Path(source_dir)
            output_dir = source_path.parent / f"{entity_name}_{output_suffix}"

            processed_files = []
            strategies_applied = {}

            for file_path in source_path.rglob("*"):
                if file_path.is_file():
                    strategy = self._determine_strategy(file_path)
                    processed_content = self._apply_strategy(
                        file_path, strategy, entity_name, ticket_id
                    )

                    # Write to output directory
                    output_file = output_dir / file_path.relative_to(source_path)
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    output_file.write_text(processed_content)

                    processed_files.append(str(file_path))
                    strategies_applied[str(file_path)] = strategy

            return ProcessingResult(
                entity_name=entity_name,
                source_directory=source_dir,
                output_directory=str(output_dir),
                processed_files=processed_files,
                strategies_applied=strategies_applied,
                success=True,
            )

        except Exception as e:
            return ProcessingResult(
                entity_name=entity_name,
                source_directory=source_dir,
                output_directory="",
                processed_files=[],
                strategies_applied={},
                success=False,
                error_message=str(e),
            )

    def _determine_strategy(self, file_path: Path) -> str:
        """Determine processing strategy based on file type."""
        if file_path.suffix in [".tf"]:
            return ProcessingStrategy.INFRASTRUCTURE.value
        elif file_path.suffix in [".yml", ".yaml"] and "helm" in str(file_path):
            return ProcessingStrategy.INFRASTRUCTURE.value
        elif file_path.suffix in [".yml", ".yaml", ".json"]:
            return ProcessingStrategy.CONFIGURATION.value
        elif file_path.suffix in [".py", ".sh", ".js", ".go", ".java"]:
            return ProcessingStrategy.CODE.value
        else:
            return ProcessingStrategy.DOCUMENTATION.value

    def _apply_strategy(
        self, file_path: Path, strategy: str, entity_name: str, ticket_id: str
    ) -> str:
        """Apply processing strategy to file content."""
        content = file_path.read_text()
        header = self._generate_header(entity_name, ticket_id, strategy)

        if strategy == ProcessingStrategy.INFRASTRUCTURE.value:
            return self._process_infrastructure(content, entity_name, header)
        elif strategy == ProcessingStrategy.CONFIGURATION.value:
            return self._process_configuration(content, entity_name, header)
        elif strategy == ProcessingStrategy.CODE.value:
            return self._process_code(content, entity_name, header)
        elif strategy == ProcessingStrategy.DOCUMENTATION.value:
            return self._process_documentation(content, entity_name, header)
        elif strategy in self.custom_processors:
            return self.custom_processors[strategy](content, entity_name, header)
        else:
            return self._process_documentation(content, entity_name, header)

    def _generate_header(self, entity_name: str, ticket_id: str, strategy: str) -> str:
        """Generate processing header."""
        return f"""# PROCESSED {self.processing_date}: {entity_name}
# Entity Type: {self.entity_type}
# Strategy: {strategy}
# Ticket: {ticket_id}
# Contact: {self.contact_email}
# Original content preserved below (commented)

"""

    def _process_infrastructure(
        self, content: str, entity_name: str, header: str
    ) -> str:
        """Comment out infrastructure resources related to the entity."""
        lines = content.split("\n")
        processed_lines = []
        for line in lines:
            if entity_name.lower() in line.lower():
                processed_lines.append(f"# {line}")
            else:
                processed_lines.append(line)
        return header + "\n".join(processed_lines)

    def _process_configuration(
        self, content: str, entity_name: str, header: str
    ) -> str:
        """Comment out configurations related to the entity."""
        lines = content.split("\n")
        processed_lines = []
        for line in lines:
            if entity_name.lower() in line.lower():
                processed_lines.append(f"# {line}")
            else:
                processed_lines.append(line)
        return header + "\n".join(processed_lines)

    def _process_code(self, content: str, entity_name: str, header: str) -> str:
        """Add processing exceptions to code."""
        exception_code = f"""
def connect_to_{entity_name}():
    raise Exception(
        "{entity_name} {self.entity_type} was processed on {self.processing_date}. "
        "Contact {self.contact_email} for migration guidance."
    )

"""
        return (
            header
            + exception_code
            + "\n# Original code:\n# "
            + content.replace("\n", "\n# ")
        )

    def _process_documentation(
        self, content: str, entity_name: str, header: str
    ) -> str:
        """Add processing notice to documentation."""
        notice = f"⚠️ **{entity_name} {self.entity_type.upper()} PROCESSED** - See header for details\n\n"
        return header + notice + content


# For backward compatibility with database decommissioning
class FileDecommissionProcessor(FileProcessor):
    """
    Database-specific file processor for backward compatibility.

    This class maintains the same interface as the original concrete implementation
    while using the generalized FileProcessor underneath.
    """

    def __init__(self):
        super().__init__(entity_type="database", contact_email="ops-team@company.com")

    async def process_files(
        self, source_dir: str, database_name: str, ticket_id: str = "DB-DECOMM-001"
    ) -> Dict[str, Any]:
        """
        Process files for database decommissioning (backward compatibility).

        Returns:
            Dict with processed_files, strategies_applied, output_directory
        """
        result = await super().process_files(
            source_dir=source_dir,
            entity_name=database_name,
            ticket_id=ticket_id,
            output_suffix="decommissioned",
        )

        # Return in the format expected by the original implementation
        return {
            "database_name": database_name,
            "source_directory": source_dir,
            "output_directory": result.output_directory,
            "processed_files": result.processed_files,
            "strategies_applied": result.strategies_applied,
            "success": result.success,
        }
