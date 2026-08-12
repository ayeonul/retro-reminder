import os
import sys
import tempfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
test_database = Path(tempfile.gettempdir()) / "reminder_api_test.db"
if test_database.exists():
    test_database.unlink()
os.environ["REMINDER_DATABASE_URL"] = f"sqlite:///{test_database.as_posix()}"

from fastapi.testclient import TestClient

from app.main import app


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
