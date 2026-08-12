import socket
import threading
import time

import uvicorn
import webview


def create_bound_socket() -> socket.socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", 0))
    return server_socket


def run_desktop_app() -> None:
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

    window = webview.create_window(
        "Reminder",
        f"http://127.0.0.1:{port}",
        width=900,
        height=600,
        min_size=(620, 400),
        frameless=True,
        easy_drag=False,
        shadow=True,
    )

    def stop_server() -> None:
        server.should_exit = True

    window.events.closed += stop_server
    webview.start()


if __name__ == "__main__":
    run_desktop_app()
