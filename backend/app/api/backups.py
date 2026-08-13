from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import DATA_DIRECTORY, DOWNLOADS_DIRECTORY
from app.core.database import engine
from app.services.backup import MAX_BACKUP_SIZE, create_backup_bytes, restore_backup


router = APIRouter(prefix="/backups", tags=["backups"])


@router.post("/export")
def export_backup() -> dict[str, str]:
    filename = f"reminder-backup-{datetime.now():%Y%m%d-%H%M%S}.db"
    backup_path = DOWNLOADS_DIRECTORY / filename
    backup_path.write_bytes(create_backup_bytes(engine))
    return {"filename": filename, "path": str(backup_path)}


@router.post("/import", status_code=status.HTTP_204_NO_CONTENT)
async def import_backup(file: UploadFile = File(...)) -> None:
    data = await file.read(MAX_BACKUP_SIZE + 1)
    try:
        restore_backup(engine, data, DATA_DIRECTORY)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
    finally:
        await file.close()
