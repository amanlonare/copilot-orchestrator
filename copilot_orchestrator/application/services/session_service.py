import logging
from datetime import UTC, datetime

from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.ports.session_repository import SessionRepository

logger = logging.getLogger(__name__)


class SessionService:
    """Service to handle application-level orchestration for session persistence."""

    def __init__(self, repository: SessionRepository) -> None:
        """Initialize with a concrete repository implementation.

        Args:
            repository: Port for session persistence.
        """
        self._repository = repository

    async def load_session(self, session_id: str) -> Session:
        """Load an existing session or initialize a new one.

        Args:
            session_id: Unique identifier for the conversation.

        Returns:
            A Session entity.
        """
        logger.debug("Loading session: %s", session_id)
        session = await self._repository.load(session_id)

        if session is None:
            logger.info("Session %s not found. Initializing new session.", session_id)
            session = Session(session_id=session_id)
        else:
            logger.debug("Session %s loaded successfully.", session_id)

        return session

    async def append_and_save(self, session: Session, message: AgentMessage) -> None:
        """Append a message to a session and persist the state.

        Args:
            session: The session entity to update.
            message: The message to append to history.
        """
        logger.debug("Appending message to session: %s", session.session_id)

        session.history.append(message)
        session.updated_at = datetime.now(UTC)

        await self._repository.save(session)
        logger.info("Session %s saved successfully after message update.", session.session_id)
