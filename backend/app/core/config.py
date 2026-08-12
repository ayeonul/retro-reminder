import os
from pathlib import Path


DATA_DIRECTORY = Path(
    os.getenv("REMINDER_DATA_DIRECTORY")
    or Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Reminder"
)
DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)


def default_database_url() -> str:
    return f"sqlite:///{(DATA_DIRECTORY / 'reminder.db').as_posix()}"


DATABASE_URL = os.getenv("REMINDER_DATABASE_URL", default_database_url())
