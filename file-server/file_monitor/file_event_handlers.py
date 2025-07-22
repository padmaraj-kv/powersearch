from typing_extensions import ParamSpecArgs
from .event_types import FileEventType
from .db import conn
from .store import FileStore, FileRecord
from .utils import generate_uuid
from datetime import datetime
from .push_to_index import push

def check_and_insert_file_by_path(path: str):
    try:
        print("[LOG] Checking if entry with the same path exists in DB...")
        existing = FileStore.read_by_path(path)
        if existing:
            print(f"[LOG] Entry already exists for path: {path}")
            return existing[0]  # Return the first matching record
        else:
            print(f"[LOG] No entry found for path: {path}. Inserting new record...")
            now = datetime.now()
            file_record = FileRecord(
                id=generate_uuid("file"),
                path=path,
                is_deleted=False,
                created_at=now,
                updated_at=now
            )
            FileStore.insert(file_record)
            print(f"[LOG] Inserted new file record for path: {path}")
            return file_record.dict()
    except Exception as e:
        print(f"[ERROR] Failed to check/insert file record: {e}")
        return None


def handle_modify(data: dict) -> None:
    path = data.get("path")
    if path:
        file = check_and_insert_file_by_path(path)
        if file:
            print(f"[LOG] File record found for path: {path}")
            print(f"[LOG] File record: {file}")
            push({
                "id": file["id"],
                "path": file["path"],
                }, "upsert")
        else:
            print("[LOG] No file record found for path: {path}")
    else:
        print("[LOG] No path found in event data")

def handle_move(data: dict) -> None:
    src_path = data.get("src_path")
    dest_path = data.get("dest_path")
    if not src_path or not dest_path:
        print("[LOG] src_path or dest_path missing in move event data")
        return
    print(f"[LOG] Moving file from {src_path} to {dest_path}")
    existing = FileStore.read_by_path(src_path)
    if not existing:
        print(f"[LOG] No file record found for src_path: {src_path}")
        return
    file_record = existing[0]
    print(f"[LOG] Existing file record: {file_record}")
    now = datetime.now()
    FileStore.update_path(file_record.id, dest_path, now)
    print(f"[LOG] Updated file record id {file_record.id} path to {dest_path}")

def handle_delete(data: dict) -> None:
    
    pass