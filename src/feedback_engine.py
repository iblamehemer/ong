"""
feedback_engine.py
------------------
Stores user feedback ratings and comments to CSV.
Provides summary analytics for the feedback dashboard.
"""

import csv
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

FEEDBACK_FILE = Path("feedback_data.csv")
FEEDBACK_COLS = ["timestamp", "session_id", "company", "industry",
                 "module", "rating", "sentiment", "comment", "preferred"]


def save_feedback(session_id: str, company: str, industry: str,
                  module: str, rating: int, comment: str = "",
                  preferred: str = "") -> bool:
    """Append a feedback record to feedback_data.csv."""
    sentiment = "positive" if rating >= 4 else "neutral" if rating == 3 else "negative"
    record = {
        "timestamp":  datetime.now().isoformat(),
        "session_id": session_id,
        "company":    company,
        "industry":   industry,
        "module":     module,
        "rating":     rating,
        "sentiment":  sentiment,
        "comment":    comment,
        "preferred":  preferred,
    }
    try:
        exists = FEEDBACK_FILE.exists()
        with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FEEDBACK_COLS)
            if not exists:
                writer.writeheader()
            writer.writerow(record)
        return True
    except Exception as e:
        log.warning(f"Feedback save failed: {e}")
        return False


def load_feedback() -> pd.DataFrame:
    """Load all feedback records. Returns empty DataFrame if file missing."""
    if not FEEDBACK_FILE.exists():
        return pd.DataFrame(columns=FEEDBACK_COLS)
    try:
        return pd.read_csv(FEEDBACK_FILE, parse_dates=["timestamp"])
    except Exception:
        return pd.DataFrame(columns=FEEDBACK_COLS)


def get_summary(df: pd.DataFrame) -> dict:
    """Summarize feedback for analytics dashboard."""
    if df.empty:
        return {}
    return {
        "total_submissions": len(df),
        "avg_rating":        round(df["rating"].mean(), 2),
        "positive_pct":      round((df["sentiment"] == "positive").mean() * 100, 1),
        "neutral_pct":       round((df["sentiment"] == "neutral").mean() * 100, 1),
        "negative_pct":      round((df["sentiment"] == "negative").mean() * 100, 1),
        "by_module":         df.groupby("module")["rating"].mean().round(2).to_dict(),
        "top_issues":        df[df["sentiment"] == "negative"]["comment"].dropna().head(5).tolist(),
        "top_praised":       df[df["sentiment"] == "positive"]["comment"].dropna().head(5).tolist(),
        "common_industries": df["industry"].value_counts().head(5).to_dict(),
    }
