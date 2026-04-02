"""
repositories/json_repository.py
--------------------------------
Concrete repository that stores data in a JSON file on disk.

KEY RESPONSIBILITIES:
  - Read the JSON file on every operation (so restarts don't lose data)
  - Write atomically using filelock to prevent corruption during concurrent requests
  - Auto-create the JSON file with an empty structure if it doesn't exist
  - Auto-increment IDs like a simple database sequence

CONCURRENCY SAFETY:
  FastAPI runs on an async event loop but uvicorn can serve multiple
  requests simultaneously. Without a file lock, two requests writing at
  the same time could produce a corrupted JSON file (partial writes).
  FileLock ensures only one writer accesses the file at a time.

ATOMIC WRITE PATTERN:
  We write to a temp file first, then rename it over the real file.
  A rename is atomic on most operating systems — readers always see
  either the old file or the new file, never a half-written one.

LSP: This class fully implements BaseRepository. Any service that
     accepts a BaseRepository will work correctly with this class.
"""

import json
import os
import tempfile
from typing import Any, Dict, List, Optional
from filelock import FileLock
from repositories.base_repository import BaseRepository
from exceptions.custom_exceptions import StorageError
import logging

logger = logging.getLogger(__name__)


class JSONRepository(BaseRepository):
    """
    Generic JSON-file-backed repository.

    Args:
        file_path  : Path to the JSON file (e.g. "data/tasks.json")
        collection : Key inside the JSON root object (e.g. "tasks")

    The JSON file looks like:
        { "tasks": [ {...}, {...} ] }
    The collection name tells us which list to read/write.
    """

    def __init__(self, file_path: str, collection: str):
        self.file_path = file_path
        self.collection = collection
        # Lock file lives alongside the data file
        self.lock_path = file_path + ".lock"
        # Ensure directories and the JSON file exist at startup
        self._ensure_file_exists()

    # ── Internal helpers ──────────────────────────────────────────────

    def _ensure_file_exists(self) -> None:
        """Create the data file and its parent directories if missing."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            self._write_data({self.collection: []})
            logger.info(f"Created new storage file: {self.file_path}")

    def _read_data(self) -> Dict[str, Any]:
        """
        Read and parse the JSON file.
        If the file is empty or corrupted, reset it gracefully.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {self.collection: []}
                return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted JSON in {self.file_path}: {e}. Resetting.")
            self._write_data({self.collection: []})
            return {self.collection: []}
        except OSError as e:
            raise StorageError(f"Cannot read {self.file_path}: {e}")

    def _write_data(self, data: Dict[str, Any]) -> None:
        """
        Write data to the JSON file using an atomic temp-file rename.
        The FileLock prevents concurrent writers from corrupting the file.
        """
        lock = FileLock(self.lock_path, timeout=5)
        try:
            with lock:
                # Write to a sibling temp file in the same directory
                dir_name = os.path.dirname(self.file_path)
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=dir_name,
                    delete=False,
                    suffix=".tmp"
                ) as tmp:
                    json.dump(data, tmp, indent=2, default=str)
                    tmp_path = tmp.name
                # Atomic rename: replaces the real file instantly
                os.replace(tmp_path, self.file_path)
        except Exception as e:
            raise StorageError(f"Cannot write {self.file_path}: {e}")

    def _get_next_id(self, records: List[Dict[str, Any]]) -> int:
        """Return max(existing IDs) + 1, or 1 if the list is empty."""
        if not records:
            return 1
        return max(r["id"] for r in records) + 1

    # ── BaseRepository interface implementation ───────────────────────

    def find_all(self) -> List[Dict[str, Any]]:
        data = self._read_data()
        return data.get(self.collection, [])

    def find_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        records = self.find_all()
        # Linear scan — acceptable for JSON file storage at this scale
        for record in records:
            if record["id"] == record_id:
                return record
        return None

    def save(self, record_data):
        data = self._read_data()
        records = data.get(self.collection, [])
        record_data["id"] = self._get_next_id(records)
        records.append(record_data)
        data[self.collection] = records
        self._write_data(data)          # lock is INSIDE here
        logger.info(...)
        return record_data

    def update(self, record_id, updated_data):
        data = self._read_data()
        records = data.get(self.collection, [])
        for i, record in enumerate(records):
            if record["id"] == record_id:
                updated_data["id"] = record_id
                records[i] = updated_data
                data[self.collection] = records
                self._write_data(data)  # lock is INSIDE here
                logger.info(...)
                return records[i]
        return None

    def delete(self, record_id):
        data = self._read_data()
        records = data.get(self.collection, [])
        original_count = len(records)
        records = [r for r in records if r["id"] != record_id]
        if len(records) == original_count:
            return False
        data[self.collection] = records
        self._write_data(data)          # lock is INSIDE here
        logger.info(...)
        return True
