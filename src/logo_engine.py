"""
logo_engine.py
--------------
Logo concept generator.

DATA SOURCE TRANSPARENCY:
  - No logo image dataset uploaded.
  - Generates SVG-based logo concepts programmatically.
  - Uses company initials, palette, and personality to create 5 variants.
  - This is academically honest and practically useful.
  - Each concept is exportable as SVG string and renderable in Streamlit.
"""

import io
import re
import math
from PIL import Image, ImageDraw, ImageFont
import logging

log = logging.getLogger(__name__)

LOGO_STYLES = ["Minimal Circle", "Bold Monogram", "Geometric Mark", "Editorial Badge", "Abstract Ring"]


def _get_initials(company: str) -> str:
    """Extract 1–2 initials from company name."""
    words = re.sub(r"[^a-zA-Z\s]", "", company).split()
    if not words:
        return "B"
    if len(words) == 1:
        return words[0][0].upper()
    return (words[0][0] + words[-1][0]).upper()


def generate_svg_logo(company: str, palette: dict, style_idx: int = 0) -> str:
    """
    Generate an SVG logo concept.
    Returns SVG string.

    5 styles (style_idx 0–4):
      0 — Minimal Circle: clean circle + initials
      1 — Bold Monogram:  rounded rect + heavy initials
      2 — Geometric Mark: diamond frame + initials
      3 — Editorial Badge: hexagon outline + initials
      4 — Abstract Ring:  double ring gradient effect
    """
    initials = _get_initials(company)
    name_upper = company.upper()[:16]

    colors = list(palette.values())
    primary   = colors[0]["hex"] if colors else "#1B3A6B"
    secondary = colors[1]["hex"] if len(colors) > 1 else "#C9A84C"
    accent    = colors[2]["hex"] if len(colors) > 2 else "#FFFFFF"

    if style_idx == 0:
        return f"""<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" width="120" height="120">
  <circle cx="60" cy="60" r="58" fill="{primary}"/>
  <circle cx="60" cy="60" r="52" fill="none" stroke="{secondary}" stroke-width="1.5"/>
  <text x="60" y="72" text-anchor="middle" font-size="38" font-family="Georgia,serif"
        fill="{accent}" font-style="italic">{initials}</text>
  <text x="60" y="100" text-anchor="middle" font-size="8" font-family="Arial,sans-serif"
        fill="{secondary}" letter-spacing="3">{name_upper[:12]}</text>
</svg>"""

    elif style_idx == 1:
        return f"""<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" width="120" height="120">
  <rect width="120" height="120" rx="20" fill="{primary}"/>
  <rect x="6" y="6" width="108" height="108" rx="15" fill="none" stroke="{secondary}" stroke-width="1.5"/>
  <text x="60" y="76" text-anchor="middle" font-size="46" font-family="Arial,sans-serif"
        font-weight="900" fill="{accent}">{initials}</text>
  <line x1="24" y1="92" x2="96" y2="92" stroke="{secondary}" stroke-width="1"/>
  <text x="60" y="108" text-anchor="middle" font-size="7.5" font-family="Arial,sans-serif"
        fill="{secondary}" letter-spacing="2.5">{name_upper[:14]}</text>
</svg>"""

    elif style_idx == 2:
        return f"""<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" width="120" height="120">
  <rect width="120" height="120" fill="{primary}"/>
  <polygon points="60,8 112,60 60,112 8,60" fill="none" stroke="{secondary}" stroke-width="2"/>
  <polygon points="60,20 100,60 60,100 20,60" fill="none" stroke="{accent}" stroke-width="0.8" opacity="0.4"/>
  <text x="60" y="70" text-anchor="middle" font-size="34" font-family="Georgia,serif"
        fill="{accent}" font-style="italic">{initials}</text>
</svg>"""

    elif style_idx == 3:
        pts = " ".join([f"{60 + 46*math.cos(math.radians(a))},{60 + 46*math.sin(math.radians(a))}"
                        for a in range(30, 390, 60)])
        return f"""<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" width="120" height="120">
  <circle cx="60" cy="60" r="58" fill="{primary}"/>
  <polygon points="{pts}" fill="none" stroke="{secondary}" stroke-width="2"/>
  <text x="60" y="69" text-anchor="middle" font-size="30" font-family="Arial,sans-serif"
        font-weight="700" fill="{accent}" letter-spacing="2">{initials}</text>
  <text x="60" y="104" text-anchor="middle" font-size="7" font-family="Arial,sans-serif"
        fill="{secondary}" letter-spacing="3">{name_upper[:12]}</text>
</svg>"""

    else:  # style 4
        return f"""<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" width="120" height="120">
  <defs>
    <radialGradient id="rg" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="{secondary}" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="{primary}"/>
    </radialGradient>
  </defs>
  <circle cx="60" cy="60" r="58" fill="url(#rg)"/>
  <circle cx="60" cy="60" r="50" fill="none" stroke="{secondary}" stroke-width="2.5"/>
  <circle cx="60" cy="60" r="40" fill="none" stroke="{secondary}" stroke-width="0.8" opacity="0.5"/>
  <text x="60" y="70" text-anchor="middle" font-size="30" font-family="Georgia,serif"
        fill="{accent}" font-weight="bold">{initials}</text>
</svg>"""


def generate_all_logos(company: str, palette: dict) -> list[dict]:
    """
    Generate all 5 logo style variants.
    Returns list of dicts: [{style, svg, description}]
    """
    descriptions = [
        "Clean circle mark — universally recognized, scales perfectly to icon size.",
        "Bold monogram — strong brand recall, ideal for fashion and professional services.",
        "Geometric diamond — distinctive, modern, suits tech and creative industries.",
        "Hexagonal badge — structured authority, ideal for premium and fintech brands.",
        "Abstract ring — dynamic gradient mark, suits innovation and design-forward brands.",
    ]
    return [
        {
            "style":       LOGO_STYLES[i],
            "svg":         generate_svg_logo(company, palette, i),
            "description": descriptions[i],
            "index":       i,
        }
        for i in range(5)
    ]


def svg_to_png_bytes(svg_string: str, size: int = 300) -> bytes:
    """
    Convert SVG to PNG bytes via Pillow fallback.
    (Cairosvg is not always available on Streamlit Cloud)
    """
    # Pillow fallback: render initials-based image
    try:
        import re as _re
        initials  = _re.search(r'<text[^>]*>([A-Z]+)</text>', svg_string)
        init_text = initials.group(1) if initials else "B"
        hex_match = _re.search(r'fill="(#[0-9a-fA-F]{6})"', svg_string)
        bg_color  = hex_match.group(1) if hex_match else "#1B3A6B"

        def _h2rgb(h):
            h = h.lstrip("#")
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        img  = Image.new("RGB", (size, size), _h2rgb(bg_color))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size // 3)
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), init_text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - tw) // 2, (size - th) // 2), init_text, fill=(255, 255, 255), font=font)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        log.warning(f"svg_to_png failed: {e}")
        return b""
