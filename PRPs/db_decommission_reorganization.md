name: "DB Decommission Code Reorganization and Test Consolidation"
description: |

## Purpose
Comprehensive PRP to reorganize scattered database decommission-specific functionality and tests into the concrete/db_decommission/ directory, maintaining backward compatibility while creating clear separation between framework and domain-specific code.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in CLAUDE.md

---

## Goal
Reorganize the GraphMCP framework by moving all database decommission-specific functionality and tests from scattered locations (utils/, workflows/, root-level) into the appropriate locations within `concrete/db_decommission/`, update all import dependencies, maintain backward compatibility, and ensure all tests pass after reorganization.

## Why
- **Code Maintainability**: Create clear separation between general framework and domain-specific functionality
- **Framework Reusability**: Make the framework more modular and extensible for future workflows
- **Test Organization**: Consolidate related tests in appropriate directories for better maintainability
- **Architectural Clarity**: Follow established patterns for concrete workflow implementations
- **Reduced Coupling**: Remove database-specific dependencies from the core framework

## What
Transform the current scattered architecture into a clean, organized structure where:
- Database-specific classes move from `utils/` to `concrete/db_decommission/`
- All scattered test files consolidate into `concrete/db_decommission/tests/`
- Root-level DB files move to appropriate concrete locations
- All import statements update to reflect new file locations
- Backward compatibility is maintained through wrapper classes
- All existing functionality continues to work identically

### Success Criteria
- [ ] All database-specific functionality moved to concrete/db_decommission/
- [ ] All tests properly organized and passing (100% pass rate)
- [ ] No broken imports or dependencies
- [ ] Backward compatibility maintained for all public interfaces
- [ ] Clear separation between framework and domain-specific code
- [ ] Documentation updated to reflect new organization

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://realpython.com/python-refactoring/
  why: Best practices for incremental refactoring and maintaining functionality
  
- url: https://chairnerd.seatgeek.com/refactoring-python-with-libcst/
  why: Safe, automated code modifications for large-scale Python refactoring
  
- url: https://hackernoon.com/why-refactoring-how-to-restructure-python-package-51b89aa91987
  why: Django-influenced package structure patterns and separation of concerns
  
- file: /Users/bprzybysz/nc-src/ovora/manager/src/frameworks/graphmcp/CLAUDE.md
  why: Project guidelines, patterns, and architectural principles to follow
  
- file: /Users/bprzybysz/nc-src/ovora/manager/src/frameworks/graphmcp/utils/__init__.py
  why: Current export patterns and backward compatibility approach
  
- file: /Users/bprzybysz/nc-src/ovora/manager/src/frameworks/graphmcp/concrete/db_decommission/__init__.py
  why: Existing concrete module organization pattern to extend
  
- doc: https://docs.python.org/3/reference/import.html
  section: Import system and module organization best practices
  critical: Proper package initialization and re-export patterns
```

### Current Codebase Structure
```bash
graphmcp/
├── utils/                           # MOVE DB-specific classes FROM here
│   ├── entity_reference_extractor.py  # DatabaseReferenceExtractor class
│   ├── file_processor.py             # FileDecommissionProcessor class
│   ├── source_type_classifier.py     # get_database_search_patterns function
│   └── __init__.py                   # Exports that need backward compatibility
├── workflows/ruliade/               # MOVE DB-specific rules FROM here
│   ├── decomission-refac-ruliade.md  # Database decommissioning rules
│   └── quicksearchpatterns.md       # Database search patterns
├── run_db_workflow.py              # MOVE entire file FROM root
├── test_step_basic.py              # MOVE DB tests FROM root
├── test_integration.py             # MOVE DB tests FROM root  
├── test_comprehensive.py           # MOVE DB tests FROM root
├── tests/                          # MOVE some DB tests FROM here
│   ├── integration/test_workflow_execution.py  # Has DB-specific tests
│   └── e2e/test_real_integration.py           # Has DB-specific tests
└── concrete/db_decommission/       # MOVE everything TO here
    ├── tests/                      # Target for test consolidation
    └── [existing files...]
