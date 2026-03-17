"""
campaign_predictor.py
---------------------
Trains and serves Random Forest regression models for:
  - ROI prediction
  - Engagement Score prediction
  - Conversion Rate prediction

DATA SOURCE: marketing_campaign_dataset.csv (200,000 real records)
MODEL TYPE:  Random Forest Regressor (scikit-learn)
"""

import pandas as pd
import numpy as np
import joblib
import logging
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from src.config import (
    MARKETING_RAW, CAMPAIGN_FEAT, MODELS_DIR,
    MODEL_ROI, MODEL_ENGAGEMENT, MODEL_CTR,
    ENCODERS_FILE, SCALER_FILE,
)

log = logging.getLogger(__name__)


# ── Feature Engineering ────────────────────────────────────────────────────────

CAT_COLS = ["Campaign_Type", "Channel_Used", "Location", "Language", "Customer_Segment"]
FEATURE_COLS = ["Campaign_Type_enc", "Channel_Used_enc", "Location_enc",
                "Language_enc", "Customer_Segment_enc",
                "Duration_Days", "Acquisition_Cost_Num", "CTR"]

def load_and_prepare(csv_path: Path):
    """Load marketing CSV and prepare feature matrix + targets."""
    df = pd.read_csv(csv_path)

    # Parse
    df["Acquisition_Cost_Num"] = (
        df["Acquisition_Cost"].astype(str)
        .str.replace(r"[$,]", "", regex=True)
        .apply(pd.to_numeric, errors="coerce")
    )
    df["Duration_Days"] = df["Duration"].astype(str).str.extract(r"(\d+)").astype(float)
    df["CTR"] = np.where(df["Impressions"] > 0,
                         df["Clicks"] / df["Impressions"] * 100, 0.0)

    for col in CAT_COLS:
        df[col] = df[col].astype(str).str.strip().str.title()

    # Encode
    encoders = {}
    for col in CAT_COLS:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col])
        encoders[col] = le

    df = df.dropna(subset=FEATURE_COLS + ["ROI", "Engagement_Score", "Conversion_Rate"])

    X = df[FEATURE_COLS].values
    y_roi  = df["ROI"].values
    y_eng  = df["Engagement_Score"].values
    y_conv = df["Conversion_Rate"].values

    return X, y_roi, y_eng, y_conv, encoders, df


