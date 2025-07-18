# Product Requirements Prompts (PRPs)

This directory contains Product Requirements Prompts (PRPs) for the GraphMCP framework. PRPs are comprehensive implementation blueprints that provide AI assistants with complete context for feature development.

## What are PRPs?

PRPs are detailed documents that combine:
- Feature requirements and business context
- Technical implementation guidance
- Code patterns and architectural context
- Testing and validation requirements
- Step-by-step implementation plans

They serve as "screenplays" for AI assistants, providing all necessary context for accurate implementation.

## Directory Structure

```
PRPs/
├── README.md                 # This file
├── templates/               # PRP templates
│   └── prp_template.md     # Standard PRP template
├── active/                  # Currently active PRPs
├── completed/              # Completed PRPs (archived)
└── examples/               # Example PRPs for reference
```

## PRP Lifecycle

### 1. Creation
- Start with a feature request in `INITIAL.md`
- Use `/research` command to analyze codebase
- Create PRP using template in `templates/prp_template.md`
- Place in `active/` directory

### 2. Implementation
- Use `/implement` command with PRP file
- Follow implementation plan step-by-step
- Validate continuously during development
- Update PRP with findings and decisions

### 3. Completion
- Use `/validate` command for final validation
- Move completed PRP to `completed/` directory
- Update examples if new patterns were created

## Creating a PRP

### Step 1: Research
```bash
# Analyze existing patterns
/research <feature_area>

# Extract relevant code patterns
/examples <pattern_type>
```

### Step 2: Create PRP
```bash
# Create comprehensive PRP
/prp <feature_name>
```

### Step 3: Implement
```bash
# Execute implementation
/implement PRPs/active/<feature_name>.md
```

### Step 4: Validate
```bash
# Validate implementation
/validate <feature_name>
```

## PRP Best Practices

### Content Requirements
- **Comprehensive Context**: Include all relevant architectural context
- **Specific Patterns**: Reference exact code patterns to follow
- **Clear Success Criteria**: Define measurable success criteria
- **Detailed Testing**: Specify testing requirements and strategies
- **Implementation Steps**: Provide step-by-step implementation plan

### Technical Requirements
- **Architecture Alignment**: Ensure alignment with GraphMCP architecture
- **Pattern Consistency**: Follow established code patterns
- **Performance Considerations**: Address performance requirements
- **Error Handling**: Specify error handling strategies
- **Logging**: Define logging requirements

### Documentation Requirements
- **Code Documentation**: Specify docstring and comment requirements
- **User Documentation**: Define user-facing documentation needs
- **Technical Documentation**: Specify technical documentation updates

## Example PRPs

### Simple Feature
- **File**: `examples/simple_feature_prp.md`
- **Description**: Example PRP for adding a simple utility function
- **Complexity**: Low
- **Implementation Time**: 1-2 hours

### Medium Feature
- **File**: `examples/medium_feature_prp.md`
- **Description**: Example PRP for adding a new MCP client
- **Complexity**: Medium
- **Implementation Time**: 1-2 days

### Complex Feature
- **File**: `examples/complex_feature_prp.md`
- **Description**: Example PRP for adding a new workflow orchestration feature
- **Complexity**: High
- **Implementation Time**: 1-2 weeks

## PRP Quality Checklist

### Content Quality
- [ ] Feature requirements clearly defined
- [ ] Business value articulated
- [ ] Success criteria measurable
- [ ] Architecture integration specified
- [ ] Code patterns referenced

### Technical Quality
- [ ] Implementation plan detailed
- [ ] Testing strategy comprehensive
- [ ] Error handling specified
- [ ] Performance requirements defined
- [ ] Documentation requirements clear

### Completeness
- [ ] All sections filled out
- [ ] Code examples included
- [ ] File structure specified
- [ ] Validation criteria defined
- [ ] Rollback plan included

## Integration with GraphMCP

PRPs are designed to work seamlessly with the GraphMCP framework:

- **Architecture Aware**: Reference GraphMCP components and patterns
- **Testing Integrated**: Align with GraphMCP testing framework
- **Documentation Consistent**: Follow GraphMCP documentation standards
- **Quality Aligned**: Meet GraphMCP code quality requirements

## Continuous Improvement

PRPs are living documents that improve over time:
- **Feedback Integration**: Incorporate feedback from implementations
- **Pattern Evolution**: Update patterns as the codebase evolves
- **Template Refinement**: Continuously improve PRP templates
- **Example Updates**: Add new examples as patterns emerge

## Getting Started

1. **Read existing PRPs**: Review examples to understand the format
2. **Use templates**: Start with the standard template
3. **Follow the process**: Use the full context engineering workflow
4. **Validate thoroughly**: Ensure implementation meets all requirements
5. **Document learnings**: Update PRPs with implementation findings