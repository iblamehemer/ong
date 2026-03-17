"""
animation_engine.py
-------------------
Generates animated brand GIF using Pillow.

Supports: fade-in, slide-in, typewriter
Output: GIF bytes (compatible with st.image)
Resolution: 600×338 (16:9 social media)
"""

import io
import logging
from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger(__name__)

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _get_font(size: int):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def create_brand_gif(logo_svg: str, tagline: str, palette: dict,
                     company: str, style: str = "typewriter",
                     frames: int = 20) -> bytes:
    """
    Generate animated brand GIF.

    Args:
        logo_svg:  SVG string (used for initials extraction only in Pillow fallback)
        tagline:   Brand tagline string
        palette:   Palette dict from palette_engine
        company:   Company name
        style:     'typewriter' | 'fade' | 'slide'
        frames:    Number of frames (default 20)

    Returns: GIF bytes
    """
    W, H = 600, 338
    colors  = list(palette.values())
    bg_hex  = colors[0]["hex"] if colors else "#1B3A6B"
    acc_hex = colors[1]["hex"] if len(colors) > 1 else "#C9A84C"
    txt_hex = colors[4]["hex"] if len(colors) > 4 else "#FFFFFF"

    bg_rgb  = _hex_to_rgb(bg_hex)
    acc_rgb = _hex_to_rgb(acc_hex)
    txt_rgb = _hex_to_rgb(txt_hex)

    font_lg = _get_font(40)
    font_md = _get_font(22)
    font_sm = _get_font(13)

    # Get initials from company
    import re as _re
    words    = _re.sub(r"[^a-zA-Z\s]", "", company).split()
    initials = (words[0][0] + words[-1][0]).upper() if len(words) > 1 else (words[0][0].upper() if words else "B")

    tag = (tagline or f"{company} — Excellence by Design")[:55]
    gif_frames = []

    for i in range(frames):
        progress = i / (frames - 1)
        frame    = Image.new("RGB", (W, H), bg_rgb)
        draw     = ImageDraw.Draw(frame)

        # Bottom accent bar
        bar_w = int(W * progress)
        if bar_w > 0:
            draw.rectangle([0, H - 5, bar_w, H], fill=acc_rgb)

        if style == "fade":
            # Fade everything in
            alpha = int(255 * progress)
            draw.text((W // 2 - 30, H // 2 - 50), initials, font=font_lg,
                      fill=tuple(int(c * progress) for c in acc_rgb))
            draw.text((40, H // 2 + 10), tag[:int(len(tag) * progress)],
                      font=font_md, fill=txt_rgb)

        elif style == "slide":
            # Logo slides in from left; tagline slides in from right
            logo_x = int(-60 + 80 * min(1.0, progress * 2))
            tag_x  = int(W + 10 - (W * min(1.0, max(0, progress * 2 - 0.5))))
            draw.ellipse([logo_x, H // 2 - 40, logo_x + 80, H // 2 + 40], fill=acc_rgb)
            draw.text((logo_x + 10, H // 2 - 26), initials, font=font_lg, fill=bg_rgb)
            draw.text((max(140, tag_x), H // 2 - 12), tag, font=font_md, fill=txt_rgb)

        else:  # typewriter (default)
            # Logo bounces in, tagline types out char by char
            logo_y = int(H // 2 - 60 - 20 * max(0, 1 - progress * 3))
            draw.ellipse([W // 2 - 38, logo_y, W // 2 + 38, logo_y + 76], fill=acc_rgb)
            draw.text((W // 2 - 22, logo_y + 14), initials, font=font_lg, fill=bg_rgb)

            chars = int(len(tag) * min(1.0, progress * 1.5))
            partial = tag[:chars]
            bbox = draw.textbbox((0, 0), partial, font=font_md)
            tw = bbox[2] - bbox[0]
            draw.text(((W - tw) // 2, H // 2 + 50), partial, font=font_md, fill=txt_rgb)

            # Cursor blink
            if progress < 0.9 and int(progress * 10) % 2 == 0:
                draw.text(((W - tw) // 2 + tw + 2, H // 2 + 50), "|", font=font_md, fill=acc_rgb)

        # Company watermark
        if progress > 0.6:
            draw.text((W - 140, H - 26), f"— {company[:20]}", font=font_sm,
                      fill=tuple(min(255, int(c + 60)) for c in acc_rgb))

        gif_frames.append(frame)

    # Pause on last frame
    for _ in range(8):
        gif_frames.append(gif_frames[-1].copy())

    buf = io.BytesIO()
    gif_frames[0].save(
        buf, format="GIF", save_all=True,
        append_images=gif_frames[1:],
        duration=80, loop=0, optimize=True,
    )
    return buf.getvalue()
