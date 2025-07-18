"""
Entity Reference Extractor - General Purpose Implementation

Extracts entity references from packed repositories using pattern matching,
preserving directory structure during file extraction. Can be used for any
entity type, not just databases.
"""

import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MatchedFile:
    """File containing entity references."""

    original_path: str
    extracted_path: str
    content: str
    match_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "original_path": self.original_path,
            "extracted_path": self.extracted_path,
            "content": self.content,
            "match_count": self.match_count,
        }


@dataclass
class ExtractionResult:
    """Result of entity reference extraction."""

    entity_name: str
    entity_type: str
    source_file: str
    total_references: int
    total_files: int
    matched_files: List[Dict[str, Any]]
    extraction_directory: str
    success: bool
    duration_seconds: float
    error: Optional[str] = None


class EntityReferenceExtractor:
    """
    General-purpose entity reference extractor for any entity type.

    This extractor can find references to databases, services, applications,
    or any other entity type in packed repositories.
    """

    def __init__(self, entity_type: str = "entity"):
        """
        Initialize the entity reference extractor.

        Args:
            entity_type: Type of entity being extracted (e.g., 'database', 'service', 'application')
        """
        self.entity_type = entity_type
        self.logger = logger

    async def extract_references(
        self,
        entity_name: str,
        target_repo_pack_path: str,
        output_dir: Optional[str] = None,
        patterns: Optional[List[str]] = None,
        case_sensitive: bool = False,
    ) -> ExtractionResult:
        """
        Extract entity references using pattern matching.

        Args:
            entity_name: Name of entity to search for
            target_repo_pack_path: Path to repomix packed XML file
            output_dir: Output directory (defaults to tests/tmp/pattern_match/{entity_name})
            patterns: Custom patterns to search for (defaults to entity_name)
            case_sensitive: Whether to use case-sensitive matching

        Returns:
            ExtractionResult with matched files and statistics
        """
        start_time = time.time()

        try:
            # Default output directory
            if not output_dir:
                output_dir = f"tests/tmp/pattern_match/{entity_name}"

            # Default patterns
            if not patterns:
                patterns = [entity_name]

            # Read and parse packed repository
            files = self._parse_repomix_file(target_repo_pack_path)

            # Find matches using pattern matching
            matched_files = []
            total_references = 0

            for file_info in files:
                matches = self._find_pattern_matches(
                    file_info["content"], patterns, case_sensitive
                )
                if matches:
                    extracted_path = self._extract_file(
                        file_info, output_dir, entity_name
                    )

                    matched_file = MatchedFile(
                        original_path=file_info["path"],
                        extracted_path=extracted_path,
                        content=file_info["content"],
                        match_count=len(matches),
                    )
                    matched_files.append(matched_file)
                    total_references += len(matches)

            return ExtractionResult(
                entity_name=entity_name,
                entity_type=self.entity_type,
                source_file=target_repo_pack_path,
                total_references=total_references,
                total_files=len(matched_files),
                matched_files=[mf.to_dict() for mf in matched_files],
                extraction_directory=output_dir,
                success=True,
                duration_seconds=time.time() - start_time,
            )

        except Exception as e:
            self.logger.error(f"Error extracting references for {entity_name}: {e}")
            return ExtractionResult(
                entity_name=entity_name,
                entity_type=self.entity_type,
                source_file=target_repo_pack_path,
                total_references=0,
                total_files=0,
                matched_files=[],
                extraction_directory=output_dir
                or f"tests/tmp/pattern_match/{entity_name}",
                success=False,
                duration_seconds=time.time() - start_time,
                error=str(e),
            )

    def _parse_repomix_file(self, file_path: str) -> List[Dict[str, str]]:
        """Parse repomix XML file to extract individual files."""
        files = []

        try:
            # Check if file exists first
            if not Path(file_path).exists():
                self.logger.warning(f"Repomix file does not exist: {file_path}")
                return []

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse files using regex pattern: <file path="...">content</file>
            file_pattern = r'<file path="([^"]+)">\s*\n(.*?)\n</file>'
            matches = re.findall(file_pattern, content, re.DOTALL)

            self.logger.info(f"🔍 DEBUG: Found {len(matches)} file matches in XML")

            for file_path, file_content in matches:
                files.append({"path": file_path, "content": file_content.strip()})
                self.logger.info(
                    f"🔍 DEBUG: Parsed file {file_path} with {len(file_content)} chars"
                )

            self.logger.info(f"Parsed {len(files)} files from repomix file")
            return files

        except Exception as e:
            self.logger.error(f"Error parsing repomix file {file_path}: {e}")
            return []

    def _find_pattern_matches(
        self, content: str, patterns: List[str], case_sensitive: bool = False
    ) -> List[str]:
        """Find pattern matches in content using regex."""
        all_matches = []

        for pattern in patterns:
            # Use word boundaries to avoid partial matches
            regex_pattern = rf"\b{re.escape(pattern)}\b"
            flags = 0 if case_sensitive else re.IGNORECASE
            matches = re.findall(regex_pattern, content, flags)
            all_matches.extend(matches)

        self.logger.info(
            f"🔍 DEBUG: Searching for {patterns} in {len(content)} chars, found {len(all_matches)} matches"
        )
        if all_matches:
            self.logger.info(
                f"🔍 DEBUG: Matches found: {all_matches[:5]}"
            )  # Show first 5 matches

        return all_matches

    def _extract_file(self, file_info: Dict, output_dir: str, entity_name: str) -> str:
        """Extract file preserving directory structure."""
        original_path = file_info["path"]
        file_content = file_info["content"]

        # Create full extraction path preserving directory structure
        extraction_path = Path(output_dir) / original_path

        # Create directories if they don't exist
        extraction_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file content
        with open(extraction_path, "w", encoding="utf-8") as f:
            f.write(file_content)

        self.logger.debug(f"Extracted file to: {extraction_path}")
        return str(extraction_path)


