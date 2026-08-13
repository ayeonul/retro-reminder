from contextlib import asynccontextmanager
from pathlib import Path
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import backups, contacts, memos, schedules, settings
from app.core.database import Base, engine
from app.core.database import SessionLocal
from app.services.notifier import WindowsNotifier
from app.services.reminder import process_due_schedules
import app.models


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    scheduler = AsyncIOScheduler()
    notifier = WindowsNotifier()
    process_due_schedules(SessionLocal, notifier)
    scheduler.add_job(
        process_due_schedules,
        "cron",
        second=0,
        args=[SessionLocal, notifier],
        id="reminder-check",
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title="Reminder API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(memos.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(schedules.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(backups.router, prefix="/api")


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


frontend_directory = (
    Path(sys._MEIPASS) / "frontend" / "dist"
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parents[2] / "frontend" / "dist"
)
if frontend_directory.is_dir():
    app.mount("/", StaticFiles(directory=frontend_directory, html=True), name="frontend")
