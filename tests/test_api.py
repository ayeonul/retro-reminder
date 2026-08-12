import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
test_database = Path(tempfile.gettempdir()) / "reminder_api_test.db"
if test_database.exists():
    test_database.unlink()
os.environ["REMINDER_DATABASE_URL"] = f"sqlite:///{test_database.as_posix()}"
os.environ["REMINDER_DATA_DIRECTORY"] = str(Path(tempfile.gettempdir()) / "reminder_api_test_data")

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.services.reminder import process_due_schedules


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

        assert client.get("/api/settings").json()["accent_color"] == "#ffdbd9"
        assert client.patch("/api/settings", json={"accent_color": "#123abc"}).json()["accent_color"] == "#123abc"

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


def test_backup_export_and_import():
    with TestClient(app) as client:
        client.post("/api/memos", json={"title": "백업 대상", "content": "보존할 내용"})
        exported = client.post("/api/backups/export")
        assert exported.status_code == 200
        assert exported.content.startswith(b"SQLite format 3")

        client.post("/api/memos", json={"title": "복원 후 사라질 메모"})
        restored = client.post(
            "/api/backups/import",
            files={"file": ("reminder-backup.db", exported.content, "application/vnd.sqlite3")},
        )
        assert restored.status_code == 204
        assert [memo["title"] for memo in client.get("/api/memos").json()] == ["백업 대상"]
