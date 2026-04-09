from typing import Protocol, runtime_checkable

from copilot_orchestrator.domain.entities.session import Session


@runtime_checkable
class SessionRepository(Protocol):
    """Contract for session persistence.

    Implementations (e.g., Redis, PostgreSQL, CosmosDB) must ensure
    consistent state across concurrent requests.
    """

    async def load(self, session_id: str) -> Session | None:
        """Load a session state by ID.

        Args:
            session_id: The unique identifier for the conversation session.

        Returns:
            The Session object if found, otherwise None.
        """
        ...

    async def save(self, session: Session) -> None:
        """Persist a modified session state.

        Args:
            session: The session object containing new messages or usage data.
        """
        ...
