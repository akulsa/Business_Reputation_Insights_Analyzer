# analysis_pipeline.py
import pandas as pd
from transformers import pipeline
from typing import Dict, List
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

# Initialize OpenAI client
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please configure it in .env or config.py")

client = OpenAI(api_key=OPENAI_API_KEY)

# Hugging Face sentiment pipeline
_sentiment_pipeline = pipeline("sentiment-analysis")


def _call_llm(prompt: str, temperature: float = 0.3) -> str:
    """
    Generic helper to call OpenAI chat completion.
    """
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert business analyst for local businesses."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def add_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Uses Hugging Face sentiment model to classify reviews.
    Maps labels to: positive / negative / neutral
    """
    df = df.copy()

    sentiments = _sentiment_pipeline(df["clean_text"].tolist())

    labels = []
    scores = []
    for result in sentiments:
        label = result["label"].lower()
        score = result["score"]

        if "pos" in label:
            mapped = "positive"
        elif "neg" in label:
            mapped = "negative"
        else:
            mapped = "neutral"

        labels.append(mapped)
        scores.append(score)

    df["sentiment"] = labels
    df["sentiment_score"] = scores

    return df


def extract_themes(df: pd.DataFrame, max_reviews: int = 50) -> Dict[str, List[str]]:
    """
    Ask the LLM to extract key recurring themes from a sample of reviews.
    Returns a dict like:
    {
        "positive": ["friendly staff", "clean ambience"],
        "negative": ["slow service", "high prices"]
    }
    """
    sample_df = df.head(max_reviews)
    joined_text = "\n".join(sample_df["clean_text"].tolist())

    prompt = f"""
You are analyzing customer reviews for a local business.

Reviews:
{joined_text}

1. Identify the main recurring positive themes (e.g., 'friendly staff', 'good ambience').
2. Identify the main recurring negative themes (e.g., 'slow service', 'high prices').

Return your answer strictly in JSON with the following structure:
{{
  "positive": ["theme1", "theme2", ...],
  "negative": ["theme1", "theme2", ...]
}}
"""

    raw = _call_llm(prompt)
    # Very simple "best effort" JSON parse – user can improve later if needed
    import json
    try:
        themes = json.loads(raw)
        if not isinstance(themes, dict):
            raise ValueError
    except Exception:
        # fallback: wrap in a dict
        themes = {"positive": [], "negative": [], "raw": raw}

    return themes


def summarize_reviews(df: pd.DataFrame, max_reviews: int = 100) -> str:
    """
    Summarize the overall customer feedback.
    """
    sample_df = df.head(max_reviews)
    joined_text = "\n".join(sample_df["clean_text"].tolist())

    prompt = f"""
Summarize the following customer reviews for a local business.
Focus on:
- Overall customer satisfaction
- Main strengths
- Main weaknesses
- Important patterns or trends

Reviews:
{joined_text}
"""

    summary = _call_llm(prompt)
    return summary


def generate_recommendations(df: pd.DataFrame, themes: Dict[str, List[str]]) -> str:
    """
    Generate actionable recommendations based on sentiment and themes.
    """
    total_reviews = len(df)
    sentiment_counts = df["sentiment"].value_counts().to_dict()

    prompt = f"""
You are an expert operations consultant.

A local business has {total_reviews} reviews on Google Maps.

Sentiment distribution:
{sentiment_counts}

Positive themes:
{themes.get('positive', [])}

Negative themes:
{themes.get('negative', [])}

Based on this information:
- Suggest 5–10 highly actionable operational improvements.
- Be specific (e.g., 'add one more staff member during evening peak hours', not just 'improve service').
- Group them under short headings if possible.

Respond in bullet points.
"""

    recs = _call_llm(prompt)
    return recs


def compute_basic_stats(df: pd.DataFrame) -> Dict:
    """
    Return a few basic stats for the dashboard.
    """
    stats = {}
    stats["total_reviews"] = len(df)
    stats["avg_rating"] = float(df["rating"].mean()) if "rating" in df.columns else None
    stats["sentiment_counts"] = df["sentiment"].value_counts().to_dict()

    return stats
