from typing import Optional
from pydantic import BaseModel


class QueryRequest(BaseModel):
    text: str
    limit: Optional[int] = 10


class QueryResponse(BaseModel):
    file_id: str
    file_path: str
    score: float


class UpsertRequest(BaseModel):
    file_id: str
    file_path: str


class UpsertResponse(BaseModel):
    message: str
    file_id: str
    status: str


class DeleteRequest(BaseModel):
    file_id: str
    file_path: str


class DeleteResponse(BaseModel):
    message: str
    file_id: str
    status: str
