"""
dashboard_engine.py
-------------------
Plotly chart builders for Analytics and Feedback dashboards.
All charts use the dark BrandSphere theme.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.config import REGIONS


DARK = dict(
    paper_bgcolor="#141518",
    plot_bgcolor="#141518",
    font_color="#F0EDE8",
    font_family="DM Sans",
    margin=dict(t=48, b=20, l=20, r=20),
)
GRID  = dict(gridcolor="#2A2C31")
GOLD  = "#C9A84C"
TEAL  = "#3ECFB2"
RED   = "#E05A5A"
MUTED = "#7A7A85"


def kpi_bar_chart(kpis: dict) -> go.Figure:
    """Compare predicted KPIs vs industry averages."""
    industry_avg = {"CTR (%)": 2.4, "ROI (×)": 3.2, "Engagement (/10)": 6.1}
    predicted    = {
        "CTR (%)":         kpis.get("CTR", 2.5),
        "ROI (×)":         round(kpis.get("ROI", 3.0), 2),
        "Engagement (/10)": round(kpis.get("Engagement", 6.5), 1),
    }
    metrics = list(predicted.keys())
    fig = go.Figure()
    fig.add_bar(name="Your Brand", x=metrics, y=list(predicted.values()),
                marker_color=GOLD, text=[str(v) for v in predicted.values()],
                textposition="outside")
    fig.add_bar(name="Industry Avg", x=metrics, y=list(industry_avg.values()),
                marker_color=MUTED)
    fig.update_layout(**DARK, barmode="group", height=300,
                      title=dict(text="Predicted KPIs vs Industry Average",
                                 font_color=GOLD, font_size=14),
                      legend=dict(bgcolor="#141518"),
                      xaxis=GRID, yaxis=GRID)
    return fig


def regional_engagement_map(region_scores: dict) -> go.Figure:
    """World choropleth of regional engagement scores."""
    iso_map = {
        "North America": "USA", "Europe": "DEU", "Asia Pacific": "CHN",
        "Middle East": "SAU",   "Latin America": "BRA", "Africa": "NGA",
        "South Asia": "IND",
    }
    locations = [iso_map.get(r, "USA") for r in region_scores]
    values    = list(region_scores.values())
    fig = go.Figure(go.Choropleth(
        locations=locations, z=values, locationmode="ISO-3",
        colorscale=[[0, "#1B3A6B"], [0.5, GOLD], [1, TEAL]],
        showscale=True, colorbar_title="Score",
    ))
    fig.update_layout(**DARK, height=320,
                      title=dict(text="Regional Engagement Prediction",
                                 font_color=GOLD, font_size=14),
                      geo=dict(bgcolor="#141518", showframe=False,
                               showcoastlines=True, coastlinecolor="#2A2C31",
                               landcolor="#1C1E22"))
    return fig


def personality_radar(personality: str) -> go.Figure:
    """Brand personality radar chart."""
    PERS_DATA = {
        "Minimalist":   {"Vibrancy": 30, "Trust": 82, "Innovation": 70,
                         "Elegance": 75, "Energy": 38, "Simplicity": 95},
        "Vibrant":      {"Vibrancy": 92, "Trust": 55, "Innovation": 78,
                         "Elegance": 40, "Energy": 95, "Simplicity": 30},
        "Luxury":       {"Vibrancy": 52, "Trust": 88, "Innovation": 60,
                         "Elegance": 97, "Energy": 52, "Simplicity": 62},
        "Bold":         {"Vibrancy": 86, "Trust": 58, "Innovation": 82,
                         "Elegance": 44, "Energy": 96, "Simplicity": 38},
        "Elegant":      {"Vibrancy": 45, "Trust": 84, "Innovation": 55,
                         "Elegance": 96, "Energy": 44, "Simplicity": 67},
        "Playful":      {"Vibrancy": 88, "Trust": 60, "Innovation": 70,
                         "Elegance": 35, "Energy": 90, "Simplicity": 42},
        "Professional": {"Vibrancy": 35, "Trust": 90, "Innovation": 62,
                         "Elegance": 70, "Energy": 48, "Simplicity": 72},
    }
    data = PERS_DATA.get(personality, PERS_DATA["Professional"])
    cats, vals = list(data.keys()), list(data.values())
    fig = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]], theta=cats + [cats[0]],
        fill="toself", fillcolor=f"rgba(201,168,76,0.15)",
        line=dict(color=GOLD, width=2), marker=dict(color=GOLD),
    ))
    fig.update_layout(**DARK, height=360,
                      polar=dict(
                          bgcolor="#1C1E22",
                          radialaxis=dict(visible=True, range=[0, 100],
                                          gridcolor="#2A2C31", color=MUTED),
                          angularaxis=dict(gridcolor="#2A2C31", color="#F0EDE8"),
                      ),
                      title=dict(text=f"Brand Personality — {personality}",
                                 font_color=GOLD, font_size=14))
    return fig


def feedback_bar(df: pd.DataFrame) -> go.Figure:
    """Ratings by module bar chart."""
    fig = px.bar(df, x="module", y="rating", color="sentiment",
                 color_discrete_map={"positive": TEAL, "neutral": GOLD, "negative": RED},
                 title="Ratings by Module", labels={"module": "Module", "rating": "Rating"})
    fig.update_layout(**DARK, height=280, xaxis=dict(**GRID, tickangle=-20),
                      yaxis=GRID, legend=dict(bgcolor="#141518"),
                      title_font_color=GOLD)
    return fig


def feedback_pie(df: pd.DataFrame) -> go.Figure:
    """Sentiment distribution donut chart."""
    counts = df["sentiment"].value_counts().reset_index()
    counts.columns = ["Sentiment", "Count"]
    fig = px.pie(counts, names="Sentiment", values="Count",
                 color="Sentiment",
                 color_discrete_map={"positive": TEAL, "neutral": GOLD, "negative": RED},
                 hole=0.55, title="Sentiment Distribution")
    fig.update_layout(**DARK, height=280, legend=dict(bgcolor="#141518"),
                      title_font_color=GOLD)
    return fig


def campaign_scatter(platforms: list, ctrs: list, rois: list, engagements: list) -> go.Figure:
    """Platform KPI bubble scatter chart."""
    fig = px.scatter(
        x=ctrs, y=rois, size=engagements, text=platforms,
        color=platforms, color_discrete_sequence=[GOLD, TEAL, RED, "#A29BFE", "#74B9FF"],
        title="Platform KPI Comparison", labels={"x": "CTR (%)", "y": "ROI (×)"},
        size_max=60,
    )
    fig.update_layout(**DARK, height=340, xaxis=GRID, yaxis=GRID,
                      legend=dict(bgcolor="#141518"), title_font_color=GOLD)
    return fig
