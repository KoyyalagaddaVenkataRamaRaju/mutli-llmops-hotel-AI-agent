import os
import re

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "illustrations"))

def _load_undraw_svg(filename: str, width: int = 240, height: int = 140) -> str:
    """Loads an authentic unDraw SVG file from local assets and formats with responsive dimensions."""
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            # Insert width, height and responsive style into the root <svg> tag
            modified = re.sub(
                r"<svg\b([^>]*)>",
                rf'<svg\1 width="{width}" height="{height}" style="max-width:100%; height:auto; display:block; margin:0 auto;">',
                content,
                count=1
            )
            return f'<div style="display:flex; justify-content:center; align-items:center; width:100%; max-width:{width}px; margin:0 auto;">{modified}</div>'
        except Exception:
            pass

    # Remote jsDelivr CDN fallback
    cdn_url = f"https://cdn.jsdelivr.net/gh/balazser/undraw-svg-collection/svgs/{filename}"
    return f'<div style="text-align:center;"><img src="{cdn_url}" width="{width}" height="{height}" style="max-width:100%; height:auto;" alt="unDraw Illustration"/></div>'

def get_undraw_bot_svg(width: int = 240, height: int = 140) -> str:
    """Official unDraw 'Chat Bot' vector illustration."""
    return _load_undraw_svg("chat-bot.svg", width, height)

def get_undraw_floorplan_svg(width: int = 240, height: int = 140) -> str:
    """Official unDraw 'Building / Architecture' vector illustration."""
    return _load_undraw_svg("building.svg", width, height)

def get_undraw_booking_svg(width: int = 240, height: int = 140) -> str:
    """Official unDraw 'Booking / Registration' vector illustration."""
    return _load_undraw_svg("booking.svg", width, height)

def get_undraw_checkout_svg(width: int = 240, height: int = 140) -> str:
    """Official unDraw 'Order Confirmed / Departure' vector illustration."""
    return _load_undraw_svg("order-confirmed.svg", width, height)

def get_undraw_housekeeping_svg(width: int = 240, height: int = 140) -> str:
    """Official unDraw 'Clean Up / Housekeeping' vector illustration."""
    return _load_undraw_svg("clean-up.svg", width, height)

def get_undraw_maintenance_svg(width: int = 240, height: int = 140) -> str:
    """Official unDraw 'Maintenance / Engineering' vector illustration."""
    return _load_undraw_svg("maintenance.svg", width, height)

def get_undraw_dining_svg(width: int = 240, height: int = 140) -> str:
    """Official unDraw 'Eating Together / Culinary Dining' vector illustration."""
    return _load_undraw_svg("eating-together.svg", width, height)

def get_undraw_analytics_svg(width: int = 240, height: int = 140) -> str:
    """Official unDraw 'Business Analytics / Financial Data' vector illustration."""
    return _load_undraw_svg("business-analytics.svg", width, height)

def get_undraw_cloud_svg(width: int = 240, height: int = 140) -> str:
    """Official unDraw 'Cloud Hosting / Vector Database' vector illustration."""
    return _load_undraw_svg("cloud-hosting.svg", width, height)

def get_undraw_sidebar_svg(width: int = 210, height: int = 110) -> str:
    """Official unDraw 'Building' compact vector banner for sidebar."""
    return _load_undraw_svg("building.svg", width, height)
