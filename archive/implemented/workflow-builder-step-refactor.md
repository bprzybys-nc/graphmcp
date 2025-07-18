# PRP: Workflow Builder Method Refactor - `custom_step` → `step`

## Goal
Refactor the GraphMCP `WorkflowBuilder.custom_step()` method to `WorkflowBuilder.step()` with lambda delegate support while maintaining backward compatibility and ensuring zero disruption to existing database decommissioning workflows.

## Why
- **API Consistency**: Rename `custom_step` to `step` to make it the primary step definition method
- **Modern Patterns**: Support lambda delegates for inline function definitions
- **Semantic Clarity**: "step" better represents the core workflow building concept than "custom_step"
- **Developer Experience**: Align with modern Python workflow patterns (Prefect, Dagster style)
- **Critical Constraint**: Must not break existing production database decommissioning workflow

## What
Transform the current `custom_step(step_id, name, func, ...)` method to `step(step_id, name, delegate, ...)` with lambda support, following a phased migration approach to avoid disruption.

### Success Criteria
- [ ] New `step()` method implemented with lambda delegate support
- [ ] All existing `custom_step()` calls continue to work (backward compatibility)
- [ ] Database decommissioning workflow functions identically after refactor
- [ ] No breaking changes to any of the 13 files using `custom_step`
- [ ] Migration path documented for future adoption
- [ ] All tests pass without modification

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- file: /workflows/builder.py
  why: Core WorkflowBuilder implementation, custom_step method definition (lines 284-301)
  critical: Function storage mechanism uses both custom_function and function fields

- file: /concrete/db_decommission/utils.py  
  why: Primary production usage with 6 custom_step calls - CANNOT BREAK
  critical: validate_environment_step, analyze_repository_step, etc. must work identically

- file: /tests/unit/test_builder_and_serialization.py
  why: Core test patterns with 5 custom_step calls and serialization tests
  critical: Pickle serialization must work - lambdas are NOT pickle-safe

- file: /tests/integration/test_workflow_execution.py
  why: Integration test patterns with 2 custom_step calls  
  critical: merge_analysis_results function delegation pattern

- url: https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled
  why: Lambda serialization constraints - cannot pickle lambda functions
  critical: Backward compatibility requires maintaining pickle-safe patterns

- url: https://www.prefect.io/
  section: Task and Flow definitions
  critical: Modern workflow pattern inspiration for lambda delegates

- docfile: /PRPs/ai_docs/workflow_patterns.md
  why: Internal workflow building patterns and conventions
```

### Current Codebase Tree
```bash
graphmcp/
├── workflows/
│   ├── builder.py                 # WorkflowBuilder.custom_step() - CORE TARGET
│   └── context.py                 # WorkflowContext for step execution
├── concrete/
│   └── db_decommission/
│       └── utils.py               # 6 custom_step calls - PRODUCTION CRITICAL
├── tests/
│   ├── unit/
│   │   └── test_builder_and_serialization.py  # 5 custom_step calls
│   ├── integration/
│   │   └── test_workflow_execution.py          # 2 custom_step calls
│   └── e2e/
│       ├── test_minimal_integration.py         # 1 custom_step call
│       └── test_real_integration.py            # 2 custom_step calls
└── demo.py                        # Production workflow demo
```

### Desired Codebase Tree (Minimal Changes)
```bash
graphmcp/
├── workflows/
│   ├── builder.py                 # + step() method, custom_step() preserved
│   └── context.py                 # No changes needed
├── concrete/
│   └── db_decommission/
│       └── utils.py               # No changes (backward compatible)
├── tests/
│   ├── unit/
│   │   ├── test_builder_and_serialization.py  # No changes initially
│   │   └── test_step_method.py                # + New test file
│   └── integration/
│       └── test_workflow_execution.py          # No changes initially
└── demo.py                        # No changes initially
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: Lambda functions are NOT pickle-safe
# Current WorkflowStep uses pickle for serialization
# Lambda delegates cannot be serialized/deserialized
lambda x: x + 1  # This CANNOT be pickled

# CRITICAL: Current function signature expects callable
# All existing calls use this pattern:
def some_function(context, step, **parameters):
    # implementation
    pass

