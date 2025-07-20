"""
Database-Specific Source Type Classification Functions.

This module contains database-specific functions extracted from the general
utils.source_type_classifier module to maintain clear separation between
framework and domain-specific functionality.
"""

from typing import List
from utils.source_type_classifier import SourceType


def get_database_search_patterns(
    source_type: SourceType, database_name: str
) -> List[str]:
    """Get database-specific search patterns for a source type."""
    base_patterns = [
        database_name,
        database_name.upper(),
        database_name.lower(),
        database_name.replace("_", "-"),
        database_name.replace("-", "_"),
    ]

    if source_type == SourceType.INFRASTRUCTURE:
        return [
            f"name.*{database_name}",
            f"database.*{database_name}",
            f"{database_name}.*database",
            f"resource.*{database_name}",
        ] + base_patterns

    elif source_type == SourceType.CONFIG:
        return [
            f"database.*{database_name}",
            f"db.*{database_name}",
            f"{database_name}.*url",
            f"{database_name}.*connection",
        ] + base_patterns

    elif source_type == SourceType.SQL:
        return [
            f"CREATE.*{database_name}",
            f"USE.*{database_name}",
            f"DATABASE.*{database_name}",
            f"SCHEMA.*{database_name}",
        ] + base_patterns

    elif source_type == SourceType.PYTHON:
        return [
            f"database.*{database_name}",
            f"db.*{database_name}",
            f"{database_name}.*model",
            f"class.*{database_name}",
        ] + base_patterns

    elif source_type == SourceType.SHELL:
        return [
            f"DB_.*{database_name}",
            f"{database_name.upper()}_DB",
            f"database.*{database_name}",
            f"{database_name}.*database",
            f"psql.*{database_name}",
            f"mysql.*{database_name}",
        ] + base_patterns

    else:
        return base_patterns


# Export for use within the concrete module
__all__ = ['get_database_search_patterns']