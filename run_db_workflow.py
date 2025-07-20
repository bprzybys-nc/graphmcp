#!/usr/bin/env python3
"""
Backward Compatibility Wrapper for Database Decommissioning CLI.

This script provides backward compatibility by delegating to the new location
at concrete.db_decommission.cli.py
"""

import sys
import warnings
import asyncio

# Add current directory to path
sys.path.insert(0, ".")

warnings.warn(
    "run_db_workflow.py at the root level is deprecated. "
    "Use 'python -m concrete.db_decommission.cli' or the new CLI location instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import and delegate to the new CLI
from concrete.db_decommission.cli import main

if __name__ == "__main__":
    asyncio.run(main())