# Secure Code Reasoner - System Architecture Specification

## Document Status

**Version**: 1.0  
**Status**: Draft for Review  
**Last Updated**: 2024

## Overview

This document defines the system architecture for Secure Code Reasoner, a research-oriented toolkit for code analysis and fingerprinting. The architecture prioritizes correctness, determinism, modularity, and testability over performance optimization.

## Architectural Principles

1. **Separation of Concerns**: Each subsystem has a single, well-defined responsibility
2. **Immutability**: Core data structures are immutable where possible
3. **Determinism**: All operations produce deterministic, reproducible results
4. **Fail-Safe Defaults**: Subsystems fail gracefully with clear error boundaries
5. **Explicit Dependencies**: All dependencies between subsystems are explicit and documented
6. **No Side Effects**: Pure functions preferred; side effects isolated and explicit

## System Boundaries

The system is divided into five primary subsystems:

1. **Fingerprinting Subsystem**
2. **Agent Framework Subsystem**
3. **Tracing Subsystem**
4. **Reporting Subsystem**
5. **CLI Subsystem**

Each subsystem operates independently and communicates through well-defined interfaces. There are no circular dependencies between subsystems.

## Subsystem Specifications

### 1. Fingerprinting Subsystem

#### Purpose
Analyzes repository structure, extracts semantic code segments, builds dependency relationships, and generates deterministic fingerprints.

#### Responsibilities
- Walk repository file system and identify processable files
- Parse source code into semantic segments (files, classes, functions)
- Extract structural metadata (line counts, parameters, inheritance)
- Detect risk signals through static pattern analysis
- Build dependency graphs representing code relationships
- Generate deterministic fingerprint hashes
- Ignore non-code files and standard ignore patterns

#### Non-Responsibilities
- Does not execute code
- Does not perform dynamic analysis
- Does not modify source code
- Does not access external services or networks
- Does not generate reports or formatted output
- Does not interpret findings or assign severity

#### Inputs
- Repository path (filesystem path)
- Configuration (file extensions, ignore patterns)

#### Outputs
- Fingerprint object containing:
  - Repository metadata (path, file counts, line counts)
  - Code segments (files, classes, functions)
  - Dependency graph
  - Risk signal counts
  - Deterministic fingerprint hash
  - Language distribution

#### Interface Contract
- Input validation: Repository path must exist and be a directory
- Error handling: Raises FingerprintingError for invalid inputs or parsing failures
- Determinism: Same repository produces identical fingerprint hash
- Idempotency: Multiple calls with same input produce identical output

#### Data Flow
- Receives: Repository path from CLI or API caller
- Produces: Fingerprint object consumed by Agent Framework and Reporting subsystems

#### Bug Prevention Strategies
- Immutable data structures prevent accidental mutation
- Deterministic hashing ensures reproducibility
- File system operations wrapped in try-except with specific error types
- AST parsing errors isolated per-file (one file failure does not stop entire fingerprint)
- Dependency graph construction validates node existence before edge creation
- Type checking enforces correct segment types

#### Critical Failure Points
- File system access failures (permission denied, missing files)
- Syntax errors in source code (handled per-file, logged, not fatal)
- Memory exhaustion on very large repositories (no explicit handling, relies on Python runtime)

---

### 2. Agent Framework Subsystem

#### Purpose
Coordinates multiple specialized analysis agents, merges their findings, and produces unified review reports.

#### Responsibilities
- Define agent interface contract
- Execute multiple agents in sequence
- Aggregate findings from all agents
- Merge patch suggestions
- Generate summary statistics
- Sort findings by severity
- Isolate agent failures (one agent failure does not stop others)

#### Non-Responsibilities
- Does not perform code analysis directly (delegates to agents)
- Does not access file system or repository
- Does not execute code
- Does not format output for display
- Does not persist results
- Does not validate agent implementations

#### Inputs
- Fingerprint object from Fingerprinting subsystem
- List of agent instances to execute

#### Outputs
- AgentReport object containing:
  - Agent name
  - List of findings (severity, title, description, recommendations)
  - List of patch suggestions (original code, suggested code, line ranges)
  - Summary text
  - Metadata (counts, statistics)

