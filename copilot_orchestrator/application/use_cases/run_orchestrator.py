import logging
from collections.abc import Mapping
from typing import Any

from copilot_orchestrator.application.services.context_builder_service import ContextBuilderService
from copilot_orchestrator.application.services.fallback_service import FallbackService
from copilot_orchestrator.application.services.generation_service import GenerationService
from copilot_orchestrator.application.services.query_intake_service import QueryIntakeService
from copilot_orchestrator.application.services.retrieval_strategy_service import (
    RetrievalStrategyService,
)
from copilot_orchestrator.application.services.session_service import SessionService
from copilot_orchestrator.domain.entities.orchestration_result import OrchestrationResult

logger = logging.getLogger(__name__)


class RunOrchestratorUseCase:
    """The main application entry point coordinating the orchestration flow."""

    def __init__(
        self,
        intake_service: QueryIntakeService,
        session_service: SessionService,
        retrieval_service: RetrievalStrategyService,
        context_service: ContextBuilderService,
        generation_service: GenerationService,
        fallback_service: FallbackService,
    ) -> None:
        self._intake = intake_service
        self._session = session_service
        self._retrieval = retrieval_service
        self._context = context_service
        self._generation = generation_service
        self._fallback = fallback_service

    async def execute(
        self,
        session_id: str,
        raw_query: str,
        user_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> OrchestrationResult:
        """Execute the full orchestration pipeline.

        Args:
            session_id: The ID for the conversation session.
            raw_query: The raw query from the user.
            user_id: Optional user identifier.
            metadata: Extra request metadata.

        Returns:
            The final OrchestrationResult containing the answer and citations.
        """
        logger.info("Executing orchestration for session: %s", session_id)

        try:
            # 1. Intake and Validation
            user_query = self._intake.process(
                raw_query=raw_query, session_id=session_id, user_id=user_id, metadata=metadata
            )

            # 2. Session Management
            session = await self._session.load_session(session_id)

            # 3. Retrieval
            retrieval_result = await self._retrieval.retrieve_for_query(user_query)

            # 4. Fallback Decision
            is_fallback = self._fallback.evaluate_fallback(retrieval_result.items)

            # 5. Context Building
            context_text = self._context.build_context(retrieval_result.items)

            # 6. Answer Generation
            agent_message = await self._generation.generate_answer(
                context=context_text, query=user_query, session=session
            )

            # 7. Persistence
            await self._session.append_and_save(session, agent_message)

            # 8. Result Assembly
            result = OrchestrationResult(
                answer=agent_message.content,
                citations=retrieval_result.items,
                fallback=is_fallback,
                metadata={
                    "session_id": session_id,
                    "retrieval_mode": retrieval_result.mode,
                    "latency_ms": retrieval_result.latency_ms,
                },
            )

            logger.info("Orchestration execute successful for session: %s", session_id)
            return result

        except Exception:
            logger.exception("Orchestration failed for session: %s", session_id)
            # In a real app, we might wrap this in a custom ApplicationError
            raise
