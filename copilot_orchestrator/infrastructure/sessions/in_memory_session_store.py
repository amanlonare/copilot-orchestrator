import copy
import threading
from typing import Final

from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.ports.session_repository import SessionRepository


class InMemorySessionStore(SessionRepository):
    """Local, thread-safe in-memory storage for sessions.

    Used for development and testing. Data is lost on process restart.
    Implements deep-copy logic to simulate database boundaries.
    """

    def __init__(self) -> None:
        """Initialize empty storage with a reentrant lock."""
        self._store: dict[str, Session] = {}
        self._lock: Final[threading.RLock] = threading.RLock()

    async def load(self, session_id: str) -> Session | None:
        """Load a deep copy of the session from memory.

        Args:
            session_id: The ID of the session to retrieve.

        Returns:
            A cloned Session if exists, else None.
        """
        with self._lock:
            session = self._store.get(session_id)
            if session:
                return copy.deepcopy(session)
            return None

    async def save(self, session: Session) -> None:
        """Save a deep copy of the session.

        Args:
            session: The session to save.
        """
        with self._lock:
            self._store[session.session_id] = copy.deepcopy(session)

    async def update(self, session: Session) -> None:
        """Alias for save in this implementation.

        Args:
            session: The session object to update.
        """
        await self.save(session)
