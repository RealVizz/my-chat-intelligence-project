from datetime import datetime
from typing import List

from pydantic import BaseModel


# --- API Schemas ---
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


class ExternalMessageSchemaObj(BaseModel):
    """Schema for a single message from the external API."""
    id: str
    user_id: str
    user_name: str
    timestamp: datetime
    message: str


class ExternalMessagesResponseSchemaObj(BaseModel):
    """Schema for the paginated response from the external messages API."""
    total: int
    items: List[ExternalMessageSchemaObj]