```

### Desired Codebase Structure
```bash
concrete/db_decommission/
├── __init__.py                     # Updated exports
├── entity_reference_extractor.py  # Moved from utils/
├── file_processor.py              # Moved from utils/
├── source_type_classifier.py      # Moved from utils/
├── cli.py                         # Renamed from run_db_workflow.py
├── rules/                         # NEW directory
│   ├── decomission-refac-ruliade.md
│   └── quicksearchpatterns.md
└── tests/                         # Consolidated tests
    ├── conftest.py
    ├── pytest.ini
    ├── unit/
    │   ├── test_entity_reference_extractor.py  # Moved
    │   ├── test_file_processor.py              # Moved
    │   ├── test_source_type_classifier.py     # NEW
    │   ├── test_cli.py                        # NEW
    │   ├── test_step_basic.py                 # Moved from root
    │   ├── test_integration.py               # Moved from root
    │   └── test_comprehensive.py             # Moved from root
    └── integration/
        └── test_db_specific_workflows.py      # Consolidated DB-specific tests
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: Import system requires careful handling of circular dependencies
# Pattern: Use delayed imports inside functions when moving modules
def get_database_config():
    from .entity_reference_extractor import DatabaseReferenceExtractor
    return DatabaseReferenceExtractor()

# CRITICAL: Backward compatibility requires exact API preservation
# Pattern: Wrapper classes must maintain identical method signatures
class DatabaseReferenceExtractor(EntityReferenceExtractor):
    def __init__(self):
        super().__init__(entity_type="database")
    
    async def extract_references(self, database_name: str, ...):
        # Preserve exact original return format
        result = await super().extract_references(entity_name=database_name, ...)
        return {
            "database_name": database_name,  # Original key name
            "source_file": target_repo_pack_path,
            # ... rest of original interface
        }

# CRITICAL: Test imports must be updated carefully
# Pattern: Update imports but keep test logic identical
from concrete.db_decommission.entity_reference_extractor import DatabaseReferenceExtractor
# NOT: from utils.entity_reference_extractor import DatabaseReferenceExtractor

# CRITICAL: AsyncIO patterns must be preserved
# Pattern: All async context managers and async functions must remain async
async def test_async_functionality():
    async with DatabaseReferenceExtractor() as extractor:
        result = await extractor.extract_references(...)
```

## Implementation Blueprint

### Data Models and Structure
```python
# Maintain existing data models exactly - no changes to interfaces
@dataclass
class FileProcessingResult:
    # Keep identical structure
    success: bool
    file_path: str
    processing_strategy: str
    # ... exact same fields

# Backward compatibility wrappers
class DatabaseReferenceExtractor(EntityReferenceExtractor):
    """Backward compatibility wrapper - maintains exact API"""
    def __init__(self):
        super().__init__(entity_type="database")
```

### List of Tasks to be Completed (in order)

```yaml
Task 1: Create Rules Directory and Move Rule Files
CREATE concrete/db_decommission/rules/:
  - CREATE directory: concrete/db_decommission/rules/
  - MOVE workflows/ruliade/decomission-refac-ruliade.md TO concrete/db_decommission/rules/
  - MOVE workflows/ruliade/quicksearchpatterns.md TO concrete/db_decommission/rules/
  - UPDATE any references to these files in the codebase

Task 2: Move Entity Reference Extractor
MOVE utils/entity_reference_extractor.py:
  - COPY utils/entity_reference_extractor.py TO concrete/db_decommission/entity_reference_extractor.py
  - FIND all imports of DatabaseReferenceExtractor and EntityReferenceExtractor
  - UPDATE imports in concrete/db_decommission/ files to use local import
  - CREATE backward compatibility wrapper in utils/entity_reference_extractor.py

Task 3: Move File Processor
MOVE utils/file_processor.py:
  - COPY utils/file_processor.py TO concrete/db_decommission/file_processor.py
  - FIND all imports of FileDecommissionProcessor and FileProcessor
  - UPDATE imports in concrete/db_decommission/ files to use local import
  - CREATE backward compatibility wrapper in utils/file_processor.py

