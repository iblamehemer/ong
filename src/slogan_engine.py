"""
slogan_engine.py
----------------
Tagline / slogan generation engine.

Pipeline:
  1. TF-IDF retrieval from real slogans corpus (sloganlist.csv or fallback)
  2. Template-based generation using tone/industry mapping
  3. NLTK preprocessing for analysis
  4. Optional Gemini API enhancement

DATA SOURCE TRANSPARENCY:
  - Corpus: sloganlist.csv (if uploaded) or built-in fallback of 50 real brand slogans
  - TF-IDF: trained on corpus at runtime (sklearn)
  - NLTK: tokenization + stopword removal + stemming (Week 4 NLP requirement)
  - Gemini: optional API enhancement when key is present
"""

import re
import string
import random
import logging
import pandas as pd
import numpy as np

# NLTK
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import SLOGANS_CLEAN, GEMINI_API_KEY

log = logging.getLogger(__name__)

# ── NLTK setup ─────────────────────────────────────────────────────────────────
def _init_nltk():
    for pkg in ["punkt", "punkt_tab", "stopwords"]:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass

_init_nltk()


# ── Templates by tone ──────────────────────────────────────────────────────────
TEMPLATES = {
    "Formal": [
        "{company}: Precision. Performance. Purpose.",
        "Excellence through {industry} innovation — {company}.",
        "{company}. Where expertise meets execution.",
        "Trusted by leaders in {industry}. That's {company}.",
        "Defining the future of {industry}.",
    ],
    "Bold": [
        "{company}: Make them remember you.",
        "Lead. Don't follow. {company}.",
        "Built to dominate {industry}.",
        "{company} — Fearless by design.",
        "The {industry} disruptor. We're {company}.",
    ],
    "Youthful": [
        "{company}: Your kind of {industry}.",
        "Fresh. Fast. {company}.",
        "Level up your {industry} game with {company}.",
        "{company} — because boring is not an option.",
        "We get {audience}. We are {company}.",
    ],
    "Inspirational": [
        "{company}: Where possibilities begin.",
        "Dream bigger. Build bolder. {company}.",
        "{company} — Empowering {audience} every day.",
        "Your journey. Our mission. {company}.",
        "The {industry} that believes in you.",
    ],
    "Professional": [
        "{company}: Delivering results that matter.",
        "Strategic {industry} solutions — {company}.",
        "{company}. Built for the way you work.",
        "Your trusted {industry} partner.",
        "Performance-driven. {company}.",
    ],
    "Playful": [
        "{company}: Because life's too short for boring {industry}.",
        "Smile. It's {company}.",
        "{company} — Happy {audience}, happy world.",
        "Making {industry} fun, one step at a time.",
        "{company}: Seriously good. Seriously fun.",
    ],
    "Trustworthy": [
        "{company}: Your {industry} partner, always.",
        "Reliability you can count on — {company}.",
        "{company}. Real people. Real results.",
        "Built on trust. Built for {audience}.",
        "Every promise kept. {company}.",
    ],
}


# ── NLTK analysis ──────────────────────────────────────────────────────────────

def nltk_analyze(text: str) -> dict:
    """
    Tokenize, clean, and analyse a tagline using NLTK.
    Returns dict with tokens, stems, unique words, avg word length.
    (Week 4 NLP preprocessing requirement)
    """
    try:
        tokens     = word_tokenize(text.lower())
        stop_words = set(stopwords.words("english"))
        stemmer    = PorterStemmer()
        clean_toks = [t for t in tokens if t not in stop_words and t not in string.punctuation]
        stems      = [stemmer.stem(t) for t in clean_toks]
        return {
            "token_count":    len(tokens),
            "clean_tokens":   clean_toks,
            "stems":          stems,
            "word_count":     len(clean_toks),
            "avg_word_len":   round(sum(len(t) for t in clean_toks) / max(1, len(clean_toks)), 1),
            "unique_words":   len(set(clean_toks)),
            "lexical_density": round(len(set(clean_toks)) / max(1, len(clean_toks)), 2),
        }
    except Exception:
        words = text.split()
        return {"token_count": len(words), "clean_tokens": words, "stems": words,
                "word_count": len(words), "avg_word_len": 5.0,
                "unique_words": len(set(words)), "lexical_density": 0.8}


