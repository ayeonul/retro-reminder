import re
import sys
from colorsys import hsv_to_rgb, rgb_to_hsv
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import DATA_DIRECTORY
from app.models.setting import Setting


DEFAULT_ACCENT_COLOR = "#ffdbd9"
ICON_TEMPLATE_PATH = (
    Path(sys._MEIPASS) / "assets" / "reminder-icon-template.png"
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parents[2] / "assets" / "reminder-icon-template.png"
)
RUNTIME_ICON_DIRECTORY = DATA_DIRECTORY / "assets"
HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


@dataclass(frozen=True)
class AppIconPaths:
    ico: Path
    png: Path


def get_accent_color(db: Session) -> str:
    setting = db.get(Setting, "accent_color")
    value = setting.value if setting else DEFAULT_ACCENT_COLOR
    return value if HEX_COLOR_PATTERN.fullmatch(value) else DEFAULT_ACCENT_COLOR


def create_themed_icons(accent_color: str) -> AppIconPaths:
    RUNTIME_ICON_DIRECTORY.mkdir(parents=True, exist_ok=True)
    color = _parse_color(accent_color)
    secondary_color = _create_secondary_color(color)
    image = Image.open(ICON_TEMPLATE_PATH).convert("RGBA")
    pixels = image.load()

    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha and red >= 240 and green >= 185 and blue >= 185:
                pixels[x, y] = (*color, alpha)
            elif alpha and 210 <= red <= 245 and 130 <= green <= 195 and 130 <= blue <= 195:
                pixels[x, y] = (*secondary_color, alpha)

    png_path = RUNTIME_ICON_DIRECTORY / "reminder-icon.png"
    ico_path = RUNTIME_ICON_DIRECTORY / "reminder-icon.ico"
    image.save(png_path)
    image.save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (20, 20), (24, 24), (32, 32), (40, 40), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    return AppIconPaths(ico=ico_path, png=png_path)


def get_runtime_notification_icon_path() -> Path:
    return RUNTIME_ICON_DIRECTORY / "reminder-icon.png"


def _parse_color(value: str) -> tuple[int, int, int]:
    normalized = value if HEX_COLOR_PATTERN.fullmatch(value) else DEFAULT_ACCENT_COLOR
    return tuple(int(normalized[index : index + 2], 16) for index in (1, 3, 5))


def _create_secondary_color(color: tuple[int, int, int]) -> tuple[int, int, int]:
    hue, saturation, value = rgb_to_hsv(*(component / 255 for component in color))
    red, green, blue = hsv_to_rgb(hue, min(1.0, saturation + 0.15), value * 0.92)
    return tuple(round(component * 255) for component in (red, green, blue))
