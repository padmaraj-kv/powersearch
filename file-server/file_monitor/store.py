from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .db import conn
from pypika import Query, Table

# Pydantic model for validation
class FileRecord(BaseModel):
    id: str
    path: str
    is_deleted: Optional[bool] = False
    created_at: datetime
    updated_at: datetime

files = Table('files')

class FileStore:
    @staticmethod
    def insert(file: FileRecord):
        q = Query.into(files).columns(
            'id', 'path', 'is_deleted', 'created_at', 'updated_at'
        ).insert(
            file.id, file.path, file.is_deleted, file.created_at, file.updated_at
        )
        sql = q.get_sql()
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()

    @staticmethod
    def delete(file_id: str):
        q = Query.update(files).set(files.is_deleted, True).where(files.id == file_id)
        sql = q.get_sql()
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()

    @staticmethod
    def update_path(file_id: str, new_path: str, updated_at: datetime):
        q = Query.update(files).set(
            files.path, new_path
        ).set(
            files.updated_at, updated_at
        ).where(files.id == file_id)
        sql = q.get_sql()
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()

    @staticmethod
    def read_by_path(path: str):
        q = Query.from_(files).select('*').where(files.path == path)
        sql = q.get_sql()
        with conn.cursor() as cur:
            cur.execute(sql)
            results = cur.fetchall()
        # Validate each result using FileRecord
        return [FileRecord(**row) for row in results] 