# CRITICAL: WorkflowStep.__post_init__ creates aliases
# Both custom_function and function fields exist for backward compatibility
# Line 41-51 in builder.py shows this pattern

# CRITICAL: Step execution expects specific signature
# Line 132-142 shows: await step.custom_function(context, step, **step.parameters)
# New delegate pattern must maintain this signature

# CRITICAL: 13 files use custom_step - breaking change would be massive
# Files: builder.py, utils.py, 5 test files, 2 e2e tests, etc.
```

## Implementation Blueprint

### Data Models and Structure
```python
# PRESERVE existing WorkflowStep structure
@dataclass
class WorkflowStep:
    custom_function: Optional[Callable] = None  # Keep for backward compatibility
    function: Optional[Callable] = field(default=None, repr=False)  # Keep alias
    delegate: Optional[Callable] = field(default=None, repr=False)  # NEW: for step() method
    
    def __post_init__(self):
        # PRESERVE existing compatibility logic
        if self.custom_function and not self.function:
            self.function = self.custom_function
        elif self.function and not self.custom_function:
            self.custom_function = self.function
        
        # NEW: Handle delegate field
        if self.delegate and not self.custom_function:
            self.custom_function = self.delegate
            self.function = self.delegate
```

### List of Tasks (Phased Migration Approach)

```yaml
Task 1: Create Git Branch
CREATE new branch: feature/workflow-builder-step-method
  - REASON: Requirement from INITIAL.md - separate branch before refactor
  - COMMAND: git checkout -b feature/workflow-builder-step-method

Task 2: Add step() Method to WorkflowBuilder
MODIFY workflows/builder.py:
  - FIND: def custom_step(self, step_id: str, name: str, func: Callable, ...)
  - ADD after custom_step method: def step(self, step_id: str, name: str, delegate: Callable, ...)
  - PRESERVE: custom_step method completely unchanged
  - PATTERN: Mirror custom_step implementation exactly, just parameter names

Task 3: Update WorkflowStep Data Structure  
MODIFY workflows/builder.py WorkflowStep class:
  - FIND: custom_function: Optional[Callable] = None
  - ADD: delegate: Optional[Callable] = field(default=None, repr=False)
  - MODIFY: __post_init__ method to handle delegate field
  - PRESERVE: All existing custom_function/function logic

Task 4: Create Comprehensive Unit Tests
CREATE tests/unit/test_step_method.py:
  - MIRROR: test_builder_and_serialization.py patterns
  - TEST: step() method with regular functions (not lambdas initially)
  - TEST: Backward compatibility - both custom_step and step work
  - TEST: Serialization safety - ensure no lambda serialization issues

Task 5: Test Database Decommissioning Workflow
RUN integration tests:
  - COMMAND: uv run pytest tests/integration/test_workflow_execution.py -v
  - VERIFY: All existing custom_step calls work unchanged
  - VERIFY: Database decommissioning workflow in concrete/db_decommission/utils.py works

Task 6: Create Migration Documentation
CREATE PRPs/ai_docs/step_method_migration.md:
  - DOCUMENT: How to migrate from custom_step to step
  - DOCUMENT: Lambda delegate patterns and limitations
  - DOCUMENT: Serialization considerations
  - PROVIDE: Migration examples for each usage pattern

Task 7: Optional Future Migration (Not Required)
IF all tests pass and no disruption:
  - OPTIONALLY update 1-2 non-critical test files to use step()
  - PRESERVE: concrete/db_decommission/utils.py unchanged
  - PRESERVE: All production code unchanged
```

### Task 2 Pseudocode - Add step() Method
```python
# In workflows/builder.py WorkflowBuilder class
def step(self, step_id: str, name: str, delegate: Callable, 
         description: str = "", parameters: Dict = None, 
         depends_on: List[str] = None, timeout_seconds: int = None, 
         retry_count: int = None, **kwargs) -> WorkflowBuilder:
    """
    Add a workflow step with a delegate function.
    
    PATTERN: Identical to custom_step but with delegate parameter
    CRITICAL: Maintains exact same behavior for backward compatibility
    """
    # MIRROR: Exact same validation logic as custom_step
    if parameters is None:
        parameters = {}
    
    # PATTERN: Same WorkflowStep creation as custom_step
    step = WorkflowStep(
        step_id=step_id,
        name=name,
        step_type=StepType.CUSTOM,
        description=description,
        parameters=parameters,
        depends_on=depends_on or [],
        timeout_seconds=timeout_seconds,
        retry_count=retry_count,
        delegate=delegate,  # NEW: Store in delegate field
        **kwargs
    )
    
    # PRESERVE: Same step addition logic
    self.steps.append(step)
    return self
