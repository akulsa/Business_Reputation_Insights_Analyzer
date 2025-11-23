# preprocess.py
import re
import pandas as pd


def clean_text(text: str) -> str:
    """
    Basic text cleaning: remove URLs, emojis, special chars, extra spaces.
    """
    if not isinstance(text, str):
        return ""

    # Remove URLs
    text = re.sub(r"http\S+|www\.\S+", "", text)

    # Remove emojis and non-alphanumeric chars (keep basic punctuation)
    text = re.sub(r"[^A-Za-z0-9\s\.,!?']", " ", text)

    # Lowercase
    text = text.lower()

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def preprocess_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a 'clean_text' column to the reviews DataFrame.
    Expects 'text' column.
    """
    df = df.copy()
    if "text" not in df.columns:
        raise ValueError("Input DataFrame must have a 'text' column")

    df["clean_text"] = df["text"].astype(str).apply(clean_text)
    return df