#### Interface Contract
- Agent interface: All agents implement `analyze(fingerprint: Fingerprint) -> AgentReport`
- Coordinator interface: `review(fingerprint: Fingerprint) -> AgentReport`
- Error isolation: Agent exceptions caught, logged, and isolated
- Determinism: Same fingerprint and agent set produces identical report structure
- Order independence: Agent execution order does not affect final merged results

#### Data Flow
- Receives: Fingerprint object from Fingerprinting subsystem
- Produces: AgentReport object consumed by Reporting subsystem
- Internal: Each agent receives fingerprint, produces individual report, coordinator merges reports

#### Bug Prevention Strategies
- Agent interface enforces type contracts
- Coordinator catches and logs agent exceptions without failing entire review
- Findings sorted deterministically by severity priority
- Immutable finding objects prevent accidental modification
- Type checking ensures correct severity levels and data structures
- Coordinator validates agent list is non-empty

#### Critical Failure Points
- Agent implementation bugs (isolated, logged, review continues)
- Memory exhaustion with very large fingerprints (no explicit handling)
- Invalid agent implementations (type system prevents at development time)

---

### 3. Tracing Subsystem

#### Purpose
Executes untrusted code in a controlled environment, captures execution traces, and calculates risk scores.

#### Responsibilities
- Execute code in subprocess with resource limits
- Enforce execution timeouts
- Capture standard output and error streams
- Parse trace events from execution output
- Calculate risk scores based on trace events
- Apply sandbox restrictions (network, file write)
- Limit output size to prevent memory exhaustion

#### Non-Responsibilities
- Does not provide full OS-level sandboxing (relies on subprocess isolation)
- Does not prevent all security issues (advisory restrictions only)
- Does not modify code before execution
- Does not persist execution traces
- Does not format output for display
- Does not interpret risk scores (scoring only)

#### Inputs
- Script path (filesystem path to executable script)
- Execution arguments (optional list of command-line arguments)
- Configuration (timeout, allow_network, allow_file_write, max_output_size)

#### Outputs
- ExecutionTrace object containing:
  - Script path
  - List of trace events (type, timestamp, metadata)
  - Exit code
  - Execution time
  - Risk score (score, factors, explanation)
  - Standard output (truncated to max size)
  - Standard error (truncated to max size)

#### Interface Contract
- Input validation: Script path must exist and be a file
- Timeout enforcement: Execution terminates after timeout, returns exit code -1
- Output limits: Stdout/stderr truncated to max_output_size
- Error handling: Raises TracingError for invalid inputs, SandboxError for execution failures
- Determinism: Same script and configuration produce identical trace structure (timestamps may vary)
- Safety: Timeout and output limits prevent resource exhaustion

#### Data Flow
- Receives: Script path and configuration from CLI or API caller
- Produces: ExecutionTrace object consumed by Reporting subsystem
- External: Spawns subprocess, communicates via stdout/stderr

#### Bug Prevention Strategies
- Timeout enforcement prevents infinite execution
- Output size limits prevent memory exhaustion
- Subprocess isolation prevents direct system modification
- Exit code validation distinguishes normal exit from timeout/error
- Risk score calculation uses deterministic rules (no randomness)
- Trace event parsing validates event types before creation
- Environment variable restrictions provide advisory sandboxing

#### Critical Failure Points
- Subprocess execution failures (permission denied, missing interpreter)
- Timeout expiration (handled, returns trace with timeout flag)
- Output size exceeding limits (handled by truncation)
- Script execution errors (captured in stderr, not fatal)
- Security bypass (advisory restrictions only, not guaranteed)

---

### 4. Reporting Subsystem

#### Purpose
Formats analysis results into structured output formats and writes reports to files or returns formatted strings.

#### Responsibilities
- Format fingerprints as JSON or text
- Format agent reports as JSON or text
- Format execution traces as JSON or text
- Write reports to filesystem
- Handle file I/O errors
- Ensure output encoding consistency (UTF-8)

#### Non-Responsibilities
- Does not perform analysis
- Does not interpret findings
- Does not filter or transform data (formatting only)
- Does not validate input data structures
- Does not cache or persist reports
- Does not provide interactive output

#### Inputs
- Fingerprint object (from Fingerprinting subsystem)
- AgentReport object (from Agent Framework subsystem)
- ExecutionTrace object (from Tracing subsystem)
- Output path (optional filesystem path)
- Format selection (JSON or text)

