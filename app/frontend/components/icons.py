import os
import base64
from typing import Dict

ASSETS_ICONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "icons"))
_ICON_CACHE: Dict[str, str] = {}

def get_icon_b64(icon_name: str) -> str:
    """Returns base64 data URI for the official Icons8 icon."""
    clean_name = icon_name.replace(".png", "")
    if clean_name in _ICON_CACHE:
        return _ICON_CACHE[clean_name]

    icon_path = os.path.join(ASSETS_ICONS_DIR, f"{clean_name}.png")
    if os.path.exists(icon_path):
        try:
            with open(icon_path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
                uri = f"data:image/png;base64,{data}"
                _ICON_CACHE[clean_name] = uri
                return uri
        except Exception:
            pass

    # Remote fallback
    return f"https://img.icons8.com/fluency/96/{clean_name}.png"

def get_icon_img(icon_name: str, size: int = 20, margin_right: int = 6, extra_style: str = "") -> str:
    """
    Renders an inline official Icons8 HTML img tag with local base64 embedding.
    Guaranteed to render offline, instant load, zero CSP or cross-origin blocks.
    """
    src = get_icon_b64(icon_name)
    style = f"vertical-align:middle; width:{size}px; height:{size}px; margin-right:{margin_right}px; {extra_style}"
    return f'<img src="{src}" width="{size}" height="{size}" alt="{icon_name}" style="{style}"/>'

