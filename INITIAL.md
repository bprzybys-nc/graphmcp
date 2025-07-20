# Feature Request

## Basic Information
- **Feature Name**: DB Decommission Code Reorganization and Test Consolidation
- **Requested By**: Development Team
- **Date**: 2025-01-20
- **Priority**: High
- **Estimated Complexity**: Medium

## Feature Description

### What
Reorganize the GraphMCP framework by moving all database decommission-specific functionality and tests to the appropriate location within `concrete/db_decommission/`, fix all import dependencies, and ensure all tests pass after the reorganization.

### Why
Currently, database decommission-specific code is scattered throughout the framework in utils/, workflows/, and root-level files, making the framework less maintainable and harder to understand. This reorganization will:
- Create clear separation between general framework and domain-specific functionality
- Improve code maintainability and reusability
- Make the framework more modular and extensible for future workflows
- Consolidate related tests in appropriate directories
- Follow established architectural patterns for concrete workflow implementations

### When
- **Target Completion**: Immediate (high priority refactoring task)
- **Dependencies**: None (internal refactoring)

### Who
- **Primary Users**: GraphMCP framework developers
- **Secondary Users**: Future workflow implementers
- **Stakeholders**: All developers working with the GraphMCP framework

## Functional Requirements

### Core Functionality
- Move database-specific classes and functions from utils/ to concrete/db_decommission/
- Relocate scattered test files to appropriate test directories
- Update all import statements to reflect new file locations
- Ensure backward compatibility where needed
- Validate that all functionality works after reorganization

### User Stories
- As a framework developer, I want database-specific code isolated so that I can understand what's framework vs domain-specific
- As a workflow implementer, I want clear patterns to follow so that I can create new workflows efficiently
- As a maintainer, I want tests organized by domain so that I can easily test specific functionality
- As a developer, I want all tests to pass so that I can be confident the refactoring didn't break anything

### Success Criteria
- All database-specific functionality moved to concrete/db_decommission/
- All tests properly organized and passing
- No broken imports or dependencies
- Clear separation between framework and domain-specific code
- Documentation updated to reflect new organization

## Technical Requirements

### Architecture Integration
- **Framework Component**: Affects utils/, workflows/, tests/, and concrete/db_decommission/
- **MCP Clients**: No changes to MCP client interfaces
- **Workflow Integration**: Database workflows continue to function normally
- **Dependencies**: Update internal imports, no external dependency changes

### Performance Requirements
- **Response Time**: No performance impact expected
- **Throughput**: No throughput impact expected
- **Scalability**: No scaling impact expected
- **Resource Usage**: No resource usage changes expected

## Acceptance Criteria

### Functional Criteria
- [ ] All database-specific classes moved from utils/ to concrete/db_decommission/
- [ ] All scattered test files moved to appropriate concrete/db_decommission/tests/ directories
- [ ] All root-level DB-specific files moved to concrete/db_decommission/
- [ ] All imports updated to reflect new file locations
- [ ] All tests pass after reorganization
- [ ] Backward compatibility maintained for critical interfaces

### Technical Criteria
- [ ] No broken imports or missing dependencies
- [ ] Test organization follows established patterns
- [ ] Code organization follows framework patterns
- [ ] All functionality preserved and working
- [ ] Performance not negatively impacted

### Quality Criteria
- [ ] Code quality maintained or improved
- [ ] Test coverage maintained
- [ ] Documentation updated appropriately
- [ ] No regression in functionality
- [ ] Clear separation between framework and domain code

## Specific Files to Move

Based on analysis, these files need to be moved:

### High Priority Moves:
- `utils/entity_reference_extractor.py` → `concrete/db_decommission/database_reference_extractor.py` (DatabaseReferenceExtractor class)
- `utils/file_processor.py` → `concrete/db_decommission/file_decommission_processor.py` (FileDecommissionProcessor class)
- `utils/source_type_classifier.py` → `concrete/db_decommission/pattern_helpers.py` (get_database_search_patterns function)
- `run_db_workflow.py` → `concrete/db_decommission/cli.py`

### Test Files to Move:
- Root-level test files: `test_step_basic.py`, `test_integration.py`, `test_comprehensive.py` → `concrete/db_decommission/tests/`
- DB-specific tests from `tests/integration/` and `tests/e2e/` → `concrete/db_decommission/tests/`

### Rules and Configuration:
- `workflows/ruliade/decomission-refac-ruliade.md` → `concrete/db_decommission/rules/`
- `workflows/ruliade/quicksearchpatterns.md` → `concrete/db_decommission/rules/`

### Framework Code to Generalize:
- `parameter_service.py` - `get_database_config()` method should be generalized for any entity type
- Test files with hardcoded DB imports should use generic patterns

## Risk Assessment

### Technical Risks
- Import dependency chains may be complex to untangle
- Tests may have hidden dependencies on file locations
- Backward compatibility may be accidentally broken

### Mitigation Strategies
- Test thoroughly after each major move
- Use automated testing to catch regressions quickly
- Make changes incrementally and test each step
- Preserve public interfaces and add deprecated warnings if needed