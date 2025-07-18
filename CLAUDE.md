# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Context Engineering Enabled

This project uses **Context Engineering** - a systematic approach to providing AI assistants with comprehensive, structured context for dramatically improved code generation and implementation accuracy. This is 10x better than prompt engineering and 100x better than basic AI coding.

### Context Engineering Workflow

1. **Feature Request**: Start with detailed `INITIAL.md` template
2. **Research**: Use `/research <feature_area>` to understand existing patterns
3. **Examples**: Use `/examples <pattern_type>` to find relevant patterns
4. **PRP Creation**: Use `/prp <feature_name>` to create comprehensive Product Requirements Prompt
5. **Implementation**: Use `/implement PRPs/active/<feature_name>.md` for structured implementation
6. **Validation**: Use `/validate <feature_name>` for thorough validation

### Context Engineering Commands

- `/research <topic>` - Analyze codebase patterns and architecture
- `/examples <pattern_type>` - Extract relevant code patterns
- `/prp <feature_name>` - Create comprehensive implementation blueprint
- `/implement <prp_file>` - Execute implementation with full context
- `/validate <feature_name>` - Validate implementation against requirements
- `/context <feature_request>` - Assemble comprehensive context

See `.claude/commands.md` for detailed command documentation.

## Project Overview

GraphMCP is a sophisticated workflow orchestration framework that coordinates multiple Model Context Protocol (MCP) servers to build complex workflows for code analysis, repository management, and automated processes. The framework emphasizes async-first design, modular architecture, comprehensive testing, and context engineering principles.

## Development Environment Setup

### Prerequisites
- Python 3.12 or higher (required)
- uv package manager (automatically installed by make setup)

### Quick Start
```bash
# Setup development environment
make setup                      # Install dependencies and setup environment
source .venv/bin/activate      # Activate virtual environment

# Verify installation
make test-all                  # Run all tests
make demo                      # Run demo workflow (mock mode)
```

### Common Development Commands
```bash
# Development
make dev                       # Full development environment setup
make setup-dev                 # Setup with pip for development
make clean                     # Clean build artifacts and cache

# Testing
make test-unit                 # Unit tests only
make test-integration          # Integration tests only
make test-e2e                  # End-to-end tests (requires MCP servers)
make test-logging              # Structured logging tests
make quick-test               # Fast unit tests only

# Code Quality
make lint                      # Code linting with ruff and mypy
make format                    # Code formatting with black
make install-pre-commit        # Install git hooks

# Demos & UI
make demo-real                 # Demo with live MCP services (~5-10min)
make demo-mock                 # Demo with cached data (~30s)
make preview-streamlit         # Start live workflow UI on port 8501
make cmp                       # Complete database decommissioning workflow
```

## Project Architecture

### Core Framework Structure
```
graphmcp/
├── clients/                   # MCP client implementations
│   ├── base.py               # Abstract base class with async context manager
│   ├── github.py             # GitHub repository operations
│   ├── slack.py              # Slack notifications
│   ├── repomix.py            # Repository packaging and analysis
│   └── filesystem.py         # File system operations
├── workflows/                 # Workflow orchestration engine
│   ├── builder.py            # Fluent API for workflow construction
│   ├── context.py            # Shared state management
│   └── ruliade/              # Rule-based workflow patterns
├── concrete/                  # Domain-specific implementations
│   ├── db_decommission/      # Database decommissioning workflow
│   └── preview_ui/           # Streamlit visualization
├── utils/                     # Reusable utilities
│   ├── parameter_service.py  # Configuration management
│   ├── monitoring.py         # System monitoring
│   └── error_handling.py     # Error handling system
├── graphmcp_logging/         # Structured logging system
└── tests/                    # Comprehensive test suite
    ├── unit/                 # Unit tests
    ├── integration/          # Integration tests
    └── e2e/                  # End-to-end tests
```

### Key Architectural Patterns

