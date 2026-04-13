import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from langfuse import propagate_attributes
from opentelemetry import trace

from copilot_orchestrator.domain.entities.query import OrchestratorRequest, UserQuery
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.presentation.api.dependencies import get_orchestrator_graph, get_services
from copilot_orchestrator.presentation.api.schemas.request import ChatRequest
from copilot_orchestrator.presentation.api.schemas.response import ChatResponse, CitationModel

router = APIRouter(prefix="/chat", tags=["orchestration"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    graph: Any = Depends(get_orchestrator_graph),  # noqa: B008
    services: dict[str, Any] = Depends(get_services),  # noqa: B008
) -> ChatResponse:
    """Primary endpoint for conversational interaction with the copilot.

    Validates the incoming schema, maps to domain Request/Session objects,
    and executes the LangGraph orchestration flow.
    """
    logging.info(
        f"Received chat request: session_id={request.session_id}, user_id={request.user_id}"
    )

    # Honeycomb deep visibility: attach metadata to current request span
    span = trace.get_current_span()
    span.set_attribute("app.session_id", request.session_id or "default")
    span.set_attribute("app.user_id", request.user_id or "anonymous")
    span.set_attribute("app.query", request.query[:200])

    try:
        # 1. Map External Request to Domain entities
        # Note: In a production app, we would load the session from the SessionService here
        # but for Phase 6 MVP, we initialize a shell session or let the graph handle loading.
        user_query = UserQuery(
            text=request.query,
            user_id=request.user_id,
            session_id=request.session_id,
            metadata=request.metadata,
        )
        orchestrator_request = OrchestratorRequest(query=user_query)

        # 2. Prepare Initial State
        initial_state = {
            "request": orchestrator_request,
            "session": Session(session_id=request.session_id or "default-session"),
            "errors": [],
            "warnings": [],
        }

        # 3. Collect Telemetry Callbacks
        callbacks = []
        for client in services.get("_telemetry", []):
            handler = client.get_callback_handler()
            if handler:
                callbacks.append(handler)

        # 4. Execute Graph
        # We pass the application services via the 'configurable' key in LangGraph config
        config = {
            "configurable": {**services, "thread_id": request.session_id or "default-session"},
            "callbacks": callbacks,
            "metadata": {
                "langfuse_session_id": request.session_id or "default-session",
                "langfuse_user_id": request.user_id or "anonymous",
            },
        }

        with propagate_attributes(
            session_id=request.session_id or "default-session",
            user_id=request.user_id or "anonymous",
            trace_name=f"Copilot: {request.query[:60]}",
        ):
            final_state = await graph.ainvoke(initial_state, config=config)

        # 4. Handle Failures in state
        if final_state.get("errors"):
            raise HTTPException(status_code=500, detail=f"Graph Error: {final_state['errors'][0]}")

        # 5. Map internal State back to External Response
        answer_content = "I'm sorry, I couldn't generate a response."
        if final_state.get("answer"):
            answer_content = final_state["answer"].content

        citations = []
        if final_state.get("retrieved_result"):
            citations = [
                CitationModel(
                    source_id=c.source_id,
                    snippet=c.snippet,
                    source_title=c.source_title,
                    score=c.score,
                )
                for c in final_state["retrieved_result"].items
            ]

        # 5. Extract Trace IDs for metadata
        trace_metadata = dict(final_state.get("trace_metadata", {}))
        for handler in callbacks:
            # Langfuse specific trace ID extraction
            if hasattr(handler, "last_trace_id") and handler.last_trace_id:
                trace_metadata["langfuse_trace_id"] = handler.last_trace_id

        return ChatResponse(
            answer=answer_content,
            citations=citations,
            fallback_flag=final_state.get("fallback_flag", False),
            session_id=final_state["session"].session_id,
            trace_metadata=trace_metadata,
        )

    except Exception as e:
        # Presentation layer catch-all
        raise HTTPException(status_code=500, detail=str(e)) from e
