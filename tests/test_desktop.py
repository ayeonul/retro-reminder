import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from desktop import DesktopApi, create_bound_socket


class FakeWindow:
    def __init__(self) -> None:
        self.minimized = False
        self.destroyed = False

    def minimize(self) -> None:
        self.minimized = True

    def destroy(self) -> None:
        self.destroyed = True


def test_desktop_api_controls_window():
    api = DesktopApi()
    window = FakeWindow()
    api.set_window(window)

    api.minimize_window()
    api.close_window()

    assert window.minimized is True
    assert window.destroyed is True


def test_bound_socket_uses_localhost_and_an_available_port():
    server_socket = create_bound_socket()
    try:
        host, port = server_socket.getsockname()
        assert host == "127.0.0.1"
        assert port > 0
    finally:
        server_socket.close()
