# GraphMCP Context Engineering Commands

This file defines custom commands for context engineering in the GraphMCP framework.

## /prp - Product Requirements Prompt

Creates a comprehensive Product Requirements Prompt (PRP) for implementing new features in the GraphMCP framework.

### Usage
```
/prp <feature_name>
```

### Process
1. **Research Phase**: Analyze existing codebase patterns, architecture, and similar implementations
2. **Requirements Gathering**: Extract requirements from INITIAL.md and related documentation
3. **Pattern Analysis**: Identify relevant code patterns from examples/ directory
4. **Context Assembly**: Compile comprehensive implementation context
5. **Blueprint Creation**: Generate detailed implementation blueprint with:
   - Architecture overview
   - Code patterns to follow
   - Testing requirements
   - Implementation steps
   - Validation criteria

### Output
Creates `PRPs/<feature_name>.md` with complete implementation blueprint.

## /implement - Context-Aware Implementation

Executes feature implementation using comprehensive context engineering approach.

### Usage
```
/implement <prp_file>
```

### Process
1. **Context Loading**: Load PRP, examples, and architectural context
2. **Task Planning**: Create detailed implementation task list
3. **Implementation**: Execute with continuous validation
4. **Testing**: Run comprehensive test suite
5. **Documentation**: Update relevant documentation
6. **Validation**: Verify implementation meets requirements

## /validate - Implementation Validation

Validates implementation against GraphMCP standards and requirements.

### Usage
```
/validate <feature_name>
```

### Process
1. **Code Quality**: Run linting, formatting, type checking
2. **Testing**: Execute unit, integration, and E2E tests
3. **Architecture**: Verify architectural patterns compliance
4. **Documentation**: Check documentation completeness
5. **Performance**: Validate performance requirements
6. **Security**: Check security best practices

## /examples - Generate Code Examples

Extracts and documents code patterns from existing GraphMCP codebase.

### Usage
```
/examples <pattern_type>
```

### Pattern Types
- `mcp_client` - MCP client implementation patterns
- `workflow` - Workflow orchestration patterns
- `logging` - Structured logging patterns
- `testing` - Testing patterns and fixtures
- `async` - Async/await patterns
- `error_handling` - Error handling patterns

## /research - Codebase Research

Performs comprehensive codebase analysis to understand implementation patterns.

### Usage
```
/research <topic>
```

### Process
1. **Pattern Discovery**: Identify existing implementations
2. **Architecture Analysis**: Understand structural patterns
3. **Dependency Mapping**: Map component relationships
4. **Best Practices**: Extract established conventions
5. **Gap Analysis**: Identify missing patterns or improvements

## /context - Context Assembly

Assembles comprehensive context for complex feature implementation.

### Usage
```
/context <feature_request>
```

### Process
1. **Architecture Context**: Load framework architecture
2. **Pattern Context**: Load relevant code patterns
3. **Testing Context**: Load testing requirements
4. **Documentation Context**: Load documentation standards
5. **Implementation Context**: Compile implementation guidelines

## Command Integration

These commands are designed to work together in the context engineering workflow:

```
/research new_feature_area
/examples relevant_patterns
/prp new_feature_name
/implement PRPs/new_feature_name.md
/validate new_feature_name
```

## Best Practices

1. **Always start with research** - Understand existing patterns before implementing
2. **Use comprehensive PRPs** - Don't skip the detailed planning phase
3. **Validate continuously** - Run validation after each major change
4. **Document patterns** - Add new patterns to examples/ directory
5. **Follow the workflow** - Use the full context engineering process