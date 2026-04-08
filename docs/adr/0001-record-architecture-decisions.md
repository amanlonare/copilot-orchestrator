# ADR 0001: Foundational Architecture

## Status
Accepted

## Context
The `copilot-orchestrator` needs to manage complex, multi-step AI inference tasks while remaining easily testable and agnostic of specific infrastructure providers (OpenAI vs Anthropic, Redis vs SQL, etc.).

## Decision
We adopt **Layered Hexagonal Architecture** (Ports & Adapters) combined with **LangGraph** for orchestration.

- **Domain**: Pure business logic and interfaces.
- **Application**: Orchestration services and use cases.
- **Infrastructure**: Concrete adapters for external APIs.
- **Orchestration**: Stateful transitions via directed graphs.

## Consequences
- **Pros**: Easy to swap LLM providers; high testability; visualizable execution flow.
- **Cons**: Initial boilerplate overhead; higher learning curve for LangGraph.
