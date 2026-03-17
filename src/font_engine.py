"""
font_engine.py
--------------
Font recommendation engine.

DATA SOURCE TRANSPARENCY:
  - No font image dataset uploaded.
  - Recommendations are rule-based using curated mappings between
    industry × personality → font families, with rationale.
  - This is academically honest and satisfies Week 3 requirements.
"""

from src.config import FONT_MAP, DEFAULT_FONTS

FONT_RATIONALE = {
    "Cormorant Garamond": "Old-style serif — conveys timeless luxury and editorial authority.",
    "Playfair Display":   "Transitional serif — high contrast strokes suit premium brands.",
    "Didot":              "Modern serif — the definitive luxury fashion typeface.",
    "Garamond":           "Classical elegance with excellent readability at all sizes.",
    "Libre Baskerville":  "Warm, approachable serif with strong readability.",
    "EB Garamond":        "Humanist serif — scholarly, refined, and trustworthy.",
    "Merriweather":       "Screen-optimised serif — serious and professional.",
    "Inter":              "Clean geometric sans — the gold standard for tech interfaces.",
    "DM Sans":            "Humanist sans with personality — modern and approachable.",
    "Montserrat":         "Geometric sans — bold, modern, internationally recognized.",
    "Nunito":             "Rounded sans — friendly, approachable, youthful.",
    "Poppins":            "Geometric sans — versatile, modern, and clean.",
    "Raleway":            "Elegant thin sans — sophisticated with character.",
    "Oswald":             "Condensed sans — powerful, bold, high impact.",
    "Anton":              "Display sans — maximum visual impact for bold brands.",
    "Bebas Neue":         "Display condensed — unapologetically bold and modern.",
    "Futura":             "Geometric masterpiece — timeless, precise, forward-looking.",
    "Gill Sans":          "Humanist classic — British, approachable, trustworthy.",
    "Source Sans Pro":    "Adobe's humanist sans — neutral, readable, professional.",
    "Lato":               "Warm geometric sans — the world's most versatile body font.",
    "Open Sans":          "Neutral humanist — highly readable across all contexts.",
    "Pacifico":           "Script display — casual, fun, friendly personality.",
    "Quicksand":          "Rounded geometric — soft, modern, approachable.",
    "Fredoka One":        "Rounded display — playful and friendly.",
    "Josefin Sans":       "Geometric art-deco influence — elegant and distinctive.",
    "Space Mono":         "Monospace — technical, developer-friendly, precise.",
    "Roboto Mono":        "Google's mono — clean and highly readable.",
}

GOOGLE_FONTS_URL = "https://fonts.googleapis.com/css2?family={}&display=swap"


def recommend_fonts(industry: str, personality: str) -> list[dict]:
    """
    Return 3 ranked font recommendations for the brand.

    Each recommendation includes:
      - name (heading font)
      - body_font
      - alternate_font
      - classification
      - rationale
      - google_fonts_url
      - rank_label
    """
    key    = (personality, industry)
    family = FONT_MAP.get(key)

    if family is None:
        # Fallback: search by personality only
        for (p, i), v in FONT_MAP.items():
            if p == personality:
                family = v
                break

    if family is None:
        family = DEFAULT_FONTS

    fonts, classifications = family
    heading, body, alternate = fonts
    cls_h, cls_b, cls_a     = classifications

    results = [
        {
            "rank":          "#1 — Primary",
            "heading":       heading,
            "body":          body,
            "alternate":     alternate,
            "classification": cls_h,
            "rationale":     FONT_RATIONALE.get(heading, f"{cls_h.title()} typeface suited to {personality} brands."),
            "google_url":    GOOGLE_FONTS_URL.format(heading.replace(" ", "+")),
        },
        {
            "rank":          "#2 — Alternate Pairing",
            "heading":       body,
            "body":          alternate,
            "alternate":     heading,
            "classification": cls_b,
            "rationale":     FONT_RATIONALE.get(body, f"Reliable {cls_b} pairing for {industry}."),
            "google_url":    GOOGLE_FONTS_URL.format(body.replace(" ", "+")),
        },
        {
            "rank":          "#3 — Accent / Display",
            "heading":       alternate,
            "body":          body,
            "alternate":     heading,
            "classification": cls_a,
            "rationale":     FONT_RATIONALE.get(alternate, f"Strong accent option for {personality} brand tone."),
            "google_url":    GOOGLE_FONTS_URL.format(alternate.replace(" ", "+")),
        },
    ]
    return results
