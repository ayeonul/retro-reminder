from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.setting import Setting
from app.schemas.setting import SettingsRead, SettingsUpdate


DEFAULT_ACCENT_COLOR = "#ffdbd9"
router = APIRouter(prefix="/settings", tags=["settings"])


def get_accent_color(db: Session) -> str:
    setting = db.get(Setting, "accent_color")
    return setting.value if setting else DEFAULT_ACCENT_COLOR


@router.get("", response_model=SettingsRead)
def get_settings(db: Session = Depends(get_db)) -> SettingsRead:
    return SettingsRead(accent_color=get_accent_color(db))


@router.patch("", response_model=SettingsRead)
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db)) -> SettingsRead:
    setting = db.get(Setting, "accent_color")
    if setting is None:
        setting = Setting(key="accent_color", value=payload.accent_color)
        db.add(setting)
    else:
        setting.value = payload.accent_color
    db.commit()
    return SettingsRead(accent_color=payload.accent_color)
