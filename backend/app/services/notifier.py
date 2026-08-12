import logging


logger = logging.getLogger(__name__)


class WindowsNotifier:
    def send(self, title: str, message: str) -> bool:
        try:
            from win11toast import notify

            notify(title, message)
            return True
        except Exception:
            logger.exception("Windows 알림 표시 중 오류가 발생했습니다.")
            return False
