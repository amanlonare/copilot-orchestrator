import json
import logging
from collections.abc import AsyncIterator, Generator
from contextlib import ExitStack, contextmanager
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langfuse import propagate_attributes
from opentelemetry import trace

from copilot_orchestrator.domain.entities.query import OrchestratorRequest, UserQuery
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.presentation.api.dependencies import get_orchestrator_graph, get_services
from copilot_orchestrator.presentation.api.schemas.request import ChatRequest
from copilot_orchestrator.presentation.api.schemas.response import ChatResponse, CitationModel

router = APIRouter(prefix="/chat", tags=["orchestration"])


@contextmanager
def _trace_context(session_id: str, user_id: str, query: str) -> Generator[None, None, None]:
    """Wrapper for propagate_attributes using ExitStack to satisfy static analysis."""
    with ExitStack() as stack:
        stack.enter_context(
            propagate_attributes(
                session_id=session_id,
                user_id=user_id,
                trace_name=f"Copilot: {query[:60]}",
            )
        )
        yield


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

        with _trace_context(
            session_id=request.session_id or "default-session",
            user_id=request.user_id or "anonymous",
            query=request.query,
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
            result = final_state["retrieved_result"]
            is_dict = isinstance(result, dict)
            items = result.get("items", []) if is_dict else getattr(result, "items", [])

            for c in items:
                # Safe access for both object and dict attributes
                def get_attr(obj: Any, attr: str) -> Any:
                    return obj.get(attr) if isinstance(obj, dict) else getattr(obj, attr, None)

                citations.append(
                    CitationModel(
                        source_id=get_attr(c, "source_id") or "unknown",
                        snippet=get_attr(c, "snippet") or "",
                        source_title=get_attr(c, "source_title"),
                        score=get_attr(c, "score"),
                    )
                )

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


def _get_citations_from_state(final_state: dict[str, Any]) -> list[dict[str, Any]]:
    """Safe extraction of citations from graph state."""
    citations: list[dict[str, Any]] = []
    if final_state.get("retrieved_result"):
        res = final_state["retrieved_result"]
        # Type safe access to items
        if isinstance(res, dict):
            res_items = res.get("items", [])
        else:
            res_items = getattr(res, "items", [])

        for c in res_items:
            if isinstance(c, dict):
                citations.append(
                    {
                        "source_id": c.get("source_id", "unknown"),
                        "snippet": c.get("snippet", ""),
                        "source_title": c.get("source_title"),
                    }
                )
            else:
                citations.append(
                    {
                        "source_id": getattr(c, "source_id", "unknown"),
                        "snippet": getattr(c, "snippet", ""),
                        "source_title": getattr(c, "source_title", None),
                    }
                )
    return citations


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    graph: Any = Depends(get_orchestrator_graph),  # noqa: B008
    services: dict[str, Any] = Depends(get_services),  # noqa: B008
) -> StreamingResponse:
    """Streamed endpoint for real-time interaction using Server-Sent Events (SSE).

    This endpoint multiplexes different event types (node progress, token content,
    terminal metadata) to provide a rich, interactive user experience.

    Args:
        request: Validated chat request.
        graph: The LangGraph instance.
        services: Application services for injection.

    Returns:
        A StreamingResponse yielding SSE events.
    """

    async def event_generator() -> AsyncIterator[str]:
        """Internal generator to stream LangGraph events as conformant SSE chunks."""
        # Setup (similar to sync chat)
        user_query = UserQuery(
            text=request.query,
            user_id=request.user_id,
            session_id=request.session_id,
            metadata=request.metadata,
        )
        initial_state = {
            "request": OrchestratorRequest(query=user_query),
            "session": Session(session_id=request.session_id or "default-stream"),
            "errors": [],
        }

        callbacks = []
        for client in services.get("_telemetry", []):
            handler = client.get_callback_handler()
            if handler:
                callbacks.append(handler)

        config = {
            "configurable": {**services, "thread_id": request.session_id or "default-stream"},
            "callbacks": callbacks,
            "metadata": {
                "langfuse_session_id": request.session_id or "default-stream",
                "langfuse_user_id": request.user_id or "anonymous",
            },
        }
        # Track final state for metadata delivery (initialize to initial state)
        final_state = initial_state

        # Use standard context manager to ensure Langfuse trace consistency for streaming
        with _trace_context(
            session_id=request.session_id or "default-stream",
            user_id=request.user_id or "anonymous",
            query=f"(Stream) {request.query}",
        ):
            try:
                # Use astream_events (v2) for multiplexing
                async for event in graph.astream_events(initial_state, config=config, version="v2"):
                    kind = event["event"]
                    name = event["name"]

                    # 1. Node Progress
                    if kind == "on_chain_start" and name == "LangGraph":
                        yield f"event: node\ndata: {json.dumps({'node': 'start'})}\n\n"

                    elif kind == "on_node_start":
                        node_data = json.dumps({"node": name, "status": "started"})
                        yield f"event: node\ndata: {node_data}\n\n"

                    # 2. Token Content (from generate_answer or format_action_response)
                    elif kind == "on_chat_model_stream":
                        content = event["data"].get("chunk", {}).content
                        if content:
                            yield f"event: content\ndata: {json.dumps({'chunk': content})}\n\n"

                    # Capture final state from completion events
                    if kind == "on_chain_end" and name == "LangGraph":
                        final_state = event["data"].get("output", {})

                # 3. Terminal Metadata
                metadata_payload = {
                    "citations": _get_citations_from_state(final_state),
                    "session_id": getattr(
                        final_state.get("session", initial_state["session"]),
                        "session_id",
                        "default",
                    ),
                    "fallback_flag": final_state.get("fallback_flag", False),
                    "trace_metadata": final_state.get("trace_metadata", {}),
                }
                yield f"event: metadata\ndata: {json.dumps(metadata_payload)}\n\n"

            except Exception as e:
                logging.error(f"Streaming failed: {e}")
                yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
