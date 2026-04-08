# copilot-orchestrator

`copilot-orchestrator` is the **Orchestration Layer** of a larger AI copilot system.

It sits above the Data Layer and is responsible for:
* receiving user requests
* understanding intent
* selecting retrieval strategy
* calling the data layer
* assembling grounded context
* generating responses
* handling fallback and low confidence
* managing session context
* routing basic actions
* exposing this logic to API, MCP, and CLI

It must remain:
* modular
* production-ready
* reusable
* independent of storage internals
* independent of frontend/UI concerns

---

# Responsibilities by Folder

## `.github/`
Contains CI/CD automation and release workflows (lint/typecheck/test/publish).

## `docs/`
Contains architecture, ADRs, contracts, and implementation roadmap.

## `scripts/`
Contains developer convenience scripts (bootstrap/setup/test wrappers).

## `tests/`
Contains all automated tests (unit/integration/e2e).

## `copilot_orchestrator/`
The main package root containing the reusable orchestration engine.

### `core/`
Shared foundational primitives (settings, logging, constants, exceptions, utilities).

### `domain/`
Pure business concepts, contracts, and abstractions (UserQuery, Session, interfaces/ports).
*Note: This layer has no dependencies on external frameworks or SDKs.*

### `application/`
Business logic and orchestration-independent use cases (services, use cases, DTOs).

### `orchestration/`
LangGraph-specific execution flow, state, nodes, and orchestration runtime logic.

### `infrastructure/`
Concrete implementations of external dependencies and adapters (LLM clients, retrieval clients, session stores, telemetry).

### `bootstrap/`
Dependency wiring, factories, and object construction (Dependency Injection).

### `presentation/`
Thin delivery interfaces (FastAPI API, CLI entrypoint, MCP server).

---

# Design Rules

1. **Keep nodes thin**: LangGraph nodes should orchestrate steps, not contain deep logic.
2. **Business logic in `application/`**: If logic is reusable outside the graph, it belongs here.
3. **External SDK logic in `infrastructure/`**: Providers (OpenAI, Redis, Langfuse) belong here.
4. **Presentation stays thin**: API, MCP, and CLI should adapt inputs/outputs only.
5. **Avoid dumping into `core/`**: Only truly cross-cutting concern belong here.
6. **Do not duplicate the Data Layer**: Call the data layer; do not recreate its ingestion or vector logic.
7. **Keep contracts explicit**: Prefer typed models and explicit interfaces over unstructured dicts.
