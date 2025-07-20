"""
Backward Compatibility Wrapper for File Processor.

This module provides backward compatibility for imports while the actual
implementation has moved to concrete.db_decommission.file_processor.
"""

import warnings
from concrete.db_decommission.file_processor import (
    FileProcessor as _FileProcessor,
    FileDecommissionProcessor as _FileDecommissionProcessor,
    ProcessingStrategy as _ProcessingStrategy,
    ProcessingResult as _ProcessingResult,
)


# Re-export the enum directly (cannot inherit from Enum)
ProcessingStrategy = _ProcessingStrategy


class ProcessingResult(_ProcessingResult):
    """Backward compatibility wrapper for ProcessingResult."""
    pass


class FileProcessor(_FileProcessor):
    """Backward compatibility wrapper for FileProcessor."""
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Importing from utils.file_processor is deprecated. "
            "Use concrete.db_decommission.file_processor instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)


class FileDecommissionProcessor(_FileDecommissionProcessor):
    """Backward compatibility wrapper for FileDecommissionProcessor."""
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Importing from utils.file_processor is deprecated. "
            "Use concrete.db_decommission.file_processor instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)


# Export the same symbols for backward compatibility
__all__ = [
    'ProcessingStrategy',
    'ProcessingResult',
    'FileProcessor',
    'FileDecommissionProcessor',
]