# For backward compatibility with database decommissioning
class DatabaseReferenceExtractor(EntityReferenceExtractor):
    """
    Database-specific reference extractor for backward compatibility.

    This class maintains the same interface as the original concrete implementation
    while using the generalized EntityReferenceExtractor underneath.
    """

    def __init__(self):
        super().__init__(entity_type="database")

    async def extract_references(
        self,
        database_name: str,
        target_repo_pack_path: str,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract database references (backward compatibility).

        Returns:
            Dict with matched_files, total_references, extraction_directory
        """
        result = await super().extract_references(
            entity_name=database_name,
            target_repo_pack_path=target_repo_pack_path,
            output_dir=output_dir,
        )

        # Return in the format expected by the original implementation
        return {
            "database_name": database_name,
            "source_file": target_repo_pack_path,
            "total_references": result.total_references,
            "total_files": result.total_files,
            "matched_files": result.matched_files,
            "files": [
                {"path": mf["original_path"], "matches": mf["match_count"]}
                for mf in result.matched_files
            ],
            "extraction_directory": result.extraction_directory,
            "success": result.success,
            "duration_seconds": result.duration_seconds,
        }


# Additional utility functions for common use cases
def extract_service_references(
    service_name: str, repo_pack_path: str, output_dir: Optional[str] = None
) -> ExtractionResult:
    """Extract service references from a packed repository."""
    extractor = EntityReferenceExtractor(entity_type="service")
    return extractor.extract_references(
        entity_name=service_name,
        target_repo_pack_path=repo_pack_path,
        output_dir=output_dir,
    )


def extract_application_references(
    app_name: str, repo_pack_path: str, output_dir: Optional[str] = None
) -> ExtractionResult:
    """Extract application references from a packed repository."""
    extractor = EntityReferenceExtractor(entity_type="application")
    return extractor.extract_references(
        entity_name=app_name,
        target_repo_pack_path=repo_pack_path,
        output_dir=output_dir,
    )
