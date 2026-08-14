import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, inspect, text


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
test_database = Path(tempfile.gettempdir()) / "reminder_api_test.db"
if test_database.exists():
    test_database.unlink()
os.environ["REMINDER_DATABASE_URL"] = f"sqlite:///{test_database.as_posix()}"
os.environ["REMINDER_DATA_DIRECTORY"] = str(Path(tempfile.gettempdir()) / "reminder_api_test_data")
os.environ["REMINDER_DOWNLOADS_DIRECTORY"] = str(Path(tempfile.gettempdir()) / "reminder_api_test_downloads")

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.services.reminder import process_due_schedules
from app.core.migrations import migrate_schedule_time_column


def test_api_crud_flow():
    with TestClient(app) as client:
        assert client.get("/api/health").json() == {"status": "ok"}

        memo = client.post("/api/memos", json={"title": "회의", "content": "오후 2시"})
        assert memo.status_code == 201
        memo_id = memo.json()["id"]
        assert client.patch(f"/api/memos/{memo_id}", json={"title": "회의 변경"}).json()["title"] == "회의 변경"
        assert len(client.get("/api/memos").json()) == 1

        contact = client.post("/api/contacts", json={"name": "홍길동", "phone": "010-1234-5678", "memo": "팀장"})
        assert contact.status_code == 201
        contact_id = contact.json()["id"]
        assert len(client.get("/api/contacts", params={"query": "1234"}).json()) == 1
        assert client.patch(f"/api/contacts/{contact_id}", json={"memo": "변경"}).json()["memo"] == "변경"

        schedule = client.post(
            "/api/schedules",
            json={"date": "2026-08-12", "time": "09:00:00", "title": "일정", "alert_enabled": True},
        )
        assert schedule.status_code == 201
        schedule_id = schedule.json()["id"]
        assert len(client.get("/api/schedules", params={"from": "2026-08-01", "to": "2026-08-31"}).json()) == 1
        assert client.patch(f"/api/schedules/{schedule_id}", json={"alert_enabled": False}).json()["alert_enabled"] is False

        settings = client.get("/api/settings").json()
        assert settings["accent_color"] == "#ffdbd9"
        assert settings["pixel_font_enabled"] is True
        updated_settings = client.patch(
            "/api/settings",
            json={"accent_color": "#123abc", "pixel_font_enabled": False},
        ).json()
        assert updated_settings == {"accent_color": "#123abc", "pixel_font_enabled": False}

        assert client.delete(f"/api/memos/{memo_id}").status_code == 204
        assert client.delete(f"/api/contacts/{contact_id}").status_code == 204
        assert client.delete(f"/api/schedules/{schedule_id}").status_code == 204


def test_reminder_marks_a_sent_schedule():
    class FakeNotifier:
        def __init__(self):
            self.messages = []

        def send(self, title: str, message: str) -> bool:
            self.messages.append((title, message))
            return True

    now = datetime.now().replace(microsecond=0)
    with TestClient(app) as client:
        schedule = client.post(
            "/api/schedules",
            json={
                "date": now.date().isoformat(),
                "time": now.time().isoformat(),
                "title": "알림 테스트",
                "alert_enabled": True,
            },
        )
        schedule_id = schedule.json()["id"]
        notifier = FakeNotifier()

        assert process_due_schedules(SessionLocal, notifier, now=now) == 1
        assert notifier.messages == [("Reminder", f"알림 테스트 · {now.strftime('%H:%M')}")]
        assert client.get("/api/schedules", params={"date": now.date().isoformat()}).json()[0]["notified_at"]
        assert process_due_schedules(SessionLocal, notifier, now=now) == 0
        assert client.delete(f"/api/schedules/{schedule_id}").status_code == 204


def test_reminder_does_not_send_a_past_schedule():
    class FakeNotifier:
        def send(self, title: str, message: str) -> bool:
            raise AssertionError("지난 일정은 알림을 보내면 안 됩니다.")

    now = datetime(2026, 8, 13, 14, 45)
    with TestClient(app) as client:
        schedule = client.post(
            "/api/schedules",
            json={
                "date": "2026-08-13",
                "time": "09:00:00",
                "title": "지난 일정",
                "alert_enabled": True,
            },
        )
        schedule_id = schedule.json()["id"]

        assert process_due_schedules(SessionLocal, FakeNotifier(), now=now) == 0
        assert client.get("/api/schedules", params={"date": "2026-08-13"}).json()[0]["notified_at"] is None
        assert client.delete(f"/api/schedules/{schedule_id}").status_code == 204


def test_backup_export_and_import():
    with TestClient(app) as client:
        client.post("/api/memos", json={"title": "백업 대상", "content": "보존할 내용"})
        exported = client.post("/api/backups/export")
        assert exported.status_code == 200
        exported_path = Path(exported.json()["path"])
        assert exported_path.parent == Path(os.environ["REMINDER_DOWNLOADS_DIRECTORY"])
        assert exported_path.read_bytes().startswith(b"SQLite format 3")

        client.post("/api/memos", json={"title": "복원 후 사라질 메모"})
        restored = client.post(
            "/api/backups/import",
            files={"file": ("reminder-backup.db", exported_path.read_bytes(), "application/vnd.sqlite3")},
        )
        assert restored.status_code == 204
        assert [memo["title"] for memo in client.get("/api/memos").json()] == ["백업 대상"]
        exported_path.unlink()


def test_schedule_without_time_disables_alerts():
    with TestClient(app) as client:
        schedule = client.post(
            "/api/schedules",
            json={"date": "2026-08-13", "title": "종일 일정", "alert_enabled": True},
        )
        assert schedule.status_code == 201
        assert schedule.json()["time"] is None
        assert schedule.json()["alert_enabled"] is False


def test_legacy_schedule_table_is_migrated_without_data_loss(tmp_path):
    legacy_engine = create_engine(f"sqlite:///{(tmp_path / 'legacy.db').as_posix()}")
    with legacy_engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE schedules (
                id INTEGER PRIMARY KEY,
                date DATE NOT NULL,
                time TIME NOT NULL,
                title VARCHAR(200) NOT NULL,
                alert_enabled BOOLEAN NOT NULL,
                notified_at DATETIME,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """))
        connection.execute(text("""
            INSERT INTO schedules VALUES
            (1, '2026-08-13', '09:00:00', '기존 일정', 1, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """))

    migrate_schedule_time_column(legacy_engine)

    assert inspect(legacy_engine).get_columns("schedules")[2]["nullable"] is True
    with legacy_engine.connect() as connection:
        assert connection.execute(text("SELECT title FROM schedules")).scalar_one() == "기존 일정"