Task 4: Move Source Type Classifier Functions
EXTRACT from utils/source_type_classifier.py:
  - COPY get_database_search_patterns function TO concrete/db_decommission/source_type_classifier.py
  - COPY any database-specific parts of SourceTypeClassifier
  - UPDATE imports in concrete/db_decommission/ files
  - PRESERVE general SourceTypeClassifier in utils/

Task 5: Move CLI Functionality
MOVE run_db_workflow.py:
  - COPY run_db_workflow.py TO concrete/db_decommission/cli.py
  - UPDATE imports in cli.py to use local concrete module imports
  - CREATE compatibility wrapper at root level run_db_workflow.py
  - UPDATE Makefile targets to use new cli.py location

Task 6: Move Root-Level Test Files
MOVE root test files:
  - MOVE test_step_basic.py TO concrete/db_decommission/tests/unit/test_step_basic.py
  - MOVE test_integration.py TO concrete/db_decommission/tests/unit/test_integration.py  
  - MOVE test_comprehensive.py TO concrete/db_decommission/tests/unit/test_comprehensive.py
  - UPDATE all imports in moved test files

Task 7: Move Scattered Tests from Main Tests Directory
EXTRACT from tests/:
  - EXTRACT DB-specific tests from tests/integration/test_workflow_execution.py
  - EXTRACT DB-specific tests from tests/e2e/test_real_integration.py
  - CREATE concrete/db_decommission/tests/integration/test_db_specific_workflows.py
  - CONSOLIDATE extracted tests into new file

Task 8: Update Backward Compatibility Layer
UPDATE utils/__init__.py:
  - MODIFY exports to import from concrete/db_decommission/ 
  - PRESERVE exact same export names and signatures
  - ADD deprecation warnings for future migration

Task 9: Update concrete/db_decommission/__init__.py
UPDATE concrete module exports:
  - ADD exports for moved functionality
  - MAINTAIN existing exports
  - FOLLOW existing patterns in the file

Task 10: Comprehensive Validation
RUN all validation steps:
  - CHECK all imports resolve correctly
  - RUN complete test suite
  - VALIDATE CLI functionality
  - CHECK Makefile targets work
```

### Per Task Pseudocode

```python
# Task 2: Move Entity Reference Extractor
# 1. Copy file preserving functionality
# 2. Update imports within concrete module
# 3. Create compatibility wrapper

# concrete/db_decommission/entity_reference_extractor.py
class EntityReferenceExtractor:
    """Base implementation - moved from utils/"""
    def __init__(self, entity_type: str = "entity"):
        self.entity_type = entity_type
    
    async def extract_references(self, entity_name: str, ...):
        # Full implementation preserved

class DatabaseReferenceExtractor(EntityReferenceExtractor):
    """Database-specific implementation"""
    def __init__(self):
        super().__init__(entity_type="database")

# utils/entity_reference_extractor.py (compatibility wrapper)
from concrete.db_decommission.entity_reference_extractor import (
    EntityReferenceExtractor as _EntityReferenceExtractor,
    DatabaseReferenceExtractor as _DatabaseReferenceExtractor,
)
import warnings

class EntityReferenceExtractor(_EntityReferenceExtractor):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Importing from utils.entity_reference_extractor is deprecated. "
            "Use concrete.db_decommission.entity_reference_extractor instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)

class DatabaseReferenceExtractor(_DatabaseReferenceExtractor):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "Importing from utils.entity_reference_extractor is deprecated. "
            "Use concrete.db_decommission.entity_reference_extractor instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)
```

### Integration Points
```yaml
IMPORTS:
  - update: All files in concrete/db_decommission/ to use local imports
  - pattern: "from .entity_reference_extractor import DatabaseReferenceExtractor"
  - maintain: utils/__init__.py exports for backward compatibility
  
