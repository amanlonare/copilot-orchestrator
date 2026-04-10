# Changelog

All notable changes to this project will be documented in this file.

## v0.5.0 (2026-04-10)

### ✨ Orchestration & Graph
- **LangGraph Integration**: Established a production-ready `StateGraph` for cyclic orchestration and explicit flow control.
- **Typed Orchestrator State**: Implemented `OrchestratorState` using Python's `TypedDict` and domain-first entities for strict contract safety.
- **Thin Node Architecture**: Refactored orchestration logic into discrete service-delegating nodes (`intake`, `select_strategy`, `retrieve`, `assemble`, `generate`, `fallback`, `finalize`).
- **Dynamic Routing**: Implemented conditional branching for automatic fallback to generic responses when retrieval confidence is low.
- **Integration Testing**: Created a comprehensive test suite in `tests/integration/orchestration/` to verify end-to-end graph state transitions.
- **Quality Gates**: Achieved 100% compliance with `ruff` and `mypy` (strict mode) across the orchestration layer.


## v0.3.0 (2026-04-10)

### ✨ Infrastructure Adapters
- **OpenAI Adapter**: Implemented `LLMClient` port using `AsyncOpenAI` for gpt-4o-mini generation.
- **Data Retrieval**: Built `DataLayerClient` to handle external knowledge fetching across multiple modes (Vector, Keyword, Hybrid).
- **Session Persistence**: Added `InMemorySessionStore` for high-performance, asynchronous conversation history management.
- **Structured Telemetry**: Integrated `StructuredLogger` using `loguru` to provide cloud-native JSON observability.
- **Domain Ports**: Created `TelemetryClient` interface to decouple business logic from specific logging implementations.
- **Verification**: Established 100% unit test coverage and pre-commit verification for all new components.

## v0.2.0 (2026-04-09)

### ✨ Application Services
- **Use Case Orchestration**: Implemented `RunOrchestratorUseCase` to coordinate the full RAG pipeline (Intake → Retrieval → Fallback → Context → Generation).
- **Intake & Validation**: Added `QueryIntakeService` for request normalization and validation.
- **Session Management**: Built `SessionService` to handle asynchronous conversation history loading and persistence.
- **Retrieval Strategy**: Implemented `RetrievalStrategyService` for decoupled search mode selection (Vector, Keyword, or Hybrid).
- **Grounded Generation**: Developed `GenerationService` for context-aware response assembly and `FallbackService` for low-confidence scenarios.
- **Formatted Context**: Added `ContextBuilderService` to deduplicate and format retrieved snippets with source citations.

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
