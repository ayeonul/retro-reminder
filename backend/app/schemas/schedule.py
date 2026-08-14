from datetime import date as Date, datetime, time as Time

from pydantic import BaseModel, ConfigDict, Field


class ScheduleCreate(BaseModel):
    date: Date
    time: Time | None = None
    title: str = Field(min_length=1, max_length=200)
    alert_enabled: bool = False


class ScheduleUpdate(BaseModel):
    date: Date | None = None
    time: Time | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    alert_enabled: bool | None = None


class ScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: Date
    time: Time | None
    title: str
    alert_enabled: bool
    notified_at: datetime | None
    created_at: datetime
    updated_at: datetime
