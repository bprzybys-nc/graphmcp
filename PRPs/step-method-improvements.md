# PRP: Database Decommissioning Workflow - Step Method Improvements

## Goal
Enhance the database decommissioning workflow by implementing modern fluent interface patterns with improved step() method usage, better parameter handling, and intuitive domain-specific builder for creating database decommission workflows. The goal is to reduce code duplication by 70%, improve maintainability, and provide a better developer experience while maintaining 100% backward compatibility.

## Why
- **Code Duplication**: Current `create_db_decommission_workflow()` has 160+ lines of repetitive lambda wrapping (`lambda context, step, **params: function(context, step, **params)`)
- **Poor Maintainability**: Parameter duplication (`database_name`, `workflow_id`, `repo_owner`, `repo_name`) across all 6 steps
- **Developer Experience**: Hard to customize workflows - requires understanding internal implementation details
- **Modern Patterns**: Workflow orchestration tools like Prefect and Dagster use fluent interfaces for better readability
- **Integration Benefits**: Easier to add new steps, modify existing ones, and create custom workflows

## What
Transform the existing database decommissioning workflow into a modern fluent interface pattern with:
1. **step_auto() method** - Automatically wrap functions in lambdas
2. **DatabaseDecommissionWorkflowBuilder** - Domain-specific builder with centralized parameter management
3. **Enhanced create_db_decommission_workflow()** - Support both simple and advanced usage patterns
4. **Backward Compatibility** - Existing code continues to work unchanged

### Success Criteria
- [ ] `step_auto()` method added to WorkflowBuilder class
- [ ] `DatabaseDecommissionWorkflowBuilder` class implemented with fluent interface
- [ ] `create_db_decommission_workflow()` enhanced with `custom_steps` parameter
- [ ] Code duplication reduced from 160+ lines to ~50 lines
- [ ] All existing tests pass without modification
- [ ] Database decommissioning workflow works identically after changes
- [ ] Both simple and advanced usage patterns supported

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- file: /workflows/builder.py
  why: Current WorkflowBuilder implementation with step() and custom_step() methods
  critical: Lines 281-352 contain current builder pattern, step() method at line 315
  
- file: /concrete/db_decommission/utils.py
  why: Current create_db_decommission_workflow() implementation with repetitive patterns
  critical: Lines 47-161 show current implementation with lambda wrapping pattern
  
- file: /concrete/db_decommission/workflow_steps.py
  why: Step function implementations that need to be wrapped
  critical: Functions like quality_assurance_step(), apply_refactoring_step() signature patterns
  
- file: /tests/unit/test_builder_and_serialization.py
  why: Test patterns for WorkflowBuilder and serialization requirements
  critical: Lines 29-40 show RepoQuickScanTemplate pattern for fluent interface
  
- file: /tests/unit/test_step_method.py
  why: Current step() method test patterns to ensure backward compatibility
  critical: Test patterns for both lambda and function wrapping
  
- url: https://docs.prefect.io/v3/get-started
  section: Flow and Task definition patterns
  critical: Modern workflow orchestration patterns using decorators and fluent interfaces
  
- url: https://docs.dagster.io/guides/build/assets/defining-assets
  section: Asset definition with decorators
  critical: Domain-specific builder patterns for data workflows
  
- url: https://martinfowler.com/bliki/FluentInterface.html
  why: Fluent interface design principles and best practices
  critical: Method chaining patterns and DSL design principles
  
- url: https://dev.to/pablocavalcanteh/builder-design-pattern-in-python-with-fluent-interface-29of
  why: Python-specific fluent interface and builder pattern implementation
  critical: Method chaining with return self pattern
