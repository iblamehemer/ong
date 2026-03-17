# BrandSphere AI — System Architecture

## Module Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│                    Streamlit (10 tabs)                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   palette_engine         logo_engine          font_engine
   (KMeans, Week 5)   (SVG gen, Week 2)   (rule-based, Week 3)
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   slogan_engine        campaign_predictor   aesthetics_engine
  (NLTK+Gemini, W4)    (RF+Ridge, Week 7)   (scoring, Module 4)
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
  multilingual_engine   animation_engine    feedback_engine
   (Gemini, Week 8)    (Pillow, Week 6)   (CSV+Plotly, Week 9)
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
                        export_engine
                      (ZIP kit, Week 10)
```

## Data Flow
1. User enters brand inputs (company, industry, personality, tone, audience)
2. All src/ modules run in parallel (palette, logo, font, slogan)
3. Aesthetics engine scores cross-module coherence
4. Campaign predictor uses saved ML models for KPI predictions
5. Multilingual engine translates top slogan into 5 languages
6. Animation engine renders GIF with palette + slogan
7. Export engine packages all assets into downloadable ZIP
8. Feedback engine persists ratings to CSV for analytics
