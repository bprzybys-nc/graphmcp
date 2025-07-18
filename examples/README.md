# GraphMCP Code Examples

This directory contains comprehensive code examples demonstrating standard patterns and best practices for the GraphMCP framework.

## Overview

These examples serve as reference implementations for common patterns used throughout the GraphMCP codebase. They are designed to be used as templates and learning resources for implementing new features.

## Directory Structure

```
examples/
├── README.md                           # This file
├── mcp_client/                         # MCP client implementation patterns
│   └── base_client_pattern.py         # Standard MCP client implementation
├── workflow/                           # Workflow orchestration patterns
│   └── workflow_builder_pattern.py    # Workflow builder and execution patterns
├── logging/                           # Structured logging patterns
│   └── structured_logging_pattern.py  # Comprehensive logging examples
├── testing/                           # Testing patterns and fixtures
│   └── test_patterns.py              # Testing best practices
├── async/                             # Async/await patterns
│   └── async_patterns.py             # Async programming patterns
└── error_handling/                    # Error handling patterns
    └── error_patterns.py             # Error handling and recovery
```

## Example Categories

### 1. MCP Client Patterns (`mcp_client/`)

**File**: `base_client_pattern.py`

Demonstrates the standard pattern for implementing MCP clients:
- Abstract base class inheritance
- SERVER_NAME class attribute pattern
- Async context manager implementation
- Connection management and health checks
- Tool listing and execution
- Structured error handling

**Key Patterns**:
```python
class ExampleMCPClient(BaseMCPClient):
    SERVER_NAME = "example_server"
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
```

### 2. Workflow Patterns (`workflow/`)

**File**: `workflow_builder_pattern.py`

Demonstrates workflow creation and execution:
- Fluent builder API usage
- Step function implementation
- Context management
- Error handling and recovery
- Parallel execution
- Result processing

**Key Patterns**:
```python
workflow = (WorkflowBuilder("example_workflow", config_path)
    .with_config(max_parallel_steps=4, default_timeout=120)
    .step_auto("validate", "Validation", validate_step)  # PREFERRED
    .github_analyze_repo("analyze", repo_url)
    .slack_post("notify", channel_id, message)
    .build())
```

### 3. Logging Patterns (`logging/`)

**File**: `structured_logging_pattern.py`

Demonstrates structured logging throughout the framework:
- Workflow-level logging
- Step-level logging
- Table and chart logging
- Error logging with context
- Progress tracking
- Custom formatters

**Key Patterns**:
```python
logger_instance = get_logger(workflow_id, config)
logger_instance.log_workflow_start(params, config)
logger_instance.log_step_start("step_name", "Description")
logger_instance.log_table("Results", table_data)
logger_instance.log_step_end("step_name", result, success=True)
```

### 4. Testing Patterns (`testing/`)

**File**: `test_patterns.py`

Demonstrates testing best practices:
- Unit test structure
- Integration test patterns
- E2E test implementation
- Mock and fixture usage
- Async test patterns
- Performance testing

**Key Patterns**:
```python
@pytest.mark.unit
async def test_example_function():
    # Test implementation
    pass

@pytest.mark.integration
async def test_mcp_client_integration():
    # Integration test
    pass
```

### 5. Async Patterns (`async/`)

**File**: `async_patterns.py`

Demonstrates async programming patterns:
- Async context managers
- Concurrent execution
- Resource management
- Error handling in async code
- Timeout handling
- Connection pooling

**Key Patterns**:
```python
async def process_concurrently(items):
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(process_item(item)) for item in items]
    return [task.result() for task in tasks]
```

### 6. Error Handling Patterns (`error_handling/`)

**File**: `error_patterns.py`

Demonstrates error handling and recovery:
- Custom exception hierarchies
- Retry mechanisms
- Circuit breaker patterns
- Graceful degradation
- Error context preservation
- Recovery strategies

**Key Patterns**:
```python
try:
    await risky_operation()
except MCPConnectionError as e:
    logger.error(f"Connection error: {e}")
    # Handle connection issues
except MCPToolError as e:
    logger.error(f"Tool error: {e}")
    # Handle tool execution issues
```

## Using the Examples

### 1. As Templates
Copy example files and modify them for your specific use case:

```bash
# Copy MCP client example
cp examples/mcp_client/base_client_pattern.py clients/my_new_client.py

# Modify for your specific MCP server
# Update SERVER_NAME and implement specific methods
```

### 2. As Learning Resources
Study the examples to understand GraphMCP patterns:

```python
# Read the examples to understand:
# - Async patterns
# - Error handling
# - Logging strategies
# - Testing approaches
```

### 3. As Reference Implementations
Use examples as reference for implementing similar functionality:

```python
# Reference workflow builder pattern
# Reference logging patterns
# Reference error handling strategies
```

## Example Usage in Context Engineering

These examples are integral to the context engineering workflow:

### In PRPs (Product Requirements Prompts)
```markdown
### Code Context

#### Existing Patterns
Reference: `examples/mcp_client/base_client_pattern.py`
- Follow the standard MCP client implementation pattern
- Use async context managers for resource management
- Implement structured error handling
```

### In Implementation
```python
# Use examples as implementation guides
# Follow established patterns
# Maintain consistency with existing code
```

## Best Practices

### 1. Pattern Consistency
- Follow the patterns demonstrated in examples
- Use the same naming conventions
- Maintain consistent error handling
- Follow the same logging patterns

### 2. Code Quality
- All examples follow GraphMCP code quality standards
- Maximum 500 lines per file
- Comprehensive type hints
- Full documentation

### 3. Testing Integration
- Examples include testing patterns
- Use pytest with async support
- Follow the testing pyramid
- Include performance considerations

### 4. Documentation
- Examples are fully documented
- Include usage examples
- Explain design decisions
- Provide context for patterns

## Continuous Improvement

These examples are living documents that evolve with the framework:

### Adding New Examples
1. Create new example files following the established structure
2. Include comprehensive documentation
3. Add usage examples
4. Update this README

### Updating Existing Examples
1. Maintain backward compatibility
2. Add new patterns as they emerge
3. Update documentation
4. Ensure examples remain current

### Pattern Evolution
1. Identify new patterns in the codebase
2. Extract them into examples
3. Document best practices
4. Share knowledge across the team

## Integration with Context Engineering

Examples are designed to work with the context engineering workflow:

1. **Research Phase**: Use examples to understand existing patterns
2. **PRP Creation**: Reference examples in Product Requirements Prompts
3. **Implementation**: Follow example patterns during development
4. **Validation**: Compare implementations against examples

## Getting Started

1. **Browse Examples**: Start with the README files in each category
2. **Study Patterns**: Read through the example implementations
3. **Run Examples**: Execute the examples to see them in action
4. **Apply Patterns**: Use the patterns in your own implementations

## Contributing

When adding new examples:

1. **Follow the Structure**: Use the established directory structure
2. **Include Documentation**: Add comprehensive docstrings and comments
3. **Provide Context**: Explain when and why to use each pattern
4. **Test Examples**: Ensure examples run correctly
5. **Update Documentation**: Update this README with new examples