#### MCP Client Architecture
- **Abstract Base Class**: All clients inherit from `BaseMCPClient`
- **Server Name Pattern**: Each client defines `SERVER_NAME` class attribute
- **Async Context Manager**: Full `async with` support for resource management
- **Error Handling**: Custom exception hierarchy (`MCPConnectionError`, `MCPToolError`)

#### Workflow Builder Pattern (Fluent API)
```python
workflow = (WorkflowBuilder("workflow_name", config_path)
    .with_config(max_parallel_steps=4, default_timeout=120)
    .step_auto("validate", "Validation", validate_step)  # PREFERRED
    .github_analyze_repo("analyze", repo_url)
    .slack_post("notify", channel_id, message)
    .build())
```

**Step Method Preference (in order):**
1. `step_auto()` - **PREFERRED** - Automatically wraps functions to match step signature
2. `step()` - Generic step method with delegate parameter
3. `custom_step()` - Legacy method, avoid unless necessary

#### Multi-Client Orchestration Pattern
```python
# Standard pattern for coordinating multiple MCP clients
github_client = GitHubMCPClient(context.config.config_path)
slack_client = SlackMCPClient(context.config.config_path)
repomix_client = RepomixMCPClient(context.config.config_path)

# Cache clients in workflow context
context._clients['ovr_github'] = github_client
context._clients['ovr_slack'] = slack_client
context._clients['ovr_repomix'] = repomix_client
```

## Configuration Management

### MCP Server Configuration
Edit `mcp_config.json` to configure MCP servers:
```json
{
  "mcpServers": {
    "ovr_github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "$TOKEN"}
    },
    "ovr_slack": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-slack"],
      "env": {"SLACK_BOT_TOKEN": "$TOKEN"}
    }
  }
}
```

### Environment Variables
- **Configuration Precedence**: `.env` → `secrets.json` → system environment
- **Variable Substitution**: Supports `${VAR_NAME}` syntax in configuration files
- **Required for Complete Workflows**: `GITHUB_TOKEN`, `SLACK_BOT_TOKEN` (optional)

## Testing Framework

### Test Structure & Markers
```bash
# Run specific test types
pytest -m unit                # Unit tests only
pytest -m integration         # Integration tests only
pytest -m e2e                 # End-to-end tests
pytest -m "not e2e"          # Skip E2E tests
pytest -k "test_specific"    # Run specific test pattern
```

### Test Categories
- **Unit Tests**: Fast, isolated, no external dependencies
- **Integration Tests**: Component interaction testing
- **E2E Tests**: Full workflow validation with real MCP servers
- **Performance Tests**: Resource management and timing tests

### Test Configuration
- **Coverage Requirement**: 80% minimum coverage
- **Async Support**: `pytest-asyncio` with `asyncio_mode = "auto"`
- **Fixtures**: Mock and real configurations in `conftest.py`

## Code Style & Conventions

### Core Principles
- **File Size Limit**: Maximum 500 lines per file
- **Async-First**: All I/O operations use `async`/`await`
- **Type Safety**: Comprehensive type hints throughout
- **Single Responsibility**: Each module has one clear purpose

### Data Models
```python
@dataclass
class WorkflowResult:
    success: bool
    duration_seconds: float
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WorkflowResult':
        return cls(**data)
```

### Async Context Manager Pattern
```python
class MCPClient:
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
```

### Structured Logging Pattern
```python
from graphmcp_logging import get_logger, LoggingConfig

config = LoggingConfig.from_env()
logger = get_logger(workflow_id=f"workflow_{name}", config=config)

logger.log_workflow_start(params, config)
logger.log_step_start("step_name", "Description...")
logger.log_table("Results", table_data)
logger.log_step_end("step_name", result, success=True)
```

## Specialized Workflows

### Database Decommissioning
Production-ready workflow for AI-driven database decommissioning:

