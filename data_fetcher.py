# data_fetcher.py
import requests
import pandas as pd
from typing import List, Dict
from config import SERPAPI_API_KEY, DEFAULT_HL

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


def fetch_google_maps_reviews(place_id: str, api_key: str = None, hl: str = DEFAULT_HL) -> pd.DataFrame:
    """
    Fetch reviews from Google Maps using SerpAPI.

    :param place_id: Google Maps place_id of the business
    :param api_key: SerpAPI key; if None, will use from config
    :param hl: language code
    :return: DataFrame with columns: author, rating, date, text
    """
    if api_key is None:
        api_key = SERPAPI_API_KEY

    if not api_key:
        raise ValueError("SERPAPI_API_KEY is not set. Please configure it in .env or config.py")

    params = {
        "engine": "google_maps_reviews",
        "place_id": place_id,
        "hl": hl,
        "api_key": api_key,
    }

    r = requests.get(SERPAPI_ENDPOINT, params=params)
    r.raise_for_status()
    data = r.json()

    reviews = data.get("reviews", [])

    if not reviews:
        return pd.DataFrame(columns=["author", "rating", "date", "text"])

    rows: List[Dict] = []
    for rev in reviews:
        rows.append({
            "author": rev.get("user", ""),
            "rating": rev.get("rating", None),
            "date": rev.get("date", ""),
            "text": rev.get("snippet", "") or rev.get("review", ""),
        })

    df = pd.DataFrame(rows)
    return df
