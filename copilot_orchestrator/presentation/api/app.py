from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from copilot_orchestrator.presentation.api.routes import chat, health

app = FastAPI(
    title="Copilot Orchestrator API",
    description="Thin presentation layer for the LangGraph-based RAG orchestrator.",
    version="0.5.0",
)

# Standard CORS configuration for MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(chat.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root redirect or info endpoint."""
    return {"message": "Copilot Orchestrator API is running. See /docs for API documentation."}