TESTS:
  - update: All test imports to use new locations
  - pattern: "from concrete.db_decommission.entity_reference_extractor import ..."
  - preserve: All test logic and assertions exactly as-is
  
CLI:
  - maintain: All Makefile targets continue to work
  - update: Internal implementation to use concrete/db_decommission/cli.py
  - preserve: All command-line interfaces and arguments

CONFIGURATION:
  - preserve: All mcp_config.json and other config files unchanged
  - maintain: All workflow execution paths work identically
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
cd /Users/bprzybysz/nc-src/ovora/manager/src/frameworks/graphmcp

# Check syntax and imports
ruff check . --fix                    # Auto-fix style issues
mypy concrete/db_decommission/        # Type checking for moved code
mypy utils/                          # Type checking for compatibility wrappers

# Check for circular imports
python -c "from concrete.db_decommission import *; print('No circular imports')"

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```bash
# Test moved functionality works identically
cd /Users/bprzybysz/nc-src/ovora/manager/src/frameworks/graphmcp

# Test concrete module tests
uv run pytest concrete/db_decommission/tests/unit/ -v

# Test backward compatibility still works
uv run pytest tests/unit/ -v -k "database or decommission"

# Test specific moved components
uv run pytest concrete/db_decommission/tests/unit/test_entity_reference_extractor.py -v
uv run pytest concrete/db_decommission/tests/unit/test_file_processor.py -v

# Expected: All tests pass. If failing, fix imports and logic.
```

### Level 3: Integration Tests
```bash
# Test complete workflow functionality
cd /Users/bprzybysz/nc-src/ovora/manager/src/frameworks/graphmcp

# Test database decommissioning workflow
uv run pytest concrete/db_decommission/tests/integration/ -v

# Test main framework integration still works
uv run pytest tests/integration/ -v

# Test CLI functionality
python concrete/db_decommission/cli.py --help
python run_db_workflow.py --help  # Compatibility wrapper

# Expected: All workflows execute successfully with identical behavior
```

### Level 4: End-to-End Validation
```bash
# Test complete functionality
cd /Users/bprzybysz/nc-src/ovora/manager/src/frameworks/graphmcp

# Run complete test suite
make test-all

# Test specific database functionality
make cmp DB=postgres_air

# Test Makefile targets still work
make demo
make db-decommission-ui

# Expected: All commands execute successfully
```

## Final Validation Checklist
- [ ] All tests pass: `uv run pytest tests/ concrete/ -v`
- [ ] No linting errors: `ruff check . --fix && echo "No errors"`
- [ ] No type errors: `mypy . --ignore-missing-imports`
- [ ] Import compatibility: All old imports still work with deprecation warnings
- [ ] CLI functionality: All make targets and CLI commands work
- [ ] Database workflow: Complete decommissioning workflow executes successfully
- [ ] Backward compatibility: Existing external code continues to work
- [ ] Documentation: README and CLAUDE.md updated with new structure

## Implementation Confidence Score: 9/10

**Rationale for High Confidence:**
- **Comprehensive Research**: Thorough analysis of current structure and dependencies
- **Clear Migration Path**: Well-defined steps with specific file moves and updates
- **Proven Patterns**: Using established backward compatibility and import patterns
- **Incremental Approach**: Step-by-step validation prevents breaking changes
- **Complete Context**: All necessary information included for successful implementation
- **Executable Validation**: Clear, testable criteria for each step

**Potential Risk (why not 10/10):**
- Complex import dependency chains may require iterative refinement of wrapper classes
- Some hidden dependencies may surface during testing that require additional compatibility measures

---

## Anti-Patterns to Avoid
- ❌ Don't change any public API interfaces during the move
- ❌ Don't skip backward compatibility - external code depends on current imports
- ❌ Don't modify test logic during moves - only update imports
- ❌ Don't break CLI commands or Makefile targets
- ❌ Don't ignore deprecation warnings - they're intentional for future migration
- ❌ Don't move files without updating ALL import references
- ❌ Don't assume tests will pass without validation - run them at each step