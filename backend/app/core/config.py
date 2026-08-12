import os
from pathlib import Path


def default_database_url() -> str:
    data_directory = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Reminder"
    data_directory.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{(data_directory / 'reminder.db').as_posix()}"


DATABASE_URL = os.getenv("REMINDER_DATABASE_URL", default_database_url())