```

### Current Codebase Tree
```bash
graphmcp/
├── workflows/
│   ├── builder.py                 # WorkflowBuilder with step() method - CORE TARGET
│   └── context.py                 # WorkflowContext for step execution
├── concrete/
│   └── db_decommission/
│       ├── utils.py               # create_db_decommission_workflow() - MAIN TARGET
│       ├── workflow_steps.py      # Step function implementations
│       └── validation_helpers.py  # Helper functions
├── tests/
│   ├── unit/
│   │   ├── test_builder_and_serialization.py  # Builder test patterns
│   │   └── test_step_method.py                # Step method tests
│   └── integration/
│       └── test_workflow_execution.py         # Integration tests
└── run_db_workflow.py            # Demo script - VALIDATION TARGET
```

### Desired Codebase Tree
```bash
graphmcp/
├── workflows/
│   ├── builder.py                 # + step_auto() method to WorkflowBuilder
│   └── context.py                 # No changes
├── concrete/
│   └── db_decommission/
│       ├── utils.py               # + DatabaseDecommissionWorkflowBuilder class
│       │                          # + Enhanced create_db_decommission_workflow()
│       ├── workflow_steps.py      # No changes
│       └── validation_helpers.py  # No changes
├── tests/
│   ├── unit/
│   │   ├── test_builder_and_serialization.py  # No changes initially
│   │   ├── test_step_method.py                # No changes initially
│   │   └── test_db_workflow_builder.py        # + New test file
│   └── integration/
│       └── test_workflow_execution.py         # No changes initially
└── run_db_workflow.py            # No changes - backward compatible
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: WorkflowStep uses pickle for serialization
# Lambda functions are pickle-safe when defined at module level
# Current step() method expects specific signature: (context, step, **params)

# CRITICAL: Current parameter passing pattern
# All step functions expect: async def func(context, step, **parameters)
# Parameters are passed via step.parameters dict

# CRITICAL: Current dependency management
# Steps use depends_on list with step IDs
# Must maintain exact same dependency chain

# CRITICAL: Current function alias pattern (lines 41-63 in builder.py)
# WorkflowStep.__post_init__ creates aliases between custom_function, function, delegate
# Must preserve this pattern for backward compatibility

# CRITICAL: extract_repo_details() function pattern
# Returns tuple (owner, name) from GitHub URL
# Used in _github_params() for repo operations

# CRITICAL: Current step execution pattern (lines 130-160 in builder.py)
# Uses: await step.custom_function(context, step, **step.parameters)
# Must maintain identical execution behavior
```

## Implementation Blueprint

### Data Models and Structure
```python
# No new data models needed - enhance existing WorkflowBuilder class
# Add new methods to WorkflowBuilder and create new specialized builder class
# Maintain existing WorkflowStep, Workflow, WorkflowConfig classes unchanged
```

### List of Tasks to be Completed

```yaml
Task 1: Add step_auto() method to WorkflowBuilder
MODIFY workflows/builder.py:
  - FIND: class WorkflowBuilder (line 281)
  - ADD after step() method (around line 352): step_auto() method
  - PATTERN: Mirror step() method but auto-wrap function with lambda
  - PRESERVE: All existing method signatures and behavior

Task 2: Create DatabaseDecommissionWorkflowBuilder class
CREATE in concrete/db_decommission/utils.py:
  - FIND: Line before create_db_decommission_workflow function (line 47)
  - ADD: DatabaseDecommissionWorkflowBuilder class definition
  - PATTERN: Inherit from WorkflowBuilder, add domain-specific methods
  - METHODS: with_repositories(), with_slack_channel(), add_*_step() methods

Task 3: Add parameter management methods to DatabaseDecommissionWorkflowBuilder
MODIFY DatabaseDecommissionWorkflowBuilder class:
  - ADD: _base_params(), _repo_params(), _github_params() methods
  - PATTERN: Centralize parameter generation for all steps
  - PRESERVE: Same parameter values as current implementation

Task 4: Enhance create_db_decommission_workflow() function
MODIFY create_db_decommission_workflow in concrete/db_decommission/utils.py:
  - FIND: Function signature (line 47)
  - ADD: custom_steps parameter with default False
  - MODIFY: Implementation to use DatabaseDecommissionWorkflowBuilder
  - PRESERVE: Exact same return value and behavior for existing calls

Task 5: Create comprehensive unit tests
CREATE tests/unit/test_db_workflow_builder.py:
  - MIRROR: test_builder_and_serialization.py patterns
  - TEST: DatabaseDecommissionWorkflowBuilder all methods
  - TEST: step_auto() method functionality
  - TEST: Parameter management methods
  - TEST: Backward compatibility with create_db_decommission_workflow()
