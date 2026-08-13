import socket
import threading
import time
from typing import Any

import uvicorn
import webview

import app.models
from app.core.database import Base, SessionLocal, engine
from app.services.app_icon import create_themed_icons, get_accent_color


def create_bound_socket() -> socket.socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", 0))
    return server_socket


class DesktopApi:
    def __init__(self) -> None:
        self._window: Any | None = None

    def set_window(self, window: Any) -> None:
        self._window = window

    def minimize_window(self) -> None:
        if self._window is not None:
            self._window.minimize()

    def close_window(self) -> None:
        if self._window is not None:
            self._window.destroy()


def run_desktop_app() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        app_icon_paths = create_themed_icons(get_accent_color(db))

    server_socket = create_bound_socket()
    port = server_socket.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config("app.main:app", host="127.0.0.1", port=port, log_level="warning")
    )
    server_thread = threading.Thread(target=server.run, kwargs={"sockets": [server_socket]}, daemon=True)
    server_thread.start()

    deadline = time.monotonic() + 5
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.05)
    if not server.started:
        server.should_exit = True
        raise RuntimeError("로컬 API 서버를 시작하지 못했습니다.")

    desktop_api = DesktopApi()
    window = webview.create_window(
        "Reminder",
        f"http://127.0.0.1:{port}",
        width=900,
        height=600,
        min_size=(620, 400),
        frameless=True,
        easy_drag=False,
        shadow=True,
        js_api=desktop_api,
    )
    desktop_api.set_window(window)

    def stop_server() -> None:
        server.should_exit = True
        server_socket.close()

    window.events.closed += stop_server
    webview.start(icon=str(app_icon_paths.ico))


if __name__ == "__main__":
    run_desktop_app()
