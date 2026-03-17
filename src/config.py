"""
config.py
---------
Central configuration for BrandSphere AI.
All paths, constants, and environment variable handling live here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).resolve().parent.parent
DATA_RAW        = BASE_DIR / "datasets" / "raw"
DATA_PROCESSED  = BASE_DIR / "datasets" / "processed"
MODELS_DIR      = BASE_DIR / "models"
ASSETS_DIR      = BASE_DIR / "assets"
TEMP_DIR        = BASE_DIR / "assets" / "temp"

# ── API Keys ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")

# ── Dataset filenames ──────────────────────────────────────────────────────────
SLOGANS_RAW     = DATA_RAW / "sloganlist.csv"
STARTUPS_RAW    = DATA_RAW / "startups.csv"
MARKETING_RAW   = DATA_RAW / "marketing_campaign_dataset.csv"

SLOGANS_CLEAN   = DATA_PROCESSED / "cleaned_slogans.csv"
STARTUPS_CLEAN  = DATA_PROCESSED / "cleaned_startups.csv"
MARKETING_CLEAN = DATA_PROCESSED / "cleaned_marketing.csv"
PERSONAS_FILE   = DATA_PROCESSED / "startup_personas.csv"
CAMPAIGN_FEAT   = DATA_PROCESSED / "campaign_features.csv"

# ── Model filenames ────────────────────────────────────────────────────────────
MODEL_ROI        = MODELS_DIR / "roi_model.pkl"
MODEL_ENGAGEMENT = MODELS_DIR / "engagement_model.pkl"
MODEL_CTR        = MODELS_DIR / "ctr_model.pkl"
ENCODERS_FILE    = MODELS_DIR / "encoders.pkl"
SCALER_FILE      = MODELS_DIR / "scaler.pkl"

# ── Industries & personalities ─────────────────────────────────────────────────
INDUSTRIES = [
    "Technology / Software", "Fashion / Apparel", "Food & Beverage",
    "Healthcare", "Finance", "Education", "Retail / E-commerce",
    "Real Estate", "Creative / Design", "Manufacturing",
    "Travel & Hospitality", "Sustainability / Green Tech",
]

PERSONALITIES = ["Minimalist", "Vibrant", "Luxury", "Bold", "Elegant", "Playful", "Professional"]

TONES = ["Formal", "Bold", "Youthful", "Inspirational", "Professional", "Playful", "Trustworthy"]

PLATFORMS = ["Instagram", "Facebook", "Twitter/X", "LinkedIn", "TikTok", "YouTube"]

REGIONS = [
    "North America", "Europe", "Asia Pacific",
    "Middle East", "Latin America", "South Asia", "Africa", "Global",
]

LANGUAGES_SUPPORTED = ["Hindi", "Spanish", "French", "German", "Gujarati", "Arabic", "Mandarin"]

CAMPAIGN_OBJECTIVES = ["Brand Awareness", "Engagement", "Lead Generation", "Conversion", "Retention"]

# ── Color psychology ───────────────────────────────────────────────────────────
COLOR_PSYCHOLOGY = {
    "Technology / Software":      {"primary": "#1B3A6B", "secondary": "#2E86AB", "accent": "#4CC9F0", "neutral": "#F0F4F8", "text": "#1A1A2E"},
    "Fashion / Apparel":          {"primary": "#1A1A2E", "secondary": "#C9A84C", "accent": "#E8DCC8", "neutral": "#F8F5F0", "text": "#1A1A2E"},
    "Food & Beverage":            {"primary": "#E63946", "secondary": "#F4A261", "accent": "#2D6A4F", "neutral": "#FFF8F0", "text": "#1A1A2E"},
    "Healthcare":                 {"primary": "#0077B6", "secondary": "#00B4D8", "accent": "#90E0EF", "neutral": "#F0F9FF", "text": "#1A1A2E"},
    "Finance":                    {"primary": "#1B3A6B", "secondary": "#2E4057", "accent": "#C9A84C", "neutral": "#F0F4F8", "text": "#1A1A2E"},
    "Education":                  {"primary": "#4361EE", "secondary": "#7209B7", "accent": "#F72585", "neutral": "#F8F9FF", "text": "#1A1A2E"},
    "Retail / E-commerce":        {"primary": "#E63946", "secondary": "#F4A261", "accent": "#1A1A2E", "neutral": "#FFF8F0", "text": "#1A1A2E"},
    "Real Estate":                {"primary": "#1B3A6B", "secondary": "#C9A84C", "accent": "#2D6A4F", "neutral": "#F0EDE8", "text": "#1A1A2E"},
    "Creative / Design":          {"primary": "#F72585", "secondary": "#7209B7", "accent": "#4361EE", "neutral": "#F8F0FF", "text": "#1A1A2E"},
    "Manufacturing":              {"primary": "#1A1A2E", "secondary": "#2E4057", "accent": "#C9A84C", "neutral": "#F0F4F8", "text": "#1A1A2E"},
    "Travel & Hospitality":       {"primary": "#2EC4B6", "secondary": "#FF9F1C", "accent": "#E71D36", "neutral": "#F0FFFE", "text": "#1A1A2E"},
    "Sustainability / Green Tech": {"primary": "#2D6A4F", "secondary": "#52B788", "accent": "#D8F3DC", "neutral": "#F0FFF4", "text": "#1A1A2E"},
}

# ── Font engine mappings ───────────────────────────────────────────────────────
FONT_MAP = {
    ("Minimalist", "Technology / Software"):   [("Inter", "Inter", "Roboto Mono"),       ("clean", "geometric", "mono")],
    ("Minimalist", "Fashion / Apparel"):        [("Futura", "Helvetica Neue", "Gill Sans"), ("geometric", "neutral", "humanist")],
    ("Luxury",     "Fashion / Apparel"):        [("Cormorant Garamond", "Didot", "Garamond"), ("serif", "modern serif", "old-style serif")],
    ("Luxury",     "Finance"):                  [("Playfair Display", "Garamond", "Libre Baskerville"), ("transitional serif", "old-style", "serif")],
    ("Luxury",     "Real Estate"):              [("Cormorant Garamond", "Libre Baskerville", "EB Garamond"), ("serif", "serif", "humanist serif")],
    ("Bold",       "Technology / Software"):    [("Montserrat", "Oswald", "Bebas Neue"),  ("geometric", "condensed", "display")],
    ("Bold",       "Retail / E-commerce"):      [("Anton", "Montserrat", "Raleway"),      ("display", "geometric", "elegant sans")],
    ("Playful",    "Food & Beverage"):          [("Nunito", "Pacifico", "Quicksand"),     ("rounded", "script", "rounded sans")],
    ("Playful",    "Education"):                [("Nunito", "Fredoka One", "Poppins"),    ("rounded", "display", "geometric")],
    ("Professional","Finance"):                 [("Merriweather", "Source Serif Pro", "Lato"), ("serif", "serif", "humanist sans")],
    ("Professional","Healthcare"):              [("Source Sans Pro", "Open Sans", "Lato"),("humanist", "humanist", "humanist")],
    ("Elegant",    "Travel & Hospitality"):     [("Cormorant Garamond", "Raleway", "Josefin Sans"), ("serif", "elegant sans", "geometric")],
    ("Vibrant",    "Sustainability / Green Tech"):[("Poppins", "Nunito", "Raleway"),      ("geometric", "rounded", "elegant sans")],
}
DEFAULT_FONTS = [("DM Sans", "Lato", "Space Mono"), ("humanist sans", "humanist", "mono")]

# ── Color palette role names ──────────────────────────────────────────────────
COLOR_NAMES = ["Primary", "Secondary", "Accent", "Background", "Text / CTA"]
