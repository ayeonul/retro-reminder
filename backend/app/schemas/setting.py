from pydantic import BaseModel, Field


class SettingsRead(BaseModel):
    accent_color: str


class SettingsUpdate(BaseModel):
    accent_color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