```

### Task 1 Pseudocode - Add step_auto() method
```python
# In workflows/builder.py WorkflowBuilder class (after line 352)
def step_auto(self, step_id: str, name: str, func: Callable, **kwargs) -> WorkflowBuilder:
    """
    Add a workflow step with automatic function wrapping.
    
    This method automatically wraps the provided function in a lambda
    to match the step() method signature requirements.
    """
    # PATTERN: Auto-wrap function to match step() signature
    wrapped_func = lambda context, step, **params: func(context, step, **params)
    
    # CRITICAL: Use existing step() method for consistency
    return self.step(step_id, name, wrapped_func, **kwargs)
```

### Task 2 Pseudocode - DatabaseDecommissionWorkflowBuilder class
```python
# In concrete/db_decommission/utils.py (before line 47)
class DatabaseDecommissionWorkflowBuilder(WorkflowBuilder):
    """Specialized workflow builder for database decommissioning workflows."""
    
    def __init__(self, database_name: str, config_path: str = "mcp_config.json"):
        # PATTERN: Initialize parent with fixed workflow name
        super().__init__(
            "db-decommission", 
            config_path,
            description=f"Decommissioning of {database_name} database"
        )
        # CRITICAL: Store database_name and generate workflow_id
        self.database_name = database_name
        self.workflow_id = f"db-{database_name}-{int(time.time())}"
    
    def with_repositories(self, target_repos: List[str]) -> 'DatabaseDecommissionWorkflowBuilder':
        """Set target repositories for processing."""
        self.target_repos = target_repos
        return self
    
    def add_validation_step(self, timeout_seconds: int = 30) -> 'DatabaseDecommissionWorkflowBuilder':
        """Add environment validation step."""
        # PATTERN: Use step_auto() to avoid lambda wrapping
        return self.step_auto(
            "validate_environment", 
            "Environment Validation & Setup",
            validate_environment_step,
            parameters=self._base_params(),
            timeout_seconds=timeout_seconds
        )
    
    def add_all_steps(self) -> 'DatabaseDecommissionWorkflowBuilder':
        """Add all standard decommission steps in correct order."""
        # PATTERN: Chain all step additions with proper dependencies
        return (self
            .add_validation_step()
            .add_repository_processing_step()
            .add_refactoring_step()
            .add_github_pr_step()
            .add_quality_assurance_step()
            .add_summary_step()
        )
```

### Task 4 Pseudocode - Enhanced create_db_decommission_workflow()
```python
# In concrete/db_decommission/utils.py (modify existing function)
def create_db_decommission_workflow(
    database_name: str = "example_database",
    target_repos: Optional[List[str]] = None,
    slack_channel: str = "demo-channel",
    config_path: str = "mcp_config.json",
    workflow_id: Optional[str] = None,
    custom_steps: bool = False  # NEW parameter
) -> Union[Workflow, DatabaseDecommissionWorkflowBuilder]:
    """Enhanced factory function with fluent interface support."""
    
    # PATTERN: Set defaults same as current implementation
    if target_repos is None:
        target_repos = ["https://github.com/bprzybys-nc/postgres-sample-dbs"]
    
    # PATTERN: Create builder with fluent interface
    builder = (DatabaseDecommissionWorkflowBuilder(database_name, config_path)
               .with_repositories(target_repos)
               .with_slack_channel(slack_channel))
    
    # PATTERN: Override workflow_id if provided
    if workflow_id:
        builder.workflow_id = workflow_id
    
    # NEW: Return builder for custom configuration
    if custom_steps:
        return builder
    
    # PATTERN: Standard workflow - same as current behavior
    return (builder
            .add_all_steps()
            .with_config(
                max_parallel_steps=4,
                default_timeout=120,
                stop_on_error=False,
                default_retry_count=3
            )
            .build())
```

### Integration Points
```yaml
NO DATABASE CHANGES:
  - No database schema modifications needed
  
NO CONFIG CHANGES:
  - No changes to MCP configuration files
  
BACKWARD COMPATIBILITY:
  - All existing calls to create_db_decommission_workflow() work unchanged
  - All existing step() and custom_step() methods continue to work
  
