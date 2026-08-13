from pydantic import BaseModel, Field


class SettingsRead(BaseModel):
    accent_color: str
    pixel_font_enabled: bool


class SettingsUpdate(BaseModel):
    accent_color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    pixel_font_enabled: bool | None = None
