import sqlite3
import threading
from datetime import datetime
from pathlib import Path

from sqlalchemy.engine import Engine


DATABASE_LOCK = threading.RLock()
REQUIRED_TABLES = {"memos", "contacts", "schedules", "settings"}
MAX_BACKUP_SIZE = 50 * 1024 * 1024


def _source_connection(engine: Engine):
    connection = engine.raw_connection()
    return connection, connection.driver_connection


def create_backup_bytes(engine: Engine) -> bytes:
    with DATABASE_LOCK:
        raw_connection, source = _source_connection(engine)
        destination = sqlite3.connect(":memory:")
        try:
            source.backup(destination)
            return destination.serialize()
        finally:
            destination.close()
            raw_connection.close()


def validate_backup(data: bytes) -> sqlite3.Connection:
    if not data or len(data) > MAX_BACKUP_SIZE:
        raise ValueError("백업 파일 크기가 올바르지 않습니다.")

    source = sqlite3.connect(":memory:")
    try:
        source.deserialize(data)
        integrity = source.execute("PRAGMA integrity_check").fetchone()[0]
        tables = {
            row[0]
            for row in source.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        }
        if integrity != "ok" or not REQUIRED_TABLES.issubset(tables):
            raise ValueError("Reminder 백업 파일이 아니거나 손상되었습니다.")
        return source
    except Exception:
        source.close()
        raise


def save_safety_backup(engine: Engine, data_directory: Path) -> Path:
    backup_directory = data_directory / "backups"
    backup_directory.mkdir(parents=True, exist_ok=True)
    backup_path = backup_directory / f"pre-restore-{datetime.now():%Y%m%d-%H%M%S}.db"
    backup_path.write_bytes(create_backup_bytes(engine))
    return backup_path


def restore_backup(engine: Engine, data: bytes, data_directory: Path) -> Path:
    source = validate_backup(data)
    try:
        with DATABASE_LOCK:
            safety_backup = save_safety_backup(engine, data_directory)
            raw_connection, destination = _source_connection(engine)
            try:
                source.backup(destination)
            finally:
                raw_connection.close()
        return safety_backup
    finally:
        source.close()
