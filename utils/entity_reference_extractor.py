"""
Backward Compatibility Wrapper for Entity Reference Extractor.

This module provides backward compatibility for imports while the actual
implementation has moved to concrete.db_decommission.entity_reference_extractor.
"""

import warnings
from concrete.db_decommission.entity_reference_extractor import (
    EntityReferenceExtractor as _EntityReferenceExtractor,
    DatabaseReferenceExtractor as _DatabaseReferenceExtractor,
    MatchedFile as _MatchedFile,
    ExtractionResult as _ExtractionResult,
)


class MatchedFile(_MatchedFile):
    """Backward compatibility wrapper for MatchedFile."""
    pass


class ExtractionResult(_ExtractionResult):
    """Backward compatibility wrapper for ExtractionResult."""
    pass


class EntityReferenceExtractor(_EntityReferenceExtractor):
    """Backward compatibility wrapper for EntityReferenceExtractor."""
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Importing from utils.entity_reference_extractor is deprecated. "
            "Use concrete.db_decommission.entity_reference_extractor instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)


class DatabaseReferenceExtractor(_DatabaseReferenceExtractor):
    """Backward compatibility wrapper for DatabaseReferenceExtractor."""
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Importing from utils.entity_reference_extractor is deprecated. "
            "Use concrete.db_decommission.entity_reference_extractor instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)


# Export the same symbols for backward compatibility
__all__ = [
    'MatchedFile',
    'ExtractionResult', 
    'EntityReferenceExtractor',
    'DatabaseReferenceExtractor',
]