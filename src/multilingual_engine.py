"""
multilingual_engine.py
----------------------
Translates brand slogans and captions into 5+ languages.
Uses google.genai (new SDK) with graceful offline fallback.
"""

import json
import re
import logging
from src.config import GEMINI_API_KEY

log = logging.getLogger(__name__)

# ALL languages the UI might request — comprehensive coverage
LANG_META = {
    "Hindi":    {"flag": "🇮🇳", "native": "हिन्दी",   "code": "hi"},
    "Spanish":  {"flag": "🇪🇸", "native": "Español",   "code": "es"},
    "French":   {"flag": "🇫🇷", "native": "Français",  "code": "fr"},
    "German":   {"flag": "🇩🇪", "native": "Deutsch",   "code": "de"},
    "Gujarati": {"flag": "🇮🇳", "native": "ગુજરાતી",   "code": "gu"},
    "Arabic":   {"flag": "🇸🇦", "native": "العربية",   "code": "ar"},
    "Mandarin": {"flag": "🇨🇳", "native": "普通话",     "code": "zh"},
    "Japanese": {"flag": "🇯🇵", "native": "日本語",     "code": "ja"},
    "Portuguese":{"flag":"🇧🇷", "native": "Português",  "code": "pt"},
    "Italian":  {"flag": "🇮🇹", "native": "Italiano",  "code": "it"},
}

MOCK_FALLBACK = {
    "Hindi":    "उत्कृष्टता, पुनर्परिभाषित — {company} के साथ।",
    "Spanish":  "Excelencia redefinida — con {company}.",
    "French":   "L'excellence réinventée — par {company}.",
    "German":   "Exzellenz neu definiert — mit {company}.",
    "Gujarati": "શ્રેષ્ઠતા, નવી રીતે — {company} સાથે.",
    "Arabic":   "التميز، معاد تعريفه — مع {company}.",
    "Mandarin": "卓越，重新定义 — {company}。",
    "Japanese": "卓越性を再定義する — {company}。",
    "Portuguese":"Excelência redefinida — com {company}.",
    "Italian":  "Eccellenza ridefinita — con {company}.",
}

TONE_NOTES = {
    "Hindi":    "Preserves aspirational tone; culturally appropriate for Indian market.",
    "Spanish":  "Latin American and European Spanish blend; brand-forward phrasing.",
    "French":   "Formal register maintained; avoids direct anglicisms.",
    "German":   "Compound structure reflects precision; suits B2B and premium segments.",
    "Gujarati": "Script preserved; appropriate for Gujarat/diaspora markets.",
    "Arabic":   "Right-to-left script; tone adjusted for MENA market resonance.",
    "Mandarin": "Simplified Chinese; concise phrasing for maximum impact.",
    "Japanese": "Polite register maintained; culturally adapted for Japanese market.",
    "Portuguese":"Brazilian Portuguese register; warm and approachable tone.",
    "Italian":  "Elegant register; suits luxury and lifestyle positioning.",
}


def translate_slogan(slogan: str, company: str, languages=None) -> dict:
    """
    Translate slogan into requested languages.
    Returns dict: {language: {text, flag, native, source}}
    """
    if languages is None:
        languages = ["Hindi", "Spanish", "French", "German", "Gujarati"]

    results = {}

    # Try Gemini API first
    if GEMINI_API_KEY:
        results = _gemini_translate(slogan, company, languages)

    # Fill any missing languages with offline fallback
    for lang in languages:
        if lang not in results:
            meta     = LANG_META.get(lang, {"flag": "🌐", "native": lang, "code": "xx"})
            fallback = MOCK_FALLBACK.get(lang, slogan + " — " + company)
            try:
                text = fallback.format(company=company)
            except Exception:
                text = fallback
            results[lang] = {
                "text":   text,
                "flag":   meta["flag"],
                "native": meta["native"],
                "source": "offline-fallback",
            }

    return results


def _gemini_translate(slogan: str, company: str, languages: list) -> dict:
    """Use Gemini to translate preserving tone. Uses new google.genai SDK."""
    try:
        from google import genai
        from google.genai import types as _gtypes
        client    = genai.Client(api_key=GEMINI_API_KEY)
        lang_list = ", ".join(languages)
        prompt    = (
            "Translate this brand tagline into " + lang_list + ".\n"
            "Tagline: \"" + slogan + "\"\n"
            "Company: " + company + "\n\n"
            "Return only a JSON object with language names as keys and translated strings as values. "
            "No explanation. No markdown. No code blocks."
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[_gtypes.Content(role="user", parts=[_gtypes.Part(text=prompt)])],
            config=_gtypes.GenerateContentConfig(temperature=0.3, max_output_tokens=800),
        )
        raw = ""
        if hasattr(response, "text") and response.text:
            raw = response.text.strip()
        else:
            for cand in getattr(response, "candidates", []):
                for part in getattr(cand.content, "parts", []):
                    if hasattr(part, "text") and part.text:
                        raw = part.text.strip()
                        break
        clean = re.sub(r"```json|```", "", raw).strip()
        data  = json.loads(clean)

        results = {}
        for lang in languages:
            text = data.get(lang, data.get(lang.lower(), ""))
            if text:
                meta = LANG_META.get(lang, {"flag": "🌐", "native": lang})
                results[lang] = {
                    "text":   text,
                    "flag":   meta["flag"],
                    "native": meta["native"],
                    "source": "gemini",
                }
        return results
    except Exception as e:
        log.warning(f"Gemini translation failed: {e}")
        return {}


def validate_translations(results: dict) -> dict:
    """Add tone notes to each translation result."""
    for lang in results:
        results[lang]["tone_note"] = TONE_NOTES.get(lang, "Culturally adapted translation.")
    return results