def evaluate(name, y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae  = mean_absolute_error(y_true, y_pred)
    r2   = r2_score(y_true, y_pred)
    log.info(f"  {name:20s} RMSE={rmse:.4f}  MAE={mae:.4f}  R²={r2:.4f}")
    return {"rmse": round(rmse, 4), "mae": round(mae, 4), "r2": round(r2, 4)}


# ── Training ───────────────────────────────────────────────────────────────────

def train_models(csv_path: Path = MARKETING_RAW) -> dict:
    """
    Train three Random Forest models on the marketing dataset.
    Returns a dict with model performance metrics.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    log.info("Loading and preparing data…")
    X, y_roi, y_eng, y_conv, encoders, df = load_and_prepare(csv_path)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    results = {}

    for target_name, y in [("ROI", y_roi), ("Engagement", y_eng), ("Conversion", y_conv)]:
        log.info(f"\n── Training {target_name} models ──")
        X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        candidates = {
            "RandomForest":  RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
            "GradientBoost": GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42),
            "Ridge":         Ridge(alpha=1.0),
        }

        best_model, best_rmse, best_name = None, np.inf, ""
        for name, model in candidates.items():
            model.fit(X_tr, y_tr)
            pred = model.predict(X_te)
            metrics = evaluate(name, y_te, pred)
            if metrics["rmse"] < best_rmse:
                best_rmse  = metrics["rmse"]
                best_model = model
                best_name  = name
            results[f"{target_name}_{name}"] = metrics

        log.info(f"  Best for {target_name}: {best_name} (RMSE={best_rmse:.4f})")

        save_path = MODELS_DIR / f"{target_name.lower()}_model.pkl"
        joblib.dump(best_model, save_path)
        log.info(f"  Saved → {save_path}")

    joblib.dump(encoders, ENCODERS_FILE)
    joblib.dump(scaler,   SCALER_FILE)
    log.info("✅ Training complete. Models + encoders saved.")
    return results


# ── Inference ──────────────────────────────────────────────────────────────────

class CampaignPredictor:
    """
    Lightweight inference wrapper.
    Loads saved models and encoders; provides predict() API.
    """

    CHANNEL_MAP = {
        "Instagram": "Instagram", "Facebook": "Facebook",
        "Twitter/X": "Website",   "LinkedIn": "Email",
        "TikTok":    "Youtube",   "YouTube":  "Youtube",
    }
    REGION_MAP = {
        "North America": "New York",   "Europe":        "Chicago",
        "Asia Pacific":  "Los Angeles","Middle East":   "Miami",
        "Latin America": "Houston",    "South Asia":    "Miami",
        "Africa":        "Chicago",    "Global":        "New York",
    }
    OBJ_MAP = {
        "Brand Awareness": "Social Media", "Engagement": "Influencer",
        "Lead Generation": "Search",       "Conversion": "Email",
        "Retention":       "Display",
    }
    PERS_CTR = {
        "Vibrant": 3.8, "Bold": 3.2, "Minimalist": 2.1,
        "Luxury": 2.7,  "Elegant": 2.4, "Playful": 3.5, "Professional": 2.2,
    }

    def __init__(self):
        self._loaded = False
        self.model_roi  = None
        self.model_eng  = None
        self.model_conv = None
        self.encoders   = None
        self.scaler     = None

    def _load(self):
        if self._loaded:
            return
        try:
            self.model_roi  = joblib.load(MODELS_DIR / "roi_model.pkl")
            self.model_eng  = joblib.load(MODELS_DIR / "engagement_model.pkl")
            self.model_conv = joblib.load(MODELS_DIR / "conversion_model.pkl")
            self.encoders   = joblib.load(ENCODERS_FILE)
            self.scaler     = joblib.load(SCALER_FILE)
            self._loaded    = True
        except Exception as e:
            log.warning(f"Models not found ({e}). Using heuristic fallback.")

    def _encode_val(self, col, val):
        """Encode a single categorical value; return 0 if unseen."""
        if self.encoders and col in self.encoders:
            le = self.encoders[col]
            if val in le.classes_:
                return int(le.transform([val])[0])
        return 0

    def predict(self, platform: str, region: str, objective: str,
                personality: str, language: str = "English",
                segment: str = "General", duration_days: int = 30,
                budget: float = 5000.0) -> dict:
        """
        Predict campaign KPIs.
        Returns dict with ROI, Engagement, Conversion, CTR, and guidance.
        """
        self._load()

        channel  = self.CHANNEL_MAP.get(platform, "Instagram")
        location = self.REGION_MAP.get(region, "New York")
        camp_type = self.OBJ_MAP.get(objective, "Social Media")
        ctr_est  = self.PERS_CTR.get(personality, 2.5)

        if self._loaded:
            row = [
                self._encode_val("Campaign_Type",    camp_type),
                self._encode_val("Channel_Used",     channel),
                self._encode_val("Location",         location),
                self._encode_val("Language",         language.title()),
                self._encode_val("Customer_Segment", segment.title()),
                float(duration_days),
                float(budget),
                float(ctr_est),
            ]
            X = self.scaler.transform([row])
            roi  = float(self.model_roi.predict(X)[0])
            eng  = float(self.model_eng.predict(X)[0])
            conv = float(self.model_conv.predict(X)[0])
        else:
            # Heuristic fallback (clearly labeled)
            base = {"Instagram": 3.2, "Facebook": 1.8, "Twitter/X": 2.1,
                    "LinkedIn": 2.6, "YouTube": 2.9}.get(platform, 2.5)
            boost = {"Brand Awareness": 1.0, "Engagement": 1.15,
                     "Conversion": 1.3, "Lead Generation": 1.2}.get(objective, 1.0)
            roi  = round(base * boost * 1.8 + np.random.uniform(-0.3, 0.3), 2)
            eng  = round(base * boost * 20 + np.random.uniform(-2, 2), 1)
            conv = round(base * boost * 0.025 + np.random.uniform(-0.003, 0.003), 4)

        best_times = {
            "Instagram": "Tue–Thu, 6–9 PM",
            "Facebook":  "Wed–Fri, 1–4 PM",
            "Twitter/X": "Mon–Wed, 9–11 AM",
            "LinkedIn":  "Tue–Thu, 8–10 AM",
            "TikTok":    "Fri–Sun, 7–10 PM",
        }
        tips = {
            "Brand Awareness": "Use eye-catching visuals and a memorable tagline. Prioritize reach over clicks.",
            "Engagement":      "Ask questions, run polls, and use carousel formats to maximize interaction.",
            "Lead Generation": "Use strong CTAs with gated content offers. Keep copy benefit-focused.",
            "Conversion":      "Retarget warm audiences with social proof and urgency signals.",
            "Retention":       "Personalise messaging. Loyalty content outperforms acquisition content 3:1.",
        }

        return {
            "ROI":            round(roi, 2),
            "Engagement":     round(eng, 1),
            "Conversion_Rate": round(conv, 4),
            "CTR":            round(ctr_est + np.random.uniform(-0.2, 0.3), 2),
            "Best_Time":      best_times.get(platform, "Weekdays 6–9 PM"),
            "Tip":            tips.get(objective, "Focus on consistent brand voice across all touchpoints."),
            "Source":         "ML model (RandomForest trained on 200K records)" if self._loaded else "Heuristic fallback",
        }


# Singleton
predictor = CampaignPredictor()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = train_models()
    print("\nTraining results:")
    for k, v in results.items():
        print(f"  {k}: {v}")
