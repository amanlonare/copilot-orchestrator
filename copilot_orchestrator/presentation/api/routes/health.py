from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["system"])


@router.get("")
async def get_health() -> dict[str, str]:
    """Basic healthcheck endpoint for liveness probes."""
    return {"status": "ok", "service": "copilot-orchestrator"}
