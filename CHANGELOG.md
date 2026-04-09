# Changelog

All notable changes to this project will be documented in this file.

## v0.1.0 (2026-04-09)

### ✨ Domain & Contracts
- **Core Entities**: Implemented all core data structures (`Action`, `Session`, `AgentMessage`, etc.) with strict type safety and detailed docstrings.
- **Granular Enums**: Standardized state management by refactoring enums into a dedicated `domain/enums/` package, introducing `ActionType` and `IntentType`.
- **Absolute Imports**: Standardized the codebase to use absolute imports across the domain layer to prevent circular dependencies and improve clarity.
- **Unit Testing**: Established verification baseline with comprehensive tests for entity logic and port protocols.

## v0.0.1 (2026-04-08)

### ✨ Initial Foundation
- **Hexagonal Architecture**: Established the core core/domain/application layer structure.
- **Dependency Management**: Integrated `uv` for lightning-fast, reproducible builds.
- **Quality Control**: Configured `ruff`, `mypy`, and `pre-commit` for consistent code standards.
- **Automated CI/CD**: Set up automated testing and semantic versioning through GitHub Actions.
- **Documentation**: Initial ADRs, README, and project guidelines created.
