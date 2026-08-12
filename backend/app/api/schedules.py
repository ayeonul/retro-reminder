from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleRead, ScheduleUpdate


router = APIRouter(prefix="/schedules", tags=["schedules"])


def get_schedule_or_404(schedule_id: int, db: Session) -> Schedule:
    schedule = db.get(Schedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일정을 찾을 수 없습니다.")
    return schedule


@router.get("", response_model=list[ScheduleRead])
def list_schedules(
    date_value: date | None = Query(default=None, alias="date"),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
) -> list[Schedule]:
    if date_value and (date_from or date_to):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="date와 from/to는 함께 사용할 수 없습니다.")
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="from은 to보다 늦을 수 없습니다.")

    statement = select(Schedule)
    if date_value:
        statement = statement.where(Schedule.date == date_value)
    if date_from:
        statement = statement.where(Schedule.date >= date_from)
    if date_to:
        statement = statement.where(Schedule.date <= date_to)
    return list(db.scalars(statement.order_by(Schedule.date, Schedule.time, Schedule.id)))


@router.post("", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
def create_schedule(payload: ScheduleCreate, db: Session = Depends(get_db)) -> Schedule:
    schedule = Schedule(**payload.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.patch("/{schedule_id}", response_model=ScheduleRead)
def update_schedule(schedule_id: int, payload: ScheduleUpdate, db: Session = Depends(get_db)) -> Schedule:
    schedule = get_schedule_or_404(schedule_id, db)
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(schedule, field, value)
    if {"date", "time", "alert_enabled"}.intersection(changes):
        schedule.notified_at = None
    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)) -> None:
    db.delete(get_schedule_or_404(schedule_id, db))
    db.commit()
