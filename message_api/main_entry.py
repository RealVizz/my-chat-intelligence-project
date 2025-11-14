import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from message_api import bg_sync_service
from message_api.schemas import UserQueryRequest, QueryResponse
from message_api.services import query_service
from message_api.utils import db_utils, rag_utils


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Handles application startup and shutdown events. """
    db_utils.initialize_database()
    rag_utils.initialize_rag()
    query_service.load_history_on_startup()
    query_service.load_identities_on_startup()
    asyncio.create_task(bg_sync_service.start_background_sync())
    yield


app = FastAPI(
    title="Message Intelligence Engine",
    description="API for answering questions about member data.",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/health", status_code=status.HTTP_200_OK)
def perform_health_check():
    """Performs a health check and returns the system's status."""
    return {"status": "ok"}


@app.post("/ask")
def handle_user_query(request: UserQueryRequest):
    """Accepts a user's question, processes it, and returns an answer."""
    answer_from_service = query_service.process_user_query(question=request.question)
    return QueryResponse(answer=answer_from_service)
