import logging
from datetime import datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.models.schedule import Schedule
from app.services.backup import DATABASE_LOCK


logger = logging.getLogger(__name__)
class Notifier(Protocol):
    def send(self, title: str, message: str) -> bool:
        pass


def process_due_schedules(
    session_factory: sessionmaker[Session],
    notifier: Notifier,
    now: datetime | None = None,
) -> int:
    checked_at = now or datetime.now()
    current_minute = checked_at.replace(second=0, microsecond=0)
    sent_count = 0

    with DATABASE_LOCK:
        with session_factory() as db:
            schedules = db.scalars(
                select(Schedule)
                .where(Schedule.alert_enabled.is_(True), Schedule.notified_at.is_(None))
                .order_by(Schedule.date, Schedule.time, Schedule.id)
            )

            for schedule in schedules:
                if schedule.time is None:
                    continue
                due_at = datetime.combine(schedule.date, schedule.time)
                if due_at.replace(second=0, microsecond=0) != current_minute:
                    continue
                if notifier.send("Reminder", f"{schedule.title} · {schedule.time.strftime('%H:%M')}"):
                    schedule.notified_at = checked_at
                    sent_count += 1

            db.commit()

    if sent_count:
        logger.info("리마인더 %s건을 발송했습니다.", sent_count)
    return sent_count
