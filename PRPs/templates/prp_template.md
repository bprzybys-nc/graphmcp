# Product Requirements Prompt (PRP) Template

## Feature Overview
**Feature Name**: [Feature Name]
**Priority**: [High/Medium/Low]
**Estimated Complexity**: [Simple/Medium/Complex]
**Implementation Date**: [YYYY-MM-DD]

### Description
[Comprehensive description of the feature]

### Business Value
[Why this feature is needed]

### Success Criteria
[Specific, measurable criteria for success]

## Technical Requirements

### Architecture Integration
- **Framework Component**: [Which GraphMCP component this affects]
- **MCP Clients Required**: [List of MCP clients needed]
- **Workflow Integration**: [How this integrates with existing workflows]
- **Dependencies**: [External dependencies or internal components]

### Implementation Patterns
- **Base Classes**: [Which base classes to extend]
- **Design Patterns**: [Specific patterns to follow]
- **Error Handling**: [Error handling strategy]
- **Logging**: [Logging requirements]
- **Testing**: [Testing strategy]

### Performance Requirements
- **Response Time**: [Expected response time]
- **Throughput**: [Expected throughput]
- **Memory Usage**: [Memory constraints]
- **Concurrency**: [Concurrency requirements]

## Code Context

### Existing Patterns
```python
# Reference existing code patterns that should be followed
```

### Similar Implementations
- [List similar features in the codebase]
- [Reference implementation locations]

### Architecture Diagram
```
[ASCII diagram showing how this feature fits into the architecture]
```

## Implementation Plan

### Phase 1: Foundation
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]

### Phase 2: Core Implementation
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]

### Phase 3: Integration & Testing
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]

### Phase 4: Documentation & Validation
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]

## Testing Strategy

### Unit Tests
- [List unit test requirements]
- [Coverage expectations]

### Integration Tests
- [List integration test requirements]
- [External service mocking]

### End-to-End Tests
- [List E2E test scenarios]
- [Performance benchmarks]

## Documentation Requirements

### Code Documentation
- [Docstring requirements]
- [Type hint requirements]
- [Inline comment requirements]

### User Documentation
- [README updates]
- [API documentation]
- [Usage examples]

### Technical Documentation
- [Architecture diagrams]
- [Sequence diagrams]
- [Configuration guides]

## File Structure

### New Files
```
path/to/new/file.py
path/to/another/file.py
```

### Modified Files
```
path/to/existing/file.py
path/to/another/existing/file.py
```

### Configuration Changes
```
config/file.json
```

## Validation Criteria

### Code Quality
- [ ] All code follows GraphMCP conventions
- [ ] File size limit (500 lines) respected
- [ ] Type hints complete
- [ ] Async patterns used correctly
- [ ] Error handling implemented

### Testing
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] E2E tests written and passing
- [ ] Coverage threshold met (80%)

### Documentation
- [ ] All functions have docstrings
- [ ] README updated
- [ ] CLAUDE.md updated if needed
- [ ] Examples added to examples/ directory

### Performance
- [ ] Response time requirements met
- [ ] Memory usage within limits
- [ ] Concurrency requirements met
- [ ] No performance regressions

## Rollback Plan

### Risk Assessment
- [Identify potential risks]
- [Mitigation strategies]

### Rollback Procedure
- [Step-by-step rollback process]
- [Dependencies to consider]

## Post-Implementation

### Monitoring
- [Metrics to monitor]
- [Alerting requirements]

### Maintenance
- [Ongoing maintenance requirements]
- [Update procedures]

## Notes

### Research Findings
[Key findings from codebase research]

### Design Decisions
[Important design decisions and rationale]

### Future Considerations
[Potential future enhancements or refactoring]