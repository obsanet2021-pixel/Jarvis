# JARVIS Development Policy

## 1. Project Protection
- Read this file before making changes
- Preserve existing project instructions and conventions
- Do not modify application source code, configuration, dependencies, or build files unless explicitly required
- Do not overwrite existing instructions with generic content

## 2. Tool Responsibilities

### Graphify
- Use `graphify-out/GRAPH_REPORT.md`, `graph.json`, and `graph.html` to understand architecture and dependencies
- Consult the graph before significant cross-module changes
- Treat source code as authoritative when graph information conflicts with implementation
- Update the graph after significant architectural changes when appropriate

### Ponytail
- Follow the active Ponytail development mode
- Prefer the smallest complete solution
- Avoid unnecessary abstractions, wrappers, duplicated logic, and speculative features
- Do not sacrifice correctness, security, or maintainability for fewer lines of code

### Agent Skills
- `/spec`: Define requirements for substantial new features
- `/plan`: Plan complex or cross-module tasks
- `/build`: Implement approved plans
- `/test`: Verify behavior
- `/review`: Review changes
- `/code-simplify`: Simplify when justified
- `/constraints`: Respect project constraints
- `/ship`: Prepare verified changes for release
- Use specialist agents when appropriate: `code-reviewer`, `security-auditor`, `test-engineer`, `web-performance-auditor`
- Do not invoke every workflow for trivial changes

## 3. Engineering Rules
- Inspect existing implementation before changing it
- Reuse established architecture and patterns
- Avoid unrelated refactoring
- Preserve public APIs and backward compatibility unless explicitly authorized
- Validate assumptions against actual source code
- Handle errors and edge cases
- Never claim a test passed unless it was actually executed
- Review security implications for permissions, authentication, API endpoints, storage, and integrations
- Never expose secrets, tokens, or credentials in logs or documentation

## 4. Change Management

### Before Significant Changes:
1. Identify affected modules
2. Inspect relevant source files
3. Consult Graphify
4. Define constraints and acceptance criteria
5. Plan implementation

### After Changes:
1. Run relevant tests
2. Review the diff
3. Check for regressions
4. Update documentation when necessary
5. Update Graphify when architecture has materially changed

## 5. Communication
- Explain the intended change before substantial implementation
- Report files changed and why
- Report tests executed and their actual results
- Identify unresolved issues and assumptions
- Ask for approval before destructive operations, major architectural changes, or changes outside the requested scope

---

*This policy governs future JARVIS development sessions.*