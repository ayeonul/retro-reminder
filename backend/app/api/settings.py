from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.setting import Setting
from app.schemas.setting import SettingsRead, SettingsUpdate


DEFAULT_ACCENT_COLOR = "#ffdbd9"
DEFAULT_PIXEL_FONT_ENABLED = True
router = APIRouter(prefix="/settings", tags=["settings"])


def get_accent_color(db: Session) -> str:
    setting = db.get(Setting, "accent_color")
    return setting.value if setting else DEFAULT_ACCENT_COLOR


def get_pixel_font_enabled(db: Session) -> bool:
    setting = db.get(Setting, "pixel_font_enabled")
    return setting.value.lower() == "true" if setting else DEFAULT_PIXEL_FONT_ENABLED


def set_setting(db: Session, key: str, value: str) -> None:
    setting = db.get(Setting, key)
    if setting is None:
        db.add(Setting(key=key, value=value))
    else:
        setting.value = value


@router.get("", response_model=SettingsRead)
def get_settings(db: Session = Depends(get_db)) -> SettingsRead:
    return SettingsRead(
        accent_color=get_accent_color(db),
        pixel_font_enabled=get_pixel_font_enabled(db),
    )


@router.patch("", response_model=SettingsRead)
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db)) -> SettingsRead:
    if payload.accent_color is not None:
        set_setting(db, "accent_color", payload.accent_color)
    if payload.pixel_font_enabled is not None:
        set_setting(db, "pixel_font_enabled", str(payload.pixel_font_enabled).lower())
    db.commit()
    return get_settings(db)