```bash
# Run complete database decommissioning
make cmp                           # Default: postgres_air database
make cmp DB=chinook               # Custom database
make cmp DB=chinook REPO=https://github.com/org/repo  # Custom DB + repo

# Start decommissioning UI
make db-decommission-ui           # Streamlit UI on port 8502
```

**Key Features:**
- Multi-repository processing with GitHub integration
- AI-powered pattern discovery using Repomix
- Contextual rules engine for intelligent file processing
- Quality assurance with automated validation
- Slack notifications with progress tracking

### Live Workflow Streaming
```bash
# Start live workflow visualization
make preview-streamlit            # Start Streamlit UI on port 8501
make preview-demo                 # Complete demo (MCP server + UI)
```

## Important Development Notes

### Virtual Environment
- **Always use venv**: `source .venv/bin/activate` before running Python commands
- **Package Management**: Uses `uv` for fast dependency management
- **Development Dependencies**: pytest, ruff, mypy, black automatically installed

### Error Handling
- **Graceful Degradation**: Workflows continue with caching when services fail
- **Retry Mechanism**: Exponential backoff for transient failures
- **Structured Exceptions**: Custom exception hierarchy for different failure types

### Performance Considerations
- **Connection Pooling**: MCP clients reuse connections
- **Caching Strategy**: Intelligent caching for repeated operations
- **Async Execution**: Parallel processing where possible

### Security
- **Credential Management**: Automatic credential masking in logs
- **Environment Isolation**: Secrets loaded from secure sources
- **Input Validation**: Comprehensive validation of all inputs

## Contributing Guidelines

### Before Making Changes
1. **Read existing code**: Follow established patterns and conventions
2. **Run tests**: `make test-all` to ensure nothing breaks
3. **Check code quality**: `make lint` and `make format`
4. **Add tests**: Unit tests required for new functionality

### File Organization
- **Modular Structure**: Group related functionality together
- **Clear Imports**: Use relative imports within packages
- **Documentation**: Comprehensive docstrings using Google style
- **Error Messages**: Clear, actionable error messages

### Performance & Reliability
- **Resource Management**: Always use async context managers
- **Error Recovery**: Implement graceful degradation strategies
- **Monitoring**: Add appropriate logging and metrics
- **Testing**: Include unit, integration, and E2E tests as appropriate

## Context Engineering Principles

This project follows context engineering principles for AI-assisted development:

### 1. Comprehensive Context Assembly

**Always provide complete context:**
- Reference existing patterns from `examples/` directory
- Include architectural context and constraints
- Specify exact patterns to follow
- Provide detailed implementation requirements

**Example Context Assembly:**
```
When implementing a new MCP client:
1. Study examples/mcp_client/base_client_pattern.py
2. Follow the SERVER_NAME class attribute pattern
3. Implement async context manager support
4. Use structured error handling from examples
5. Add comprehensive logging as shown in examples/logging/
```

### 2. Structured Feature Requests

**Use the INITIAL.md template for all feature requests:**
- Provide comprehensive feature descriptions
- Include business justification and success criteria
- Specify technical requirements and constraints
- Reference existing patterns and similar features
- Define clear acceptance criteria

**Template Sections:**
- Basic Information & Feature Description
- Functional & Technical Requirements
- Implementation Context & Existing Patterns
- Quality Requirements & Testing Strategy
- Acceptance Criteria & Risk Assessment

### 3. Product Requirements Prompts (PRPs)

**Create PRPs for all non-trivial features:**
- Research existing codebase patterns thoroughly
- Assemble comprehensive implementation context
- Provide detailed step-by-step implementation plan
- Include validation criteria and testing requirements
- Reference specific code examples and patterns

**PRP Structure:**
```
PRPs/
├── active/          # Currently active PRPs
├── completed/       # Completed PRPs (archived)
├── templates/       # PRP templates
└── examples/        # Example PRPs
```

### 4. Pattern-Based Implementation