```

### Task 3 Pseudocode - Update WorkflowStep
```python
# In workflows/builder.py WorkflowStep class
def __post_init__(self):
    # PRESERVE: Existing compatibility logic
    if self.custom_function and not self.function:
        self.function = self.custom_function
    elif self.function and not self.custom_function:
        self.custom_function = self.function
    
    # NEW: Handle delegate field compatibility
    if self.delegate and not self.custom_function:
        self.custom_function = self.delegate
        self.function = self.delegate
    elif self.delegate and self.custom_function:
        # Both exist - preserve existing behavior
        pass
        
    # CRITICAL: Step execution still uses custom_function
    # Line 132-142 pattern remains unchanged
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
uv run ruff check workflows/builder.py --fix
uv run mypy workflows/builder.py

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```bash
# Test backward compatibility first - CRITICAL
uv run pytest tests/unit/test_builder_and_serialization.py -v
# Expected: ALL tests pass unchanged

# Test new step method
uv run pytest tests/unit/test_step_method.py -v
# Expected: All new tests pass

# Test serialization safety
uv run pytest tests/unit/test_step_method.py::test_step_serialization -v
# Expected: Serialization works, no lambda issues
```

### Level 3: Integration Tests
```bash
# CRITICAL: Database decommissioning must work
uv run pytest tests/integration/test_workflow_execution.py -v
# Expected: No failures, all custom_step usage works

# Test production workflow
uv run pytest tests/e2e/test_minimal_integration.py -v
# Expected: No disruption to existing workflows
```

### Level 4: Manual Verification
```bash
# Test database decommissioning workflow manually
cd concrete/db_decommission/
uv run python -c "from utils import create_db_decommission_workflow; print('Import successful')"
# Expected: No import errors, workflow creation works
```

## Final Validation Checklist
- [ ] All existing tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check workflows/`
- [ ] No type errors: `uv run mypy workflows/`
- [ ] Database decommissioning workflow works: Manual test in concrete/db_decommission/
- [ ] Both custom_step and step methods work identically
- [ ] No breaking changes to any of the 13 files using custom_step
- [ ] Serialization safety maintained (no lambda serialization issues)
- [ ] Backward compatibility preserved 100%

## Anti-Patterns to Avoid
- ❌ Don't break existing custom_step calls - maintain 100% backward compatibility
- ❌ Don't introduce lambda serialization issues - test pickle safety
- ❌ Don't modify production database decommissioning code in first phase
- ❌ Don't remove custom_step method - keep it for backward compatibility
- ❌ Don't change existing function signatures or behavior
- ❌ Don't rush migration - phased approach prevents disruption

## Risk Assessment & Mitigation

### High Risk Areas
1. **Database Decommissioning Workflow**: 6 custom_step calls in production
   - Mitigation: Zero changes to concrete/db_decommission/utils.py initially
   
2. **Serialization Compatibility**: Pickle-based WorkflowStep serialization
   - Mitigation: Maintain existing custom_function field, test serialization

3. **Test Suite**: 10+ custom_step calls across multiple test files
   - Mitigation: No test modifications initially, comprehensive validation

### Success Indicators
- All 13 files using custom_step continue to work unchanged
- Database decommissioning workflow executes identically
- New step() method provides equivalent functionality
- Migration path documented for future adoption

## PRP Quality Score: 9/10

**Rationale**: This PRP provides comprehensive context including all 13 affected files, external research on workflow patterns, specific implementation details, and a phased migration approach that minimizes disruption risk. The backward compatibility strategy ensures the critical "ONLY IF IT NOT CAUSE DISRUPTION" requirement is met. The only deduction is for the inherent complexity of refactoring a core API used in 13 files, but the phased approach mitigates this risk significantly.