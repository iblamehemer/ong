"""
preprocess.py
-------------
Data cleaning and preprocessing pipeline.
Handles: marketing_campaign_dataset.csv, startups.csv, sloganlist.csv

DATA SOURCE TRANSPARENCY:
- marketing_campaign_dataset.csv : real uploaded dataset (200K rows)
- startups.csv                   : real uploaded dataset (42K rows)
- sloganlist.csv                 : optional; fallback corpus used if missing
"""

import pandas as pd
import numpy as np
import re
import logging
from pathlib import Path
from src.config import (
    MARKETING_RAW, STARTUPS_RAW, SLOGANS_RAW,
    MARKETING_CLEAN, STARTUPS_CLEAN, SLOGANS_CLEAN,
    PERSONAS_FILE, CAMPAIGN_FEAT, DATA_PROCESSED,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


# ── Marketing dataset ──────────────────────────────────────────────────────────

def clean_marketing(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and engineer features from marketing_campaign_dataset.csv."""
    df = df.copy()

    # Parse currency
    df["Acquisition_Cost_Num"] = (
        df["Acquisition_Cost"]
        .astype(str)
        .str.replace(r"[$,]", "", regex=True)
        .str.strip()
        .apply(pd.to_numeric, errors="coerce")
    )

    # Parse duration
    df["Duration_Days"] = (
        df["Duration"]
        .astype(str)
        .str.extract(r"(\d+)")
        .astype(float)
    )

    # Parse date
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.month
    df["Quarter"] = df["Date"].dt.quarter

    # CTR
    df["CTR"] = np.where(
        df["Impressions"] > 0,
        (df["Clicks"] / df["Impressions"] * 100).round(4),
        0.0,
    )

    # Drop nulls in key columns
    df = df.dropna(subset=["ROI", "Engagement_Score"])

    # Strip string columns
    for col in ["Campaign_Type", "Channel_Used", "Location", "Language", "Customer_Segment", "Target_Audience"]:
        df[col] = df[col].astype(str).str.strip().str.title()

    log.info(f"Marketing cleaned: {len(df):,} rows")
    return df


def encode_marketing(df: pd.DataFrame):
    """Label-encode categoricals; return encoded df + encoder dict."""
    from sklearn.preprocessing import LabelEncoder
    cat_cols = ["Campaign_Type", "Channel_Used", "Location", "Language",
                "Customer_Segment", "Target_Audience"]
    encoders = {}
    df_enc = df.copy()
    for col in cat_cols:
        le = LabelEncoder()
        df_enc[col + "_enc"] = le.fit_transform(df_enc[col].astype(str))
        encoders[col] = le
    return df_enc, encoders


def build_campaign_features(df: pd.DataFrame) -> pd.DataFrame:
    """Select and return feature matrix used by ML models."""
    feature_cols = [
        "Campaign_Type_enc", "Channel_Used_enc", "Location_enc",
        "Language_enc", "Customer_Segment_enc",
        "Duration_Days", "Acquisition_Cost_Num", "CTR",
        "Clicks", "Impressions",
    ]
    available = [c for c in feature_cols if c in df.columns]
    return df[available + ["ROI", "Engagement_Score", "Conversion_Rate"]].dropna()


# ── Startups dataset ───────────────────────────────────────────────────────────

def clean_startups(df: pd.DataFrame) -> pd.DataFrame:
    """Clean startups.csv."""
    df = df.copy()
    df = df.dropna(subset=["name", "tagline"])
    df["name"]        = df["name"].str.strip()
    df["tagline"]     = df["tagline"].str.strip()
    df["city"]        = df["city"].fillna("Unknown").str.strip()
    df["description"] = df["description"].fillna("").str.strip()
    df = df[df["tagline"].str.len() > 4]
    df["word_count"]  = df["tagline"].str.split().str.len()
    df["char_count"]  = df["tagline"].str.len()
    log.info(f"Startups cleaned: {len(df):,} rows")
    return df


INDUSTRY_KEYWORDS = {
    "Technology / Software": ["software","saas","app","tech","ai","data","cloud","api","platform","developer","code","digital"],
    "Healthcare":            ["health","medical","care","clinic","wellness","therapy","patient","pharma","doctor","mental"],
    "Finance":               ["finance","fintech","payment","invest","bank","credit","loan","insurance","money","trading"],
    "Education":             ["education","learning","course","student","school","university","tutor","teach","skill"],
    "Food & Beverage":       ["food","restaurant","drink","beverage","meal","recipe","diet","nutrition","coffee","snack"],
    "Fashion / Apparel":     ["fashion","apparel","clothing","style","wear","design","brand","luxury","textile"],
    "Real Estate":           ["real estate","property","housing","rental","mortgage","realty","home","land"],
    "Sustainability / Green Tech": ["green","eco","sustainable","environment","climate","energy","solar","carbon","recycle"],
    "Travel & Hospitality":  ["travel","hotel","booking","flight","tourism","hospitality","trip","vacation"],
    "Retail / E-commerce":   ["retail","ecommerce","shop","store","marketplace","delivery","logistics","supply"],
    "Creative / Design":     ["design","creative","agency","marketing","branding","art","media","content","visual"],
}

def infer_industry(text: str) -> str:
    text_lower = text.lower()
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            return industry
    return "Technology / Software"


def build_personas(df: pd.DataFrame) -> pd.DataFrame:
    """Assign inferred industry/persona to each startup."""
    df = df.copy()
    df["inferred_industry"] = df["description"].apply(infer_industry)

    persona_map = {
        "Technology / Software":  "Modern SaaS",
        "Healthcare":             "Trusted Health",
        "Finance":                "Professional Finance",
        "Education":              "Knowledge First",
        "Food & Beverage":        "Lifestyle & Food",
        "Fashion / Apparel":      "Luxury Lifestyle",
        "Real Estate":            "Premium Properties",
        "Sustainability / Green Tech": "Eco-Conscious",
        "Travel & Hospitality":   "Experience-Driven",
        "Retail / E-commerce":    "Youthful D2C",
        "Creative / Design":      "Creative Studio",
        "Manufacturing":          "Industrial Excellence",
    }
    df["persona"] = df["inferred_industry"].map(persona_map).fillna("Modern SaaS")
    log.info(f"Personas built: {df['persona'].value_counts().to_dict()}")
    return df


# ── Slogans dataset ────────────────────────────────────────────────────────────

FALLBACK_SLOGANS = [
    ("Nike",    "Just Do It"),
    ("Apple",   "Think Different"),
    ("Google",  "Don't Be Evil"),
    ("Amazon",  "Work Hard. Have Fun. Make History."),
    ("Tesla",   "Accelerating the world's transition to sustainable energy"),
    ("Airbnb",  "Belong Anywhere"),
    ("Spotify", "Music for Everyone"),
    ("Slack",   "Where Work Happens"),
    ("Notion",  "One workspace. Every team."),
    ("Figma",   "Design Together"),
    ("Stripe",  "Payments infrastructure for the internet"),
    ("Shopify", "Make Commerce Better for Everyone"),
    ("HubSpot", "Grow Better"),
    ("Zoom",    "Video Communications Empowering People"),
    ("Canva",   "Empowering the World to Design"),
]

def clean_slogans(df: pd.DataFrame | None) -> pd.DataFrame:
    """Clean sloganlist.csv or return fallback corpus."""
    if df is None or df.empty:
        log.warning("Slogans CSV missing — using fallback corpus.")
        df = pd.DataFrame(FALLBACK_SLOGANS, columns=["Company", "Slogan"])

    df = df.copy()
    df.columns = [c.strip().title() for c in df.columns]
    if "Company" not in df.columns or "Slogan" not in df.columns:
        df = pd.DataFrame(FALLBACK_SLOGANS, columns=["Company", "Slogan"])

    df = df.dropna(subset=["Slogan"])
    df["Slogan"]       = df["Slogan"].str.strip()
    df["Company"]      = df["Company"].str.strip()
    df                 = df[df["Slogan"].str.len() > 3]
    df["word_count"]   = df["Slogan"].str.split().str.len()
    df["slogan_clean"] = (
        df["Slogan"]
        .str.lower()
        .str.replace(r"[^a-z0-9\s]", "", regex=True)
        .str.strip()
    )
    log.info(f"Slogans cleaned: {len(df):,} rows")
    return df


# ── Main runner ────────────────────────────────────────────────────────────────

def run_preprocessing():
    """Run full preprocessing pipeline and save all outputs."""
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    # Marketing
    if MARKETING_RAW.exists():
        df_mkt = pd.read_csv(MARKETING_RAW)
        df_mkt_clean = clean_marketing(df_mkt)
        df_mkt_enc, encoders = encode_marketing(df_mkt_clean)
        df_mkt_clean.to_csv(MARKETING_CLEAN, index=False)
        df_feat = build_campaign_features(df_mkt_enc)
        df_feat.to_csv(CAMPAIGN_FEAT, index=False)

        import joblib
        from src.config import ENCODERS_FILE, MODELS_DIR
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(encoders, ENCODERS_FILE)
        log.info(f"Saved encoders → {ENCODERS_FILE}")
    else:
        log.warning(f"Marketing CSV not found at {MARKETING_RAW}")

    # Startups
    if STARTUPS_RAW.exists():
        df_s = pd.read_csv(STARTUPS_RAW)
        df_s_clean = clean_startups(df_s)
        df_s_clean.to_csv(STARTUPS_CLEAN, index=False)
        df_personas = build_personas(df_s_clean)
        df_personas.to_csv(PERSONAS_FILE, index=False)

    # Slogans
    df_slogans_raw = pd.read_csv(SLOGANS_RAW) if SLOGANS_RAW.exists() else None
    df_slogans = clean_slogans(df_slogans_raw)
    df_slogans.to_csv(SLOGANS_CLEAN, index=False)

    log.info("✅ Preprocessing complete.")
    return True


if __name__ == "__main__":
    run_preprocessing()