#### Outputs
- Formatted string (JSON or text)
- Written file (if output path provided)

#### Interface Contract
- Format selection: Formatter selected at Reporter initialization
- Output path: Optional, if provided creates parent directories
- Error handling: Raises ReportingError for file I/O failures
- Encoding: All output uses UTF-8 encoding
- Determinism: Same input produces identical formatted output
- Idempotency: Multiple formatting calls produce identical results

#### Data Flow
- Receives: Fingerprint, AgentReport, or ExecutionTrace objects from other subsystems
- Produces: Formatted strings or files consumed by CLI or API callers
- Internal: Formatter converts objects to strings, Reporter handles I/O

#### Bug Prevention Strategies
- Formatter interface enforces consistent output structure
- File writing creates parent directories automatically
- UTF-8 encoding prevents encoding errors
- Error handling isolates file I/O failures
- Type checking ensures correct formatter selection
- Output path validation prevents directory traversal (relies on Path library)

#### Critical Failure Points
- File system write failures (permission denied, disk full)
- Invalid output path (handled by Path library, raises ReportingError)
- Encoding errors (prevented by explicit UTF-8 specification)
- Memory exhaustion with very large reports (no explicit handling)

---

### 5. CLI Subsystem

#### Purpose
Provides command-line interface for all system operations, coordinates subsystem interactions, and handles user input/output.

#### Responsibilities
- Parse command-line arguments
- Validate user inputs
- Initialize subsystems with configuration
- Coordinate workflow between subsystems
- Handle errors and display messages
- Configure logging verbosity
- Provide help text and usage information

#### Non-Responsibilities
- Does not perform analysis (delegates to subsystems)
- Does not format output (delegates to Reporting subsystem)
- Does not validate repository contents
- Does not persist configuration
- Does not provide interactive prompts
- Does not manage state between commands

#### Inputs
- Command-line arguments (path, options, flags)
- Environment variables (for logging configuration)

#### Outputs
- Formatted output to stdout/stderr
- Exit codes (0 for success, 1 for failure)
- Log messages (based on verbosity)

#### Interface Contract
- Command structure: Three commands (analyze, trace, report)
- Input validation: Paths validated for existence before processing
- Error handling: Exceptions caught, logged, displayed, exit code 1
- Logging: Configurable via --verbose and --quiet flags
- Determinism: Same command-line arguments produce identical behavior
- Stateless: Each command is independent, no state persists between commands

#### Data Flow
- Receives: Command-line arguments from user
- Produces: Formatted output to stdout/stderr
- Coordinates: Fingerprinting -> Agent Framework -> Reporting workflow
- Coordinates: Tracing -> Reporting workflow

#### Bug Prevention Strategies
- Input validation before subsystem initialization
- Error handling wraps all subsystem calls
- Logging provides debugging information
- Exit codes indicate success/failure clearly
- Type checking ensures correct argument types
- Path validation prevents invalid file system access
- Command isolation prevents state leakage between commands

#### Critical Failure Points
- Invalid command-line arguments (handled by Click library)
- Missing required arguments (handled by Click library)
- Subsystem initialization failures (caught, logged, exit code 1)
- Subsystem execution failures (caught, logged, exit code 1)
- Output stream failures (rare, not explicitly handled)

---

## Inter-Subsystem Data Flow

### Primary Workflow: Analysis

```
CLI Subsystem
    ↓ (repository path)
Fingerprinting Subsystem
    ↓ (Fingerprint object)
Agent Framework Subsystem
    ↓ (AgentReport object)
Reporting Subsystem
    ↓ (formatted output)
CLI Subsystem (stdout)
```

### Secondary Workflow: Execution Tracing

```
CLI Subsystem
    ↓ (script path, configuration)
Tracing Subsystem
    ↓ (ExecutionTrace object)
Reporting Subsystem
    ↓ (formatted output)
CLI Subsystem (stdout)
```

### Data Object Flow

1. **Fingerprint Object**: Created by Fingerprinting, consumed by Agent Framework and Reporting
2. **AgentReport Object**: Created by Agent Framework, consumed by Reporting
3. **ExecutionTrace Object**: Created by Tracing, consumed by Reporting
4. **Formatted Strings**: Created by Reporting, consumed by CLI

