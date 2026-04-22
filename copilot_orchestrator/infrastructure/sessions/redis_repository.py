from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from redis.asyncio import Redis

from copilot_orchestrator.domain.entities.citation import Citation
from copilot_orchestrator.domain.entities.message import AgentMessage
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.domain.entities.token_usage import TokenUsage
from copilot_orchestrator.domain.enums.message_role import MessageRole


class RedisSessionRepository:
    """Redis-backed implementation of SessionRepository."""

    def __init__(self, redis_client: Redis[str], prefix: str = "session:"):
        """Initialize with a redis client and optional prefix.

        Args:
            redis_client: An authenticated redis.asyncio client.
            prefix: Key prefix for session storage.
        """
        self.redis = redis_client
        self.prefix = prefix

    def _get_key(self, session_id: str) -> str:
        return f"{self.prefix}{session_id}"

    async def load(self, session_id: str) -> Session | None:
        """Load session from Redis.

        Args:
            session_id: The ID of the session to load.

        Returns:
            The Session object or None if not found.
        """
        data = await self.redis.get(self._get_key(session_id))
        if not data:
            return None

        raw_session = json.loads(data)

        # Reconstruct Session from raw dictionary
        history = []
        for msg_data in raw_session.get("history", []):
            citations = [Citation(**c) for c in msg_data.get("citations", [])]
            history.append(
                AgentMessage(
                    role=MessageRole(msg_data["role"]),
                    content=msg_data["content"],
                    citations=citations,
                    name=msg_data.get("name"),
                    metadata=msg_data.get("metadata", {}),
                )
            )

        usage_data = raw_session.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        return Session(
            session_id=raw_session["session_id"],
            history=history,
            usage=usage,
            metadata=raw_session.get("metadata", {}),
            created_at=datetime.fromisoformat(raw_session["created_at"]),
            updated_at=datetime.fromisoformat(raw_session["updated_at"]),
        )

    async def save(self, session: Session) -> None:
        """Save session to Redis as JSON.

        Args:
            session: The session object to persist.
        """

        # Manual serialization because of nested dataclasses and MessageRole enum
        def _serialize_msg(msg: AgentMessage) -> dict[str, Any]:
            return {
                "role": msg.role.value if hasattr(msg.role, "value") else msg.role,
                "content": msg.content,
                "citations": [
                    {
                        "source_id": c.source_id,
                        "snippet": c.snippet,
                        "source_title": c.source_title,
                        "score": c.score,
                        "url": c.url,
                        "metadata": c.metadata,
                    }
                    for c in msg.citations
                ],
                "name": msg.name,
                "metadata": msg.metadata,
            }

        data = {
            "session_id": session.session_id,
            "history": [_serialize_msg(m) for m in session.history],
            "usage": {
                "prompt_tokens": session.usage.prompt_tokens,
                "completion_tokens": session.usage.completion_tokens,
                "total_tokens": session.usage.total_tokens,
            },
            "metadata": session.metadata,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
        }

        await self.redis.set(self._get_key(session.session_id), json.dumps(data))
