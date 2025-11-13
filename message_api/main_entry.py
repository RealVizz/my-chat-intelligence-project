from fastapi import FastAPI, status

from message_api.schemas import UserQueryRequest, QueryResponse
from message_api.services import query_service

app = FastAPI(
    title="Message Intelligence Engine",
    description="API for answering questions about member data.",
    version="0.1.0",
)


@app.get("/health", status_code=status.HTTP_200_OK)
def perform_health_check():
    """
    Performs a health check and returns the system's status.
    """
    return {"status": "ok"}


@app.post("/ask")
def handle_user_query(request: UserQueryRequest):
    """Accepts a user's question, processes it, and returns an answer."""
    answer_from_service = query_service.process_user_query(question=request.question)
    return QueryResponse(answer=answer_from_service)
