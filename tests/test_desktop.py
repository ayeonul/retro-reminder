import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from desktop import DesktopApi, create_bound_socket


class FakeWindow:
    def __init__(self) -> None:
        self.minimized = False
        self.destroyed = False
        self.size: tuple[int, int] | None = None

    def minimize(self) -> None:
        self.minimized = True

    def destroy(self) -> None:
        self.destroyed = True

    def resize(self, width: int, height: int) -> None:
        self.size = (width, height)


def test_desktop_api_controls_window():
    api = DesktopApi()
    window = FakeWindow()
    api.set_window(window)

    api.minimize_window()
    api.resize_window(900, 600)
    api.close_window()

    assert window.minimized is True
    assert window.size == (900, 600)
    assert window.destroyed is True


def test_desktop_api_enforces_minimum_window_size():
    api = DesktopApi()
    window = FakeWindow()
    api.set_window(window)

    api.resize_window(100, 200)

    assert window.size == (620, 400)


def test_bound_socket_uses_localhost_and_an_available_port():
    server_socket = create_bound_socket()
    try:
        host, port = server_socket.getsockname()
        assert host == "127.0.0.1"
        assert port > 0
    finally:
        server_socket.close()