## Error Handling Architecture

### Error Propagation

- Each subsystem defines custom exception types (FingerprintingError, AgentError, TracingError, ReportingError, SandboxError)
- Exceptions propagate upward through call stack
- CLI subsystem catches all exceptions and converts to user-friendly messages
- Subsystem errors do not cross subsystem boundaries (each subsystem handles its own errors)

### Error Isolation

- Fingerprinting: File parsing errors isolated per-file
- Agent Framework: Agent failures isolated per-agent
- Tracing: Execution failures isolated to single trace operation
- Reporting: File I/O errors isolated per-file write

### Error Recovery

- No automatic retry mechanisms
- No fallback behaviors
- Failures are explicit and logged
- User receives clear error messages

## Security Considerations

### Input Validation

- All file system paths validated before use
- Repository paths must exist and be directories
- Script paths must exist and be files
- Output paths validated by Path library

### Sandboxing

- Tracing subsystem uses subprocess isolation (not guaranteed security)
- Environment variable restrictions are advisory only
- No OS-level sandboxing or containerization
- Users must not execute untrusted code without additional security measures

### Resource Limits

- Execution timeouts enforced
- Output size limits enforced
- No explicit memory limits (relies on Python runtime)
- No explicit CPU limits

## Determinism Guarantees

### Fingerprinting

- Same repository produces identical fingerprint hash
- File processing order is deterministic (sorted paths)
- Dependency graph construction is deterministic
- Risk signal detection is rule-based (no randomness)

### Agent Framework

- Agent execution order does not affect merged results
- Finding sorting is deterministic (severity priority)
- Report structure is deterministic

### Tracing

- Risk score calculation uses deterministic rules
- Trace event parsing is deterministic
- Execution order is deterministic (single subprocess)

### Reporting

- Formatting is deterministic (no random ordering)
- JSON serialization is deterministic
- Text formatting is deterministic

## Testing Strategy

### Unit Testing

- Each subsystem tested independently
- Mock interfaces for cross-subsystem dependencies
- Test deterministic behavior
- Test error conditions

### Integration Testing

- Test full workflows (CLI -> Fingerprinting -> Agents -> Reporting)
- Test error propagation
- Test data object transformations

### System Testing

- Test with real repositories
- Test with various code patterns
- Test error scenarios
- Test performance characteristics

## Extension Points

### Adding New Agents

- Implement Agent interface
- Add to AgentCoordinator agent list
- No changes required to other subsystems

### Adding New Formatters

- Implement Formatter interface
- Add to Reporter formatter selection
- No changes required to other subsystems

### Adding New Languages

- Extend Fingerprinting subsystem parser
- Add language-specific segment extraction
- No changes required to other subsystems

## Architecture Constraints

### Immutability

- Core data objects (Fingerprint, AgentReport, ExecutionTrace) are immutable
- Subsystems cannot modify input objects
- All transformations create new objects

### No Circular Dependencies

- Subsystems form a directed acyclic graph
- CLI depends on all subsystems
- Reporting depends on data objects (not other subsystems)
- Agent Framework depends on Fingerprinting data objects
- No subsystem depends on CLI

### No Global State

- All state is explicit and passed as parameters
- No singleton patterns
- No module-level mutable state
- Configuration passed explicitly

## Performance Considerations

### Scalability

- Fingerprinting processes files sequentially (no parallelization)
- Agent execution is sequential (no parallelization)
- Tracing executes single subprocess (no parallelization)
- Large repositories may be slow (acceptable for research tool)

### Resource Usage

- Memory usage scales with repository size
- No streaming or incremental processing
- All data loaded into memory
- Output size limits prevent excessive memory usage

### Optimization Opportunities

- File processing could be parallelized (future enhancement)
- Agent execution could be parallelized (future enhancement)
- Dependency graph could use more efficient data structures (future enhancement)

## Conclusion

This architecture prioritizes correctness, determinism, and modularity over performance. Each subsystem has clear boundaries, explicit interfaces, and well-defined responsibilities. The design prevents common bugs through immutability, type checking, error isolation, and deterministic operations. The system is extensible through well-defined interfaces while maintaining architectural constraints.

