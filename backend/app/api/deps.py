from sqlalchemy.orm import Session

from app.core.database import get_db


DbSession = Session

__all__ = ["DbSession", "get_db"]
