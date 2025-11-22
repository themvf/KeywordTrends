import re
from collections import Counter
from typing import Dict, Iterable, List, Tuple

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


STOPWORDS = set(
    [
        "and",
        "or",
        "the",
        "a",
        "an",
        "to",
        "for",
        "of",
        "in",
        "on",
        "with",
        "by",
        "at",
        "from",
        "video",
        "official",
        "product",
        "shop",
    ]
)


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\s#]+", " ", text.lower())
    tokens = [t for t in cleaned.split() if t not in STOPWORDS and len(t) > 2]
    return " ".join(tokens)


def extract_ngrams(texts: Iterable[str], n: int = 1, max_features: int = 500) -> Tuple[List[str], List[int]]:
    try:
        vectorizer = CountVectorizer(ngram_range=(n, n), max_features=max_features)
        matrix = vectorizer.fit_transform(texts)
        counts = matrix.sum(axis=0).A1
        terms = vectorizer.get_feature_names_out()
        return list(terms), list(counts)
    except ValueError:
        # Handle empty vocabulary (e.g., empty input or only stop words)
        return [], []


def tfidf_keywords(texts: Iterable[str], max_features: int = 500) -> Dict[str, float]:
    try:
        vectorizer = TfidfVectorizer(max_features=max_features)
        matrix = vectorizer.fit_transform(texts)
        scores = matrix.sum(axis=0).A1
        terms = vectorizer.get_feature_names_out()
        return dict(zip(terms, scores))
    except ValueError:
        return {}


def merge_platform_counts(platform_texts: Dict[str, List[str]]) -> pd.DataFrame:
    rows = []
    for platform, texts in platform_texts.items():
        combined = [normalize_text(t) for t in texts if t]
        terms, counts = extract_ngrams(combined, n=1)
        for term, count in zip(terms, counts):
            rows.append({"platform": platform, "term": term, "count": count})
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["term", "platform", "count", "opportunity_score"])
    pivot = df.pivot_table(index="term", columns="platform", values="count", aggfunc="sum").fillna(0)
    for col in platform_texts.keys():
        if col not in pivot.columns:
            pivot[col] = 0
    pivot["opportunity_score"] = _compute_opportunity(pivot)
    pivot = pivot.reset_index()
    return pivot


def _compute_opportunity(pivot: pd.DataFrame) -> List[float]:
    yt = pivot.get("youtube", 0)
    etsy = pivot.get("etsy", 0)
    ig = pivot.get("instagram", 0)
    web = pivot.get("web", 0)
    # Heuristic: reward Etsy/IG/Web presence and penalize when YT is already saturated.
    raw = (0.4 * etsy + 0.3 * ig + 0.2 * web) - (0.3 * yt)
    raw = raw.fillna(0)
    if raw.max() == raw.min():
        return [0.0 for _ in raw]
    normalized = (raw - raw.min()) / (raw.max() - raw.min())
    return normalized.tolist()
