# BrandSphere AI
### AI-Powered Automated Branding Assistant for Businesses
**CRS AI Capstone 2025–26 | Scenario 1**

> Generate complete brand identities in minutes — logos, taglines, colour palettes, campaigns, multilingual kits — powered by ML, NLP, and Generative AI.

---

## Problem Statement

SMBs spend thousands of dollars and weeks on brand identity work that is repetitive, inconsistent, and inaccessible. BrandSphere AI automates the full pipeline from brand input to downloadable kit using real ML models and generative AI.

---

## Architecture

```
User Input → palette_engine (KMeans) → logo_engine (SVG)
           → font_engine (rule-based) → slogan_engine (NLTK+Gemini)
           → campaign_predictor (RandomForest) → multilingual_engine
           → animation_engine (Pillow GIF) → export_engine (ZIP)
           → feedback_engine (CSV+Plotly) → Streamlit Cloud
```

---

## Datasets

| Dataset | Rows | Used For |
|---|---|---|
| marketing_campaign_dataset.csv | 200,000 | KPI prediction (RF model) |
| startups.csv | 42,038 | Persona profiling |
| sloganlist.csv | optional | TF-IDF retrieval |

**Honesty notes:** Logo = SVG-based (no image dataset). Font = rule-based. Campaign R²≈0 = synthetic dataset. All documented in code and models/training_results.json.

---

## Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/brandsphere-ai.git
cd brandsphere-ai
pip install -r requirements.txt
cp .env.example .env  # add GEMINI_API_KEY
python src/preprocess.py
python src/campaign_predictor.py
streamlit run app.py
```

## Streamlit Cloud

1. Push to GitHub (include models/ folder)
2. share.streamlit.io → connect repo → main file: app.py
3. Secrets: GEMINI_API_KEY = "your_key"

---

## Team
Aashi Dimple Soni (2405728) · Hemer Manish Pandya (2405426) · Zivantika Amit Singh (2405744)
