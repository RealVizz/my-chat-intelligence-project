from datetime import datetime

from pydantic import BaseModel


class UserQueryRequest(BaseModel):
    """Schema for validating the user's incoming query."""
    question: str


class QueryResponse(BaseModel):
    """Schema for formatting the final answer response."""
    answer: str


class ChatMessageSchemaObj(BaseModel):
    """Schema for a single message in the chat history."""
    role: str
    content: str
    timestamp: datetime
