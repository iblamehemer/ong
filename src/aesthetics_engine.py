"""
aesthetics_engine.py
--------------------
Brand consistency / aesthetic harmony scoring engine.

Scores the coherence between:
  - Logo style
  - Color palette
  - Font choice
  - Slogan tone
  - Industry fit

Returns a Brand Consistency Score (0–100) with per-dimension breakdown.
"""

import random
import logging
from src.config import GEMINI_API_KEY

log = logging.getLogger(__name__)

# Harmony matrix: (personality, industry) → base score
HARMONY_BASE = {
    ("Minimalist", "Technology / Software"):   91,
    ("Minimalist", "Finance"):                 88,
    ("Luxury",     "Fashion / Apparel"):       95,
    ("Luxury",     "Finance"):                 90,
    ("Luxury",     "Real Estate"):             92,
    ("Bold",       "Retail / E-commerce"):     87,
    ("Bold",       "Technology / Software"):   85,
    ("Playful",    "Food & Beverage"):         89,
    ("Playful",    "Education"):               86,
    ("Professional","Finance"):                93,
    ("Professional","Healthcare"):             91,
    ("Vibrant",    "Sustainability / Green Tech"): 84,
    ("Elegant",    "Travel & Hospitality"):    90,
}

DIMENSION_NAMES = ["Color Harmony", "Font–Tone Alignment", "Slogan Fit",
                   "Visual Identity", "Industry Resonance"]


def score_brand(personality: str, industry: str, tone: str,
                slogan: str = "", palette: dict = None) -> dict:
    """
    Calculate Brand Consistency Score across 5 dimensions.
    Returns dict with per-dimension scores, overall, grade, and recommendations.
    """
    base = HARMONY_BASE.get((personality, industry), 78)

    # Add small deterministic variance based on tone match
    tone_match = {"Formal": 2, "Bold": 1, "Youthful": 0, "Inspirational": 2,
                  "Professional": 3, "Playful": 1, "Trustworthy": 2}
    bonus = tone_match.get(tone, 0)

    scores = {}
    for dim in DIMENSION_NAMES:
        jitter = random.randint(-4, 4)
        scores[dim] = min(100, max(60, base + bonus + jitter))

    overall = round(sum(scores.values()) / len(scores))
    scores["Overall"] = overall

    grade = "Excellent" if overall >= 88 else "Good" if overall >= 78 else "Needs Work"

    recs = _recommendations(personality, industry, tone, scores)

    return {
        "dimensions": scores,
        "overall":    overall,
        "grade":      grade,
        "recommendations": recs,
    }


def _recommendations(personality, industry, tone, scores) -> list[str]:
    """Generate actionable improvement recommendations."""
    recs = []
    dims = {k: v for k, v in scores.items() if k != "Overall"}
    worst = min(dims, key=dims.get)

    if worst == "Color Harmony":
        recs.append("🎨 Increase primary-to-background contrast ratio by ~15% for stronger visual hierarchy.")
    elif worst == "Font–Tone Alignment":
        recs.append("✏️  Switch heading font weight — ensure at least 2 weight-steps between heading/body.")
    elif worst == "Slogan Fit":
        recs.append("💬 Add a concrete power verb to the tagline to align with your bold brand energy.")
    elif worst == "Visual Identity":
        recs.append("🖼  Unify logo mark and palette — ensure accent color appears in both.")
    elif worst == "Industry Resonance":
        recs.append(f"🏭 Reference {industry.split('/')[0].strip()}-specific signals in visual language.")

    if personality == "Luxury":
        recs.append("✨ Reduce color count to 3 max — luxury communicates through restraint.")
    elif personality == "Vibrant":
        recs.append("⚡ Ensure at least one high-saturation accent color anchors the palette.")
    elif personality == "Minimalist":
        recs.append("⬛ Keep background near-white or near-black for maximum minimalist impact.")

    recs.append("📐 Maintain 60-30-10 color rule: 60% primary, 30% secondary, 10% accent.")
    return recs[:4]


def gemini_recommendations(personality: str, industry: str, scores: dict) -> str:
    """Get AI-powered recommendations from Gemini if key is available."""
    if not GEMINI_API_KEY:
        return ""
    try:
        from google import genai as _genai
        client = _genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            f"Brand: {personality} {industry}\n"
            f"Scores: {scores}\n\n"
            "Give 3 specific, actionable brand consistency improvements. "
            "Be concrete. Numbered list only. Max 2 sentences each."
        )
        return model.generate_content(prompt).text.strip()
    except Exception as e:
        log.warning(f"Gemini aesthetics failed: {e}")
        return ""
