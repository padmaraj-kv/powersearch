from typing import Optional
from pydantic import BaseModel, Field

from constants import DEFAULT_QUERY_LIMIT, MAX_QUERY_LIMIT


class QueryRequest(BaseModel):
    text: str = Field(
        ..., min_length=1, max_length=1000, description="Search query text"
    )
    limit: Optional[int] = Field(
        default=DEFAULT_QUERY_LIMIT,
        ge=1,
        le=MAX_QUERY_LIMIT,
        description=f"Maximum number of results to return (1-{MAX_QUERY_LIMIT})",
    )


class QueryResponse(BaseModel):
    file_id: str = Field(..., description="Unique file identifier")
    file_path: str = Field(..., description="Path to the file")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")


class UpsertRequest(BaseModel):
    file_id: str = Field(..., min_length=1, description="Unique file identifier")
    file_path: str = Field(..., min_length=1, description="Path to the file to index")


class UpsertResponse(BaseModel):
    message: str = Field(..., description="Success message")
    file_id: str = Field(..., description="File identifier that was processed")
    status: str = Field(..., description="Operation status: 'created' or 'updated'")


class DeleteRequest(BaseModel):
    file_id: str = Field(
        ..., min_length=1, description="Unique file identifier to delete"
    )


class DeleteResponse(BaseModel):
    message: str = Field(..., description="Success message")
    file_id: str = Field(..., description="File identifier that was deleted")
    status: str = Field(..., description="Operation status")


class HealthResponse(BaseModel):
    message: str = Field(..., description="Status message")
    version: str = Field(..., description="API version")
    status: str = Field(..., description="Health status")