**Follow established patterns consistently:**
- **MCP Clients**: Use BaseMCPClient pattern with SERVER_NAME
- **Workflows**: Use WorkflowBuilder with step_auto() method
- **Logging**: Use structured logging with get_logger()
- **Testing**: Use pytest with appropriate markers
- **Error Handling**: Use custom exception hierarchies

**Pattern Discovery Process:**
1. Use `/research <feature_area>` to understand existing implementations
2. Use `/examples <pattern_type>` to find relevant patterns
3. Follow patterns exactly to maintain consistency
4. Add new patterns to examples/ directory when created

### 5. Validation Gates

**Implement comprehensive validation:**
- Code quality validation (lint, format, type-check)
- Functional validation (unit, integration, E2E tests)
- Performance validation (response time, throughput)
- Architecture validation (pattern compliance)
- Documentation validation (completeness, accuracy)

**Validation Commands:**
- `make lint` - Code quality validation
- `make test-all` - Comprehensive testing
- `make format` - Code formatting
- `/validate <feature_name>` - Full validation suite

### 6. Context Engineering Commands

**Use custom commands for structured development:**

**Research Commands:**
- `/research <topic>` - Comprehensive codebase analysis
- `/examples <pattern_type>` - Pattern extraction and documentation

**Implementation Commands:**
- `/prp <feature_name>` - Create Product Requirements Prompt
- `/implement <prp_file>` - Execute structured implementation
- `/context <feature_request>` - Assemble comprehensive context

**Validation Commands:**
- `/validate <feature_name>` - Comprehensive validation
- Standard make commands for specific validation types

### 7. Documentation-Driven Development

**Maintain comprehensive documentation:**
- Update CLAUDE.md with new patterns and conventions
- Document all patterns in examples/ directory
- Include usage examples and context in all documentation
- Update README.md with feature additions and changes

**Documentation Requirements:**
- All functions must have Google-style docstrings
- All patterns must be documented with examples
- All features must include usage examples
- All changes must update relevant documentation

### 8. Continuous Pattern Evolution

**Evolve patterns based on learnings:**
- Extract new patterns from successful implementations
- Update examples/ directory with new patterns
- Refine PRP templates based on experience
- Improve context engineering process continuously

**Pattern Evolution Process:**
1. Identify successful implementation patterns
2. Extract patterns into reusable examples
3. Update templates and documentation
4. Share patterns across the team
5. Continuously refine the process

### Context Engineering Benefits

Following these principles provides:
- **Predictable Results**: Consistent, high-quality implementations
- **Reduced Iterations**: Fewer implementation mistakes and rework
- **Knowledge Sharing**: Reusable patterns and comprehensive documentation
- **Faster Development**: Structured process with clear guidelines
- **Better Quality**: Comprehensive validation and testing
- **Maintainability**: Consistent patterns and thorough documentation

### Getting Started with Context Engineering

1. **Study the Examples**: Review `examples/` directory thoroughly
2. **Practice the Workflow**: Use the full context engineering process
3. **Create Comprehensive PRPs**: Don't skip the detailed planning phase
4. **Follow Patterns Exactly**: Maintain consistency with existing code
5. **Validate Thoroughly**: Use all validation gates
6. **Document Everything**: Update examples and documentation

### Context Engineering vs. Traditional Approaches

| Aspect | Traditional Coding | Prompt Engineering | Context Engineering |
|--------|-------------------|-------------------|-------------------|
| **Success Rate** | 60-70% | 70-80% | 90-95% |
| **Consistency** | Variable | Moderate | High |
| **Maintainability** | Low | Low | High |
| **Knowledge Sharing** | Limited | Limited | Comprehensive |
| **Rework Required** | High | Moderate | Low |
| **Documentation** | Sparse | Moderate | Comprehensive |

Context engineering transforms AI-assisted development from unpredictable interactions into a systematic, reliable development methodology.