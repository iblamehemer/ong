"""
export_engine.py
----------------
Assembles and packages the complete brand kit as a downloadable ZIP.

Contents:
  - logo SVGs (all 5 variants)
  - color palette JSON + text summary
  - font recommendations
  - taglines
  - brand story
  - multilingual translations
  - campaign captions + hashtags
  - KPI predictions
  - brand consistency report
  - animation GIF
  - README.md summary
"""

import io
import json
import zipfile
import datetime
from pathlib import Path


def build_brand_kit_zip(
    company: str,
    industry: str,
    personality: str,
    logos: list[dict],
    palette: dict,
    fonts: list[dict],
    slogans: list[dict],
    brand_story: str,
    translations: dict,
    campaigns: dict,
    kpis: dict,
    aesthetics: dict,
    gif_bytes: bytes = None,
) -> bytes:
    """
    Package all brand assets into a ZIP file.
    Returns ZIP bytes for st.download_button.
    """
    buf = io.BytesIO()
    ts  = datetime.datetime.now().strftime("%Y-%m-%d")

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:

        # ── Logos ────────────────────────────────────────────────────────────
        for logo in logos:
            fname = f"logos/{logo['style'].replace(' ', '_')}.svg"
            zf.writestr(fname, logo["svg"])

        # ── Palette ──────────────────────────────────────────────────────────
        palette_data = {
            name: {"hex": v["hex"], "role": v["role"], "psychology": v["psychology"]}
            for name, v in palette.items()
        }
        zf.writestr("branding/color_palette.json", json.dumps(palette_data, indent=2))

        palette_txt = f"# {company} — Color Palette\nGenerated: {ts}\n\n"
        for name, v in palette.items():
            palette_txt += f"{name}: {v['hex']}  ({v['role']}) — {v['psychology']}\n"
        zf.writestr("branding/color_palette.txt", palette_txt)

        # ── Fonts ─────────────────────────────────────────────────────────────
        font_txt = f"# {company} — Font Recommendations\n\n"
        for f in fonts:
            font_txt += (
                f"{f['rank']}\n"
                f"  Heading:   {f['heading']}\n"
                f"  Body:      {f['body']}\n"
                f"  Alternate: {f['alternate']}\n"
                f"  Class:     {f['classification']}\n"
                f"  Rationale: {f['rationale']}\n\n"
            )
        zf.writestr("branding/font_recommendations.txt", font_txt)

        # ── Slogans ───────────────────────────────────────────────────────────
        slogan_txt = f"# {company} — Brand Taglines\n\n"
        for i, s in enumerate(slogans, 1):
            slogan_txt += f'{i}. "{s["text"]}"\n   Tone: {s["tone"]}  |  Source: {s["source"]}\n\n'
        zf.writestr("content/taglines.txt", slogan_txt)

        # ── Brand story ───────────────────────────────────────────────────────
        if brand_story:
            zf.writestr("content/brand_story.txt", brand_story)

        # ── Translations ──────────────────────────────────────────────────────
        if translations:
            trans_txt = f"# {company} — Multilingual Taglines\n\n"
            for lang, data in translations.items():
                src = data.get("source", "unknown")
                trans_txt += f"[{data['flag']} {lang} ({data['native']})]\n"
                trans_txt += f"  {data['text']}\n"
                trans_txt += f"  Source: {src}\n\n"
            zf.writestr("content/multilingual_taglines.txt", trans_txt)

        # ── Campaigns ─────────────────────────────────────────────────────────
        if campaigns:
            camp_txt = f"# {company} — Campaign Content\n\n"
            for platform, data in campaigns.items():
                camp_txt += f"## {platform}\n"
                camp_txt += f"Caption:\n{data.get('caption', '')}\n\n"
                hashtags = data.get("hashtags", [])
                camp_txt += "Hashtags:\n" + " ".join(hashtags) + "\n\n"
                if data.get("regional_strategy"):
                    camp_txt += f"Regional Strategy:\n{data['regional_strategy']}\n\n"
                camp_txt += "---\n"
            zf.writestr("campaigns/campaign_content.txt", camp_txt)

        # ── KPI predictions ───────────────────────────────────────────────────
        if kpis:
            kpi_txt = f"# {company} — Campaign KPI Predictions\nSource: {kpis.get('Source','')}\n\n"
            for k, v in kpis.items():
                if k != "Source":
                    kpi_txt += f"  {k}: {v}\n"
            zf.writestr("analytics/kpi_predictions.txt", kpi_txt)

        # ── Aesthetics report ─────────────────────────────────────────────────
        if aesthetics:
            aes_txt = f"# {company} — Brand Consistency Report\n\n"
            aes_txt += f"Overall Score: {aesthetics.get('overall', '—')}/100\n"
            aes_txt += f"Grade: {aesthetics.get('grade', '—')}\n\n"
            aes_txt += "Dimension Scores:\n"
            for dim, score in aesthetics.get("dimensions", {}).items():
                aes_txt += f"  {dim}: {score}/100\n"
            aes_txt += "\nRecommendations:\n"
            for rec in aesthetics.get("recommendations", []):
                aes_txt += f"  • {rec}\n"
            zf.writestr("analytics/brand_consistency_report.txt", aes_txt)

        # ── Animation ────────────────────────────────────────────────────────
        if gif_bytes:
            zf.writestr("animation/brand_animation.gif", gif_bytes)

        # ── README ────────────────────────────────────────────────────────────
        readme = f"""# {company} — BrandSphere AI Brand Kit
Generated: {ts}
Platform: BrandSphere AI | CRS AI Capstone 2025–26

## Contents
- logos/              → 5 SVG logo concepts
- branding/           → Color palette (JSON + TXT), Font recommendations
- content/            → Taglines, Brand story, Multilingual translations
- campaigns/          → Social media captions, hashtags, regional strategy
- analytics/          → KPI predictions, Brand consistency report
- animation/          → Animated brand GIF

## About BrandSphere AI
AI-powered branding assistant built with:
  Python · Streamlit · Gemini API · scikit-learn · NLTK · Pillow

Team: Aashi Dimple Soni | Hemer Manish Pandya | Zivantika Amit Singh
"""
        zf.writestr("README.md", readme)

    return buf.getvalue()
