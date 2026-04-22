# Changelog

All notable changes to this project will be documented in this file.
 
## v0.8.0 (2026-04-22)
 
### ✨ Multi-Action & Conversational Enhanced
- **Multi-Action Resolution**: Refactored the orchestration graph to support resolving and executing multiple tool-driven actions in a single turn (e.g., product searches across categories).
- **Conversational Greetings**: Implemented a dedicated `generate_greeting` path for `IntentType.GREETING` queries, ensuring friendly, persona-driven responses instead of empty results.
- **Enhanced Streaming Visibility**: Updated the `/chat/stream` endpoint to yield real-time `node` status events (intake, resolve, execute, etc.) and guaranteed delivery of final answer bodies for non-streaming nodes.
- **Session Persistence Fix**: Resolved a critical `500 AttributeError` in the `RedisSessionRepository` caused by inconsistent serialization of AI message roles.
- **Robust Integration Testing**: Added a full suite of pipeline tests for greeting resolution and multi-action tool execution.
 

## v0.7.0 (2026-04-13)

### ✨ Quality, Observability & Stability
- **Node-Level Tracing**: Implemented a `traced_node` decorator in `graph.py` to provide immediate terminal visibility into LangGraph node transitions and output keys.
- **Configurable RAG Threshold**: Introduced `RAG_RELEVANCE_THRESHOLD` in global settings and `.env`, allowing dynamic control over the grounded answer vs. fallback decision logic.
- **MCP Connectivity Fix**: Resolved a critical lifecycle issue where the `client_session` was not being correctly injected into the `MCPRetrieverGateway` across the graph nodes.
- **Better Diagnostics**: Enhanced `FallbackService` logging to output real-time relevance scores and comparison thresholds, simplifying the tuning process.
- **Improved Retrieval Confidence**: Refactored `evaluate_fallback` logic to support highly granular relevance scores (e.g., < 0.1) often returned by RAG search engines.


## v0.6.0 (2026-04-10)

### ✨ Presentation Layer
- **FastAPI Core**: Implemented a robust API server with `/chat` for orchestration and `/health` for diagnostics.
- **Interactive CLI**: Built a high-fidelity CLI using `rich` with streaming placeholders and formatted citation blocks.
- **MCP Integration**: Developed `MCPRetrieverGateway` to interface with the external Data Layer Manager via the Model Context Protocol.
- **Environment Parity**: Added `RETRIEVER_TYPE` branching to support both mocked local development and live MCP-powered integration.
- **Extensive Coverage**: Achieved baseline verification for all presentation components with unit tests for API and CLI layers.
- **DevEx Tooling**: Configured `uv` with new presentation-layer dependencies for streamlined builds.

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
