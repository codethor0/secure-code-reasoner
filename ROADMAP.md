# Secure Code Reasoner - Development Roadmap

## Current Version: v0.1.0 (CLI Engine)

Secure Code Reasoner v0.1.0 is a **CLI-based security analysis engine** with deterministic execution, strong correctness guarantees, and clean subsystem separation.

## Future Roadmap

### Planned: Web GUI Application

**Goal**: Transform the CLI engine into a web-based security analysis platform.

**Planned Capabilities**:
- Web-based user interface for repository analysis
- Interactive report viewing and filtering
- Real-time analysis progress tracking
- User authentication and session management
- Multi-user support with access controls

**Architecture Approach**:
- Web GUI will be built as a separate layer consuming the CLI engine as a library
- Core correctness guarantees will be preserved
- Security boundaries will be maintained between web layer and analysis engine

**Status**: Design phase (not yet implemented)

### Planned: Multi-LLM Review Framework

**Goal**: Extend the agent framework to support multiple LLM providers for code review.

**Planned Capabilities**:
- LLM provider adapter architecture (OpenAI, Anthropic, Google, etc.)
- Configurable LLM selection per analysis
- Multi-LLM consensus mechanisms
- Provider-specific prompt optimization
- API key management and security

**Architecture Approach**:
- Provider adapters will be isolated from core analysis logic
- Deterministic merging of LLM outputs will be maintained
- No LLM provider logic will leak into core domain code

**Status**: Design phase (not yet implemented)

### Planned: Enhanced Sandbox Architecture

**Goal**: Provide stronger isolation guarantees for code execution.

**Planned Capabilities**:
- OS-level sandboxing (beyond Python-level restrictions)
- Container-based isolation
- Resource limits enforcement
- Network isolation guarantees
- Filesystem access controls

**Status**: Research phase (not yet implemented)

## Development Principles

1. **Preserve Correctness**: All future features must maintain existing correctness guarantees
2. **Maintain Security**: New features must not weaken security boundaries
3. **Incremental Evolution**: Features will be added incrementally with proper testing
4. **Clear Boundaries**: Web/LLM layers will be clearly separated from core engine

## Version Planning

- **v0.1.x**: CLI engine stabilization and correctness improvements
- **v0.2.x**: Core engine enhancements (if needed)
- **v1.0.0**: Stable CLI engine release
- **v2.0.0**: Web GUI integration (planned)
- **v3.0.0**: Multi-LLM framework (planned)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to current and planned features.