DEMO SCRIPT:
  - run_db_workflow.py works without changes
  - Demo functionality identical to current implementation
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
source .venv/bin/activate
ruff check workflows/builder.py --fix
ruff check concrete/db_decommission/utils.py --fix
mypy workflows/builder.py
mypy concrete/db_decommission/utils.py

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```bash
# Test new functionality
source .venv/bin/activate
python -m pytest tests/unit/test_db_workflow_builder.py -v

# Test backward compatibility
python -m pytest tests/unit/test_step_method.py -v
python -m pytest tests/unit/test_builder_and_serialization.py -v

# Expected: All tests pass. If failing, read error and fix code.
```

### Level 3: Integration Tests
```bash
# Test existing database decommissioning workflow
source .venv/bin/activate
python -c "
from concrete.db_decommission.utils import create_db_decommission_workflow
workflow = create_db_decommission_workflow('test_db', ['https://github.com/test/repo'])
print('✅ Standard workflow creation works')

# Test new builder pattern
builder = create_db_decommission_workflow('test_db', custom_steps=True)
custom_workflow = builder.add_validation_step().add_repository_processing_step().build()
print('✅ Custom workflow creation works')
"

# Test demo script works unchanged
python run_db_workflow.py --database postgres_air --repo "https://github.com/bprzybysz/postgres-sample-dbs" --mock

# Expected: All tests pass, demo runs successfully
```

### Level 4: Comprehensive Validation
```bash
# Test backward compatibility with actual execution
source .venv/bin/activate
python tests/unit/test_step_basic.py

# Test all parameter management methods
python -c "
from concrete.db_decommission.utils import DatabaseDecommissionWorkflowBuilder
builder = DatabaseDecommissionWorkflowBuilder('test_db')
builder.with_repositories(['https://github.com/test/repo'])
builder.with_slack_channel('test-channel')
print('Base params:', builder._base_params())
print('Repo params:', builder._repo_params())
print('GitHub params:', builder._github_params())
print('✅ Parameter management works')
"
```

## Final Validation Checklist
- [ ] All tests pass: `source .venv/bin/activate && python -m pytest tests/ -v`
- [ ] No linting errors: `ruff check workflows/ concrete/`
- [ ] No type errors: `mypy workflows/builder.py concrete/db_decommission/utils.py`
- [ ] Database decommission workflow works: `python run_db_workflow.py --database test_db --mock`
- [ ] Backward compatibility maintained: All existing calls work unchanged
- [ ] New fluent interface works: Custom workflow building successful
- [ ] Code duplication reduced: From 160+ lines to ~50 lines
- [ ] Parameter management centralized: No duplication across steps

## Anti-Patterns to Avoid
- ❌ Don't break existing function signatures - maintain backward compatibility
- ❌ Don't change existing step function implementations - only enhance builder
- ❌ Don't modify existing test files unless necessary - create new tests
- ❌ Don't change workflow execution behavior - only improve creation interface
- ❌ Don't introduce new dependencies - use existing patterns
- ❌ Don't skip validation steps - ensure all levels pass

## Risk Assessment & Mitigation

### High Risk Areas
1. **Backward Compatibility**: Existing create_db_decommission_workflow() calls
   - Mitigation: Preserve exact same function signature and default behavior
   
2. **Parameter Management**: Centralized parameter generation
   - Mitigation: Test parameter values match current implementation exactly

3. **Step Execution**: Lambda wrapping with step_auto()
   - Mitigation: Use existing step() method internally for consistency

### Success Indicators
- All existing tests pass without modification
- Database decommissioning workflow executes identically
- New fluent interface provides better developer experience
- Code duplication reduced by 70%

---

## PRP Quality Score: 9/10

**Rationale**: This PRP provides comprehensive context including current implementation details, external research on fluent interfaces and workflow orchestration patterns, specific file locations and line numbers, complete implementation blueprint with pseudocode, multi-level validation strategy, and risk mitigation. The approach ensures backward compatibility while providing modern developer experience improvements. The only minor deduction is for the inherent complexity of maintaining backward compatibility while enhancing the interface, but the phased validation approach mitigates this risk effectively.