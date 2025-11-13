from pydantic import BaseModel


class UserQueryRequest(BaseModel):
    """Schema for validating the user's incoming query."""
    question: str


class QueryResponse(BaseModel):
    """Schema for formatting the final answer response."""
    answer: str