# ── TF-IDF retrieval ───────────────────────────────────────────────────────────

class SloganRetriever:
    """Retrieve semantically similar slogans from corpus using TF-IDF."""

    def __init__(self):
        self._fitted = False
        self._df     = None
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
        self._matrix = None

    def fit(self, df: pd.DataFrame):
        self._df = df.copy()
        corpus   = df["slogan_clean"].fillna("").tolist()
        self._matrix = self._vectorizer.fit_transform(corpus)
        self._fitted = True
        log.info(f"TF-IDF fitted on {len(corpus)} slogans.")

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        if not self._fitted:
            return []
        q_vec = self._vectorizer.transform([query.lower()])
        sims  = cosine_similarity(q_vec, self._matrix)[0]
        idxs  = np.argsort(sims)[::-1][:top_k]
        return [self._df.iloc[i]["Slogan"] for i in idxs if sims[i] > 0.01]


_retriever = SloganRetriever()


def _load_retriever():
    """Lazy-load TF-IDF retriever from cleaned slogans."""
    if _retriever._fitted:
        return
    if SLOGANS_CLEAN.exists():
        df = pd.read_csv(SLOGANS_CLEAN)
        if "Slogan" in df.columns and "slogan_clean" in df.columns:
            _retriever.fit(df)


# ── Template generation ────────────────────────────────────────────────────────

def _fill_template(template: str, company: str, industry: str, audience: str) -> str:
    industry_short = industry.split("/")[0].strip().lower()
    return (template
            .replace("{company}", company)
            .replace("{industry}", industry_short)
            .replace("{audience}", audience or "customers"))


def generate_from_templates(company: str, industry: str, tone: str,
                             audience: str, n: int = 5) -> list[dict]:
    """Generate taglines from tone-specific templates."""
    templates = TEMPLATES.get(tone, TEMPLATES["Professional"])
    selected  = random.sample(templates, min(n, len(templates)))
    results = []
    for t in selected:
        text = _fill_template(t, company, industry, audience)
        results.append({"text": text, "source": "template", "tone": tone})
    return results


# ── Gemini enhancement ─────────────────────────────────────────────────────────

def _gemini_slogans(company: str, industry: str, tone: str, audience: str,
                    hint: str = "", n: int = 5) -> list[dict]:
    """Use Gemini to generate/refine slogans. Returns [] if key missing."""
    if not GEMINI_API_KEY:
        return []
    try:
        from google import genai as _genai
        client = _genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            f"Generate {n} unique, memorable brand taglines for:\n"
            f"  Company: {company}\n  Industry: {industry}\n  Tone: {tone}\n"
            f"  Target audience: {audience or 'general consumers'}\n"
            f"  Hint: {hint or 'none'}\n\n"
            "Return a numbered list only. One tagline per line. No explanation."
        )
        resp  = model.generate_content(prompt)
        lines = [l.strip() for l in resp.text.strip().split("\n") if l.strip()]
        slogans = []
        for l in lines[:n]:
            clean = re.sub(r"^[\d\.\*\-\s]+", "", l).strip().strip('"')
            if clean:
                slogans.append({"text": clean, "source": "gemini", "tone": tone})
        return slogans
    except Exception as e:
        log.warning(f"Gemini slogan generation failed: {e}")
        return []


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_slogans(company: str, industry: str, tone: str,
                     audience: str = "", hint: str = "",
                     n: int = 5) -> list[dict]:
    """
    Main entry point: generate n brand taglines.
    Strategy: Gemini (if key) → template-based → TF-IDF retrieved inspiration
    Returns list of dicts: [{text, source, tone, analysis}]
    """
    results = []

    # 1. Gemini (best quality, needs API key)
    gemini_results = _gemini_slogans(company, industry, tone, audience, hint, n)
    results.extend(gemini_results)

    # 2. Template-based (reliable offline)
    needed = n - len(results)
    if needed > 0:
        results.extend(generate_from_templates(company, industry, tone, audience, needed))

    # 3. Retrieval-based inspiration
    _load_retriever()
    query = f"{industry} {tone} {audience}"
    retrieved = _retriever.retrieve(query, top_k=3)

    # Attach NLTK analysis to each
    for r in results:
        r["analysis"] = nltk_analyze(r["text"])

    return results[:n], retrieved
